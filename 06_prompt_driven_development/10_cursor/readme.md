# Using Cursor in 2025 — A Practical, Up-to-Date Guide

Cursor is a VS Code–style IDE with AI built in. You write prompts; Cursor proposes diffs, multi-file edits, inline completions, and repo-aware explanations. This guide focuses on **how to get the most out of Cursor today**—with patterns that keep quality high (PDD × TDD, ADRs, PR gates) and avoid the “vibe coding” trap.

---

## 1) Install & First-Run Setup

1. **Download & install** Cursor from the official site for your OS.
2. **Sign in** (GitHub/Google/email).
3. **Open a workspace** (folder or repo).
4. **Models**: choose a default provider/model in Settings. Cursor can route to multiple LLMs; pick the best one you have access to (e.g., GPT-class for coding, another for analysis).
5. **Extensions**: install the standard **Python**, **Docker**, **Git** integrations (Cursor supports most VS Code extensions).
6. **Environment**: create a quick project script:

   * `make setup` → create venv / sync deps (or `uv sync`)
   * `make test` → run tests locally and offline
   * `.env.sample` with required vars

> Tip: Put a **README** section called “How to run tests locally” so Cursor can quote it back when planning.

---

## 2) Set “Workspace Rules” (tell Cursor how to behave)

Add a short rules file (e.g., *Cursor → Settings → Rules for AI* or a `docs/rules.md`) that Cursor can read:

* **Language/runtime**: Python 3.12+, **uv** for deps
* **Architecture**: FastAPI service, Pydantic models, Agents SDK when building agentic apps
* **Quality gates**: pytest, ruff, coverage ≥ 80%, deterministic tests (mock network)
* **Output discipline**: “Smallest diff”, no unrelated refactors, public APIs stable unless ADR attached
* **Security**: no secrets in code; use `.env`
* **Docs**: update README + ADRs for major decisions

These rules act as a “style guide” for the model and make generations consistent.

---

## 3) The Three Ways You’ll Use Cursor

### A) **Inline** (Tab/Enter to accept)

* Great for **small edits**: rename, fix types, complete a function.
* Keep the cursor near what you want; write a short comment like
  `# add pagination with page,size params (validate ranges; default page=1,size=20)`.

### B) **Chat** (repo-aware conversation)

* Ask “why/what” questions: *“Explain the data flow from /chat to tool calls in two bullets per file.”*
* Good for **explanations, code tours, and targeted suggestions**.

### C) **Composer** (multi-file diffs)

* Best for **structured changes**: new endpoint, refactor, test scaffolds.
* Treat Composer prompts like **GitHub Issues**: include file paths, acceptance criteria, and test plan.

---

## 4) The Cursor Method: PDD × TDD (baby steps)

Cursor shines when your prompts are **small and test-guarded**. Use this 7-step loop:

1. **Plan** — Architect prompt (micro-spec, constraints, acceptance checks)
2. **Red** — Ask Cursor to **add failing tests first**
3. **Green** — “**Smallest diff** to pass `tests/...`”
4. **Refactor** — improve internals; **tests stay green**
5. **Explain** — ask for an 8-bullet summary of the change
6. **Record** — **ADR** (context, options, decision, consequences)
7. **Share** — commit and open a **PR** (CI must be green: “no green, no merge”)

> Think of Cursor as a fast typist. **You** provide the spec and the test. Cursor makes it pass.

---

## 5) Prompt Templates You Can Paste

### 5.1 Architect a tiny slice

```
Design <feature> as a minimal slice.
- Files to touch (paths)
- Public interface + payloads
- Given/When/Then acceptance tests
- Risks + rollback notes
Return a short plan + diff outline only.
```

### 5.2 Red: tests first

```
Add failing tests for <behavior>:
- Unit + contract tests
- Edge/negative cases
No production code yet. Keep diff minimal and offline.
```

### 5.3 Green: minimal implementation

```
Make the smallest change necessary to pass tests/<path>::<name>.
Do not refactor unrelated code. No new dependencies. Output diff-only.
```

### 5.4 Refactor safely

