"""
Music feature extraction using librosa.

Music-native counterpart to the openSMILE pipeline (which is speech/prosody
oriented). Loads each audio file mono at 22.05 kHz (MIR standard) and computes
one row of features per clip. Output has two tiers:

  Tier 1 - interpretable scores (one scalar per clip):
    - tempo_bpm           global tempo (beat_track)
    - onset_rate          onsets per second (rhythmic density)
    - beat_strength       pulse clarity (normalized onset-autocorrelation peak)
    - rms_energy          mean RMS (energy/loudness proxy)
    - dynamic_range       std of RMS across frames
    - spectral_centroid_hz mean centroid (brightness)
    - spectral_flatness   mean flatness (tonal vs noise-like)
    - zcr                 mean zero-crossing rate (percussiveness)
    - harmonic_ratio      harmonic energy / total energy (HPSS)
    - key / mode / mode_confidence  Krumhansl-Schmuckler key estimate; mode is
                          the major/minor valence proxy
    - duration_s          analyzed clip length

  Tier 2 - raw block (mean + std of each frame-wise descriptor):
    chroma (12), mfcc (13), spectral_contrast (7), tonnetz (6), and
    spectral_centroid / bandwidth / rolloff / flatness / zcr / rms /
    onset_strength.

--feature-set: curated (default, both tiers) | scores (tier 1 only) |
full (curated + delta/delta-delta MFCC, 20 MFCCs, tempogram-ratio).

Generic - no project-specific names. All paths come from CLI args.

Tip: set PYTHONUNBUFFERED=1 or use `python -u` for live progress in
background/piped execution.
"""

import argparse
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from common import read_input, save_excel, derive_subject, merge_checkpoints
from tqdm import tqdm

try:
    import librosa
except ImportError:
    librosa = None

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac",
                    ".mp4", ".mov", ".mkv", ".webm"}

VALID_FEATURE_SETS = {"curated", "scores", "full"}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Krumhansl-Kessler key profiles (major, minor): perceptual weights for the 12
# pitch classes relative to the tonic. Krumhansl & Kessler (1982).
_KK_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                      2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_KK_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                      2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Tier-1 interpretable score columns, in output order
SCORE_COLS = [
    "tempo_bpm", "onset_rate", "beat_strength", "rms_energy", "dynamic_range",
    "spectral_centroid_hz", "spectral_flatness", "zcr", "harmonic_ratio",
    "key", "mode", "mode_confidence", "duration_s",
]


# ---------------------------------------------------------------------------
# Key / mode estimation
# ---------------------------------------------------------------------------

def estimate_key_mode(chroma_mean):
    """Krumhansl-Schmuckler: correlate mean chroma against the 24 rotated
    major/minor key profiles. Returns (key_name, mode, confidence)."""
    chroma_mean = chroma_mean - chroma_mean.mean()
    norm = np.linalg.norm(chroma_mean)
    if norm == 0:
        return "", "", float("nan")

    best = (-2.0, 0, "major")
    for prof, mode in ((_KK_MAJOR, "major"), (_KK_MINOR, "minor")):
        p = prof - prof.mean()
        p_norm = np.linalg.norm(p)
        for shift in range(12):
            # correlate against the profile rotated to each tonic
            corr = float(np.dot(chroma_mean, np.roll(p, shift)) / (norm * p_norm))
            if corr > best[0]:
                best = (corr, shift, mode)
    return NOTE_NAMES[best[1]], best[2], best[0]


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------

def _mean_std(name, mat, out):
    """Write mean+std of a (n_features, n_frames) matrix as <name>[_i]_mean/_std."""
    mat = np.atleast_2d(mat)
    multi = mat.shape[0] > 1
    for i in range(mat.shape[0]):
        stem = f"{name}_{i}" if multi else name
        out[f"{stem}_mean"] = float(np.mean(mat[i]))
        out[f"{stem}_std"] = float(np.std(mat[i]))


