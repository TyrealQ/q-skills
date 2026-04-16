# Image Visual Features — Detailed Reference

Script: `scripts/pillow/visual_features.py`

Extracts scalar visual features from pixel values using Pillow and numpy. No API calls, runs locally. Supports JPEG, PNG, BMP, TIFF, and WebP.

## All CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | (required) | Input file (xlsx, csv, json, parquet, etc.) |
| `--base-dir` | (required) | Base directory for resolving relative file paths |
| `--output-dir` | `output/pillow_image` | Checkpoint output directory |
| `--file-col` | `file_path` | Column containing file paths |
| `--group-col` | (auto) | Column to group by subject; default: parent directory of file path |
| `--id-cols` | file column only | Source columns to keep in output (default: file column only) |
| `--features` | `rgb,hsv,texture,shape,spatial,quality` | Comma-separated feature categories (default: all except exif) |
| `--subjects` | all | Process only these subjects |
| `--max-workers` | 10 | Concurrent workers for parallel image processing |
| `--preview` | off | Dry run: show pending subjects and counts, then exit |

## Feature Categories (47 total columns)

### RGB (12 columns)

| Column | Description |
|--------|-------------|
| `rgb_r_mean`, `rgb_r_std` | Red channel mean and standard deviation |
| `rgb_g_mean`, `rgb_g_std` | Green channel mean and standard deviation |
| `rgb_b_mean`, `rgb_b_std` | Blue channel mean and standard deviation |
| `brightness` | Mean luminance (0.299R + 0.587G + 0.114B) |
| `contrast` | Standard deviation of luminance |
| `colorfulness` | Hasler-Susstrunk metric |
| `dominant_color_1/2/3` | Top 3 colors from k-means clustering (k=5, seed=42), hex format |

### HSV (7 columns)

| Column | Description |
|--------|-------------|
| `hsv_h_mean`, `hsv_h_std` | Circular hue mean and standard deviation |
| `hsv_s_mean`, `hsv_s_std` | Saturation mean and standard deviation |
| `hsv_v_mean`, `hsv_v_std` | Value (brightness) mean and standard deviation |
| `color_temp` | Warm (>0) vs cool (<0) color temperature estimate |

### Texture (4 columns)

| Column | Description |
|--------|-------------|
| `entropy` | Shannon entropy of grayscale histogram |
| `sharpness` | Laplacian variance (higher = sharper) |
| `edge_density` | Fraction of edge pixels (Canny detection) |
| `noise_estimate` | Estimated noise level |

### Shape (3 columns)

| Column | Description |
|--------|-------------|
| `contour_count` | Number of detected contours |
| `line_orientation` | Dominant line angle |
| `aspect_ratio` | Width / height |

### Spatial (6 columns)

| Column | Description |
|--------|-------------|
| `rule_of_thirds` | Alignment score with rule-of-thirds grid |
| `symmetry_h`, `symmetry_v` | Horizontal and vertical symmetry scores |
| `whitespace_ratio` | Fraction of near-white pixels |
| `visual_center_x`, `visual_center_y` | Weighted visual center of the image (0-1) |

### Quality (2 columns)

| Column | Description |
|--------|-------------|
| `dynamic_range` | Difference between max and min luminance |
| `resolution` | Image resolution in megapixels |

### EXIF (13 columns, excluded by default)

| Column | Description |
|--------|-------------|
| `exif_camera_make`, `exif_camera_model` | Camera manufacturer and model |
| `exif_datetime` | Original capture timestamp |
| `exif_exposure_time`, `exif_f_number`, `exif_iso` | Exposure settings |
| `exif_focal_length` | Lens focal length |
| `exif_gps_lat`, `exif_gps_lon` | GPS coordinates |
| `exif_orientation` | Image orientation tag |
| `exif_software` | Software used to process the image |
| `exif_image_width`, `exif_image_height` | Original image dimensions |

EXIF data is often empty for social media images. Include with `--features rgb,hsv,...,exif`.

## Output

Checkpoint path: `<output-dir>/checkpoints/<subject>.xlsx`

Output columns: `identifier (--file-col) | additional id_cols (if specified) | selected feature columns | ok`

The `ok` column is `True` if features were extracted successfully, `False` on error (corrupt image, unsupported format, etc.). Failed rows are included with empty feature values.

## Edge Cases

- **Corrupt/truncated images**: Logged as warning, row saved with `ok=False` and empty features
- **Non-image files**: Skipped (filtered by extension: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`, `.webp`)
- **Grayscale images**: RGB/HSV features still computed (Pillow converts to RGB internally)
- **Very small images** (<10px): May produce degenerate spatial features
- **EXIF-stripped images**: EXIF columns return empty strings

## Performance

- Uses `concurrent.futures.ThreadPoolExecutor` with `--max-workers` threads
- Nested tqdm progress: subject-level + file-level within each subject
- Tip: Set `PYTHONUNBUFFERED=1` for real-time progress output
