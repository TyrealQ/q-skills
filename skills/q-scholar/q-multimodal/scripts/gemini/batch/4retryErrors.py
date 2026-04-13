"""Scan checkpoints for model_ok=False rows, build retry JSONL, submit, and merge back.

Reuses existing File API URIs from URI maps. Auto re-uploads expired files.
Retry results merge back into existing checkpoints (overwrites error rows).

Output: <RETRY_JSONL_DIR>/<RETRY_PREFIX>NNN.jsonl
"""

import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from utils import (
    init_config, get_config, add_config_arg,
    get_all_clients, load_uri_map, uri_map_path,
    load_system_prompt, read_job_log, log_batch_job, job_created_at,
    submit_batch, parse_batch_results, split_results_by_subject,
    list_to_excel_str, analyze_single_row,
    TERMINAL_STATES,
)


MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Error scanning
# ---------------------------------------------------------------------------

def scan_error_rows(include_exhausted: bool = False) -> dict[str, pd.DataFrame]:
    """Scan all checkpoints for model_ok=False rows.

    By default, skips rows that have reached MAX_RETRIES (exhausted).
    Set include_exhausted=True to return all error rows regardless.

    Returns {subject_id: DataFrame of error rows}.
    """
    cfg = get_config()
    errors: dict[str, pd.DataFrame] = {}
    pattern = f"{cfg.CHECKPOINT_PREFIX}*.xlsx"
    for f in sorted(Path(cfg.BATCH_CHECKPOINT_DIR).glob(pattern)):
        subject = f.stem.removeprefix(cfg.CHECKPOINT_PREFIX)
        try:
            df = pd.read_excel(f)
        except Exception as e:
            print(f"  [WARN] Failed to read {f}: {e}")
            continue
        if "model_ok" not in df.columns:
            continue
        err = df[~df["model_ok"].astype(bool)]
        if not include_exhausted and "retry_count" in err.columns:
            err = err[err["retry_count"].fillna(0).astype(int) < MAX_RETRIES]
        if len(err) > 0:
            errors[subject] = err
    return errors


# ---------------------------------------------------------------------------
# URI validation & re-upload
# ---------------------------------------------------------------------------

def check_file_exists(client, resource_name: str) -> bool:
    """Check if a file still exists in File API."""
    try:
        client.files.get(name=resource_name)
        return True
    except Exception:
        return False


def reupload_files_concurrent(
    client,
    local_paths: list[str],
    max_workers: int = 50,
) -> dict[str, tuple[str, str]]:
    """Re-upload files to File API concurrently.

    Returns {local_path: (uri, name)} for successful uploads.
    """
    from google.genai import types

    RETRYABLE_HTTP = ("429", "500", "502", "503", "504")
    RETRYABLE_NETWORK = ("10054", "10060", "Server disconnected", "forcibly closed")
    STORAGE_QUOTA_MARKER = "file_storage_bytes"
    storage_exhausted = [False]

    def _upload_one(fp: str) -> tuple[str, str | None, str | None]:
        if storage_exhausted[0] or not os.path.isfile(fp):
            return fp, None, None
        ext = Path(fp).suffix.lower()
        mime = "video/mp4" if ext == ".mp4" else "image/jpeg"
        for attempt in range(3):
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
                if attempt < 2 and (is_http or is_network):
                    wait = 2 ** (attempt + 1) if is_http else 1
                    time.sleep(wait)
                else:
                    return fp, None, None
        return fp, None, None

    results: dict[str, tuple[str, str]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_upload_one, fp): fp for fp in local_paths}
        for future in as_completed(futures, timeout=120 * max(len(local_paths), 1)):
            try:
                fp, uri, name = future.result(timeout=120)
            except (TimeoutError, Exception):
                continue
            if uri and name:
                results[fp] = (uri, name)

    if storage_exhausted[0]:
        print(f"  [STOP] Storage quota exhausted during re-upload")

    return results


