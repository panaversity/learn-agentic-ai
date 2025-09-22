# OpenAI Codex + VS Code IDE Playbook (2025): Prompt-Driven Development “…with a suit on”

> Build maintainable, production-ready software in **VS Code** with **OpenAI Codex**—without vibe-coding yourself into a rewrite. This playbook shows how to run **Prompt-Driven Development (PDD)** together with **TDD, ADRs, PR discipline**, **Prompt History Records (PHRs)**, and **uv** for Python deps, wiring agent logic with the **OpenAI Agents SDK**.
> Where relevant, I point to official docs for setup and API choices.

---

## 0) What you’ll have at the end

* A repeatable **VS Code + Codex workflow** for planning, generating, testing, and reviewing AI-written code.
* A lightweight Python service (FastAPI) with **/healthz** and **/chat** (non-streaming + SSE), powered by the **OpenAI Agents SDK**.
* **PHRs** (Prompt History Records), **ADRs** (decision memos), a **PR template**, and **CI gates**—so speed doesn’t kill quality.
* Ready-to-paste **prompts** (architect/red/green/refactor/explainer) for the first iterations.

---

## 1) Why VS Code + Codex

* **Codex inside VS Code** gives you repo-aware edits, file-scoped or multi-file diffs, and hands-off “agentic” tasks you can delegate from the editor. The official OpenAI docs describe the VS Code extension (“Work with Apps / VS Code extension”) and how to sideload/install it; once installed, Codex can operate on open files and your workspace. ([OpenAI Help Center][1])
* **VS Code** contributes repeatability with **Tasks**, launch configs, and a rich **Extension API**. You’ll use Tasks for deterministic local commands (tests, linters, docker), keeping Codex focused and your runs reproducible. ([Visual Studio Code][2])
* **OpenAI Agents SDK** provides minimal, production-oriented primitives—**Agent, Tools, Sessions, Handoff**—so your chatbot logic stays small and testable. Use the official SDK & docs.

---

## 2) One-time setup (VS Code + Codex + uv)

### 2.1 Install VS Code and Codex

1. Install **VS Code** from the official site. ([Visual Studio Code][4])
2. Install **OpenAI’s ChatGPT/Codex VS Code extension** (via Marketplace or VSIX). If you have a `.vsix` file, use **Command Palette → “Extensions: Install from VSIX”**. Sign in with your OpenAI account. ([OpenAI Help Center][1])

> Tip: Keep Codex scoped—work in a VS Code **folder workspace**, not loose files, so Tasks and project context apply. ([Visual Studio Code][2])

### 2.2 Initialize the Python project with uv

```bash
mkdir agents-chatbot && cd agents-chatbot
git init
uv init --python 3.12
uv add fastapi "uvicorn[standard]" pydantic python-dotenv httpx pytest ruff
uv add openai-agents   # OpenAI Agents SDK
mkdir -p app/agents app/guards tests docs/{adr,prompts,diagrams,pr} .github/workflows
echo "OPENAI_API_KEY=\nMODEL=gpt-5" > .env.sample
```

### 2.3 VS Code workspace hygiene

Create `.vscode/tasks.json` so CI-like commands are one keystroke:

```json
{
  "version": "2.0.0",
  "tasks": [
    { "label": "test", "type": "shell", "command": "uv run pytest -q", "problemMatcher": [] },
    { "label": "lint", "type": "shell", "command": "uv run ruff check .", "problemMatcher": [] },
    { "label": "run",  "type": "shell", "command": "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000" }
  ]
}
```

These mirror CI and keep Codex’s actions predictable.

---

## 3) PDD × TDD loop (…but with a suit on)

**PDD** = you design in **sequenced prompts** (intent, constraints, acceptance checks). **Codex** writes the code.
You advance in **baby steps**:

1. **Plan** → Architect prompt (micro-spec).
2. **Red** → tests only (failing).
3. **Green** → minimal diff to pass tests.
4. **Refactor** → keep tests green.
5. **Explain** → summarize diffs & trade-offs.
6. **Record** → ADR(s) for consequential decisions.
7. **Share** → small PR gated by CI.

---

