
# To run this code you need to install the following dependencies:
# pip install google-genai python-dotenv

import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def generate(input_text, system_prompt_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    model = "gemini-3-pro-preview"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=input_text),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        system_instruction=[
             types.Part.from_text(text=system_prompt_text),
        ],
    )

    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            print(chunk.text, end="")
    except Exception as e:
        print(f"\nError during API call: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python gen_story.py <input_text_file> <prompt_file>")
        sys.exit(1)
    else:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            i_text = f.read()
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            p_text = f.read()
            
        generate(i_text, p_text)
