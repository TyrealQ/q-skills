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

Column order: `id_cols + file column | feature columns | (audio diagnostics) | ok`

The file column is always retained, so every row is asset-specific — output filenames and ids survive checkpoints and merges. Audio checkpoints append the diagnostics block (`audio_stream_present`, `audio_signal_ok`, `audio_status`, `audio_rms_dbfs`, `audio_peak_dbfs`, `audio_duration_s`, `audio_error`) before `ok`; see `audio-features.md`.

Id and file columns are read as **text** end-to-end (`read_input(str_cols=...)` and string converters on checkpoint reads). This is load-bearing for long numeric ids: a 19-digit TikTok post id inferred as a number is silently rounded when written back to xlsx (pandas serializes int64 as float — …208031 becomes …207744). Never re-read an output with plain `pd.read_excel` and write it back without string converters on id columns.

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
| Image visual | Per-subject | id_cols + file col + up to 47 features + ok | Width depends on `--id-cols` and `--features` selection (default 34, all 47 with exif) |
| Video visual | Frame-level | ~41+ | id_cols + file col + frame_number + second + scene_id + scene_start + scene_end + 34 features + ok (scene columns are `NaN` when `--extractor ffmpeg`) |
| Video visual | Video-level | ~130–140 | id_cols + file col + numeric features × 4 (mean/std/min/max) + categorical features × 1 (mode) + frame_count + ok_ratio + ok |
| Audio (emobase) | Per-subject | ~121 | id_cols + file col + 8 scores + 104 raw mean/std + 7 diagnostics + ok |

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
- Deduplicates on the asset-level key: `id_cols + file column` (image, audio, video-level); frame-level adds `frame_number`. Never on an id alone — multi-asset posts keep one row per file.
- Key columns are re-read as text during merge, so long numeric ids (e.g. 19-digit TikTok post ids) survive the round-trip exactly
- Fails closed: an unreadable checkpoint, duplicate column names, a missing key column, or a column list that differs from the first valid checkpoint aborts the merge with one exception listing every problem — mismatched schemas are never unioned and null-padded, and no partial merged file is written
- Files starting with `_` are excluded from merge input (prevents self-inclusion on re-merge)
- Uses `save_excel()` formatting (bold headers, auto-fit widths, frozen panes)

