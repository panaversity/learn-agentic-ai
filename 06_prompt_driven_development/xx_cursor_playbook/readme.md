# Cursor IDE Playbook (2025): Prompt-Driven Development “…with a suit on”

> Build maintainable AI-assisted software in **Cursor**—without vibe-coding yourself into a rewrite. This end-to-end guide shows how to run **Prompt-Driven Development (PDD)** together with **TDD, ADRs, PR discipline**, and **Prompt History Records (PHRs)**, using **uv** for Python deps and the **OpenAI Agents SDK** for agent logic.

> Note: You shared a CLI-oriented tutorial for another model earlier. I’m **not** copying that template; I’m expanding the ideas into a Cursor-native, editor-first flow.&#x20;

---

## 0) Outcomes you’ll get

* A repeatable **Cursor workflow** for planning, generating, testing, and reviewing AI-written code.
* A lightweight Python service (FastAPI) with **/healthz** and **/chat** (non-streaming + SSE), wired to **OpenAI Agents SDK**.
* A **prompt library**, **PHR** logs, **ADR** docs, a **PR template**, and **CI** gates—so speed doesn’t kill quality.
* Ready-to-paste **Cursor prompts** (architect/red/green/refactor/explainer) for your first iterations.

---

## 1) What makes Cursor different (and how to use it well)

**Cursor is an AI-first IDE**, not just a chat window. Lean on these capabilities:

* **Rules for AI** (global and workspace): pin constraints (Python 3.12+, `uv`, no secrets, tests first, minimal diffs).
* **Composer (⌘I / Ctrl+I)**: writes *multi-file* diffs from a single prompt; great for “architect” and “green” steps.
* **Inline chat & quick-fix**: select code → ask for a refactor/test; perfect for “smallest possible change.”
* **@-mentions**: reference files/folders in prompts (`@app/main.py`, `@tests/test_chat_contract.py`).
* **Diff review**: accept or discard hunks. PDD means you *curate* changes—don’t rubber-stamp.

**Anti-pattern (avoid):** unspecific, sprawling prompts (“make it better”).
**Pro-pattern:** micro-spec + acceptance tests + “minimal diff” guardrail.

---

## 2) One-time setup (10–15 min)

### 2.1 Create the repo structure

```bash
mkdir agents-chatbot && cd agents-chatbot
git init
mkdir -p app/agents app/guards tests docs/{adr,prompts,diagrams,pr} .github/workflows .githooks scripts
echo "OPENAI_API_KEY=\nMODEL=gpt-5" > .env.sample
```

### 2.2 Use **uv** for Python deps (fast, reproducible)

```bash
uv init --python 3.12
uv add fastapi "uvicorn[standard]" pydantic python-dotenv httpx pytest ruff
uv add openai-agents  # OpenAI Agents SDK (per your request)
```

> Keep **`uv.lock`** checked in; it’s your dependency truth.

### 2.3 Cursor workspace rules (paste this once)

Open **Cursor → Settings → Rules for AI** and add:

```
# Project guardrails
- Use Python 3.12+ and uv for deps (pyproject.toml + uv.lock).
- Use OpenAI Agents SDK for agents, tools, sessions, handoffs, guardrails.
- Scaffold FastAPI with /healthz and /chat endpoints.
- Tests first with pytest; network mocked by default.
- Structured outputs via Pydantic; length limit 1200 chars.
- No secrets in code or prompts; use .env / .env.sample.
- Keep diffs minimal and explain changes; small PRs only.
- For Docker, use a uv-based multi-stage build; non-root runtime.

# Documentation
- Maintain PHRs in docs/prompts (one per meaningful step).
- Add ADRs in docs/adr for consequential decisions.
- PRs must link PHRs + ADRs; CI: ruff + pytest + (optional) docker build.

# Agent defaults
- Start with CustomerAgent; add ResearchAgent with intent-based handoff.
- Provide two function_tool(s): calculator(expression), now(tz?).
- Sessions per session_id; streaming via SSE with JSON fallback.

# Quality bar
- All tests green locally and in CI. "No green, no merge."
```

