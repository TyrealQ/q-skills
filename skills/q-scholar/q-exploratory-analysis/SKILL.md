---
name: q-exploratory-analysis
description: "Universal exploratory data analysis for tabular datasets. Interviews the user to confirm column measurement levels, then applies appropriate analysis for each: descriptive statistics and distribution shape for numeric variables, frequency tables for categorical, proportion analysis for binary, text frequency analysis for free-text fields, and temporal trend analysis for date columns. Produces a structured TABLE/ folder of CSV outputs and a holistic EXPLORATORY_SUMMARY.md with flagged insights. Use before methods/results writing in academic workflows."
---

# Q-Exploratory-Analysis

Universal exploratory data analysis (EDA) for tabular datasets. Previews the dataset, interviews the user to confirm column measurement levels, and applies statistically appropriate analysis for each variable type, producing a structured TABLE/ folder and a holistic EXPLORATORY_SUMMARY.md with flagged insights.

> **IMPORTANT:** Run the script for CSVs and the Excel report. Write `EXPLORATORY_SUMMARY.md`
> yourself (Phase 6) by reading the CSVs and using the Write tool directly.
> Do **NOT** write inline Python for analysis.

## 1. Requirements Gathering (Interview)

Before invoking the script, conduct a two-stage interview:

### Stage A: Context Questions

Ask 2 questions before loading data:

1. **Research questions** - What are you exploring? (guides which comparisons matter)
2. **Temporal column** - Is there a date/time column for trend analysis?

### Stage B: Column Classification Review

After the context questions, **auto-detect column types and present for confirmation**:

1. **Load and preview** - Read the file with a quick Python snippet to get `df.head()`, `df.dtypes`, `df.nunique()`.
2. **Auto-classify** - Apply the heuristic rules from Section 3 to generate suggested types.
   **Pay special attention to:**
   - High-cardinality numeric integers (views, revenue, duration) — these should be **Continuous**, not ID
   - Low-cardinality integers (1-5, 1-7 scales) — ask whether Ordinal (scale) or Discrete (count)
   - Columns with >40% missing — flag for user awareness
3. **Present classification table** - Show all columns organized by suggested type:

   | # | Column | Sample Values | Unique | Suggested Type | Notes |
   |---|--------|---------------|--------|----------------|-------|
   | 1 | id | 1, 2, 3 | 768 | ID | nunique > 95% of n, non-numeric |
   | 2 | views | 100, 5000, 1M | 1885 | Continuous | high-cardinality integer metric |
   | 3 | platform | YouTube, Twitch | 5 | Nominal (Group) | grouping variable |
   | 4 | rating | 1, 2, 3, 4, 5 | 5 | Ordinal | low-cardinality integer - scale or count? |
   | ... | ... | ... | ... | ... | ... |

4. **Ask for confirmation** - Use AskUserQuestion to present the table and ask:
   "If these all look correct, select **Confirm all**. Otherwise, select **Corrections needed**."
5. **Record confirmed types** and map to script arguments.
6. **Invoke the script immediately** — Do NOT write inline Python. Run `run_eda.py` per Section 2.

   | Confirmed Type | Script Argument |
   |----------------|-----------------|
   | Ordinal | `--ordinal_cols col1 col2` |
   | Text | `--text_cols col1 col2` |
   | Nominal (Group) | `--group col1 col2` |
   | Continuous | `--continuous_cols col1 col2` |
   | ID | `--id_cols col1 col2` |
   | Binary, Discrete, Temporal | Auto-detected (no flag needed; `--no_interactive` prevents ambiguity prompts) |

## 2. Script Invocation

**Standard invocation (built from interview):**
```bash
python scripts/run_eda.py data.xlsx \
  --group platform tier \
  --text_cols description comments \
  --ordinal_cols rating satisfaction \
  --output TABLE/ \
  --no_interactive \
  --top_n 10
```

> **Windows note:** Use `python` (not `python3`). If the system has both Python 2 and 3,
> use `py -3` or the full path (e.g., `C:\Python312\python.exe`).

**Lightweight run (no Excel output):**
```bash
python scripts/run_eda.py data.xlsx \
  --group platform \
  --ordinal_cols rating \
  --output TABLE/ \
  --no_interactive \
  --no_excel
```

