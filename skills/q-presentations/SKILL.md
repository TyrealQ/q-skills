---
name: q-presentations
description: Generates professional slide deck images from content with organic content positioning, smart logo branding, and video-overlay-aware layout. Use when user asks to "create slides", "make a presentation", "generate deck", "slide deck", or "PPT".
---

# q-presentations — AI-Powered Slide Deck Generator

Built on the foundation of [baoyu-slide-deck](https://github.com/nicepkg/baoyu-slide-deck) by baoyu, extended with organic content positioning, smart logo branding, and video-overlay-aware layout.

## Usage

```bash
/q-presentations path/to/content.md
/q-presentations path/to/content.md --style sketch-notes
/q-presentations path/to/content.md --audience executives
/q-presentations path/to/content.md --lang zh
/q-presentations path/to/content.md --slides 10
/q-presentations path/to/content.md --outline-only
/q-presentations  # Then paste content
```

## Script Directory

**Agent Execution Instructions**:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`
2. Script path = `${SKILL_DIR}/scripts/<script-name>`

| Script | Purpose |
|--------|---------|
| `scripts/gen_slide.py` | Generate slide images via Gemini API |
| `scripts/overlay_logo.py` | Apply Dr. Q logo overlay |
| `scripts/merge_slides.py` | Merge slides into PowerPoint (Python) |
| `scripts/merge-to-pptx.ts` | Merge slides into PowerPoint (Bun/TS) |
| `scripts/merge-to-pdf.ts` | Merge slides into PDF (Bun/TS) |

## Options

| Option | Description |
|--------|-------------|
| `--style <name>` | Visual style: preset name, `custom`, or custom style name |
| `--audience <type>` | Target: beginners, intermediate, experts, executives, general |
| `--lang <code>` | Output language (en, zh, ja, etc.) |
| `--slides <number>` | Target slide count (8-25 recommended, max 30) |
| `--outline-only` | Generate outline only, skip image generation |
| `--prompts-only` | Generate outline + prompts, skip images |
| `--images-only` | Generate images from existing prompts directory |
| `--regenerate <N>` | Regenerate specific slide(s): `--regenerate 3` or `--regenerate 2,5,8` |
| `--logo <position>` | Logo placement: top-right (default), bottom-right, top-left, bottom-left, none |
| `--video-overlay <side>` | Side reserved for video overlay: right (default), left, bottom, none |

**Slide Count by Content Length**:
| Content | Slides |
|---------|--------|
| < 1000 words | 5-10 |
| 1000-3000 words | 10-18 |
| 3000-5000 words | 15-25 |
| > 5000 words | 20-30 (consider splitting) |

## Style System

### Presets

| Preset | Dimensions | Best For |
|--------|------------|----------|
| `blueprint` (Default) | grid + cool + technical + balanced | Architecture, system design |
| `chalkboard` | organic + warm + handwritten + balanced | Education, tutorials |
| `corporate` | clean + professional + geometric + balanced | Investor decks, proposals |
| `minimal` | clean + neutral + geometric + minimal | Executive briefings |
| `sketch-notes` | organic + warm + handwritten + balanced | Educational, tutorials |
| `watercolor` | organic + warm + humanist + minimal | Lifestyle, wellness |
| `dark-atmospheric` | clean + dark + editorial + balanced | Entertainment, gaming |
| `notion` | clean + neutral + geometric + dense | Product demos, SaaS |
| `bold-editorial` | clean + vibrant + editorial + balanced | Product launches, keynotes |
| `editorial-infographic` | clean + cool + editorial + dense | Tech explainers, research |
| `fantasy-animation` | organic + vibrant + handwritten + minimal | Educational storytelling |
| `intuition-machine` | clean + cool + technical + dense | Technical docs, academic |
| `pixel-art` | pixel + vibrant + technical + balanced | Gaming, developer talks |
| `scientific` | clean + cool + technical + dense | Biology, chemistry, medical |
| `vector-illustration` | clean + vibrant + humanist + balanced | Creative, children's content |
| `vintage` | paper + warm + editorial + balanced | Historical, heritage |

### Style Dimensions

| Dimension | Options | Description |
|-----------|---------|-------------|
| **Texture** | clean, grid, organic, pixel, paper | Visual texture and background treatment |
| **Mood** | professional, warm, cool, vibrant, dark, neutral | Color temperature and palette style |
| **Typography** | geometric, humanist, handwritten, editorial, technical | Headline and body text styling |
| **Density** | minimal, balanced, dense | Information density per slide |

Full specs: `references/dimensions/*.md`

### Auto Style Selection

| Content Signals | Preset |
|-----------------|--------|
| tutorial, learn, education, guide, beginner | `sketch-notes` |
| classroom, teaching, school, chalkboard | `chalkboard` |
| architecture, system, data, analysis, technical | `blueprint` |
| creative, children, kids, cute | `vector-illustration` |
| briefing, academic, research, bilingual | `intuition-machine` |
| executive, minimal, clean, simple | `minimal` |
| saas, product, dashboard, metrics | `notion` |
| investor, quarterly, business, corporate | `corporate` |
| launch, marketing, keynote, magazine | `bold-editorial` |
| entertainment, music, gaming, atmospheric | `dark-atmospheric` |
| explainer, journalism, science communication | `editorial-infographic` |
| story, fantasy, animation, magical | `fantasy-animation` |
| gaming, retro, pixel, developer | `pixel-art` |
| biology, chemistry, medical, scientific | `scientific` |
| history, heritage, vintage, expedition | `vintage` |
| lifestyle, wellness, travel, artistic | `watercolor` |
| Default | `blueprint` |

## Design Philosophy

Decks designed for **reading and sharing**, not live presentation:
- Each slide self-explanatory without verbal commentary
- Logical flow when scrolling
- All necessary context within each slide
- Optimized for social media sharing

See `references/design-guidelines.md` for:
- Audience-specific principles
- Visual hierarchy
- Content density guidelines
- Color and typography selection
- Font recommendations

See `references/layouts.md` for layout options.

## Organic Positioning Principle

See `references/organic-positioning.md` for full rules. Key principles:

- Per-slide `// VISUAL` paragraphs describe where content IS using natural spatial words
- Never include a global `## CONTENT PLACEMENT` section in prompts
- Never mention empty space, reserved zones, or percentages
- Never tell the image generator what NOT to put somewhere
- Background spec in `STYLE_INSTRUCTIONS` is 1-2 lines max — never add Uniformity sub-sections or per-slide background reminders
- The less you say about the background, the more consistent it will be

## File Management

### Output Directory

```
slide-deck/{topic-slug}/
├── source-{slug}.{ext}
├── outline.md
├── prompts/
│   └── 01-slide-cover.md, 02-slide-{slug}.md, ...
├── 01-slide-cover.png, 02-slide-{slug}.png, ...
├── {topic-slug}.pptx
└── {topic-slug}.pdf
```

**Slug**: Extract topic (2-4 words, kebab-case). Example: "Introduction to Machine Learning" → `intro-machine-learning`

**Conflict Handling**: See Step 1.3 for existing content detection and user options.

## Language Handling

**Detection Priority**:
1. `--lang` flag (explicit)
2. EXTEND.md `language` setting
3. User's conversation language (input language)
4. Source content language

**Rule**: ALL responses use user's preferred language:
- Questions and confirmations
- Progress reports
- Error messages
- Completion summaries

Technical terms (style names, file paths, code) remain in English.

## Workflow

Copy this checklist and check off items as you complete them:

```
Slide Deck Progress:
- [ ] Step 0: Skill announcement (first run only)
- [ ] Step 1: Setup & Analyze
  - [ ] 1.1 Load preferences
  - [ ] 1.2 Analyze content
  - [ ] 1.3 Check existing
- [ ] Step 2: Confirmation (Round 1 + optional Round 2 + q-presentations questions)
- [ ] Step 3: Generate outline
- [ ] Step 4: Review outline (conditional)
- [ ] Step 5: Generate prompts
- [ ] Step 6: Review prompts (conditional)
- [ ] Step 7: Generate images
- [ ] Step 7.5: Logo overlay
- [ ] Step 8: Merge to PPTX/PDF
- [ ] Step 9: Output summary
```

### Flow

```
Announce → Input → Preferences → Analyze → [Check Existing?] → Confirm (1-2 rounds + positioning) → Outline → [Review?] → Prompts → [Review?] → Images → Logo → Merge → Complete
```

### Step 0: Skill Announcement

On first invocation, display:

> **q-presentations** — AI-powered slide deck generator
> Built on the foundation of [baoyu-slide-deck](https://github.com/nicepkg/baoyu-slide-deck) by baoyu, extended with organic content positioning, smart logo branding, and video-overlay-aware layout.
>
> Ready to create your next presentation.

### Step 1: Setup & Analyze

**1.1 Load Preferences (EXTEND.md)**

Use Bash to check EXTEND.md existence (priority order):

```bash
# Check project-level first
test -f .q-skills/q-presentations/EXTEND.md && echo "project"

# Then user-level
test -f "$HOME/.q-skills/q-presentations/EXTEND.md" && echo "user"
```

| Path | Location |
|------|----------|
| `.q-skills/q-presentations/EXTEND.md` | Project directory |
| `$HOME/.q-skills/q-presentations/EXTEND.md` | User home |

**When EXTEND.md Found** → Read, parse, output summary to user.

**When EXTEND.md Not Found** → First-time setup using AskUserQuestion or proceed with defaults.

Schema: `references/config/preferences-schema.md`

**1.2 Analyze Content**

1. Save source content (if pasted, save as `source.md`)
   - **Backup rule**: If `source.md` exists, rename to `source-backup-YYYYMMDD-HHMMSS.md`
2. Follow `references/analysis-framework.md` for content analysis
3. Analyze content signals for style recommendations
4. Detect source language
5. Determine recommended slide count
6. Generate topic slug from content

**1.3 Check Existing Content**

Use Bash to check if output directory exists:

```bash
test -d "slide-deck/{topic-slug}" && echo "exists"
```

**If directory exists**, use AskUserQuestion with options: Regenerate outline, Regenerate images, Backup and regenerate, Exit.

**Save to `analysis.md`** with: Topic, audience, content signals, recommended style, recommended slide count, language detection.

### Step 2: Confirmation

**Three parts**: Round 1 (always), Round 2 (if custom), q-presentations questions (always).

**Language**: Use user's input language or saved language preference.

#### Round 1 (Always) — same as baoyu

**Use AskUserQuestion** for all 5 questions:

1. **Style**: Recommended preset vs alternatives vs custom dimensions
2. **Audience**: General / Beginners / Experts / Executives
3. **Slide Count**: Recommended vs fewer vs more
4. **Review Outline**: Yes (recommended) / No
5. **Review Prompts**: Yes (recommended) / No

#### Round 2 (Only if "Custom dimensions" selected)

**Use AskUserQuestion** for 4 dimensions: Texture, Mood, Typography, Density.

#### q-presentations Questions (Always)

**Question: Video Overlay Side**
```
header: "Video"
question: "Where will the video overlay appear in post-production?"
options:
  - label: "Right side (Recommended)"
    description: "Content anchors left/center-left"
  - label: "Left side"
    description: "Content anchors center-right/right"
  - label: "Bottom"
    description: "Content anchors upper area"
  - label: "None"
    description: "Content centered freely, no video overlay"
```

**Question: Logo Placement**
```
header: "Logo"
question: "Logo placement?"
options:
  - label: "Top-right (Recommended)"
    description: "Dr. Q logo at top-right corner"
  - label: "Bottom-right"
    description: "Dr. Q logo at bottom-right corner"
  - label: "None"
    description: "No logo overlay"
```

**Derive content anchor direction from video overlay answer:**

| Video Overlay Side | Content Anchor Direction |
|--------------------|------------------------|
| Right | Left (upper-left, center-left, bottom-left) |
| Left | Right (upper-right, center-right, bottom-right) |
| Bottom | Top (upper area, top-center) |
| None | Center (freely positioned) |

**After Confirmation**: Store all preferences including `video_overlay_side`, `content_anchor`, `logo_position`.

### Step 3: Generate Outline

Create outline using the confirmed style from Step 2.

**Style Resolution**:
- If preset selected → Read `references/styles/{preset}.md`
- If custom dimensions → Read dimension files from `references/dimensions/` and combine

**Generate**:
1. Follow `references/outline-template.md` for structure
2. Build STYLE_INSTRUCTIONS from style or dimensions
3. Apply confirmed audience, language, slide count
4. **CRITICAL — Organic Positioning** (see `references/organic-positioning.md`):
   - Background in STYLE_INSTRUCTIONS: ONE concise line (Color + Texture). Use "flat" and "edge to edge" for uniformity. No Uniformity sub-section.
   - Per-slide `// VISUAL` paragraphs: Describe where content IS using natural spatial words based on the content anchor direction. Never mention empty space, reserved zones, or percentages.
5. Add metadata to outline header:
   ```
   **Content Anchor**: [left/right/top/center]
   **Video Overlay**: [right/left/bottom/none]
   **Logo**: [top-right/bottom-right/none]
   ```
6. Save as `outline.md`

**After generation**:
- If `--outline-only`, stop here
- If `skip_outline_review` is true → Skip Step 4, go to Step 5
- Otherwise → Continue to Step 4

### Step 4: Review Outline (Conditional)

**Skip** if user selected "No, skip outline review" in Step 2.

Display slide-by-slide summary table. Use AskUserQuestion: Proceed / Edit outline / Regenerate.

### Step 5: Generate Prompts

1. Read `references/base-prompt.md`
2. For each slide in outline:
   - Extract STYLE_INSTRUCTIONS from outline (not from style file again)
   - Add slide-specific content
   - If `Layout:` specified, include layout guidance from `references/layouts.md`
   - **CRITICAL — Organic Positioning**: Copy Background line from STYLE_INSTRUCTIONS exactly (1-2 lines). Do NOT expand into verbose uniformity paragraphs. Do NOT add per-slide "Background must be..." sentences. Do NOT add lists of what to avoid.
3. Save to `prompts/` directory
   - **Backup rule**: If prompt file exists, rename to backup

**After generation**:
- If `--prompts-only`, stop here
- If `skip_prompt_review` is true → Skip Step 6, go to Step 7
- Otherwise → Continue to Step 6

### Step 6: Review Prompts (Conditional)

**Skip** if user selected "No, skip prompt review" in Step 2.

Display prompt list. Use AskUserQuestion: Proceed / Edit prompts / Regenerate.

### Step 7: Generate Images

**For `--images-only`**: Start here with existing prompts.

**For `--regenerate N`**: Only regenerate specified slide(s).

**Standard flow**:
1. For each slide:
   - **Backup rule**: If image file exists, rename to backup
   - Generate image using Python script:
     ```bash
     python ${SKILL_DIR}/scripts/gen_slide.py <prompt-file> <output-png>
     ```
   - Report progress: "Generated X/N" (in user's language)
2. Auto-retry once on failure before reporting error
3. Generate sequentially

### Step 7.5: Logo Overlay

After all images are generated, apply logo:

```bash
python ${SKILL_DIR}/scripts/overlay_logo.py <slide-deck-dir> --position <logo-position> --style <style-name>
```

- Position comes from Step 2 logo placement answer
- `--style` flag enables auto-invert for dark background styles (technical, storytelling, chalkboard, dark-atmospheric, etc.)
- If logo placement is "none", add `--skip` flag

### Step 8: Merge to PPTX and PDF

**Option A — Python** (PPTX only):
```bash
python ${SKILL_DIR}/scripts/merge_slides.py <slide-deck-dir>
```

**Option B — Bun/TypeScript** (PPTX + PDF):
```bash
npx -y bun ${SKILL_DIR}/scripts/merge-to-pptx.ts <slide-deck-dir>
npx -y bun ${SKILL_DIR}/scripts/merge-to-pdf.ts <slide-deck-dir>
```

### Step 9: Output Summary

```
Slide Deck Complete!

Topic: [topic]
Style: [preset name or custom dimensions]
Content Anchor: [direction]
Video Overlay Zone: [side]
Logo: [position]
Location: [directory path]
Slides: N total

- 01-slide-cover.png - Cover
- 02-slide-intro.png - Content
- ...
- {NN}-slide-back-cover.png - Back Cover

Outline: outline.md
PPTX: {topic-slug}.pptx
PDF: {topic-slug}.pdf
```

## Partial Workflows

| Option | Workflow |
|--------|----------|
| `--outline-only` | Steps 1-3 only (stop after outline) |
| `--prompts-only` | Steps 1-5 (generate prompts, skip images) |
| `--images-only` | Skip to Step 7 (requires existing prompts/) |
| `--regenerate N` | Regenerate specific slide(s) only |

## Slide Modification

### Quick Reference

| Action | Command | Manual Steps |
|--------|---------|--------------|
| **Edit** | `--regenerate N` | Update prompt file FIRST → Regenerate image → Regenerate PDF |
| **Add** | Manual | Create prompt → Generate image → Renumber subsequent → Update outline → Regenerate PDF |
| **Delete** | Manual | Remove files → Renumber subsequent → Update outline → Regenerate PDF |

See `references/modification-guide.md` for complete details.

### File Naming

Format: `NN-slide-[slug].png`
- `NN`: Two-digit sequence (01, 02, ...)
- `slug`: Kebab-case from content (2-5 words, unique)

## References

| File | Content |
|------|---------|
| `references/analysis-framework.md` | Content analysis for presentations |
| `references/outline-template.md` | Outline structure and format |
| `references/organic-positioning.md` | Organic content positioning and background rules |
| `references/modification-guide.md` | Edit, add, delete slide workflows |
| `references/content-rules.md` | Content and style guidelines |
| `references/design-guidelines.md` | Audience, typography, colors, visual elements |
| `references/layouts.md` | Layout options and selection tips |
| `references/base-prompt.md` | Base prompt for image generation |
| `references/dimensions/*.md` | Dimension specifications (texture, mood, typography, density) |
| `references/dimensions/presets.md` | Preset → dimension mapping |
| `references/styles/<style>.md` | Full style specifications |
| `references/config/preferences-schema.md` | EXTEND.md structure |

## Notes

- Image generation: 10-30 seconds per slide
- Auto-retry once on generation failure
- Use stylized alternatives for sensitive public figures
- Maintain style consistency across all slides
- **Step 2 confirmation required** — do not skip
- Never include photorealistic images of prominent individuals
- Never include placeholder slides for author name, date, etc.

## Extension Support

Custom configurations via EXTEND.md. See **Step 1.1** for paths and supported options.
