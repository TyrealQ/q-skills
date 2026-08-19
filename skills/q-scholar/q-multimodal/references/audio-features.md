# Audio Features — Detailed Reference

Script: `scripts/opensmile/audio_features.py`

Preflights ffmpeg + ffprobe, probes each file for an audio stream (ffprobe), extracts audio via FFmpeg (16 kHz mono PCM WAV), measures RMS/peak/duration from the PCM samples, then runs openSMILE for prosodic and voice quality features. Outputs 8 interpretable scores, full raw features, and stream/signal diagnostics.

## All CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required) | Input file (xlsx, csv, json, parquet, etc.) |
| `--base-dir` | (required) | Base directory for resolving relative file paths |
| `--output-dir` | `output/opensmile` | Checkpoint output directory |
| `--file-col` | `file_path` | Column containing file paths |
| `--group-col` | (auto) | Column to group by subject; default: parent directory of file path |
| `--id-cols` | — | Extra source columns to keep in output; the file column is always retained regardless |
| `--feature-set` | `emobase` | openSMILE feature set (see table below) |
| `--feature-level` | `functionals` | Extraction level: `functionals` (one row per file). Only `functionals` is supported. |
| `--silence-threshold-dbfs` | `-80.0` | RMS at or below this is classified `silent_or_near_silent` |
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

- `functionals` (default): One row per audio file. openSMILE computes statistical functionals (mean, std, etc.) over the entire file. This is the only supported mode.

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
| `talking_duration_mean` | `voiceProb_sma_amean` | 0-1 | None (voicing probability) |
| `talking_duration_std` | `voiceProb_sma_stddev` | 0-1 | None |

Scores are only computed when the emobase feature set is used. Other feature sets skip score computation and output raw features only.

**Note on score naming**: Column names (`loudness_var`, `talking_duration`) are semantic labels chosen for interpretability in downstream analysis. They map to specific openSMILE features (zero-crossing rate, voicing probability) that serve as proxies for the named constructs.

## Output

Checkpoint path: `<output-dir>/checkpoints/<subject>.xlsx`

Output columns (emobase default): `id_cols + file column (always retained) | 8 scores | 104 raw features | diagnostics | ok`.

## Diagnostics and Status

| Column | Meaning |
|--------|---------|
| `audio_stream_present` | nullable boolean: container has an audio stream (ffprobe); missing when undeterminable |
| `audio_signal_ok` | nullable boolean: RMS above `--silence-threshold-dbfs` |
| `audio_status` | `ok`, `silent_or_near_silent`, `no_audio_stream`, `file_not_found`, `unsupported_format`, `probe_error`, `extraction_error`, `feature_error` |
| `audio_rms_dbfs` / `audio_peak_dbfs` | signal level from normalized PCM, floored at -120 dBFS (never -inf) |
| `audio_duration_s` | extracted WAV duration |
| `audio_error` | technical error message; blank for `no_audio_stream` (structural, not an error) |
| `ok` | technical processing success (openSMILE ran) |

`ok` and `audio_signal_ok` answer different questions: a valid silent stream is `ok=True` with `audio_signal_ok=False` (openSMILE still runs); a file with no audio stream is a structural absence — `ok=False`, `audio_status=no_audio_stream` — not a missing feature or extraction failure. Silence is measured from PCM, never inferred from zero-valued openSMILE fields.

## Audio Extraction

FFmpeg extracts audio as 16 kHz mono PCM WAV to a temporary file. All input files — including native `.wav` files — are re-encoded through FFmpeg to ensure consistent 16 kHz mono PCM format regardless of source sample rate, bit depth, or channel count.

Supported input formats: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`

## Edge Cases

- **Silent streams**: classified `silent_or_near_silent` via the PCM RMS threshold; openSMILE still runs, `ok=True`
- **No audio stream**: detected by ffprobe before extraction; `audio_status=no_audio_stream`, `ok=False`, `audio_error` blank
- **Image files passed as input**: `unsupported_format`, `ok=False`
- **Very short audio** (<100ms): May produce unreliable functionals
- **ffmpeg or ffprobe not found**: preflight exits with an error message
- **Missing opensmile package**: ImportError at startup

## Performance

- Audio extraction is sequential per file (FFmpeg subprocess)
- openSMILE processing uses `--max-workers` threads
- Tip: Set `PYTHONUNBUFFERED=1` for real-time progress output
