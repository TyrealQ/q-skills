# EXPLORATORY_SUMMARY.md — Template

> Reference template for `EXPLORATORY_SUMMARY.md` generation.
> Each section shows the expected structure with one worked example row per table type.
> Omit sections whose source CSVs are entirely absent; see two-tier omission rule in SKILL.md.

---

## 1. Dataset Overview *(Source: `01_dataset_profile.csv`, `14_temporal_trends.csv`)*


| Metric         | Value                            |
| -------------- | -------------------------------- |
| Rows           | 768                              |
| Columns        | 12                               |
| Temporal range | Jan 2022 – Dec 2024 (36 periods) |
| Memory usage   | 1.2 MB                           |


The dataset contains 768 records across 12 variables spanning 36 monthly periods.

---

## 2. Data Quality *(Source: `02_data_quality.csv`)*


| Column    | Missing_n | Missing_pct | Duplicate_rows | Constant | Outlier_count |
| --------- | --------- | ----------- | -------------- | -------- | ------------- |
| income    | 42        | 5.5%        | —              | —        | 18            |
| age       | 0         | 0.0%        | —              | —        | 3             |
| *Overall* | —         | —           | 12             | 0        | —             |


Income has 5.5% missing values — below the 20% review threshold. Twelve duplicate rows should be investigated before analysis.

---

## 3. Nominal Variables *(Source: `03_nominal_frequencies.csv`)*


| variable | value   | count | pct   |
| -------- | ------- | ----- | ----- |
| platform | YouTube | 476   | 62.0% |
| platform | Twitch  | 154   | 20.1% |
| platform | TikTok  | 138   | 17.9% |


YouTube dominates the sample at 62%, suggesting findings may primarily reflect YouTube-specific patterns.

---

## 4. Binary Variables *(Source: `04_binary_summary.csv`)*


| variable | value | count | proportion | CI95_lower | CI95_upper |
| -------- | ----- | ----- | ---------- | ---------- | ---------- |
| verified | True  | 512   | 0.667      | 0.633      | 0.700      |
| verified | False | 256   | 0.333      | 0.300      | 0.367      |


Two-thirds of accounts are verified (66.7%, 95% CI [63.3%, 70.0%]).

---

## 5. Ordinal Variables *(Source: `05_ordinal_distribution.csv`, `06_ordinal_descriptives.csv`)*

**Distribution:**


| variable | value | count | pct   | cumulative_pct |
| -------- | ----- | ----- | ----- | -------------- |
| rating   | 1     | 38    | 4.9%  | 4.9%           |
| rating   | 5     | 245   | 31.9% | 100.0%         |


**Descriptives — Core:**


| variable | N_valid | M_quasi_interval | Mdn  | SD   | IQR  | Skewness | Kurtosis |
| -------- | ------- | ---------------- | ---- | ---- | ---- | -------- | -------- |
| rating   | 768     | 3.82             | 4.00 | 1.14 | 2.00 | -0.65    | -0.32    |


**Descriptives — Detail:**


| variable | Range | Min | Max | Q1_25th | Q3_75th | CV_pct | SE    | CI95_lower | CI95_upper | Mild_outliers_IQR1.5 | Extreme_outliers_IQR3.0 |
| -------- | ----- | --- | --- | ------- | ------- | ------ | ----- | ---------- | ---------- | -------------------- | ----------------------- |
| rating   | 4     | 1   | 5   | 3.00    | 5.00    | 29.8%  | 0.041 | 3.74       | 3.90       | 0                    | 0                       |


Ratings are moderately left-skewed (skewness = -0.65) with the median at 4, indicating generally positive assessments. Quasi-interval mean (3.82) is reported for reference but should be interpreted cautiously given the ordinal scale.

---

## 6. Discrete Variables *(Source: `07_discrete_descriptives.csv`)*

**Core:**


| variable  | N_valid | M    | Mdn  | SD   | IQR  | Skewness | Kurtosis |
| --------- | ------- | ---- | ---- | ---- | ---- | -------- | -------- |
| num_posts | 768     | 24.3 | 18.0 | 19.7 | 22.0 | 1.84     | 4.12     |


**Detail:**


| variable  | Range | Min | Max | Q1_25th | Q3_75th | CV_pct | SE    | CI95_lower | CI95_upper | Mild_outliers_IQR1.5 | Extreme_outliers_IQR3.0 |
| --------- | ----- | --- | --- | ------- | ------- | ------ | ----- | ---------- | ---------- | -------------------- | ----------------------- |
| num_posts | 98    | 1   | 99  | 8.00    | 30.00   | 81.1%  | 0.711 | 22.9       | 25.7       | 24                   | 3                       |


Post counts are right-skewed (1.84) with 24 IQR-flagged outliers representing highly active accounts.

---

## 7. Continuous Variables *(Source: `08_continuous_descriptives.csv`)*

**Core:**


