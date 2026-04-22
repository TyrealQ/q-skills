# Changelog

All notable changes to this project will be documented in this file.

## [2.1.5] - 2026-04-22

### Changed

- **q-presentations**, **q-infographics**: default image generation model switched to `gpt-image-2`. Gemini (`gemini-3-pro-image-preview`) remains available via `IMAGE_MODEL=gemini` environment variable or `--model gemini` CLI flag. Requires new `openai` dependency and `OPENAI_API_KEY` environment variable; `GEMINI_API_KEY` still used for the Gemini fallback and for `gen_story.py`.

## [2.1.4] - 2026-04-19

### Fixed

- **q-multimodal**: fix `talking_duration_mean/std` always being NaN under emobase by mapping to `voiceProb_sma` (was `voicingFinalUnclipped_sma`, an eGeMAPS-only LLD)

## [2.1.3] - 2026-04-17

### Added

- **organize**: new utility skill for auditing project structure, aligning it to documented conventions, and archiving superseded content. Detects case drift, superseded generations, orphan files, and tracked per-machine state. Hands off to `/commit` or `/ship`.

### Changed

- **commit**: sweep editor/build temp files (`*.bak-*`, `__pycache__/`, `*.pyc`, `*.swp`, `.pytest_cache/`, etc.) from the working tree after each commit
- **ship**: mirror cleanup step after push, with matching checklist item

## [2.1.2] - 2026-04-16

### Added

- **q-multimodal**: add PySceneDetect as default video frame extractor with three sampling modes (`middle`, `boundaries`, `evenly-spaced`) and new `scene_id` / `scene_start` / `scene_end` columns in frame-level output
- **q-multimodal**: add `--extractor ffmpeg` option to retain fixed-interval (`--fps`) frame extraction for dense temporal sampling

## [2.1.1] - 2026-04-15

### Fixed

- **q-multimodal**: fix video frame merging dropping all but last frame per video during checkpoint merge
- **q-multimodal**: fix video summaries using empty strings instead of NaN for missing numeric values
- **q-multimodal**: fix video `ok` flag reporting success when no frames were actually analyzed
- **q-multimodal**: fix subject-name extraction for Windows backslash paths and sanitize unsafe filename characters
- **q-multimodal**: fix default output columns including all source columns instead of file column only

### Changed

- **q-multimodal**: remove LLD as supported audio feature level; only functionals is accepted
- **q-multimodal**: normalize all audio inputs through FFmpeg including native WAV files

## [2.1.0] - 2026-04-13

### Added

- **q-scholar/q-multimodal**: port multimodal feature extraction skill (Pillow, openSMILE, Gemini batch/standard) as a q-scholar sub-skill

### Changed

- **learn**: add inline trigger taxonomy, expanded frontmatter description, anti-patterns table, repetition threshold, conflict detection, and query mode
- **q-scholar**: reorder sub-skills by research trajectory (data: multimodal, eda, tf → writing: intro, litreview, methods, results)

## [2.0.3] - 2026-04-11

### Changed

- **q-infographics, q-presentations**: Bump image model to `gemini-3-pro-image-preview`

## [2.0.2] - 2026-04-05

### Changed

- **structure**: Flattened `skills/` by removing category subfolders (academic-skills, visual-content-skills, utility-skills); skills now sit directly under `skills/`
- **marketplace**: Consolidated three plugin entries into a single `q-skills` plugin; install with `/plugin install q-skills@q-skills`
- **README, CLAUDE.md**: Updated installation commands, folder trees, and skill-addition guidance to reflect flat structure

## [2.0.1] - 2026-04-03

### Changed

- **commit, ship**: Clarify cascade check skip condition in heading; strengthen CLAUDE.md freshness check to always run

## [2.0.0] - 2026-04-02

### Changed

