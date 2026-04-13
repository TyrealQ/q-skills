"""Final checkpoint review, fix, and merge into analysis file.

Validates all per-subject checkpoints for column order, analysis field coverage,
model_ok rates, and data quality. After review passes, merges all checkpoints
into the final output file.

Usage:
    python 5review.py --config path/to/config.py                # review only
    python 5review.py --config config.py --fix                  # fix column order
    python 5review.py --config config.py --merge                # review then merge
    python 5review.py --config config.py --subjects s1          # specific subjects
"""

import argparse
import os

import pandas as pd
from pathlib import Path

from utils import init_config, get_config, add_config_arg


TRAILING_COLS = ["raw_json", "model_ok", "retry_count"]


# ---------------------------------------------------------------------------
# Column order
# ---------------------------------------------------------------------------

def check_column_order(df: pd.DataFrame) -> list[str]:
    """Check that columns follow: source | ANALYSIS_FIELDS | trailing."""
    cfg = get_config()
    issues = []
    cols = list(df.columns)
    analysis_set = set(cfg.ANALYSIS_FIELDS)
    trailing_set = set(TRAILING_COLS)

    # Analysis field order
    analysis_in_df = [c for c in cols if c in analysis_set]
    expected_analysis = [c for c in cfg.ANALYSIS_FIELDS if c in set(cols)]
    if analysis_in_df != expected_analysis:
        issues.append("Analysis field order wrong")

    # Trailing columns after analysis fields
    last_analysis = -1
    first_trailing = len(cols)
    for i, c in enumerate(cols):
        if c in analysis_set:
            last_analysis = max(last_analysis, i)
        if c in trailing_set:
            first_trailing = min(first_trailing, i)
    if last_analysis >= 0 and first_trailing < last_analysis:
        issues.append("trailing columns not at end")

    return issues


def fix_column_order(df: pd.DataFrame) -> pd.DataFrame:
    """Reorder columns: source | ANALYSIS_FIELDS | trailing."""
    cfg = get_config()
    cols = list(df.columns)
    analysis_set = set(cfg.ANALYSIS_FIELDS)
    trailing_set = set(TRAILING_COLS)
    source_cols = [c for c in cols if c not in analysis_set and c not in trailing_set]
    analysis_cols = [c for c in cfg.ANALYSIS_FIELDS if c in set(cols)]
    trail_cols = [c for c in TRAILING_COLS if c in set(cols)]
    return df[source_cols + analysis_cols + trail_cols]


# ---------------------------------------------------------------------------
# Per-subject review
# ---------------------------------------------------------------------------

def review_checkpoint(df: pd.DataFrame, subject: str) -> dict:
    """Review a single checkpoint for quality issues."""
    cfg = get_config()
    total = len(df)
    result = {"subject": subject, "total": total, "issues": []}

    # Column order
    result["issues"].extend(check_column_order(df))

    # model_ok coverage
    if "model_ok" not in df.columns:
        result["issues"].append("missing model_ok column")
        result["ok_count"] = 0
        result["ok_pct"] = 0.0
    else:
        ok = int(df["model_ok"].astype(bool).sum())
        result["ok_count"] = ok
        result["ok_pct"] = ok / total * 100 if total else 0.0
        if ok < total:
            result["issues"].append(f"{total - ok} rows model_ok=False")

    # Analysis field presence
    missing_fields = [f for f in cfg.ANALYSIS_FIELDS if f not in df.columns]
    if missing_fields:
        result["issues"].append(f"missing fields: {missing_fields}")

    # Config-driven validation on ok rows
    if "model_ok" in df.columns:
        ok_df = df[df["model_ok"].astype(bool)]
        validation_issues = 0
        for _, row in ok_df.iterrows():
            data = {f: row.get(f) for f in cfg.ANALYSIS_FIELDS if f in ok_df.columns}
            issues = cfg.validate_row(data)
            if issues:
                validation_issues += 1
        if validation_issues:
            result["issues"].append(f"{validation_issues} rows with validation issues")

    return result


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_checkpoints(files: list[Path], output_path: str) -> pd.DataFrame:
    """Merge checkpoint files into a single DataFrame and save."""
    cfg = get_config()
    dfs = []
    for f in files:
        try:
            dfs.append(pd.read_excel(f))
        except Exception as e:
            print(f"  [WARN] Failed to read {f}: {e}")

    if not dfs:
        print("  No data to merge.")
        return pd.DataFrame()

    merged = pd.concat(dfs, ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates(subset=[cfg.FILE_COL], keep="last")
    if len(merged) < before:
        print(f"  Dropped {before - len(merged)} duplicate rows")

    merged = fix_column_order(merged)

    drop_cols = [c for c in ["retry_count"] if c in merged.columns]
    if drop_cols:
        merged = merged.drop(columns=drop_cols)

    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="xlsxwriter",
                         engine_kwargs={"options": {"strings_to_urls": False}}) as writer:
        merged.to_excel(writer, index=False)
    return merged


