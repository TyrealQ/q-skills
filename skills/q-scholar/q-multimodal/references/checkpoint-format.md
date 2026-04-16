# Checkpoint Format — Detailed Reference

## Gemini Checkpoints

Column order: `source columns | analysis fields | raw_json | model_ok` (+ `retry_count` after retry step)

Analysis fields are defined by the system prompt and `ANALYSIS_FIELDS` list in `pipeline_config.py`. The `retry_count` column is only present after `4retryErrors.py` processes a checkpoint; first-pass checkpoints from standard or batch pipelines do not include it.

### Validation

Validation is split between the system prompt (defines rules) and `5review.py` (enforces via config):

**Enforced by** `5review.py`: Missing analysis fields flagged, column order checked, `model_ok` counts reported. Custom validation via `validate_row()` in `pipeline_config.py`.

**Defined in system prompt but not script-enforced**: Domain-specific rules depend on the LLM following the system prompt correctly. Use `validate_row()` to add post-hoc checks.

Merged output drops `retry_count`.

## Local Pipeline Checkpoints (Pillow, Video, openSMILE)

Column order: `id_cols (or all source columns) | feature columns | ok`

### Excel Formatting

Input is read via `read_input()` from `scripts/common.py`, which auto-detects format by extension (xlsx, csv, json, parquet, tsv). Output checkpoints use `save_excel()`:
- Bold + centered headers
- Auto-fit column widths from sample (capped at 55 chars)
- Frozen header row at A2
- Engine: openpyxl

### Idempotency

All scripts check for existing checkpoints before processing:
- If the subject's checkpoint file exists at its pipeline-specific location, the subject is skipped
- To reprocess a subject, delete its checkpoint file
- The `--preview` flag shows pending vs. already-done counts

### Output Column Counts

| Pipeline | Output type | Columns | Breakdown |
|----------|------------|---------|-----------|
| Image visual | Per-subject | (user id_cols) + up to 47 features + ok | Width depends on `--id-cols` (default: file column only) and `--features` selection (default 34, all 47 with exif) |
| Video visual | Frame-level | 38 | file_path + frame_number + second + 34 features + ok |
| Video visual | Video-level | ~130–140 | file_path + numeric features × 4 (mean/std/min/max) + categorical features × 1 (mode) + frame_count + ok_ratio + ok |
| Audio (emobase) | Per-subject | 114 | file_path + 8 scores + 104 raw mean/std + ok |

### Output Directory Structure

Checkpoint paths vary by pipeline:

```
output/pillow_image/checkpoints/<subject>.xlsx          # image
output/opensmile/checkpoints/<subject>.xlsx             # audio
output/pillow_video/frames/checkpoints/<subject>.xlsx   # video frame-level
output/pillow_video/videos/checkpoints/<subject>.xlsx   # video aggregate
output/standard/<CHECKPOINT_PREFIX><subject_id>.xlsx   # Gemini standard
output/batch/checkpoints/<CHECKPOINT_PREFIX><subject_id>.xlsx  # Gemini batch
```

For video features, two parallel structures:
```
output/pillow_video/
  frames/
    checkpoints/<subject>.xlsx         # one row per frame
  videos/
    checkpoints/<subject>.xlsx         # one row per video
```

## Merged Output

All local pipelines support `--merge` to compile per-subject checkpoints into a single file. Can be used standalone (`--merge` only) or after processing (`--input ... --merge`).

**Merged file locations** (saved next to `checkpoints/` directory):

| Pipeline | Merged output |
|----------|--------------|
| Image visual | `output/pillow_image/_image_features.xlsx` |
| Video frames | `output/pillow_video/frames/_frame_features.xlsx` |
| Video videos | `output/pillow_video/videos/_video_features.xlsx` |
| Audio | `output/opensmile/_audio_features.xlsx` |

**Behavior:**
- Concatenates all `*.xlsx` in the checkpoint directory (sorted alphabetically)
- Deduplicates by `file_path` column for single-row-per-file outputs (image, audio, video-level). Frame-level video output deduplicates by `[file_path, frame_number]` to preserve all frames.
- Files starting with `_` are excluded from merge input (prevents self-inclusion on re-merge)
- Uses `save_excel()` formatting (bold headers, auto-fit widths, frozen panes)