def analyze_music(abs_path, sr, feature_set):
    """Extract music features from one audio file. Returns {ok, scores, raw, error}."""
    try:
        y, sr = librosa.load(abs_path, sr=sr, mono=True)
    except Exception as e:
        return {"ok": False, "scores": {}, "raw": {}, "error": f"load failed: {e}"}

    if y.size == 0 or float(np.max(np.abs(y))) < 1e-5:
        return {"ok": False, "scores": {}, "raw": {}, "error": "empty or silent"}
    if y.size < sr * 0.1:  # < 100 ms: functionals are unreliable
        return {"ok": False, "scores": {}, "raw": {}, "error": "too short (<100ms)"}

    try:
        duration = float(len(y) / sr)

        # Frame-wise spectral / energy descriptors
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        flatness = librosa.feature.spectral_flatness(y=y)
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)  # 7 sub-bands
        zcr = librosa.feature.zero_crossing_rate(y=y)
        rms = librosa.feature.rms(y=y)

        # Timbre / tonal
        n_mfcc = 20 if feature_set == "full" else 13
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)  # 12 pitch classes
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)    # 6-dim tonal centroid

        # Rhythm
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)[0]
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        onset_rate = float(len(onsets) / duration) if duration else 0.0
        # pulse clarity = strongest onset-envelope autocorrelation peak / lag-0
        ac = librosa.autocorrelate(onset_env)
        beat_strength = float(ac[1:].max() / ac[0]) if ac.size > 1 and ac[0] > 0 else 0.0

        # Harmonic balance: harmonic energy / total energy (HPSS)
        y_harm, y_perc = librosa.effects.hpss(y)
        total_e = float(np.sum(y_harm ** 2) + np.sum(y_perc ** 2))
        harmonic_ratio = float(np.sum(y_harm ** 2) / total_e) if total_e > 0 else float("nan")

        key, mode, mode_conf = estimate_key_mode(chroma.mean(axis=1))

        scores = {
            "tempo_bpm": float(np.atleast_1d(tempo)[0]),
            "onset_rate": onset_rate,
            "beat_strength": beat_strength,
            "rms_energy": float(np.mean(rms)),
            "dynamic_range": float(np.std(rms)),
            "spectral_centroid_hz": float(np.mean(centroid)),
            "spectral_flatness": float(np.mean(flatness)),
            "zcr": float(np.mean(zcr)),
            "harmonic_ratio": harmonic_ratio,
            "key": key,
            "mode": mode,
            "mode_confidence": mode_conf,
            "duration_s": duration,
        }
        if feature_set == "scores":
            return {"ok": True, "scores": scores, "raw": {}, "error": ""}

        raw = {}
        _mean_std("chroma", chroma, raw)
        _mean_std("mfcc", mfcc, raw)
        _mean_std("spectral_contrast", contrast, raw)
        _mean_std("tonnetz", tonnetz, raw)
        _mean_std("spectral_centroid", centroid, raw)
        _mean_std("spectral_bandwidth", bandwidth, raw)
        _mean_std("spectral_rolloff", rolloff, raw)
        _mean_std("spectral_flatness", flatness, raw)
        _mean_std("zcr", zcr, raw)
        _mean_std("rms", rms, raw)
        _mean_std("onset_strength", onset_env, raw)

        if feature_set == "full":
            _mean_std("mfcc_delta", librosa.feature.delta(mfcc), raw)
            _mean_std("mfcc_delta2", librosa.feature.delta(mfcc, order=2), raw)
            # tempogram-ratio: rhythmic self-similarity across tempo lags
            tgr = librosa.feature.tempogram_ratio(onset_envelope=onset_env, sr=sr)
            _mean_std("tempogram_ratio", tgr, raw)

        return {"ok": True, "scores": scores, "raw": raw, "error": ""}
    except Exception as e:
        return {"ok": False, "scores": {}, "raw": {}, "error": str(e)}


def _worker(args):
    """Top-level wrapper so ProcessPoolExecutor can pickle the call."""
    idx, abs_path, sr, feature_set = args
    return idx, analyze_music(abs_path, sr, feature_set)


# ---------------------------------------------------------------------------
# DataFrame construction and subject processing
# ---------------------------------------------------------------------------

def build_output_df(rows, results, id_cols=None, file_col="file_path"):
    """Merge source id columns with tier-1 scores + tier-2 raw features."""
    source_df = pd.DataFrame(rows)
    keep = [c for c in (id_cols or [file_col]) if c in source_df.columns]
    source_df = source_df[keep]

    raw_cols = sorted({c for r in results for c in r.get("raw", {})})

    out_rows = []
    for r in results:
        row = {s: r.get("scores", {}).get(s, np.nan) for s in SCORE_COLS}
        for c in raw_cols:
            row[c] = r.get("raw", {}).get(c, np.nan)
        row["ok"] = r["ok"]
        out_rows.append(row)

    feature_df = pd.DataFrame(out_rows)
    return pd.concat([source_df.reset_index(drop=True),
                      feature_df.reset_index(drop=True)], axis=1)