def print_stats(df: pd.DataFrame) -> None:
    """Print field coverage and score statistics."""
    cfg = get_config()
    total = len(df)
    if total == 0:
        return

    if "model_ok" in df.columns:
        ok = int(df["model_ok"].astype(bool).sum())
        print(f"\n  model_ok: {ok}/{total} ({ok / total * 100:.2f}%)")

    print(f"\n  {'Field':<25} {'Non-empty':>10} {'Coverage':>10}")
    print("  " + "-" * 47)
    for field in cfg.ANALYSIS_FIELDS:
        if field not in df.columns:
            print(f"  {field:<25} {'MISSING':>10} {'-':>10}")
            continue
        non_empty = df[field].notna() & (df[field].astype(str).str.strip() != "")
        count = int(non_empty.sum())
        pct = f"{count / total * 100:.1f}%"
        print(f"  {field:<25} {count:>10} {pct:>10}")

    score_fields = [f for f in cfg.ANALYSIS_FIELDS if f.endswith("_score")]
    if score_fields:
        print("\n  Score distributions:")
        for field in score_fields:
            if field in df.columns:
                numeric = pd.to_numeric(df[field], errors="coerce")
                valid = numeric.dropna()
                if len(valid) > 0:
                    print(f"    {field}: mean={valid.mean():.2f}, "
                          f"median={valid.median():.1f}, n={len(valid)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Review and merge batch checkpoints")
    add_config_arg(parser)
    parser.add_argument("--subjects", nargs="*",
                        help="Review specific subjects only")
    parser.add_argument("--players", nargs="*", dest="subjects_alias",
                        help=argparse.SUPPRESS)
    parser.add_argument("--fix", action="store_true",
                        help="Fix column order in place")
    parser.add_argument("--merge", action="store_true",
                        help="Merge all checkpoints into final output after review")
    args = parser.parse_args()

    cfg = init_config(args.config_path)

    ckpt_dir = Path(cfg.BATCH_CHECKPOINT_DIR)
    pattern = f"{cfg.CHECKPOINT_PREFIX}*.xlsx"
    files = sorted(ckpt_dir.glob(pattern))

    subjects_filter = args.subjects or args.subjects_alias
    if subjects_filter:
        requested = set(subjects_filter)
        files = [f for f in files
                 if f.stem.removeprefix(cfg.CHECKPOINT_PREFIX) in requested]

    print(f"Reviewing {len(files)} checkpoints...\n")

    total_rows = 0
    total_ok = 0
    subjects_with_issues = 0
    fixed_count = 0
    blocking_issues = False

    all_results = []
    for f in files:
        subject = f.stem.removeprefix(cfg.CHECKPOINT_PREFIX)
        df = pd.read_excel(f)
        result = review_checkpoint(df, subject)
        all_results.append(result)

        total_rows += result["total"]
        total_ok += result.get("ok_count", 0)

        if result["issues"]:
            subjects_with_issues += 1
            non_ok_issues = [i for i in result["issues"] if "model_ok=False" not in i]
            if non_ok_issues:
                blocking_issues = True

        if args.fix:
            col_issues = check_column_order(df)
            if col_issues:
                df = fix_column_order(df)
                df.to_excel(f, index=False)
                fixed_count += 1
                print(f"  Fixed: {subject}")

    # Print issues
    issue_subjects = [r for r in all_results if r["issues"]]
    if issue_subjects:
        print(f"{'Subject':<25} {'Rows':>7} {'OK %':>6}  Issues")
        print("-" * 80)
        for r in issue_subjects:
            ok_pct = f"{r['ok_pct']:.0f}%"
            for issue in r["issues"]:
                print(f"{r['subject']:<25} {r['total']:>7} {ok_pct:>6}  {issue}")
        print()

    total_errors = total_rows - total_ok
    ok_pct = total_ok / total_rows * 100 if total_rows else 0

    print(f"{'='*60}")
    print(f"Checkpoints:        {len(files)}")
    print(f"Total rows:         {total_rows:,}")
    print(f"OK rows:            {total_ok:,} ({ok_pct:.2f}%)")
    print(f"Error rows:         {total_errors:,}")
    print(f"Subjects w/ issues: {subjects_with_issues}")
    if args.fix and fixed_count:
        print(f"Fixed:              {fixed_count}")
    print(f"{'='*60}")

    if args.merge:
        if blocking_issues and not args.fix:
            print("\nBlocking issues found. Run with --fix first, then --merge.")
            return

        print(f"\nMerging {len(files)} checkpoints into {cfg.MERGED_OUTPUT}...")
        merged = merge_checkpoints(files, cfg.MERGED_OUTPUT)
        if len(merged) > 0:
            subjects = (merged[cfg.GROUP_COL].nunique()
                        if cfg.GROUP_COL in merged.columns else "?")
            print(f"  {len(merged):,} rows, {subjects} subjects")
            print_stats(merged)


if __name__ == "__main__":
    main()
