# Changelog

All notable changes to this project will be documented in this file.

## [1.5.3] - 2026-02-22

### Fixed
- **q-exploratory-analysis/SKILL.md**: Resolved contradictory section omission rules (line 159 "state No data" vs line 160 "omit entirely")
  - New two-tier rule: all source CSVs absent → omit section; some absent → include section with note
- **q-exploratory-analysis/SKILL.md**: Fixed unreadable 22-24 column descriptive tables in summary
  - Split into core table (8 cols: variable, N_valid, M, Mdn, SD, IQR, Skewness, Kurtosis) and detail table (11 cols: Range, Min, Max, Q1/Q3, CV, SE, CI, outliers)
  - Narrow CSVs (frequencies, binary, correlations, crosstabs) keep full columns as-is
- **q-exploratory-analysis/SKILL.md**: Replaced vague flagging severity scheme with explicit thresholds
  - Missing >10%, skewness abs>2, kurtosis abs>7, correlation abs>0.7, CV >100%, ID-like >95% uniqueness
- **q-exploratory-analysis/SKILL.md**: Fixed ordinal variables misplaced under "Categorical Variables" section
  - Restructured from 10 thematic sections to 13 measurement-level sections (Nominal, Binary, Ordinal, Discrete, Continuous each separate)
- **q-exploratory-analysis/SKILL.md**: Fixed temporal data referenced in two sections without scope guidance
  - Section 1 (Dataset Overview): temporal range and period count only
  - Section 12 (Temporal Trends): full trend table and pattern interpretation
- **q-exploratory-analysis/SKILL.md**: Fixed output directory listing order (summary now last as final deliverable)

### Added
- **q-exploratory-analysis/SKILL.md**: Table sizing rules for frequency, correlation, and cross-tab tables
- **q-exploratory-analysis/SKILL.md**: Two new verification checklist items (13-section count, split-table format)
- **q-exploratory-analysis/references/summary_template.md**: Reference template with 13-section skeleton and worked example rows per table type

### Changed
- **README**: Updated q-exploratory-analysis folder structure to include `references/` directory

## [1.5.2] - 2026-02-22

### Changed
- **q-exploratory-analysis/run_eda.py**: Consolidated 4 type-override flags (`--ordinal_cols`, `--text_cols`, `--continuous_cols`, `--id_cols`) into single `--col_types col=type` pairs
- **q-exploratory-analysis/run_eda.py**: Inverted `--no_interactive` to `--interactive` (non-interactive is now the default)
- **q-exploratory-analysis/run_eda.py**: Renamed Phase 7 (Excel Report) to Phase 6 to match actual pipeline order
- **q-exploratory-analysis/SKILL.md**: Removed duplicate mapping tables from Sections 1 and 2; single arguments table remains
- **q-exploratory-analysis/SKILL.md**: Reordered Section 4 so script phases (0-6) come first, Claude's narrative summary is Post-Script
- **q-exploratory-analysis/SKILL.md**: Removed stale `DESCRIPTIVE_SUMMARY.md` style reference and incorrect "chi-square" claim (script does cross-tabulation)
- **q-exploratory-analysis/SKILL.md**: Trimmed verification checklist to remove items restating script runtime behavior
- **q-scholar/SKILL.md**: Updated "seven-phase" references to "six-phase"

## [1.5.1] - 2026-02-22

### Fixed
- **q-exploratory-analysis/run_eda.py**: Fixed ID heuristic misclassifying numeric metrics
  - High-cardinality numeric columns (e.g., views, revenue) now classified as Continuous, not ID
  - Added dtype guard: only non-numeric columns with >95% uniqueness are treated as identifiers
- **q-exploratory-analysis/run_eda.py**: Pearson correlation now includes both Continuous and Discrete columns
  - Previously only used Continuous columns, producing empty correlations when all numeric columns were Discrete
- **q-exploratory-analysis/run_eda.py**: Added `--continuous_cols` and `--id_cols` CLI flags
  - Users can force-classify columns as continuous or ID, overriding auto-detection

