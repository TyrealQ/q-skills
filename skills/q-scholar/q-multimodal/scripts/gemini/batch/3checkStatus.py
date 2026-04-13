"""Poll multi-subject batch jobs, download results, save per-subject checkpoints.

Reads batch_jobs.csv, checks job statuses, downloads results for
succeeded jobs, splits by subject ID, saves per-subject Excel checkpoints.
Supports multi-key polling (reads key_id per job) and selective cleanup.
"""

import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from utils import (
    init_config, get_config, add_config_arg,
    get_all_clients,
    read_job_log, log_batch_job, job_created_at,
    list_to_excel_str, parse_batch_results, split_results_by_subject,
    load_uri_map, uri_map_path,
    TERMINAL_STATES,
)


# ---------------------------------------------------------------------------
# Batch job lifecycle
# ---------------------------------------------------------------------------

def poll_existing_batch(
    client,
    job_name: str,
    poll_interval: int = 30,
    max_poll_seconds: int = 6 * 3600,
    job_log_path: str = "",
    display_name: str = "",
    model: str = "",
    jsonl_path: str = "",
    subjects: str = "",
    key_id: str = "",
) -> object:
    """Check status of an existing batch job, poll if still running."""
    job = client.batches.get(name=job_name)
    state = job.state.name if hasattr(job.state, "name") else str(job.state)

    if state in TERMINAL_STATES:
        print(f"  Job {job_name} already finished: {state}")
    else:
        print(f"  Job {job_name} still running ({state}), polling...")
        deadline = time.time() + max_poll_seconds
        while state not in TERMINAL_STATES:
            if time.time() > deadline:
                raise RuntimeError(f"Job {job_name} timed out after {max_poll_seconds}s")
            time.sleep(poll_interval)
            job = client.batches.get(name=job_name)
            state = job.state.name if hasattr(job.state, "name") else str(job.state)
            print(f"  Polling... state={state}")
        print(f"  Job finished: {state}")

    if job_log_path:
        result_file = ""
        if state == "JOB_STATE_SUCCEEDED" and hasattr(job, "dest") and job.dest:
            result_file = getattr(job.dest, "file_name", "")
        log_batch_job(job_log_path, job_name, display_name, model, state,
                      jsonl_path=jsonl_path, subjects=subjects,
                      result_file=result_file, created_at=job_created_at(job),
                      key_id=key_id)

    return job


# ---------------------------------------------------------------------------
# DataFrame helpers
# ---------------------------------------------------------------------------

def results_to_dataframe(
    rows: list[dict],
    results: dict[str, dict],
    key_column: str,
    json_col_name: str = "raw_json",
) -> pd.DataFrame:
    """Merge batch results back into the source rows."""
    cfg = get_config()
    all_keys: set[str] = set()
    for r in results.values():
        if r.get("ok") and isinstance(r.get("data"), dict):
            all_keys.update(r["data"].keys())
    all_keys_sorted = [f for f in cfg.ANALYSIS_FIELDS if f in all_keys]
    all_keys_sorted += sorted(all_keys - set(cfg.ANALYSIS_FIELDS))

    records = []
    for row in rows:
        rec = dict(row)
        key = str(row[key_column]).replace("\\", "/")
        res = results.get(key, {})
        data = res.get("data", {})
        for k in all_keys_sorted:
            rec[k] = list_to_excel_str(data.get(k, ""))
        rec[json_col_name] = res.get("raw_json", "")
        rec["model_ok"] = bool(res.get("ok", False))
        records.append(rec)

    return pd.DataFrame(records)


