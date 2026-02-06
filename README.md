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

### Research Promotion Skills

| Skill                             | Description                                              |
| --------------------------------- | -------------------------------------------------------- |
| [q-infographics](#q-infographics) | Convert documents into business stories and infographics |

---

## Skill Details

### q-scholar

Academic manuscript writing suite for drafting journal-ready prose following APA 7th edition standards. Orchestrates specialized sub-skills for complete manuscript preparation workflows.

**Sub-Skills:**

| Sub-Skill | Description |
| --------- | ----------- |
| q-intro | Introduction section drafting with interview-driven workflow |
| q-descriptive-analysis | Comprehensive exploratory analysis of tabular datasets |
| q-methods | Methods section drafting in clear, narrative style |
| q-results | Results section drafting with APA-compliant tables |

**Triggers:**

- "Help me write the methods and results for my study"
- "Draft a results section for this analysis"
- "Analyze this dataset and generate descriptive statistics"

**Features:**

- End-to-end manuscript support (data exploration → methods → results)
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
├── SKILL.md                              # Orchestration skill
├── references/                           # Shared style guides
│   ├── apa_style_guide.md                # Numbers, statistics, notation
│   └── table_formatting.md               # APA 7th table examples
├── q-intro/
│   ├── SKILL.md                          # Introduction drafting skill
│   └── references/                       # Templates and interview questions
├── q-descriptive-analysis/
│   └── SKILL.md                          # Data exploration skill
├── q-methods/
│   ├── SKILL.md                          # Methods drafting skill
│   └── references/                       # Methods and appendix templates
└── q-results/
    ├── SKILL.md                          # Results drafting skill
    └── references/                       # Results template
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
├── SKILL.md                                  # Main skill file
├── scripts/
│   ├── classify_outliers.py                  # Outlier reclassification via Gemini
│   ├── generate_implementation_plan.py       # Full plan generation
│   └── update_excel_with_labels.py           # Excel column updates
└── references/
    ├── esports_ugc_example.md                # Worked example
    └── SP_OUTLIER_TEMPLATE.txt               # Outlier classification prompt template
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

- Two-stage pipeline: Document → Story → Infographic
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
├── SKILL.md                              # Main skill file
├── requirements.txt                      # Python dependencies
├── assets/
│   └── Logo_Q.png                        # Brand logo, auto-overlaid on infographics
├── prompts/
│   ├── story.txt                         # Story generation prompt
│   └── image.txt                         # Infographic generation prompt
├── scripts/
│   ├── gen_story.py                      # Story generator script
│   └── gen_image.py                      # Image generator script
└── examples/                             # Sample outputs
```

**Example:**

```
Create an infographic from my research paper on gamification in esports
```

**Sample Outputs:**

![ESPORTS_INFO](skills/q-infographics/examples/ESPORTS_INFO.jpg)

![ESPORTS_GAMIFICATION_INFO](skills/q-infographics/examples/ESPORTS_GAMIFICATION_INFO.jpg)

---

## Acknowledgments

- Inspired by [baoyu-skills](https://github.com/JimLiu/baoyu-skills) by Jim Liu
- Built for use with Claude Code and compatible AI assistants

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please submit issues or pull requests.
