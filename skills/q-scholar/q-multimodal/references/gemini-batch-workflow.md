# Gemini Batch Pipeline — Detailed Workflow

Six scripts in `scripts/gemini/batch/`, run in order. Each step is idempotent — rerunning skips already-completed work. File API URIs expire after 48 hours, so complete the pipeline within that window.

## Step 0: Upload Media (`0uploadMedia.py`)

Upload media files to Gemini File API. Saves URI maps per subject with `key_id` tracking.

| Goal | Command |
|------|---------|
| Upload with key 1 | `python 0uploadMedia.py --config config.py --key 1` |
| Specific subjects | `python 0uploadMedia.py --config config.py --subjects s1 s2 --key 1` |
| From file list | `python 0uploadMedia.py --config config.py --subjects-file ids.txt --key 1` |
| Preview sizes | `python 0uploadMedia.py --config config.py --preview` |
| Upload + auto-submit batches | `python 0uploadMedia.py --config config.py --submit --max-batch-gb 2 --key 1` |

25 concurrent upload workers. Auto-stops at 18 GB media (leaves 2 GB headroom for JSONL uploads within the 20 GB File API storage quota). Sorts subjects smallest-first to maximize uploads before quota. With `--submit`, builds and submits batch jobs progressively in ~2 GB chunks during upload — this combines steps 0–2 into one command.

## Step 1: Build JSONL (`1buildJsonl.py`)

Groups subjects by `key_id`.

| Goal | Command |
|------|---------|
| Build JSONL files | `python 1buildJsonl.py --config config.py --max-batch-gb 2` |
| Build + auto-submit | `python 1buildJsonl.py --config config.py --submit --max-batch-gb 2` |

Skip this step if step 0 used `--submit`.

## Step 2: Submit Jobs (`2submitJobs.py`)

Auto-detects `key_id` from URI maps.

| Goal | Command |
|------|---------|
| Submit all pending | `python 2submitJobs.py --config config.py` |
| Preview | `python 2submitJobs.py --config config.py --preview` |
| Override API key | `python 2submitJobs.py --config config.py --key 2` |

Skip this step if step 0 or 1 used `--submit`. Logs jobs to `batch_jobs.csv` with `key_id`, subjects, and state.

## Step 3: Poll & Download (`3checkStatus.py`)

Poll batch jobs, download results, split by subject, save per-subject checkpoints.

| Goal | Command |
|------|---------|
| Quick status check | `python 3checkStatus.py --config config.py` |
| Block until all complete | `python 3checkStatus.py --config config.py --poll` |
| Cleanup all result files after save | `python 3checkStatus.py --config config.py --cleanup` |
| Cleanup OK files after save | `python 3checkStatus.py --config config.py --cleanup-ok` |

Reads `key_id` per job from CSV to use the correct API client. Splits multi-subject results by file path. Saves checkpoints to `<BATCH_CHECKPOINT_DIR>/<CHECKPOINT_PREFIX><subject_id>.xlsx`.

## Step 4: Retry Errors (`4retryErrors.py`)

Scan checkpoints for `model_ok=False` rows, retry via batch or live API fallback.

| Goal | Command |
|------|---------|
| Preview error counts | `python 4retryErrors.py --config config.py --preview` |
| Build retry JSONL only | `python 4retryErrors.py --config config.py --build` |
| Build + submit retry batch | `python 4retryErrors.py --config config.py --submit` |
| Collect retry results | `python 4retryErrors.py --config config.py --collect` |
| Live API fallback | `python 4retryErrors.py --config config.py --standard` |
| Export unretryable rows | `python 4retryErrors.py --config config.py --export-failed` |

**Retry workflow**:
1. `--preview` to see what failed — note the **total** failed rows across all subjects
2. If **> 500 total rows**: `--submit` to batch retry (50% discount)
3. If **<= 500 total rows**: `--standard` for speed (skip to live API)
4. For batch path: wait for retry jobs (`3checkStatus.py`), then `--collect`
5. Repeat batch cycle up to 3 times (retry_count tracked per row)
6. `--standard` for any rows that fail 3+ batch attempts
7. `--export-failed` for rows that failed all retries

## Step 5: Review & Merge (`5review.py`)

Validate checkpoints and merge into final output.

| Goal | Command |
|------|---------|
| Review all checkpoints | `python 5review.py --config config.py` |
| Fix column order issues | `python 5review.py --config config.py --fix` |
| Review + merge to final | `python 5review.py --config config.py --merge` |

Validates column order, analysis field coverage, score ranges, and model_ok counts. `--merge` concatenates all checkpoints, deduplicates by file_path, drops retry_count, and disables Excel URL auto-detection.

## Quick Reference: Full Batch Run

End-to-end using progressive submit (combines steps 0–2):

```bash
cd scripts/gemini/batch

# Upload + auto-build + auto-submit
python 0uploadMedia.py --config /path/to/config.py --submit --max-batch-gb 2 --key 1

# Poll until done
python 3checkStatus.py --config /path/to/config.py --poll

# Retry errors
python 4retryErrors.py --config /path/to/config.py --preview
python 4retryErrors.py --config /path/to/config.py --submit
# (wait for retry jobs)
python 4retryErrors.py --config /path/to/config.py --collect

# Fallback for stubborn errors
python 4retryErrors.py --config /path/to/config.py --standard

# Review and merge
python 5review.py --config /path/to/config.py --fix
python 5review.py --config /path/to/config.py --merge
```

## Error Handling

| Error | Resolution |
|-------|-----------|
| Storage quota exhausted | Auto-stops upload; submit existing jobs to free space, then switch `--key` |
| RECITATION blocked | Batch retry → live fallback → accept loss |
| Expired File API URIs | Step 4 auto re-uploads during retry |
