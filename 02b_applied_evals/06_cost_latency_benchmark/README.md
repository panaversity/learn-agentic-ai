# Step 06 — Cost & Latency Benchmarking

What you’ll learn
- Time a step and surface latency in ms.
- Sketch where cost would be estimated (per-token/per-call).

Why it matters (business)
- Enables data-driven tradeoffs: “Keep quality, reduce p95 latency by X%” or “cut cost/request by Y%”.

Run
```bash
uv run python 06_cost_latency_benchmark/bench.py
```

Next
- Extend with token counters per provider for cost estimates.
