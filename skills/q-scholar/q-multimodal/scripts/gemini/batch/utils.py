"""Shared utilities for the Gemini analysis pipeline.

Provides config management, multi-key client management, CSV job logging,
JSON helpers, batch submission, result parsing, and single-row analysis
used across all pipeline scripts.
"""

import csv
import heapq
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Pipeline configuration
# ---------------------------------------------------------------------------

_cfg = None


def init_config(config_path=None):
    """Load and validate pipeline configuration.

    Discovery chain:
        1. config_path argument (from --config CLI flag)
        2. GEMINI_PIPELINE_CONFIG environment variable
        3. ./pipeline_config.py in current working directory
        4. Error with instructions

    Returns the loaded config module.
    """
    global _cfg
    import importlib.util

    if config_path is None:
        config_path = os.getenv("GEMINI_PIPELINE_CONFIG")
    if config_path is None:
        if os.path.isfile("pipeline_config.py"):
            config_path = "pipeline_config.py"
        else:
            raise RuntimeError(
                "No pipeline config found. Provide --config <path>, "
                "set GEMINI_PIPELINE_CONFIG env var, "
                "or place pipeline_config.py in the current directory.\n"
                "Copy the template from scripts/gemini/pipeline_config.py."
            )

    config_path = os.path.abspath(config_path)
    spec = importlib.util.spec_from_file_location("pipeline_config", config_path)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)

    # Validate required fields
    required = [
        "BASE_DIR", "INPUT_PATH", "SYSTEM_PROMPT_PATH",
        "GROUP_COL", "FILE_COL", "ANALYSIS_FIELDS",
        "subject_id", "format_metadata",
    ]
    missing = [f for f in required if not hasattr(cfg, f)]
    if missing:
        raise RuntimeError(f"Config missing required fields: {', '.join(missing)}")

    # Defaults for optional fields
    defaults = {
        "MODEL": "gemini-3.1-pro-preview",
        "TEMPERATURE": 1,
        "THINKING_LEVEL": "HIGH",
        "OUTPUT_DIR": "output",
        "CHECKPOINT_PREFIX": "subject_",
        "BATCH_PREFIX": "batch_",
        "RETRY_PREFIX": "retry_",
        "MERGED_FILENAME": "analysis.xlsx",
        "METADATA_COLS": [],
    }
    for key, val in defaults.items():
        if not hasattr(cfg, key):
            setattr(cfg, key, val)

    if not hasattr(cfg, "validate_row"):
        cfg.validate_row = lambda data: []

    # Resolve relative paths against BASE_DIR
    base = cfg.BASE_DIR
    if not os.path.isabs(cfg.INPUT_PATH):
        cfg.INPUT_PATH = os.path.join(base, cfg.INPUT_PATH)
    if not os.path.isabs(cfg.SYSTEM_PROMPT_PATH):
        cfg.SYSTEM_PROMPT_PATH = os.path.join(base, cfg.SYSTEM_PROMPT_PATH)

    # Resolve OUTPUT_DIR to absolute
    if not os.path.isabs(cfg.OUTPUT_DIR):
        cfg.OUTPUT_DIR = os.path.join(base, cfg.OUTPUT_DIR)
    out = cfg.OUTPUT_DIR
    cfg.STANDARD_CHECKPOINT_DIR = os.path.join(out, "standard")
    cfg.BATCH_CHECKPOINT_DIR = os.path.join(out, "batch", "checkpoints")
    cfg.URI_MAP_DIR = os.path.join(out, "batch", "uri_maps")
    cfg.JSONL_DIR = os.path.join(out, "batch", "jsonl")
    cfg.RETRY_JSONL_DIR = os.path.join(out, "batch", "retry", "jsonl")
    cfg.JOB_LOG_PATH = os.path.join(out, "batch", "batch_jobs.csv")
    cfg.MERGED_OUTPUT = os.path.join(out, cfg.MERGED_FILENAME)

    _cfg = cfg
    return cfg


def get_config():
    """Return the loaded config. Call init_config() first."""
    if _cfg is None:
        raise RuntimeError("Config not initialized. Call init_config() first.")
    return _cfg


def add_config_arg(parser):
    """Add --config argument to an argparse parser."""
    parser.add_argument(
        "--config", dest="config_path", default=None,
        help="Path to pipeline_config.py (auto-discovered if omitted)",
    )


# ---------------------------------------------------------------------------
# Constants (infrastructure, not domain-specific)
# ---------------------------------------------------------------------------

TERMINAL_STATES = {
    "JOB_STATE_SUCCEEDED", "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED",
}

TERMINAL_FAILED = {"JOB_STATE_FAILED", "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"}


# ---------------------------------------------------------------------------
# Multi-key client management
# ---------------------------------------------------------------------------

