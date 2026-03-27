# q-skills

End-to-end skills for academic writing, data analysis, teaching, and research communication.

## Prerequisites

- [Claude Code](https://claude.ai/code) or compatible AI coding assistant
- Python 3.8+ (for script-based skills)
- pandas, openpyxl (for data processing skills)
- [Node.js](https://nodejs.org/) (for `npx`-based installation)

## Installation

Choose **one** of the methods below.

| Method | Best for |
| ------ | -------- |
| [Ask the Agent](#option-1-ask-the-agent-beginner-friendly) | **No coding experience needed** — just talk to Claude |
| [Quick Install](#option-2-quick-install) | Command-line users — installs all skills at once |
| [Plugin Marketplace](#option-3-plugin-marketplace) | Register once, then install all or specific skills |
| [Manual](#option-4-manual-clone-and-copy) | Offline or restricted environments |

---

### Option 1: Ask the Agent (Beginner-Friendly)

> **No coding experience required.** If you are new to Claude Code or not comfortable with the command line, this is the easiest way to get started. Just open Claude Code and type:

```
Please install skills from github.com/TyrealQ/q-skills
```

Claude will handle the installation for you — no terminal, no commands.

---

### Option 2: Quick Install

Requires [Node.js](https://nodejs.org/) for `npx`:

```bash
npx skills add TyrealQ/q-skills
```

---

### Option 3: Plugin Marketplace

Register q-skills as a plugin source in Claude Code, then install all or selected skills.

**Step 1 — Register** (run once inside Claude Code):

```
/plugin marketplace add TyrealQ/q-skills
```

**Step 2 — Install:**

To install all skills at once, use [Option 2](#option-2-quick-install) or browse via the Claude Code plugin UI after Step 1.

To install specific skills only:

```
/plugin install academic-skills@q-skills
/plugin install visual-content-skills@q-skills
/plugin install utility-skills@q-skills
```

---

### Option 4: Manual (Clone and Copy)

```bash
git clone https://github.com/TyrealQ/q-skills.git
```

**Windows (PowerShell):**

```powershell
Copy-Item -Recurse -Force q-skills\skills\*\q-* $env:USERPROFILE\.claude\skills\
```

**macOS/Linux:**

```bash
cp -r q-skills/skills/*/q-* ~/.claude/skills/
```

> **Note:** The exact skills path depends on your AI assistant. Common locations: `~/.claude/skills/`, `~/.gemini/skills/`

## Update Skills

### Via Plugin UI (Recommended)

1. Run `/plugin` in Claude Code
2. Switch to the **Marketplaces** tab (arrow keys or Tab)
3. Select **q-skills**
4. Choose **Update marketplace**

You can also enable **auto-update** to receive the latest versions automatically.

### Force Reinstall

```bash
npx skills add TyrealQ/q-skills --force
```

### Manual Update

```bash
cd q-skills
git pull
```

Then re-copy the skills to your skills directory (see Manual install above).

---

## Available Skills

### Academic Skills

| Skill                         | Description                                                                 |
| ----------------------------- | --------------------------------------------------------------------------- |
| [q-scholar](#q-scholar)       | Academic manuscript writing suite (intro, exploratory data analysis, topic modeling, methods, results) |
| [q-educator](#q-educator)     | Course content development for lectures, demos, assignments, and feedback   |

### Visual Content Skills

| Skill                               | Description                                              |
| ----------------------------------- | -------------------------------------------------------- |
| [q-infographics](#q-infographics)   | Convert documents into business stories and infographics |
| [q-presentations](#q-presentations) | Convert content into branded slide decks with style presets |

### Utility Skills

| Skill                   | Description                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| [commit](#commit)       | Stage and commit with smart file grouping and conventional commits       |
| [learn](#learn)         | Persist user preferences and styles across sessions                      |
| [ship](#ship)           | Full ship cycle: update docs, commit, and push to remote                 |

---

## Skill Details

### q-scholar

Academic manuscript writing suite for drafting journal-ready prose following APA 7th edition standards. Orchestrates specialized sub-skills for complete manuscript preparation workflows.

**Sub-Skills:**

| Sub-Skill | Description |
| --------- | ----------- |
| q-intro | Introduction drafting and refinement with argumentative architecture guidance |
| q-litreview | Literature review drafting with progressive-argument architecture and cross-section coordination |
| q-eda | Universal exploratory data analysis with user-confirmed column types and measurement-appropriate statistics |
| q-topic-finetuning | Consolidate topic modeling outputs (BERTopic, LDA, NMF) into theory-driven frameworks |
| q-methods | Methods section drafting in clear, narrative style |
| q-results | Results section drafting with APA-compliant tables |

**Triggers:**

- "Help me write the methods and results for my study"
- "Draft a results section for this analysis"
- "Analyze this dataset and generate descriptive statistics"

**Features:**

- End-to-end manuscript support (exploratory data analysis -> methods -> results)
- APA 7th edition formatting (tables, statistics, notation)
- Narrative prose style (no bullet points or em-dashes)
- Shared style guides and templates
- Appendix strategies for technical details

**Folder Structure:**

```text
q-scholar/
|-- SKILL.md                              # Orchestration skill
|-- references/                           # Shared style guides
|   |-- apa_style_guide.md                # Numbers, statistics, notation
|   `-- table_formatting.md               # APA 7th table examples
|-- q-intro/
|   |-- SKILL.md                          # Introduction drafting skill
|   `-- references/                       # Template and interview questions
|-- q-litreview/
|   |-- SKILL.md                          # Literature review drafting skill
|   `-- references/                       # Template and interview questions
|-- q-eda/
|   |-- SKILL.md                          # Data exploration skill
|   |-- scripts/                          # run_eda.py
|   `-- references/                       # Summary template and examples
|-- q-topic-finetuning/
|   |-- SKILL.md                          # Topic modeling consolidation skill
|   |-- scripts/                          # classify_outliers.py, plan & Excel updaters
|   `-- references/                       # Worked example + outlier prompt template
|-- q-methods/
|   |-- SKILL.md                          # Methods drafting skill
|   `-- references/                       # Methods and appendix templates
`-- q-results/
    |-- SKILL.md                          # Results drafting skill
    `-- references/                       # Results template
```

**Example:**

```
Help me write the methods and results sections for my topic modeling study on esports discourse
```

---

### q-infographics

Convert documents into compelling business stories and cartoon-style infographics using Nano Banana.

**Triggers:**

- "Create an infographic from this document..."
- "Convert this paper to a visual summary..."
- "Generate a business story from..."

**Features:**

- Two-stage pipeline: Document -> Story -> Infographic
- Business story style (36Kr/Huxiu format) with "golden sentences"
- Hand-drawn cartoon-style infographics (16:9)
- Automatic logo branding on generated infographics
- Review checkpoints at each stage
- Supports PDF, DOCX, and text input (via markitdown)

**Requirements:**

- `pip install google-genai Pillow python-dotenv markitdown`
- `GEMINI_API_KEY` environment variable (see [Environment Configuration](#environment-configuration))

**Folder Structure:**

```text
skills/q-infographics/
|-- SKILL.md                              # Main skill file
|-- assets/
|   `-- Logo_Q.png                        # Brand logo, auto-overlaid on infographics
|-- prompts/
|   |-- story.txt                         # Story generation prompt
|   `-- image.txt                         # Infographic generation prompt
|-- scripts/
|   |-- gen_story.py                      # Story generator script
|   `-- gen_image.py                      # Image generator script
# Sample outputs → see illustrations/q-infographics/ at repo root
```

**Example:**

```
Create an infographic from my research paper on gamification in esports
```

**Sample Outputs:**

![DIGITAL_ENTREPRENEURSHIP_INFO1](illustrations/q-infographics/DIGITAL_ENTREPRENEURSHIP_INFO1.jpg)

![DIGITAL_ENTREPRENEURSHIP_INFO2](illustrations/q-infographics/DIGITAL_ENTREPRENEURSHIP_INFO2.jpg)

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
- Nano Banana 2 image generation
- PPTX and PDF export
- Partial workflows (outline-only, prompts-only, regenerate specific slides)

**Requirements:**

- `pip install google-genai Pillow python-dotenv`
- `GEMINI_API_KEY` environment variable
- Bun available for PPTX/PDF merge scripts (`npx -y bun ...`)

**Folder Structure:**

```text
q-presentations/
|-- SKILL.md                              # Main skill file
|-- assets/
|   `-- Logo_Q.png                        # Brand logo, auto-overlaid on slides
|-- references/
|   |-- base-prompt.md                    # Image generation base prompt
|   |-- design-guidelines.md              # Typography, colors, visual hierarchy
|   |-- layouts.md                        # 28 layout types
|   |-- outline-template.md               # Outline structure template
|   |-- config/preferences-schema.md      # EXTEND.md user preferences
|   |-- dimensions/                       # Composable style dimensions (5 files)
|   `-- styles/                           # 22 style definitions
`-- scripts/
    |-- gen_slide.py                      # Gemini API image generation
    |-- overlay_logo.py                   # Logo overlay with auto-invert
    |-- merge-to-pptx.ts                  # PPTX merge (Bun/TS)
    `-- merge-to-pdf.ts                   # PDF merge (Bun/TS)
# Sample outputs → see illustrations/q-presentations/ at repo root
```

**Example:**

```
Create a chalkboard-style slide deck from my research paper on AI agents
```

**Sample Outputs:**

![01-slide-cover](illustrations/q-presentations/01-slide-cover.png)

![02-slide-from-answers-to-outcomes](illustrations/q-presentations/02-slide-from-answers-to-outcomes.png)

![03-slide-chatbot-vs-agent](illustrations/q-presentations/03-slide-chatbot-vs-agent.png)

![04-slide-what-it-does-what-you-do](illustrations/q-presentations/04-slide-what-it-does-what-you-do.png)

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

### commit

Stage and commit all uncommitted changes with smart file grouping and conventional commit messages. Analyzes changed files, groups by topic (content, skills, code, config), and generates descriptive commit messages.

**Triggers:**

- `/commit`
- "Commit my changes"

**Features:**

- Automatic file classification by path pattern
- Smart grouping: one commit per topic when changes span multiple areas
- Conventional commit format (`feat:`, `fix:`, `docs:`, etc.)
- Explicit file staging (never `git add .`)

---

### learn

Persist user preferences, styles, and behavioral patterns to `~/CLAUDE.md`, `~/.claude/rules/`, or project memory. Extracts corrections, explicit rules, and positive reinforcement from the current conversation.

**Triggers:**

- `/learn`
- "Remember this preference"
- "Save this to CLAUDE.md"
- "Update CM"

**Features:**

- Three-tier persistence: user instructions, user rules, project memory
- Scans conversation for corrections, explicit rules, and reinforced behaviors
- Deduplicates against existing preferences before saving
- Keeps `~/CLAUDE.md` under 200 lines, migrating overflow to rule files

---

### ship

Full ship cycle: update documentation, stage, commit, and push to remote. Automatically updates CHANGELOG.md, CLAUDE.md, and READMEs affected by the current changes.

**Triggers:**

- `/ship`
- "Ship my changes"

**Features:**

- Auto-updates CHANGELOG.md, CLAUDE.md, and relevant READMEs
- Stale reference detection for deleted/renamed files
- Smart commit grouping (same as commit skill)
- Pushes to remote with upstream tracking

---

## Environment Configuration

Some skills (q-infographics, q-presentations, q-topic-finetuning) use the Google Gemini API and need an API key to generate images and content.

### Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key — you'll need it in the next step

### Setting the API Key

Create a `.env` file in your project's working directory:

```
GEMINI_API_KEY=your-api-key-here
```

> **Important:** Add `.env` to your `.gitignore` so you don't accidentally commit your key:
> ```bash
> echo ".env" >> .gitignore
> ```

All skills that use the Gemini API load this file automatically via `python-dotenv`. Alternatively, set the variable directly in your terminal:

**macOS / Linux:**
```bash
export GEMINI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

To make it permanent, add the export line to your shell profile (`~/.bashrc`, `~/.zshrc`) or set it as a system environment variable on Windows.

### Optional Variables

| Variable | Purpose | Default |
| -------- | ------- | ------- |
| `GEMINI_MODEL` | Override the model used by q-topic-finetuning | `gemini-3-flash-preview` |

---

## Acknowledgments

- Inspired by [baoyu-skills](https://github.com/JimLiu/baoyu-skills) by Jim Liu
- Built for use with Claude Code and compatible AI assistants

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please submit issues or pull requests.