- **All skills**: Standardized SKILL.md files to concise navigation format (~65-97 lines); detailed instructions migrated to `references/` files
- **All skills**: Unified workflow sections to consistent `| Step | Action | Reference |` table format
- **All skills**: Standardized frontmatter descriptions (imperative verb lead, concise triggers)
- **q-scholar**: Added q-litreview to frontmatter description; added Script Directory section with path resolution
- **q-educator**: Extracted 8 reference files (teaching philosophy, interview protocol, 5 deliverable templates, key phrases)
- **q-eda**: Extracted 4 reference files (interview protocol with column types, invocation guide, summary instructions); fixed script invocation to use `${SKILL_DIR}` directly; replaced Claude-specific primitives with generic agent phrasing; inlined pipeline phases table
- **q-tf**: Extracted 3 reference files (code patterns, preservation rules, outlier workflow); added Dependencies section with environment variables
- **q-presentations**: Extracted 2 reference files (options, workflow detailed); added Bun/Node.js runtime dependency; added workflow summary table with per-step references
- **q-infographics**: Moved prompt files from `prompts/` to `references/`; fixed folder path; added Plan Mode Guard and workflow summary table
- **q-methods, q-results**: Added workflow table sections with step-by-step references; enriched Section Architecture with narrative reasoning guidance; added anti-replication preamble to templates
- **q-intro, q-litreview**: Added Plan Mode Guards
- **commit**: Added When to Use context to frontmatter description
- **learn**: Removed stale references to non-existent skills
- **ship**: Added Verification Checklist section

## [1.9.2] - 2026-04-02

### Changed

- **commit**: Merged CLAUDE.md freshness check into Step 2 with cascade check for downstream file consistency; expanded file type table to include R and CSV
- **ship**: Added cascade check to Step 3 for verifying downstream reports match modified scripts; expanded file type table to include R and CSV; fixed broken YAML frontmatter

## [1.9.1] - 2026-03-31

### Changed

- **commit**: Added CLAUDE.md freshness check (Step 1.5) to catch stale temporal markers before committing
- **ship**: Added temporal marker awareness to CLAUDE.md update step

## [1.9.0] - 2026-03-29

### Changed

- **q-scholar**: Simplified orchestrator to sub-skill index and core writing principles; removed redundant folder tree, cross-references, usage examples, and generic quality statements
- **q-tf**: Renamed from q-topic-finetuning
- **q-scholar suite**: Standardized all drafting skills (q-intro, q-litreview, q-methods, q-results) to consistent section order (References, Core Principles, Architecture/Structure, Workflow, Scope, Checklist) with shared references at top and bullet-point instructions throughout
- **q-scholar suite**: Consolidated duplicated APA formatting rules; each skill now references shared apa_style_guide.md for numbers, notation, punctuation, and formulas instead of restating rules inline
- **q-scholar suite**: Added paragraph-density policy (3-12 sentences, no single-sentence paragraphs, no standalone intro paragraphs) across all drafting skills
- **q-methods**: Added appendix strategy with general inline-vs-appendix guidance and a user-refinement step for context-dependent standard-vs-detail boundaries
- **q-results**: Added core vs. peripheral results separation with appendix strategy and user-refinement step for context-dependent boundaries
- **apa_style_guide.md**: Expanded formula and backtick guidance to cover all expression types (regression equations, interaction terms, transformations, thresholds) with explicit in-table examples
- **appendix_template.md**: Moved from q-methods/references to shared q-scholar/references; expanded to cover both methods appendices (configuration, specifications, codebooks) and results appendices (complete tables, robustness checks, supplementary breakdowns)

## [1.8.0] - 2026-03-27

### Added

- **q-litreview**: New sub-skill under q-scholar for drafting standalone literature review sections with progressive-argument architecture, earned research questions, and cross-section coordination with the introduction

### Changed

- **q-scholar**: Added cross-section coordination principle to core writing principles
- **q-intro**: Added scope separation guidance for manuscripts with standalone literature reviews; restructured SKILL.md to reference files at top and remove content duplicated in references
- **q-intro, q-litreview**: Templates clarified as structural guidance, not verbatim scripts
- **commit, ship**: Replaced project-specific examples with generic ones
- **ship**: Stale reference check now also catches newly added directories missing from folder trees

