---
name: q-exploratory-analysis
description: "Universal exploratory data analysis for tabular datasets. Interviews the user to confirm column measurement levels, then applies appropriate analysis for each: descriptive statistics and distribution shape for numeric variables, frequency tables for categorical, proportion analysis for binary, text frequency analysis for free-text fields, and temporal trend analysis for date columns. Produces a structured TABLE/ folder of CSV outputs and a holistic EXPLORATORY_SUMMARY.md with flagged insights. Use before methods/results writing in academic workflows."
---

# Q-Exploratory-Analysis

Universal exploratory data analysis (EDA) for tabular datasets. Previews the dataset, interviews the user to confirm column measurement levels, and applies statistically appropriate analysis for each variable type, producing a structured TABLE/ folder and a holistic EXPLORATORY_SUMMARY.md with flagged insights.

> **IMPORTANT:** The skill includes a pre-built `scripts/run_eda.py`. Copy it from
> `${SKILL_DIR}/scripts/` — do **NOT** write a new script from scratch. Run it (Phases 0-6)
> for CSVs and the Excel report. Then write `EXPLORATORY_SUMMARY.md` yourself (Post-Script
> step) by reading the CSVs, consulting `${SKILL_DIR}/references/summary_template.md` for
> structure, and using the Write tool directly. Do **NOT** write inline Python for analysis.

## 0. Dependencies

```
pandas
numpy
scipy
openpyxl   # required for .xlsx input and Phase 6 Excel report
```

Install: `pip install pandas numpy scipy openpyxl`

## 0b. Script Deployment

Agent execution instructions:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`.
2. Script path = `${SKILL_DIR}/scripts/run_eda.py`.
3. Reference path = `${SKILL_DIR}/references/summary_template.md`.

The skill ships a pre-built `scripts/run_eda.py`. **Do NOT write a new script.**

**Deploy the script to the project before first run:**
```bash
mkdir -p scripts
cp "${SKILL_DIR}/scripts/run_eda.py" scripts/run_eda.py
```

> **Windows equivalent:** `mkdir scripts 2>nul & copy "%SKILL_DIR%\scripts\run_eda.py" scripts\run_eda.py`
> Or in PowerShell: `New-Item -ItemType Directory -Force scripts; Copy-Item "$env:SKILL_DIR/scripts/run_eda.py" scripts/run_eda.py`

If the project already has `scripts/run_eda.py`, verify it matches the skill version
before running (the skill version is authoritative).

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
6. **Invoke the script immediately** — Do NOT write inline Python. Map confirmed types to `--col_types` pairs and run `run_eda.py` per Section 2.

## 2. Script Invocation

**Standard invocation (built from interview):**
```bash
python scripts/run_eda.py data.xlsx \
  --col_types rating=ordinal views=continuous description=text record_id=id \
  --group platform tier \
  --output TABLE/
