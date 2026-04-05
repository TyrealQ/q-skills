---
name: q-eda
description: Run exploratory data analysis on tabular datasets with measurement-appropriate statistics. Use for EDA, descriptive statistics, data exploration, or preparing data summaries for reports and manuscripts.
---

# Q-EDA

Universal exploratory data analysis for tabular datasets. Interviews the user to confirm column measurement levels, runs statistically appropriate analysis per variable type, and produces structured CSVs with a narrative summary.

> **IMPORTANT:** This skill requires Bash execution. Use the pre-built `scripts/run_eda.py`
> from `${SKILL_DIR}/scripts/` — do **NOT** write a new script or inline Python.
>
> **If in plan mode:** write a brief plan — *"Run q-eda skill: interview
> user for context and column types, execute run_eda.py, write
> EXPLORATORY_SUMMARY.md from generated CSVs."* — then exit plan mode immediately.
> Do NOT attempt interview stages, script execution, or any analysis while plan mode is active.

## Script Directory

Agent execution instructions:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`.
2. Script path = `${SKILL_DIR}/scripts/run_eda.py`.
3. Reference path = `${SKILL_DIR}/references/<ref-name>`.

## Dependencies

```
pandas
numpy
scipy
openpyxl   # required for .xlsx input and Phase 6 Excel report
```

Install: `pip install pandas numpy scipy openpyxl`

## References

- **references/interview_protocol.md** — two-stage interview, column classification table, and detection rules
- **references/invocation_guide.md** — script arguments, examples, and behavioral defaults
- **references/summary_instructions.md** — post-script summary instructions, table formatting rules, flagging thresholds
- **references/summary_template.md** — structural blueprint for EXPLORATORY_SUMMARY.md
- **../references/apa_style_guide.md** — APA formatting, numbers, notation

## Core Principles

- Exploratory-first: no confirmatory statistics; build the picture before hypothesis testing
- User-confirmed classification: suggest measurement levels; user confirms before analysis runs
- Measurement-appropriate methods: median/IQR for ordinal, Pearson for continuous, Spearman for ordinal, cross-tabs for nominal
- Insight-flagging: report patterns and warnings, not just numbers
- Dual output: CSVs for validation and import; markdown for interpretation
- APA-compatible statistics: full metric set (M, Mdn, SD, SE, 95% CI, skewness, kurtosis) ready for reporting

## Workflow

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Interview: context questions, then column classification with user confirmation | references/interview_protocol.md |
| 2 | Execute: run `run_eda.py` with confirmed types (see Pipeline below) | references/invocation_guide.md |
| 3 | Summarize: write `tables-eda/EXPLORATORY_SUMMARY.md` from generated CSVs | references/summary_template.md, references/summary_instructions.md |

### Pipeline (Step 2 output)

| Phase | Output | Content |
|-------|--------|---------|
| 0 | *(console)* | Data loading, column classification, schema summary |
| 1 | `01_dataset_profile.csv` | Shape, column types, missing%, uniqueness |
| 2 | `02_data_quality.csv` | Missing counts/%, duplicates, constant columns, outliers (IQR) |
| 3 | `03`-`08_*.csv` | Univariate: nominal frequencies, binary summary, ordinal/discrete/continuous descriptives |
| 4 | `09`-`12_*.csv` | Bivariate: Pearson/Spearman correlations, grouped descriptives, cross-tabs |
| 5 | `13`-`14_*.csv` | Specialized: text analysis, temporal trends |
| 6 | `EXPLORATORY_REPORT.xlsx` | APA-7th formatted workbook (B&W, one sheet per CSV) |

Files are omitted when no columns of that type exist. Output directory: `tables-eda/`.

## Scope

**Include:** Any .xlsx/.csv dataset — academic, business, or general. Outputs feed directly into q-methods and q-results.

**Exclude:** Confirmatory statistics, visualization, hypothesis testing, data cleaning beyond script internals.

## Checklist

- [ ] Column classification table presented and confirmed by user
- [ ] Confirmed types passed via `--col_types`; grouping columns via `--group`
- [ ] Each detected column type has at least one output file
- [ ] `EXPLORATORY_SUMMARY.md` follows references/summary_template.md structure
- [ ] Descriptive tables use core + detail split-table format
- [ ] Every content section cites its source CSV in the heading
- [ ] Numbers in the summary match the source CSVs exactly
- [ ] No ad-hoc Python used to derive findings outside the script pipeline