### Changed
- **q-exploratory-analysis/SKILL.md**: Strengthened interview workflow (Stage B)
  - Added high-cardinality numeric awareness (views, revenue should be Continuous, not ID)
  - Added mandatory "invoke the script immediately" step to prevent inline Python
  - Updated argument mapping table with `--continuous_cols` and `--id_cols`
- **q-exploratory-analysis/SKILL.md**: Mandated source-file citations in EXPLORATORY_SUMMARY.md
  - Every section heading must include `Source:` annotation citing CSV file(s)
  - Explicitly forbids ad-hoc Python for deriving findings
  - Sections with missing source CSVs should be omitted entirely
- **q-exploratory-analysis/SKILL.md**: Added Windows `python` compatibility note
- **q-exploratory-analysis/SKILL.md**: Updated Column-Type Coverage table
  - ID detection rule now specifies "AND non-numeric dtype"
  - Continuous detection rule now includes "OR numeric dtype with nunique > 95%"
  - Added numeric high-uniqueness explanation note
- **q-exploratory-analysis/SKILL.md**: Expanded verification checklist with 5 new items

## [1.5.0] - 2026-02-21

### Changed
- **q-exploratory-analysis**: Replaced auto-classification with interview-driven column type confirmation
  - Claude now previews the dataset and presents a classification table with suggested types for user review
  - Two-stage interview: context questions (research goals, temporal column) then column classification review
  - Users confirm or correct all column types before the script runs
  - All confirmed types mapped to CLI flags (`--ordinal_cols`, `--text_cols`, `--group`); `--no_interactive` always used
- **q-exploratory-analysis/run_eda.py**: Bug fixes (no workflow changes)
  - Guard `quantitative_summary` for n=1 (was producing NaN-heavy rows)
  - Fix nullable Float64 detection (`float.is_integer` → modulo check)
  - Clip binary CI to [0, 1] (Wald interval could exceed bounds)
  - Filter empty DataFrames before `pd.concat` in grouped analysis
  - Remove redundant quantile computation
  - Fix "Done" message when `--no_excel` is passed
- **q-scholar/SKILL.md**: Updated q-exploratory-analysis description, Phase 1 bullets, and phase count references
- **README**: Updated sub-skill table description to reference user-confirmed column types

## [1.4.9] - 2026-02-21

### Changed
- **q-scholar**: Renamed sub-skill `q-descriptive-analysis` to `q-exploratory-analysis` to reflect broader exploratory intent
- **q-exploratory-analysis**: Complete redesign around Stevens' levels of measurement (Nominal, Ordinal, Discrete, Continuous, Temporal, Text, ID/key)
  - Auto-detects column measurement level; flags ambiguous integers (e.g., Likert scales) for interactive user confirmation
  - Six-phase pipeline: Dataset Profile, Data Quality, Univariate, Bivariate/Multivariate, Specialized, Summary Report
  - Measurement-appropriate bivariate analysis: Pearson for Continuous x Continuous, Spearman for Ordinal x Ordinal, grouped descriptives for Continuous/Discrete x Nominal, contingency tables for Nominal x Nominal
  - Full APA-compatible quantitative metrics (M, Mdn, SD, Variance, IQR, CV, SE, 95% CI, skewness, kurtosis, outlier counts) for Ordinal, Discrete, and Continuous columns
  - Ordinal mean labeled as M (quasi-interval) in all outputs
  - Binary variable analysis with proportion and 95% CI (normal approximation)
  - Text analysis: top unigrams/bigrams, vocab size, avg word count (built-in EN stopword list)
  - Temporal analysis: range, gap detection, trend by month/year
  - Holistic EXPLORATORY_SUMMARY.md with flagged insights (missing data, distribution shape, strong correlations, coverage)
  - Extracted all code from SKILL.md inline blocks into `scripts/run_eda.py` (self-contained, runnable)
  - Added `scripts/requirements.txt` with pinned dependencies
- **README**: Updated sub-skill name and folder structure diagram
- **q-scholar/SKILL.md**: Updated sub-skill name, description, folder diagram, and all cross-references

## [1.4.8] - 2026-02-21

### Added
- **`.claude-plugin/marketplace.json`**: Enables `/plugin marketplace add TyrealQ/q-skills` and `/plugin install <skill>@q-skills` commands in Claude Code — each skill registered as a named plugin

