# Q-Presentations: Detailed Workflow

## Step 0: Skill announcement

```text
q-presentations - slide deck generator
Built on baoyu-slide-deck, extended with layout-driven overlay safety and smart logo branding.
```

## Step 1: Setup and analyze

### 1.1 Load preferences (EXTEND.md)

Check in this order:
1. `.q-skills/q-presentations/EXTEND.md` (project)
2. `$HOME/.q-skills/q-presentations/EXTEND.md` (user)

When found: parse and summarize.
When missing: collect preferences and proceed with defaults.

Schema: `references/config/preferences-schema.md`

### 1.2 Analyze content

1. Save source content (if pasted, save as `source.md`).
2. Backup existing source/prompt/image files before overwrite.
3. Follow `references/analysis-framework.md`.
4. Detect language and recommend slide count/style.
5. Generate topic slug.

### 1.3 Check existing content

If `slide-deck/{topic-slug}` exists, ask user whether to regenerate outline, regenerate images, backup and regenerate, or exit.

## Step 2: Confirmation

Three parts:
1. Round 1 (always): style, audience, slide count, outline review, prompt review.
2. Round 2 (if custom style): texture, mood, typography, density.
3. q-presentations questions (always): video overlay side and logo placement.

Video overlay options:
- right (recommended)
- left
- bottom
- none

Logo options:
- top-right (recommended)
- bottom-right
- top-left
- bottom-left
- none

Store: `video_overlay_side`, `logo_position`, and all style/audience/review preferences.

## Step 3: Generate outline

1. Build STYLE_INSTRUCTIONS from preset/custom dimensions.
2. Apply audience, language, and slide count.
3. Select a `Layout` for every slide using `references/layouts.md`.

Layout selection policy:
1. Infer content-fit candidates.
2. Use `primary_content_bias` and derived safe-side mapping from `layouts.md`.
3. Apply `layouts.md` exceptions table.
4. Keep only layouts compatible with selected `video_overlay_side`.
5. Rank by content fit and diversity.
6. If empty, use fallback layouts from `layouts.md`.

Prompting rule:
- Do not state overlay reservations or empty-zone instructions.
- Only include the chosen layout composition.

Outline metadata should include:
```text
**Video Overlay**: [right/left/bottom/none]
**Logo**: [top-right/bottom-right/top-left/bottom-left/none]
```

Save as `outline.md`.

## Step 4: Review outline (conditional)

Skip when user disabled outline review.
Otherwise show slide-by-slide summary and ask: proceed, edit, regenerate.

## Step 5: Generate prompts

1. Read `references/base-prompt.md`.
2. For each slide, merge:
   - STYLE_INSTRUCTIONS from outline
   - slide content
   - selected layout guidance
3. Save into `prompts/` with backups on overwrite.

## Step 6: Review prompts (conditional)

Skip when user disabled prompt review.
Otherwise ask: proceed, edit, regenerate.

## Step 7: Generate images

Generate sequentially using:

```bash
python ${SKILL_DIR}/scripts/gen_slide.py <prompt-file> <output-png>
```

Rules:
- Backup existing image before overwrite.
- Auto-retry once on failure.
- Report progress in user language.

## Step 7.5: Logo overlay

```bash
python ${SKILL_DIR}/scripts/overlay_logo.py <slide-deck-dir> --position <logo-position> --style <style-name>
```

If logo is `none`, add `--skip`.

## Step 8: Merge to PPTX/PDF

Use Bun/TypeScript tools:
```bash
npx -y bun ${SKILL_DIR}/scripts/merge-to-pptx.ts <slide-deck-dir>
npx -y bun ${SKILL_DIR}/scripts/merge-to-pdf.ts <slide-deck-dir>
```

## Step 9: Output summary

```text
Slide Deck Complete!

Topic: [topic]
Style: [preset or custom dimensions]
Video Overlay Zone: [side]
Logo: [position]
Location: [directory]
Slides: N total

Outline: outline.md
PPTX: {topic-slug}.pptx
PDF: {topic-slug}.pdf
```