def save_checkpoint(df: pd.DataFrame, path: str) -> None:
    """Save a DataFrame to Excel."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    df.to_excel(path, index=False)
    print(f"  Saved: {path} ({len(df)} rows)")


# ---------------------------------------------------------------------------
# File API cleanup
# ---------------------------------------------------------------------------

def delete_uploaded_files(client, file_names: list[str], max_workers: int = 100) -> int:
    """Best-effort concurrent cleanup of uploaded files. Returns number of successful deletes."""
    if not file_names:
        return 0

    def _delete_one(name: str) -> bool:
        try:
            client.files.delete(name=name)
            return True
        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "may not exist" in err_str:
                return True
            if "10054" in err_str or "10038" in err_str:
                return True
            print(f"  [WARN] Failed to delete {name}: {e}")
            return False

    success = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_delete_one, n): n for n in file_names}
        for future in as_completed(futures):
            if future.result():
                success += 1
    return success


def cleanup_ok_files(subject: str, clients: dict) -> None:
    """Delete only model_ok=True files from File API for a subject.

    Reads the checkpoint to identify OK file_paths, looks up their
    resource_name in the URI map's name_map, deletes those files,
    and updates the URI map (removes deleted entries, keeps error ones).
    """
    cfg = get_config()
    ckpt_path = os.path.join(cfg.BATCH_CHECKPOINT_DIR,
                             f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
    if not os.path.isfile(ckpt_path):
        return

    uri_data = load_uri_map(subject)
    if uri_data is None:
        return

    name_map = uri_data.get("name_map", {})
    if not name_map:
        return

    key_id = int(uri_data.get("key_id", 1))
    if key_id not in clients:
        print(f"  [WARN] No client for key_id={key_id}, skipping cleanup for {subject}")
        return

    client = clients[key_id]

    df = pd.read_excel(ckpt_path)
    if "model_ok" not in df.columns:
        return

    ok_paths = set()
    for _, row in df[df["model_ok"].astype(bool)].iterrows():
        fp = str(row.get(cfg.FILE_COL, ""))
        abs_path = os.path.join(cfg.BASE_DIR, fp)
        ok_paths.add(abs_path)

    to_delete = []
    to_remove_keys = []
    for local_path, resource_name in name_map.items():
        if local_path in ok_paths:
            to_delete.append(resource_name)
            to_remove_keys.append(local_path)

    if not to_delete:
        return

    print(f"  Cleaning up {len(to_delete)}/{len(name_map)} OK files for {subject} [key={key_id}]...")
    deleted = delete_uploaded_files(client, to_delete)

    if deleted < len(to_delete):
        print(f"  [WARN] {len(to_delete) - deleted} remote deletes failed")

    for key in to_remove_keys:
        uri_data["uri_map"].pop(key, None)
        uri_data["name_map"].pop(key, None)

    u_path = uri_map_path(subject)
    if not uri_data["uri_map"] and not uri_data["name_map"]:
        os.remove(u_path)
        print(f"  Removed {u_path} (all files cleaned)")
    else:
        with open(u_path, "w", encoding="utf-8") as f:
            json.dump(uri_data, f, ensure_ascii=False, indent=2)
        remaining = len(uri_data["name_map"])
        print(f"  Updated URI map: {remaining} entries remaining (error files kept)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Check multi-subject batch jobs and download results")
    add_config_arg(parser)
    parser.add_argument("--poll", action="store_true",
                        help="Block until all jobs finish")
    parser.add_argument("--subjects", nargs="*",
                        help="Extract checkpoints for only these subject IDs")
    parser.add_argument("--players", nargs="*", dest="subjects_alias",
                        help=argparse.SUPPRESS)
    parser.add_argument("--cleanup", action="store_true",
                        help="Delete model_ok=True files after checkpoint saved")
    parser.add_argument("--cleanup-ok", action="store_true",
                        help="Delete only model_ok=True files (keeps error files for retry)")
    parser.add_argument("--min-coverage", type=float, default=0.0,
                        help="Minimum coverage to save checkpoint (default: 0.0 = always save)")
    args = parser.parse_args()

    cfg = init_config(args.config_path)
    os.makedirs(cfg.BATCH_CHECKPOINT_DIR, exist_ok=True)

    # Read job log
    log_rows = read_job_log(cfg.JOB_LOG_PATH)
    if not log_rows:
        print("No jobs found in batch_jobs.csv")
        return

    # Filter to jobs matching our batch/retry prefixes
    filtered = [r for r in log_rows
                if r.get("display_name", "").startswith(cfg.BATCH_PREFIX)
                or r.get("display_name", "").startswith(cfg.RETRY_PREFIX)]

    if not filtered:
        print("No matching jobs found in log.")
        return

    # Load source data for result reconstruction
    print(f"Loading source data from {cfg.INPUT_PATH}...")
    df = pd.read_excel(cfg.INPUT_PATH)
    grouped = df.groupby(cfg.GROUP_COL)

    # Build subject -> group_key lookup
    subject_to_key: dict[str, object] = {}
    for key in grouped.groups.keys():
        subject_to_key[cfg.subject_id(key)] = key

    # Subject filter
    subjects_filter = args.subjects or args.subjects_alias
    requested = set(subjects_filter) if subjects_filter else None

    clients = get_all_clients()

    subject_results = []
    downloaded = 0
    still_running = 0

    for row in filtered:
        display_name = row["display_name"]
        # Read subjects from both new and legacy column names
        subjects_str = row.get("subjects", "") or row.get("handles", "")
        is_batch = (display_name.startswith(cfg.BATCH_PREFIX)
                    or display_name.startswith(cfg.RETRY_PREFIX))

        row_key_id = int(row.get("key_id", "") or 1)
        if row_key_id not in clients:
            print(f"  [WARN] No client for key_id={row_key_id}, using key_id={min(clients)}")
        client = clients.get(row_key_id, clients[min(clients)])

        if is_batch:
            batch_subjects = subjects_str.split(";") if subjects_str else []
        else:
            batch_subjects = [display_name]

        print(f"\n--- {display_name} ({len(batch_subjects)} subject{'s' if len(batch_subjects) != 1 else ''}) [key={row_key_id}] ---")

        try:
            if args.poll:
                job = poll_existing_batch(
                    client, row["job_name"],
                    job_log_path=cfg.JOB_LOG_PATH,
                    display_name=display_name,
                    model=row.get("model", cfg.MODEL),
                    jsonl_path=row.get("jsonl_path", ""),
                    subjects=subjects_str,
                    key_id=str(row_key_id),
                )
            else:
                job = client.batches.get(name=row["job_name"])

            state = job.state.name if hasattr(job.state, "name") else str(job.state)

            prev_state = row.get("state", "")
            if state != prev_state and not args.poll:
                result_file = ""
                if state == "JOB_STATE_SUCCEEDED" and hasattr(job, "dest") and job.dest:
                    result_file = getattr(job.dest, "file_name", "")
                log_batch_job(
                    cfg.JOB_LOG_PATH, row["job_name"], display_name,
                    row.get("model", cfg.MODEL), state,
                    jsonl_path=row.get("jsonl_path", ""), subjects=subjects_str,
                    result_file=result_file, created_at=job_created_at(job),
                    key_id=str(row_key_id),
                )
                print(f"  [{display_name}] changed from {prev_state} to {state}")

            if state in TERMINAL_STATES and state != "JOB_STATE_SUCCEEDED":
                print(f"  [{display_name}] {state}")
                if hasattr(job, "error") and job.error:
                    print(f"  [{display_name}] Error: {job.error}")

            if state not in TERMINAL_STATES:
                for s in batch_subjects:
                    subject_results.append((s, display_name, state, "-", "-"))
                still_running += 1
                continue

            if state != "JOB_STATE_SUCCEEDED":
                for s in batch_subjects:
                    subject_results.append((s, display_name, state, "0", "0%"))
                continue

            parsed = parse_batch_results(client, job)

            if is_batch:
                by_subject = split_results_by_subject(parsed)
            else:
                by_subject = {batch_subjects[0]: parsed}

            for subject in batch_subjects:
                if requested and subject not in requested:
                    continue

                ckpt_path = os.path.join(cfg.BATCH_CHECKPOINT_DIR,
                                         f"{cfg.CHECKPOINT_PREFIX}{subject}.xlsx")
                if os.path.isfile(ckpt_path):
                    subject_results.append((subject, display_name, "DONE (checkpoint)", "-", "-"))
                    if args.cleanup or args.cleanup_ok:
                        cleanup_ok_files(subject, clients)
                    continue

                group_key = subject_to_key.get(subject)
                if not group_key:
                    subject_results.append((subject, display_name, "ERROR: subject not found", "-", "-"))
                    continue

                subject_df = grouped.get_group(group_key)
                subject_rows = subject_df.to_dict(orient="records")

                subject_res = by_subject.get(subject, {})
                ok_count = sum(1 for r in subject_res.values() if r["ok"])
                ok_rate = f"{ok_count / len(subject_res) * 100:.0f}%" if subject_res else "0%"

                coverage = len(subject_res) / len(subject_rows) if subject_rows else 0
                if coverage < args.min_coverage:
                    print(f"  [SKIP] Coverage for {subject}: {len(subject_res)}/{len(subject_rows)} "
                          f"({coverage:.0%}) below --min-coverage {args.min_coverage:.0%}")
                    subject_results.append((subject, display_name, f"LOW COVERAGE ({coverage:.0%})",
                                            str(len(subject_res)), ok_rate))
                    continue

                if coverage < 0.9:
                    print(f"  [WARN] Low coverage for {subject}: {len(subject_res)}/{len(subject_rows)} "
                          f"({coverage:.0%})")

                result_df = results_to_dataframe(
                    subject_rows, subject_res, key_column=cfg.FILE_COL
                )
                save_checkpoint(result_df, ckpt_path)
                subject_results.append((subject, display_name, state, str(len(subject_res)), ok_rate))
                downloaded += 1

                if args.cleanup or args.cleanup_ok:
                    cleanup_ok_files(subject, clients)

        except Exception as e:
            for s in batch_subjects:
                subject_results.append((s, display_name, f"ERROR: {e}", "-", "-"))

    print(f"\n{'Subject':<30} {'Batch':<20} {'State':<30} {'Rows':>6} {'OK':>6}")
    print("-" * 94)
    for subject, batch, state, rows, ok in subject_results:
        print(f"{subject:<30} {batch:<20} {state:<30} {rows:>6} {ok:>6}")

    print(f"\n{'='*60}")
    print(f"Downloaded: {downloaded}, Running: {still_running}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
