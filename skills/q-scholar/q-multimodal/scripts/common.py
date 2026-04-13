"""
Shared utilities for multimodal analysis scripts.

Provides common functions used across pillow and opensmile pipelines:
read_input, save_excel, derive_subject, merge_checkpoints.
"""

import os
from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


def read_input(path):
    """Read tabular input file, auto-detecting format by extension."""
    ext = Path(path).suffix.lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif ext == ".csv":
        return pd.read_csv(path)
    elif ext == ".json":
        return pd.read_json(path)
    elif ext == ".parquet":
        return pd.read_parquet(path)
    elif ext == ".tsv":
        return pd.read_csv(path, sep="\t")
    else:
        raise ValueError(f"Unsupported input format: {ext}. Use xlsx, csv, json, parquet, or tsv.")


def save_excel(df, path):
    """Save DataFrame to Excel with bold headers, auto-fit widths, frozen panes."""
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="features")
        ws = writer.sheets["features"]

        header_font = Font(bold=True)
        header_alignment = Alignment(horizontal="center", vertical="bottom")

        for col_idx, col_name in enumerate(df.columns, 1):
            letter = get_column_letter(col_idx)
            header_cell = ws[f"{letter}1"]
            header_cell.font = header_font
            header_cell.alignment = header_alignment

            sample = df[col_name].head(100).dropna().astype(str)
            max_val_len = int(sample.str.len().max()) if len(sample) else 0
            width = min(max(len(col_name), min(max_val_len, 50)) + 2, 55)
            ws.column_dimensions[letter].width = width

        ws.freeze_panes = "A2"


def derive_subject(row, file_col, group_col):
    """Derive subject name from group column or file path parent directory."""
    if group_col:
        val = str(row.get(group_col, "unknown"))
        val = val.rstrip("/").split("/")[-1]
        return val
    fp = str(row.get(file_col, ""))
    parts = Path(fp).parts
    if len(parts) >= 2:
        return parts[-2]
    return "default"


def merge_checkpoints(checkpoint_dir, output_path, file_col="file_path", exclude_prefix="_"):
    """Merge all checkpoint xlsx files in a directory into one file.

    Args:
        checkpoint_dir: Directory containing per-subject checkpoint xlsx files.
        output_path: Path for the merged output xlsx file.
        file_col: Column name for deduplication (default: "file_path").
        exclude_prefix: Skip files whose name starts with this prefix.
    Returns:
        Tuple of (merged_df, stats_dict) with keys: files, rows, deduped.
    """
    empty_stats = {"files": 0, "rows": 0, "deduped": 0}
    ckpt_path = Path(checkpoint_dir)
    if not ckpt_path.is_dir():
        print(f"  No checkpoint directory: {checkpoint_dir}", flush=True)
        return pd.DataFrame(), empty_stats

    files = sorted(f for f in ckpt_path.glob("*.xlsx") if not f.name.startswith(exclude_prefix))
    if not files:
        print(f"  No checkpoints found in {checkpoint_dir}", flush=True)
        return pd.DataFrame(), empty_stats

    dfs = []
    for f in files:
        try:
            dfs.append(pd.read_excel(f))
        except Exception as e:
            print(f"  Warning: failed to read {f.name}: {e}", flush=True)

    if not dfs:
        return pd.DataFrame(), empty_stats

    merged = pd.concat(dfs, ignore_index=True)
    before = len(merged)
    if file_col in merged.columns:
        merged = merged.drop_duplicates(subset=[file_col], keep="last")
    else:
        print(f"  Warning: column '{file_col}' not found, skipping deduplication", flush=True)
    deduped = before - len(merged)

    save_excel(merged, output_path)
    return merged, {"files": len(dfs), "rows": len(merged), "deduped": deduped}
