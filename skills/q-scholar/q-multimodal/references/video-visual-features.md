# Video Visual Features — Detailed Reference

Script: `scripts/pillow/video_features.py`

Extracts frames from videos via PySceneDetect (default) or FFmpeg, then runs Pillow analysis per frame. Produces dual output: frame-level and video-level (aggregated) checkpoints.

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
| `--extractor` | `scenedetect` | Frame extraction strategy: `scenedetect` or `ffmpeg` |
| `--frame-mode` | `middle` | scenedetect only: `middle`, `boundaries`, or `evenly-spaced` |
| `--frames-per-scene` | 3 | scenedetect only: N frames per scene when `--frame-mode evenly-spaced` |
| `--scene-threshold` | 27.0 | scenedetect only: ContentDetector HSV threshold; lower = more scenes |
| `--min-scene-len` | 15 | scenedetect only: minimum scene length in frames |
| `--fps` | 1.0 | ffmpeg only: frames per second to extract |
| `--subjects` | all | Process only these subjects |
| `--max-workers` | 10 | Concurrent workers |
| `--preview` | off | Dry run: show pending subjects and counts, then exit |

## Frame Extraction

Two strategies are available via `--extractor`:

### Scene-Based (default: `--extractor scenedetect`)

PySceneDetect's ContentDetector identifies scene boundaries by HSV content changes. OpenCV reads the target frame(s) from each detected scene. Three sampling modes via `--frame-mode`:

- `middle` (default): 1 frame at the midpoint of each scene — most representative, smallest output
- `boundaries`: 2 frames per scene (scene start + scene end) — captures transitions
- `evenly-spaced`: N frames per scene, evenly distributed; N set by `--frames-per-scene` (default 3)

Tuning flags (apply to all modes):

- `--scene-threshold` (default 27.0): HSV content-delta threshold; lower = more scenes
- `--min-scene-len` (default 15 frames): minimum scene length to avoid flicker splits

Frame-level output always includes `scene_id`, `scene_start`, `scene_end` (seconds) when `--extractor scenedetect` — produced by default with no additional flag. If no scenes are detected (e.g., single-shot video), the whole video is treated as one scene.

### Fixed-Interval (`--extractor ffmpeg`)

FFmpeg extracts frames at a constant rate. Use for dense temporal sampling or when scene detection is undesirable (e.g., single-shot videos, static cameras).

- `--fps` (default 1.0): frames per second; ignored when `--extractor scenedetect`
- `scene_id`, `scene_start`, `scene_end` columns are `NaN`
- `--frame-mode` / `--frames-per-scene` / `--scene-threshold` / `--min-scene-len` are ignored

Frame numbering is 1-indexed in both strategies. `second` is the timestamp of the extracted frame in the source video. Frames are written to a temporary directory and cleaned up after processing.

Supported video formats: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`

## Dual Output

### Frame-Level Checkpoints

Path: `<output-dir>/frames/checkpoints/<subject>.xlsx`

One row per extracted frame. Columns: `file_path | frame_number | second | scene_id | scene_start | scene_end | feature columns | ok`

The `frame_number` and `second` columns identify when in the video the frame was captured. `scene_id` is the 1-indexed detected-scene number; `scene_start` and `scene_end` are the scene's start/end timestamps in seconds. These three scene columns are populated when `--extractor scenedetect` and `NaN` when `--extractor ffmpeg`.

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
- **Very short videos**: scenedetect treats the whole video as a single scene if no cuts are detected; ffmpeg may extract 0-1 frames at low `--fps`
- **FFmpeg not found**: Script exits with error message (only relevant to `--extractor ffmpeg`)
- **PySceneDetect / OpenCV missing**: `--extractor scenedetect` raises a clear install hint (`pip install scenedetect[opencv]`)
- **PySceneDetect decoder failure**: Video marked `ok=False` with error; rerun that subject with `--extractor ffmpeg` as a workaround
- **Corrupt video frames**: Individual frames logged as warning, processing continues

## Performance

- Frame extraction is sequential per video (FFmpeg subprocess or PySceneDetect+OpenCV)
- Pillow analysis of extracted frames uses `--max-workers` threads
- Scene-based extraction typically yields far fewer frames than fixed-interval sampling; expect faster downstream Pillow analysis with `--frame-mode middle`
- Tip: Set `PYTHONUNBUFFERED=1` for real-time progress output
