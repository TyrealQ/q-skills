"""Build multi-subject batch JSONL files from saved URI maps.

Reads per-subject URI maps from <URI_MAP_DIR>/<subject_id>.json,
combines multiple subjects into batch JSONL files for efficient submission.
Groups subjects by key_id to ensure all URIs in a JSONL belong to the same project.

Output: <JSONL_DIR>/<BATCH_PREFIX>NNN.jsonl
"""

import argparse
import os
import re
from pathlib import Path

import pandas as pd

from utils import (
    init_config, get_config, add_config_arg,
    TERMINAL_FAILED,
    load_uri_map, load_system_prompt, get_uri_map_key_id,
    read_job_log, submit_batch, get_client, build_batch_jsonl,
)


def get_subject_media_size(rows: list[dict]) -> int:
    """Sum file sizes on disk for a subject's rows."""
    cfg = get_config()
    return sum(
        os.path.getsize(os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]))
        for r in rows
        if os.path.isfile(os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]))
    )


def next_batch_number() -> int:
    """Scan existing batch JSONL files for next available batch number."""
    cfg = get_config()
    existing = list(Path(cfg.JSONL_DIR).glob(f"{cfg.BATCH_PREFIX}*.jsonl"))
    numbers = []
    for f in existing:
        m = re.match(re.escape(cfg.BATCH_PREFIX) + r"(\d+)\.jsonl$", f.name)
        if m:
            numbers.append(int(m.group(1)))
    return max(numbers, default=0) + 1


def already_batched_subjects() -> set[str]:
    """Read batch_jobs.csv to find already-batched subjects.

    Excludes subjects from failed/cancelled/expired jobs so they can be re-batched.
    """
    cfg = get_config()
    if not os.path.isfile(cfg.JOB_LOG_PATH):
        return set()
    subjects = set()
    log_rows = read_job_log(cfg.JOB_LOG_PATH)
    for row in log_rows:
        state = row.get("state", "")
        if state in TERMINAL_FAILED:
            continue
        # Check both new "subjects" and legacy "handles" columns
        s = row.get("subjects", "") or row.get("handles", "")
        if s:
            subjects.update(s.split(";"))
    return subjects


def preview_subjects(
    subject_groups: list[tuple[str, list[dict], dict[str, str]]],
    batch_size: int,
    max_batch_gb: float = 0,
) -> None:
    """Report expected batch assignments and line counts."""
    cfg = get_config()
    total_rows = 0
    total_with_uri = 0
    total_media_bytes = 0

    print(f"\n{'Subject':<30} {'Rows':>8} {'With URI':>10} {'Media MB':>10} {'Key':>5}")
    print("-" * 67)
    for subject, rows, uri_map in subject_groups:
        n_rows = len(rows)
        total_rows += n_rows
        with_uri = sum(1 for r in rows
                       if os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]) in uri_map)
        total_with_uri += with_uri
        media_bytes = get_subject_media_size(rows)
        total_media_bytes += media_bytes
        key_id = get_uri_map_key_id(subject)
        flag = " !" if with_uri < n_rows else ""
        print(f"{subject:<30} {n_rows:>8} {with_uri:>10} {media_bytes/1024**2:>10.0f} {key_id:>5}{flag}")
    print("-" * 67)
    print(f"{'TOTAL':<30} {total_rows:>8} {total_with_uri:>10} {total_media_bytes/1024**2:>10.0f}")

    n_subjects = len(subject_groups)
    if max_batch_gb > 0:
        max_bytes = max_batch_gb * 1024**3
        n_batches, current_size = 1, 0
        for _, rows, _ in subject_groups:
            s_bytes = get_subject_media_size(rows)
            if current_size > 0 and current_size + s_bytes > max_bytes:
                n_batches += 1
                current_size = 0
            current_size += s_bytes
        print(f"\nMax batch size: {max_batch_gb} GB/batch -> {n_batches} batch file(s)")
    elif batch_size > 0:
        n_batches = (n_subjects + batch_size - 1) // batch_size
        print(f"\nBatch size: {batch_size} subjects/batch -> {n_batches} batch file(s)")
    else:
        print(f"\nBatch size: all -> 1 batch file ({n_subjects} subjects)")


