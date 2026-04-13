"""
Audio feature extraction using openSMILE.

Extracts audio from video/audio files via FFmpeg, then runs openSMILE
with the emobase configuration (52 LLDs) at the Functionals level.
Keeps only mean (amean) and std (stddev) per descriptor = 104 raw features.

Additionally computes 8 interpretable score columns:
  - loudness_mean/std      (dB, Eq. A.1: 10*log10(intensity/I0))
  - pitch_mean/std         (Hz, F0 via ACF+SHS+Viterbi)
  - loudness_var_mean/std  (zero-crossing rate, Eq. A.2)
  - talking_duration_mean/std (voicing probability, Eq. A.3: ACF_max/ACF_0)

Output: file_path + 8 scores + 104 raw features + ok = 114 columns.

Generic — no project-specific names. All paths come from CLI args.

Tip: set PYTHONUNBUFFERED=1 or use `python -u` for live progress in
background/piped execution.
"""

import argparse
import math
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from common import read_input, save_excel, derive_subject, merge_checkpoints
from tqdm import tqdm

try:
    import opensmile
except ImportError:
    opensmile = None

AUDIO_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wav", ".mp3", ".flac", ".ogg", ".m4a"}

VALID_FEATURE_SETS = {"emobase", "eGeMAPSv02", "GeMAPSv01b", "ComParE_2016"}
VALID_FEATURE_LEVELS = {"functionals", "lld"}


def _get_feature_set(name):
    """Resolve openSMILE feature set enum by name."""
    if opensmile is None:
        raise ImportError("opensmile is not installed. Run: pip install opensmile")
    return getattr(opensmile.FeatureSet, name)

# LLD name patterns for the 4 interpretable scores (emobase column names)
SCORE_MAPPINGS = {
    "loudness_mean": "pcm_loudness_sma_amean",
    "loudness_std": "pcm_loudness_sma_stddev",
    "pitch_mean": "F0_sma_amean",
    "pitch_std": "F0_sma_stddev",
    "loudness_var_mean": "pcm_zcr_sma_amean",
    "loudness_var_std": "pcm_zcr_sma_stddev",
    "talking_duration_mean": "voicingFinalUnclipped_sma_amean",
    "talking_duration_std": "voicingFinalUnclipped_sma_stddev",
}

# Reference intensity for dB conversion (Eq. A.1)
I0 = 1e-12


def _to_db(value):
    """Convert raw intensity to dB (Eq. A.1): 10 * log10(value / I0)."""
    if value <= 0:
        return 0.0
    return 10.0 * math.log10(value / I0)


# ---------------------------------------------------------------------------
# Audio extraction
# ---------------------------------------------------------------------------

def extract_audio_wav(video_path, output_path):
    """Extract audio from video to 16kHz mono WAV using FFmpeg."""
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


# ---------------------------------------------------------------------------
# Per-file processing
# ---------------------------------------------------------------------------

def analyze_audio(idx, row, base_dir, file_col, smile, feature_set_name):
    """Extract audio features from one file. Returns {ok, data, scores, raw_cols, error}."""
    rel_path = row.get(file_col, "")
    if not rel_path:
        return {"ok": False, "data": {}, "error": "empty path"}

    ext = Path(str(rel_path)).suffix.lower()
    if ext not in AUDIO_VIDEO_EXTENSIONS:
        return {"ok": False, "data": {}, "error": f"skipped: {ext}"}

    abs_path = os.path.join(base_dir, rel_path)
    if not os.path.isfile(abs_path):
        return {"ok": False, "data": {}, "error": f"file not found: {abs_path}"}

    tmp_wav = None
    try:
        # If not already wav, extract audio
        if ext != ".wav":
            fd, tmp_wav = tempfile.mkstemp(suffix=".wav", prefix="osmile_")
            os.close(fd)
            extract_audio_wav(abs_path, tmp_wav)
            wav_path = tmp_wav
        else:
            wav_path = abs_path

        # Run openSMILE
        features_df = smile.process_file(wav_path)

        if features_df.empty:
            return {"ok": False, "data": {}, "error": "openSMILE returned empty"}

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
                scores[score_name] = ""

        return {"ok": True, "data": raw_data, "scores": scores, "error": ""}
    except Exception as e:
        return {"ok": False, "data": {}, "scores": {}, "error": str(e)}
    finally:
        if tmp_wav and os.path.isfile(tmp_wav):
            os.remove(tmp_wav)


# ---------------------------------------------------------------------------
# DataFrame construction and subject processing
# ---------------------------------------------------------------------------

def build_output_df(rows, results, id_cols=None):
    """Merge source rows with scores + raw features."""
    source_df = pd.DataFrame(rows)
    if id_cols:
        keep = [c for c in id_cols if c in source_df.columns]
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
            row[s] = r.get("scores", {}).get(s, "")
        for c in raw_cols:
            row[c] = r.get("data", {}).get(c, "")
        row["ok"] = r["ok"]
        out_rows.append(row)

    feature_df = pd.DataFrame(out_rows)
    out = pd.concat([source_df.reset_index(drop=True), feature_df.reset_index(drop=True)], axis=1)
    return out


def process_subject(name, subject_df, base_dir, file_col, max_workers,
                    output_dir, smile, feature_set_name, id_cols=None):
    """Process all audio/video files for one subject, save checkpoint."""
    rows = subject_df.to_dict("records")
    results = [None] * len(rows)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(analyze_audio, i, row, base_dir, file_col, smile, feature_set_name): i
            for i, row in enumerate(rows)
        }
        with tqdm(total=len(rows), desc=f"  {name}", position=1, leave=False) as file_bar:
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = {"ok": False, "data": {}, "scores": {}, "error": str(e)}
                file_bar.update(1)

    out_df = build_output_df(rows, results, id_cols)
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
    _, stats = merge_checkpoints(ckpt_dir, out_path, file_col=args.file_col)
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
    parser.add_argument("--id-cols", nargs="*", default=None, help="Source columns to keep in output")
    parser.add_argument("--feature-set", default="emobase",
                        help="openSMILE feature set: emobase (default), eGeMAPSv02, GeMAPSv01b, ComParE_2016")
    parser.add_argument("--feature-level", default="functionals",
                        help="Extraction level: functionals (default, one row per file), lld (frame-level)")
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

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", flush=True)
        return

    if args.feature_set not in VALID_FEATURE_SETS:
        print(f"Unknown feature set: {args.feature_set}. Available: {sorted(VALID_FEATURE_SETS)}", flush=True)
        return

    if args.feature_level not in VALID_FEATURE_LEVELS:
        print(f"Unknown feature level: {args.feature_level}. Available: {sorted(VALID_FEATURE_LEVELS)}", flush=True)
        return

    if args.feature_level == "lld" and args.feature_set == "emobase":
        print("Warning: --feature-level lld with emobase produces per-frame LLDs, not functionals. "
              "The amean/stddev column filter will not apply.", flush=True)

    # Initialize openSMILE
    feature_level = (opensmile.FeatureLevel.Functionals if args.feature_level == "functionals"
                     else opensmile.FeatureLevel.LowLevelDescriptors)
    smile = opensmile.Smile(
        feature_set=_get_feature_set(args.feature_set),
        feature_level=feature_level,
    )
    print(f"openSMILE: {args.feature_set}, level={args.feature_level}", flush=True)

    df = read_input(args.input)
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