**Mapping from interview to arguments:**

| Confirmed Type | Script Argument |
|----------------|-----------------|
| Ordinal | `--ordinal_cols col1 col2` |
| Text | `--text_cols col1 col2` |
| Nominal (Group) | `--group col1 col2` |
| Continuous | `--continuous_cols col1 col2` |
| ID | `--id_cols col1 col2` |
| All other types | Auto-detected; no flag needed |
| (always) | `--no_interactive` (skip ambiguity prompts when Claude drives the workflow) |

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `data` | Yes | Path to input file (.xlsx or .csv) |
| `--output` | No | Output directory (default: `TABLE/`) |
| `--group` | No | Nominal columns for grouped analysis |
| `--text_cols` | No | Text columns for n-gram analysis |
| `--ordinal_cols` | No | Columns confirmed as ordinal during interview |
| `--continuous_cols` | No | Force-classify columns as continuous (overrides auto-detection) |
| `--id_cols` | No | Force-classify columns as ID/excluded (overrides auto-detection) |
| `--top_n` | No | Top-N items in frequency tables (default: 10) |
| `--no_interactive` | No | Skip ambiguity prompts (always used when Claude drives the workflow) |
| `--no_excel` | No | Skip Phase 7 (Excel report); produce CSVs and markdown only |

## 3. Column-Type Coverage

Claude presents suggested types during the interview; the user confirms or corrects before the script runs. Types follow Stevens' levels of measurement extended with Temporal, Text, and ID/key types.

| Level | Detection Rule | Analysis Applied |
|-------|---------------|-----------------|
| **ID/key** | nunique > 95% of n AND non-numeric dtype | Excluded from analysis; flagged in profile |
| **Binary** | Exactly 2 unique values (any dtype) | Count, proportion, 95% CI |
| **Nominal** | object/string dtype, avg length <= 50 chars | Frequency table, mode, top-N |
| **Ordinal** | User-confirmed low-cardinality integer | Ordered freq table + cumulative % + full quantitative metrics (M labeled quasi-interval) |
| **Discrete** | integer dtype, meaningful count/quantity | Frequency distribution + full quantitative metrics |
| **Continuous** | float dtype, OR numeric dtype with nunique > 95% of n | Full quantitative metrics + outlier flags + distribution shape |
| **Temporal** | datetime dtype or parseable date string | Range, gap detection, trend by month/year |
| **Text** | object dtype, avg length > 50 chars | Top unigrams/bigrams, avg word count, vocabulary richness |

**Numeric high-uniqueness:** Integer columns with >95% unique values (e.g., views, revenue) are classified as Continuous, not ID. Only non-numeric columns (strings, mixed types) with >95% uniqueness are treated as identifiers. Use `--id_cols` to force-classify a numeric column as ID if needed.

**Ordinal vs. Discrete ambiguity:** Claude flags low-cardinality integers (e.g., 1-5, 1-7 scales) prominently during the interview and asks whether each is a scale (Ordinal) or count (Discrete).

## 4. Eight-Phase Pipeline

### Phase 0: Data Loading & Column Classification
Loads the file, applies user-confirmed column types (passed via CLI flags), auto-detects unambiguous types for remaining columns, and prints a schema summary: column name | detected type | nunique | missing%.

### Phase 1: Dataset Profile
`01_dataset_profile.csv` - shape, column types, missing%, uniqueness, memory usage.

### Phase 2: Data Quality Assessment
`02_data_quality.csv` - missing counts/%, duplicate rows, constant columns, outlier counts per Continuous/Discrete column (IQR method).

### Phase 3: Univariate Analysis
Measurement-level-appropriate analysis for each column:

- `03_nominal_frequencies.csv` - frequency + % for each Nominal column (top-N)
- `04_binary_summary.csv` - count, proportion, 95% CI for all Binary columns
- `05_ordinal_distribution.csv` - ordered frequency + cumulative %
- `06_ordinal_descriptives.csv` - full quantitative metrics (M quasi-interval, Mdn, SD, IQR, SE, 95% CI, skewness, kurtosis, outliers)
- `07_discrete_descriptives.csv` - frequency distribution + full quantitative metrics
- `08_continuous_descriptives.csv` - full quantitative metrics (M, Mdn, Mode, SD, Var, Range, IQR, CV, Q1/Q3, skewness, kurtosis, SE, 95% CI, outlier counts)

