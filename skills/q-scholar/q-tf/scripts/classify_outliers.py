"""
Gemini Outlier Classification Pipeline (Reference Implementation)

Use this script to reclassify outlier documents (Topic = -1) using a predefined list of topics.
Customized for Esports UGC data but adaptable for any domain.

Usage:
1. Set up your .env with GEMINI_API_KEY
2. Customize VALID_TOPICS list
3. Update specific file paths (BASE_DIR, input/output filenames)
4. Customize system prompt file
"""

import os
import json
import re
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tqdm.auto import tqdm

# Load API key
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Placeholder for actual error handling or setup instruction
    print("Warning: Missing API key. Set GEMINI_API_KEY in .env file.")

# Configuration
# Default to Gemini 3 Flash, but allow override via env var
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview") 
BASE_DIR = os.getcwd() 
MAX_WORKERS = 50
MAX_RETRIES = 3

# Initialize Client
client = None
if api_key:
    client = genai.Client(api_key=api_key)

# Valid topics list (Example: 58 topics + MANUAL)
VALID_TOPICS = [
    "Hangzhou Asian Games: Esports as Official Sport",
    "Asian Games National Team Selection Process",
    # ... Add your topics here ...
    "MANUAL"
]

def load_system_prompt():
    """Load the system prompt."""
    prompt_path = os.path.join(BASE_DIR, "SP_OUTLIER_TEMPLATE.txt")  # Update filename as needed
    if not os.path.exists(prompt_path):
         return "You are an expert classifier. Classify the document into one of the valid topics."
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def try_json_load(s: str):
    """Parse a string as JSON, falling back to the first {...} block if needed."""
    if not s:
        return None
    s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", s, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
        return None

def classify_document(idx: int, document: str, system_prompt: str) -> dict:
    """Classify a single document using the Gemini API."""
    try:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=f"Document:\n{document}")],
            )
        ]

        # Config is model-agnostic enough for most Gemini models
        config = types.GenerateContentConfig(
            temperature=1.0,
            response_mime_type="application/json",
            system_instruction=[types.Part.from_text(text=system_prompt)],
        )

        full = ""
        try:
            # Use generate_content_stream for better reliability/handling large outputs
            chunks = client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )
            for ch in chunks:
                if ch.text:
                    full += ch.text
        except Exception as api_err:
            print(f"[ERROR] Index {idx} API call failed: {api_err}")
            return {"ok": False, "topic": "Error", "classification_confidence": "low", "key_phrases": "", "error": str(api_err)}

        data = try_json_load(full)
        if data is None:
            print(f"[ERROR] Index {idx} Failed parsing JSON. Snippet: {full[:120]}")
            return {"ok": False, "topic": "Parse Error", "classification_confidence": "low", "key_phrases": "", "raw": full[:200]}

        return {
            "ok": True,
            "topic": data.get("topic", "Unknown"),
            "classification_confidence": data.get("classification_confidence", "low"),
            "key_phrases": data.get("key_phrases", "")
        }
    except Exception as e:
        print(f"[ERROR] Index {idx} Exception: {e}")
        return {"ok": False, "topic": "Exception", "classification_confidence": "low", "key_phrases": "", "error": str(e)}

def validate_topic(topic_label: str) -> bool:
    """Check if topic is one of valid topics or MANUAL."""
    return topic_label in VALID_TOPICS

def classify_with_retry(df: pd.DataFrame, outlier_indices: list, system_prompt: str) -> dict:
    """Classify documents and retry those with invalid topics."""
    results = {}
    to_classify = outlier_indices.copy()
    retry_count = 0
    
    while to_classify and retry_count <= MAX_RETRIES:
        if retry_count > 0:
            print(f"\n[RETRY {retry_count}/{MAX_RETRIES}] Retrying {len(to_classify)} documents with invalid topics...")
        else:
            print(f"\n[INITIAL RUN] Procesing {len(to_classify)} outlier documents with {MODEL_NAME}...")
        
        batch_results = {}
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Assumes 'text' column exists
            futures = {
                executor.submit(classify_document, idx, df.loc[idx, 'text'], system_prompt): idx 
                for idx in to_classify
            }
            
            desc = f"Retry {retry_count}" if retry_count > 0 else "Classifying"
            for fut in tqdm(as_completed(futures), total=len(futures), desc=desc):
                idx = futures[fut]
                batch_results[idx] = fut.result()
        
        # Update results
        results.update(batch_results)
        
        # Find documents with invalid topics
        invalid_indices = [
            idx for idx in to_classify 
            if not validate_topic(results[idx].get('topic', ''))
        ]
        
        if not invalid_indices:
            print(f"✓ All classifications valid!")
            break
        
        print(f"Found {len(invalid_indices)} documents with invalid topics")
        to_classify = invalid_indices
        retry_count += 1
    
    return results, invalid_indices

def main():
    parser = argparse.ArgumentParser(description='Outlier Reclassification Pipeline')
    parser.add_argument('--dry-run', action='store_true',
                       help='Test mode: classify only 10 outlier documents')
    parser.add_argument('--model', type=str, default=MODEL_NAME,
                       help='Gemini model name (default: env var GEMINI_MODEL or gemini-2.0-flash-exp)')
    
    args = parser.parse_args()
    
    # Update global model name if arg provided
    global MODEL_NAME
    MODEL_NAME = args.model
    
    # Input/Output paths - UPDATE THESE
    input_filename = "output_with_labels.xlsx"
    output_filename = "output_with_outliers.xlsx"
    
    input_path = os.path.join(BASE_DIR, input_filename)
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    df = pd.read_excel(input_path)
    system_prompt = load_system_prompt()
    
    # Filter behavior - UPDATE COLUMN NAME IF NEEDED
    if 'Topic' in df.columns:
        outlier_mask = df['Topic'] == -1
    else:
        print("Topic column not found, processing all rows...")
        outlier_mask = pd.Series([True] * len(df))

    outlier_indices = df[outlier_mask].index.tolist()
    
    if args.dry_run:
        outlier_indices = outlier_indices[:10]
    
    results, final_invalid = classify_with_retry(df, outlier_indices, system_prompt)
    
    # Update dataframe
    for idx, res in results.items():
        df.at[idx, 'Final_Topic_Label'] = res.get('topic', 'Unknown')
        df.at[idx, 'classification_confidence'] = res.get('classification_confidence', 'low')
        phrases = res.get('key_phrases', "")
        df.at[idx, 'key_phrases'] = str(phrases) if phrases else None
    
    output_path = os.path.join(BASE_DIR, output_filename)
    df.to_excel(output_path, index=False)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    import sys
    if not client:
        print("Error: Client not initialized. Check GEMINI_API_KEY.")
        sys.exit(1)
    main()
