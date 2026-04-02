---
name: q-results
description: Draft results sections for academic manuscripts with APA 7th tables and narrative flow. Use for writing results, presenting findings, formatting statistical tables, or reporting quantitative analysis.
---

# Q-Results

Draft results sections following APA 7th edition standards with narrative flow and properly formatted tables.

## References

- **references/results_template.md** — structural guidance (draft dynamically, not verbatim)
- **../references/appendix_template.md** — shared appendix structure (methods and results)
- **../references/apa_style_guide.md** — APA formatting, numbers, notation, formulas
- **../references/table_formatting.md** — APA 7th table structure and examples

## Core Principles

- Narrative prose; no bullet points, em-dashes, or standalone introductory paragraphs
- Prefer 3-12 sentence paragraphs; merge pre-table intros into post-table narrative
- Organize by research questions or analytical stages, not by statistical test
- Tables support the narrative, not replace it
- Report findings objectively without interpretation (save for discussion)
- No unnecessary bold or italic emphasis in running text
- Wrap all formulas and operator-heavy expressions in inline code backticks, in both prose and table cells (see ../references/apa_style_guide.md, "Equations, Formulas, and Set Notation")
- Focus the main text on core findings that directly address the research questions; move peripheral, supplementary, or exhaustive detail to appendices

## Section Architecture

The template describes what goes where; this section describes why each element appears where it does and how findings build narratively.

### Opening Overview

Orient the reader to the full analytical landscape before presenting specific findings. Summarize what analyses were conducted, how the section is organized, and what the reader should expect. This paragraph earns the reader's attention by previewing the story the data tells.

### Results by Research Question

Organize by research question, not by statistical test — the reader follows the argument, not the toolchain. For each RQ: state what was analyzed, present key findings with statistics, reference supporting tables, and transition to the next RQ by connecting what was just found to what comes next. Tables support the narrative but do not replace it; every table should be introduced before it appears and interpreted after. Summarize patterns rather than exhaustively listing every result.

### Summary

Brief synthesis of key findings without interpretation. Connect the findings back to the research questions. Do not introduce new results or offer theoretical explanations — those belong in the discussion.

## Workflow

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Identify research questions and corresponding analyses | — |
| 2 | Draft sections organized by RQ, not by statistical test; use template as structural guide, not verbatim script | references/results_template.md |
| 3 | Format tables per APA 7th | ../references/table_formatting.md |
| 4 | Separate core findings (main text) from peripheral detail (appendix) | ../references/appendix_template.md |
| 5 | Ask user to refine the core-vs-peripheral boundary | — |
| 6 | Tighten: apply Core Principles, ensure no interpretation beyond connectors | ../references/apa_style_guide.md |

## Appendix Strategy

The main text tells the story of the findings; appendices provide the evidence trail for verification and reproducibility.

**Core results (main text):** Findings that directly answer the research questions, including the key tables and statistics needed to follow the narrative. Present only the most informative tables inline; summarize patterns rather than exhaustively listing every pathway, configuration, or subgroup.

**Peripheral results (appendices):** Complete truth tables, full solution tables with all equivalent models, exhaustive cross-tabulations, detailed robustness checks, sensitivity analyses, and supplementary breakdowns by subgroup or condition. Reference these at the point of relevance: "complete results in Table A4" or "detailed breakdowns are available in Appendix B."

**When to move results to an appendix:**
- The detail supports but does not drive the narrative (e.g., full truth tables behind a summarized solution)
- The table has more rows or columns than the reader needs to follow the argument
- The finding confirms rather than advances the story (e.g., robustness checks, alternative specifications)
- Multiple equivalent models or sensitivity tests produce similar conclusions

**Then ask the user to refine** the core-vs-peripheral boundary for their study, since it is context-dependent. What counts as a core table in one analysis may be appendix material in another depending on the research questions and audience.

## Scope

**Include:** Statistical findings, pattern discoveries, comparative analyses, distribution results. **Reserve:** Theoretical interpretation, implications, causal explanations (discussion).

## Checklist

- [ ] Tables referenced before they appear; formatted per ../references/table_formatting.md
- [ ] No interpretation beyond observational connectors ("consistent with," "suggesting")
- [ ] Statistics formatted per ../references/apa_style_guide.md (italicized symbols, no leading zeros on bounded values)
- [ ] Core findings in main text; peripheral detail in appendices with cross-references
- [ ] Appendix cross-references at point of first relevance
