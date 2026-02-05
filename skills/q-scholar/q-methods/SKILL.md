---
name: q-methods
description: Draft methods sections for academic manuscripts following a structured, narrative style. Use when the user needs to write or refine a methods section for research papers involving computational methods (machine learning, statistical modeling, text analysis, simulation, network analysis, image processing, or other computational approaches). Produces clear, accessible prose without em-dashes or bullet points, with appropriate appendix cross-references for technical details.
---

# Methods Section Drafting

This skill guides drafting of methods sections for academic manuscripts in a clear, narrative style suitable for broad scholarly audiences.

## Core Principles

1. Write in flowing paragraphs without bullet points or em-dashes
2. Use conceptual language; minimize technical jargon in main text
3. Organize by logical workflow stages: data collection, preprocessing, analysis, validation
4. Reference appendices for implementation details and technical parameters
5. Include placeholders where coauthor contributions are pending
6. Keep methods strictly separate from results: describe what was done and how, not what was found

## Scope Boundaries

The methods section describes procedures and summarizes the data collected, but does not report analysis findings.

**Include in methods:**
- Sample size, date range, and demographic breakdown of collected data
- Descriptive overview of the corpus (e.g., total documents, distribution across categories)
- Preprocessing steps and resulting dataset dimensions
- Analytical procedures and validation protocols

**Reserve for results:**
- Statistical findings and effect sizes
- Pattern discoveries and thematic outcomes
- Comparative analyses between groups
- Any interpretation of what the data reveals

## Standard Structure

### Data Collection and Preprocessing

Describe sampling strategy, recruitment procedures, and data sources. If details are pending from coauthors, mark with explicit placeholders. Present preprocessing at a conceptual level without code-specific language, and reference the appendix for technical parameters and library specifications.

Include a summary of the collected data: total sample size, date range, and breakdown by key variables. This descriptive overview establishes what was gathered before the analysis, distinct from reporting what the analysis found.

### Data Analysis

Open with a brief pipeline overview that establishes the analytical approach. Organize by analytical stages (e.g., topic modeling, classification, validation). For each stage, justify the method choice, describe key parameters conceptually, and reference the appendix for technical details.

### Validation

Describe the human validation sampling strategy and coding procedures. Leave placeholders for reliability metrics (e.g., Cohen's kappa, percent agreement) if not yet available.

## Writing Style

Avoid implementation language like "importing Python libraries" or "using pandas for data manipulation." Write conceptually: "Interview responses were organized by dimension" rather than "We filtered the DataFrame by question type."

Use hyphens for compound modifiers (e.g., "high-confidence classifications"). Never use em-dashes. Spell out numbers below ten unless they represent measurements, statistics, or technical values.

When referencing appendix sections: "Detailed parameters are provided in Appendix A" or "The complete system prompt is documented in Appendix E."

## Reference Files

- references/methods_template.md: Complete section template with placeholders
- references/appendix_template.md: Companion appendix structure
