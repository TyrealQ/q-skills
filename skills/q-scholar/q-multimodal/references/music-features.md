# Music Features — Detailed Reference

Script: `scripts/librosa/music_features.py`

Music-native counterpart to the openSMILE audio pipeline (which is speech/prosody oriented). Loads each audio/video file mono at 22.05 kHz (MIR standard) with librosa and computes one row of features per clip. Output has two tiers: interpretable tonal/rhythmic scores plus a raw block of spectral, tonal, and timbre descriptors. Reuses the shared `common.py` helpers and per-subject checkpoints, so it resumes safely and merges like the other local pipelines.

## All CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required unless `--merge`) | Input file (xlsx, csv, json, parquet) |
| `--base-dir` | (required with `--input`) | Base directory for resolving relative file paths |
| `--output-dir` | `output/librosa` | Checkpoint output directory |
| `--merge` | off | Merge all checkpoints into a single `_music_features.xlsx` |
| `--group-col` | (auto) | Column to group by subject; default: parent directory of file path |
| `--file-col` | `file_path` | Column containing file paths |
| `--id-cols` | file column only | Source columns to keep in output (default: file column only) |
| `--feature-set` | `curated` | `curated` \| `scores` \| `full` (see table below) |
| `--sr` | `22050` | Target load sample rate (mono) |
| `--max-workers` | `8` | Concurrent worker **processes** |
| `--limit` | `0` | Smoke-test: process only the first N rows |
| `--subjects` | all | Process only these subjects |
| `--preview` | off | Dry run: show pending subjects and counts, then exit |

## Feature Sets

The `--feature-set` flag selects how much is computed and written:

| Set | Output | Use case |
|-----|--------|----------|
| `curated` (default) | 13 tier-1 scores **and** the tier-2 raw block | General music analysis |
| `scores` | 13 tier-1 scores only (no raw block) | Compact, interpretable summary |
| `full` | `curated` plus delta / delta-delta MFCC, 20 MFCCs (instead of 13), and tempogram-ratio | Maximal timbre/rhythm detail |

## Tier-1 Interpretable Scores

Thirteen scores, one scalar per clip, placed first in the output (before the raw block). Computed for every feature set.

| Score column | Meaning | Unit / range |
|-------------|---------|--------------|
| `tempo_bpm` | Global tempo (`librosa.beat.beat_track`) | BPM |
| `onset_rate` | Onsets per second (rhythmic density) | onsets/sec |
| `beat_strength` | Pulse clarity: strongest onset-envelope autocorrelation peak ÷ lag-0 | 0–1 |
| `rms_energy` | Mean RMS amplitude (energy/loudness proxy) | RMS |
| `dynamic_range` | Std of RMS across frames | RMS |
| `spectral_centroid_hz` | Mean spectral centroid (brightness) | Hz |
| `spectral_flatness` | Mean spectral flatness (tonal vs noise-like) | 0–1 |
| `zcr` | Mean zero-crossing rate (percussiveness/noisiness) | rate |
| `harmonic_ratio` | Harmonic energy ÷ total energy via HPSS | 0–1 |
| `key` | Estimated tonic pitch class (Krumhansl–Schmuckler) | `C`…`B` |
| `mode` | Major/minor (valence proxy) | `major` / `minor` |
| `mode_confidence` | Correlation of the best-matching key profile | -1…1 |
| `duration_s` | Analyzed clip length | seconds |

Key and mode use the Krumhansl–Schmuckler algorithm: the mean chroma vector is correlated against the 24 rotated Krumhansl–Kessler (1982) major/minor key profiles; the best-correlating tonic and mode are returned with that correlation as `mode_confidence`.

## Tier-2 Raw Block

Written for `curated` and `full` (omitted for `scores`). Each frame-wise descriptor is summarized as its mean and std over frames. Single-band descriptors are emitted as `<name>_mean` / `<name>_std`; multi-band descriptors are indexed `<name>_<i>_mean` / `<name>_<i>_std`.