def process_subject(name, subject_df, base_dir, file_col, max_workers,
                    output_dir, sr, feature_set, id_cols=None):
    """Process all audio files for one subject, save checkpoint.

    Uses ProcessPoolExecutor: librosa is CPU-bound (NumPy/FFT), so processes
    parallelize better than threads here (unlike the openSMILE pipeline, where
    work happens in a separate native binary)."""
    rows = subject_df.to_dict("records")
    results = [None] * len(rows)

    tasks = []
    for i, row in enumerate(rows):
        abs_path = os.path.join(base_dir, str(row.get(file_col, "")))
        tasks.append((i, abs_path, sr, feature_set))

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(_worker, t) for t in tasks]
        with tqdm(total=len(rows), desc=f"  {name}", position=1, leave=False) as bar:
            for future in as_completed(futures):
                idx, res = future.result()
                results[idx] = res
                bar.update(1)

    out_df = build_output_df(rows, results, id_cols, file_col=file_col)
    ckpt_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    out_path = os.path.join(ckpt_dir, f"{name}.xlsx")
    save_excel(out_df, out_path)

    ok_count = sum(1 for r in results if r["ok"])
    return {"name": name, "total": len(rows), "ok": ok_count,
            "fail": len(results) - ok_count, "path": out_path}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _run_merge(args):
    ckpt_dir = os.path.join(args.output_dir, "checkpoints")
    out_path = os.path.join(args.output_dir, "_music_features.xlsx")
    _, stats = merge_checkpoints(ckpt_dir, out_path, file_col=args.file_col)
    if stats["files"]:
        print(f"Merged {stats['files']} checkpoints -> {out_path} ({stats['rows']} rows)", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Extract music features using librosa")
    parser.add_argument("--input", default=None, help="Input file (xlsx, csv, json, parquet)")
    parser.add_argument("--base-dir", default=None, help="Base directory for resolving relative file paths")
    parser.add_argument("--output-dir", default="output/librosa", help="Output directory")
    parser.add_argument("--merge", action="store_true", help="Merge all checkpoints into a single file")
    parser.add_argument("--group-col", default=None, help="Column to group rows by subject")
    parser.add_argument("--file-col", default="file_path", help="Column containing file paths")
    parser.add_argument("--id-cols", nargs="*", default=None, help="Source columns to keep in output (default: file column only)")
    parser.add_argument("--feature-set", default="curated",
                        help="curated (default) | scores (tier-1 only) | full (adds delta MFCC, 20 MFCC, tempogram-ratio)")
    parser.add_argument("--sr", type=int, default=22050, help="Target load sample rate (mono)")
    parser.add_argument("--max-workers", type=int, default=8, help="Number of concurrent worker processes")
    parser.add_argument("--limit", type=int, default=0, help="Smoke-test: only first N rows")
    parser.add_argument("--subjects", nargs="*", default=None, help="Process only these subjects")
    parser.add_argument("--preview", action="store_true", help="Dry run: show pending subjects and exit")
    args = parser.parse_args()

    if not args.merge and not args.input:
        parser.error("--input is required unless using --merge standalone")
    if args.input and not args.base_dir:
        parser.error("--base-dir is required when --input is specified")
    if args.feature_set not in VALID_FEATURE_SETS:
        parser.error(f"Unknown feature set: {args.feature_set}. Available: {sorted(VALID_FEATURE_SETS)}")

    if args.merge and not args.input:
        _run_merge(args)
        return

    if librosa is None:
        print("Error: librosa not installed. Run: pip install librosa", flush=True)
        return
    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", flush=True)
        return

    df = read_input(args.input)
    print(f"Loaded {len(df)} rows from {args.input}", flush=True)

    if args.file_col not in df.columns:
        print(f"Column '{args.file_col}' not found. Available: {list(df.columns)}", flush=True)
        return

    # Filter to audio rows only
    df = df[df[args.file_col].apply(
        lambda x: Path(str(x)).suffix.lower() in AUDIO_EXTENSIONS if pd.notna(x) else False
    )].copy()
    if args.limit:
        df = df.head(args.limit)
    print(f"  {len(df)} audio rows after filtering", flush=True)

    # Group by subject (default: parent directory of the file path)
    df["_subject"] = df.apply(lambda r: derive_subject(r, args.file_col, args.group_col), axis=1)
    groups = dict(list(df.groupby("_subject")))
    if args.subjects:
        groups = {k: v for k, v in groups.items() if k in args.subjects}

    # Skip existing checkpoints (resume-safe; Ctrl-C safe)
    ckpt_dir = os.path.join(args.output_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    pending = {name: g for name, g in sorted(groups.items())
               if not os.path.isfile(os.path.join(ckpt_dir, f"{name}.xlsx"))}
    print(f"  {len(pending)} subjects pending ({len(groups) - len(pending)} already done)", flush=True)

    if args.preview or not pending:
        for name, g in sorted(pending.items()):
            print(f"  {name}: {len(g)} files", flush=True)
        return

    summaries = []
    for name in tqdm(sorted(pending.keys()), desc="Subjects", position=0):
        group_df = pending[name].drop(columns=["_subject"])
        summary = process_subject(
            name, group_df, args.base_dir, args.file_col, args.max_workers,
            args.output_dir, args.sr, args.feature_set, args.id_cols,
        )
        summaries.append(summary)
        tqdm.write(f"  {summary['name']}: {summary['ok']}/{summary['total']} ok -> {summary['path']}")

    total_ok = sum(s["ok"] for s in summaries)
    total_fail = sum(s["fail"] for s in summaries)
    print(f"\nDone: {len(summaries)} subjects, {total_ok} ok, {total_fail} failed", flush=True)

    if args.merge:
        _run_merge(args)


if __name__ == "__main__":
    main()
