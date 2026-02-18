# q-skills

Skills for academic research workflows with Claude Code.

## Prerequisites

- [Claude Code](https://claude.ai/code) or compatible AI coding assistant
- Python 3.8+ (for script-based skills)
- pandas, openpyxl (for data processing skills)

## Installation

### Quick Install (Recommended)

```bash
npx skills add TyrealQ/q-skills
```

### Alternative: Clone and Copy

```bash
git clone https://github.com/TyrealQ/q-skills.git
```

**Windows (PowerShell):**

```powershell
Copy-Item -Recurse -Force q-skills\skills\q-* $env:USERPROFILE\.claude\skills\
```

**macOS/Linux:**

```bash
cp -r q-skills/skills/q-* ~/.claude/skills/
```

> **Note:** The exact skills path depends on your AI assistant. Common locations: `~/.claude/skills/`, `~/.gemini/skills/`

## Update Skills

To update to the latest version:

```bash
cd q-skills
git pull
```

Then re-copy the skills to your skills directory.

**Or reinstall:**
```bash
npx skills add TyrealQ/q-skills --force
```

---

## Available Skills

### Academic Writing Skills

| Skill                      | Description                                                   |
| -------------------------- | ------------------------------------------------------------- |
| [q-scholar](#q-scholar)    | Academic manuscript writing suite (methods, results, analysis) |

### Data Analysis Skills

| Skill                                     | Description                                                      |
| ----------------------------------------- | ---------------------------------------------------------------- |
| [q-topic-finetuning](#q-topic-finetuning) | Consolidate topic modeling outputs into theory-driven frameworks |

### Education Skills

| Skill                         | Description                                                                 |
| ----------------------------- | --------------------------------------------------------------------------- |
| [q-educator](#q-educator)     | Course content development for lectures, demos, assignments, and feedback   |

### Research Promotion Skills

| Skill                               | Description                                              |
| ----------------------------------- | -------------------------------------------------------- |
| [q-infographics](#q-infographics)   | Convert documents into business stories and infographics |
| [q-presentations](#q-presentations) | Convert content into branded slide decks with style presets |

---

## Skill Details

### q-scholar

Academic manuscript writing suite for drafting journal-ready prose following APA 7th edition standards. Orchestrates specialized sub-skills for complete manuscript preparation workflows.

**Sub-Skills:**

| Sub-Skill | Description |
| --------- | ----------- |
| q-intro | Introduction drafting and refinement with argumentative architecture guidance |
| q-descriptive-analysis | Comprehensive exploratory analysis of tabular datasets |
| q-methods | Methods section drafting in clear, narrative style |
| q-results | Results section drafting with APA-compliant tables |

**Triggers:**

- "Help me write the methods and results for my study"
- "Draft a results section for this analysis"
- "Analyze this dataset and generate descriptive statistics"

**Features:**

- End-to-end manuscript support (data exploration â†’ methods â†’ results)
- APA 7th edition formatting (tables, statistics, notation)
- Narrative prose style (no bullet points or em-dashes)
- Shared style guides and templates
- Appendix strategies for technical details

**Workflow Phases:**

1. **Data Exploration** - Invoke q-descriptive-analysis for statistics and summaries
2. **Introduction Drafting** - Invoke q-intro for context, gaps, RQs, and contributions
3. **Methods Documentation** - Invoke q-methods for data collection and analysis procedures
4. **Results Presentation** - Invoke q-results for findings organized by research questions

**Folder Structure:**

```
q-scholar/
â”œâ”€â”€ SKILL.md                              # Orchestration skill
â”œâ”€â”€ references/                           # Shared style guides
â”‚   â”œâ”€â”€ apa_style_guide.md                # Numbers, statistics, notation
â”‚   â””â”€â”€ table_formatting.md               # APA 7th table examples
â”œâ”€â”€ q-intro/
â”‚   â”œâ”€â”€ SKILL.md                          # Introduction drafting skill
â”‚   â””â”€â”€ references/                       # Templates and interview questions
â”œâ”€â”€ q-descriptive-analysis/
â”‚   â””â”€â”€ SKILL.md                          # Data exploration skill
â”œâ”€â”€ q-methods/
â”‚   â”œâ”€â”€ SKILL.md                          # Methods drafting skill
â”‚   â””â”€â”€ references/                       # Methods and appendix templates
â””â”€â”€ q-results/
    â”œâ”€â”€ SKILL.md                          # Results drafting skill
    â””â”€â”€ references/                       # Results template
```

**Example:**

```
Help me write the methods and results sections for my topic modeling study on esports discourse
```

---

### q-topic-finetuning

Fine-tune and consolidate topic modeling outputs (BERTopic, LDA, NMF) into theory-driven classification frameworks.

**Triggers:**

- "Consolidate these BERTopic topics..."
- "Classify topics using [framework]..."
- "Merge topic modeling results for my manuscript..."

**Features:**

- Convert 50+ raw topics into 20-50 manuscript-ready categories
- Apply theoretical frameworks (legitimacy, stakeholder theory, sentiment)
- Preserve domain-specific distinctions (entity, event, geography)
- Handle multi-category assignments with overlap reconciliation
- Generate Excel output with classification labels

**Folder Structure:**

```
q-topic-finetuning/
â”œâ”€â”€ SKILL.md                                  # Main skill file
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ classify_outliers.py                  # Outlier reclassification via Gemini
â”‚   â”œâ”€â”€ generate_implementation_plan.py       # Full plan generation
â”‚   â””â”€â”€ update_excel_with_labels.py           # Excel column updates
â””â”€â”€ references/
    â”œâ”€â”€ esports_ugc_example.md                # Worked example
    â””â”€â”€ SP_OUTLIER_TEMPLATE.txt               # Outlier classification prompt template
```

**Example:**

```
Consolidate my 129 BERTopic topics using organizational legitimacy framework
```

**Reference:** See `references/esports_ugc_example.md` for complete worked example.

---

### q-infographics

Convert documents into compelling business stories and cartoon-style infographics using Gemini 3.0 Pro.

**Triggers:**

- "Create an infographic from this document..."
- "Convert this paper to a visual summary..."
- "Generate a business story from..."

**Features:**

- Two-stage pipeline: Document â†’ Story â†’ Infographic
- Business story style (36Kr/Huxiu format) with "golden sentences"
- Hand-drawn cartoon-style infographics (16:9)
- Automatic logo branding on generated infographics
- Review checkpoints at each stage
- Supports PDF, DOCX, and text input (via markitdown)

**Requirements:**

- `pip install google-genai Pillow markitdown`
- `GEMINI_API_KEY` environment variable (load via `export $(cat /path/to/.env | xargs)`)

**Folder Structure:**

```
q-infographics/
â”œâ”€â”€ SKILL.md                              # Main skill file
â”œâ”€â”€ requirements.txt                      # Python dependencies
â”œâ”€â”€ assets/
â”‚   â””â”€â”€ Logo_Q.png                        # Brand logo, auto-overlaid on infographics
â”œâ”€â”€ prompts/
â”‚   â”œâ”€â”€ story.txt                         # Story generation prompt
â”‚   â””â”€â”€ image.txt                         # Infographic generation prompt
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ gen_story.py                      # Story generator script
â”‚   â””â”€â”€ gen_image.py                      # Image generator script
â””â”€â”€ examples/                             # Sample outputs
```

**Example:**

```
Create an infographic from my research paper on gamification in esports
```

**Sample Outputs:**

![DIGITAL_ENTREPRENEURSHIP_INFO1](skills/q-infographics/examples/DIGITAL_ENTREPRENEURSHIP_INFO1.jpg)

![DIGITAL_ENTREPRENEURSHIP_INFO2](skills/q-infographics/examples/DIGITAL_ENTREPRENEURSHIP_INFO2.jpg)

---

### q-presentations

Convert content into branded slide decks with 16 visual style presets, layout-driven overlay safety, and automatic logo branding. Fork of [baoyu-slide-deck](https://github.com/JimLiu/baoyu-skills) with video-overlay-aware layout.

**Triggers:**

- "Create a slide deck from this content..."
- "Make a presentation about..."
- "Generate slides for my talk..."

**Features:**

- 16 style presets (blueprint, chalkboard, corporate, minimal, sketch-notes, watercolor, etc.)
- Composable dimension system (texture + mood + typography + density)
- Video-overlay-aware layout: internal layout-driven overlay-safe selection
- Automatic Dr. Q logo branding with configurable placement and auto-invert for dark styles
- Gemini 3.0 Pro image generation
- PPTX and PDF export
- Partial workflows (outline-only, prompts-only, regenerate specific slides)

**Requirements:**

- `pip install google-genai Pillow python-dotenv`
- `GEMINI_API_KEY` environment variable
- Bun available for PPTX/PDF merge scripts (`npx -y bun ...`)

**Folder Structure:**

```
q-presentations/
â”œâ”€â”€ SKILL.md                              # Main skill file
â”œâ”€â”€ requirements.txt                      # Python dependencies
â”œâ”€â”€ assets/
â”‚   â””â”€â”€ Logo_Q.png                        # Brand logo, auto-overlaid on slides
â”œâ”€â”€ references/
â”‚   â”œâ”€â”€ base-prompt.md                    # Image generation base prompt
â”‚   â”œâ”€â”€ design-guidelines.md              # Typography, colors, visual hierarchy
â”‚   â”œâ”€â”€ layouts.md                        # 28 layout types
â”‚   â”œâ”€â”€ outline-template.md              # Outline structure template
â”‚   â”œâ”€â”€ config/preferences-schema.md     # EXTEND.md user preferences
â”‚   â”œâ”€â”€ dimensions/                       # Composable style dimensions (5 files)
â”‚   â””â”€â”€ styles/                           # 22 style definitions
â””â”€â”€ scripts/
    â”œâ”€â”€ gen_slide.py                      # Gemini API image generation
    â”œâ”€â”€ overlay_logo.py                   # Logo overlay with auto-invert
    â”œâ”€â”€ merge-to-pptx.ts                  # PPTX merge (Bun/TS)
    â””â”€â”€ merge-to-pdf.ts                   # PDF merge (Bun/TS)
```

**Example:**

```
Create a chalkboard-style slide deck from my research paper on AI agents
```

---

### q-educator

Course content development skill for university teaching workflows. Produces interview-driven lecture outlines, demo plans, follow-up emails, assignment prompts, and per-group feedback.

**Triggers:**

- "Help me design next week's lecture..."
- "Draft an assignment prompt for this module..."
- "Write feedback for each student group..."

**Features:**

- Interview-first planning workflow before drafting
- Projects-first teaching philosophy with domain-specific analogies
- Structured deliverables for lecture, demo, email, assignment, and feedback
- Iterative review checkpoints after each deliverable
- Reference examples for assignments, lectures, emails, demos, and feedback

**Folder Structure:**

```text
q-educator/
|-- SKILL.md
`-- references/
    |-- assignment_example.md
    |-- demo_example.md
    |-- email_example.md
    |-- feedback_example.md
    `-- lecture_example.md
```

**Example:**

```
Help me build a week 6 lecture + demo + assignment plan for a graduate analytics course
```

---
## Acknowledgments

- Inspired by [baoyu-skills](https://github.com/JimLiu/baoyu-skills) by Jim Liu
- Built for use with Claude Code and compatible AI assistants

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please submit issues or pull requests.

