# Audio Features — Detailed Reference

Script: `scripts/opensmile/audio_features.py`

Extracts audio from video/audio files via FFmpeg (16 kHz mono PCM WAV), then runs openSMILE for prosodic and voice quality features. Outputs 8 interpretable scores plus full raw features.

## All CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required) | Input file (xlsx, csv, json, parquet, etc.) |
| `--base-dir` | (required) | Base directory for resolving relative file paths |
| `--output-dir` | `output/opensmile` | Checkpoint output directory |
| `--file-col` | `file_path` | Column containing file paths |
| `--group-col` | (auto) | Column to group by subject; default: parent directory of file path |
| `--id-cols` | identifier only | Additional source columns to keep in output beyond the file column |
| `--feature-set` | `emobase` | openSMILE feature set (see table below) |
| `--feature-level` | `functionals` | Extraction level: `functionals` (one row per file) or `lld` (frame-level) |
| `--subjects` | all | Process only these subjects |
| `--max-workers` | 10 | Concurrent workers |
| `--preview` | off | Dry run: show pending subjects and counts, then exit |

## Feature Sets

| Set | Columns | Use case |
|-----|---------|----------|
| `emobase` (default) | ~104 (52 LLDs x mean+std) | Emotion recognition, prosodic analysis |
| `eGeMAPSv02` | 88 | Standard paralinguistic/emotion research |
| `GeMAPSv01b` | 62 | Minimal Geneva set |
| `ComParE_2016` | 6,373 | Full INTERSPEECH ComParE challenge set |

For emobase with functionals level, the script filters to `_amean` and `_stddev` columns only (104 columns from 52 low-level descriptors).

## Feature Levels

- `functionals` (default): One row per audio file. openSMILE computes statistical functionals (mean, std, etc.) over the entire file. This is the standard mode.
- `lld`: One row per analysis frame (typically 10ms windows). Produces per-frame low-level descriptors. Much larger output. Note: the emobase amean/stddev column filter still applies when `--feature-set emobase` is used with `--feature-level lld`.

## Interpretable Scores (emobase only)

Eight scores are mapped from openSMILE functionals columns and placed first in the output, before the raw features:

| Score column | openSMILE source | Unit | Conversion |
|-------------|-----------------|------|------------|
| `loudness_mean` | `pcm_loudness_sma_amean` | dB | `10 * log10(value / 1e-12)` |
| `loudness_std` | `pcm_loudness_sma_stddev` | raw | None |
| `pitch_mean` | `F0_sma_amean` | Hz | None |
| `pitch_std` | `F0_sma_stddev` | Hz | None |
| `loudness_var_mean` | `pcm_zcr_sma_amean` | rate | None (zero-crossing rate) |
| `loudness_var_std` | `pcm_zcr_sma_stddev` | rate | None |
| `talking_duration_mean` | `voicingFinalUnclipped_sma_amean` | 0-1 | None (voicing probability) |
| `talking_duration_std` | `voicingFinalUnclipped_sma_stddev` | 0-1 | None |

Scores are only computed when the emobase feature set is used. Other feature sets skip score computation and output raw features only.

**Note on score naming**: Column names (`loudness_var`, `talking_duration`) are semantic labels chosen for interpretability in downstream analysis. They map to specific openSMILE features (zero-crossing rate, voicing probability) that serve as proxies for the named constructs.

## Output

Checkpoint path: `<output-dir>/checkpoints/<subject>.xlsx`

Output columns (emobase default): `identifier (--file-col) | additional id_cols (if specified) | 8 scores | 104 raw features | ok`.

The `ok` column is `True` if audio was extracted and features computed successfully.

## Audio Extraction

FFmpeg extracts audio as 16 kHz mono PCM WAV to a temporary file. This standardized format ensures consistent openSMILE results regardless of source format or codec.

Supported input formats: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`

## Edge Cases

- **Silent/no-audio files**: openSMILE may produce zero or near-zero values; row saved with `ok=True` but features may not be meaningful
- **Image files passed as input**: FFmpeg fails to extract audio, row saved with `ok=False`
- **Very short audio** (<100ms): May produce unreliable functionals
- **FFmpeg not found**: Script exits with error message
- **Missing opensmile package**: ImportError at startup

## Performance

- Audio extraction is sequential per file (FFmpeg subprocess)
- openSMILE processing uses `--max-workers` threads
- Tip: Set `PYTHONUNBUFFERED=1` for real-time progress output