## [1.7.2] - 2026-03-24

### Changed

- **structure**: Removed redundant `skills/` subdirectory from each category — skills now sit directly under their category folder (e.g., `skills/academic-skills/q-scholar/` instead of `skills/academic-skills/skills/q-scholar/`)
- **marketplace.json**: Updated skill paths to match flattened structure
- **README**: Expanded "EDA" abbreviation to "exploratory data analysis" for reader clarity

## [1.7.1] - 2026-03-23

### Added

- **q-scholar**: Formula and equation formatting guidance in apa_style_guide.md (QCA paths, Boolean expressions, set notation)

### Changed

- **structure**: Renamed top-level `plugins/` to `skills/`; updated marketplace source paths

## [1.7.0] - 2026-03-22

### Added

- **learn**: New skill for persisting user preferences, styles, and behavioral patterns across sessions

### Changed

- **q-eda**: Renamed from q-exploratory-analysis; output folder renamed from TABLE/ to tables-eda/
- **all skills**: Condensed YAML descriptions to concise, trigger-rich format

### Fixed

- **q-eda**: Classify high-cardinality whole-number columns as discrete instead of continuous
- **ship**: Add doc catch-up path for unpushed commits missing documentation updates
- **commit**: Add `git diff --cached` check to detect already-staged files

### Changed

- **marketplace**: Isolate plugin source directories to fix triple skill registration. Each plugin now caches only its own skills instead of the entire repo
- **structure**: Skills moved from `skills/` to `plugins/<plugin-name>/skills/` for per-plugin isolation

## [1.6.0] - 2026-03-02

### Added

- **utility-skills**: New plugin bundle with commit and ship skills for git workflow automation
- **commit**: Stage and commit with smart file grouping and conventional commit messages
- **ship**: Full ship cycle — update docs, commit, and push to remote

## [1.5.8] - 2026-02-27

### Added

- **README**: Environment Configuration section with API key setup guide, `.env` usage, and optional variables
- **q-infographics**: `python-dotenv` loading in `gen_image.py` and `gen_story.py` so `.env` files are picked up automatically

### Fixed

- **q-topic-finetuning**: Standardize env var name from `GEMINI_KEY` to `GEMINI_API_KEY` across all references
- **q-presentations**: `gen_slide.py` now exits with a clear error instead of a raw `KeyError` when API key is missing

## [1.5.7] - 2026-02-26

### Changed

- **q-presentations, q-infographics**: Update image generation model to Nano Banana 2
- **q-infographics**: Update documentation references to use Nano Banana branding

## [1.5.6] - 2026-02-25

### Fixed

- **q-eda**: Correlations now use pairwise deletion by default instead of listwise, maximizing N per pair
- **q-eda/SKILL.md**: Resolved inline-Python contradiction — preview step now uses `--preview` flag instead of ad-hoc Python snippet
- **q-eda/SKILL.md**: Source annotation and table rules scoped to content sections with infrastructure section exemption
- **q-eda/summary_template**: Crosstab example now includes Total row to match script's `margins=True` output

### Added

- **q-eda/SKILL.md**: Plan-mode guard that exits plan mode before attempting Bash-dependent stages (script deployment, `--preview`, EDA pipeline)
- **q-eda**: `--preview` flag prints `df.head()`, `df.dtypes`, `df.nunique()` and exits without running analysis
- **q-eda**: `--corr_deletion` CLI flag (`pairwise`|`listwise`) for user control over missing-data strategy in correlations
- **q-eda**: Expanded STOPWORDS from ~70 to ~318 words (scikit-learn ENGLISH_STOP_WORDS, no new dependency)

### Removed

- **q-eda**: `memory_kb` from dataset profile

### Changed

- **q-infographics, q-presentations, q-eda**: Moved dependencies from `requirements.txt` into SKILL.md; removed requirements.txt files

