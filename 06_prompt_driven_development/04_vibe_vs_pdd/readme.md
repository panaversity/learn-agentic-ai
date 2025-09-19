
# Vibe Coding vs. Prompt‑Driven Development

This tutorial clarifies the difference between **vibe coding** and **prompt‑driven development (PDD)** and shows how to practice PDD in **incremental baby steps** using a sequence of focused prompts (the AI writes the code; you write the specs). Keep the creativity of vibes—**but with a suit on**: tight prompts, tests, docs, and traceability.

---

## 1) Clear Definitions

### Vibe Coding
Fast, exploratory building guided by intuition and ad‑hoc prompts. You discover the problem by poking at it. Great for spikes and concept discovery; risky for maintainability.

**Use when:** Prototyping, mapping the unknown, comparing approaches quickly.  
**Tradeoffs:** Loose specs, uneven quality, hidden debt.

### Prompt‑Driven Development (PDD)
A disciplined method where you design and evolve the system **through sequential prompts**. Each prompt is a micro‑spec; the AI generates code, tests, and docs. You verify, record decisions, and move to the next slice—**the same creativity, but with a suit on**.

**Use when:** You intend to ship, collaborate, and maintain.  
**Tradeoffs:** Slightly more upfront structure; far less rework later.

---

## 2) Mindset Differences

| Dimension | Vibe Coding | PDD (“with a suit on”) |
|---|---|---|
| Intent | Explore possibilities | Deliver predictably |
| Prompts | Free‑form, evolving | Structured, versioned, reusable |
| Artifacts | Ephemeral spikes | Code + tests + docs + ADRs |
| Quality | “Works now” | Guardrails, contracts, CI by default |
| Risk | Accepts ambiguity | Controls ambiguity |

---

## 3) PDD in Baby Steps (the Incremental Loop)
**PDD is iterative by design.** You progress via **small, verified deltas**, each driven by a **focused prompt**. No hand‑coding required.

### The PDD × TDD Loop (Suit + Tie)
1. **Plan (PDD)** — *Architect Prompt*: define one tiny outcome, constraints, and acceptance tests.
2. **Red (TDD)** — *Tests‑Only Prompt*: add failing unit/contract tests that encode the acceptance criteria.
3. **Green (PDD)** — *Minimal‑Diff Prompt*: generate the **smallest change** to pass the new tests (code + docs). No unrelated refactors.
4. **Refactor (TDD)** — *Refactor Prompt*: improve internals while keeping tests green.
5. **Explain (PDD)** — *Explainer Prompt*: summarize diffs/trade‑offs in plain language.
6. **Record (PDD)** — *ADR Prompt*: capture the decision, alternatives, and consequences.
7. **Share (Team)** — *PR*: open a Pull Request linking tests and ADR; reviewers verify red→green history and scope.

> Baby steps ≈ TDD/iterative delivery, but your keyboard types **prompts**, not functions—**the same creativity, but with a suit on**.

---

## 4) Side‑by‑Side Flows

### Vibe Coding Flow
1) Loose goal → 2) ad‑hoc prompts → 3) quick try → 4) tweak → 5) demo → 6) keep or discard.  
**Strength:** discovery speed. **Risk:** brittle outcomes, unclear rationale.

### PDD Flow (Baby Steps)
1) Micro‑spec prompt → 2) minimal code+tests → 3) verify → 4) explain → 5) ADR → 6) repeat.  
**Strength:** sustainable velocity, onboarding ease, predictable quality.

---

## 5) Concrete Examples (Vibes vs. PDD)

### A) Add a PDF Summarizer Endpoint
- **Vibes Prompt:** “Add `/summarize` that takes a file and returns a summary.”  
  *Outcome:* works today; lacks size limits, error taxonomy, tests.
- **PDD × TDD Micro‑Steps:**
  1) *Architect Prompt:* specify 10MB limit, PDF‑only, streaming, error codes 200/400/415, perf budget, docs.  
  2) *Red:* tests for happy path + 400 size/type + 415 wrong MIME.  
  3) *Green:* minimal implementation to pass tests.  
  4) *Refactor:* extract validators, keep tests green.  
  5) *Explain:* 8‑bullet summary.  
  6) *ADR:* “Why SSE for streaming; alternatives considered.”  
  7) *PR:* link ADR + tests; reviewers see contained diff.

### B) Multi‑Agent Handoff
- **Vibes Prompt:** “If question says ‘compare’ or ‘research’, use a second agent.”  
  *Risk:* fragile heuristics.  
- **PDD × TDD Micro‑Steps:** intent classifier with `RESEARCH` ≥0.7, logs `handoff_reason`. Tests for thresholds; README diagram; ADR on handoff strategy; PR with clear scope.