| variable | N_valid | M     | Mdn   | SD    | IQR   | Skewness | Kurtosis |
| -------- | ------- | ----- | ----- | ----- | ----- | -------- | -------- |
| views    | 768     | 45200 | 12400 | 89100 | 31000 | 3.41     | 15.8     |


**Detail:**


| variable | Range  | Min | Max    | Q1_25th | Q3_75th | CV_pct | SE   | CI95_lower | CI95_upper | Mild_outliers_IQR1.5 | Extreme_outliers_IQR3.0 |
| -------- | ------ | --- | ------ | ------- | ------- | ------ | ---- | ---------- | ---------- | -------------------- | ----------------------- |
| views    | 998000 | 12  | 998012 | 2100    | 33100   | 197.1% | 3214 | 38900      | 51500      | 87                   | 12                      |


> **Flags:** Views shows high skewness (3.41 > 2), high kurtosis (15.8 > 7), and extreme variability (CV = 197.1% > 100%). Median (12,400) better represents typical values than the mean (45,200).

---

## 8. Bivariate Relationships *(Source: `09_pearson_correlation.csv`, `10_spearman_correlation.csv`)*

**Pearson (continuous + discrete):**


| var1      | var2      | r        | p_value   |
| --------- | --------- | -------- | --------- |
| **views** | **likes** | **0.87** | **<.001** |
| views     | num_posts | 0.34     | <.001     |


**Spearman (ordinal):**


| var1   | var2         | rho  | p_value |
| ------ | ------------ | ---- | ------- |
| rating | satisfaction | 0.62 | <.001   |


> **Flag:** Strong positive correlation between views and likes (r = 0.87) — these variables share substantial variance and may be redundant in regression models.

---

## 9. Group Comparisons *(Source: `11_grouped_by_platform.csv`)*


| platform | variable | N   | M     | Mdn   | SD     |
| -------- | -------- | --- | ----- | ----- | ------ |
| YouTube  | views    | 476 | 58400 | 18200 | 102000 |
| Twitch   | views    | 154 | 31200 | 8900  | 54300  |
| TikTok   | views    | 138 | 22100 | 7100  | 41200  |


YouTube creators show the highest average views (M = 58,400) but also the greatest variability (SD = 102,000), suggesting a wide performance spread on that platform.

---

## 10. Cross-Tabulations *(Source: `12_crosstab_platform_x_verified.csv`)*


| platform | verified=True | verified=False | Total |
| -------- | ------------- | -------------- | ----- |
| YouTube  | 342           | 134            | 476   |
| Twitch   | 98            | 56             | 154   |
| TikTok   | 72            | 66             | 138   |


Verification rates vary by platform: YouTube (71.8%) > Twitch (63.6%) > TikTok (52.2%), suggesting platform-specific verification norms.

---

## 11. Text Analysis *(Source: `13_text_description.csv`)*

*Omit this section entirely if no text columns exist.*


| metric          | value               |
| --------------- | ------------------- |
| avg_word_count  | 42.3                |
| vocabulary_size | 8,412               |
| top_unigram     | "video" (n=1,204)   |
| top_bigram      | "check out" (n=387) |


Descriptions average 42 words with "video" and "check out" as dominant terms, reflecting promotional language patterns.

---

## 12. Temporal Trends *(Source: `14_temporal_trends.csv`)*

*Omit this section entirely if no temporal column exists.*


| period  | n_records | mean_views | mean_likes |
| ------- | --------- | ---------- | ---------- |
| 2022-01 | 18        | 32100      | 1240       |
| 2024-12 | 28        | 61400      | 3180       |


Views and engagement show steady growth over 36 months, with a notable acceleration in Q3 2024.

---

## 13. Output Files

- `01_dataset_profile.csv` — Dataset shape, column types, missing%, uniqueness
- `02_data_quality.csv` — Missing data, duplicates, constant columns, outliers
- `03_nominal_frequencies.csv` — Frequency tables for nominal variables
- `04_binary_summary.csv` — Proportions and 95% CI for binary variables
- `05_ordinal_distribution.csv` — Ordered frequency + cumulative %
- `06_ordinal_descriptives.csv` — Quasi-interval descriptive statistics
- `07_discrete_descriptives.csv` — Discrete variable descriptives
- `08_continuous_descriptives.csv` — Continuous variable descriptives
- `09_pearson_correlation.csv` — Pearson r for ratio-scale pairs
- `10_spearman_correlation.csv` — Spearman rho for ordinal pairs
- `11_grouped_by_platform.csv` — Descriptives by group
- `12_crosstab_platform_x_verified.csv` — Contingency table
- `13_text_description.csv` — Text analysis metrics
- `14_temporal_trends.csv` — Key metrics over time
- `EXPLORATORY_REPORT.xlsx` — APA-formatted Excel workbook
- `EXPLORATORY_SUMMARY.md` — This file

