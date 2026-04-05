# Script Invocation Guide

## Standard Invocation

Built from interview results:

```bash
python "${SKILL_DIR}/scripts/run_eda.py" data.xlsx \
  --col_types rating=ordinal views=continuous description=text record_id=id \
  --group platform tier \
  --output tables-eda/
```

> **Windows note:** Use `python` (not `python3`). If the system has both Python 2 and 3,
> use `py -3` or the full path (e.g., `C:\Python312\python.exe`).

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `data` | Yes | Path to .xlsx or .csv |
| `--col_types` | No | Confirmed types: `col=type` pairs. Valid: id, binary, nominal, ordinal, discrete, continuous, temporal, text. Unspecified columns auto-detected. |
| `--group` | No | Nominal columns for grouped analysis |
| `--output` | No | Output directory (default: `tables-eda/`) |
| `--top_n` | No | Top-N for frequency tables (default: 10) |
| `--no_excel` | No | Skip Phase 6 (Excel report) |
| `--corr_deletion` | No | Missing-data strategy for correlations: `pairwise` (default) or `listwise` |
| `--interactive` | No | Prompt for ambiguous integers (standalone CLI only) |

## Behavioral Defaults

- `--group` omitted: grouping defaults to **all** nominal columns (no cap).
- Cross-tabs: all nominal column pairs are generated (no cap).
- ID detection: requires `n > 10` rows; otherwise high-uniqueness columns stay as their detected numeric/string type.
- `LOW_CARD_MAX = 20`: integers with <= 20 unique values are flagged as ambiguous (ordinal vs. discrete).
- `--corr_deletion` omitted: uses **pairwise** deletion (drops missing per pair, maximizing N). Use `--corr_deletion listwise` for consistent N across all pairs.
