"""Generate slide images using Gemini API with image generation."""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types


def generate_slide(prompt_text: str, output_path: str):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt_text,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = part.inline_data.data
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"Saved: {output_path}")
            return True

    print("No image generated in response")
    if response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.text:
                print(f"Text response: {part.text[:200]}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: gen_slide.py <prompt_file> <output_file>")
        sys.exit(1)

    prompt_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.exists(prompt_file):
        print(f"Error: Prompt file not found: {prompt_file}")
        sys.exit(1)

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt = f.read()

    generate_slide(prompt, output_file)
