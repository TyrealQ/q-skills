# Outlier Classification (Foundation Model)

For datasets with significant noise or unclustered documents (Topic = -1), use the `classify_outliers.py` script to reclassify them using a Gemini foundation model.

### Workflow
1. **Prepare Prompt**: Create a system prompt listing all valid finalized topics + descriptions. See `${SKILL_DIR}/references/SP_OUTLIER_TEMPLATE.txt`.
2. **Configure Script**: Update `valid_topics` and file paths in `${SKILL_DIR}/scripts/classify_outliers.py`.
3. **Run Classification**:
   ```bash
   # Default uses GEMINI_MODEL env var or standard Flash model
   python "${SKILL_DIR}/scripts/classify_outliers.py"

   # Or specify a model version
   python "${SKILL_DIR}/scripts/classify_outliers.py" --model gemini-3-flash-preview
   ```
   - Uses Google Gemini Foundation Models (supports Flash, Pro, etc.)
   - Auto-retries invalid outputs
   - Updates `Final_Topic_Label`, `classification_confidence`, and `key_phrases` columns

### When to Use
- You have >10% outlier documents (Topic -1)
- You have a stable final topic list (from Table 1)
- You want to "clean up" the dataset for final analysis
