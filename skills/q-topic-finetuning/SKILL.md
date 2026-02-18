---
name: q-topic-finetuning
description: "Fine-tune and consolidate topic modeling outputs (BERTopic, LDA, etc.) into a theory-driven classification framework for academic manuscripts. Use when processing topic modeling results that need topic consolidation, theoretical classification, domain-specific preservation, multi-category handling, data verification, or Excel updates with final labels."
---

# Q-Topic-Finetuning

Fine-tune topic modeling outputs into consolidated, theory-driven topic frameworks for academic manuscripts.

## Folder Structure

```
q-topic-finetuning/
├── SKILL.md                                  # This file
├── scripts/
│   ├── classify_outliers.py                  # Outlier reclassification via Gemini
│   ├── generate_implementation_plan.py       # Full plan generation
│   └── update_excel_with_labels.py           # Excel column updates
└── references/
    ├── esports_ugc_example.md                # Worked example
    └── SP_OUTLIER_TEMPLATE.txt               # Outlier classification prompt template
```

## When to Use

- Converting raw topic model outputs (BERTopic, LDA, NMF) into manuscript-ready categories
- Applying theoretical frameworks (legitimacy, stakeholder theory, etc.) to topic clusters
- Consolidating 50+ topics into 20-50 theoretically meaningful groups
- Preserving domain-specific distinctions (by entity, event, geography, time)
- Creating reproducible Excel outputs with classification labels

## Workflow Overview

```
Source Data (Topic Model Excel) 
    |
    v
1. Load & Analyze Topics --> identify overlaps, unassigned
    |
    v
2. Define Final Topic Structure --> FINAL_TOPICS dictionary
    |
    v
3. Apply Theoretical Framework --> classify each topic
    |
    v
4. Generate Implementation Plan (MD)
    |
    v
5. Update Source Data with Labels (Excel)
```

## Core Principles

### Preservation Rules (Customize per Domain)
Identify what should NEVER be merged based on theoretical importance:
- **Entity-specific**: Different companies, teams, people
- **Event-specific**: Different conferences, tournaments, time periods
- **Geography-specific**: Different countries, regions
- **Stakeholder-specific**: Different actor perspectives

### Theoretical Framework (Template)
Replace with your relevant framework:

| Type | Description | Example Topics |
|------|-------------|----------------|
| **Category A** | Definition | Topics fitting A |
| **Category B** | Definition | Topics fitting B |
| **Category C** | Definition | Topics fitting C |
| **Cross-cutting** | Spans multiple | Topics by entity/domain |

**Example: Legitimacy Framework (Suchman, 1995)**
- Cognitive: Institutional recognition, taken-for-granted status
- Pragmatic: Direct stakeholder benefits, practical interests
- Moral: Normative evaluation, values alignment

### Multi-Category Topics
Some topics belong to multiple categories:
- Track explicitly in assignments dictionary
- Calculate overlap for reconciliation
- Display as semicolon-separated: "Category A; Cross-cutting"

## Required Inputs

1. **Topic model output** (Excel/CSV)
   - Columns: Topic ID, Count, Name/Label, Keywords, Representative_Docs (optional)

2. **Merge recommendations** (optional)
   - Sheets: MERGE_GROUPS, INDEPENDENT_TOPICS

3. **Document data** (for label updates)
   - Contains individual documents with Topic ID column

## Key Code Patterns

### Pattern 1: Final Topic Definition

```python
FINAL_TOPICS = {
    'A1': {
        'label': 'Descriptive Label for Topic',
        'theme': 'Category-Subcategory',  # e.g., 'Pragmatic-Fan'
        'sources': [8, 12, 45]  # Original topic IDs to merge
    },
    'A2': {
        'label': 'Another Topic Label',
        'theme': 'Category-Subcategory',
        'sources': [3, 17, 33]
    },
    # Topics can appear in multiple final topics for multi-category
}
```

### Pattern 2: Assignment Mapping

```python
assignments = {}
for code, data in FINAL_TOPICS.items():
    for tid in data['sources']:
        if tid not in assignments:
            assignments[tid] = []
        assignments[tid].append((code, data['theme']))

# Find multi-category topics
multi_cat = {tid: assigns for tid, assigns in assignments.items() 
             if len(assigns) > 1}
```

### Pattern 3: Overlap Calculation

```python
total_overlap = sum(
    topics[tid]['count'] * (len(assigns) - 1)
    for tid, assigns in assignments.items()
    if len(assigns) > 1
)

# Verification: non_outlier_docs + total_overlap = table1_total
```

### Pattern 4: Excel Label Update

```python
TOPIC_MAPPING = {
    0: [('A1', 'Category')],
    1: [('A2', 'Category')],
    4: [('B1', 'Category A'), ('C1', 'Cross-cutting')],  # Multi-category
    # ... all topic IDs
}

def get_themes(topic_id):
    if topic_id in TOPIC_MAPPING:
        themes = list(set([m[1] for m in TOPIC_MAPPING[topic_id]]))
        return '; '.join(themes)
    return 'Unknown'

df['Final_Topic_Code'] = df['Topic'].apply(get_final_codes)
df['Final_Topic_Label'] = df['Topic'].apply(get_final_labels)
df['Category_Theme'] = df['Topic'].apply(get_themes)
```

## Handling Common Requests

| User Request | Action |
|--------------|--------|
| "Preserve X separately" | Add as independent topic code |
| "Merge these topics" | Combine source IDs into single code |
| "Exact counts please" | Replace ~ approximations with computed totals |
| "Integrate into tables" | Remove standalone sections, embed in category tables |
| "Count mismatch?" | Explain multi-category overlap, show reconciliation |
| "Keep original style" | Preserve existing template structure when updating |

## Script Templates

See `scripts/` for reference implementations:
- `generate_implementation_plan.py` - Full plan generation
- `update_excel_with_labels.py` - Excel column updates

Adapt these scripts by:
1. Updating FINAL_TOPICS with your topic structure
2. Replacing FINAL_LABELS with your labels
3. Modifying theme categories to match your framework

## Verification Checklist

- [ ] All non-outlier topics assigned to at least one category
- [ ] Multi-category topics explicitly tracked
- [ ] Overlap reconciliation verified
- [ ] Domain-specific topics preserved separately
- [ ] Category subtotals match grand total
- [ ] Output file has new classification columns

## Outlier Classification (Foundation Model)

For datasets with significant noise or unclustered documents (Topic = -1), use the `classify_outliers.py` script to reclassify them using a Gemini foundation model.

### Workflow
1. **Prepare Prompt**: Create a system prompt listing all valid finalized topics + descriptions. See `references/SP_OUTLIER_TEMPLATE.txt`.
2. **Configure Script**: Update `valid_topics` and file paths in `scripts/classify_outliers.py`.
3. **Run Classification**:
   ```bash
   # Default uses GEMINI_MODEL env var or standard Flash model
   python scripts/classify_outliers.py
   
   # Or specify a model version
   python scripts/classify_outliers.py --model gemini-3-flash-preview
   ```
   - Uses Google Gemini Foundation Models (supports Flash, Pro, etc.)
   - Auto-retries invalid outputs
   - Updates `Final_Topic_Label`, `classification_confidence`, and `key_phrases` columns

### When to Use
- You have >10% outlier documents (Topic -1)
- You have a stable final topic list (from Table 1)
- You want to "clean up" the dataset for final analysis
