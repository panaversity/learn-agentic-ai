# Step 03 — Subjective Rubric with LLM-as-Judge

What you’ll learn
- Score subjective outputs using binary criteria (0/1) instead of pairwise comparisons.
- Reduce bias and improve calibration by summing binary checks.

Why it matters (business)
- Lets product teams define quality rubrics (e.g., compliance, tone, completeness) and track improvements objectively across releases.

Run
```bash
uv run python 03_subjective_rubric_llm_judge/evaluate.py --artifact-file sample.txt --rubric-file rubric.txt
```

Deliverables
- JSON with per-criterion scores and total that dashboards can ingest.