## [1.5.5] - 2026-02-24

### Fixed

- **q-eda/scripts/run_eda.py**: Filter NaT dates in `temporal_trends()` before period conversion to prevent crashes on unparseable dates
- **q-eda/scripts/run_eda.py**: Validate `--col_types` input format (`col=type`) and reject unknown types with clear error messages
- **q-eda/scripts/run_eda.py**: `save_csv()` now returns bool; CSV count only increments on successful writes (was overstated when data was empty)
- **q-eda/scripts/run_eda.py**: Final message no longer claims Excel output when `openpyxl` import fails
- **q-eda/SKILL.md**: Temporal analysis description corrected — no longer claims gap detection (not yet implemented)
- **q-eda/scripts/run_eda.py**: `quantitative_summary()` n=1 edge case now returns full column schema instead of 3-field stub
- **q-eda/scripts/run_eda.py**: `grouped_stats_by_nominal()` ordinal branch now includes M_quasi_interval and SD (was median/IQR only)
- **q-eda/scripts/run_eda.py**: Removed crosstab and group-column caps (was [:4] and [:2])

### Added

- **q-eda/SKILL.md**: Windows CMD and PowerShell deployment commands
- **q-eda/SKILL.md**: Behavioral defaults section documenting --group, cross-tab, ID detection, and LOW_CARD_MAX behavior
- **q-eda/references/summary_template.md**: Split outlier column into mild (IQR 1.5) and extreme (IQR 3.0) in detail tables

## [1.5.4] - 2026-02-22

### Fixed

- **q-eda/run_eda.py**: Fixed ID heuristic misclassifying numeric metrics — high-cardinality numeric columns now classified as Continuous; only non-numeric columns with >95% uniqueness treated as identifiers
- **q-eda/run_eda.py**: Pearson correlation now includes both Continuous and Discrete columns (was Continuous-only, producing empty correlations when all numeric columns were Discrete)
- **q-eda/SKILL.md**: Resolved contradictory section omission rules — new two-tier rule: all source CSVs absent → omit section; some absent → include section with note
- **q-eda/SKILL.md**: Fixed unreadable 22-24 column descriptive tables — split into core table (8 cols) and detail table (11 cols); narrow CSVs keep full columns
- **q-eda/SKILL.md**: Replaced vague flagging severity scheme with explicit thresholds (missing >10%, skewness abs>2, kurtosis abs>7, correlation abs>0.7, CV >100%, ID-like >95%)
- **q-eda/SKILL.md**: Fixed ordinal variables misplaced under "Categorical Variables" — restructured from 10 thematic sections to 13 measurement-level sections
- **q-eda/SKILL.md**: Fixed temporal data referenced in two sections — scoped overview vs. full trends
- **q-eda/SKILL.md**: Removed stale `DESCRIPTIVE_SUMMARY.md` style reference and incorrect "chi-square" claim
- **q-infographics, q-topic-finetuning, q-eda**: Replaced hardcoded paths with `${SKILL_DIR}` pattern — all script/reference paths now resolve from skill cache

### Added

- **q-eda/SKILL.md**: Script Directory section, table sizing rules, source-citation mandate, and two new verification checklist items
- **q-eda/references/summary_template.md**: Reference template with 13-section skeleton and worked example rows
- **q-infographics, q-topic-finetuning**: Script Directory sections with resource tables
- **CLAUDE.md**: Script Path Convention section documenting the `${SKILL_DIR}` standard

### Changed

