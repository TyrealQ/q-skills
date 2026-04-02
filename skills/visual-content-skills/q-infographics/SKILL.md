---
name: q-infographics
description: Convert documents into business stories and infographics via Gemini API. Use for turning reports, documents, or text into visual summaries or infographics.
---

# Q-Infographics

Transform source documents into business stories and infographic images using the Gemini API.

> **If in plan mode:** write a brief plan — *"Run q-infographics skill: convert source
> document to markdown, generate business story via Gemini, generate infographic image."*
> — then exit plan mode immediately. Do NOT attempt document conversion, story generation,
> or image generation while plan mode is active.

## Script Directory

Agent execution instructions:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`.
2. Script path = `${SKILL_DIR}/scripts/<script-name>`.
3. Prompt path = `${SKILL_DIR}/references/<prompt-name>`.

| Resource | Purpose |
|----------|---------|
| `scripts/gen_story.py` | Generate business story from document via Gemini API |
| `scripts/gen_image.py` | Generate infographic image from story via Gemini API |
| `references/story.txt` | Story generation prompt template |
| `references/image.txt` | Infographic generation prompt template |

## Dependencies

```
google-genai
Pillow
markitdown
```

Install: `pip install google-genai Pillow markitdown`

Requires `GEMINI_API_KEY` environment variable. Load from `.env`:

**PowerShell (Windows):**
```powershell
$env:GEMINI_API_KEY = (Get-Content path\to\.env | Where-Object { $_ -match '^GEMINI_API_KEY=' } | Select-Object -First 1).Split('=',2)[1]
```

**Bash (macOS/Linux):**
```bash
export $(cat /path/to/.env | xargs)
```

## References

- **references/prompts_reference.md** — story and image prompt descriptions and key elements

## Core Principles

- Review checkpoint after each step — display outputs and get user confirmation before proceeding
- Output files use source filename with `_INFO` suffix (e.g., `MY_REPORT.pdf` → `MY_REPORT_INFO.jpg`)
- Logo auto-overlaid in bottom-right corner (~6% of image width); customize via `assets/Logo_Q.png`

## Workflow

| Step | Action | Command / Reference |
|------|--------|---------------------|
| 1 | Convert source document to markdown; show first ~50 lines for confirmation | `markitdown <input_file> -o <OUTPUT.md>` |
| 2 | Generate business story; show prompt and full output for review | `python "${SKILL_DIR}/scripts/gen_story.py" <INPUT.md> "${SKILL_DIR}/references/story.txt" > STORY_OUTPUT.md` |
| 3 | Generate infographic image; display result for review | `python "${SKILL_DIR}/scripts/gen_image.py" STORY_OUTPUT.md "${SKILL_DIR}/references/image.txt" <SOURCE_NAME>_INFO` |

## Customization

- **Story style**: Edit `${SKILL_DIR}/references/story.txt` — see references/prompts_reference.md
- **Infographic style**: Edit `${SKILL_DIR}/references/image.txt` — see references/prompts_reference.md

## Scope

**Include:** Document-to-story conversion, infographic generation, logo branding.
**Exclude:** Slide decks (use q-presentations), data visualization, chart generation.

## Checklist

- [ ] Source document converted to markdown
- [ ] Story reviewed and approved by user before infographic generation
- [ ] Infographic generated with correct naming convention
- [ ] Logo overlay applied
