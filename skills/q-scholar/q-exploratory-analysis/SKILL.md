---
name: q-exploratory-analysis
description: "Universal exploratory data analysis for tabular datasets. Auto-detects column types and applies appropriate analysis for each: descriptive statistics and distribution shape for numeric variables, frequency tables for categorical, proportion analysis for binary, text frequency analysis for free-text fields, and temporal trend analysis for date columns. Produces a structured TABLE/ folder of CSV outputs and a holistic EXPLORATORY_SUMMARY.md with flagged insights. Use before methods/results writing in academic workflows."
---

# Q-Exploratory-Analysis

Universal exploratory data analysis (EDA) for tabular datasets. Auto-detects column measurement levels and applies statistically appropriate analysis for each variable type, producing a structured TABLE/ folder and a holistic EXPLORATORY_SUMMARY.md with flagged insights.

## 1. Requirements Gathering (Interview)

Before invoking the script, ask 4 core questions:

1. **Research questions** - What are you exploring? (guides which comparisons matter)
2. **Grouping variables** - Any categorical variables to stratify by? (e.g., platform, condition, tier)
3. **Text columns** - Which free-text fields should receive n-gram and vocabulary analysis?
4. **Temporal column** - Is there a date/time column? Which metric trends over time?

Ambiguous integer columns (e.g., Likert scales 1-5, 1-7) will be flagged during the script's Phase 0 classification step. The script prompts the user to confirm whether these are Ordinal or Discrete before proceeding.

## 2. Script Invocation

**Minimal config (auto-detects all column types):**
```bash
python scripts/run_eda.py data.xlsx --output TABLE/
```

**Full config with optional overrides:**
```bash
python scripts/run_eda.py data.xlsx \
  --group platform tier \
  --text_cols description comments \
  --output TABLE/ \
  --top_n 10
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `data` | Yes | Path to input file (.xlsx or .csv) |
| `--output` | No | Output directory (default: `TABLE/`) |
| `--group` | No | Nominal columns for grouped analysis |
| `--text_cols` | No | Text columns for n-gram analysis |
| `--top_n` | No | Top-N items in frequency tables (default: 10) |

## 3. Column-Type Coverage

The script auto-detects measurement level for each column using Stevens' levels of measurement extended with Temporal, Text, and ID/key types.

| Level | Detection Rule | Analysis Applied |
|-------|---------------|-----------------|
| **ID/key** | nunique > 95% of n | Excluded from analysis; flagged in profile |
| **Binary** | Exactly 2 unique values (any dtype) | Count, proportion, 95% CI |
| **Nominal** | object/string dtype, avg length <= 50 chars | Frequency table, mode, top-N |
| **Ordinal** | User-confirmed low-cardinality integer | Ordered freq table + cumulative % + full quantitative metrics (M labeled quasi-interval) |
| **Discrete** | integer dtype, meaningful count/quantity | Frequency distribution + full quantitative metrics |
| **Continuous** | float dtype or high-cardinality integer | Full quantitative metrics + outlier flags + distribution shape |
| **Temporal** | datetime dtype or parseable date string | Range, gap detection, trend by month/year |
| **Text** | object dtype, avg length > 50 chars | Top unigrams/bigrams, avg word count, vocabulary richness |

**Ordinal vs. Discrete ambiguity:** Low-cardinality integers (e.g., 1-5, 1-7 scales) are flagged interactively. The script asks the user to confirm measurement level before classifying.

## 4. Six-Phase Pipeline

### Phase 0: Data Loading & Column Classification
Loads the file, auto-detects all column types, flags ambiguous integers for user confirmation, and prints a schema summary: column name | detected type | nunique | missing%.

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

- `09_pearson_correlation.csv` - Continuous x Continuous (r + p-value)
- `10_spearman_correlation.csv` - Ordinal x Ordinal (rho + p-value)
- `11_grouped_by_{groupvar}.csv` - Continuous/Discrete descriptives per Nominal group
- `12_crosstab_{nom1}_x_{nom2}.csv` - Nominal x Nominal contingency tables

### Phase 5: Specialized Analysis
- `13_text_{colname}.csv` - word freq, top bigrams, avg word count, vocab size
- `14_temporal_trends.csv` - key metrics over time by period

### Phase 6: Summary Report
`EXPLORATORY_SUMMARY.md` - narrative report with measurement-appropriate statistics and flagged insights (issues, patterns, distribution shape, coverage).

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

Flags use this severity scheme: high missing% -> review flag; high skewness -> distribution flag; strong correlations (|r| > 0.7) -> relationship flag; ID-like columns -> exclusion flag.

## 7. Design Principles

1. **Exploratory-first** - No confirmatory statistics; builds the picture before hypothesis testing
2. **Universal auto-detection** - Minimizes manual configuration; flags ambiguity interactively
3. **Measurement-appropriate** - Uses median/IQR for Ordinal, Pearson for Continuous, Spearman for Ordinal, chi-square for Nominal
4. **Insight-flagging** - Summary reports patterns and warnings, not just numbers
5. **Dual output** - CSVs for validation and import into results tables; markdown for interpretation
6. **APA-compatible statistics** - Full metric set (M, Mdn, SD, SE, 95% CI, skewness, kurtosis) ready for APA 7th reporting

## 8. Verification Checklist

- [ ] Phase 0 schema summary printed; all columns assigned a type
- [ ] Ambiguous integer columns resolved (confirmed Ordinal or Discrete)
- [ ] Each detected column type has at least one output file
- [ ] No empty CSVs (phases with no applicable columns are skipped, not empty)
- [ ] EXPLORATORY_SUMMARY.md contains at least 3 flagged insights
- [ ] No inline Python code blocks remain - all code is in `scripts/run_eda.py`
- [ ] Bivariate outputs use correct method for each level pairing

## Future Roadmap

| Enhancement | Rationale |
|-------------|-----------|
| Visualization suite | Box plots, histograms, heatmaps, violin plots per measurement level |
| Normality tests (Shapiro-Wilk for n<5000) | Formal distribution assessment for Continuous variables |
| Hypothesis generation section | Bridge EDA to confirmatory research questions |
| `ydata-profiling` HTML report | One-line automated profiling complement |
| Interval vs. Ratio distinction | Full Stevens' framework for specific research contexts |
