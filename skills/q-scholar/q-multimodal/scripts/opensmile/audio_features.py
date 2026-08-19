"""
Audio feature extraction using openSMILE.

Preflights ffmpeg + ffprobe, probes each file for an audio stream, extracts
normalized 16 kHz mono PCM WAV, measures RMS/peak/duration from the PCM
samples, then runs openSMILE with the emobase configuration (52 LLDs) at the
Functionals level. Keeps only mean (amean) and std (stddev) per descriptor
= 104 raw features.

Additionally computes 8 interpretable score columns:
  - loudness_mean/std      (dB, Eq. A.1: 10*log10(intensity/I0))
  - pitch_mean/std         (Hz, F0 via ACF+SHS+Viterbi)
  - loudness_var_mean/std  (zero-crossing rate, Eq. A.2)
  - talking_duration_mean/std (voicing probability, Eq. A.3: ACF_max/ACF_0)

Diagnostics per row: audio_stream_present, audio_signal_ok, audio_status,
audio_rms_dbfs, audio_peak_dbfs, audio_duration_s, audio_error, ok.
`ok` means technical success: a silent stream is ok=True with
audio_signal_ok=False; no audio stream is structural — ok=False,
audio_status=no_audio_stream, audio_error blank.
See references/audio-features.md for the full column contract.

Output: id/file columns + 8 scores + 104 raw features + diagnostics.

Generic — no project-specific names. All paths come from CLI args.

Tip: set PYTHONUNBUFFERED=1 or use `python -u` for live progress in
background/piped execution.
"""

import argparse
import math
import os
import shutil
import subprocess
import tempfile
import wave
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from common import read_input, save_excel, derive_subject, merge_checkpoints, source_columns
from tqdm import tqdm

try:
    import opensmile
except ImportError:
    opensmile = None

AUDIO_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wav", ".mp3", ".flac", ".ogg", ".m4a"}

VALID_FEATURE_SETS = {"emobase", "eGeMAPSv02", "GeMAPSv01b", "ComParE_2016"}
VALID_FEATURE_LEVELS = {"functionals"}

# Documented numeric floor for dBFS values: digital silence (all-zero PCM)
# is reported as this floor instead of -inf so the column stays numeric.
DBFS_FLOOR = -120.0

# Default RMS threshold separating usable signal from silent/near-silent.
DEFAULT_SILENCE_THRESHOLD_DBFS = -80.0

# Controlled audio_status vocabulary.
STATUS_OK = "ok"
STATUS_SILENT = "silent_or_near_silent"
STATUS_NO_STREAM = "no_audio_stream"
STATUS_FILE_NOT_FOUND = "file_not_found"
STATUS_UNSUPPORTED = "unsupported_format"
STATUS_PROBE_ERROR = "probe_error"
STATUS_EXTRACTION_ERROR = "extraction_error"
STATUS_FEATURE_ERROR = "feature_error"

DIAG_COLS = [
    "audio_stream_present", "audio_signal_ok", "audio_status",
    "audio_rms_dbfs", "audio_peak_dbfs", "audio_duration_s", "audio_error",
]


def _get_feature_set(name):
    """Resolve openSMILE feature set enum by name."""
    if opensmile is None:
        raise ImportError("opensmile is not installed. Run: pip install opensmile")
    return getattr(opensmile.FeatureSet, name)

# LLD name patterns for the 8 interpretable scores (emobase column names)
SCORE_MAPPINGS = {
    "loudness_mean": "pcm_loudness_sma_amean",
    "loudness_std": "pcm_loudness_sma_stddev",
    "pitch_mean": "F0_sma_amean",
    "pitch_std": "F0_sma_stddev",
    "loudness_var_mean": "pcm_zcr_sma_amean",
    "loudness_var_std": "pcm_zcr_sma_stddev",
    "talking_duration_mean": "voiceProb_sma_amean",
    "talking_duration_std": "voiceProb_sma_stddev",
}

# Reference intensity for dB conversion (Eq. A.1)
I0 = 1e-12


def _to_db(value):
    """Convert raw intensity to dB (Eq. A.1): 10 * log10(value / I0)."""
    if value <= 0:
        return 0.0
    return 10.0 * math.log10(value / I0)


# ---------------------------------------------------------------------------
# Tool preflight, stream probe, audio extraction, PCM measurement
# ---------------------------------------------------------------------------

def preflight_tools():
    """Fail fast when ffmpeg or ffprobe is not on PATH."""
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        raise SystemExit(
            f"Required tool(s) not found on PATH: {', '.join(missing)}. "
            "Both ffmpeg and ffprobe are needed for audio extraction."
        )