| Prefix | Count | Index meaning |
|--------|-------|---------------|
| `chroma_0..11` | 12 | Pitch-class energies (`chroma_cqt`); index = pitch class in order C, C#, D, D#, E, F, F#, G, G#, A, A#, B |
| `mfcc_0..12` | 13 | MFCC timbre coefficients (`curated`/`scores`). With `full`: `mfcc_0..19` (20 coefficients) |
| `spectral_contrast_0..6` | 7 | Spectral contrast per sub-band |
| `tonnetz_0..5` | 6 | Tonal-centroid dimensions (fifths / minor-thirds / major-thirds axes) |

Single-band descriptors (no index): `spectral_centroid`, `spectral_bandwidth`, `spectral_rolloff`, `spectral_flatness`, `zcr`, `rms`, `onset_strength` — each as `<name>_mean` / `<name>_std`.

The `full` set adds delta and delta-delta of the 20 MFCCs (`mfcc_delta_0..19`, `mfcc_delta2_0..19`) and tempogram-ratio bins (`tempogram_ratio_*`, rhythmic self-similarity across tempo lags), all as `_mean` / `_std` pairs.

**Note on overlapping names**: the tier-1 scores `zcr`, `spectral_flatness`, `spectral_centroid_hz`, `rms_energy`, and `dynamic_range` are distinct columns from their tier-2 `*_mean` / `*_std` counterparts (e.g., tier-1 `zcr` vs tier-2 `zcr_mean` / `zcr_std`). Tier-1 values are clip-level summaries chosen for interpretability; tier-2 values are the raw frame-wise mean/std.

## Output

Checkpoint path: `<output-dir>/checkpoints/<subject>.xlsx` (one file per subject; existing checkpoints are skipped on rerun, so the pipeline is resume-safe and Ctrl-C safe).

Output column order: `identifier (--file-col) | additional id_cols (if specified) | 13 scores | raw features (curated/full only) | ok`.

The `ok` column is `True` when the file loaded and features were computed successfully; `False` rows carry blank/`NaN` features.

`--merge` (with or without `--input`) consolidates all per-subject checkpoints into `<output-dir>/_music_features.xlsx`, deduplicating on `--file-col`.

## Audio Loading

`librosa.load(path, sr=--sr, mono=True)` loads and resamples every file to mono at the target sample rate (default 22.05 kHz). Uncompressed formats (`.wav`, `.flac`, `.ogg`) are read via soundfile; compressed and video containers (`.mp3`, `.m4a`, `.aac`, `.mp4`, `.mov`, `.mkv`, `.webm`) fall back to audioread, which requires `ffmpeg` on PATH.

Supported input extensions (`AUDIO_EXTENSIONS`): `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`, `.aac`, `.mp4`, `.mov`, `.mkv`, `.webm`. Rows whose file path has any other extension are filtered out before processing.

## Edge Cases

- **Load failure** (corrupt file, missing codec): row saved with `ok=False` and a `load failed` error.
- **Empty or silent** (`max|y| < 1e-5`): row saved with `ok=False` ("empty or silent").
- **Very short clip** (< 100 ms): row saved with `ok=False` ("too short"); functionals are unreliable below this length.
- **Silent/degenerate chroma**: `key` and `mode` are returned empty with `NaN` `mode_confidence`.
- **Missing `librosa` package**: the script prints an install hint (`pip install librosa`) and exits before processing.

## Performance

- Parallelism uses `ProcessPoolExecutor`: librosa is CPU-bound (NumPy/FFT), so worker processes scale better than threads here — unlike the openSMILE pipeline, where work happens in a separate native binary.
- `--max-workers` defaults to 8 worker processes.
- Use `--limit N` for a quick smoke test on the first N rows.
- Tip: set `PYTHONUNBUFFERED=1` or run with `python -u` for live progress in background/piped execution.
