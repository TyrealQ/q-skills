"""Standard Gemini analysis pipeline — call Gemini directly with inline media bytes.

No File API upload needed. Reads media from disk, sends via Part.from_bytes().
Output is compatible with 5review.py (per-subject checkpoints).

Usage:
    python gemini_standard.py --config path/to/config.py                # all subjects
    python gemini_standard.py --config config.py --subjects s1 s2       # specific
    python gemini_standard.py --config config.py --max-workers 25       # concurrency
    python gemini_standard.py --config config.py --preview              # dry run
"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from tqdm.auto import tqdm

load_dotenv()

# Import shared utilities from batch/utils.py
_BATCH_DIR = str(Path(__file__).resolve().parent.parent / "batch")
if _BATCH_DIR not in sys.path:
    sys.path.insert(0, _BATCH_DIR)

from utils import (
    init_config, get_config, add_config_arg,
    analyze_single_row, load_system_prompt,
    list_to_excel_str, get_client, get_all_clients,
)


# ---------------------------------------------------------------------------
# Build output DataFrame
# ---------------------------------------------------------------------------

def build_output_df(rows: list[dict], results: list[dict]) -> pd.DataFrame:
    """Merge source rows with model results into a checkpoint-compatible DataFrame."""
    cfg = get_config()
    all_keys: set[str] = set()
    for r in results:
        if r.get("ok") and isinstance(r.get("data"), dict):
            all_keys.update(r["data"].keys())
    ordered_keys = [f for f in cfg.ANALYSIS_FIELDS if f in all_keys]
    ordered_keys += sorted(all_keys - set(cfg.ANALYSIS_FIELDS))

    records = []
    for row, res in zip(rows, results):
        rec = dict(row)
        data = res.get("data", {})
        for k in ordered_keys:
            rec[k] = list_to_excel_str(data.get(k, ""))
        rec["raw_json"] = res.get("raw_json", "")
        rec["model_ok"] = bool(res.get("ok", False))
        records.append(rec)

    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Per-subject verification
# ---------------------------------------------------------------------------

def verify_subject(results: list[dict], subject: str) -> dict:
    """Validate analysis fields using config rules. Returns summary counts."""
    cfg = get_config()
    total = len(results)
    ok = sum(1 for r in results if r.get("ok"))
    errors = total - ok

    validation_issues = 0
    for r in results:
        if not r.get("ok"):
            continue
        issues = cfg.validate_row(r.get("data", {}))
        if issues:
            validation_issues += 1
            for issue in issues:
                print(f"  [WARN] {subject}: {issue}")

    return {"total": total, "ok": ok, "errors": errors,
            "validation_issues": validation_issues}


# ---------------------------------------------------------------------------
# Process one subject
# ---------------------------------------------------------------------------

def _run_batch(client, rows, indices, max_workers, subject, label, system_prompt):
    """Run analyze_single_row for a list of indices. Returns {idx: result}."""
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(analyze_single_row, client, idx, rows[idx], system_prompt): idx
            for idx in indices
        }
        for fut in tqdm(as_completed(futures), total=len(futures),
                        desc=f"  {subject} {label}", leave=False):
            idx = futures[fut]
            try:
                results[idx] = fut.result()
            except Exception as e:
                results[idx] = {"ok": False, "data": {}, "raw_json": f"[future error] {e}"}
    return results


def process_subject(client, subject: str, subject_df: pd.DataFrame,
                    max_workers: int, system_prompt: str,
                    retries: int = 2) -> dict:
    """Process all rows for a single subject with concurrent API calls.

    After the initial pass, automatically retries failed rows up to `retries`
    times, merging fixes back in before saving the final checkpoint.
    """
    cfg = get_config()
    rows = subject_df.to_dict(orient="records")

    # Check files exist on disk
    missing = 0
    for row in rows:
        abs_path = os.path.join(cfg.BASE_DIR, row.get(cfg.FILE_COL, ""))
        if not os.path.isfile(abs_path):
            missing += 1

    # Initial pass
    all_indices = list(range(len(rows)))
    batch_results = _run_batch(client, rows, all_indices, max_workers,
                               subject, "pass 1", system_prompt)
    results = [batch_results[i] for i in range(len(rows))]

    failed = [i for i, r in enumerate(results) if not r.get("ok")]
    ok_count = len(rows) - len(failed)
    print(f"  {subject}: pass 1 — {ok_count}/{len(rows)} OK, {len(failed)} errors")

    # Retry failed rows
    for attempt in range(1, retries + 1):
        if not failed:
            break
        print(f"  {subject}: retrying {len(failed)} failed rows (attempt {attempt}/{retries})...")
        retry_results = _run_batch(client, rows, failed, max_workers,
                                   subject, f"retry {attempt}", system_prompt)
        for idx, res in retry_results.items():
            results[idx] = res
        failed = [i for i, r in enumerate(results) if not r.get("ok")]
        ok_count = len(rows) - len(failed)
        print(f"  {subject}: retry {attempt} — {ok_count}/{len(rows)} OK, {len(failed)} errors")

    # Verify
    verify = verify_subject(results, subject)
    ok = verify["ok"]
    total = verify["total"]

    # Save final checkpoint
    out_df = build_output_df(rows, results)
    ckpt_path = os.path.join(cfg.STANDARD_CHECKPOINT_DIR,
                             f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
    os.makedirs(cfg.STANDARD_CHECKPOINT_DIR, exist_ok=True)
    out_df.to_excel(ckpt_path, index=False)
    print(f"  {subject}: {ok}/{total} OK, saved -> {ckpt_path}")

    return {"subject": subject, "total": total, "ok": ok,
            "errors": verify["errors"], "missing": missing}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Standard Gemini analysis pipeline (inline media bytes)")
    add_config_arg(parser)
    parser.add_argument("--subjects", nargs="*",
                        help="Process only these subject IDs")
    parser.add_argument("--players", nargs="*", dest="subjects_alias",
                        help=argparse.SUPPRESS)  # hidden backward-compat alias
    parser.add_argument("--max-workers", type=int, default=25,
                        help="Concurrent API calls per subject (default 25)")
    parser.add_argument("--retries", type=int, default=5,
                        help="Auto-retry failed rows N times (default 5)")
    parser.add_argument("--preview", action="store_true",
                        help="Dry run — show what would be processed")
    args = parser.parse_args()

    # Merge --subjects and --players alias
    subjects_filter = args.subjects or args.subjects_alias

    cfg = init_config(args.config_path)

    # Set up client (tries GOOGLE_API_KEY, then GOOGLE_API_KEY1..N)
    _api_key = os.getenv("GOOGLE_API_KEY")
    if _api_key:
        client = genai.Client(api_key=_api_key)
    else:
        clients = get_all_clients()
        client = clients[min(clients)]

    system_prompt = load_system_prompt()

    # Load data
    print(f"Loading {cfg.INPUT_PATH}...")
    df = pd.read_excel(cfg.INPUT_PATH)
    print(f"  {len(df)} rows, {df[cfg.GROUP_COL].nunique()} subjects")

    grouped = df.groupby(cfg.GROUP_COL)
    group_keys = sorted(grouped.groups.keys())

    # Filter by --subjects
    if subjects_filter:
        requested = set(subjects_filter)
        group_keys = [k for k in group_keys if cfg.subject_id(k) in requested]
        print(f"  Filtered to {len(group_keys)} requested subjects")

    # Skip existing checkpoints
    pending = []
    skipped = 0
    for key in group_keys:
        subject = cfg.subject_id(key)
        ckpt_path = os.path.join(cfg.STANDARD_CHECKPOINT_DIR,
                                 f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
        if os.path.isfile(ckpt_path):
            skipped += 1
            continue
        subject_df = grouped.get_group(key)
        pending.append((subject, key, subject_df))

    if skipped:
        print(f"  {skipped} subjects already have checkpoints (skipped)")

    if not pending:
        print("No pending subjects to process.")
        return

    # Preview mode
    if args.preview:
        print(f"\n{'Subject':<30} {'Rows':>8} {'Files Found':>12}")
        print("-" * 52)
        total_rows = 0
        total_found = 0
        for subject, _key, subject_df in pending:
            n_rows = len(subject_df)
            found = subject_df[cfg.FILE_COL].apply(
                lambda fp: os.path.isfile(os.path.join(cfg.BASE_DIR, fp))
            ).sum()
            total_rows += n_rows
            total_found += found
            flag = " !" if found < n_rows else ""
            print(f"{subject:<30} {n_rows:>8} {found:>12}{flag}")
        print("-" * 52)
        print(f"{'TOTAL':<30} {total_rows:>8} {total_found:>12}")
        print(f"\n{len(pending)} subjects, {total_rows} rows")
        return

    # Process subjects sequentially
    summaries = []
    for subject, _key, subject_df in tqdm(pending, desc="Subjects"):
        summary = process_subject(client, subject, subject_df,
                                  args.max_workers, system_prompt, args.retries)
        summaries.append(summary)

    # Final summary table
    print(f"\n{'Subject':<30} {'Total':>8} {'OK':>8}")
    print("-" * 48)
    for s in summaries:
        print(f"{s['subject']:<30} {s['total']:>8} {s['ok']:>8}")
    print("-" * 48)
    total_all = sum(s["total"] for s in summaries)
    ok_all = sum(s["ok"] for s in summaries)
    print(f"{'TOTAL':<30} {total_all:>8} {ok_all:>8}")


if __name__ == "__main__":
    main()
