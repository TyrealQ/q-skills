"""
Low-level visual feature extraction using Pillow and numpy.

Extracts scalar visual features from images: color (RGB/HSV), texture,
shape, spatial composition, image quality, and optionally EXIF metadata.
All outputs are scalars (one column per metric) for flat xlsx output.

Generic — no project-specific names. All paths come from CLI args.

Tip: set PYTHONUNBUFFERED=1 or use `python -u` for live progress in
background/piped execution.
"""

import argparse
import math
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from common import read_input, save_excel, derive_subject, merge_checkpoints
from PIL import Image, ImageFilter, ExifTags
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Feature column lists (project-independent)
# ---------------------------------------------------------------------------

RGB_FIELDS = [
    "rgb_r_mean", "rgb_r_std", "rgb_g_mean", "rgb_g_std",
    "rgb_b_mean", "rgb_b_std", "brightness", "contrast",
    "colorfulness", "dominant_color_1", "dominant_color_2", "dominant_color_3",
]

HSV_FIELDS = [
    "hsv_h_mean", "hsv_h_std", "hsv_s_mean", "hsv_s_std",
    "hsv_v_mean", "hsv_v_std", "color_temp",
]

TEXTURE_FIELDS = ["entropy", "sharpness", "edge_density", "noise_estimate"]

SHAPE_FIELDS = ["contour_count", "line_orientation", "aspect_ratio"]

SPATIAL_FIELDS = [
    "rule_of_thirds", "symmetry_h", "symmetry_v",
    "whitespace_ratio", "visual_center_x", "visual_center_y",
]

QUALITY_FIELDS = ["dynamic_range", "resolution"]

EXIF_FIELDS = [
    "exif_camera_make", "exif_camera_model", "exif_datetime",
    "exif_exposure_time", "exif_f_number", "exif_iso",
    "exif_focal_length", "exif_gps_lat", "exif_gps_lon",
    "exif_orientation", "exif_software",
    "exif_image_width", "exif_image_height",
]

# Category registry: name -> (field list, extractor key)
FEATURE_CATEGORIES = {
    "rgb": RGB_FIELDS,
    "hsv": HSV_FIELDS,
    "texture": TEXTURE_FIELDS,
    "shape": SHAPE_FIELDS,
    "spatial": SPATIAL_FIELDS,
    "quality": QUALITY_FIELDS,
    "exif": EXIF_FIELDS,
}

CATEGORY_ORDER = ["rgb", "hsv", "texture", "shape", "spatial", "quality", "exif"]

VISUAL_FIELDS = RGB_FIELDS + HSV_FIELDS + TEXTURE_FIELDS + SHAPE_FIELDS + SPATIAL_FIELDS + QUALITY_FIELDS

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


# ---------------------------------------------------------------------------
# K-means (numpy only, no scikit-learn)
# ---------------------------------------------------------------------------

def kmeans_numpy(pixels, k=5, max_iter=20):
    """Pure-numpy k-means. Returns cluster centers sorted by count desc."""
    rng = np.random.default_rng(42)
    n = len(pixels)
    if n < k:
        pad = np.zeros((k - n, 3), dtype=pixels.dtype)
        pixels = np.vstack([pixels, pad])
        n = len(pixels)
    indices = rng.choice(n, size=k, replace=False)
    centers = pixels[indices].astype(np.float64)
    for _ in range(max_iter):
        dists = np.linalg.norm(pixels[:, None].astype(np.float64) - centers[None, :], axis=2)
        labels = np.argmin(dists, axis=1)
        for j in range(k):
            mask = labels == j
            if mask.any():
                centers[j] = pixels[mask].astype(np.float64).mean(axis=0)
    counts = np.bincount(labels, minlength=k)
    order = np.argsort(-counts)
    return centers[order]


def _rgb_to_hex(r, g, b):
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"


# ---------------------------------------------------------------------------
# Feature extractors
# ---------------------------------------------------------------------------