```
Refactor internals for clarity/performance. Preserve public APIs and behavior.
All tests must remain green. Summarize changes in 5 bullets.
```

### 5.5 ADR + PR drafting

```
Create ADR <id-title> with Context, Options (pros/cons), Decision, Consequences, References.
Draft a PR description: problem/solution, test plan, screenshots/curl, risks/rollback.
Link the ADR in the PR text.
```

---

## 6) Typical Workflows (end-to-end)

### A) Add a new API endpoint (FastAPI)

1. **Composer (Plan)**: spec `/summarize` with 10 MB limit, PDF-only, SSE + JSON fallback, error codes 200/400/415.
2. **Composer (Red)**: add tests for happy path + 400 (oversize) + 415 (wrong MIME).
3. **Composer (Green)**: implement minimal code to pass; update README with `curl`.
4. **Chat (Explain)**: get a human-readable summary and risks.
5. **Composer (ADR)**: “streaming-protocol choice (SSE vs WS)”.
6. **Git**: open PR; ensure CI green.

### B) Multi-file refactor

* “Move config from `app/main.py` to `app/config.py` with typed settings; add tests; update docs; keep public APIs stable.”
* Ask for **diff-only** changes. Review carefully, then accept or iterate.

### C) Debug + regression test

* “Create failing test reproducing issue #142; minimally fix; add regression; summarize root cause in PR.”

---

## 7) Keeping Cursor on the Rails

* **Be specific**: include file paths, API names, expected error codes, and test names.
* **One thing at a time**: if the diff is big, split the spec into smaller prompts.
* **Deterministic tests**: mock network and time; pin seeds; avoid flakiness.
* **No secret leakage**: reference environment variables; never paste real keys.
* **Reject overreach**: if Cursor changes unrelated code, reply “undo unrelated edits; smallest diff only.”

---

## 8) Model Strategy in Cursor

* Choose a **strong coding model** as default; keep a **secondary model** for long reasoning or summarization.
* When a response drifts, **re-prompt with constraints** (“diff-only,” “no new deps,” “keep public APIs stable”).
* For large plans, ask Cursor to **list a step sequence** first, then tackle **step 1** only.

---

## 9) Git & CI Integration

* Work in **feature branches**; one vertical slice per PR.
* CI should run `ruff`, `pytest`, coverage gates, and (optionally) a lightweight Docker build.
* Add a **PR template** that asks: “Tests added?”, “ADR linked?”, “Screenshots/curl?”, “Risk/rollback?”

---

## 10) Example: Fresh Python project with **uv**

**Prompt (Composer):**

```
Scaffold a Python service using uv:
- pyproject.toml, uv lock
- app/main.py (FastAPI + /healthz)
- tests/test_healthz.py
- Makefile: setup, test, run, lint
- .env.sample; README with uv commands
- .github/workflows/ci.yml (ruff, pytest, coverage>=80%)
```

Then iterate feature-by-feature using the PDD × TDD loop.

---

## 11) Troubleshooting

* **Cursor edited the wrong files** → “Revert unrelated edits and propose the smallest diff limited to <files>.”
* **Test failing with flaky network** → “Mock external calls; run tests offline; stabilize fixtures.”
* **Prompt drift** → Restate the **micro-spec** and explicitly add an “**Out of scope**” list.
* **Model stalls** → Break the task into steps; plan first, implement one step; avoid mega-prompts.

---

## 12) Quick Checklists

**Daily checklist**

* [ ] Micro-spec prompt written
* [ ] Red tests added
* [ ] Green minimal diff applied
* [ ] Refactor with tests green
* [ ] Explainer summary generated
* [ ] ADR recorded; PR opened; CI green

**Prompt anatomy**

* Title (like a GitHub Issue)
* Files/paths to touch
* Acceptance criteria & test plan
* Risks + rollback
* “Smallest diff; no unrelated changes”

---

### Final Takeaway

Cursor is best when **you steer with precise prompts and tests**. Keep each change small, review diffs like PRs, and record decisions with ADRs. That’s how you turn AI speed into **maintainable, production-grade software**—creativity, **but with a suit on**.
