"""Submit multi-subject batch jobs from JSONL files.

Reads JSONL files from <JSONL_DIR>/<BATCH_PREFIX>*.jsonl, checks
batch_jobs.csv for already-submitted jobs, submits new ones.
Writes subjects column and key_id to CSV for downstream result splitting.
"""

import argparse
import os
from pathlib import Path

from utils import (
    init_config, get_config, add_config_arg,
    get_client, get_uri_map_key_id,
    read_job_log, extract_subjects_from_jsonl, submit_batch,
    TERMINAL_FAILED,
)


def infer_key_id_from_subjects(subjects: list[str]) -> int:
    """Infer key_id from the first subject's URI map (defaults to 1)."""
    for s in subjects:
        kid = get_uri_map_key_id(s)
        if kid:
            return kid
    return 1


def main():
    parser = argparse.ArgumentParser(description="Submit multi-subject batch jobs")
    add_config_arg(parser)
    parser.add_argument("--preview", action="store_true",
                        help="List batch files ready to submit")
    parser.add_argument("--key", type=int, default=0,
                        help="Override API key ID (0 = auto-detect from URI maps)")
    args = parser.parse_args()

    cfg = init_config(args.config_path)

    # Scan for batch JSONL files
    jsonl_files = sorted(Path(cfg.JSONL_DIR).glob(f"{cfg.BATCH_PREFIX}*.jsonl"))
    if not jsonl_files:
        print(f"No {cfg.BATCH_PREFIX}*.jsonl files found. Run 1buildJsonl.py first.")
        return

    # Read existing job log, allow resubmission after terminal failure
    log_rows = read_job_log(cfg.JOB_LOG_PATH)
    submitted_names = {
        r["display_name"] for r in log_rows
        if r.get("state", "") not in TERMINAL_FAILED
    }

    # Determine what's pending
    pending = []
    already = 0
    for jpath in jsonl_files:
        display_name = jpath.stem
        if display_name in submitted_names:
            already += 1
        else:
            subjects = extract_subjects_from_jsonl(str(jpath))
            key_id = args.key if args.key > 0 else infer_key_id_from_subjects(subjects)
            pending.append((str(jpath), display_name, subjects, key_id))

    if args.preview:
        print(f"\n{already} already submitted, {len(pending)} ready to submit:\n")
        print(f"{'Batch':<25} {'Size (KB)':>12} {'Subjects':>10} {'Key':>5} {'IDs'}")
        print("-" * 95)
        for jpath, display_name, subjects, key_id in pending:
            size_kb = os.path.getsize(jpath) / 1024
            print(f"{display_name:<25} {size_kb:>12.0f} {len(subjects):>10} {key_id:>5} "
                  f"{';'.join(subjects[:5])}{'...' if len(subjects) > 5 else ''}")
        return

    if not pending:
        print(f"All {already} batch files already submitted. Nothing to do.")
        return

    submitted = 0
    failed = 0

    for jpath, display_name, subjects, key_id in pending:
        subjects_str = ";".join(subjects)
        print(f"\nSubmitting: {display_name} ({len(subjects)} subjects, key={key_id})")
        try:
            client = get_client(key_id)
            submit_batch(
                client, cfg.MODEL, jpath,
                display_name=display_name,
                job_log_path=cfg.JOB_LOG_PATH,
                subjects=subjects_str,
                key_id=key_id,
            )
            submitted += 1
        except Exception as e:
            print(f"  [ERROR] Failed to submit {display_name}: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"COMPLETE: {submitted} submitted, {already} already done, {failed} failed")
    print(f"  Total submitted (excl. failed): {already + submitted}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