def extract_rgb_features(img, arr):
    """RGB channel statistics and dominant colors."""
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    rf, gf, bf = r.astype(np.float64), g.astype(np.float64), b.astype(np.float64)

    lum = 0.299 * rf + 0.587 * gf + 0.114 * bf

    rg = rf - gf
    yb = 0.5 * (rf + gf) - bf
    sigma = math.sqrt(np.std(rg) ** 2 + np.std(yb) ** 2)
    mu = math.sqrt(np.mean(rg) ** 2 + np.mean(yb) ** 2)
    colorfulness = sigma + 0.3 * mu

    small = img.copy()
    small.thumbnail((200, 200))
    px = np.array(small).reshape(-1, 3)
    sample_size = min(1000, len(px))
    rng = np.random.default_rng(42)
    sample = px[rng.choice(len(px), size=sample_size, replace=False)]
    centers = kmeans_numpy(sample, k=5)
    hex_colors = [_rgb_to_hex(*c) for c in centers[:3]]

    return {
        "rgb_r_mean": float(np.mean(rf)), "rgb_r_std": float(np.std(rf)),
        "rgb_g_mean": float(np.mean(gf)), "rgb_g_std": float(np.std(gf)),
        "rgb_b_mean": float(np.mean(bf)), "rgb_b_std": float(np.std(bf)),
        "brightness": float(np.mean(lum)),
        "contrast": float(np.std(lum)),
        "colorfulness": float(colorfulness),
        "dominant_color_1": hex_colors[0],
        "dominant_color_2": hex_colors[1],
        "dominant_color_3": hex_colors[2],
    }


def extract_hsv_features(img):
    """HSV statistics with circular mean/std for hue."""
    hsv_img = img.convert("HSV")
    hsv_arr = np.array(hsv_img, dtype=np.float64)

    h_raw = hsv_arr[:, :, 0] * (360.0 / 255.0)
    s_raw = hsv_arr[:, :, 1] / 255.0
    v_raw = hsv_arr[:, :, 2] / 255.0

    mask = s_raw > 0.1
    if np.sum(mask) < 10:
        h_mean, h_std = 0.0, 0.0
    else:
        h_vals = h_raw[mask]
        h_rad = np.deg2rad(h_vals)
        sin_m = np.mean(np.sin(h_rad))
        cos_m = np.mean(np.cos(h_rad))
        h_mean = float(np.rad2deg(np.arctan2(sin_m, cos_m)) % 360)
        r_bar = math.sqrt(sin_m ** 2 + cos_m ** 2)
        h_std = float(np.rad2deg(math.sqrt(-2 * math.log(max(r_bar, 1e-10))))) if r_bar < 1 else 0.0

    warm = np.sum((h_raw < 60) | (h_raw > 300))
    cool = np.sum((h_raw > 120) & (h_raw < 240))
    color_temp = float(warm / max(cool, 1))

    return {
        "hsv_h_mean": h_mean, "hsv_h_std": h_std,
        "hsv_s_mean": float(np.mean(s_raw)), "hsv_s_std": float(np.std(s_raw)),
        "hsv_v_mean": float(np.mean(v_raw)), "hsv_v_std": float(np.std(v_raw)),
        "color_temp": color_temp,
    }


def extract_texture_features(gray, gray_arr):
    """Entropy, sharpness, edge density, noise. Returns intermediates for reuse."""
    entropy = float(gray.entropy())

    lap_kernel = ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], scale=1, offset=128)
    lap = np.array(gray.filter(lap_kernel), dtype=np.float64) - 128.0
    sharpness = float(np.var(lap))

    sobel_x_kernel = ImageFilter.Kernel((3, 3), [-1, 0, 1, -2, 0, 2, -1, 0, 1], scale=1, offset=128)
    sobel_y_kernel = ImageFilter.Kernel((3, 3), [-1, -2, -1, 0, 0, 0, 1, 2, 1], scale=1, offset=128)
    sx = np.array(gray.filter(sobel_x_kernel), dtype=np.float64) - 128.0
    sy = np.array(gray.filter(sobel_y_kernel), dtype=np.float64) - 128.0
    grad_mag = np.sqrt(sx ** 2 + sy ** 2)

    threshold = np.mean(grad_mag) + np.std(grad_mag)
    edge_mask = grad_mag > threshold
    edge_density = float(np.mean(edge_mask))

    med = gray.filter(ImageFilter.MedianFilter(3))
    diff = gray_arr.astype(np.float64) - np.array(med, dtype=np.float64)
    noise_estimate = float(np.std(diff))

    features = {
        "entropy": entropy,
        "sharpness": sharpness,
        "edge_density": edge_density,
        "noise_estimate": noise_estimate,
    }
    return features, sx, sy, grad_mag


