---
name: q-tf
description: Consolidate topic modeling outputs (BERTopic, LDA, NMF) into theory-driven classification frameworks. Use for topic finetuning, topic consolidation, reclassification, outlier handling, or updating Excel labels from topic models.
---

# Q-TF

Fine-tune topic modeling outputs into consolidated, theory-driven topic frameworks for academic manuscripts.

> **If in plan mode:** write a brief plan — *"Run q-tf skill: load topic model output,
> define final topic structure with theoretical framework, generate implementation plan,
> update Excel with labels."* — then exit plan mode immediately.
> Do NOT attempt topic analysis, script execution, or Excel updates while plan mode is active.

## Script Directory
Agent execution instructions:
1. Determine this SKILL.md file's directory path as `SKILL_DIR`.
2. Script path = `${SKILL_DIR}/scripts/<script-name>`.
3. Reference path = `${SKILL_DIR}/references/<ref-name>`.

## Dependencies
```
pandas
openpyxl          # required for .xlsx input/output
google-genai      # required for outlier classification via Gemini
```
Install: `pip install pandas openpyxl google-genai`

**Environment variables:** `GEMINI_API_KEY` (for outlier classification only), `GEMINI_MODEL` (optional model override).

## References
- **references/preservation_rules.md** — domain preservation rules, theoretical framework template, multi-category handling
- **references/code_patterns.md** — four Python patterns: topic definition, assignment mapping, overlap calculation, Excel update
- **references/outlier_workflow.md** — foundation model outlier classification workflow
- **references/esports_ugc_example.md** — worked example
- **references/SP_OUTLIER_TEMPLATE.txt** — outlier classification prompt template

## Core Principles
- Preserve domain-specific distinctions (entity, event, geography, stakeholder) — see references/preservation_rules.md
- Theory-driven classification using a customizable framework template
- Track multi-category topics explicitly; calculate overlap for reconciliation
- All non-outlier topics must be assigned to at least one category

## Workflow

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Load & analyze topics — identify overlaps, unassigned | — |
| 2 | Define final topic structure (FINAL_TOPICS dictionary) | references/code_patterns.md |
| 3 | Apply theoretical framework — classify each topic | references/preservation_rules.md |
| 4 | Generate implementation plan (MD) | `scripts/generate_implementation_plan.py` |
| 5 | Update source data with labels (Excel) | `scripts/update_excel_with_labels.py` |
| 6 | Reclassify outliers via foundation model | references/outlier_workflow.md |

## Required Inputs
1. **Topic model output** (Excel/CSV) — Topic ID, Count, Name/Label, Keywords, Representative_Docs (optional)
2. **Merge recommendations** (optional) — Sheets: MERGE_GROUPS, INDEPENDENT_TOPICS
3. **Document data** (for label updates) — individual documents with Topic ID column

## Script Invocation

```bash
python "${SKILL_DIR}/scripts/generate_implementation_plan.py" --input topic_model_output.xlsx --output implementation_plan.md
python "${SKILL_DIR}/scripts/update_excel_with_labels.py" --input document_data.xlsx --output document_data_labeled.xlsx
```
Adapt scripts by updating FINAL_TOPICS, FINAL_LABELS, and theme categories. See references/code_patterns.md. For a worked example, see references/esports_ugc_example.md.

## Expected Outputs
| Output | Description |
|--------|-------------|
| `implementation_plan.md` | Full classification plan with topic mappings and reconciliation |
| `*_labeled.xlsx` | Source data with `Final_Topic_Code`, `Final_Topic_Label`, `Category_Theme` columns |
| Outlier results (optional) | Updated `Final_Topic_Label`, `classification_confidence`, `key_phrases` columns |

## Scope
**Include:** Topic consolidation, theoretical classification, Excel label updates, outlier reclassification.
**Exclude:** Topic modeling itself (BERTopic/LDA/NMF execution), visualization, statistical analysis.

## Checklist
- [ ] All non-outlier topics assigned to at least one category
- [ ] Multi-category topics explicitly tracked
- [ ] Overlap reconciliation verified
- [ ] Domain-specific topics preserved separately
- [ ] Category subtotals match grand total
- [ ] Output file has new classification columns
