"""
Video visual feature extraction: frame extraction + Pillow analysis.

Two frame-extraction strategies (selected via --extractor):
  - scenedetect (default): PySceneDetect detects scene boundaries; 1+ frames
    are sampled per scene per --frame-mode (middle / boundaries / evenly-spaced)
  - ffmpeg: fixed-interval sampling at --fps

Pillow visual feature extraction runs on each extracted frame, producing:
  - Frame-level: one row per frame (temporal detail + scene metadata)
  - Video-level: one row per video (aggregated summary)

Generic — no project-specific names. All paths come from CLI args.

Tip: set PYTHONUNBUFFERED=1 or use `python -u` for live progress in
background/piped execution.
"""

import argparse
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mode as stat_mode

import numpy as np
import pandas as pd
from tqdm import tqdm

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import read_input, save_excel, derive_subject, merge_checkpoints
from visual_features import (
    CATEGORY_ORDER,
    FEATURE_CATEGORIES,
    analyze_image_from_path,
)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
FRAME_MODES = {"middle", "boundaries", "evenly-spaced"}


# ---------------------------------------------------------------------------
# FFmpeg frame extraction (fixed-interval)
# ---------------------------------------------------------------------------

def extract_frames_ffmpeg(video_path, output_dir, fps=1.0):
    """Extract frames at constant FPS via FFmpeg.
    Returns list of {path, scene_id, scene_start, scene_end, timestamp}."""
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={fps}",
        "-q:v", "2",
        os.path.join(output_dir, "%06d.jpg"),
        "-loglevel", "error",
        "-y",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()}")

    frames = sorted(Path(output_dir).glob("*.jpg"))
    step = 1.0 / fps if fps > 0 else 1.0
    return [
        {
            "path": str(f),
            "scene_id": None,
            "scene_start": None,
            "scene_end": None,
            "timestamp": i * step,
        }
        for i, f in enumerate(frames)
    ]


# ---------------------------------------------------------------------------
# PySceneDetect frame extraction (scene-based)
# ---------------------------------------------------------------------------

