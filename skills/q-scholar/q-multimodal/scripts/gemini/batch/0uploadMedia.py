"""Upload media files to Gemini File API with concurrent workers.

Uploads JPG/MP4 files per subject, saving URI maps for later JSONL building.
Manages 20 GB File API storage by processing small subjects first.
Supports multi-key rotation (--key N) and progressive submission (--submit).

Output: <OUTPUT_DIR>/batch/uri_maps/<subject_id>.json
"""

import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

import pandas as pd

from utils import (
    init_config, get_config, add_config_arg,
    get_client, uri_map_path, load_uri_map, load_system_prompt,
    submit_batch, build_batch_jsonl,
    read_job_log, TERMINAL_FAILED,
)

STORAGE_LIMIT_BYTES = 18.0 * 1024**3  # 18 GB media limit (leaves ~2 GB for JSONL uploads)


def checkpoint_exists(subject: str) -> bool:
    """Check if a subject already has a completed checkpoint."""
    cfg = get_config()
    return os.path.isfile(
        os.path.join(cfg.BATCH_CHECKPOINT_DIR, f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
    )


def get_subject_media_size(file_paths: list[str]) -> int:
    """Sum of file sizes in bytes."""
    return sum(os.path.getsize(fp) for fp in file_paths if os.path.isfile(fp))


def upload_media_files_concurrent(
    client,
    file_paths: list[str],
    max_workers: int = 25,
    per_file_timeout: int = 120,
) -> tuple[dict[str, str], dict[str, str], bool]:
    """Upload media files to Gemini File API with concurrent workers.

    Returns (uri_map, name_map, storage_exhausted):
      - uri_map: {local_path: file_uri}
      - name_map: {local_path: resource_name}
      - storage_exhausted: True if File API storage quota was hit
    """
    from google.genai import types

    uri_map: dict[str, str] = {}
    name_map: dict[str, str] = {}
    lock = Lock()
    done_count = [0]
    storage_exhausted = [False]
    total = len(file_paths)

    RETRYABLE_HTTP = ("429", "500", "502", "503", "504")
    RETRYABLE_NETWORK = ("10054", "10060", "Server disconnected", "forcibly closed")
    STORAGE_QUOTA_MARKER = "file_storage_bytes"

    def upload_one(fp: str) -> tuple[str, str | None, str | None]:
        if storage_exhausted[0]:
            return fp, None, None
        ext = Path(fp).suffix.lower()
        mime = "video/mp4" if ext == ".mp4" else "image/jpeg"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                uploaded = client.files.upload(
                    file=fp,
                    config=types.UploadFileConfig(mime_type=mime),
                )
                return fp, uploaded.uri, uploaded.name
            except Exception as e:
                err_str = str(e)
                if STORAGE_QUOTA_MARKER in err_str:
                    storage_exhausted[0] = True
                    return fp, None, None
                is_http = any(code in err_str for code in RETRYABLE_HTTP)
                is_network = any(code in err_str for code in RETRYABLE_NETWORK)
                if attempt < max_retries - 1 and (is_http or is_network):
                    wait = 2 ** (attempt + 1) if is_http else 1
                    time.sleep(wait)
                else:
                    print(f"  [WARN] Upload failed for {Path(fp).name}: {e}")
                    return fp, None, None
        return fp, None, None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(upload_one, fp): fp for fp in file_paths}
        for future in as_completed(futures):
            try:
                fp, uri, name = future.result()
            except Exception as e:
                print(f"  [WARN] Worker exception: {e}")
                continue
            if uri and name:
                with lock:
                    uri_map[fp] = uri
                    name_map[fp] = name
                    done_count[0] += 1
                    if done_count[0] % 100 == 0:
                        print(f"  Uploaded {done_count[0]}/{total}")

    if storage_exhausted[0]:
        print(f"  [STOP] File API storage quota exhausted, saved {len(uri_map)}/{total} files")

    return uri_map, name_map, storage_exhausted[0]


def preview_subjects(subject_groups: list[tuple[str, list[dict]]]) -> None:
    """Report per-subject file counts and sizes without uploading."""
    cfg = get_config()
    total_size = 0
    total_files = 0
    print(f"\n{'Subject':<30} {'Files':>8} {'Size (MB)':>12}")
    print("-" * 52)
    for subject, rows in subject_groups:
        paths = [os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]) for r in rows]
        paths = [p for p in paths if os.path.isfile(p)]
        size = get_subject_media_size(paths)
        total_size += size
        total_files += len(paths)
        print(f"{subject:<30} {len(paths):>8} {size / 1024**2:>12.1f}")
    print("-" * 52)
    print(f"{'TOTAL':<30} {total_files:>8} {total_size / 1024**2:>12.1f}")
    print(f"\nEstimated storage: {total_size / 1024**3:.2f} GB")


