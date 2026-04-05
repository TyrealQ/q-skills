# Interview Protocol

Before invoking the script, conduct a two-stage interview:

## Stage A: Context Questions

Ask 2 questions before loading data:

1. **Research questions** - What are you exploring? (guides which comparisons matter)
2. **Temporal column** - Is there a date/time column for trend analysis?

## Stage B: Column Classification Review

After the context questions, **auto-detect column types and present for confirmation**:

1. **Load and preview** - Run `run_eda.py --preview` to get `df.head()`, `df.dtypes`, `df.nunique()`. *(Requires Bash — if in plan mode, see Plan Mode Guard above.)*
2. **Auto-classify** - Apply the detection rules below to generate suggested types.

### Column-Type Detection Rules

Types follow Stevens' levels of measurement extended with Temporal, Text, and ID/key types.

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

4. **Ask for confirmation** - Present the table and ask the user:
   "If these all look correct, select **Confirm all**. Otherwise, select **Corrections needed**."
5. **Record confirmed types** and map to script arguments.
6. **Invoke the script immediately** — Do NOT write inline Python. Map confirmed types to `--col_types` pairs and run `run_eda.py` per invocation_guide.md.