def main():
    parser = argparse.ArgumentParser(description="Build multi-subject batch JSONL files")
    add_config_arg(parser)
    parser.add_argument("--subjects", nargs="*", help="Include only these subject IDs")
    parser.add_argument("--players", nargs="*", dest="subjects_alias",
                        help=argparse.SUPPRESS)
    parser.add_argument("--batch-size", type=int, default=0,
                        help="Max subjects per batch file (0 = all in one, default)")
    parser.add_argument("--max-batch-gb", type=float, default=0,
                        help="Max media size (GB) per batch file (overrides --batch-size)")
    parser.add_argument("--preview", action="store_true",
                        help="Show pending subjects without building")
    parser.add_argument("--force", action="store_true",
                        help="Include subjects even if already in batch_jobs.csv")
    parser.add_argument("--submit", action="store_true",
                        help="Submit each batch immediately after building")
    args = parser.parse_args()

    cfg = init_config(args.config_path)
    os.makedirs(cfg.JSONL_DIR, exist_ok=True)

    # Load data
    print(f"Loading {cfg.INPUT_PATH}...")
    df = pd.read_excel(cfg.INPUT_PATH)
    print(f"  {len(df)} rows, {df[cfg.GROUP_COL].nunique()} subjects")

    system_prompt = load_system_prompt()

    # Group by subject
    grouped = df.groupby(cfg.GROUP_COL)
    group_keys = sorted(grouped.groups.keys())

    subjects_filter = args.subjects or args.subjects_alias
    if subjects_filter:
        requested = set(subjects_filter)
        group_keys = [k for k in group_keys if cfg.subject_id(k) in requested]
        print(f"  Filtered to {len(group_keys)} requested subjects")

    # Find subjects with URI maps, excluding already-batched
    batched = set() if args.force else already_batched_subjects()
    by_key: dict[int, list[tuple[str, list[dict], dict[str, str]]]] = {}
    no_uri_map = 0
    already_done = 0

    for key in group_keys:
        subject = cfg.subject_id(key)
        if subject in batched:
            already_done += 1
            continue
        uri_data = load_uri_map(subject)
        if uri_data is None:
            no_uri_map += 1
            continue
        rows = grouped.get_group(key).to_dict(orient="records")
        key_id = int(uri_data.get("key_id", 1))
        by_key.setdefault(key_id, []).append((subject, rows, uri_data["uri_map"]))

    if no_uri_map:
        print(f"  {no_uri_map} subjects have no URI map (run 0uploadMedia.py first)")
    if already_done:
        print(f"  {already_done} subjects already batched (in batch_jobs.csv)")

    total_subjects = sum(len(v) for v in by_key.values())
    if total_subjects == 0:
        print("No pending subjects to batch.")
        return

    all_subject_groups = []
    for kid in sorted(by_key):
        all_subject_groups.extend(by_key[kid])

    if args.preview:
        preview_subjects(all_subject_groups, args.batch_size, args.max_batch_gb)
        return

    # Build JSONL files, one set of batches per key_id
    batch_num = next_batch_number()
    total_lines = 0
    total_batches = 0

    for key_id in sorted(by_key):
        subject_groups = by_key[key_id]
        if len(by_key) > 1:
            print(f"\n--- Key {key_id}: {len(subject_groups)} subjects ---")

        # Split into batches
        if args.max_batch_gb > 0:
            max_bytes = args.max_batch_gb * 1024**3
            batches = []
            current = []
            current_size = 0
            for subject, rows, uri_map in subject_groups:
                s_bytes = get_subject_media_size(rows)
                if current and current_size + s_bytes > max_bytes:
                    batches.append(current)
                    current = []
                    current_size = 0
                current.append((subject, rows, uri_map))
                current_size += s_bytes
            if current:
                batches.append(current)
        else:
            batch_size = args.batch_size if args.batch_size > 0 else len(subject_groups)
            batches = []
            for i in range(0, len(subject_groups), batch_size):
                batches.append(subject_groups[i : i + batch_size])

        for batch_group in batches:
            batch_name = f"{cfg.BATCH_PREFIX}{batch_num:03d}"
            jpath = os.path.join(cfg.JSONL_DIR, f"{batch_name}.jsonl")

            n_lines = build_batch_jsonl(batch_group, system_prompt, jpath)
            size_kb = os.path.getsize(jpath) / 1024
            subjects_in_batch = [s for s, _, _ in batch_group]
            subjects_str = ";".join(subjects_in_batch)

            media_mb = sum(get_subject_media_size(rows) for _, rows, _ in batch_group) / 1024**2
            print(f"  {batch_name}: {len(subjects_in_batch)} subjects, "
                  f"{n_lines} lines, {size_kb:.0f} KB JSONL, {media_mb:.0f} MB media"
                  f" [key={key_id}]")

            if args.submit:
                print(f"  Submitting {batch_name}...")
                client = get_client(key_id)
                try:
                    submit_batch(
                        client, cfg.MODEL, jpath,
                        display_name=batch_name,
                        job_log_path=cfg.JOB_LOG_PATH,
                        subjects=subjects_str,
                        key_id=key_id,
                    )
                except Exception as e:
                    print(f"  [ERROR] Failed to submit {batch_name}: {e}")

            total_lines += n_lines
            total_batches += 1
            batch_num += 1

    print(f"\n{'='*60}")
    action = "built + submitted" if args.submit else "built"
    print(f"COMPLETE: {total_batches} batch file(s) {action} ({total_lines} total lines)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
