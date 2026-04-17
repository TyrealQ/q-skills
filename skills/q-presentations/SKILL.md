---
name: q-presentations
description: Generate professional slide deck images from content with smart logo branding. Use for creating slides, presentations, decks, or PPT output.
---

# Q-Presentations

Generate slide deck images from content via Gemini API with layout-driven overlay safety and smart logo branding. Built on [baoyu-slide-deck](https://github.com/nicepkg/baoyu-slide-deck).

> **If in plan mode:** write a brief plan — *"Run q-presentations skill: analyze content,
> confirm style/audience preferences, generate outline and prompts, generate slide images,
> overlay logo, merge to PPTX/PDF."* — then exit plan mode immediately. Do NOT attempt
> content analysis, image generation, or file merging while plan mode is active.

## Script Directory

Agent execution instructions:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`.
2. Script path = `${SKILL_DIR}/scripts/<script-name>`.

| Script | Purpose |
|--------|---------|
| `scripts/gen_slide.py` | Generate slide images via Gemini API |
| `scripts/overlay_logo.py` | Apply Dr. Q logo overlay |
| `scripts/merge-to-pptx.ts` | Merge slides into PowerPoint (Bun/TS) |
| `scripts/merge-to-pdf.ts` | Merge slides into PDF (Bun/TS) |

## Dependencies

Install: `pip install google-genai Pillow python-dotenv` | Bun runtime (via `npx -y bun`, Node.js 18+).

## References

- **references/options.md** — CLI options, usage examples, and partial workflows
- **references/workflow_detailed.md** — full 10-step workflow with substeps and commands
- **references/analysis-framework.md** — content analysis for presentations
- **references/outline-template.md** — outline structure and format
- **references/modification-guide.md** — edit, add, delete slide workflows
- **references/content-rules.md** — content and style guidelines
- **references/design-guidelines.md** — audience, typography, colors, visual elements
- **references/layouts.md** — layout catalog, overlay-safe policy, fallback rules
- **references/base-prompt.md** — base prompt for image generation
- **references/dimensions/presets.md** — preset-to-dimension mapping
- **references/styles/*.md** — per-style specifications
- **references/config/preferences-schema.md** — EXTEND.md structure

## Core Principles

- Each slide self-explanatory (designed for reading and sharing, not only presenting)
- Flow clear in scroll view; context present on each slide
- Consistent style across the full deck
- Never include photorealistic images of prominent individuals
- Never include placeholder slides for author/date metadata

## Style System

16 presets available (default: `blueprint`). Full specs in references/dimensions/presets.md and references/styles/*.md.

## Workflow

Full step details: **references/workflow_detailed.md**

| Step | Action | Key references |
|------|--------|----------------|
| 0 | Skill announcement | — |
| 1 | Analyze content, load EXTEND.md preferences | references/analysis-framework.md, references/config/preferences-schema.md |
| 2 | Confirm style, audience, video overlay, logo | references/options.md |
| 3 | Generate outline with layout selection | references/outline-template.md, references/layouts.md |
| 4 | Review outline (conditional) | — |
| 5 | Generate per-slide prompts | references/base-prompt.md, references/content-rules.md |
| 6 | Review prompts (conditional) | — |
| 7 | Generate slide images | `scripts/gen_slide.py` |
| 7.5 | Logo overlay | `scripts/overlay_logo.py` |
| 8 | Merge to PPTX/PDF | `scripts/merge-to-pptx.ts`, `scripts/merge-to-pdf.ts` |
| 9 | Output summary | — |

For editing existing decks: references/modification-guide.md. For audience and visual hierarchy: references/design-guidelines.md.

## File Management

Output directory: `slide-deck/{topic-slug}/` containing `source-{slug}.{ext}`, `outline.md`, `prompts/` (numbered `.md` files), numbered slide `.png` files, `{topic-slug}.pptx`, and `{topic-slug}.pdf`.

## Language Handling

Detection priority: `--lang` flag > EXTEND.md > user conversation language > source content language. All user-facing responses use the user's preferred language; technical names remain in English.

## Scope

**Include:** Slide deck generation from content with logo branding and video-overlay-aware layouts.
**Exclude:** Slide editing in PowerPoint, animation, speaker notes.

## Checklist

- [ ] Style and audience confirmed with user
- [ ] Layout selection compatible with video_overlay_side
- [ ] Logo overlay applied (or explicitly set to none)
- [ ] PPTX and PDF outputs generated
- [ ] Output summary displayed to user