def _build_and_submit_batch(
    subjects_with_rows: list[tuple[str, list[dict]]],
    key_id: int,
    batch_num: int,
) -> int:
    """Build JSONL for a group of subjects and submit as a batch job.

    Returns the next batch number.
    """
    cfg = get_config()
    system_prompt = load_system_prompt()
    subject_groups = []
    for subject, rows in subjects_with_rows:
        uri_data = load_uri_map(subject)
        if uri_data is None:
            continue
        subject_groups.append((subject, rows, uri_data["uri_map"]))

    if not subject_groups:
        return batch_num

    batch_name = f"{cfg.BATCH_PREFIX}{batch_num:03d}"
    jpath = os.path.join(cfg.JSONL_DIR, f"{batch_name}.jsonl")
    os.makedirs(cfg.JSONL_DIR, exist_ok=True)

    n_lines = build_batch_jsonl(subject_groups, system_prompt, jpath)
    subjects_str = ";".join(s for s, _, _ in subject_groups)
    print(f"  Built {batch_name}: {len(subject_groups)} subjects, {n_lines} lines")

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
        print(f"  JSONL saved at {jpath}, submit later with 2submitJobs.py")
    return batch_num + 1


def main():
    parser = argparse.ArgumentParser(description="Upload media to Gemini File API")
    add_config_arg(parser)
    parser.add_argument("--subjects", nargs="*", help="Process only these subject IDs")
    parser.add_argument("--players", nargs="*", dest="subjects_alias",
                        help=argparse.SUPPRESS)
    parser.add_argument("--subjects-file", help="Read subject IDs from a text file (one per line)")
    parser.add_argument("--players-file", dest="subjects_file_alias",
                        help=argparse.SUPPRESS)
    parser.add_argument("--max-workers", type=int, default=25, help="Upload concurrency (default: 25)")
    parser.add_argument("--preview", action="store_true", help="Report sizes without uploading")
    parser.add_argument("--key", type=int, default=1, help="API key ID to use (default: 1)")
    parser.add_argument("--submit", action="store_true",
                        help="Progressively build+submit ~2GB batches during upload")
    parser.add_argument("--max-batch-gb", type=float, default=2.0,
                        help="Max media size per progressive batch (default: 2.0 GB)")
    args = parser.parse_args()

    cfg = init_config(args.config_path)
    os.makedirs(cfg.URI_MAP_DIR, exist_ok=True)

    # Load data
    print(f"Loading {cfg.INPUT_PATH}...")
    df = pd.read_excel(cfg.INPUT_PATH)
    print(f"  {len(df)} rows, {df[cfg.GROUP_COL].nunique()} subjects")

    # Group by subject
    grouped = df.groupby(cfg.GROUP_COL)
    group_keys = sorted(grouped.groups.keys())

    # Merge --subjects and aliases
    requested = set(args.subjects or args.subjects_alias or [])
    subjects_file = args.subjects_file or args.subjects_file_alias
    if subjects_file:
        with open(subjects_file, "r", encoding="utf-8") as pf:
            for line in pf:
                line = line.strip()
                if line:
                    requested.add(line)
    if requested:
        group_keys = [k for k in group_keys if cfg.subject_id(k) in requested]
        print(f"  Filtered to {len(group_keys)} requested subjects")

    # Build (subject, rows) list sorted by media size ascending
    subject_groups = []
    for key in group_keys:
        subject = cfg.subject_id(key)
        rows = grouped.get_group(key).to_dict(orient="records")
        subject_groups.append((subject, rows))

    def subject_size(item):
        _, rows = item
        return sum(
            os.path.getsize(os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]))
            for r in rows
            if os.path.isfile(os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]))
        )

    subject_groups.sort(key=subject_size)

    # Skip subjects with existing checkpoints
    before = len(subject_groups)
    subject_groups = [(s, rows) for s, rows in subject_groups if not checkpoint_exists(s)]
    checkpointed = before - len(subject_groups)
    if checkpointed:
        print(f"  {checkpointed} subjects already have checkpoints, skipped")

    # Preview mode
    if args.preview:
        pending = [(s, rows) for s, rows in subject_groups
                   if not os.path.isfile(uri_map_path(s))]
        already = len(subject_groups) - len(pending)
        if already:
            print(f"\n  {already} subjects already uploaded, showing {len(pending)} pending:")
        preview_subjects(pending)
        return

    # Upload mode
    client = get_client(args.key)
    cumulative_bytes = 0
    uploaded_count = 0
    skipped_count = 0

    # Load already-batched subjects to avoid duplicate submissions on restart
    already_batched: set[str] = set()
    if args.submit:
        for row in read_job_log(cfg.JOB_LOG_PATH):
            dn = row.get("display_name", "")
            state = row.get("state", "")
            if not dn.startswith(cfg.BATCH_PREFIX) or state in TERMINAL_FAILED:
                continue
            for s in (row.get("subjects", "") or row.get("handles", "") or "").split(";"):
                if s:
                    already_batched.add(s)
        if already_batched:
            print(f"  {len(already_batched)} subjects already batched, will skip in progressive submit")

    # Progressive submission state
    batch_accumulator: list[tuple[str, list[dict]]] = []
    batch_accum_bytes = 0
    max_batch_bytes = args.max_batch_gb * 1024**3
    next_batch_num_val = None

    def _next_batch_num():
        nonlocal next_batch_num_val
        if next_batch_num_val is None:
            existing = list(Path(cfg.JSONL_DIR).glob(f"{cfg.BATCH_PREFIX}*.jsonl"))
            numbers = []
            for f in existing:
                m = re.match(re.escape(cfg.BATCH_PREFIX) + r"(\d+)\.jsonl$", f.name)
                if m:
                    numbers.append(int(m.group(1)))
            next_batch_num_val = max(numbers, default=0) + 1
        return next_batch_num_val

    for subject, rows in subject_groups:
        # Skip if URI map already exists
        if os.path.isfile(uri_map_path(subject)):
            skipped_count += 1
            if args.submit and subject not in already_batched:
                p_bytes = sum(
                    os.path.getsize(os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]))
                    for r in rows
                    if os.path.isfile(os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL]))
                )
                batch_accumulator.append((subject, rows))
                batch_accum_bytes += p_bytes
                if batch_accum_bytes >= max_batch_bytes:
                    print(f"\n  Progressive submit: {len(batch_accumulator)} subjects, "
                          f"{batch_accum_bytes / 1024**3:.2f} GB")
                    next_batch_num_val = _build_and_submit_batch(
                        batch_accumulator, args.key, _next_batch_num()
                    )
                    batch_accumulator = []
                    batch_accum_bytes = 0
            continue

        # Collect absolute paths
        abs_paths = []
        for row in rows:
            fp = os.path.join(cfg.BASE_DIR, row[cfg.FILE_COL])
            if os.path.isfile(fp):
                abs_paths.append(fp)

        if not abs_paths:
            print(f"  [SKIP] No media files for {subject}")
            continue

        subject_bytes = get_subject_media_size(abs_paths)

        if cumulative_bytes + subject_bytes > STORAGE_LIMIT_BYTES:
            print(f"\n  [WARN] Approaching 20 GB storage limit "
                  f"({(cumulative_bytes + subject_bytes) / 1024**3:.2f} GB)")
            print("  Stopping uploads. Submit existing jobs to free storage, then re-run.")
            break

        print(f"\n{'='*60}")
        print(f"Subject: {subject} ({len(abs_paths)} files, {subject_bytes / 1024**2:.1f} MB)")
        print(f"  Cumulative so far: {cumulative_bytes / 1024**3:.2f} GB")
        print(f"{'='*60}")

        uri_map, name_map, quota_hit = upload_media_files_concurrent(
            client, abs_paths, max_workers=args.max_workers
        )
        print(f"  Uploaded {len(uri_map)}/{len(abs_paths)} files")

        if not uri_map:
            if quota_hit:
                print("  Stopping uploads, storage quota exhausted.")
                break
            print(f"  [SKIP] All uploads failed for {subject}")
            continue

        actual_bytes = sum(
            os.path.getsize(p) for p in abs_paths if p in uri_map
        )
        cumulative_bytes += actual_bytes

        out = {
            "uri_map": uri_map,
            "name_map": name_map,
            "key_id": args.key,
            "uploaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(uri_map_path(subject), "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {uri_map_path(subject)}")
        uploaded_count += 1

        if quota_hit:
            print("  Stopping uploads, storage quota exhausted.")
            break

        if args.submit:
            batch_accumulator.append((subject, rows))
            batch_accum_bytes += actual_bytes
            if batch_accum_bytes >= max_batch_bytes:
                print(f"\n  Progressive submit: {len(batch_accumulator)} subjects, "
                      f"{batch_accum_bytes / 1024**3:.2f} GB")
                next_batch_num_val = _build_and_submit_batch(
                    batch_accumulator, args.key, _next_batch_num()
                )
                batch_accumulator = []
                batch_accum_bytes = 0

    # Submit any remaining accumulated subjects
    if args.submit and batch_accumulator:
        print(f"\n  Progressive submit (final): {len(batch_accumulator)} subjects, "
              f"{batch_accum_bytes / 1024**3:.2f} GB")
        next_batch_num_val = _build_and_submit_batch(batch_accumulator, args.key, _next_batch_num())

    print(f"\n{'='*60}")
    print(f"COMPLETE: {uploaded_count} uploaded, {skipped_count} skipped (already done)")
    print(f"  Storage used this session: {cumulative_bytes / 1024**3:.2f} GB")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