---

## 3) The PDD × TDD loop (…but with a suit on)

**Loop steps:** **Plan → Red → Green → Refactor → Explain → Record (ADR) → PR**
Each step is a **prompt** you paste into Cursor (Composer or inline). Each step creates a **PHR** file.

### PHR: Prompt History Records (what/why/how of each step)

* Location: `docs/prompts/NNNN-<slug>-<stage>.prompt.md`
* Includes: metadata, acceptance checks, constraints, the exact prompt text, and a short outcome note.

**PHR benefits:** reproducible changes, reviewable intent, reusable prompt patterns.

---

## 4) Copy-paste prompt library (Cursor-native)

Below are **ready prompts** you can paste directly into **Composer (⌘I)**.
Use **@mentions** to bind context (files/folders) before submitting.

### 4.1 Iteration A — `/healthz`

**A1 — Architect (PHR-0001)**

```
Goal: Implement GET /healthz returning {"status":"ok"}.
Acceptance:
- Given GET /healthz Then HTTP 200 with body {"status":"ok"}
Constraints:
- minimal diff; no new deps; update README with a curl example
Out of scope:
- auth, db, tracing

Deliverables:
- app/main.py route
- tests/test_healthz.py with a failing test first (RED)
- README snippet with curl
```

**A2 — Red (tests only) (PHR-0002)**

```
Add failing test tests/test_healthz.py::test_healthz_ok expecting 200 and {"status":"ok"}.
No production code changes. Keep tests offline.
```

**A3 — Green (smallest diff) (PHR-0003)**

```
Make the smallest code change required to pass tests/test_healthz.py::test_healthz_ok.
Do not modify unrelated files. Output diff-only.
```

**A4 — Explainer (PHR-0004)**

```
Explain the diff in <=8 bullets, list trade-offs, follow-ups, and assumptions.
```

---

### 4.2 Iteration B — `/chat` (non-streaming contract)

**B1 — Architect (PHR-0005)**

```
POST /chat {session_id, user_message} → JSON ChatReply {text, used_tool?, handoff:boolean}
Errors:
- 400 when user_message missing (error_code=MISSING_USER_MESSAGE)
Sessions:
- Maintain conversation per session_id (in-memory store for now)

Acceptance:
- test_chat_happy_path_returns_chatreply_shape -> 200 and fields {text, handoff}
- test_chat_missing_user_message_returns_400

Constraints:
- minimal diff; offline tests; no new deps
Deliverables:
- tests/test_chat_contract.py (RED first)
- app/guards/schemas.py defining ChatReply
- stubs in app/agents/core.py for session store + runner
```

**B2 — Red (tests only) (PHR-0006)**

```
Create tests/test_chat_contract.py with:
- test_chat_missing_user_message_returns_400()
- test_chat_happy_path_returns_chatreply_shape()
No production code.
```

**B3 — Green (smallest diff) (PHR-0007)**

```
Implement minimal /chat to pass both tests:
- In app/main.py, validate payload; 400 with error_code=MISSING_USER_MESSAGE if absent.
- Use a stubbed run path that returns ChatReply {text, used_tool?: null, handoff: false}.
- Persist session via an in-memory store in app/agents/core.get_session(session_id).
Output: diff-only.
```

**B4 — Explainer (PHR-0008)**

```
Summarize changes in 8 bullets; call out edge cases and coverage.
```

---

### 4.3 Iteration C — Streaming via SSE (+ ADR)

**C1 — Architect (PHR-0009)**