### Changed
- **README**: Broadened tagline from "academic research workflows" to reflect full collection scope (academic writing, data analysis, teaching, research communication)

## [1.4.7] - 2026-02-21

### Changed
- **README**: Expanded installation and update documentation
  - Added Node.js to Prerequisites (required for `npx`-based install)
  - Added `/plugin marketplace add` method for registering as a plugin marketplace
  - Added `/plugin install` commands for installing individual skills by name
  - Added "Ask the Agent" natural language install method
  - Renamed "Alternative: Clone and Copy" to "Manual: Clone and Copy" for clarity
  - Replaced flat Update Skills section with three sub-sections: Via Plugin UI (with auto-update note), Force Reinstall, and Manual Update

## [1.4.6] - 2026-02-19

### Added
- **q-presentations**: Added example output slides (4-slide AI agents deck) to SKILL.md and README.md
- **q-presentations**: Added `examples/` directory to README folder structure tree

## [1.4.5] - 2026-02-18

### Changed
- **All skills**: Standardized H1 titles to skill name only (`# Q-[Name]`) — removed subtitles and colons from all 9 SKILL.md files for uniform formatting

## [1.4.4] - 2026-02-18

### Changed
- **q-presentations**: Corrected H1 title capitalization to `# Q-Presentations: AI-Powered Slide Deck Generator`
- **q-educator**: Removed 11 `---` horizontal rule dividers between sections; header hierarchy provides sufficient structure
- **q-educator**: Added `## Reference Files` section listing all 5 reference examples
- **q-infographics**: Added "Use when…" trigger phrase to frontmatter description
- **q-infographics**: Replaced informal ASCII-arrow opening line with a proper sentence
- **q-scholar**: Renamed `## Directory Structure` to `## Folder Structure` for consistency with other skills

## [1.4.3] - 2026-02-18

### Added
- **q-educator**: New course content development skill for university teaching workflows
  - Interview-driven planning process before drafting content
  - Deliverable templates for lecture outlines, demo outlines, follow-up emails, assignment prompts, and per-group feedback
  - Reference examples for assignment, demo, email, feedback, and lecture outputs

### Changed
- **README/CLAUDE docs**: Added `q-educator` to skill listings and repository structure
- **README**: Synchronized `q-presentations` wording with layout-driven overlay safety and removed stale organic-positioning reference

## [1.4.2] - 2026-02-18

### Changed
- **q-presentations**: Refactored workflow to use layout-driven overlay safety
  - Removed organic-positioning guidance and related reference file
  - Added `primary_content_bias` + exceptions/fallback rules in `references/layouts.md`
  - Updated outline and prompt templates to enforce internal overlay-safe layout selection
  - Clarified `video_overlay` semantics in preferences schema (internal layout logic, not explicit prompt text)

- **q-presentations**: Standardized slide merge pipeline to TypeScript only
  - Removed `scripts/merge_slides.py` (Python PPTX merge)
  - Updated skill docs and README to Bun/TS merge flow
  - Removed `python-pptx` dependency from `skills/q-presentations/requirements.txt`

## [1.4.1] - 2026-02-16

### Fixed
- **q-infographics**: Removed `allowed-tools` from SKILL.md frontmatter to match standard format (name + description only)

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
- **q-topic-finetuning**: Added folder structure diagram to SKILL.md and README.md
- Added folder structure diagrams for all skills in README.md

### Fixed
- **q-descriptive-analysis**: Fixed skill name from `q_descriptive-analysis` to `q-descriptive-analysis` in YAML frontmatter
- **q-topic-finetuning**: Fixed title to use hyphenated format (`Q-Topic-Finetuning`)

## [1.2.1] - 2026-02-06

### Added
- **q-infographics**: Automatic logo branding on generated infographics
  - Logo overlay via Pillow post-processing (configurable filename, size, position)
  - Brand logo placed in bottom-right corner of every infographic
  - Added `assets/` folder with `Logo_Q.png`
  - Added Pillow dependency to requirements.txt
  - Updated SKILL.md and README.md with branding documentation and `.env` loading instructions

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
