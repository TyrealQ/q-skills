# Video Visual Features — Detailed Reference

Script: `scripts/pillow/video_features.py`

Extracts frames from videos via FFmpeg, then runs Pillow analysis per frame. Produces dual output: frame-level and video-level (aggregated) checkpoints.

## All CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required) | Input file (xlsx, csv, json, parquet, etc.) |
| `--base-dir` | (required) | Base directory for resolving relative file paths |
| `--output-dir` | `output/pillow_video` | Checkpoint output directory |
| `--file-col` | `file_path` | Column containing file paths |
| `--group-col` | (auto) | Column to group by subject; default: parent directory of file path |
| `--id-cols` | file column only | Source columns to keep in output (default: file column only) |
| `--features` | `rgb,hsv,texture,shape,spatial,quality` | Comma-separated feature categories (default: all except exif) |
| `--fps` | 1.0 | Frames per second to extract |
| `--subjects` | all | Process only these subjects |
| `--max-workers` | 10 | Concurrent workers |
| `--preview` | off | Dry run: show pending subjects and counts, then exit |

## Frame Extraction

FFmpeg extracts frames as JPEG at the specified FPS rate:
- Default 1 FPS = one frame per second of video
- Higher FPS captures more temporal detail but increases processing time and output size
- Frames are extracted to a temporary directory and cleaned up after processing
- Frame numbering is 1-indexed; `second` is computed as `(frame_number - 1) / fps`

Supported video formats: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`

## Dual Output

### Frame-Level Checkpoints

Path: `<output-dir>/frames/checkpoints/<subject>.xlsx`

One row per extracted frame. Columns: `file_path | frame_number | second | feature columns | ok`

The `frame_number` and `second` columns identify when in the video the frame was captured.

### Video-Level Checkpoints

Path: `<output-dir>/videos/checkpoints/<subject>.xlsx`

One row per video. Columns: `file_path | aggregated features | frame_count | ok_ratio | ok`

**Aggregation logic:**
- Numeric features: `mean`, `std`, `min`, `max` (4 columns per feature, e.g., `brightness_mean`, `brightness_std`, `brightness_min`, `brightness_max`)
- Categorical features (dominant colors, EXIF strings): `mode` (most frequent value)
- `frame_count`: total frames extracted from the video
- `ok_ratio`: fraction of frames with `ok=True`
- `ok`: `True` if at least one frame was successfully processed

Column count varies based on feature selection and id_cols. With default features (34 numeric): ~133 aggregated columns + id_cols.

## Idempotency

The script checks for existing video-level checkpoints. If `<output-dir>/videos/checkpoints/<subject>.xlsx` exists, the subject is skipped. Delete both frame and video checkpoints to reprocess.

## Feature Categories

Same categories as the image pipeline (see `references/image-visual-features.md`). The `exif` category is accepted but generally not useful since FFmpeg-extracted JPEG frames do not carry EXIF metadata.

## Edge Cases

- **Audio-only files**: No frames extracted, row saved with `ok=False`
- **Very short videos** (<1 second at default FPS): May extract 0-1 frames
- **FFmpeg not found**: Script exits with error message
- **Corrupt video frames**: Individual frames logged as warning, processing continues

## Performance

- Frame extraction is sequential per video (FFmpeg subprocess)
- Pillow analysis of extracted frames uses `--max-workers` threads
- Tip: Set `PYTHONUNBUFFERED=1` for real-time progress output