def validate_and_reupload(
    subject: str,
    error_paths: list[str],
    clients: dict[int, object],
) -> dict[str, str]:
    """Validate URIs for error rows; re-upload expired ones concurrently.

    Returns {abs_path: file_uri} for all valid entries.
    """
    uri_data = load_uri_map(subject)
    if uri_data is None:
        print(f"  [WARN] No URI map for {subject}, cannot retry")
        return {}

    u_map = uri_data.get("uri_map", {})
    name_map = uri_data.get("name_map", {})
    key_id = int(uri_data.get("key_id", 1))

    if key_id not in clients:
        print(f"  [WARN] No client for key_id={key_id}")
        return {}

    client = clients[key_id]
    valid_uris: dict[str, str] = {}
    need_reupload: list[str] = []

    for abs_path in error_paths:
        uri = u_map.get(abs_path)
        name = name_map.get(abs_path)

        if uri and name:
            if check_file_exists(client, name):
                valid_uris[abs_path] = uri
            else:
                need_reupload.append(abs_path)
        else:
            need_reupload.append(abs_path)

    if need_reupload:
        print(f"  Re-uploading {len(need_reupload)} expired/missing files for {subject} [key={key_id}]...")
        uploaded = reupload_files_concurrent(client, need_reupload)
        for abs_path, (new_uri, new_name) in uploaded.items():
            uri_data["uri_map"][abs_path] = new_uri
            uri_data["name_map"][abs_path] = new_name
            valid_uris[abs_path] = new_uri

        with open(uri_map_path(subject), "w", encoding="utf-8") as f:
            json.dump(uri_data, f, ensure_ascii=False, indent=2)

    return valid_uris


# ---------------------------------------------------------------------------
# Retry JSONL building
# ---------------------------------------------------------------------------

def next_retry_number() -> int:
    """Scan existing retry JSONL files for next available number."""
    cfg = get_config()
    os.makedirs(cfg.RETRY_JSONL_DIR, exist_ok=True)
    existing = list(Path(cfg.RETRY_JSONL_DIR).glob(f"{cfg.RETRY_PREFIX}*.jsonl"))
    numbers = []
    for f in existing:
        m = re.match(re.escape(cfg.RETRY_PREFIX) + r"(\d+)\.jsonl$", f.name)
        if m:
            numbers.append(int(m.group(1)))
    return max(numbers, default=0) + 1


def build_retry_jsonl(
    entries: list[tuple[str, dict, str, str]],
    system_prompt: str,
    jsonl_path: str,
) -> int:
    """Build a retry JSONL file.

    entries: [(subject_id, row_dict, file_uri, mime_type), ...]
    Returns lines written.
    """
    cfg = get_config()
    count = 0
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for subject, row, file_uri, mime in entries:
            fp = row[cfg.FILE_COL]
            metadata_text = cfg.format_metadata(row)

            line = {
                "key": f"{subject}::{fp}".replace("\\", "/"),
                "request": {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": metadata_text},
                                {"file_data": {"file_uri": file_uri, "mime_type": mime}},
                            ],
                        }
                    ],
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "generation_config": {
                        "temperature": cfg.TEMPERATURE,
                        "response_mime_type": "application/json",
                        "thinking_config": {"thinking_level": cfg.THINKING_LEVEL},
                    },
                },
            }
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
            count += 1
    return count


# ---------------------------------------------------------------------------
# Result collection & checkpoint merge
# ---------------------------------------------------------------------------

