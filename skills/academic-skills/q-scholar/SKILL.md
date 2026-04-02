---
name: q-scholar
description: Academic manuscript writing suite (APA 7th). Orchestrates q-intro, q-litreview, q-eda, q-tf, q-methods, and q-results for end-to-end manuscript preparation. Use for writing papers, drafting sections, or academic writing support.
---

# Q-Scholar

Orchestrates specialized sub-skills for academic manuscript preparation following APA 7th edition standards.

## Script Directory

Agent execution instructions:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`.
2. Sub-skill path = `${SKILL_DIR}/<sub-skill>/SKILL.md`.
3. Shared reference path = `${SKILL_DIR}/references/<ref-name>`.

## Shared References

All drafting sub-skills inherit these:
- **references/apa_style_guide.md** — numbers, statistics, notation, punctuation, formulas
- **references/table_formatting.md** — APA 7th table structure and examples
- **references/appendix_template.md** — shared appendix structure for methods and results

## Sub-Skills

| Skill | Purpose |
|-------|---------|
| q-intro | Draft or refine introduction sections (phenomenon to theory to contribution) |
| q-litreview | Draft standalone literature reviews (progressive argument to earned RQs) |
| q-methods | Draft methods sections (data collection, analysis, validation procedures) |
| q-results | Draft results sections (findings with APA tables and narrative flow) |
| q-eda | Exploratory data analysis (measurement-appropriate statistics to CSV + summary) |
| q-tf | Topic finetuning (raw topics to theory-driven classification) |

## Core Writing Principles

All drafting sub-skills follow these standards:

- Narrative prose; no bullet points, em-dashes, or standalone introductory paragraphs
- Prefer 3-12 sentence paragraphs; merge pre-table intros into the post-table narrative
- No unnecessary bold or italic emphasis in running text
- Follow ../references/apa_style_guide.md for APA formatting, numbers, notation, and formulas
- Use appendices for technical details; placeholders for pending information
- Cross-section coordination: compress in the intro what the lit review elaborates; each section does distinct work