- **q-eda/run_eda.py**: Consolidated 4 type-override flags into single `--col_types col=type` pairs; inverted `--no_interactive` to `--interactive`; renamed Phase 7 to Phase 6
- **q-eda/SKILL.md**: Reordered Section 4 (script phases first, Claude's narrative summary post-script); strengthened interview workflow; updated Column-Type Coverage table; added Windows `python` note
- **q-eda/scripts/requirements.txt**: Removed unused matplotlib and seaborn dependencies
- **q-topic-finetuning**: Moved from top-level skill into q-scholar as sub-skill
- **marketplace.json**: Reorganized from 5 one-per-skill plugins to 2 category plugins; bumped version
- **q-scholar/SKILL.md**: Added q-topic-finetuning as fifth sub-skill; updated phase references

## [1.5.0] - 2026-02-21

### Added

- **marketplace.json**: Enables `/plugin marketplace add TyrealQ/q-skills` and `/plugin install <skill>@q-skills` commands — each skill registered as a named plugin

### Changed

- **q-eda**: Renamed from q-descriptive-analysis; complete redesign around Stevens' levels of measurement (Nominal, Ordinal, Discrete, Continuous, Temporal, Text, ID/key)
  - Six-phase pipeline: Dataset Profile, Data Quality, Univariate, Bivariate/Multivariate, Specialized, Summary Report
  - Auto-detects column measurement level; flags ambiguous integers for interactive confirmation
  - Measurement-appropriate bivariate analysis: Pearson, Spearman, grouped descriptives, contingency tables
  - Full APA-compatible quantitative metrics for Ordinal, Discrete, and Continuous columns
  - Binary variable analysis with proportion and 95% CI
  - Text analysis: top unigrams/bigrams, vocab size, avg word count
  - Temporal analysis: range, gap detection, trend by month/year
  - Holistic EXPLORATORY_SUMMARY.md with flagged insights
  - Extracted all code from SKILL.md into `scripts/run_eda.py`; added `scripts/requirements.txt`
- **q-eda**: Replaced auto-classification with interview-driven column type confirmation — Claude previews dataset, presents classification table, users confirm before script runs
- **q-eda/run_eda.py**: Bug fixes — guard n=1, fix Float64 detection, clip binary CI, filter empty DataFrames, fix --no_excel message
- **q-scholar/SKILL.md**: Updated sub-skill name, description, and phase references
- **README**: Expanded installation docs — added Node.js prerequisite, plugin marketplace method, plugin install commands, natural language install, and structured update sections

## [1.4.6] - 2026-02-19

### Added

- **q-presentations**: Added example output slides (4-slide AI agents deck) to SKILL.md and README.md

## [1.4.5] - 2026-02-18

### Added

- **q-educator**: New course content development skill for university teaching workflows
  - Interview-driven planning process before drafting content
  - Deliverable templates for lecture outlines, demo outlines, follow-up emails, assignment prompts, and per-group feedback
  - Reference examples for assignment, demo, email, feedback, and lecture outputs
  - Reference Files section listing all 5 reference examples

### Changed

- **q-presentations**: Refactored workflow to use layout-driven overlay safety — added `primary_content_bias` + exceptions/fallback rules; updated outline and prompt templates
- **q-presentations**: Standardized slide merge pipeline to TypeScript only — removed Python merge script and `python-pptx` dependency

## [1.4.0] - 2026-02-16

### Added

- **q-presentations**: New skill for generating branded slide decks from content
  - Fork of baoyu-slide-deck with organic content positioning (v1→v3 lessons baked in)
  - 16 style presets + composable dimension system (texture, mood, typography, density)
  - Video-overlay-aware layout: content anchors away from specified overlay zone
  - Dr. Q logo branding with configurable placement and auto-invert for dark styles
  - Gemini 3.0 Pro image generation via Python script
  - PPTX and PDF export (Python + Bun/TS options)
  - Partial workflows: outline-only, prompts-only, images-only, regenerate specific slides
  - Organic Background Principle: concise one-liner specs prevent uneven Gemini backgrounds
  - 22 style files, 5 dimension files, 28 layout types, full reference documentation

## [1.3.0] - 2026-02-11

### Changed

- **q-intro**: Major update adding argumentative architecture principles and refinement mode
  - New **Argumentative Architecture** section codifying paragraph-level logic, cross-paragraph bridge patterns, and within-paragraph narrative flow
  - Expanded core principles from 6 to 11 (narrative arc, discipline-first grounding, theory-as-resolution, bridge architecture, RQ scope progression, concept precision)
  - New **Phase 4: Refinement Mode** with four-step diagnostic workflow (macro restructure, meso revise, micro tighten)
  - Dual-mode support: interview-based drafting from scratch and diagnostic refinement of existing drafts
  - Integrated tightening guidance into writing style (cut filler, compress clauses, eliminate redundancy)
  - Expanded quality checklist from 10 to 16 items
  - Updated interview protocol: venue-first ordering so disciplinary home anchors all decisions
  - Updated templates with architectural annotations explaining the logic behind each pattern
  - Literature template now uses narrative-arc pattern instead of disconnected-streams catalog
  - RQ template now uses scope-progression pattern (descriptive, relational, conditional)

## [1.2.2] - 2026-02-06

### Added

- **q-infographics**: Automatic logo branding on generated infographics
  - Logo overlay via Pillow post-processing (configurable filename, size, position)
  - Brand logo placed in bottom-right corner of every infographic
  - Added `assets/` folder with `Logo_Q.png`
  - Added Pillow dependency to requirements.txt
  - Updated SKILL.md with branding documentation and `.env` loading instructions

## [1.2.0] - 2026-02-05

### Added

- **q-scholar**: New academic manuscript writing suite that orchestrates sub-skills
  - Consolidated skill bundle for end-to-end manuscript preparation
  - Follows APA 7th edition formatting standards
  - Shared references for style guides and table formatting
  - q-intro: Introduction section drafting with interview-driven workflow
  - q-descriptive-analysis: Comprehensive exploratory data analysis
  - q-methods: Methods section drafting with appendix templates
  - q-results: Results section drafting with APA-compliant tables
- **q-intro**: New sub-skill for introduction sections
  - Interview-driven workflow (5-8 questions before drafting)
  - Six-component structure: hook, literature, context, RQs, contributions, roadmap
  - Template patterns for openings, gaps, questions, and contributions
  - Scope boundaries separating intro from literature review

### Changed

- Migrated standalone q-methods into q-scholar sub-skill
- Renamed q_descriptive-analysis to q-descriptive-analysis (hyphen convention)
- Moved q_descriptive-analysis into q-scholar sub-skill
- **q-methods**: Improved clarity and added scope boundaries
  - Added principle: keep methods strictly separate from results
  - New section clarifying what belongs in methods vs results (data summaries vs analysis findings)
  - Converted structure guidelines to flowing prose

### Removed

- Standalone q-methods skill (now part of q-scholar)
- Standalone q_descriptive-analysis skill (now part of q-scholar)

## [1.1.0] - 2026-02-02

### Added

- **q-infographics**: New skill for converting documents into business stories and infographics
  - Two-stage pipeline: Document → Story → Infographic
  - Powered by Gemini 3.0 Pro (google-genai SDK)
  - Business story style with "golden sentences" (36Kr/Huxiu format)
  - Hand-drawn cartoon-style infographics (16:9 aspect ratio)
  - Review checkpoints at each workflow stage
  - Organized folder structure: prompts/, scripts/, examples/
  - Supports PDF, DOCX, and text input via markitdown

## [1.0.1] - 2026-01-30

### Changed

- **q-topic-finetuning**: Marked Esports UGC plan generator as example reference and standardized input/output filenames
- **q-topic-finetuning**: Removed artifact output block and renamed backup file to topic_consolidation.md
- **q-topic-finetuning**: Updated outlier classification script to use template prompt and generic input/output names
- **q-topic-finetuning**: Updated example reference to reflect generic output filename

## [1.0.0] - 2025-01-29

### Added

- **q-methods**: Draft methods sections for academic manuscripts
- **q-topic-finetuning**: Consolidate topic modeling outputs into theory-driven frameworks
- **q_descriptive-analysis**: Comprehensive descriptive analysis of tabular datasets
- Initial README with installation instructions
- MIT License
