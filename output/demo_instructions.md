# DEMO & REPRODUCIBILITY INSTRUCTIONS

## Quick Start / How to Run Analysis & Tests

### Prerequisites
- Python 3.10+
- `pytest` installed (`pip install pytest`)

### Running the End-to-End Analysis Pipeline
Run the following scripts from the project root (`C:\Users\h.sunitha\Desktop\vireo-refund-analysis`):

```bash
# 1. Run Data Inspection Script
python .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/inspect_data.py

# 2. Run Duplicate Reconciliation
python .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/reconcile_duplicates.py

# 3. Build Clean Dataset & Legacy Normalization
python .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/build_clean_dataset.py

# 4. Run Relational Enrichment
python .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/build_enriched_dataset.py

# 5. Run Financial Refund Reconciliation
python .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/reconcile_refunds.py

# 6. Generate Monthly Summaries & Insights
python .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/generate_analysis.py

# 7. Run AI NLP Ticket Audit
python .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/run_ai_validation.py
```

### Running Automated Test Suite
To run the automated verification suite:

```bash
python -m pytest .gemini/antigravity-ide/brain/5e6ff19f-5e8a-4c41-9671-abab37392964/scratch/test_clean_dataset.py
```
