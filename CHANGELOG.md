# Changelog

All notable changes to this project will be documented in this file.

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