## 4) Prompt History Records (PHRs)—“commit messages for prompts”

* Keep a **markdown** per meaningful step in `docs/prompts/NNNN-<slug>-<stage>.prompt.md`.
* Include: metadata, scope, acceptance, exact prompt you used, and outcome notes.
* Reviewers open PHRs to judge **intent vs. diff** at a glance.

> ADRs document **why**; PHRs document **what you asked the AI to do and how**. (Pair them in every PR.)

---

## 5) First three iterations (ready-to-paste prompts)

Paste these into Codex in VS Code (Side Panel or Chat view). **Always** set constraints like “minimal diff” and list the **files to touch** so the agent stays scoped.

### Iteration A — `/healthz`

**A1 — Architect (PHR-0001)**

```
Goal: Implement GET /healthz returning {"status":"ok"}.
Acceptance:
- Given GET /healthz Then HTTP 200 and body {"status":"ok"}
Constraints:
- minimal diff; no new deps; update README with a curl example
Out of scope:
- auth, db, tracing

Deliverables:
- app/main.py route
- tests/test_healthz.py (RED first)
- README snippet with curl
```

**A2 — Red (tests only) (PHR-0002)**

```
Create tests/test_healthz.py::test_healthz_ok expecting 200 and {"status":"ok"}.
No production code changes. Keep tests offline.
```

**A3 — Green (smallest diff) (PHR-0003)**

```
Make the smallest code change required to pass tests/test_healthz.py::test_healthz_ok.
Do not modify unrelated files. Output diff-only.
```

**A4 — Explainer (PHR-0004)**

```
Explain the diff in <=8 bullets; call out risks and follow-ups.
```

---

### Iteration B — `/chat` (non-streaming contract)

**B1 — Architect (PHR-0005)**

```
POST /chat {session_id, user_message} → JSON ChatReply {text, used_tool?, handoff:boolean}
Errors:
- 400 when user_message missing (error_code=MISSING_USER_MESSAGE)
Sessions:
- Maintain conversation per session_id (in-memory store)

Acceptance:
- test_chat_happy_path_returns_chatreply_shape -> 200 with fields {text, handoff}
- test_chat_missing_user_message_returns_400

Constraints:
- minimal diff; offline tests; no new deps
Deliverables:
- tests/test_chat_contract.py (RED)
- app/guards/schemas.py (ChatReply model)
- stubs in app/agents/core.py for session + runner
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
- Validate payload; 400 with error_code=MISSING_USER_MESSAGE if absent.
- Stub run that returns ChatReply {text, used_tool?: null, handoff: false}.
- In-memory sessions via app/agents/core.get_session(session_id).
Output diff-only.
```

**B4 — Explainer (PHR-0008)**

```
Summarize changes in 8 bullets; call out edge cases and coverage.
```

---

### Iteration C — Streaming via SSE (+ ADR)

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
- ADR "streaming-protocol-choice" (SSE vs WebSocket vs long-poll)
```

**C2 — Red (PHR-0010)** – tests for SSE headers + event format
**C3 — Green (PHR-0011)** – implement minimal SSE path
**C4 — ADR (PHR-0012)** – capture decision & consequences

---

## 6) Wiring the OpenAI Agents SDK (minimal, production-shaped)

**Concepts:** **Agent** (instructions + tools + optional `output_type`), **Tools** (function calls), **Sessions** (memory per `session_id`), **Handoff** (route to specialist). Official docs walk through each primitive.

**Prompt to Codex (when you’re ready to “green” the agent slice):**

```
Implement app/agents/core.py:
- get_customer_agent() with concise instructions; prefer tools for math/time.
- get_runner() suitable for streaming.
- get_session(session_id) using an in-memory dict.

Implement app/agents/tools.py with two function tools:
- calculator(expression: str) -> str (safe eval, handle errors)
- now(tz?: str) -> str (ISO timestamp; default UTC)

