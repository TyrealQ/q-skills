# Q-Skills

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
Copy-Item -Recurse -Force q-skills\q-* $env:USERPROFILE\.claude\skills\
```

**macOS/Linux:**

```bash
cp -r q-skills/q-* ~/.claude/skills/
```

> **Note:** The exact skills path depends on your AI assistant. Common locations: `~/.claude/skills/`, `~/.gemini/skills/`

---

## Available Skills

### Academic Writing Skills

| Skill                | Description                                     |
| -------------------- | ----------------------------------------------- |
| [q-methods](#q-methods) | Draft methods sections for academic manuscripts |

### Data Analysis Skills

| Skill                                          | Description                                                      |
| ---------------------------------------------- | ---------------------------------------------------------------- |
| [q-topic-finetuning](#q-topic-finetuning)         | Consolidate topic modeling outputs into theory-driven frameworks |
| [q_descriptive-analysis](#q_descriptive-analysis) | Comprehensive descriptive analysis of tabular datasets           |

---

## Skill Details

### q-methods

Draft methods sections for academic manuscripts following a structured, narrative style.

**Triggers:**

- "Write a methods section for..."
- "Draft the methodology for..."
- "Help me write the methods for my paper on..."

**Features:**

- Flowing paragraph style (no bullet points or em-dashes)
- Conceptual language over implementation details
- Standard structure: Data Collection → Analysis → Validation
- Appendix templates for technical parameters

**Example:**

```
Help me write the methods section for my NLP paper analyzing social media discourse
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

**Example:**

```
Consolidate my 129 BERTopic topics using organizational legitimacy framework
```

**Reference:** See `references/esports_ugc_example.md` for complete worked example.

---

### q_descriptive-analysis

Comprehensive descriptive analysis of tabular datasets with grouped statistics and publication-ready summaries.

**Triggers:**

- "Analyze this dataset..."
- "Generate descriptive statistics for..."
- "Create a summary table for my data..."

**Features:**

- Overall and grouped descriptive statistics
- Frequency distributions by categorical variables
- Entity extraction from text columns
- Temporal dynamics analysis
- CSV output tables with MD summary reports

**Example:**

```
Analyze my survey data grouped by condition and generate descriptive tables
```

---

## Acknowledgments

- Inspired by [baoyu-skills](https://github.com/JimLiu/baoyu-skills) by Jim Liu
- Built for use with Claude Code and compatible AI assistants

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please submit issues or pull requests.