def _target_frames_for_scene(start_frame, end_frame, frame_mode, frames_per_scene):
    """Compute frame indices to sample from a scene given the mode.
    Scene runs [start_frame, end_frame) in PySceneDetect convention."""
    last = max(end_frame - 1, start_frame)
    if frame_mode == "middle":
        return [(start_frame + last) // 2]
    if frame_mode == "boundaries":
        if last == start_frame:
            return [start_frame]
        return [start_frame, last]
    # evenly-spaced
    n = max(int(frames_per_scene), 1)
    if n == 1:
        return [(start_frame + last) // 2]
    span = last - start_frame
    return [start_frame + int(round(k * span / (n - 1))) for k in range(n)]


def extract_frames_scenedetect(video_path, output_dir, threshold=27.0,
                               min_scene_len=15, frame_mode="middle",
                               frames_per_scene=3):
    """Detect scenes with PySceneDetect, sample frames per mode, write JPEGs.
    Returns list of {path, scene_id, scene_start, scene_end, timestamp}."""
    try:
        from scenedetect import detect, ContentDetector
        import cv2
    except ImportError as e:
        raise RuntimeError(
            f"scenedetect extractor requires scenedetect[opencv]: {e}. "
            "Install with: pip install scenedetect[opencv]"
        )

    if frame_mode not in FRAME_MODES:
        raise ValueError(f"invalid frame_mode={frame_mode}; expected one of {sorted(FRAME_MODES)}")

    os.makedirs(output_dir, exist_ok=True)

    scene_list = detect(
        video_path,
        ContentDetector(threshold=threshold, min_scene_len=min_scene_len),
    )

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"opencv failed to open video: {video_path}")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if fps <= 0:
            raise RuntimeError(f"opencv reported non-positive fps ({fps}) for {video_path}")

        if not scene_list:
            if total_frames <= 0:
                return []
            scenes = [(0, total_frames)]
        else:
            scenes = [(s.get_frames(), e.get_frames()) for s, e in scene_list]

        results = []
        for scene_idx, (start_f, end_f) in enumerate(scenes, start=1):
            scene_start_sec = start_f / fps
            scene_end_sec = end_f / fps
            targets = _target_frames_for_scene(start_f, end_f, frame_mode, frames_per_scene)

            for img_idx, target in enumerate(targets, start=1):
                cap.set(cv2.CAP_PROP_POS_FRAMES, target)
                ret, frame = cap.read()
                if not ret or frame is None:
                    continue
                out_name = f"scene_{scene_idx:04d}_img_{img_idx:02d}.jpg"
                out_path = os.path.join(output_dir, out_name)
                cv2.imwrite(out_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                results.append({
                    "path": out_path,
                    "scene_id": scene_idx,
                    "scene_start": float(scene_start_sec),
                    "scene_end": float(scene_end_sec),
                    "timestamp": float(target / fps),
                })
        return results
    finally:
        cap.release()


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def extract_frames_dispatch(video_path, output_dir, extractor, fps=1.0,
                            scene_threshold=27.0, min_scene_len=15,
                            frame_mode="middle", frames_per_scene=3):
    if extractor == "scenedetect":
        return extract_frames_scenedetect(
            video_path, output_dir,
            threshold=scene_threshold,
            min_scene_len=min_scene_len,
            frame_mode=frame_mode,
            frames_per_scene=frames_per_scene,
        )
    if extractor == "ffmpeg":
        return extract_frames_ffmpeg(video_path, output_dir, fps=fps)
    raise ValueError(f"unknown extractor: {extractor}")


# ---------------------------------------------------------------------------
# Per-video processing
# ---------------------------------------------------------------------------

def analyze_video(idx, row, base_dir, file_col, active_categories,
                  extractor, fps, scene_threshold, min_scene_len,
                  frame_mode, frames_per_scene):
    """Extract frames from one video, analyze each. Returns {ok, frames, error}."""
    rel_path = row.get(file_col, "")
    if not rel_path:
        return {"ok": False, "frames": [], "error": "empty path"}

    ext = Path(str(rel_path)).suffix.lower()
    if ext not in VIDEO_EXTENSIONS:
        return {"ok": False, "frames": [], "error": f"skipped non-video: {ext}"}

    abs_path = os.path.join(base_dir, rel_path)
    if not os.path.isfile(abs_path):
        return {"ok": False, "frames": [], "error": f"file not found: {abs_path}"}

    tmp_dir = tempfile.mkdtemp(prefix="vf_frames_")
    try:
        frames = extract_frames_dispatch(
            abs_path, tmp_dir, extractor,
            fps=fps,
            scene_threshold=scene_threshold,
            min_scene_len=min_scene_len,
            frame_mode=frame_mode,
            frames_per_scene=frames_per_scene,
        )
        if not frames:
            return {"ok": False, "frames": [], "error": "no frames extracted"}

        frame_results = []
        for i, fr in enumerate(frames):
            result = analyze_image_from_path(fr["path"], active_categories)
            result["frame_number"] = i + 1
            result["second"] = float(fr["timestamp"])
            result["scene_id"] = fr["scene_id"]
            result["scene_start"] = fr["scene_start"]
            result["scene_end"] = fr["scene_end"]
            frame_results.append(result)

        return {"ok": True, "frames": frame_results, "error": ""}
    except Exception as e:
        return {"ok": False, "frames": [], "error": str(e)}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_video_features(frame_df, active_fields):
    """Aggregate frame-level features to video-level summary."""
    agg = {}
    numeric_cols = []
    categorical_cols = []

    for f in active_fields:
        if f in frame_df.columns:
            if pd.api.types.is_numeric_dtype(frame_df[f]):
                numeric_cols.append(f)
            else:
                categorical_cols.append(f)

    for col in numeric_cols:
        vals = pd.to_numeric(frame_df[col], errors="coerce").dropna()
        if len(vals) > 0:
            agg[f"{col}_mean"] = float(vals.mean())
            agg[f"{col}_std"] = float(vals.std())
            agg[f"{col}_min"] = float(vals.min())
            agg[f"{col}_max"] = float(vals.max())
        else:
            agg[f"{col}_mean"] = np.nan
            agg[f"{col}_std"] = np.nan
            agg[f"{col}_min"] = np.nan
            agg[f"{col}_max"] = np.nan

    for col in categorical_cols:
        vals = frame_df[col].dropna()
        if len(vals) > 0:
            try:
                agg[f"{col}_mode"] = stat_mode(vals.tolist())
            except Exception:
                agg[f"{col}_mode"] = vals.iloc[0]
        else:
            agg[f"{col}_mode"] = np.nan

    agg["frame_count"] = len(frame_df)
    agg["ok_ratio"] = float(frame_df["ok"].sum() / max(len(frame_df), 1))

    return agg


# ---------------------------------------------------------------------------
# Subject processing
# ---------------------------------------------------------------------------

def process_subject(name, subject_df, base_dir, file_col, max_workers,
                    output_dir, active_categories, active_fields,
                    extractor, fps, scene_threshold, min_scene_len,
                    frame_mode, frames_per_scene, id_cols=None):
    """Process all videos for one subject, save frame-level and video-level checkpoints."""
    rows = subject_df.to_dict("records")
    results = [None] * len(rows)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(
                analyze_video, i, row, base_dir, file_col, active_categories,
                extractor, fps, scene_threshold, min_scene_len,
                frame_mode, frames_per_scene,
            ): i
            for i, row in enumerate(rows)
        }
        with tqdm(total=len(rows), desc=f"  {name}", position=1, leave=False) as vid_bar:
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = {"ok": False, "frames": [], "error": str(e)}
                vid_bar.update(1)

    # Build frame-level DataFrame
    frame_rows = []
    video_rows = []

    for row, result in zip(rows, results):
        source_data = {}
        if id_cols:
            for c in id_cols:
                source_data[c] = row.get(c, "")
        else:
            source_data = {file_col: row.get(file_col, "")}

        if result["ok"] and result["frames"]:
            any_frame_ok = any(fr["ok"] for fr in result["frames"])

            for fr in result["frames"]:
                fr_row = dict(source_data)
                fr_row["frame_number"] = fr["frame_number"]
                fr_row["second"] = fr["second"]
                fr_row["scene_id"] = fr.get("scene_id")
                fr_row["scene_start"] = fr.get("scene_start")
                fr_row["scene_end"] = fr.get("scene_end")
                for f in active_fields:
                    fr_row[f] = fr["data"].get(f, np.nan)
                fr_row["ok"] = fr["ok"]
                frame_rows.append(fr_row)

            vid_frame_df = pd.DataFrame([
                {f: fr["data"].get(f, np.nan) for f in active_fields} | {"ok": fr["ok"]}
                for fr in result["frames"]
            ])
            agg = aggregate_video_features(vid_frame_df, active_fields)
            vid_row = dict(source_data)
            vid_row.update(agg)
            vid_row["ok"] = any_frame_ok
            video_rows.append(vid_row)
        else:
            vid_row = dict(source_data)
            vid_row["frame_count"] = 0
            vid_row["ok_ratio"] = 0.0
            vid_row["ok"] = False
            video_rows.append(vid_row)

    frame_df = pd.DataFrame(frame_rows) if frame_rows else pd.DataFrame()
    video_df = pd.DataFrame(video_rows) if video_rows else pd.DataFrame()

    # Save checkpoints
    frames_dir = os.path.join(output_dir, "frames", "checkpoints")
    videos_dir = os.path.join(output_dir, "videos", "checkpoints")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)

    frames_path = os.path.join(frames_dir, f"{name}.xlsx")
    videos_path = os.path.join(videos_dir, f"{name}.xlsx")

    if not frame_df.empty:
        save_excel(frame_df, frames_path)
    if not video_df.empty:
        save_excel(video_df, videos_path)

    ok_count = sum(1 for r in results if r["ok"])
    fail_count = len(results) - ok_count
    total_frames = sum(len(r["frames"]) for r in results if r["ok"])
    return {
        "name": name, "total": len(rows), "ok": ok_count, "fail": fail_count,
        "frames": total_frames, "frames_path": frames_path, "videos_path": videos_path,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _run_merge(args):
    for kind, subdir, name, dedup in [
        ("Frames", "frames", "_frame_features.xlsx", [args.file_col, "frame_number"]),
        ("Videos", "videos", "_video_features.xlsx", None),
    ]:
        ckpt_dir = os.path.join(args.output_dir, subdir, "checkpoints")
        out_path = os.path.join(args.output_dir, subdir, name)
        _, stats = merge_checkpoints(ckpt_dir, out_path, file_col=args.file_col, dedup_cols=dedup)
        if stats["files"]:
            print(f"{kind}: merged {stats['files']} checkpoints -> {out_path} ({stats['rows']} rows)", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Extract visual features from video frames using PySceneDetect or FFmpeg + Pillow")
    parser.add_argument("--input", default=None, help="Input xlsx file")
    parser.add_argument("--base-dir", default=None, help="Base directory for resolving relative file paths")
    parser.add_argument("--output-dir", default="output/pillow_video", help="Output directory")
    parser.add_argument("--merge", action="store_true", help="Merge all checkpoints into single files")
    parser.add_argument("--group-col", default=None, help="Column to group rows by subject")
    parser.add_argument("--file-col", default="file_path", help="Column containing video file paths")
    parser.add_argument("--id-cols", nargs="*", default=None, help="Source columns to keep in output (default: file column only)")
    parser.add_argument("--features", default="rgb,hsv,texture,shape,spatial,quality",
                        help="Comma-separated feature categories. Available: rgb,hsv,texture,shape,spatial,quality")
    parser.add_argument("--extractor", choices=["scenedetect", "ffmpeg"], default="scenedetect",
                        help="Frame extraction strategy (default: scenedetect)")
    parser.add_argument("--frame-mode", choices=sorted(FRAME_MODES), default="middle",
                        help="scenedetect only: frames sampled per detected scene (default: middle)")
    parser.add_argument("--frames-per-scene", type=int, default=3,
                        help="scenedetect only: N frames per scene when --frame-mode evenly-spaced (default: 3)")
    parser.add_argument("--scene-threshold", type=float, default=27.0,
                        help="scenedetect only: ContentDetector HSV threshold; lower = more scenes (default: 27.0)")
    parser.add_argument("--min-scene-len", type=int, default=15,
                        help="scenedetect only: minimum scene length in frames (default: 15)")
    parser.add_argument("--fps", type=float, default=1.0,
                        help="ffmpeg only: frames per second to extract (default: 1.0)")
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

    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}", flush=True)
        return

    # Parse feature categories
    active_categories = set(c.strip() for c in args.features.split(","))
    unknown = active_categories - set(FEATURE_CATEGORIES.keys())
    if unknown:
        print(f"Unknown feature categories: {unknown}", flush=True)
        return
    active_fields = []
    for cat in CATEGORY_ORDER:
        if cat in active_categories:
            active_fields.extend(FEATURE_CATEGORIES[cat])
    print(f"Feature categories: {sorted(active_categories)} ({len(active_fields)} columns)", flush=True)
    if args.extractor == "scenedetect":
        mode_desc = args.frame_mode
        if args.frame_mode == "evenly-spaced":
            mode_desc += f", n={args.frames_per_scene}"
        print(
            f"Extractor: scenedetect (mode={mode_desc}, "
            f"threshold={args.scene_threshold}, min_scene_len={args.min_scene_len})",
            flush=True,
        )
        if args.fps != 1.0:
            print("  (note: --fps is ignored with --extractor scenedetect)", flush=True)
    else:
        print(f"Extractor: ffmpeg (fps={args.fps})", flush=True)
        ignored = [
            f"--{name}={getattr(args, attr)}"
            for name, attr, default in [
                ("frame-mode", "frame_mode", "middle"),
                ("frames-per-scene", "frames_per_scene", 3),
                ("scene-threshold", "scene_threshold", 27.0),
                ("min-scene-len", "min_scene_len", 15),
            ]
            if getattr(args, attr) != default
        ]
        if ignored:
            print(f"  (note: ignored with --extractor ffmpeg: {', '.join(ignored)})", flush=True)

    df = read_input(args.input)
    print(f"Loaded {len(df)} rows from {args.input}", flush=True)

    if args.file_col not in df.columns:
        print(f"Column '{args.file_col}' not found. Available: {list(df.columns)}", flush=True)
        return

    # Filter to video rows only
    df = df[df[args.file_col].apply(
        lambda x: Path(str(x)).suffix.lower() in VIDEO_EXTENSIONS if pd.notna(x) else False
    )].copy()
    print(f"  {len(df)} video rows after filtering", flush=True)

    # Group by subject
    df["_subject"] = df.apply(lambda r: derive_subject(r, args.file_col, args.group_col), axis=1)
    groups = dict(list(df.groupby("_subject")))

    if args.subjects:
        groups = {k: v for k, v in groups.items() if k in args.subjects}

    # Skip existing checkpoints (check video-level as indicator)
    videos_ckpt_dir = os.path.join(args.output_dir, "videos", "checkpoints")
    os.makedirs(videos_ckpt_dir, exist_ok=True)
    pending = {}
    for name, group_df in sorted(groups.items()):
        checkpoint = os.path.join(videos_ckpt_dir, f"{name}.xlsx")
        if os.path.isfile(checkpoint):
            continue
        pending[name] = group_df

    print(f"  {len(pending)} subjects pending ({len(groups) - len(pending)} already done)", flush=True)

    if args.preview or not pending:
        print(flush=True)
        for name, group_df in sorted(pending.items()):
            print(f"  {name}: {len(group_df)} videos", flush=True)
        return

    # Process
    summaries = []
    for name in tqdm(sorted(pending.keys()), desc="Subjects", position=0):
        group_df = pending[name].drop(columns=["_subject"])
        summary = process_subject(
            name, group_df, args.base_dir, args.file_col, args.max_workers,
            args.output_dir, active_categories, active_fields,
            args.extractor, args.fps, args.scene_threshold, args.min_scene_len,
            args.frame_mode, args.frames_per_scene, args.id_cols,
        )
        summaries.append(summary)
        tqdm.write(f"  {summary['name']}: {summary['ok']}/{summary['total']} ok, "
                    f"{summary['frames']} frames")

    print(f"\nDone: {len(summaries)} subjects processed", flush=True)
    total_ok = sum(s["ok"] for s in summaries)
    total_fail = sum(s["fail"] for s in summaries)
    total_frames = sum(s["frames"] for s in summaries)
    print(f"  Total: {total_ok} ok, {total_fail} failed, {total_frames} frames extracted", flush=True)

    if args.merge:
        _run_merge(args)


if __name__ == "__main__":
    main()