def get_key_count() -> int:
    """Count available GOOGLE_API_KEY{N} entries in the environment."""
    return sum(1 for i in range(1, 11) if os.getenv(f"GOOGLE_API_KEY{i}"))


def get_client(key_id: int = 1) -> genai.Client:
    """Return a Gemini client for the given key_id (1-based).

    Reads GOOGLE_API_KEY{key_id} from the environment.
    """
    env_var = f"GOOGLE_API_KEY{key_id}"
    api_key = os.getenv(env_var)
    if not api_key:
        raise RuntimeError(f"Missing {env_var} in environment.")
    return genai.Client(api_key=api_key)


def get_all_clients() -> dict[int, genai.Client]:
    """Return {key_id: client} for all available API keys.

    Checks GOOGLE_API_KEY (unnumbered, mapped to key_id=0), then
    GOOGLE_API_KEY1 through GOOGLE_API_KEY10, tolerating gaps.
    """
    clients = {}
    # Unnumbered key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        clients[0] = genai.Client(api_key=api_key)
    # Numbered keys
    for key_id in range(1, 11):
        api_key = os.getenv(f"GOOGLE_API_KEY{key_id}")
        if api_key:
            clients[key_id] = genai.Client(api_key=api_key)
    if not clients:
        raise RuntimeError(
            "No GOOGLE_API_KEY or GOOGLE_API_KEY{N} found in environment."
        )
    return clients


# ---------------------------------------------------------------------------
# URI map helpers
# ---------------------------------------------------------------------------

def uri_map_path(subject: str) -> str:
    """Return the path to a subject's URI map JSON."""
    cfg = get_config()
    return os.path.join(cfg.URI_MAP_DIR, f"{subject}.json")


def load_uri_map(subject: str) -> dict | None:
    """Load a saved URI map JSON. Returns None if not found."""
    path = uri_map_path(subject)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_uri_map_key_id(subject: str) -> int:
    """Read key_id from a subject's URI map (defaults to 1)."""
    data = load_uri_map(subject)
    if data is None:
        return 1
    return int(data.get("key_id", 1))


# ---------------------------------------------------------------------------
# CSV job log
# ---------------------------------------------------------------------------

JOB_LOG_FIELDS = [
    "job_name", "display_name", "model", "state",
    "jsonl_path", "subjects", "result_file",
    "created_at", "updated_at", "key_id",
]


