# Changelog

All notable changes to this project will be documented in this file.

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
