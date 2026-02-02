
# To run this code you need to install the following dependencies:
# pip install google-genai

import mimetypes
import os
import sys
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")


def generate(input_text, system_prompt_text, output_prefix):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    model = "gemini-3-pro-image-preview"

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=input_text),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
        ),
        system_instruction=[
            types.Part.from_text(text=system_prompt_text),
        ],
    )

    file_index = 0

    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                chunk.candidates is None
                or not chunk.candidates
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue

            part = chunk.candidates[0].content.parts[0]

            if part.inline_data and part.inline_data.data:
                base, ext = os.path.splitext(output_prefix)
                if file_index == 0:
                    file_name_base = base
                else:
                    file_name_base = f"{base}_{file_index}"

                file_index += 1
                inline_data = part.inline_data
                data_buffer = inline_data.data

                guessed_ext = mimetypes.guess_extension(inline_data.mime_type)
                if guessed_ext:
                    final_filename = f"{file_name_base}{guessed_ext}"
                else:
                    final_filename = f"{file_name_base}.png"

                save_binary_file(final_filename, data_buffer)
            else:
                print(chunk.text, end="")
                sys.stdout.flush()
    except Exception as e:
        print(f"\nError during API call: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python gen_image.py <input_story_file> <prompt_file> <output_image_prefix>")
        sys.exit(1)
    else:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            i_text = f.read()
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            p_text = f.read()
        generate(i_text, p_text, sys.argv[3])