def extract_shape_features(img, gray_arr, sx, sy, grad_mag):
    """Contour count, line orientation, aspect ratio."""
    w, h = img.size

    threshold = np.mean(grad_mag) + np.std(grad_mag)
    edge_binary = (grad_mag > threshold).astype(np.uint8)
    diffs = np.diff(edge_binary, axis=1)
    contour_count = int(np.sum(diffs == 1))

    strong = grad_mag > threshold
    if np.sum(strong) > 0:
        angles = np.rad2deg(np.arctan2(sy[strong], sx[strong])) % 180
        hist, edges = np.histogram(angles, bins=18, range=(0, 180))
        peak_bin = np.argmax(hist)
        line_orientation = float((edges[peak_bin] + edges[peak_bin + 1]) / 2)
    else:
        line_orientation = 0.0

    return {
        "contour_count": contour_count,
        "line_orientation": line_orientation,
        "aspect_ratio": float(w / max(h, 1)),
    }


def extract_spatial_features(gray_arr, grad_mag, rgb_arr):
    """Rule of thirds, symmetry, whitespace, visual center."""
    h, w = gray_arr.shape

    energy = grad_mag ** 2
    total_energy = np.sum(energy)
    if total_energy > 0:
        band_w = max(int(0.05 * w), 1)
        band_h = max(int(0.05 * h), 1)
        thirds_energy = 0.0
        for frac in (1 / 3, 2 / 3):
            cx = int(frac * w)
            cy = int(frac * h)
            thirds_energy += np.sum(energy[:, max(0, cx - band_w):cx + band_w])
            thirds_energy += np.sum(energy[max(0, cy - band_h):cy + band_h, :])
        rule_of_thirds = float(min(thirds_energy / total_energy, 1.0))
    else:
        rule_of_thirds = 0.0

    small_h, small_w = min(h, 200), min(w, 200)
    small = np.array(Image.fromarray(gray_arr.astype(np.uint8)).resize((small_w, small_h)), dtype=np.float64)
    mid_w = small_w // 2
    if mid_w > 0:
        left = small[:, :mid_w]
        right = small[:, -mid_w:][:, ::-1]
        symmetry_h = float(1.0 - np.mean(np.abs(left - right)) / 255.0)
    else:
        symmetry_h = 1.0
    mid_h = small_h // 2
    if mid_h > 0:
        top = small[:mid_h, :]
        bottom = small[-mid_h:, :][::-1, :]
        symmetry_v = float(1.0 - np.mean(np.abs(top - bottom)) / 255.0)
    else:
        symmetry_v = 1.0

    white_mask = np.all(rgb_arr > 240, axis=2)
    whitespace_ratio = float(np.mean(white_mask))

    total = np.sum(grad_mag)
    if total > 0:
        visual_center_x = float(np.dot(grad_mag.sum(axis=0), np.arange(w)) / total / max(w - 1, 1))
        visual_center_y = float(np.dot(grad_mag.sum(axis=1), np.arange(h)) / total / max(h - 1, 1))
    else:
        visual_center_x, visual_center_y = 0.5, 0.5

    return {
        "rule_of_thirds": rule_of_thirds,
        "symmetry_h": symmetry_h,
        "symmetry_v": symmetry_v,
        "whitespace_ratio": whitespace_ratio,
        "visual_center_x": visual_center_x,
        "visual_center_y": visual_center_y,
    }


def extract_quality_features(gray_arr, img):
    """Dynamic range and resolution."""
    w, h = img.size
    return {
        "dynamic_range": float(np.max(gray_arr) - np.min(gray_arr)),
        "resolution": float(w * h / 1_000_000),
    }