```
Extend /chat with SSE when Accept: text/event-stream; JSON fallback otherwise.

Acceptance:
- SSE Content-Type: text/event-stream
- Events "data:<token>\n\n" streaming; terminator "data:[DONE]\n\n"
- JSON fallback preserved

Constraints:
- minimal diff; no new deps; offline tests (mock stream)
Deliverables:
- app/streaming.py helper (to_sse)
- tests/test_chat_streaming.py (RED)
- ADR "streaming-protocol-choice" comparing SSE, WS, long-polling
```

**C2 — Red (tests only) (PHR-0010)**

```
Add tests/test_chat_streaming.py to assert:
- Response header starts with text/event-stream when Accept is SSE
- At least one "data:" line appears in the stream
```

**C3 — Green (smallest diff) (PHR-0011)**

```
Add SSE path to /chat while keeping non-streaming JSON behavior intact.
Use a mocked token stream; do not add dependencies. Output diff-only.
```

**C4 — ADR (PHR-0012)**

```
Create docs/adr/0002-streaming-protocol-choice.md:
Context, Options (SSE/WS/long-poll), Decision=SSE (initial), Consequences, References.
```

---

## 5) Agents: minimal but real (OpenAI Agents SDK)

**Concepts (brief):**

* **Agent**: instructions + tools + (optional) `output_type` for structured replies.
* **Tools**: Python functions decorated for tool calls (e.g., `calculator`, `now`).
* **Runner/Sessions**: invoke the agent in the context of a session id; enables memory.
* **Handoff**: route request to a specialist agent (e.g., `ResearchAgent`) based on intent.

**Cursor prompts** (when you’re ready to wire the agent):

**Agent & tools (Green slice):**

```
Implement app/agents/core.py:
- get_customer_agent() with concise instructions; prefer tools for math/time.
- get_runner() suitable for streaming.
- get_session(session_id) using an in-memory dict.

Implement app/agents/tools.py:
- function_tool calculator(expression: str) -> str (safe eval, handle errors)
- function_tool now(tz?: str) -> str (ISO timestamp; default UTC)

Register tools on the agent; set output_type=ChatReply for structured responses.
Add unit tests stubbing model calls (no network).
```

**Handoff (later slice):**

```
Add ResearchAgent with bullet-point responses.
Route to ResearchAgent when intent = "RESEARCH" and confidence >= 0.7.
Surface handoff_reason in logs and response.metadata (non-breaking).
```

---

## 6) Governance: ADRs, PRs, CI, and “no green, no merge”

* **ADRs** (Architecture Decision Records): capture **why this way** (context, options, decision, consequences).
* **PRs**: small diffs, link to PHR(s) & ADRs, include **test plan** and **rollback**.
* **CI**:

  * `ruff` lint
  * `pytest` (network-free)
  * optional Docker build
* **Policy**: *If tests aren’t green, the PR doesn’t merge.*

**PR template (paste into `.github/PULL_REQUEST_TEMPLATE.md`):**

```markdown
# PR Title

## Summary
What changed and why? Link issues.

## Prompt History (PHR)
- docs/prompts/00xx-*-architect.prompt.md
- docs/prompts/00xx-*-red.prompt.md
- docs/prompts/00xx-*-green.prompt.md

## ADRs
- docs/adr/00yy-*.md

## Test Plan
- commands, screenshots, curl

## Risks & Rollback
- risks, rollback steps

## Checklist
- [ ] Small diff
- [ ] Tests green (CI + local)
- [ ] ADR linked (if consequential)
- [ ] No secrets
```

**GitHub Actions ( `.github/workflows/ci.yml` )**—sketch:

```yaml
name: CI
on: [pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run pytest -q
```

---

## 7) Prompt History Records (PHRs) in practice

**Why log prompts?** To turn “AI magic” into **auditable, reproducible process**.

**Minimal PHR template (drop in `docs/prompts/0000-template.prompt.md`):**