def collect_retry_results(clients: dict[int, object]) -> None:
    """Poll retry jobs, download results, merge back into checkpoints."""
    cfg = get_config()
    log_rows = read_job_log(cfg.JOB_LOG_PATH)
    retry_jobs = [
        r for r in log_rows
        if r.get("display_name", "").startswith(cfg.RETRY_PREFIX)
        and r.get("state", "") not in TERMINAL_STATES
    ]

    if not retry_jobs:
        print("No retry jobs found in batch_jobs.csv")
        return

    merged_count = 0

    for row in retry_jobs:
        display_name = row["display_name"]
        key_id = int(row.get("key_id", "") or 1)
        client = clients.get(key_id, clients[min(clients)])
        subjects_str = row.get("subjects", "") or row.get("handles", "")
        batch_subjects = subjects_str.split(";") if subjects_str else []

        print(f"\n--- {display_name} ({len(batch_subjects)} subjects) [key={key_id}] ---")

        try:
            job = client.batches.get(name=row["job_name"])
            state = job.state.name if hasattr(job.state, "name") else str(job.state)

            if state not in TERMINAL_STATES:
                print(f"  Still running: {state}")
                log_batch_job(
                    cfg.JOB_LOG_PATH, row["job_name"], display_name,
                    row.get("model", cfg.MODEL), state,
                    jsonl_path=row.get("jsonl_path", ""), subjects=subjects_str,
                    key_id=str(key_id),
                )
                continue

            result_file = ""
            if state == "JOB_STATE_SUCCEEDED" and hasattr(job, "dest") and job.dest:
                result_file = getattr(job.dest, "file_name", "")
            log_batch_job(
                cfg.JOB_LOG_PATH, row["job_name"], display_name,
                row.get("model", cfg.MODEL), state,
                jsonl_path=row.get("jsonl_path", ""), subjects=subjects_str,
                result_file=result_file, created_at=job_created_at(job),
                key_id=str(key_id),
            )

            if state != "JOB_STATE_SUCCEEDED":
                print(f"  Job {state}")
                continue

            results = parse_batch_results(client, job)
            by_subject = split_results_by_subject(results)

            for subject, subject_results in by_subject.items():
                ckpt_path = os.path.join(cfg.BATCH_CHECKPOINT_DIR,
                                         f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
                if not os.path.isfile(ckpt_path):
                    print(f"  [WARN] No checkpoint for {subject}, skipping merge")
                    continue

                existing_df = pd.read_excel(ckpt_path)
                if "retry_count" not in existing_df.columns:
                    existing_df["retry_count"] = 0
                updated = 0
                still_bad = 0

                for _, row_data in existing_df.iterrows():
                    fp = str(row_data.get(cfg.FILE_COL, "")).replace("\\", "/")
                    if fp not in subject_results:
                        continue
                    res = subject_results[fp]
                    idx = row_data.name

                    rc = existing_df.at[idx, "retry_count"]
                    existing_df.at[idx, "retry_count"] = int(rc if pd.notna(rc) else 0) + 1

                    if res["ok"]:
                        data = res["data"]
                        for field in cfg.ANALYSIS_FIELDS:
                            val = data.get(field, "")
                            existing_df.at[idx, field] = list_to_excel_str(val) if isinstance(val, list) else val
                        existing_df.at[idx, "raw_json"] = res["raw_json"]
                        existing_df.at[idx, "model_ok"] = True
                        updated += 1
                    else:
                        still_bad += 1

                if updated > 0 or still_bad > 0:
                    existing_df.to_excel(ckpt_path, index=False)
                    merged_count += updated
                    if updated > 0:
                        print(f"  {subject}: {updated} rows fixed, {still_bad} still failed")
                    else:
                        print(f"  {subject}: no improvements ({still_bad} still failed)")

        except Exception as e:
            print(f"  [ERROR] {display_name}: {e}")

    print(f"\n{'='*60}")
    print(f"Merged {merged_count} corrected rows back into checkpoints")
    print("=" * 60)

    export_failed_rows()


# ---------------------------------------------------------------------------
# Export permanently failed rows
# ---------------------------------------------------------------------------

def export_failed_rows() -> None:
    """Export rows still model_ok=False after MAX_RETRIES to a single Excel file."""
    cfg = get_config()
    exhausted: list[pd.DataFrame] = []
    pattern = f"{cfg.CHECKPOINT_PREFIX}*.xlsx"
    for f in sorted(Path(cfg.BATCH_CHECKPOINT_DIR).glob(pattern)):
        try:
            df = pd.read_excel(f)
        except Exception:
            continue
        if "model_ok" not in df.columns or "retry_count" not in df.columns:
            continue
        failed = df[
            (~df["model_ok"].astype(bool))
            & (df["retry_count"].fillna(0).astype(int) >= MAX_RETRIES)
        ]
        if len(failed) > 0:
            exhausted.append(failed)

    if not exhausted:
        print("\nNo rows have exhausted all retries yet.")
        return

    failed_df = pd.concat(exhausted, ignore_index=True)
    out_path = os.path.join(cfg.BASE_DIR, cfg.OUTPUT_DIR, "batch",
                            "failed_rows_for_standard.xlsx")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    failed_df.to_excel(out_path, index=False)

    subjects = (failed_df[cfg.GROUP_COL].nunique()
                if cfg.GROUP_COL in failed_df.columns else "?")
    print(f"\nExported {len(failed_df)} permanently failed rows ({subjects} subjects) to:")
    print(f"  {out_path}")


# ---------------------------------------------------------------------------
# Standard (live API) retry
# ---------------------------------------------------------------------------

def run_standard_retry(max_workers: int = 25, subjects: list[str] | None = None) -> None:
    """Process failed rows via the standard pipeline (inline media bytes, no File API).

    Reads failed_rows_for_standard.xlsx, uses analyze_single_row from utils,
    runs concurrently, and merges results back into batch checkpoints.
    """
    cfg = get_config()
    from google import genai as _genai

    _api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY1")
    if not _api_key:
        raise RuntimeError("GOOGLE_API_KEY or GOOGLE_API_KEY1 not set.")
    client = _genai.Client(api_key=_api_key)
    system_prompt = load_system_prompt()

    failed_path = os.path.join(cfg.BASE_DIR, cfg.OUTPUT_DIR, "batch",
                               "failed_rows_for_standard.xlsx")
    if not os.path.isfile(failed_path):
        print(f"No file found at {failed_path}")
        return

    failed_df = pd.read_excel(failed_path)
    if failed_df.empty:
        print("No failed rows to process.")
        return

    if subjects:
        requested = set(subjects)
        failed_df = failed_df[
            failed_df[cfg.GROUP_COL].apply(
                lambda x: cfg.subject_id(str(x)) in requested)
        ]

    rows = failed_df.to_dict(orient="records")
    print(f"Processing {len(rows)} failed rows via standard pipeline ({max_workers} workers)...")

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(analyze_single_row, client, i, rows[i], system_prompt): i
            for i in range(len(rows))
        }
        done = 0
        for fut in as_completed(futures):
            idx = futures[fut]
            try:
                results[idx] = fut.result()
            except Exception as e:
                results[idx] = {"ok": False, "data": {}, "raw_json": f"[error] {e}"}
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{len(rows)} done")

    ok_count = sum(1 for r in results.values() if r["ok"])
    print(f"\nResults: {ok_count}/{len(rows)} OK")

    by_subject: dict[str, list[tuple[str, dict]]] = {}
    for i, row in enumerate(rows):
        res = results[i]
        if not res["ok"]:
            continue
        subject = cfg.subject_id(str(row.get(cfg.GROUP_COL, "")))
        fp = str(row.get(cfg.FILE_COL, "")).replace("\\", "/")
        by_subject.setdefault(subject, []).append((fp, res))

    merged = 0
    for subject, fixes in by_subject.items():
        ckpt_path = os.path.join(cfg.BATCH_CHECKPOINT_DIR,
                                 f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
        if not os.path.isfile(ckpt_path):
            continue

        ckpt_df = pd.read_excel(ckpt_path)
        norm_paths = ckpt_df[cfg.FILE_COL].astype(str).str.replace("\\", "/", regex=False)

        for fp, res in fixes:
            mask = norm_paths == fp
            if mask.sum() == 0:
                continue
            idx = ckpt_df[mask].index[0]
            data = res["data"]
            for field in cfg.ANALYSIS_FIELDS:
                val = data.get(field, "")
                ckpt_df.at[idx, field] = list_to_excel_str(val) if isinstance(val, list) else val
            ckpt_df.at[idx, "raw_json"] = res["raw_json"]
            ckpt_df.at[idx, "model_ok"] = True
            merged += 1

        ckpt_df.to_excel(ckpt_path, index=False)

    still_bad = len(rows) - ok_count
    print(f"Merged {merged} fixes, {still_bad} still failed")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Retry model_ok=False rows from checkpoints")
    add_config_arg(parser)
    parser.add_argument("--preview", action="store_true",
                        help="Show error counts per subject")
    parser.add_argument("--build", action="store_true",
                        help="Scan + build retry JSONL only")
    parser.add_argument("--submit", action="store_true",
                        help="Scan + build + submit retry batch")
    parser.add_argument("--collect", action="store_true",
                        help="Poll retry jobs + merge back into checkpoints")
    parser.add_argument("--standard", action="store_true",
                        help="Process failed rows via standard pipeline (live API, no File API)")
    parser.add_argument("--export-failed", action="store_true",
                        help="Export rows that failed after max retries")
    parser.add_argument("--subjects", nargs="*",
                        help="Filter to specific subject IDs")
    parser.add_argument("--players", nargs="*", dest="subjects_alias",
                        help=argparse.SUPPRESS)
    parser.add_argument("--max-workers", type=int, default=25,
                        help="Concurrency for --standard mode (default: 25)")
    parser.add_argument("--max-batch-gb", type=float, default=2.0,
                        help="Max media size per retry batch (default: 2.0 GB)")
    args = parser.parse_args()

    cfg = init_config(args.config_path)
    os.makedirs(cfg.RETRY_JSONL_DIR, exist_ok=True)

    subjects_filter = args.subjects or args.subjects_alias

    if args.export_failed:
        export_failed_rows()
        return

    if args.standard:
        run_standard_retry(max_workers=args.max_workers, subjects=subjects_filter)
        return

    if args.collect:
        clients = get_all_clients()
        collect_retry_results(clients)
        return

    # Scan for retryable errors
    errors = scan_error_rows()
    if subjects_filter:
        requested = set(subjects_filter)
        errors = {s: df for s, df in errors.items() if s in requested}

    all_errors = scan_error_rows(include_exhausted=True)
    exhausted_count = 0
    for subject, all_err in all_errors.items():
        retryable = errors.get(subject)
        if retryable is not None:
            exhausted_count += len(all_err) - len(retryable)
        else:
            exhausted_count += len(all_err)

    if not errors and exhausted_count == 0:
        print("No model_ok=False rows found in any checkpoint.")
        return

    total_errors = sum(len(df) for df in errors.values())
    print(f"\nFound {total_errors} retryable error rows across {len(errors)} subjects"
          f" ({exhausted_count} exhausted after {MAX_RETRIES} retries):\n")
    print(f"{'Subject':<30} {'Retryable':>10} {'Exhausted':>10} {'Total':>8} {'Error %':>8}")
    print("-" * 68)
    all_subjects = sorted(set(list(errors.keys()) + list(all_errors.keys())))
    for subject in all_subjects:
        retryable = len(errors.get(subject, []))
        all_err = len(all_errors.get(subject, []))
        exh = all_err - retryable
        ckpt_path = os.path.join(cfg.BATCH_CHECKPOINT_DIR,
                                 f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
        total = len(pd.read_excel(ckpt_path)) if os.path.isfile(ckpt_path) else all_err
        pct = f"{all_err / total * 100:.0f}%" if total else "?"
        print(f"{subject:<30} {retryable:>10} {exh:>10} {total:>8} {pct:>8}")
    print("-" * 68)
    print(f"{'TOTAL':<30} {total_errors:>10} {exhausted_count:>10}")

    if not errors:
        print(f"\nAll error rows have exhausted {MAX_RETRIES} retries.")
        print("Run --export-failed to export them for the standard pipeline.")
        return

    if args.preview:
        return

    # Build retry JSONL
    clients = get_all_clients()
    system_prompt = load_system_prompt()

    print(f"\nLoading source data from {cfg.INPUT_PATH}...")
    source_df = pd.read_excel(cfg.INPUT_PATH)
    grouped = source_df.groupby(cfg.GROUP_COL)
    subject_to_key = {}
    for key in grouped.groups.keys():
        subject_to_key[cfg.subject_id(key)] = key

    by_key: dict[int, list[tuple[str, dict, str, str]]] = {}

    for subject in sorted(errors):
        err_df = errors[subject]
        error_abs_paths = [
            os.path.join(cfg.BASE_DIR, str(fp))
            for fp in err_df[cfg.FILE_COL].values
        ]

        valid_uris = validate_and_reupload(subject, error_abs_paths, clients)

        if not valid_uris:
            print(f"  [SKIP] No valid URIs for {subject}")
            continue

        group_key = subject_to_key.get(subject)
        if not group_key:
            print(f"  [SKIP] Subject {subject} not found in source data")
            continue

        subject_rows = grouped.get_group(group_key).to_dict(orient="records")
        row_by_path = {}
        for r in subject_rows:
            abs_p = os.path.join(cfg.BASE_DIR, r[cfg.FILE_COL])
            row_by_path[abs_p] = r

        key_id = int((load_uri_map(subject) or {}).get("key_id", 1))

        for abs_path, file_uri in valid_uris.items():
            row = row_by_path.get(abs_path)
            if row is None:
                continue
            ext = Path(abs_path).suffix.lower()
            mime = "video/mp4" if ext == ".mp4" else "image/jpeg"
            by_key.setdefault(key_id, []).append((subject, row, file_uri, mime))

    total_entries = sum(len(v) for v in by_key.values())
    if total_entries == 0:
        print("No valid entries to retry.")
        return

    print(f"\n{total_entries} entries ready for retry across {len(by_key)} key(s)")

    retry_num = next_retry_number()
    max_bytes = args.max_batch_gb * 1024**3
    all_jsonl_files: list[tuple[str, str, str, int]] = []

    for key_id in sorted(by_key):
        entries = by_key[key_id]

        batches = []
        current = []
        current_size = 0
        for entry in entries:
            _subject, row, _file_uri, _mime = entry
            fp = os.path.join(cfg.BASE_DIR, row[cfg.FILE_COL])
            fsize = os.path.getsize(fp) if os.path.isfile(fp) else 0
            if current and current_size + fsize > max_bytes:
                batches.append(current)
                current = []
                current_size = 0
            current.append(entry)
            current_size += fsize
        if current:
            batches.append(current)

        for batch in batches:
            batch_name = f"{cfg.RETRY_PREFIX}{retry_num:03d}"
            jpath = os.path.join(cfg.RETRY_JSONL_DIR, f"{batch_name}.jsonl")

            n_lines = build_retry_jsonl(batch, system_prompt, jpath)
            subjects_in_batch = sorted(set(s for s, _, _, _ in batch))
            subjects_str = ";".join(subjects_in_batch)

            print(f"  {batch_name}: {len(subjects_in_batch)} subjects, {n_lines} lines [key={key_id}]")
            all_jsonl_files.append((jpath, batch_name, subjects_str, key_id))
            retry_num += 1

    if not args.build and not args.submit:
        print("\nUse --build to just build JSONL, or --submit to build and submit.")
        return

    if not args.submit:
        print(f"\nBuilt {len(all_jsonl_files)} retry JSONL file(s). Use --submit to submit them.")
        return

    submitted = 0
    for jpath, batch_name, subjects_str, key_id in all_jsonl_files:
        print(f"\nSubmitting {batch_name} [key={key_id}]...")
        try:
            client = clients[key_id]
            submit_batch(
                client, cfg.MODEL, jpath,
                display_name=batch_name,
                job_log_path=cfg.JOB_LOG_PATH,
                subjects=subjects_str,
                key_id=key_id,
            )
            submitted += 1
        except Exception as e:
            print(f"  [ERROR] Failed to submit {batch_name}: {e}")

    print(f"\n{'='*60}")
    print(f"Submitted {submitted}/{len(all_jsonl_files)} retry batch(es)")
    print("Run --collect after jobs complete to merge results back")
    print("=" * 60)


if __name__ == "__main__":
    main()
