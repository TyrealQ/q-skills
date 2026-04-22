"""Generate slide images using GPT Image 2 (default) or Gemini."""
import argparse
import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _generate_gpt(prompt_text: str, output_path: str) -> bool:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed — run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    result = client.images.generate(
        model="gpt-image-2",
        prompt=prompt_text,
    )
    image_bytes = base64.b64decode(result.data[0].b64_json)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    print(f"Saved: {output_path}")
    return True


def _generate_gemini(prompt_text: str, output_path: str) -> bool:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed — run: pip install google-genai", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
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


def generate_slide(prompt_text: str, output_path: str, model: str) -> bool:
    if model == "gpt":
        return _generate_gpt(prompt_text, output_path)
    if model == "gemini":
        return _generate_gemini(prompt_text, output_path)
    print(f"Error: unknown model '{model}' (expected 'gpt' or 'gemini')", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    default_model = os.environ.get("IMAGE_MODEL", "gpt")
    parser = argparse.ArgumentParser(description="Generate a slide image from a prompt file.")
    parser.add_argument("prompt_file", help="Path to the prompt text file")
    parser.add_argument("output_file", help="Path to write the generated image")
    parser.add_argument(
        "--model",
        choices=["gpt", "gemini"],
        default=default_model,
        help="Image generation backend (default: env IMAGE_MODEL or 'gpt')",
    )
    args = parser.parse_args()

    if not os.path.exists(args.prompt_file):
        print(f"Error: Prompt file not found: {args.prompt_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.prompt_file, "r", encoding="utf-8") as f:
        prompt = f.read()

    generate_slide(prompt, args.output_file, args.model)


if __name__ == "__main__":
    main()
