# Post-Script Summary Instructions

## Narrative Summary (Agent-Authored)

IMPORTANT: This step is performed by the agent after the script finishes. `EXPLORATORY_SUMMARY.md` is
produced by reading the generated CSVs and writing a formatted document directly.

**Before writing**, read `${SKILL_DIR}/references/summary_template.md`.
This template shows the exact expected structure, table formats, and narrative style for
each section. Use it as the structural blueprint — populate it with actual data from the
generated CSVs. The template includes worked example rows for every table type.

**Step 1 — Read the CSVs:**
`01_dataset_profile.csv`, `02_data_quality.csv`, `03_nominal_frequencies.csv`,
`04_binary_summary.csv`, `05_ordinal_distribution.csv`, `06_ordinal_descriptives.csv`,
`07_discrete_descriptives.csv`, `08_continuous_descriptives.csv`,
`09_pearson_correlation.csv`, `10_spearman_correlation.csv`,
all `11_grouped_by_*.csv`, all `12_crosstab_*.csv`, all `13_text_*.csv`,
`14_temporal_trends.csv`.

**Step 2 — Write `tables-eda/EXPLORATORY_SUMMARY.md`** directly.

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
  - *Core table:* variable, N_valid, missing_count, missing_pct, M (or M_quasi_interval), Mdn, Mode, SD, IQR, Skewness, Kurtosis
  - *Detail table:* variable, Variance, Range, Min, Max, Q1_25th, Q3_75th, CV_pct, SE, CI95_lower, CI95_upper, mild_outliers_IQR1.5, extreme_outliers_IQR3.0, P10_10th, P90_90th (discrete/continuous only)
- **Narrow CSVs** (frequencies `03`, binary `04`, ordinal distribution `05`, correlations `09`/`10`, crosstabs `12`): Use the same columns as the source CSV.
- **Frequency tables:** Include all rows from the CSV (script already caps at top-N).
- **Correlation tables:** Include all pairs; bold rows where abs(r/rho) > 0.7.
- **Cross-tabs:** Include full table from CSV. If a crosstab has >10 columns, note the CSV as the authoritative source and provide a prose summary instead.
- Do not round further than the CSV already rounds.

**General rules:**
- End each section with 1-3 sentences of interpretation.
- **Every content section heading must include a `Source:` annotation** citing the CSV file(s) it draws from. Infrastructure sections (e.g., Output Files) are exempt.
- **NEVER derive findings from ad-hoc Python**. All findings must come from the generated CSVs.
- **Section omission:** If **all** source CSVs for a section are absent, omit the section entirely. If **some** source CSVs exist but others are absent, include the section and note "No [subtype] data available (file skipped by script)" for the missing part.

## Interpreting the Summary

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