### C) Security/Compliance
- **Vibes Prompt:** “Save chat history for later analysis.”  
  *Oops:* no retention policy or redaction.  
- **PDD × TDD Micro‑Steps:** redact PII before persistence; 30‑day retention; config flag for dev; tests for redaction; ADR “Data retention policy”; PR checklist includes privacy review.

---

## 6) Choosing the Right Mode
**Use Vibes** to explore feasibility, reduce uncertainty, or shape UX quickly.  
**Use PDD** to converge on production quality with traceability, tests, and clear interfaces.  
**Hybrid:** Spike with vibes → converge with PDD.

---

## 7) How to Upgrade Vibes → PDD
1) **Freeze learning** into a one‑page *Prompted Spec* (goal, constraints, acceptance tests).  
2) **Guardrails**: security, error taxonomy, performance budgets, observability.  
3) **Template prompts** by role (Architect, Implementer, Tester, Tech Writer).  
4) **Automate checks**: lint, type, unit, contract, CI, coverage gates.
5) **Record why**: write/append **ADRs** for major decisions and alternatives.
6) **Enforce via PR policy**: small scope, tests required, ADR link if interfaces/deps change, “no green, no merge,” diff size guard.

---

## 8) Baby‑Step Prompt Templates

### A) Architect (Micro‑Spec)
```text
You are the software architect. Design <feature> as a minimal slice. Provide goals, constraints, public interfaces, Given/When/Then acceptance tests, risks, and an ADR draft summarizing the decision and alternatives.
```

### B) Red (Tests‑Only)
```text
Add failing tests for <behavior>. Include edge/negative cases and clear names. No production code changes. Keep the diff minimal and runnable offline.
```

### C) Green (Smallest Diff)
```text
Make the smallest change necessary to pass tests/<path>::<test_name>. Do not refactor unrelated code. No new dependencies. Output diff-only.
```

### D) Refactor (Safety Rails)
```text
Refactor internals for clarity/performance. Preserve public APIs and behavior. All tests must remain green. Provide a short refactor summary.
```

### E) Explainer (Human Digest)
```text
Summarize the change in 8 bullets: purpose, key files, interfaces touched, tests added, risks, and how to extend safely.
```

### F) ADR (Why This Way)
```text
Create ADR <id-title> with: Context, Options (pros/cons), Decision, Consequences, References. Status = Accepted. Link to related PR and tests.
```

### G) PR (Team Gate)
```text
Draft a PR description: problem/solution, screenshots or curl, linked ADRs/issues, test plan, rollout notes, and risk assessment. Keep scope small.
```

---

## 9) Anti‑Patterns (and Fixes)
- **Prompt drift:** Specs change mid‑generation → Freeze the micro‑spec and regenerate.  
- **Hidden coupling:** AI adds leaky abstractions → Add contracts + smoke tests.  
- **Scope creep:** Prompts grow horns → Add an “Out of scope” list to every prompt.  
- **Tool roulette:** Switching libs casually → Require an ADR to change dependencies.  
- **Gigantic diffs:** Hard to review → Use “smallest diff / diff‑only” prompts.

---

## 10) Success Metrics
**Vibes:** Did we learn enough to decide next steps quickly?  
**PDD × TDD:**
- Clean clone runs with one command
- Stable tests and CI; coverage ≥ target (e.g., 80%)
- ADRs exist for major decisions and are referenced in PRs
- PRs are small, pass checks, and merge without rework churn
- New teammate contributes within a day using docs

---

## 11) One‑Page PDD Checklist (Suit On)
- [ ] Micro‑spec prompt with acceptance tests  
- [ ] **TDD**: Red → Green → Refactor prompts  
- [ ] Guardrails (security, errors, performance)  
- [ ] Contracts (types, API schemas)  
- [ ] Automated checks (lint, type, unit, contract, CI, coverage)  
- [ ] Docs (README runbook) + **ADRs**  
- [ ] Diff‑only, smallest‑change prompts  
- [ ] **PR** policy: small scope, tests required, ADR link, “no green, no merge”  
- [ ] Commit after green; repeat

---

## 12) Glossary (Quick)
- **ADR** — Architecture Decision Record: concise doc capturing context, options, decision, and consequences.
- **PR** — Pull Request: a reviewed proposal to merge changes; should link tests and ADRs.
- **TDD** — Test‑Driven Development: Red → Green → Refactor loop that encodes behavior in tests before implementation.

---

## 13) Closing Note
Vibe coding is your spark of discovery. **Prompt‑Driven Development is the engine that ships**—now fortified with **TDD** for correctness, **ADRs** for traceability, and **PRs** for team quality gates—**the same creativity, but with a suit on**.


