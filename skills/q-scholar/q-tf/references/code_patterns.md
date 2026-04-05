# Key Code Patterns

## Pattern 1: Final Topic Definition

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

## Pattern 2: Assignment Mapping

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

## Pattern 3: Overlap Calculation

```python
total_overlap = sum(
    topics[tid]['count'] * (len(assigns) - 1)
    for tid, assigns in assignments.items()
    if len(assigns) > 1
)

# Verification: non_outlier_docs + total_overlap = table1_total
```

## Pattern 4: Excel Label Update

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
