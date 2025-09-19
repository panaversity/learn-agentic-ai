# New Paradigm of 2025

## 1. Why Summer 2025 Changed the Game

By mid-2025, large language models cleared key bars in reasoning, tool use, and latency, making human–AI pair programming not only feasible but often the preferred mode. AI-first IDEs fused model context, navigation, refactoring, and repo-aware prompting; agentic systems learned to read issues, implement changes, and open PRs with tests. Outcomes, however, split sharply: some teams saw dramatic cycle-time reductions, while others accumulated rework from unstructured “vibe coding.” Speed without method simply accelerates defects.

---

## 2. The Modern Stack: Models, IDEs, Agents

**Frontier models** now plan, synthesize code, and call tools reliably. **AI IDEs** (e.g., Cursor) translate prompts into targeted, repo-aware diffs. **Software agents** coordinate across repos, CI, and ticketing—yes, including docs updates. This trio makes generation inexpensive and iteration rapid, but also raises the premium on crisp specs and rigorous tests: refined prompts yield leverage; vague prompts yield polished mistakes.

---

## 3. Vibe Coding: Where It Helps—and Where It Hurts

**Definition.** Vibe coding is intuition-led, prompt-and-iterate exploration—excellent for spikes and discovery, poor for long-lived systems.
**Strengths.** Fast prototyping, low overhead, creative leaps.
**Failure modes.** Ambiguous requirements, undocumented choices, sporadic or missing tests, architecture drift—code that dazzles today and invoices you tomorrow.

---

## 4. Prompt-Driven Development (PDD): The Discipline

**Definition.** PDD builds primarily through **ordered prompts** that capture intent, constraints, and acceptance criteria—the AI types; engineers decide.
**Core loop (“suit + tie”):**

1. **Plan** via an *Architect Prompt* (micro-spec).
2. **Red** with tests-only (TDD).
3. **Green** with the smallest change to pass.
4. **Refactor** while preserving behavior.
5. **Explain** with an *Explainer Prompt*.
6. **Record** via an ADR.
7. **Share** through a PR with CI gates (“no green, no merge”).
   Creative momentum is preserved, while quality and traceability are institutionalized.

---

## 5. The Guardrails: TDD, ADR, and PR

* **TDD** encodes expectations before code exists, aligning AI output to intent.
* **ADRs** capture context, options, decisions, and consequences so teams inherit rationale—not folklore.
* **PRs** enforce small, reviewed, test-backed changes and provide auditable history.

---

## 6. Operating Model for AI-First Teams

**Roles (expressed as prompts or responsibilities):** Architect, Implementer, Tester, Tech Writer, Release Shepherd.
**Default policies:**

* Optimize for the **smallest diff**; require an ADR for public API/dependency shifts; maintain coverage at or above target; keep CI deterministic.
* Maintain repo hygiene: `.env.sample`, Makefile targets, PR template, and fail-fast CI.
  **Tooling:** AI IDE (e.g., Cursor), frontier model, local mocks, tracing, and **uv** for dependencies—practices that turn speed into reliability.

---

## 7. A Tale of Two Teams: Same Feature, Different Paths

**Feature:** `/summarize` for PDFs.

* **Team A (vibes):** “Add summarize”; ships quickly; lacks size limits, clear errors, and docs; breaks in staging.
* **Team B (PDD + TDD):** Micro-spec with 10-MB cap, PDF MIME checks, SSE streaming, explicit 200/400/415, tests first, minimal diff, ADR for streaming choice, PR with passing CI; smooth release.
  **Result:** Team A burns time fixing regressions; Team B ships enhancements the same day.

---

## 8. Measuring the Shift (Signals That Matter)

* **Lead time to change:** hours per small PR.
* **Change-failure rate:** % of PRs causing rollback/hotfix.
* **MTTR:** time to recover from failure.
* **Coverage & contract tests:** clarity and enforceability of the spec.
* **ADR density:** decisions documented per meaningful change.
* **AI utilization:** proportion of diffs generated via prompts (with human review).

---

## 9. Ninety-Day Migration Plan

* **Days 0–10 — Foundations:** PR template, CI gates, ADR folder, Makefile, coverage target.
* **Days 10–30 — Pilot:** Apply PDD×TDD on a non-critical service; produce 5–8 ADRs; ship 10–20 small PRs.
* **Days 30–60 — Scale:** Extend to three repos; add tracing, contract tests, and “no green, no merge”; run a blameless retro.
* **Days 60–90 — Institutionalize:** Formalize policies, onboard wider org, publish playbooks and prompt libraries.

---

## 10. Ready-to-Use Prompt Patterns

**Architect (micro-spec).**
“Design `<feature>` as a minimal slice: goals, constraints, interfaces, Given/When/Then tests, risks, and an ADR draft.”

**TDD: Red (tests only).**
“Add failing tests for `<behavior>` (edge/negative included). No production code. Minimal diff; offline.”

**PDD: Green (smallest change).**
“Make the least change to pass `tests/<path>::<test>`; no new deps; no unrelated refactors; diff-only.”

**Refactor (safe).**
“Refactor internals for clarity/performance; preserve public APIs; keep tests green; summarize in 5 bullets.”

**ADR (why).**
“Create ADR `<id-title>`: Context, Options (pros/cons), Decision, Consequences, References. Link PR and tests.”

**PR (review gate).**
“Draft a PR with problem/solution, screenshots or curl, linked ADRs/issues, test plan, rollout steps, risks. Keep scope small.”

---

## 11. Risks—and How to Mitigate Them

* **Prompt drift →** Freeze a micro-spec per slice; regenerate from spec if intent changes.
* **Tool lock-in →** Document in ADRs; keep adapters thin; isolate integrations.
* **Security/privacy →** Redact PII, encrypt at rest, test redaction; add privacy checks to PR template.
* **Over-automation →** Keep humans in the review/merge loop; delegate toil, not judgment.
* **Model brittleness →** Mock external calls; use contract tests; pin versions when possible.

---

## 12. Organizational Shifts

**Skills:** Specification via prompts, test design, diff review, decision capture.
**Culture:** Small PRs, “no green, no merge,” ADRs for consequential changes, blameless retros.
**Ethics:** Licensing, attribution, and data governance for training artifacts.

---

## 13. Conclusion: From Novelty to Norm

Summer 2025 turned AI assistance into table stakes. The teams that win aren’t merely “using AI”—they’re **operationalizing** it with **PDD + TDD + ADR + PR**. Keep the inventiveness of vibe coding, but put structure around it: small, test-guarded prompts; documented decisions; PR-gated integration. That’s how you move faster—and sleep better.

---

## Appendix A: One-Page Checklist

* [ ] Micro-spec prompt with acceptance tests
* [ ] **TDD**: Red → Green → Refactor
* [ ] **ADR** for material decisions
* [ ] **PR** policy: small scope, CI passing, ADR linked, “no green, no merge”
* [ ] Observability: tracing, error taxonomy, SLOs
* [ ] Security & privacy: redaction, retention, encryption
* [ ] Metrics: lead time, change-fail %, MTTR, coverage, ADR density
* [ ] Prompt library: architect, tests-only, minimal-diff, refactor, ADR, PR