def probe_audio_stream(path):
    """Return True if ffprobe reports at least one audio stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "csv=p=0",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr.strip()}")
    return bool(result.stdout.strip())


def extract_audio_wav(video_path, output_path):
    """Extract audio from video to 16kHz mono PCM WAV using FFmpeg."""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        output_path,
        "-loglevel", "error",
        "-y",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed: {result.stderr.strip()}")


def measure_pcm(wav_path):
    """Measure RMS/peak level (dBFS, floored at DBFS_FLOOR) and duration from
    the normalized PCM samples. Preferred over parsing FFmpeg volumedetect."""
    with wave.open(wav_path, "rb") as wf:
        n_frames = wf.getnframes()
        rate = wf.getframerate()
        raw = wf.readframes(n_frames)
    duration_s = n_frames / float(rate) if rate else 0.0
    samples = np.frombuffer(raw, dtype=np.int16)
    if samples.size == 0:
        return DBFS_FLOOR, DBFS_FLOOR, duration_s
    x = samples.astype(np.float64) / 32768.0
    rms = float(np.sqrt(np.mean(np.square(x))))
    peak = float(np.max(np.abs(x)))
    rms_dbfs = 20.0 * math.log10(rms) if rms > 0 else DBFS_FLOOR
    peak_dbfs = 20.0 * math.log10(peak) if peak > 0 else DBFS_FLOOR
    return max(rms_dbfs, DBFS_FLOOR), max(peak_dbfs, DBFS_FLOOR), duration_s


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------

def _result(ok, status, stream=None, signal=None, rms=None, peak=None,
            duration=None, error="", data=None, scores=None):
    """Assemble one file's result. stream/signal use None for 'unknown'."""
    return {
        "ok": ok,
        "audio_status": status,
        "audio_stream_present": stream,
        "audio_signal_ok": signal,
        "audio_rms_dbfs": rms,
        "audio_peak_dbfs": peak,
        "audio_duration_s": duration,
        "error": error,
        "data": data or {},
        "scores": scores or {},
    }


def analyze_audio(idx, row, base_dir, file_col, smile, feature_set_name,
                  silence_threshold_dbfs=DEFAULT_SILENCE_THRESHOLD_DBFS):
    """Extract audio features from one file with stream/signal diagnostics."""
    rel_path = row.get(file_col, "")
    if not rel_path:
        return _result(False, STATUS_FILE_NOT_FOUND, error="empty path")

    ext = Path(str(rel_path)).suffix.lower()
    if ext not in AUDIO_VIDEO_EXTENSIONS:
        return _result(False, STATUS_UNSUPPORTED, error=f"unsupported extension: {ext}")

    abs_path = os.path.join(base_dir, rel_path)
    if not os.path.isfile(abs_path):
        return _result(False, STATUS_FILE_NOT_FOUND, error=f"file not found: {abs_path}")

    try:
        has_stream = probe_audio_stream(abs_path)
    except Exception as e:
        return _result(False, STATUS_PROBE_ERROR, error=str(e))
    if not has_stream:
        # Structural absence, not an error: audio_error stays blank.
        return _result(False, STATUS_NO_STREAM, stream=False, signal=False)

    tmp_wav = None
    try:
        fd, tmp_wav = tempfile.mkstemp(suffix=".wav", prefix="osmile_")
        os.close(fd)
        try:
            extract_audio_wav(abs_path, tmp_wav)
        except Exception as e:
            return _result(False, STATUS_EXTRACTION_ERROR, stream=True, error=str(e))

        try:
            rms_dbfs, peak_dbfs, duration_s = measure_pcm(tmp_wav)
        except Exception as e:
            return _result(False, STATUS_EXTRACTION_ERROR, stream=True, error=str(e))

        signal_ok = rms_dbfs > silence_threshold_dbfs
        status = STATUS_OK if signal_ok else STATUS_SILENT

        # openSMILE still runs on a valid silent stream.
        try:
            features_df = smile.process_file(tmp_wav)
            if features_df.empty:
                raise RuntimeError("openSMILE returned empty")
        except Exception as e:
            return _result(False, STATUS_FEATURE_ERROR, stream=True,
                           signal=signal_ok, rms=rms_dbfs, peak=peak_dbfs,
                           duration=duration_s, error=str(e))

        # Get all columns — filter to amean and stddev only for emobase
        all_cols = features_df.columns.tolist()
        if feature_set_name == "emobase":
            keep_cols = [c for c in all_cols if c.endswith("_amean") or c.endswith("_stddev")]
        else:
            keep_cols = all_cols

        raw_data = {}
        for col in keep_cols:
            raw_data[col] = float(features_df.iloc[0][col])

        # Compute interpretable scores
        scores = {}
        for score_name, source_col in SCORE_MAPPINGS.items():
            if source_col in raw_data:
                val = raw_data[source_col]
                # Apply dB conversion for loudness mean only (Eq. A.1)
                # loudness_std stays in raw units (std of dB values is not meaningful via this formula)
                if score_name == "loudness_mean":
                    scores[score_name] = _to_db(val)
                else:
                    scores[score_name] = val
            else:
                scores[score_name] = np.nan

        return _result(True, status, stream=True, signal=signal_ok,
                       rms=rms_dbfs, peak=peak_dbfs, duration=duration_s,
                       data=raw_data, scores=scores)
    except Exception as e:
        return _result(False, STATUS_FEATURE_ERROR, stream=True, error=str(e))
    finally:
        if tmp_wav and os.path.isfile(tmp_wav):
            os.remove(tmp_wav)