```markdown
---
id: 0007
title: Chat Endpoint
stage: green            # architect | red | green | refactor | explainer | adr-draft | pr-draft
date: 2025-09-22
surface: cursor-composer
model: gpt-5-codex
repo_ref: <branch-or-commit>
scope_files: [app/main.py, tests/test_chat_contract.py]
links: { adr: null, issue: null, pr: null }
acceptance:
  - Given POST /chat with user_message -> Then 200 and ChatReply shape
constraints:
  - minimal diff, no new deps
  - offline tests
out_of_scope: [auth]
secrets_policy: "No secrets; use .env"
labels: [api, contract]
---

<PASTE THE EXACT PROMPT YOU USED>

### Outcome
- Files changed: app/main.py
- Tests added: tests/test_chat_contract.py::test_chat_happy_path_returns_chatreply_shape
- Next prompts: add SSE streaming (architect)
- Notes: kept diff minimal
```

> Tip: add a pre-commit hook to block code-only commits without a new/updated PHR.

---

## 8) Diagrams to include (you can generate with Nano Banana or Mermaid)

* **System context** (Client → FastAPI → Agents SDK → Tools/Tracing/CI/Registry/Runtime)
* **Sequence**: POST `/chat` non-streaming & streaming (SSE)
* **Contract**: `ChatReply` class + `ErrorBody`
* **Deployment**: Dev → CI → Registry → Runtime
* **PDD loop**: Plan → Red → Green → Refactor → Explain → Record → PR
* **Traceability**: PHR ↔ ADR ↔ PR ↔ Commits

(We prepared ready-made diagram prompts earlier; want me to drop them into `docs/diagrams/NANO-BANANA-PROMPTS.md`?)

---

## 9) First hour: your exact moves

1. **Paste** “/healthz Architect” → accept test + route diffs → run `uv run pytest -q` (see RED → GREEN).
2. **Paste** “/chat Architect” → accept tests only → run tests (RED).
3. **Paste** “/chat Green” → accept minimal diffs → run tests (GREEN).
4. **Paste** “/chat SSE Architect” → add tests (RED).
5. **Paste** “/chat SSE Green” → accept minimal streaming code → run tests (GREEN).
6. **Open PR** with PHR links + ADR link → CI green → merge.

---

## 10) FAQ for Cursor users

* **“Cursor rewrote half my repo.”**
  Add **constraints** to every prompt: *“minimal diff; touch only X and Y; no new deps.”* Decline unrelated hunks.

* **“It invented APIs.”**
  Pin the source of truth inside the prompt: *“Use the official OpenAI Agents SDK; cite function/class names you used in comments.”*

* **“Streaming feels flaky.”**
  Start with **SSE** for simplicity; add tests for headers and event shape; document the JSON fallback.

* **“How do I stop vibe coding?”**
  Force the loop: **Architect → Red → Green**. If you can’t write acceptance tests, your spec is too vague.

---

## 11) Handy snippets

**Makefile (local commands):**

```make
.PHONY: run test lint
run: ; uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
test: ; uv run pytest -q
lint: ; uv run ruff check .
```

**Dockerfile (uv multi-stage, slim runtime):**

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
WORKDIR /app
COPY pyproject.toml ./
# COPY uv.lock ./
RUN uv venv && uv sync --frozen --no-dev
COPY app ./app
# tests could run here in builder if desired