def read_job_log(csv_path: str) -> list[dict]:
    """Read batch job CSV log. Returns empty list if file missing."""
    if not os.path.isfile(csv_path):
        return []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def log_batch_job(
    csv_path: str,
    job_name: str,
    display_name: str,
    model: str,
    state: str,
    *,
    jsonl_path: str = "",
    subjects: str = "",
    result_file: str = "",
    created_at: str = "",
    key_id: str = "",
) -> None:
    """Append or update a batch job entry in the CSV log."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    found = False
    existing_headers: list[str] = []

    if os.path.isfile(csv_path):
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_headers = reader.fieldnames or []
            for row in reader:
                if row.get("job_name") == job_name:
                    row["state"] = state
                    row["updated_at"] = now
                    if result_file:
                        row["result_file"] = result_file
                    if key_id:
                        row["key_id"] = key_id
                    found = True
                rows.append(row)

    if not found:
        rows.append({
            "job_name": job_name,
            "display_name": display_name,
            "model": model,
            "state": state,
            "jsonl_path": jsonl_path,
            "subjects": subjects,
            "result_file": result_file,
            "created_at": created_at or now,
            "updated_at": now,
            "key_id": str(key_id),
        })

    # Merge: keep expected order, append any extra columns from CSV
    headers = list(JOB_LOG_FIELDS)
    for h in existing_headers:
        if h not in headers:
            headers.append(h)
    # Backward compat: if CSV has "handles" column, keep it
    if "handles" in existing_headers and "handles" not in headers:
        headers.append("handles")

    parent = os.path.dirname(csv_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def job_created_at(job) -> str:
    """Extract create_time from API job object as ISO string."""
    ct = getattr(job, "create_time", None)
    if ct:
        return ct.astimezone(timezone.utc).isoformat(timespec="seconds")
    return ""


# ---------------------------------------------------------------------------
# JSONL helpers
# ---------------------------------------------------------------------------

def extract_subject_from_key(key: str) -> str | None:
    """Extract subject ID from a JSONL key.

    New format: 'subject_id::path/to/file' -- split on '::'
    Legacy format: 'assets/player_<handle>/...' -- regex fallback
    """
    if "::" in key:
        return key.split("::", 1)[0]
    m = re.search(r"assets/player_([^/]+)/", key)
    return m.group(1) if m else None


def extract_subjects_from_jsonl(jsonl_path: str) -> list[str]:
    """Extract unique subject IDs from JSONL keys."""
    subjects = set()
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = entry.get("key", "")
            sid = extract_subject_from_key(key)
            if sid:
                subjects.add(sid)
    return sorted(subjects)


def load_system_prompt() -> str:
    """Load the system prompt from the config path."""
    cfg = get_config()
    if not os.path.isfile(cfg.SYSTEM_PROMPT_PATH):
        raise FileNotFoundError(f"System prompt not found: {cfg.SYSTEM_PROMPT_PATH}")
    with open(cfg.SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def try_json_load(s: str):
    """Parse a string as JSON, falling back to the first valid {...} object."""
    if not s:
        return None
    s = s.strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        for i, ch in enumerate(s):
            if ch == '{':
                try:
                    obj, _ = decoder.raw_decode(s, i)
                    return obj
                except json.JSONDecodeError:
                    continue
        return None


def flatten_dict(d, parent_key="", sep="."):
    """Flatten nested dicts into dot-notation keys."""
    items = {}
    for k, v in (d or {}).items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items


def list_to_excel_str(v):
    """Convert lists to semicolon-separated strings for Excel."""
    if v is None:
        return ""
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return v


# ---------------------------------------------------------------------------
# Subject distribution across keys
# ---------------------------------------------------------------------------

def split_subjects_by_key(
    subjects: list[tuple[str, int]],
    num_keys: int,
) -> list[tuple[int, int, list]]:
    """Bin-pack subjects across N keys by media size (greedy, largest first).

    Args:
        subjects: list of (subject_id, size_bytes) tuples
        num_keys: number of API keys to distribute across

    Returns sorted list of (total_bytes, key_id, [(subject_id, size_bytes)]).
    """
    sorted_subjects = sorted(subjects, key=lambda x: x[1], reverse=True)

    buckets: list[tuple[int, int, list]] = [(0, k, []) for k in range(1, num_keys + 1)]
    heapq.heapify(buckets)

    for subject, size in sorted_subjects:
        total, key_id, items = heapq.heappop(buckets)
        items.append((subject, size))
        heapq.heappush(buckets, (total + size, key_id, items))

    return sorted(buckets, key=lambda x: x[1])


# ---------------------------------------------------------------------------
# Batch submission
# ---------------------------------------------------------------------------

def submit_batch(
    client: genai.Client,
    model: str,
    jsonl_path: str,
    display_name: str,
    job_log_path: str = "",
    subjects: str = "",
    key_id: int = 1,
) -> object:
    """Upload JSONL, submit batch job, log to CSV. No polling."""
    uploaded = client.files.upload(
        file=jsonl_path,
        config=types.UploadFileConfig(
            display_name=display_name,
            mime_type="jsonl",
        ),
    )
    print(f"  Uploaded JSONL as {uploaded.name}")

    job = client.batches.create(
        model=model,
        src=uploaded.name,
        config={"display_name": display_name},
    )
    state = job.state.name if hasattr(job.state, "name") else str(job.state)
    print(f"  Batch job created: {job.name} ({state})")

    if job_log_path:
        log_batch_job(
            job_log_path, job.name, display_name, model, state,
            jsonl_path=jsonl_path, subjects=subjects,
            created_at=job_created_at(job), key_id=str(key_id),
        )

    return job


# ---------------------------------------------------------------------------
# Result parsing
# ---------------------------------------------------------------------------

def parse_batch_results(client: genai.Client, job) -> dict[str, dict]:
    """Download and parse batch results into {key: parsed_result}.

    Returns {key: {"ok": bool, "data": dict, "raw_json": str}}.
    """
    state = job.state.name if hasattr(job.state, "name") else str(job.state)
    if state != "JOB_STATE_SUCCEEDED":
        print(f"  [ERROR] Job did not succeed: {state}")
        return {}

    result_bytes = client.files.download(file=job.dest.file_name)
    content = result_bytes.decode("utf-8") if isinstance(result_bytes, bytes) else result_bytes

    results: dict[str, dict] = {}
    for line in content.splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        key = entry.get("key", "")
        response = entry.get("response", {})

        raw_text = ""
        try:
            candidates = response.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "text" in part:
                        raw_text += part["text"]
        except Exception as e:
            print(f"  [WARN] Failed to parse response for key={key}: {e}")
            raw_text = json.dumps(response)

        data = try_json_load(raw_text)
        # Unwrap single-item lists (Gemini sometimes wraps the dict in a list)
        if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
            data = data[0]
        if data is not None and isinstance(data, dict):
            flat = flatten_dict(data)
            results[key] = {
                "ok": True,
                "data": flat,
                "raw_json": json.dumps(data, ensure_ascii=False),
            }
        else:
            results[key] = {
                "ok": False,
                "data": {},
                "raw_json": raw_text,
            }

    return results


def split_results_by_subject(results: dict[str, dict]) -> dict[str, dict[str, dict]]:
    """Bucket parsed results by subject ID extracted from keys.

    Keys in the returned per-subject dicts have the subject prefix stripped
    (for new-format keys) so downstream code can look up by file_path alone.
    """
    by_subject: dict[str, dict[str, dict]] = {}
    for key, result in results.items():
        subject = extract_subject_from_key(key)
        if subject is None:
            continue
        # Strip subject prefix for downstream lookups by file_path
        if "::" in key:
            stripped_key = key.split("::", 1)[1]
        else:
            stripped_key = key
        by_subject.setdefault(subject, {})[stripped_key] = result
    return by_subject


# ---------------------------------------------------------------------------
# JSONL building
# ---------------------------------------------------------------------------

def build_batch_jsonl(
    subject_groups: list[tuple[str, list[dict], dict[str, str]]],
    system_prompt: str,
    jsonl_path: str,
) -> int:
    """Build a JSONL file for batch requests.

    Each subject_group is (subject_id, rows, uri_map).
    Returns the number of lines written.
    """
    cfg = get_config()
    count = 0
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for subject, rows, uri_map in subject_groups:
            for row in rows:
                fp = row[cfg.FILE_COL]
                abs_path = os.path.join(cfg.BASE_DIR, fp)
                file_uri = uri_map.get(abs_path)
                if not file_uri:
                    continue

                ext = Path(fp).suffix.lower()
                mime = "video/mp4" if ext == ".mp4" else "image/jpeg"

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
# Single-row analysis (standard pipeline, shared with retry)
# ---------------------------------------------------------------------------

_SP_PREFIX = (
    "IMPORTANT: For any text visible in the image, summarize its meaning "
    "in your own words. Do not quote or reproduce text verbatim.\n\n"
)


def analyze_single_row(
    client: genai.Client,
    idx: int,
    row: dict,
    system_prompt: str,
) -> dict:
    """Call Gemini with inline media bytes for a single row.

    Returns {"ok": bool, "data": dict, "raw_json": str}.
    """
    cfg = get_config()
    fp = row.get(cfg.FILE_COL, "")
    abs_path = os.path.join(cfg.BASE_DIR, fp)

    if not os.path.isfile(abs_path):
        return {"ok": False, "data": {}, "raw_json": f"File not found: {abs_path}"}

    try:
        with open(abs_path, "rb") as fh:
            media_bytes = fh.read()
    except Exception as e:
        return {"ok": False, "data": {}, "raw_json": f"Failed to read file: {e}"}

    ext = Path(fp).suffix.lower()
    if ext == ".mp4":
        media_part = types.Part.from_bytes(data=media_bytes, mime_type="video/mp4")
    else:
        media_part = types.Part.from_bytes(data=media_bytes, mime_type="image/jpeg")

    metadata_text = cfg.format_metadata(row)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=metadata_text),
                media_part,
            ],
        )
    ]

    gen_config = types.GenerateContentConfig(
        temperature=cfg.TEMPERATURE,
        response_mime_type="application/json",
        system_instruction=[types.Part.from_text(text=_SP_PREFIX + system_prompt)],
        thinking_config=types.ThinkingConfig(thinking_level=cfg.THINKING_LEVEL),
    )

    last_err = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=cfg.MODEL, contents=contents, config=gen_config,
            )

            raw_text = ""
            candidate = response.candidates[0] if response.candidates else None
            parts = (candidate.content.parts or []) if candidate and candidate.content else []
            if not parts:
                reason = getattr(candidate, "finish_reason", "unknown") if candidate else "no candidates"
                return {"ok": False, "data": {}, "raw_json": f"[blocked] {reason}"}
            for part in parts:
                if hasattr(part, "thought") and part.thought:
                    continue
                if part.text:
                    raw_text += part.text

            data = try_json_load(raw_text)
            if data is None:
                return {"ok": False, "data": {}, "raw_json": raw_text}

            if isinstance(data, list):
                data = data[0] if len(data) == 1 and isinstance(data[0], dict) else None
                if data is None:
                    return {"ok": False, "data": {}, "raw_json": raw_text}

            flat = flatten_dict(data)
            return {
                "ok": True,
                "data": flat,
                "raw_json": json.dumps(data, ensure_ascii=False),
            }

        except Exception as e:
            last_err = e
            err_str = str(e)
            retryable = any(code in err_str for code in ("429", "500", "502", "503", "504"))
            if retryable and attempt < 2:
                wait = 2 ** (attempt + 1)
                print(f"  [RETRY] Row {idx} attempt {attempt + 1}/3: {err_str[:80]}... waiting {wait}s")
                time.sleep(wait)
            else:
                if not retryable:
                    print(f"  [ERROR] Row {idx}: {err_str[:120]}")
                break

    return {"ok": False, "data": {}, "raw_json": f"[error] {last_err}"}
