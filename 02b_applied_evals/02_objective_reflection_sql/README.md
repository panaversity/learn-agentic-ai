# Step 02 — Objective Reflection (SQL-like)

What you’ll learn
- Measure accuracy lift from adding a reflection pass to query generation.
- Use a tiny dataset with ground truth to compute % correct.
- Make prompt and reflection changes measurable.

Why it matters (business)
- Reflection often increases answer accuracy but adds latency/cost. This step quantifies the tradeoff so product can decide whether the lift justifies the extra step.
- Outcome-type: “With reflection, accuracy +X pp at +Y ms/+Z$ per request.”

Run
```bash
uv run python 02_objective_reflection_sql/run_eval.py --dataset 02_objective_reflection_sql/data/sql_eval.jsonl --reflect false
uv run python 02_objective_reflection_sql/run_eval.py --dataset 02_objective_reflection_sql/data/sql_eval.jsonl --reflect true
```
Compare the two accuracies to assess value.

Tips
- Expand `data/sql_eval.jsonl` to 10–20 items for a stronger signal.
- Try variations of the reflection instruction and re-run to A/B prompts.
