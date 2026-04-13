# Gemini Standard Pipeline — Detailed Reference

Single script: `scripts/gemini/standard/gemini_standard.py` — config-driven, no code modification needed for new projects.

**Model config** (set in `pipeline_config.py`): `MODEL`, `TEMPERATURE`, `THINKING_LEVEL`, `response_mime_type=application/json`

## Config

All project-specific values come from `pipeline_config.py`. See `scripts/gemini/pipeline_config.py` for the template with all fields documented.

Required config fields: `BASE_DIR`, `INPUT_PATH`, `SYSTEM_PROMPT_PATH`, `GROUP_COL`, `FILE_COL`, `ANALYSIS_FIELDS`, `subject_id()`, `format_metadata()`

## Commands

| Goal | Command |
|------|---------|
| All pending subjects | `python gemini_standard.py --config /path/to/config.py` |
| Specific subjects | `python gemini_standard.py --config config.py --subjects id1 id2` |
| Dry run | `python gemini_standard.py --config config.py --preview` |
| Custom concurrency | `python gemini_standard.py --config config.py --max-workers 25` |
| Custom retries | `python gemini_standard.py --config config.py --retries 5` |

The `--players` flag is accepted as a hidden alias for `--subjects` (backward compatibility).

## How It Works

1. Loads config, then input file; skips subjects with existing checkpoints (idempotent)
2. Sends media bytes inline via `Part.from_bytes()` — 25 concurrent workers
3. Two retry layers: 3 per-request retries with exponential backoff on HTTP 429/5xx (inner), plus `--retries N` outer passes over failed rows (default 5)
4. Prepends anti-recitation prefix to system prompt (prevents RECITATION blocks on text-heavy images)
5. Saves per-subject checkpoint to `<STANDARD_CHECKPOINT_DIR>/<CHECKPOINT_PREFIX><subject_id>.xlsx`

## Pipeline Decision

Choose based on dataset size and urgency:

```
Volume > 5 GB or > 10 subjects?
  YES → Time-sensitive (need results within 1 hour)?
    YES → Standard (targeted --subjects)
    NO  → Batch (50% savings)
  NO  → Standard (simpler, faster to start)
```

## Adapting for New Projects

1. Copy `scripts/gemini/pipeline_config.py` to your project directory
2. Set paths: `BASE_DIR`, `INPUT_PATH`, `SYSTEM_PROMPT_PATH`
3. Set schema: `GROUP_COL`, `FILE_COL`, `ANALYSIS_FIELDS`
4. Implement `subject_id(group_value)` to extract a filesystem-safe ID from your grouping column
5. Implement `format_metadata(row)` to format context text per media file
6. Optionally set output prefixes: `CHECKPOINT_PREFIX`, `MERGED_FILENAME`
7. Optionally implement `validate_row(data)` for domain-specific validation
8. Create a system prompt file defining your analysis fields, scoring rules, and domain instructions