def extract_exif(img):
    """Extract EXIF metadata. Returns empty strings/NaN for missing tags."""
    result = {f: "" for f in EXIF_FIELDS}
    try:
        exif_data = img.getexif()
        if not exif_data:
            return result
    except Exception:
        return result

    tag_map = {}
    for tag_id, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        tag_map[tag_name] = value

    result["exif_camera_make"] = str(tag_map.get("Make", ""))
    result["exif_camera_model"] = str(tag_map.get("Model", ""))
    result["exif_datetime"] = str(tag_map.get("DateTimeOriginal", tag_map.get("DateTime", "")))
    result["exif_software"] = str(tag_map.get("Software", ""))
    result["exif_orientation"] = tag_map.get("Orientation", "")

    for field, tag in [("exif_f_number", "FNumber"), ("exif_focal_length", "FocalLength")]:
        val = tag_map.get(tag)
        if val is not None:
            try:
                result[field] = float(val)
            except (TypeError, ValueError):
                pass

    val = tag_map.get("ExposureTime")
    if val is not None:
        result["exif_exposure_time"] = str(val)

    val = tag_map.get("ISOSpeedRatings")
    if val is not None:
        result["exif_iso"] = val

    result["exif_image_width"] = tag_map.get("ExifImageWidth", "")
    result["exif_image_height"] = tag_map.get("ExifImageHeight", "")

    try:
        gps_info = exif_data.get_ifd(ExifTags.IFD.GPSInfo)
        if gps_info:
            def _dms_to_decimal(dms, ref):
                d, m, s = [float(x) for x in dms]
                dec = d + m / 60 + s / 3600
                if ref in ("S", "W"):
                    dec = -dec
                return dec

            lat_dms = gps_info.get(2)
            lat_ref = gps_info.get(1, "N")
            lon_dms = gps_info.get(4)
            lon_ref = gps_info.get(3, "E")
            if lat_dms:
                result["exif_gps_lat"] = _dms_to_decimal(lat_dms, lat_ref)
            if lon_dms:
                result["exif_gps_lon"] = _dms_to_decimal(lon_dms, lon_ref)
    except Exception:
        pass

    return result


# ---------------------------------------------------------------------------
# Per-image orchestrator
# ---------------------------------------------------------------------------

def analyze_image_from_path(abs_path, active_categories):
    """Analyze a single image file by absolute path. Returns {ok, data, error}."""
    try:
        img = Image.open(abs_path).convert("RGB")
        arr = np.array(img)
        gray = img.convert("L")
        gray_arr = np.array(gray, dtype=np.float64)

        features = {}

        # Texture intermediates are reused by shape and spatial
        tex_data, sx, sy, grad_mag = None, None, None, None
        if any(c in active_categories for c in ("texture", "shape", "spatial")):
            tex_data, sx, sy, grad_mag = extract_texture_features(gray, gray_arr)
            if "texture" in active_categories:
                features.update(tex_data)

        if "rgb" in active_categories:
            features.update(extract_rgb_features(img, arr))
        if "hsv" in active_categories:
            features.update(extract_hsv_features(img))
        if "shape" in active_categories:
            features.update(extract_shape_features(img, gray_arr, sx, sy, grad_mag))
        if "spatial" in active_categories:
            features.update(extract_spatial_features(gray_arr, grad_mag, arr))
        if "quality" in active_categories:
            features.update(extract_quality_features(gray_arr, img))
        if "exif" in active_categories:
            features.update(extract_exif(img))

        return {"ok": True, "data": features, "error": ""}
    except Exception as e:
        return {"ok": False, "data": {}, "error": str(e)}


def analyze_image(idx, row, base_dir, file_col, active_categories):
    """Open one image from a row, extract selected features. Returns {ok, data, error}."""
    rel_path = row.get(file_col, "")
    if not rel_path:
        return {"ok": False, "data": {}, "error": "empty path"}

    ext = Path(str(rel_path)).suffix.lower()
    if ext not in IMAGE_EXTENSIONS:
        return {"ok": False, "data": {}, "error": f"skipped non-image: {ext}"}

    abs_path = os.path.join(base_dir, rel_path)
    if not os.path.isfile(abs_path):
        return {"ok": False, "data": {}, "error": f"file not found: {abs_path}"}

    return analyze_image_from_path(abs_path, active_categories)


# ---------------------------------------------------------------------------
# DataFrame construction and subject processing
# ---------------------------------------------------------------------------

def build_output_df(rows, results, active_fields, id_cols=None):
    """Merge source rows with extracted features."""
    source_df = pd.DataFrame(rows)
    if id_cols:
        keep = [c for c in id_cols if c in source_df.columns]
        source_df = source_df[keep]

    feature_rows = []
    ok_flags = []
    for r in results:
        row_data = {}
        for f in active_fields:
            row_data[f] = r["data"].get(f, "")
        feature_rows.append(row_data)
        ok_flags.append(r["ok"])

    feature_df = pd.DataFrame(feature_rows)
    out = pd.concat([source_df.reset_index(drop=True), feature_df.reset_index(drop=True)], axis=1)
    out["ok"] = ok_flags
    return out


