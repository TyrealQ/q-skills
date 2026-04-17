---
name: q-multimodal
description: Extract visual, video, and audio features from media. Use for pixel features (Pillow), video frames (FFmpeg+Pillow), audio features (openSMILE), and visual semantic analysis (Gemini API batch or standard).
---

# Q-Multimodal

Multimodal media analysis: local low-level features (Pillow, openSMILE), mid/high-level visual semantic analysis (Gemini API). Local pipelines are fully generic and CLI-driven. Gemini pipelines are config-driven: copy `scripts/gemini/pipeline_config.py` to your project, customize, and run with `--config <path>`.

## Setup (first time in a project)

Do this once when adopting the skill in a new project. The canonical layout is a target only for `scripts/` and `output/` — user assets (input data, media, `.env`, system prompt) can stay wherever they already live; point the scripts at them via absolute paths.

- **Identify** `<BASE_DIR>`: read the project's CLAUDE.md if it exists. If `BASE_DIR` isn't defined, ask the user which directory is the project root.
- **Locate existing user assets — do not move them.** Search, confirm each location with the user before proceeding:
  - Input dataset file (xlsx/csv/json/parquet)
  - Media directory (grouping structure — one subfolder per subject is ideal)
  - `.env` with `GOOGLE_API_KEY1`-`4` (Gemini only; check project root, home directory, common locations)
  - System prompt file (Gemini only)
- **Default: point at files in place.** Set `pipeline_config.py` fields or CLI `--input` / `--base-dir` arguments to the absolute paths you found. Never move user data without explicit confirmation.
- **Materialize** only `scripts/` and `output/` under `<BASE_DIR>`. Copy the pipelines actually being used from `${SKILL_DIR}/scripts/` into `<BASE_DIR>/scripts/`:
  - **Local pipelines**: `pillow/`, `opensmile/`, `common.py`
  - **Gemini pipelines**: `gemini/batch/`, `gemini/standard/`, `gemini/pipeline_config.py` (template → adapt in place or copy to `<BASE_DIR>/scripts/pipeline_config.py`)
  - `output/` is auto-created by scripts on first run
- **Scan input columns** (adapt reader to file format):
  `python -c "import pandas as pd; print(list(pd.read_<FORMAT>('INPUT', nrows=1).columns))"`
- **Confirm** `--id-cols` with the user. By default only the identifier column (from `--file-col`) is kept; the user may want additional columns carried through to the output.

## References

Read the relevant reference file **before** executing a pipeline. These contain all flags, output column definitions, edge cases, and validation rules.

**Local pipelines:**
- `references/image-visual-features.md` — all feature categories, column definitions, computation notes
- `references/video-visual-features.md` — frame extraction, aggregation logic, dual output format
- `references/audio-features.md` — openSMILE feature sets, interpretable scores, feature levels

**Gemini pipelines:**
- `references/gemini-batch-workflow.md` — full 6-step batch pipeline, retry workflow, error handling
- `references/gemini-standard.md` — standard pipeline details, model config, adapting for new projects
- `references/multi-key-management.md` — multi-key quota strategy, retry threshold decision table

**Shared:**
- `references/checkpoint-format.md` — column order, validation rules, output directory structure

## Dependencies

| Pipeline | Python packages | System |
|----------|----------------|--------|
| Image visual | `Pillow`, `numpy`, `pandas`, `tqdm`, `openpyxl` | — |
| Video visual | (same as image) + `scenedetect[opencv]` | `ffmpeg` on PATH (for `--extractor ffmpeg`) |
| Audio | `opensmile`, `pandas`, `tqdm`, `openpyxl` | `ffmpeg` on PATH |
| Gemini | `google-genai`, `python-dotenv` (+ above) | `.env` with `GOOGLE_API_KEY1`-`4` |

## Pipelines

Script path = `${SKILL_DIR}/scripts/<path>`. Read the pipeline's reference file before running.

### Local Pipelines (generic, CLI-driven)

| Script | Input | Output | Reference |
|--------|-------|--------|-----------|
| `pillow/visual_features.py` | Images | 47 pixel features (color, texture, spatial, quality) | `image-visual-features.md` |
| `pillow/video_features.py` | Videos | Frame-level + video-level aggregated features (scene-based extraction by default, FFmpeg fixed-interval optional) | `video-visual-features.md` |
| `opensmile/audio_features.py` | Video/audio | 8 interpretable scores + raw openSMILE features | `audio-features.md` |

Shared utilities: `common.py` — `read_input()`, `save_excel()`, `derive_subject()`, `merge_checkpoints()`

**Command pattern**: `python <script> --input <file> --base-dir <root> [--features ...] [--id-cols ...] [--subjects ...] [--preview] [--merge]`

### Gemini Pipelines (config-driven)

Both pipelines read a `pipeline_config.py` file that defines paths, schema, metadata formatting, and validation rules. Copy `scripts/gemini/pipeline_config.py` to your project and customize.

**Standard** (`gemini/standard/gemini_standard.py`): inline media, 25 workers, auto-retry. See `gemini-standard.md`.

**Batch** (`gemini/batch/[0-5]*.py` + `utils.py`): 6-step pipeline, 50% discount. URIs expire after 48 hours. See `gemini-batch-workflow.md`.

```bash
python 0uploadMedia.py --config /path/to/config.py --submit --max-batch-gb 2 --key 1
python 3checkStatus.py --config /path/to/config.py --poll
python 4retryErrors.py --config /path/to/config.py --preview
# >500 failures: batch retry
python 4retryErrors.py --config /path/to/config.py --submit
python 3checkStatus.py --config /path/to/config.py --poll
python 4retryErrors.py --config /path/to/config.py --collect
# <=500 failures or after batch retries: live fallback
python 4retryErrors.py --config /path/to/config.py --standard
python 5review.py --config /path/to/config.py --merge
```

**Decision**: >5 GB or >10 subjects and not time-sensitive → batch. Otherwise → standard. See `gemini-standard.md`.

**Multi-key**: Each `GOOGLE_API_KEY{N}` = 20 GB quota. See `multi-key-management.md`.

## Adapting for New Projects

**Local pipelines** (Pillow, openSMILE): No modification needed. All project-specific values come from CLI args.

**Gemini pipelines**: Config-driven, no script modification needed. Scripts are copied to the project in step 2 above, then:

- Adapt `<BASE_DIR>/scripts/pipeline_config.py` (already copied from template in step 2)
- Set `BASE_DIR`, `INPUT_PATH`, `SYSTEM_PROMPT_PATH` to your project paths (`SYSTEM_PROMPT_PATH` relative to `BASE_DIR`, e.g., `scripts/<prompt>.txt`)
- Set `GROUP_COL`, `FILE_COL`, `ANALYSIS_FIELDS` to match your input schema and system prompt
- Implement `subject_id()` and `format_metadata()` for your domain
- Optionally implement `validate_row()` for field-specific validation rules
- Run any script with `--config <BASE_DIR>/scripts/pipeline_config.py`

## Scope

**Include**: Image/video/audio feature extraction, Gemini visual semantic analysis, batch job management, checkpoint merging, multi-key quota management.

**Exclude**: ML model training, deep learning inference, real-time streaming analysis.

## Checklist

- [ ] Read project CLAUDE.md for paths and column names
- [ ] Confirm `--id-cols` and `--features` with user
- [ ] `--preview` dry run confirms expected subjects and counts
- [ ] Extraction completed with 0 or acceptable failures
- [ ] For Gemini: `.env` with API keys, system prompt file created
