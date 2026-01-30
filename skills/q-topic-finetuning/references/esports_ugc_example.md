# Esports UGC Example

This reference shows a complete example of the q-topic-finetuning workflow applied to esports user-generated content with a legitimacy framework classification.

## Context

- **Domain**: Esports social media discourse (Weibo)
- **Source Topics**: 129 BERTopic topics
- **Final Topics**: 58 consolidated categories
- **Theoretical Framework**: Organizational Legitimacy (Suchman, 1995)
  - Cognitive: Institutional recognition
  - Pragmatic: Stakeholder benefits
  - Moral: Normative evaluation
- **Preservation Rules**: Game-specific (LoL, HoK, MLBB, etc.), event-specific (Asian Games vs EWC)

## Final Topic Structure Example

```python
FINAL_TOPICS = {
    # COGNITIVE (Institutional Recognition)
    'C1': {'label': 'Hangzhou Asian Games: Esports as Official Sport', 'theme': 'Cognitive', 'sources': [8]},
    'C2': {'label': 'Asian Games National Team Selection Process', 'theme': 'Cognitive', 'sources': [46, 72, 88]},
    'C3': {'label': 'Esports World Cup (EWC) as Premier Global Event', 'theme': 'Cognitive', 'sources': [1, 3, 17, 32, 33, 71, 103, 110]},
    
    # PRAGMATIC (Stakeholder Benefits)
    'P1': {'label': 'Yinuo Wins EWC FMVP', 'theme': 'Pragmatic-Results', 'sources': [13]},
    'P12': {'label': 'LGD/Hua Aotian EWC Fan Hype', 'theme': 'Pragmatic-Fan', 'sources': [2, 5, 30, 37, 38, ...]},
    
    # MORAL (Normative Evaluation)
    'M1': {'label': 'JackeyLove Withdrawal Controversy', 'theme': 'Moral', 'sources': [4]},
    'M2': {'label': 'Jiuwei Roster Exclusion Controversy', 'theme': 'Moral', 'sources': [9, 26, 85, 108]},
    
    # GAME-SPECIFIC (Cross-cutting)
    'G7': {'label': 'League of Legends at Asian Games & EWC', 'theme': 'Game-Specific', 'sources': [4, 11, 40, 72, 83, 119]},
}
```

## Topic Mapping Example

```python
TOPIC_MAPPING = {
    -1: [('Outlier', 'Outlier')],  # Keep outlier separate
    0: [('P18', 'Pragmatic-Fan')],
    1: [('C3', 'Cognitive')],
    4: [('M1', 'Moral'), ('G7', 'Game-Specific')],  # Multi-category
    11: [('P22', 'Pragmatic-Team'), ('G7', 'Game-Specific')],  # Multi-category
    # ... all 129 topics mapped
}
```

## Results Summary

| Category | Topics | Documents |
|----------|--------|-----------|
| Cognitive | 9 | 17,908 |
| Pragmatic | 34 | 56,119 |
| Moral | 7 | 10,904 |
| Game-Specific | 9 | 12,467 |
| **Total** | **58** | **97,398** |

Multi-category overlap: 13 topics, 7,377 documents

## Files Generated

1. `implementation_plan.md` - Complete consolidation plan
2. `output_with_labels.xlsx` - Updated with columns:
   - Final_Topic_Code
   - Final_Topic_Label
   - Legitimacy_Theme