# ---------------------------------------------------------------------------
# DataFrame construction and subject processing
# ---------------------------------------------------------------------------

def build_output_df(rows, results, id_cols=None, file_col="file_path"):
    """Merge source rows with scores + raw features + diagnostics."""
    source_df = pd.DataFrame(rows)
    keep = [c for c in source_columns(id_cols, file_col) if c in source_df.columns]
    source_df = source_df[keep]

    # Collect all raw column names from successful results
    raw_cols = set()
    for r in results:
        raw_cols.update(r.get("data", {}).keys())
    raw_cols = sorted(raw_cols)

    score_names = list(SCORE_MAPPINGS.keys())

    out_rows = []
    for r in results:
        row = {}
        for s in score_names:
            row[s] = r.get("scores", {}).get(s, np.nan)
        for c in raw_cols:
            row[c] = r.get("data", {}).get(c, np.nan)
        row["audio_stream_present"] = r.get("audio_stream_present")
        row["audio_signal_ok"] = r.get("audio_signal_ok")
        row["audio_status"] = r.get("audio_status")
        row["audio_rms_dbfs"] = r.get("audio_rms_dbfs")
        row["audio_peak_dbfs"] = r.get("audio_peak_dbfs")
        row["audio_duration_s"] = r.get("audio_duration_s")
        row["audio_error"] = r.get("error", "")
        row["ok"] = r["ok"]
        out_rows.append(row)

    feature_df = pd.DataFrame(out_rows)
    # Nullable booleans: unknown stays missing on technical failures.
    for col in ("audio_stream_present", "audio_signal_ok"):
        feature_df[col] = feature_df[col].astype("boolean")
    out = pd.concat([source_df.reset_index(drop=True), feature_df.reset_index(drop=True)], axis=1)
    return out