### Phase 4: Bivariate & Multivariate Analysis
Measurement-appropriate pairing analysis:

- `09_pearson_correlation.csv` - Ratio-scale x Ratio-scale (Continuous + Discrete; r + p-value)
- `10_spearman_correlation.csv` - Ordinal x Ordinal (rho + p-value)
- `11_grouped_by_{groupvar}.csv` - Continuous/Discrete descriptives per Nominal group
- `12_crosstab_{nom1}_x_{nom2}.csv` - Nominal x Nominal contingency tables

### Phase 5: Specialized Analysis
- `13_text_{colname}.csv` - word freq, top bigrams, avg word count, vocab size
- `14_temporal_trends.csv` - key metrics over time by period

### Phase 6: Narrative Summary (Model-Authored)

IMPORTANT: This phase is performed by Claude, not by the script. `EXPLORATORY_SUMMARY.md` is
produced by Claude reading the generated CSVs and writing a formatted document with the Write tool.

**Step 1 — Read the CSVs** using the Read tool:
`01_dataset_profile.csv`, `02_data_quality.csv`, `03_nominal_frequencies.csv`,
`04_binary_summary.csv`, `05_ordinal_distribution.csv`, `06_ordinal_descriptives.csv`,
`07_discrete_descriptives.csv`, `08_continuous_descriptives.csv`,
`09_pearson_correlation.csv`, `10_spearman_correlation.csv`,
all `11_grouped_by_*.csv`, all `12_crosstab_*.csv`, all `13_text_*.csv`,
`14_temporal_trends.csv`.

**Step 2 — Write `TABLE/EXPLORATORY_SUMMARY.md`** directly using the Write tool.

**Content requirements:**
Thematic sections (not one-per-CSV). Required structure:
1. Dataset Overview *(Source: `01_dataset_profile.csv`, `14_temporal_trends.csv`)*
2. Data Quality *(Source: `02_data_quality.csv`)*
3. Categorical Variables *(Source: `03_nominal_frequencies.csv`, `04_binary_summary.csv`, `05_ordinal_distribution.csv`, `06_ordinal_descriptives.csv`)*
4. Quantitative Variables *(Source: `07_discrete_descriptives.csv`, `08_continuous_descriptives.csv`)*
5. Bivariate Relationships *(Source: `09_pearson_correlation.csv`, `10_spearman_correlation.csv`)*
6. Group Comparisons *(Source: `11_grouped_by_*.csv`)*
7. Cross-Tabulations *(Source: `12_crosstab_*.csv`)*
8. Text Analysis *(Source: `13_text_*.csv`; omit section if no text columns)*
9. Temporal Trends *(Source: `14_temporal_trends.csv`; omit section if no temporal column)*
10. Output Files — bullet list of all files in the output directory

Rules:
- Use aligned GFM markdown tables with the same columns as the source CSV.
- Do not round further than the CSV already rounds.
- End each section with 1–3 sentences of interpretation.
- Style reference: `TABLE/DESCRIPTIVE_SUMMARY.md` in the active DEMO directory.
- **Every section heading must include a `Source:` annotation** citing the CSV file(s) it draws from.
- **NEVER derive findings from ad-hoc Python**. If a CSV is missing or empty, state "No data available (file skipped by script)" rather than computing supplementary statistics.
- If a section's source CSV was skipped, omit the section entirely.

### Phase 7: Excel Report
`EXPLORATORY_REPORT.xlsx` - APA-7th formatted workbook (B&W, no color fills). Sheet 0 "Summary" contains dataset dimensions and quality highlights. Sheets 1-N contain one sheet per generated CSV (skipped if absent). All sheets use Calibri 11 pt, table-number bold rows, title italic rows, bold column headers with bottom border, and data rows with top/bottom rules only. Skip with `--no_excel`.

## 5. Output Directory Reference