FROM python:3.12-slim-bookworm AS runtime
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd -m -u 10001 appuser
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
USER appuser
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
```

---

## 12) Measuring success

Track these in a simple `metrics/` folder:

* **Lead time / PR** (open → merge, hours)
* **Change-fail rate** (% of PRs causing hotfix/rollback)
* **Coverage & contract tests** (# and stability)
* **ADR density** (decisions per significant change)
* **AI utilization** (% diffs generated via Cursor prompts)
* **Rework ratio** (# of follow-up fixes after a feature)

---

### Final word

Summer 2025 made AI pair-dev **table stakes**. The winners aren’t those who “use AI”—they’re the ones who **operationalize** it with **PDD + TDD + ADR + PR**. Keep the creative spark, but **put a suit on it**: tiny, test-guarded prompts; documented decisions; PR-gated merges. Cursor gives you speed; this playbook gives you **stability at speed**.

If you’d like, I can also generate:

* A **starter repo** scaffolded for this tutorial (folders, Makefile, hooks, CI, PHR/ADR templates), or
* A **Cursor “Rules for AI” JSON** you can import directly.

## Attachments

All set! Here are both deliverables you asked for:

* **Starter repo (Cursor PDD + TDD + ADR + PHR + CI + Docker + uv):**
  
  cursor-pdd-starter.zip

* **Cursor “Rules for AI” bundle (copy/paste into Cursor → Settings → Rules for AI):**
  
  cursor-rules.json

### What’s inside the starter repo

* **Python app scaffolding**: `app/main.py` with `/healthz`; stubs for agents, tools, guardrails, streaming.
* **Tests**: `tests/test_healthz.py` (green out of the box).
* **Docs**:

  * `docs/prompts/0000-template.prompt.md` (PHR template)
  * `docs/adr/0000-template.md` (ADR template)
  * `docs/AI-FIRST-PLAYBOOK-DIAGRAMS-PHRS.md` (diagram/iteration guide)
  * `docs/diagrams/NANO-BANANA-PROMPTS.md` (diagram prompts list)
* **Governance**:

  * `.github/workflows/ci.yml` (ruff + pytest)
  * `.github/PULL_REQUEST_TEMPLATE.md`
  * `.githooks/pre-commit` & `commit-msg` (PHR nudges)
* **Tooling**:

  * `pyproject.toml` (uv project)
  * `Makefile` (`run`, `test`, `lint`)
  * `Dockerfile` (uv multi-stage, non-root)
  * `.env.sample`

### Quickstart

```bash
unzip cursor-pdd-starter.zip -d ./cursor-pdd-starter
cd cursor-pdd-starter
uv venv && source .venv/bin/activate
uv sync
uv run pytest -q
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
curl -s http://localhost:8000/healthz
```

### Apply the Cursor rules

Open **Cursor → Settings → Rules for AI**, paste the `rules` field from the JSON (or simply open `cursor-rules.json` and copy the text). The same content is also in the repo as `cursor-rules.md`.

## Appendix: Evaluation-Driven Development (EDD) for Cursor-Based, Agentic Projects

> This appendix extends your Cursor IDE playbook with **Evaluation-Driven Development (EDD)**—a discipline for validating an **agent’s behavior**, not just its functions. It plugs directly into your PDD × TDD workflow, adds **prompt/model evals on every PR**, and shows how to run **vendor-neutral evals** (Promptfoo) and **OpenAI Evals / Evaluation API** patterns.

---

## 1) What EDD Adds (in one page)

* **TDD** proves your code works; **EDD** proves your **agent behaves** as intended across prompts, edge cases, and models.
* Daily workflow: **Architect (PDD) → Red (TDD) → Green (TDD) → EDD run → Refactor (if behavior drifts) → ADR/PR**.
* Recommended stack: **Promptfoo** for day-to-day, matrixed prompt/model checks in PRs; add **OpenAI Evals** for deeper, rubric- or model-graded suites on golden sets and releases.

---

## 2) Folder & Governance Additions

Add these to your repo (they integrate with the starter you downloaded):

```
evals/
  behavior/
    001-flight-intent.yaml
    002-tool-usage.yaml
  datasets/
    flight_scenarios.csv
  rubrics/
    faithfulness.md
