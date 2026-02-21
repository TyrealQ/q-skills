---
name: q-infographics
description: Converts documents into business stories and infographics using Gemini 3.0 Pro (Python SDK). Use when the user wants to convert a document, report, or text into a visual business story or infographic.
---

# Q-Infographics

Q-Infographics transforms source documents into business stories and infographic images using the Gemini API.

**Powered by**: `google-genai` (Gemini 3.0 Pro).

## Folder Structure

```text
skills/q-infographics/
|-- SKILL.md           # This file
|-- requirements.txt   # Python dependencies
|-- assets/
|   `-- Logo_Q.png     # Brand logo, auto-overlaid on infographics
|-- prompts/
|   |-- story.txt      # Story generation prompt
|   `-- image.txt      # Infographic generation prompt
|-- scripts/
|   |-- gen_story.py   # Story generator script
|   `-- gen_image.py   # Image generator script
```

## When to Use

Use this skill when the user wants to:
- Convert a document, report, or text into a compelling business story
- Create an infographic from written content
- Transform dry business information into visual summaries
- Generate cartoon-style visual representations of key points

## Workflow

**IMPORTANT**: After each step, display outputs and ask for user confirmation before proceeding.

### Step 1: Prepare Input
Convert the source document to markdown/text.

```bash
markitdown <input_file> -o <OUTPUT.md>
```

**Review checkpoint**: Show the first ~50 lines of converted content. Ask user to confirm before proceeding.

### Step 2: Generate Story
```bash
python skills/q-infographics/scripts/gen_story.py <INPUT.md> skills/q-infographics/prompts/story.txt > STORY_OUTPUT.md
```

**Review checkpoint**:
1. Show the prompt being used: `cat skills/q-infographics/prompts/story.txt`
2. After generation, show the full story output: `cat STORY_OUTPUT.md`
3. Ask user: "Story generated. Review above and confirm to proceed with infographic generation, or request edits."

### Step 3: Generate Infographic
```bash
python skills/q-infographics/scripts/gen_image.py STORY_OUTPUT.md skills/q-infographics/prompts/image.txt <SOURCE_NAME>_INFO
```

**Naming convention**: Output files use the source filename with `_INFO` suffix (e.g., `MY_REPORT.pdf` -> `MY_REPORT_INFO.jpg`).

**Review checkpoint**:
1. Show the image prompt being used: `cat skills/q-infographics/prompts/image.txt`
2. After generation, display the infographic image
3. Ask user: "Infographic generated. Would you like to regenerate with different settings?"

## Requirements
*   `pip install -r skills/q-infographics/requirements.txt`
*   `GEMINI_API_KEY` environment variable. Load from a `.env` file:
    **PowerShell (Windows):**
    ```powershell
    $env:GEMINI_API_KEY = (Get-Content path\to\.env | Where-Object { $_ -match '^GEMINI_API_KEY=' } | Select-Object -First 1).Split('=',2)[1]
    ```
    **Bash (macOS/Linux):**
    ```bash
    export $(cat /path/to/.env | xargs)
    ```

## Branding

Every generated infographic is automatically branded with a logo in the bottom-right corner, resized to ~6% of the image width. To use your own logo, place it in the `assets/` folder and update `LOGO_FILENAME` in `scripts/gen_image.py`.

## Customization

*   **Story Style**: Edit `skills/q-infographics/prompts/story.txt` to change the writing persona
*   **Infographic Style**: Edit `skills/q-infographics/prompts/image.txt` to change the visual art style

## Prompts Reference

### Story Prompt (`prompts/story.txt`)
Creates business stories in the style of top-tier Chinese tech media (36Kr, Huxiu). Key elements:
- Story-first approach with hero's journey structure
- "Golden sentences" - bold, shareable quotes
- Effective analogies for complex concepts
- Structured methodology breakdowns
- Rhythmic flow with rhetorical questions

### Image Prompt (`prompts/image.txt`)
Generates hand-drawn cartoon-style infographics:
- 16:9 landscape composition
- Concise cartoon elements and icons
- Highlights keywords and core concepts
- Ample white space for readability
- Language matches input content