Register tools on the agent; set output_type=ChatReply for structured responses.
Add unit tests stubbing model calls (no network).
```

> Keep external dependencies small and test with **mocks**. The official SDK README/docsite is the source of truth for API names. 

---

## 7) Governance: ADRs, PRs, CI, and “no green, no merge”

* **ADRs** (Architecture Decision Records): context → options → decision → consequences; store in `docs/adr/`.
* **PRs**: small diffs; link PHR(s) & ADRs; include **test plan** and **rollback**.
* **CI** runs on every PR: `ruff` + `pytest` + (optional) docker build.

**PR template** (`.github/PULL_REQUEST_TEMPLATE.md`)

```markdown
# PR Title

## Summary
What changed and why.

## Prompt History (PHR)
- docs/prompts/00xx-*-architect.prompt.md
- docs/prompts/00xx-*-red.prompt.md
- docs/prompts/00xx-*-green.prompt.md

## ADRs
- docs/adr/00yy-*.md

## Test Plan
Commands, screenshots, curl.

## Risks & Rollback
Risks; how to rollback.

## Checklist
- [ ] Small diff
- [ ] CI green (ruff + pytest)
- [ ] ADR linked (if consequential)
- [ ] No secrets
```

**GitHub Actions** (`.github/workflows/ci.yml`)

```yaml
name: CI
on: [pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv venv && uv sync
      - run: uv run ruff check .
      - run: uv run pytest -q
```

---

## 8) “Vibe coding” vs PDD (…and how Codex helps)

* **Vibe coding** = intuition-driven prompting. Great for spikes. Risky for long-lived systems (ambiguous specs, flaky tests, architecture drift).
* **PDD** keeps creativity but adds **guardrails**: micro-specs, tests first, minimal diffs, documented decisions, PR gates.
* In VS Code, **Codex** excels when you **constrain scope**: point to specific files, list acceptance tests, and insist on diff-only outputs. Use VS Code **Tasks** to standardize test/lint runs so Codex’s changes are verified the same way humans do. ([Visual Studio Code][2])

---

## 9) Optional: add Evaluation-Driven Development (EDD)

Layer **behavioral evals** (Promptfoo or OpenAI Evals) on top of unit tests to check agent behavior on prompt suites (PR-time smoke; nightly deep). See OpenAI **Evals** docs and Cookbook for patterns; wire CI to fail on threshold drops.

---

## 10) Minimal code & config you’ll generate (reference)

**`app/main.py` sketch (non-streaming):**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.guards.schemas import ChatReply

app = FastAPI(title="Agents Chatbot")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

class ChatIn(BaseModel):
    session_id: str
    user_message: str | None = None

@app.post("/chat", response_model=ChatReply)
def chat(payload: ChatIn):
    if not payload.user_message:
        raise HTTPException(400, detail={"error_code": "MISSING_USER_MESSAGE"})
    # stub until agent is wired:
    return ChatReply(text="Hello!", used_tool=None, handoff=False)
```

**`app/guards/schemas.py`**

```python
from pydantic import BaseModel
from typing import Optional

class ChatReply(BaseModel):
    text: str
    used_tool: Optional[str] = None
    handoff: bool = False
```

**VS Code Tasks** (see §2.3) keep runs deterministic.

---

## 11) Diagrams to include (generate with your favorite tool)

* **System context**: Client → FastAPI → Agents SDK → Tools / Tracing / CI / Registry / Runtime
* **Sequence**: POST `/chat` (non-streaming & SSE)
* **Contract**: `ChatReply` class + error envelope
* **PDD loop**: Plan → Red → Green → Refactor → Explain → Record → PR
* **Traceability**: PHR ↔ ADR ↔ PR ↔ Commits

---

## 12) First hour: exact moves in VS Code

1. Open folder → **Task: test** (should fail until you add tests).
2. Paste **A1 Architect** → accept test file + route stubs; run **Task: test** (RED).
3. Paste **A3 Green** → accept minimal diff; run **Task: test** (GREEN).
4. Paste **B1 Architect** → create contract tests for `/chat` (RED).
5. Paste **B3 Green** → minimal `/chat`; run tests (GREEN).
6. Paste **C1/C3** → add SSE tests (RED) then minimal SSE streaming (GREEN).
7. Open a **PR** with PHR/ADR links; **CI green**; merge.

---

## 13) Tips that keep Codex effective in VS Code

* **Scope prompts**: list files to touch, insist on “diff-only,” and restate acceptance tests.
* **Prefer many small prompts** over one huge one—Codex’s planning is good, your governance is better.
* **Fail fast**: run **Tasks** locally; wire CI to mirror them exactly.
* **Explain**: ask Codex for an 8-bullet explainer after each change; paste into the PHR outcome.

---

## 14) References & further reading

* OpenAI **Agents SDK**: GitHub & docsite (Agents, Tools, Sessions, Handoffs). ([GitHub][3])
* OpenAI **VS Code integration** (“Work with Apps”/extension install). ([OpenAI Help Center][1])
* VS Code **Tasks** & **Extension API** (for advanced automation). ([Visual Studio Code][2])
* OpenAI **Evals** (API & Cookbook) for EDD. ([OpenAI Platform][6])

---

### Final word

Summer 2025 made AI pair-dev **table stakes**. The teams who win aren’t just “using Codex”—they’re **operationalizing** it with **PDD + TDD + ADR + PR**. Keep the creative spark, but **put a suit on it**: tiny, test-guarded prompts; documented decisions; PR-gated merges. VS Code gives you the rails; Codex supplies the horsepower; this playbook keeps the train on time.

[1]: https://help.openai.com/en/articles/10128592-how-to-install-the-work-with-apps-visual-studio-code-extension?utm_source=chatgpt.com "How to install the Work with Apps Visual Studio Code ..."
[2]: https://code.visualstudio.com/docs/debugtest/tasks?utm_source=chatgpt.com "Integrate with External Tools via Tasks"
[3]: https://github.com/openai/openai-agents-python?utm_source=chatgpt.com "openai/openai-agents-python: A lightweight, powerful ..."
[4]: https://code.visualstudio.com/docs?utm_source=chatgpt.com "Documentation for Visual Studio Code"
[5]: https://openai.github.io/openai-agents-python/?utm_source=chatgpt.com "OpenAI Agents SDK"
[6]: https://platform.openai.com/docs/guides/evals?utm_source=chatgpt.com "Evaluating model performance - OpenAI API"


Below is an **extension** to the *OpenAI Codex + VS Code IDE Playbook (2025): PDD “…with a suit on”*, plus a full **Appendix: Evaluation-Driven Development (EDD) with promptfoo**. It plugs cleanly into the PDD × TDD × ADR × PR workflow you already have.

---

# Extended Sections (Playbook Add-Ons)

## 9½) Where EDD fits in your loop

PDD gives you **specs via prompts**; TDD proves **code units** behave; **EDD** proves your **end-to-end behavior** (what the *agent actually says/does* across realistic prompts). Treat it like **contract tests for language behavior**.

**Updated loop**
Plan (Architect) → **Red (unit tests)** → Green (unit) → **EDD (behavior tests)** → Refactor → Explain → Record (ADR) → PR

**Gate policy**

* PRs must pass: **lint + unit tests + EDD smoke** (small, fast suite).
* Nightly/weekly: **EDD full** (bigger scenario sets and model matrix).

---

## 10) Repo layout add-ons

Add a first-class `evals/` area:

```
evals/
  behavior/
    001-scope-discipline.yaml
    002-math-tool-usage.yaml
  datasets/
    math_questions.csv
    scope_prompts.csv
  rubrics/
    clarity.md
    faithfulness.md
promptfoo.config.yaml
```

* `behavior/*.yaml` – small, human-readable behavior suites.
* `datasets/*.csv` – large scenario tables.
* `rubrics/*.md` – written criteria for model-graded or rubric-based checks.
* `promptfoo.config.yaml` – the runner config (providers, thresholds, output formats).

---

## 11) VS Code tasks for EDD

Extend your `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    { "label": "test", "type": "shell", "command": "uv run pytest -q" },
    { "label": "lint", "type": "shell", "command": "uv run ruff check ." },
    { "label": "run",  "type": "shell", "command": "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000" },
    { "label": "edd:smoke", "type": "shell", "command": "promptfoo eval --config promptfoo.config.yaml --suite smoke" },
    { "label": "edd:full",  "type": "shell", "command": "promptfoo eval --config promptfoo.config.yaml --suite full" }
  ]
}
```

---

# Appendix — Evaluation-Driven Development (EDD) with **promptfoo**

> Goal: make **behavior** measurable, repeatable, and **gated in CI**—so your agent doesn’t regress when prompts, tools, or models change.

## A. Install and wire promptfoo

1. Install globally (or as a dev dependency if you prefer):

```bash
npm i -g promptfoo
# or: npm i -D promptfoo
```

2. Create `promptfoo.config.yaml` at repo root:

```yaml
# Promptfoo master config
# You can run smaller named suites with: promptfoo eval --suite smoke

defaultTest:
  # Fallback assertions if a test omits them
  assert:
    - type: not-contains
      value: "I'm just an AI"   # Example of avoiding generic disclaimers
  options:
    timeoutMs: 15000

providers:
  # Hit your local agent API in dev/CI (recommended)
  - id: 'api:fastapi-agent'
    label: 'Local Agent /chat'
    config:
      url: 'http://localhost:8000/chat'
      method: 'POST'
      headers:
        Content-Type: 'application/json'
      body: |
        {
          "session_id": "eval-{{ N }}",
          "user_message": "{{prompt}}"
        }
      # Map your service response to a plain text string to test
      response: '{{ output.text ?? text ?? output }}'

suites:
  smoke:
    prompts:
      - file://evals/behavior/001-scope-discipline.yaml
      - file://evals/behavior/002-math-tool-usage.yaml
    thresholds:
      # Fail PR if pass rate drops below this
      passRate: 0.95

  full:
    prompts:
      - file://evals/behavior/*.yaml
      - file://evals/datasets/*.csv
    thresholds:
      passRate: 0.97
    options:
      # Example: retry-once to reduce flake; keep low for determinism
      maxRetries: 1
```

> **Tip:** Add additional providers for cross-model checks (e.g., OpenAI, Anthropic). Start with your **API provider** for deterministic CI gating.

---

## B. Write behavior tests

### B1. Scope discipline (keep the bot in-bounds)

`evals/behavior/001-scope-discipline.yaml`:

```yaml
tests:
  - name: "Out-of-scope politely declines"
    vars:
      prompt: "Can you reset my AWS root password?"
    assert:
      - type: contains
        value: "I can’t help with that"
      - type: not-contains
        value: "Here are the steps"
  - name: "In-scope responds helpfully"
    vars:
      prompt: "What’s the time in UTC right now?"
    assert:
      - type: regex
        value: "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}"  # ISO-ish time surface
```

### B2. Tool usage policy (math goes to `calculator`)

`evals/behavior/002-math-tool-usage.yaml`:

```yaml
tests:
  - name: "Tips are computed, not guessed"
    vars:
      prompt: "What is an 18% tip on $62.50?"
    assert:
      - type: contains
        value: "18%"
      - type: similar
        value: "The tip is 11.25"  # semantic compare, not exact phrasing
        threshold: 0.80
```

> If you expose metadata (e.g., `used_tool`) in your response, assert it too:

```yaml
assert:
  - type: javascript
    value: |
      // For structured responses, you can access parsed JSON if provider maps it.
      // Return true/false to pass/fail.
      !!(context?.rawJson?.used_tool?.toLowerCase().includes('calculator'))
```

### B3. CSV-driven scenarios (scale up fast)

`evals/datasets/math_questions.csv`:

```csv
prompt,expected
"What is 15% of 80?","12"
"Add 3.5 and 6.7","10.2"
"Calculate 10% tip on 47.25","4.725"
```

Reference it from a behavior file:

```yaml
tests:
  - dataset: file://evals/datasets/math_questions.csv
    assert:
      - type: javascript
        value: |
          // Require the numeric expected value to appear in output
          const target = String(expected).replace(/\\s+/g,'').toLowerCase();
          const out = String(output).replace(/\\s+/g,'').toLowerCase();
          out.includes(target)
```

---

## C. Run EDD locally

```bash
# Start your API if needed
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Smoke (quick, good for PR pre-check)
promptfoo eval --suite smoke

# Full matrix (slower, do before merging or on a schedule)
promptfoo eval --suite full
```

Promptfoo shows a table with pass/fail counts and diffs. Fix intent or prompts until green.

---

## D. CI: make EDD a merge gate

Extend `.github/workflows/ci.yml`:

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
      - name: Start API (background)
        run: |
          python -m venv .venv && . .venv/bin/activate
          pip install uvicorn fastapi pydantic
          nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
          sleep 2
      - name: EDD smoke
        run: promptfoo eval --config promptfoo.config.yaml --suite smoke --format junit --output results/edd.xml
      - name: Upload EDD report
        uses: actions/upload-artifact@v4
        with:
          name: edd-report
          path: results/edd.xml
```

**PR policy**: “No green, no merge.” Unit tests **and** EDD smoke must pass.

---

## E. Governance: ADR for evaluation policy

Add **`docs/adr/0003-evaluation-policy.md`**:

```markdown
# ADR-0003: Evaluation Policy
- **Status:** Accepted
- **Scope:** CustomerAgent + tools; /chat endpoint
- **Why:** Prevent behavior regressions; vendor-neutral evals

## Suites
- PR Gate: promptfoo smoke (≤ 60s)
- Nightly: promptfoo full (datasets, semantic checks)

## Thresholds
- PR: passRate ≥ 95%
- Nightly: passRate ≥ 97%; alert on -5% delta

## Determinism
- Pin model/version for PR; allow matrix nightly
- Keep retries low (≤1); fail loud on drift

## Artifacts
- Results stored under CI artifacts
- EDD summaries referenced in PRs

## Change control
- Evaluation changes require ADR update
```

---

## F. Patterns that reduce flakiness

* **Constrain outputs** (e.g., reply length, JSON schema) and **test the shape** first.
* Use **semantic assertions** sparingly—good for phrasing variance, not for math.
* Split suites: **smoke (fast & deterministic)** vs **full (thorough & slower)**.
* Prefer **provider: API** (your service) for PRs; add external model providers in nightly jobs.
* Keep datasets **small but representative**; rotate and grow them as the product grows.

---

## G. Failure triage (what to do when EDD fails)

1. **Read the diff**: is it a *prompt* problem, a *tooling* bug, or *drift*?
2. If it’s a prompt/spec gap → write an **Architect PHR** that tightens instructions and acceptance checks; re-run EDD locally.
3. If it’s code/tool → TDD (unit tests) first, then **Green**; re-run EDD.
4. If it’s model variance → pin model for PR gates; keep matrix coverage nightly; document in ADR.

---

## H. Ready-to-paste PHRs for EDD integration

**PHR — Architect (EDD policy & smoke suite)**
`docs/prompts/0100-edd-architect.prompt.md`

```markdown
Goal: Add promptfoo EDD with a smoke suite to gate PRs.
Acceptance:
- `promptfoo eval --suite smoke` passes locally
- CI job `edd` runs smoke and uploads a report
Constraints:
- Minimal changes; no runtime deps; providers use local API
Deliverables:
- promptfoo.config.yaml with suites {smoke, full}
- evals/behavior/001-scope-discipline.yaml
- evals/behavior/002-math-tool-usage.yaml
- docs/adr/0003-evaluation-policy.md (Accepted)
```

**PHR — Green (wire CI gate)**
`docs/prompts/0101-edd-green.prompt.md`

```markdown
Make the smallest changes to run `edd` job in CI:
- Add edd job to .github/workflows/ci.yml
- Ensure it starts API and runs smoke suite
- Upload JUnit report artifact
```

---

## I. Developer cheat-sheet

* **Run locally**: `promptfoo eval --suite smoke`
* **Before pushing**: VS Code Tasks → `lint` → `test` → `edd:smoke`
* **PR description**: paste pass rate; attach link to EDD artifact; reference ADR-0003
* **Nightly failures**: attach matrix diff; open an Architect PHR to address drift

---

### Closing thought

Unit tests protect **logic**; **EDD** protects **behavior**—the thing users actually experience. By adding a **promptfoo smoke gate** to every PR (and a richer nightly suite), you turn “we hope it still behaves” into **we measure that it behaves**. That’s how you keep shipping fast **without** vibe-coding your way into regressions.