def process_subject(name, subject_df, base_dir, file_col, max_workers,
                    output_dir, active_categories, active_fields, id_cols=None):
    """Process all images for one subject, save checkpoint."""
    rows = subject_df.to_dict("records")
    results = [None] * len(rows)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(analyze_image, i, row, base_dir, file_col, active_categories): i
            for i, row in enumerate(rows)
        }
        with tqdm(total=len(rows), desc=f"  {name}", position=1, leave=False) as img_bar:
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = {"ok": False, "data": {}, "error": str(e)}
                img_bar.update(1)

    out_df = build_output_df(rows, results, active_fields, id_cols)
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
    out_path = os.path.join(args.output_dir, "_image_features.xlsx")
    _, stats = merge_checkpoints(ckpt_dir, out_path, file_col=args.file_col)
    if stats["files"]:
        print(f"Merged {stats['files']} checkpoints -> {out_path} ({stats['rows']} rows)", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Extract low-level visual features from images using Pillow")
    parser.add_argument("--input", default=None, help="Input xlsx file")
    parser.add_argument("--base-dir", default=None, help="Base directory for resolving relative file paths")
    parser.add_argument("--output-dir", default="output/pillow_image", help="Output directory")
    parser.add_argument("--merge", action="store_true", help="Merge all checkpoints into a single file")
    parser.add_argument("--group-col", default=None, help="Column to group rows by subject (default: auto from file path)")
    parser.add_argument("--file-col", default="file_path", help="Column containing image file paths")
    parser.add_argument("--id-cols", nargs="*", default=None,
                        help="Source columns to keep in output (default: all). Example: --id-cols file_path shortcode")
    parser.add_argument("--features", default="rgb,hsv,texture,shape,spatial,quality",
                        help="Comma-separated feature categories to extract. "
                             "Available: rgb, hsv, texture, shape, spatial, quality, exif. "
                             "Default: rgb,hsv,texture,shape,spatial,quality")
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
        print(f"Unknown feature categories: {unknown}. Available: {list(FEATURE_CATEGORIES.keys())}", flush=True)
        return
    active_fields = []
    for cat in CATEGORY_ORDER:
        if cat in active_categories:
            active_fields.extend(FEATURE_CATEGORIES[cat])
    print(f"Feature categories: {sorted(active_categories)} ({len(active_fields)} columns)", flush=True)

    df = read_input(args.input)
    print(f"Loaded {len(df)} rows from {args.input}", flush=True)

    if args.file_col not in df.columns:
        print(f"Column '{args.file_col}' not found. Available: {list(df.columns)}", flush=True)
        return

    # Filter to image rows only
    df = df[df[args.file_col].apply(
        lambda x: Path(str(x)).suffix.lower() in IMAGE_EXTENSIONS if pd.notna(x) else False
    )].copy()
    print(f"  {len(df)} image rows after filtering", flush=True)

    # Group by subject
    df["_subject"] = df.apply(lambda r: derive_subject(r, args.file_col, args.group_col), axis=1)
    groups = dict(list(df.groupby("_subject")))

    # Filter by --subjects if specified
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
            print(f"  {name}: {len(group_df)} images", flush=True)
        return

    # Process
    summaries = []
    for name in tqdm(sorted(pending.keys()), desc="Subjects", position=0):
        group_df = pending[name].drop(columns=["_subject"])
        summary = process_subject(
            name, group_df, args.base_dir, args.file_col, args.max_workers,
            args.output_dir, active_categories, active_fields, args.id_cols,
        )
        summaries.append(summary)
        tqdm.write(f"  {summary['name']}: {summary['ok']}/{summary['total']} ok -> {summary['path']}")

    # Summary
    print(f"\nDone: {len(summaries)} subjects processed", flush=True)
    total_ok = sum(s["ok"] for s in summaries)
    total_fail = sum(s["fail"] for s in summaries)
    print(f"  Total: {total_ok} ok, {total_fail} failed", flush=True)

    if args.merge:
        _run_merge(args)


if __name__ == "__main__":
    main()
