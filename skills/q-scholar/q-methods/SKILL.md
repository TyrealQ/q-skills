---
name: q-methods
description: Draft methods sections for academic manuscripts in narrative style with appendix cross-references. Use for writing methods, describing data collection, preprocessing, or computational analysis procedures.
---

# Q-Methods

Draft methods sections in clear narrative style for broad scholarly audiences.

## References

- **references/methods_template.md** — structural guidance (draft dynamically, not verbatim)
- **../references/appendix_template.md** — shared appendix structure (methods and results)
- **../references/apa_style_guide.md** — APA formatting, numbers, notation, formulas

## Core Principles

- Narrative prose; no bullet points, em-dashes, or standalone introductory paragraphs
- Prefer 3-12 sentence paragraphs; merge pre-table intros into post-table narrative
- Conceptual language; avoid implementation jargon ("Interview responses were organized by dimension" not "We filtered the DataFrame")
- Organize by logical workflow stages: data collection, preprocessing, analysis, validation
- Wrap all formulas and operator-heavy expressions in inline code backticks, in both prose and table cells (see ../references/apa_style_guide.md, "Equations, Formulas, and Set Notation")
- Strict methods/results separation: describe what was done and how, not what was found

## Section Architecture

The template describes what goes where; this section describes why each element appears where it does and how sections connect narratively.

### Data Collection and Preprocessing

Open by grounding the reader in the empirical scope — sample size, date range, breakdown by key variables. Describe preprocessing conceptually so the reader understands what was done to the data and why, without needing to see code or configuration. Technical parameters belong in the appendix; the main text explains the reasoning behind choices. End with a transition that motivates the analytical approach.

### Data Analysis

Open with a pipeline overview that tells the reader the full analytical arc before diving into components. Each method choice should be justified conceptually — why this method fits this research question — not merely named. Reference the appendix for technical details (hyperparameters, prompts, thresholds). The reader should understand the analytical logic without consulting the appendix.

### Validation

Describe human validation as a scholarly activity, not a mechanical procedure. Explain sampling rationale, coding protocols, and what the validation is designed to confirm. Leave placeholders for reliability metrics if pending, clearly marked for later completion.

## Appendix Strategy

The main text presents the analytical logic at a level accessible to the target audience; appendices provide the detail needed for reproducibility.

**General guidance (apply by default):** If a parameter is needed to understand the analytical logic, include it in the main text (sample size, key thresholds, model names). If it is needed to replicate the analysis but not to follow the argument, place it in an appendix (full configuration tables, system prompts, coding rubrics, preprocessing specifications). Cross-reference appendices at the point of first relevance: "Detailed parameters are provided in Appendix A." Use placeholders for pending contributions.

**Then ask the user to refine** the standard-vs-detail boundary for their study, since it is context-dependent. A consistency threshold may be a standard parameter in one study but require appendix-level justification in another.

## Workflow

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Gather context: sample, date range, key variables, analytical approach | — |
| 2 | Draft sections per structure above; use template as structural guide, not verbatim script | references/methods_template.md |
| 3 | Separate main text (logic) from appendix (reproducibility detail) | ../references/appendix_template.md |
| 4 | Ask user to refine the standard-vs-detail boundary | — |
| 5 | Tighten: apply Core Principles, ensure conceptual language throughout | ../references/apa_style_guide.md |

## Scope

**Include:** Sample and corpus descriptive overview, preprocessing procedures, analytical methods, validation protocols.

## Checklist

- [ ] Conceptual language throughout (no library names or code-level details in main text)
- [ ] Each workflow stage has appendix cross-references for technical parameters
- [ ] No analysis findings reported (reserved for results)
- [ ] Placeholders marked for pending contributions
- [ ] Appendix structure follows ../references/appendix_template.md
