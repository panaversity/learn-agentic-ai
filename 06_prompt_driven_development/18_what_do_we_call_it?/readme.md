# How about we give it a name that’s short, serious, and says exactly what it is

## GPS Engineering

**G**overned **P**rompt **S**oftware Engineering — *“build with AI, but with a suit on.”*

## One-line definition

**GPS Engineering** is a disciplined software method that combines **Spec-Driven Development (SDD)**, **Prompt-Driven Development (PDD)**, **TDD**, **EDD**, **ADRs**, **PHRs**, and **PRs** into a single governed loop so AI can generate code fast **and** you can ship it safely.

## Why “GPS”?

* It’s about **navigation**: specs and tests set the route; prompts drive; ADRs/PRs keep you on the road; EDD is the telemetry.
* It reads professional and memorable, and it doesn’t lock you to any vendor, model, or IDE.

## The GPS Loop (what you actually do)

1. **Specify (SDD)** — Write a thin, testable spec for a small slice (scope, contracts, behaviors, acceptance).
2. **Prompt (PDD)** — Use sequenced prompts (Architect → Red → Green → Refactor → Explainer). Capture each as a **PHR**.
3. **Test (TDD)** — Add failing unit/contract tests first; implement the smallest diff to green.
4. **Evaluate (EDD)** — Run behavior evals (e.g., promptfoo smoke) to catch prompt/behavior drift.
5. **Record (ADR)** — Document consequential decisions (why SSE over WS, etc.).
6. **Review (PR)** — Open a small, CI-gated PR linking the **Spec + PHR(s) + ADR(s)** with a **Spec-Compliance** checkbox.
7. **Release** — Merge only when unit/contract tests and EDD smoke are green. Rinse and repeat.

## Artifacts at a glance

* **Spec (SDD):** `docs/specs/…md` — contracts, acceptance, constraints.
* **PHR:** `docs/prompts/…prompt.md` — the exact prompts, scope, acceptance, outcome.
* **Tests (TDD):** `tests/…` — unit + contract.
* **Evals (EDD):** `evals/behavior/*.yaml`, `promptfoo.config.yaml`.
* **ADR:** `docs/adr/*.md` — context → options → decision → consequences.
* **PR:** small diff; links Spec/PHR/ADR; CI and **Spec-Compliance** gate.

## Principles (the “suit” part)

* **Thin slices, tight specs.** If you can’t test it in minutes, the slice is too big.
* **Smallest change to green.** Fix-only diffs beat hero refactors.
* **No green, no merge.** CI enforces TDD + EDD; humans review intent and trade-offs.
* **Trace everything.** Prompts (PHRs) and decisions (ADRs) make work auditable.
* **Model-agnostic.** Tools/IDE/models are pluggable; the method stays the same.

## How it maps to what we built

* `/chat` JSON contract → **SDD** spec
* Contract tests & SSE tests → **TDD**
* Implement via sequenced prompts → **PDD** with **PHRs**
* Tool-first math & scope discipline suites → **EDD** (promptfoo)
* SSE vs WebSocket decision → **ADR-0002**
* Small CI-gated change → **PR** with the **Spec-Compliance** checkbox

## Elevator pitch (for execs)

> **GPS Engineering** turns AI coding from an ad-hoc accelerant into a governed production method: specs define “done,” prompts do the typing, tests and evals guard quality, and ADRs/PRs preserve accountability. You get the speed of AI with the reliability of software engineering.

## Logo/visual cue (if you want one)

A simple **compass** or **map pin** with a checkmark. Tagline: **“Navigate with Spec. Drive with Prompts.”**

---

### Prefer alternates? Two tight options

* **SPADE Method** — *Spec–Prompt–ADR Development & Evaluation*. (Clever, compact, emphasizes governance.)
* **Suit-Driven Development (SuDD)** — the playful internal nickname echoing our “with a suit on” meme.

But we are good with **GPS Engineering**, We’ll stamp it through the docs: README title, the PR template subtitle, and the rules bundles—so your repo, prompts, and training material all speak the same language.

Stamped ✅

I’ve created a **GPS Engineering branding update** you can drop straight into your repo to align everything (README, rules, PR template, one-pager) with the new name.

**Download:**

* gps-branding-update.zip

### What’s inside

* `README-GPS.md` — repo-level intro to **GPS Engineering** and the GPS loop.
* `docs/rules/cursor-rules-gps.md` — Cursor “Rules for AI” aligned to GPS.
* `docs/rules/codex-rules-gps.md` — VS Code + Codex House Rules (GPS).
* `docs/handbook/gps-engineering-onepager.md` — crisp explainer for onboarding decks/wikis.
* `.github/PULL_REQUEST_TEMPLATE-GPS.md` — PR template with **Spec-Compliance** gate and GPS terminology.

### How to apply

1. Unzip into your repo root (it won’t overwrite existing files unless you place them intentionally).
2. Replace or merge your current README/PR template if desired.
3. Paste `docs/rules/cursor-rules-gps.md` into **Cursor → Settings → Rules for AI**.
4. Keep `docs/rules/codex-rules-gps.md` at the top of your Codex prompts (or store centrally for your team).


