---
name: q-methods
description: Draft methods sections for academic manuscripts in narrative style with appendix cross-references. Use for writing methods, describing data collection, preprocessing, or computational analysis procedures.
---

# Q-Methods

Draft methods sections in clear narrative style for broad scholarly audiences.

## References

- **references/methods_template.md** — section template with placeholders
- **references/appendix_template.md** — companion appendix structure
- **../references/apa_style_guide.md** — APA formatting, numbers, notation, formulas

## Core Principles

- Narrative prose; no bullet points, em-dashes, or standalone introductory paragraphs
- Prefer 3-12 sentence paragraphs; merge pre-table intros into post-table narrative
- Conceptual language; avoid implementation jargon ("Interview responses were organized by dimension" not "We filtered the DataFrame")
- Organize by logical workflow stages: data collection, preprocessing, analysis, validation
- Wrap all formulas and operator-heavy expressions in inline code backticks, in both prose and table cells (see ../references/apa_style_guide.md, "Equations, Formulas, and Set Notation")
- Strict methods/results separation: describe what was done and how, not what was found

## Section Structure

### Data Collection and Preprocessing

Summarize sample size, date range, and breakdown by key variables. Describe preprocessing conceptually; reference appendix for technical parameters.

### Data Analysis

Open with a pipeline overview. Justify method choices conceptually and reference appendix for technical details.

### Validation

Describe human validation sampling and coding procedures. Leave placeholders for reliability metrics if pending.

## Appendix Strategy

The main text presents the analytical logic at a level accessible to the target audience; appendices provide the detail needed for reproducibility.

**General guidance (apply by default):** If a parameter is needed to understand the analytical logic, include it in the main text (sample size, key thresholds, model names). If it is needed to replicate the analysis but not to follow the argument, place it in an appendix (full configuration tables, system prompts, coding rubrics, preprocessing specifications). Cross-reference appendices at the point of first relevance: "Detailed parameters are provided in Appendix A." Use placeholders for pending contributions.

**Then ask the user to refine** the standard-vs-detail boundary for their study, since it is context-dependent. A consistency threshold may be a standard parameter in one study but require appendix-level justification in another.

## Scope

**Include:** Sample and corpus descriptive overview, preprocessing procedures, analytical methods, validation protocols.

## Checklist

- [ ] Conceptual language throughout (no library names or code-level details in main text)
- [ ] Each workflow stage has appendix cross-references for technical parameters
- [ ] No analysis findings reported (reserved for results)
- [ ] Placeholders marked for pending contributions
- [ ] Appendix structure follows references/appendix_template.md