def process_subject(name, subject_df, base_dir, file_col, max_workers,
                    output_dir, smile, feature_set_name, id_cols=None,
                    silence_threshold_dbfs=DEFAULT_SILENCE_THRESHOLD_DBFS):
    """Process all audio/video files for one subject, save checkpoint."""
    rows = subject_df.to_dict("records")
    results = [None] * len(rows)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(analyze_audio, i, row, base_dir, file_col, smile,
                        feature_set_name, silence_threshold_dbfs): i
            for i, row in enumerate(rows)
        }
        with tqdm(total=len(rows), desc=f"  {name}", position=1, leave=False) as file_bar:
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = _result(False, STATUS_FEATURE_ERROR, error=str(e))
                file_bar.update(1)

    out_df = build_output_df(rows, results, id_cols, file_col=file_col)
    ckpt_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    out_path = os.path.join(ckpt_dir, f"{name}.xlsx")
    save_excel(out_df, out_path)

    ok_count = sum(1 for r in results if r["ok"])
    fail_count = len(results) - ok_count
    return {"name": name, "total": len(rows), "ok": ok_count, "fail": fail_count, "path": out_path}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _run_merge(args):
    ckpt_dir = os.path.join(args.output_dir, "checkpoints")
    out_path = os.path.join(args.output_dir, "_audio_features.xlsx")
    # Merge key: id columns + file column — never an id alone, so
    # multi-asset posts keep one row per file.
    dedup = source_columns(args.id_cols, args.file_col)
    _, stats = merge_checkpoints(ckpt_dir, out_path, file_col=args.file_col,
                                 dedup_cols=dedup)
    if stats["files"]:
        print(f"Merged {stats['files']} checkpoints -> {out_path} ({stats['rows']} rows)", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Extract audio features using openSMILE")
    parser.add_argument("--input", default=None, help="Input xlsx file")
    parser.add_argument("--base-dir", default=None, help="Base directory for resolving relative file paths")
    parser.add_argument("--output-dir", default="output/opensmile", help="Output directory")
    parser.add_argument("--merge", action="store_true", help="Merge all checkpoints into a single file")
    parser.add_argument("--group-col", default=None, help="Column to group rows by subject")
    parser.add_argument("--file-col", default="file_path", help="Column containing file paths")
    parser.add_argument("--id-cols", nargs="*", default=None,
                        help="Source columns to keep in output (the file column is always retained)")
    parser.add_argument("--feature-set", default="emobase",
                        help="openSMILE feature set: emobase (default), eGeMAPSv02, GeMAPSv01b, ComParE_2016")
    parser.add_argument("--feature-level", default="functionals",
                        help="Extraction level: functionals (one row per file). Only functionals is supported.")
    parser.add_argument("--silence-threshold-dbfs", type=float,
                        default=DEFAULT_SILENCE_THRESHOLD_DBFS,
                        help="RMS dBFS at or below which a stream is classified "
                             f"silent_or_near_silent (default: {DEFAULT_SILENCE_THRESHOLD_DBFS})")
    parser.add_argument("--subjects", nargs="*", default=None, help="Process only these subjects")
    parser.add_argument("--max-workers", type=int, default=10, help="Number of concurrent workers")
    parser.add_argument("--preview", action="store_true", help="Dry run: show pending subjects and exit")
    args = parser.parse_args()

    if not args.merge and not args.input:
        parser.error("--input is required unless using --merge standalone")
    if args.input and not args.base_dir:
        parser.error("--base-dir is required when --input is specified")

    if args.merge and not args.input:
        _run_merge(args)
        return

    if opensmile is None:
        print("Error: opensmile package not installed. Run: pip install opensmile", flush=True)
        return

    preflight_tools()

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", flush=True)
        return

    if args.feature_set not in VALID_FEATURE_SETS:
        print(f"Unknown feature set: {args.feature_set}. Available: {sorted(VALID_FEATURE_SETS)}", flush=True)
        return

    if args.feature_level not in VALID_FEATURE_LEVELS:
        print(f"Unknown feature level: {args.feature_level}. Available: {sorted(VALID_FEATURE_LEVELS)}", flush=True)
        return

    # Initialize openSMILE
    smile = opensmile.Smile(
        feature_set=_get_feature_set(args.feature_set),
        feature_level=opensmile.FeatureLevel.Functionals,
    )
    print(f"openSMILE: {args.feature_set}, level={args.feature_level}", flush=True)
    print(f"Silence threshold: {args.silence_threshold_dbfs} dBFS", flush=True)

    # id/file columns as strings from the read point (never through float)
    df = read_input(args.input, str_cols=source_columns(args.id_cols, args.file_col))
    print(f"Loaded {len(df)} rows from {args.input}", flush=True)

    if args.file_col not in df.columns:
        print(f"Column '{args.file_col}' not found. Available: {list(df.columns)}", flush=True)
        return

    # Filter to audio/video rows only
    df = df[df[args.file_col].apply(
        lambda x: Path(str(x)).suffix.lower() in AUDIO_VIDEO_EXTENSIONS if pd.notna(x) else False
    )].copy()
    print(f"  {len(df)} audio/video rows after filtering", flush=True)

    # Group by subject
    df["_subject"] = df.apply(lambda r: derive_subject(r, args.file_col, args.group_col), axis=1)
    groups = dict(list(df.groupby("_subject")))

    if args.subjects:
        groups = {k: v for k, v in groups.items() if k in args.subjects}

    # Skip existing checkpoints
    ckpt_dir = os.path.join(args.output_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    pending = {}
    for name, group_df in sorted(groups.items()):
        checkpoint = os.path.join(ckpt_dir, f"{name}.xlsx")
        if os.path.isfile(checkpoint):
            continue
        pending[name] = group_df

    print(f"  {len(pending)} subjects pending ({len(groups) - len(pending)} already done)", flush=True)

    if args.preview or not pending:
        print(flush=True)
        for name, group_df in sorted(pending.items()):
            print(f"  {name}: {len(group_df)} files", flush=True)
        return

    # Process
    summaries = []
    for name in tqdm(sorted(pending.keys()), desc="Subjects", position=0):
        group_df = pending[name].drop(columns=["_subject"])
        summary = process_subject(
            name, group_df, args.base_dir, args.file_col, args.max_workers,
            args.output_dir, smile, args.feature_set, args.id_cols,
            args.silence_threshold_dbfs,
        )
        summaries.append(summary)
        tqdm.write(f"  {summary['name']}: {summary['ok']}/{summary['total']} ok -> {summary['path']}")

    print(f"\nDone: {len(summaries)} subjects processed", flush=True)
    total_ok = sum(s["ok"] for s in summaries)
    total_fail = sum(s["fail"] for s in summaries)
    print(f"  Total: {total_ok} ok, {total_fail} failed", flush=True)

    if args.merge:
        _run_merge(args)


if __name__ == "__main__":
    main()