```

> **Windows note:** Use `python` (not `python3`). If the system has both Python 2 and 3,
> use `py -3` or the full path (e.g., `C:\Python312\python.exe`).

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `data` | Yes | Path to .xlsx or .csv |
| `--col_types` | No | Confirmed types: `col=type` pairs. Valid: id, binary, nominal, ordinal, discrete, continuous, temporal, text. Unspecified columns auto-detected. |
| `--group` | No | Nominal columns for grouped analysis |
| `--output` | No | Output directory (default: `TABLE/`) |
| `--top_n` | No | Top-N for frequency tables (default: 10) |
| `--no_excel` | No | Skip Phase 6 (Excel report) |
| `--corr_deletion` | No | Missing-data strategy for correlations: `pairwise` (default) or `listwise` |
| `--interactive` | No | Prompt for ambiguous integers (standalone CLI only) |

**Behavioral defaults:**
- `--group` omitted: grouping defaults to **all** nominal columns (no cap).
- Cross-tabs: all nominal column pairs are generated (no cap).
- ID detection: requires `n > 10` rows; otherwise high-uniqueness columns stay as their detected numeric/string type.
- `LOW_CARD_MAX = 20`: integers with <= 20 unique values are flagged as ambiguous (ordinal vs. discrete).
- `--corr_deletion` omitted: uses **pairwise** deletion (drops missing per pair, maximizing N). Use `--corr_deletion listwise` for consistent N across all pairs.

## 3. Column-Type Coverage

Claude presents suggested types during the interview; the user confirms or corrects before the script runs. Types follow Stevens' levels of measurement extended with Temporal, Text, and ID/key types.

| Level | Detection Rule | Analysis Applied |
|-------|---------------|-----------------|
| **ID/key** | nunique > 95% of n AND non-numeric dtype | Excluded from analysis; flagged in profile |
| **Binary** | Exactly 2 unique values (any dtype) | Count, proportion, 95% CI |
| **Nominal** | object/string dtype, avg length <= 50 chars | Frequency table, mode, top-N |
| **Ordinal** | User-confirmed low-cardinality integer | Ordered freq table + cumulative % + full quantitative metrics (M labeled quasi-interval) |
| **Discrete** | integer dtype, meaningful count/quantity | Full quantitative metrics (M, Mdn, Mode, SD, Var, Range, IQR, CV, Q1/Q3, skewness, kurtosis, SE, 95% CI, outlier counts) |
| **Continuous** | float dtype, OR numeric with nunique > 95% of n (n > 10) | Full quantitative metrics + outlier flags + distribution shape |
| **Temporal** | datetime dtype or parseable date string | Monthly aggregated trend table (mean/median per period); gap detection not yet implemented |
| **Text** | object dtype, avg length > 50 chars | Top unigrams/bigrams, avg word count, vocabulary richness |

## 4. Pipeline

### Phase 0: Data Loading & Column Classification
Loads the file, applies user-confirmed column types (passed via `--col_types`), auto-detects unambiguous types for remaining columns, and prints a schema summary: column name | detected type | nunique | missing%.

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
- `07_discrete_descriptives.csv` - full quantitative metrics (M, Mdn, Mode, SD, Var, Range, IQR, CV, Q1/Q3, skewness, kurtosis, SE, 95% CI, outlier counts)
- `08_continuous_descriptives.csv` - full quantitative metrics (M, Mdn, Mode, SD, Var, Range, IQR, CV, Q1/Q3, skewness, kurtosis, SE, 95% CI, outlier counts)

### Phase 4: Bivariate & Multivariate Analysis
Measurement-appropriate pairing analysis:

- `09_pearson_correlation.csv` - Ratio-scale x Ratio-scale (Continuous + Discrete; r + p-value; pairwise deletion by default)
- `10_spearman_correlation.csv` - Ordinal x Ordinal (rho + p-value; pairwise deletion by default)
- `11_grouped_by_{groupvar}.csv` - Continuous/Discrete/Ordinal descriptives per Nominal group
- `12_crosstab_{nom1}_x_{nom2}.csv` - Nominal x Nominal contingency tables

### Phase 5: Specialized Analysis
- `13_text_{colname}.csv` - word freq, top bigrams, avg word count, vocab size
- `14_temporal_trends.csv` - key metrics over time by period

### Phase 6: Excel Report
`EXPLORATORY_REPORT.xlsx` - APA-7th formatted workbook (B&W, no color fills). Sheet 0 "Summary" contains dataset dimensions and quality highlights. Sheets 1-N contain one sheet per generated CSV (skipped if absent). All sheets use Calibri 11 pt, table-number bold rows, title italic rows, bold column headers with bottom border, and data rows with top/bottom rules only. Skip with `--no_excel`.

### Post-Script: Narrative Summary (Model-Authored)

IMPORTANT: This step is performed by Claude after the script finishes. `EXPLORATORY_SUMMARY.md` is
produced by Claude reading the generated CSVs and writing a formatted document with the Write tool.

**Before writing**, read `${SKILL_DIR}/references/summary_template.md`.
This template shows the exact expected structure, table formats, and narrative style for
each section. Use it as the structural blueprint — populate it with actual data from the
generated CSVs. The template includes worked example rows for every table type.

**Step 1 — Read the CSVs** using the Read tool:
`01_dataset_profile.csv`, `02_data_quality.csv`, `03_nominal_frequencies.csv`,
`04_binary_summary.csv`, `05_ordinal_distribution.csv`, `06_ordinal_descriptives.csv`,
`07_discrete_descriptives.csv`, `08_continuous_descriptives.csv`,
`09_pearson_correlation.csv`, `10_spearman_correlation.csv`,
all `11_grouped_by_*.csv`, all `12_crosstab_*.csv`, all `13_text_*.csv`,
`14_temporal_trends.csv`.

**Step 2 — Write `TABLE/EXPLORATORY_SUMMARY.md`** directly using the Write tool.

**Content requirements:**
One section per measurement level plus infrastructure sections. Required structure:
1. Dataset Overview *(Source: `01_dataset_profile.csv`, `14_temporal_trends.csv` — temporal range and period count only)*
2. Data Quality *(Source: `02_data_quality.csv`)*
3. Nominal Variables *(Source: `03_nominal_frequencies.csv`)*
4. Binary Variables *(Source: `04_binary_summary.csv`)*
5. Ordinal Variables *(Source: `05_ordinal_distribution.csv`, `06_ordinal_descriptives.csv`)*
6. Discrete Variables *(Source: `07_discrete_descriptives.csv`)*
7. Continuous Variables *(Source: `08_continuous_descriptives.csv`)*
8. Bivariate Relationships *(Source: `09_pearson_correlation.csv`, `10_spearman_correlation.csv`)*
9. Group Comparisons *(Source: `11_grouped_by_*.csv`)*
10. Cross-Tabulations *(Source: `12_crosstab_*.csv`)*
11. Text Analysis *(Source: `13_text_*.csv`; omit section if no text columns)*
12. Temporal Trends *(Source: `14_temporal_trends.csv`; omit section if no temporal column — full trend table and pattern interpretation here)*
13. Output Files — bullet list of all files in the output directory

**Table formatting rules:**
- **Descriptive tables** (ordinal `06`, discrete `07`, continuous `08`): Split into two tables:
  - *Core table:* variable, N_valid, M (or M_quasi_interval), Mdn, SD, IQR, Skewness, Kurtosis
  - *Detail table:* variable, Range, Min, Max, Q1_25th, Q3_75th, CV_pct, SE, CI95_lower, CI95_upper, outlier counts
- **Narrow CSVs** (frequencies `03`, binary `04`, ordinal distribution `05`, correlations `09`/`10`, crosstabs `12`): Use the same columns as the source CSV.
- **Frequency tables:** Include all rows from the CSV (script already caps at top-N).
- **Correlation tables:** Include all pairs; bold rows where abs(r/rho) > 0.7.
- **Cross-tabs:** Include full table from CSV. If a crosstab has >10 columns, note the CSV as the authoritative source and provide a prose summary instead.
- Do not round further than the CSV already rounds.

**General rules:**
- End each section with 1–3 sentences of interpretation.
- **Every section heading must include a `Source:` annotation** citing the CSV file(s) it draws from.
- **NEVER derive findings from ad-hoc Python**. All findings must come from the generated CSVs.
- **Section omission:** If **all** source CSVs for a section are absent, omit the section entirely. If **some** source CSVs exist but others are absent, include the section and note "No [subtype] data available (file skipped by script)" for the missing part.

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
├── EXPLORATORY_REPORT.xlsx          (omitted with --no_excel)
└── EXPLORATORY_SUMMARY.md
```