promptfoo.config.yaml
docs/adr/0003-evaluation-policy.md
```

* **`evals/behavior/*.yaml`** – human-readable behavioral tests (prompts + assertions).
* **`evals/datasets/*.csv`** – large scenario sets (inputs + expected outcomes).
* **`promptfoo.config.yaml`** – runs evals against your **local FastAPI** `/chat` or directly against a model endpoint.
* **ADR-0003 “Evaluation Policy”** – documents gates, thresholds, models under test, and when to run which suite (PR vs nightly).
  *(EDD policy + vendor-neutral first: Promptfoo in PRs; OpenAI Evals for deep checks or releases.)

---

## 3) Wiring Promptfoo to Your Local Agent API

**Why Promptfoo?** Quick, vendor-neutral, runs in CI on every PR, supports prompt/model matrices, diff views, and custom assertions.

### `promptfoo.config.yaml` (example)

```yaml
prompts:
  - file://evals/behavior/*.yaml

providers:
  - id: 'api:fastapi-agent'
    config:
      command: 'uv run uvicorn app.main:app --port 8000'
      url: 'http://localhost:8000/chat'
      method: 'POST'
      headers:
        Content-Type: 'application/json'
      body: |
        {
          "session_id": "eval-session-{{ N }}",
          "user_message": "{{prompt}}"
        }
      # Adapt to your response envelope; this extracts text from your structured ChatReply
      response: '{{ output.text }}'

# Optional: run each test across multiple providers (models/endpoints)
# providers:
#   - id: openai:gpt-5
#   - id: anthropic:claude-4.1
#   - id: 'api:fastapi-agent'  # your service

# thresholds, scoring, and default assertions can live here or in each eval file
```

### Minimal behavior eval (`evals/behavior/001-flight-intent.yaml`)

```yaml
tests:
  - name: "Identifies explicit flight booking"
    vars:
      prompt: "I need to book a flight from Karachi to Lahore next Tuesday."
    assert:
      - type: contains
        value: "I can help you with booking a flight"

  - name: "Politely declines hotel requests"
    vars:
      prompt: "Can you find me a hotel in Islamabad?"
    assert:
      - type: contains
        value: "I can only assist with flight bookings"
```

**Run locally**

```bash
npm i -g promptfoo
promptfoo eval
# See PASS/FAIL table with diffs; useful in PRs, too
```

---

## 4) Scaling EDD: Datasets, Semantics, and Rubrics

### 4.1 CSV-driven scenarios

Put large sets in `evals/datasets/flight_scenarios.csv`:

```csv
user_prompt,expected
"Book a flight to Dubai",flight_intent
"Find me a cheap hotel",out_of_scope
"I need a ticket to Islamabad for tomorrow",flight_intent
```

Reference them from a behavior file:

```yaml
tests:
  - provider: api:fastapi-agent
    dataset: file://evals/datasets/flight_scenarios.csv
    assert:
      - type: javascript
        value: |
          // simple mapping: check if output includes an intent keyword
          const ok =
            (expected === 'flight_intent' && /flight|ticket/i.test(output)) ||
            (expected === 'out_of_scope' && /only.*flight/i.test(output));
          ok
```

### 4.2 Semantic assertions

Prefer **meaning** over exact words to reduce brittle failures:

```yaml
assert:
  - type: similar
    value: "I can help you book a flight"
    threshold: 0.85
```

*(Promptfoo supports semantic checks; use judiciously, keep data drift in mind.)*

### 4.3 Rubric-graded checks (golden sets)

Add `evals/rubrics/faithfulness.md` and run a deeper suite nightly (e.g., model-graded “Is the answer faithful to sources?”). **Use OpenAI Evals** (OSS) or model-graded assertions; reserve for pre-release gates.

---

## 5) OpenAI Evals (OSS) and Cross-Vendor Endpoints

* **Open-source OpenAI Evals** can be used with **non-OpenAI models** by pointing the OpenAI SDK to a compatible base URL (e.g., **Google Gemini’s OpenAI-compatible endpoint**). This keeps your EDD portable.

**Pattern (Python)**

```python
from openai import OpenAI

client = OpenAI(
    api_key="GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# now client calls can target e.g. "gemini-2.5-flash" in the eval runner
```

> **Note:** OpenAI’s **hosted Evaluation API/UI** runs on OpenAI’s platform and doesn’t evaluate third-party models; for Gemini use the **OSS Evals** path or a vendor-neutral tool like Promptfoo.

---

## 6) CI: Make EDD a Gate (No Green, No Merge)

Add a **second job** next to `ruff` and `pytest` in your GitHub Actions:

```yaml
name: CI
on: [pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv venv && uv sync
      - run: uv run ruff check .
      - run: uv run pytest -q

  edd:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm i -g promptfoo
      - run: promptfoo eval --format junit --output results/edd.xml
    # Optional: upload artifacts, fail on threshold
```

**PR policy:**

* PHR links for the slice that changed.
* ADR link for evaluation policy changes.
* **EDD must pass** (or “acceptable degradation” note with approver sign-off).

---

## 7) How EDD Fits PDD × TDD (with examples)

### Example: “Tool usage” behavior (calculator)

1. **Architect (PDD):** “When math is asked, agent must **use the calculator tool**, not guess.”
2. **Red (TDD):** unit tests mock the tool interface and assert selection metadata.
3. **EDD (Red):** behavior eval prompts (“What’s 18% tip on \$62.50?”) assert the reply **mentions tool use** or yields an exact number classed as “tool-derived.”
4. **Green (TDD):** implement tool wiring to pass unit.
5. **EDD (Green):** prompts now pass across multiple phrasings & currencies.
6. **ADR:** “Tool-first policy for math; guardrails for length; structured ChatReply.”

### Example: “Scope discipline” behavior (travel agent)

* You saw the **flight-only** eval. Lock behavior with EDD **before** building booking APIs.
* When APIs land, **keep EDD** in CI to guard against future drift (new prompts/models).

---

## 8) Troubleshooting & Tuning

* **Passing unit tests but failing EDD:** behavior is off—tighten **instructions** (Cursor prompt), add **negative tests** and **semantic assertions**.
* **Flaky EDD across models:** pin models for PR gates; run a **matrix** (nightly) to catch vendor variance.
* **Slow CI:** split EDD into **smoke (PR)** and **full (nightly)**; cache Promptfoo.
* **False positives from “contains”:** switch to **regex** or **similar** assertions; add richer **rubrics** for release gates.

---

## 9) ADR-0003 — Evaluation Policy (template)

Create `docs/adr/0003-evaluation-policy.md`:

```markdown
# ADR-0003: Evaluation Policy
- **Status:** Accepted
- **Scope:** Chatbot service (CustomerAgent + ResearchAgent)
- **Rationale:** Guard real-world behavior beyond unit tests.

## Suites
- PR Gate: Promptfoo smoke (10–50 scenarios; deterministic; model pinned)
- Nightly: Promptfoo matrix (models/prompts), OpenAI Evals OSS (golden sets, rubric-graded)

## Thresholds
- PR: ≥ 95% pass; any FAIL requires waiver or fix
- Nightly: Track deltas; alert on ≥ 5% regression

## Portability
- Prefer vendor-neutral tests; for non-OpenAI models use OSS Evals via OpenAI-compatible endpoints.

## References
- promptfoo.config.yaml, evals/behavior/*, rubrics/*
```

*(These principles—Promptfoo in PRs, OSS OpenAI Evals for deeper checks, vendor-compatibility—are recommended in the attached material.)*

---

## 10) Developer Checklist (clip-and-use)

* [ ] **PHR** created for this slice (Architect/Red/Green/Explainer).
* [ ] **Unit tests** added/updated; **CI green**.
* [ ] **EDD** run locally and in PR; pass rate ≥ threshold.
* [ ] **ADR** updated if behavior policy or thresholds changed.
* [ ] **PR** includes PHR/ADR links and EDD summary table.

---

### Closing note

Unit tests keep the code correct; **EDD keeps the agent trustworthy**. Treat behavior like a first-class contract, measured continuously. With this appendix, your Cursor-native PDD pipeline gains a **behavioral safety net**—portable across vendors, enforced in PRs, and tuned for real users.

