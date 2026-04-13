"""Pipeline configuration template for Gemini semantic analysis.

Copy this file to your project directory and customize the values below.
The pipeline discovers config via:
    --config <path>  >  GEMINI_PIPELINE_CONFIG env var  >  ./pipeline_config.py

All relative paths are resolved against BASE_DIR.
"""

# ============================================================================
# Required: Paths
# ============================================================================

BASE_DIR = r"D:\my_project"
# Example (NBA): r"D:\NBA_players_images"

INPUT_PATH = "output/assets.xlsx"               # relative to BASE_DIR
# Example (NBA): "output/nba_player_assets.xlsx"

SYSTEM_PROMPT_PATH = "scripts/prompt.txt"       # relative to BASE_DIR
# Example (NBA): "scripts/SP_NBA_MMAB.txt"


# ============================================================================
# Required: Schema
# ============================================================================

GROUP_COL = "subject_id"    # column to group rows by subject
# Example (NBA): "ig_link"

FILE_COL = "file_path"      # column with media file paths (relative to BASE_DIR)

ANALYSIS_FIELDS = [          # output fields — must match your system prompt JSON schema
    # "field1", "field2", ...
]
# Example (NBA):
# ANALYSIS_FIELDS = [
#     "summary", "text", "individuals", "objects",
#     "v_fs_evidence", "v_fs_score", "v_bs_evidence", "v_bs_score",
#     "ss_evidence", "ss_score",
#     "t_fs_evidence", "t_fs_score", "t_bs_evidence", "t_bs_score",
#     "sponsored", "confidence",
# ]


# ============================================================================
# Required: Subject ID + Metadata
# ============================================================================

def subject_id(group_value):
    """Extract a short ID from GROUP_COL value (used in filenames and JSONL keys).

    Must return a filesystem-safe string.
    """
    return str(group_value).strip()

# Example (NBA): extract Instagram handle from URL
# def subject_id(ig_link):
#     s = ig_link.strip().rstrip("/")
#     return s.rsplit("/", 1)[-1]


METADATA_COLS = []  # columns included as context per media file
# Example (NBA): ["name", "country", "timestamp", "caption"]


def format_metadata(row):
    """Format context text sent alongside each media file.

    This text is prepended to the media in the Gemini request.
    """
    parts = []
    for col in METADATA_COLS:
        val = str(row.get(col, "") or "").strip() or "Unknown"
        parts.append(f"{col}: {val}")
    return "\n".join(parts)

# Example (NBA):
# def format_metadata(row):
#     caption = str(row.get("caption") or "").strip() or "None provided"
#     timestamp = str(row.get("timestamp") or "").strip() or "Unknown"
#     return (
#         f"Player: {row.get('name', 'Unknown')}\n"
#         f"Country: {row.get('country', 'Unknown')}\n"
#         f"Date: {timestamp}\n"
#         f"Caption: {caption}"
#     )


# ============================================================================
# Optional: Model
# ============================================================================

MODEL = "gemini-3.1-pro-preview"
TEMPERATURE = 1
THINKING_LEVEL = "HIGH"


# ============================================================================
# Optional: Output
# ============================================================================

OUTPUT_DIR = "output"                     # relative to BASE_DIR
CHECKPOINT_PREFIX = "subject_"            # prefix for per-subject checkpoint files
BATCH_PREFIX = "batch_"                   # prefix for batch job display names / JSONL files
RETRY_PREFIX = "retry_"                   # prefix for retry job display names / JSONL files
MERGED_FILENAME = "analysis.xlsx"         # final merged output filename

# Example (NBA):
# CHECKPOINT_PREFIX = "player_"
# BATCH_PREFIX = "mmab_batch_"
# RETRY_PREFIX = "mmab_retry_"
# MERGED_FILENAME = "nba_mmab_analysis.xlsx"


# ============================================================================
# Optional: Validation
# ============================================================================

def validate_row(data):
    """Per-row validation rules applied during review (5review.py).

    Args:
        data: dict of analysis fields from model output

    Returns:
        list of issue description strings (empty if valid)
    """
    return []

# Example (NBA):
# def validate_row(data):
#     issues = []
#     score_fields = [f for f in ANALYSIS_FIELDS if f.endswith("_score")]
#     for sf in score_fields:
#         val = data.get(sf)
#         if val is not None:
#             try:
#                 if not (1 <= int(val) <= 5):
#                     issues.append(f"{sf}={val} outside 1-5")
#             except (ValueError, TypeError):
#                 issues.append(f"{sf}={val} not an integer")
#     sp = data.get("sponsored")
#     if sp is not None:
#         try:
#             if int(sp) not in (0, 1):
#                 issues.append(f"sponsored={sp} not 0/1")
#         except (ValueError, TypeError):
#             issues.append(f"sponsored={sp} not an integer")
#     conf = data.get("confidence")
#     if isinstance(conf, str) and conf.lower() not in ("high", "low"):
#         issues.append(f"confidence={conf} not high/low")
#     return issues