Files are omitted when no columns of the relevant type exist (e.g., no text columns means no `13_text_*.csv`).

## 6. Interpreting the Summary

`EXPLORATORY_SUMMARY.md` uses a flagged-insight format rather than just reporting numbers:

- **Issue flags** - *"Column X has 34% missing - review before analysis"*
- **Pattern highlights** - *"Strong positive correlation between views and likes (r=0.87, p<.001)"*
- **Distribution notes** - *"Duration is right-skewed (skewness=3.1) - median better represents typical values"*
- **Coverage summary** - *"768 records across 5 platforms; YouTube accounts for 62% of sample"*
- **Measurement caveats** - Ordinal means labeled as quasi-interval; Spearman used instead of Pearson for ranked scales

**Flagging thresholds:**

| Flag | Threshold | Severity |
|------|-----------|----------|
| Missing data | >20% of rows | review |
| Skewness | abs(skew) > 2 | distribution |
| Kurtosis | abs(kurt) > 7 | distribution |
| Correlation | abs(r/rho) > 0.7 | relationship |
| CV | >100% | variability |
| ID-like column | nunique > 95% of n | exclusion |

## 7. Design Principles

1. **Exploratory-first** - No confirmatory statistics; builds the picture before hypothesis testing
2. **User-confirmed classification** - Claude suggests measurement levels from heuristic rules; the user reviews and confirms before analysis runs
3. **Measurement-appropriate** - Uses median/IQR for Ordinal, Pearson for Continuous, Spearman for Ordinal, cross-tabulation for Nominal
4. **Insight-flagging** - Summary reports patterns and warnings, not just numbers
5. **Dual output** - CSVs for validation and import into results tables; markdown for interpretation
6. **APA-compatible statistics** - Full metric set (M, Mdn, SD, SE, 95% CI, skewness, kurtosis) ready for APA 7th reporting

## 8. Verification Checklist

- [ ] Column classification table presented to user; user confirmed or corrected types
- [ ] Confirmed types passed via `--col_types` and grouping columns via `--group`
- [ ] Each detected column type has at least one output file
- [ ] `EXPLORATORY_SUMMARY.md` written by Claude via Write tool
- [ ] All 13 content sections present where applicable; sections for absent column types omitted per two-tier rule
- [ ] Descriptive tables (ordinal/discrete/continuous) use core + detail split-table format
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