```
TABLE/
├── 01_dataset_profile.csv
├── 02_data_quality.csv
├── 03_nominal_frequencies.csv
├── 04_binary_summary.csv
├── 05_ordinal_distribution.csv
├── 06_ordinal_descriptives.csv
├── 07_discrete_descriptives.csv
├── 08_continuous_descriptives.csv
├── 09_pearson_correlation.csv
├── 10_spearman_correlation.csv
├── 11_grouped_by_{groupvar}.csv     (one per group variable)
├── 12_crosstab_{nom1}_x_{nom2}.csv  (one per Nominal pair)
├── 13_text_{colname}.csv            (one per text column)
├── 14_temporal_trends.csv
├── EXPLORATORY_SUMMARY.md
└── EXPLORATORY_REPORT.xlsx          (omitted with --no_excel)
```

Files are omitted when no columns of the relevant type exist (e.g., no text columns means no `13_text_*.csv`).

## 6. Interpreting the Summary

`EXPLORATORY_SUMMARY.md` uses a flagged-insight format rather than just reporting numbers:

- **Issue flags** - *"Column X has 34% missing - review before analysis"*
- **Pattern highlights** - *"Strong positive correlation between views and likes (r=0.87, p<.001)"*
- **Distribution notes** - *"Duration is right-skewed (skewness=3.1) - median better represents typical values"*
- **Coverage summary** - *"768 records across 5 platforms; YouTube accounts for 62% of sample"*
- **Measurement caveats** - Ordinal means labeled as quasi-interval; Spearman used instead of Pearson for ranked scales

Flags use this severity scheme: high missing% -> review flag; high skewness -> distribution flag; strong correlations (|r| > 0.7) -> relationship flag; ID-like columns -> exclusion flag.

## 7. Design Principles

1. **Exploratory-first** - No confirmatory statistics; builds the picture before hypothesis testing
2. **User-confirmed classification** - Claude suggests measurement levels from heuristic rules; the user reviews and confirms before analysis runs
3. **Measurement-appropriate** - Uses median/IQR for Ordinal, Pearson for Continuous, Spearman for Ordinal, chi-square for Nominal
4. **Insight-flagging** - Summary reports patterns and warnings, not just numbers
5. **Dual output** - CSVs for validation and import into results tables; markdown for interpretation
6. **APA-compatible statistics** - Full metric set (M, Mdn, SD, SE, 95% CI, skewness, kurtosis) ready for APA 7th reporting

## 8. Verification Checklist

- [ ] Column classification table presented to user; user confirmed or corrected types
- [ ] Script invoked with `--no_interactive` and all confirmed Ordinal/Text/Group columns passed as arguments
- [ ] Phase 0 schema summary printed; all columns assigned a type consistent with user confirmation
- [ ] Each detected column type has at least one output file
- [ ] No empty CSVs (phases with no applicable columns are skipped, not empty)
- [ ] `EXPLORATORY_SUMMARY.md` written by Claude via Write tool
- [ ] All 10 thematic sections present; sections for absent column types omitted cleanly
- [ ] Every section contains at least one populated markdown table and one narrative sentence
- [ ] Numbers in the summary match the source CSVs exactly
- [ ] `EXPLORATORY_REPORT.xlsx` present with "Summary" as first sheet + one sheet per CSV (unless `--no_excel`)
- [ ] Excel workbook is B&W only (no color fills; no gridlines)
- [ ] Bivariate outputs use correct method for each level pairing
- [ ] High-cardinality numeric columns classified as Continuous, not ID (check `01_dataset_profile.csv`)
- [ ] Pearson correlations include both continuous and discrete ratio-scale columns
- [ ] Every `EXPLORATORY_SUMMARY.md` section cites its source CSV file(s) in the heading
- [ ] No ad-hoc Python used to derive findings outside the script pipeline
- [ ] Script invoked with `python` (not `python3`) on Windows

## Future Roadmap

| Enhancement | Rationale |
|-------------|-----------|
| Visualization suite | Box plots, histograms, heatmaps, violin plots per measurement level |
| Normality tests (Shapiro-Wilk for n<5000) | Formal distribution assessment for Continuous variables |
| Hypothesis generation section | Bridge EDA to confirmatory research questions |
| `ydata-profiling` HTML report | One-line automated profiling complement |
| Interval vs. Ratio distinction | Full Stevens' framework for specific research contexts |
