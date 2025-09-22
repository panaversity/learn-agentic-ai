# What is Spec-Driven Development?

**[Spec-Driven Development (SDD)](https://thenewstack.io/spec-driven-development-the-key-to-scalable-ai-agents/)** is a method where you put a **clear, testable specification** in front of the AI (and your team) *before* any code is generated. The spec defines behavior, contracts, constraints, risks, and acceptance tests; the AI (agent/IDE) then implements to that spec. SDD is presented as a practical antidote to “vibe coding” and a requirement for scaling AI-built systems—particularly agentic apps—because it forces clarity, repeatability, and governance (tests/PRs/ADRs) from day one. ([The New Stack][1])

In 2025, this matters because:

* AI IDEs and agent SDKs can turn ambiguous prompts into a lot of code quickly. Without a spec, you just get **elegant garbage faster**. ([The New Stack][1])
* Agent platforms (e.g., **OpenAI Agents SDK**) make multi-tool, multi-agent orchestration cheap—but the **cost of weak specifications is amplified** at scale. ([openai.github.io][2])
* The broader ecosystem (e.g., GitHub’s recent “spec-driven” tooling push) is converging on **spec-first workflows** for AI software. ([The GitHub Blog][3])

---

# SDD vs. PDD (and why they pair well)

* **PDD (Prompt-Driven Development)**: You develop by **sequencing prompts** (architect → red → green → refactor → explain), letting the AI generate diffs/tests/docs in **small, verified steps**. Great for velocity and tight feedback. ([Capgemini Software Engineering][4])
* **SDD (Spec-Driven Development)**: You develop by **writing the spec first**—API contracts, behaviors, constraints, and acceptance checks—then prompting the AI to implement *to the spec*. Great for **consistency, scaling, and team alignment**. ([The New Stack][1])

Think of SDD as **PDD’s backbone**: you still drive with prompts, but every prompt anchors to a **single source-of-truth spec**. That’s how you avoid “prompt drift.”

---

# Core elements of an SDD spec (adapted to agentic apps)

From the New Stack guidance and current industry patterns, a good spec for an AI/agent system includes: ([The New Stack][1])

1. **Scope & Outcomes** — The problem, users, boundaries, non-goals.
2. **Interfaces & Contracts** — Endpoints, request/response schemas, error envelopes, streaming rules.
3. **Agent Behaviors** — Roles, tools (and when to use them), handoff rules, guardrails, output shape.
4. **Acceptance Tests** — Given/When/Then checks and contract tests (TDD starter).
5. **Operational Constraints** — Latency/limits, privacy/security, observability/tracing.
6. **Change Control** — ADR linkage, PR policy, versioning, and migration notes.

---

# SDD in action — mapped to our examples

Below are **spec snippets** you can drop into `docs/specs/` (Markdown or YAML). Each immediately feeds a PDD step (architect → red → green).

## 1) `/healthz` (hello world done right)

**Spec (excerpt)**

```markdown
# Spec: Health Endpoint

Goal
- Provide a health probe for the service.

Contract
- GET /healthz -> 200 {"status":"ok"}

Acceptance
- When GET /healthz Then status=200 And body={"status":"ok"}

Non-goals
- Auth, tracing, DB checks.
```

**PDD move:** Paste this spec into your **Architect prompt**, then “**Red**: add failing test,” then “**Green**: minimal diff.”
Result: deterministic first commit anchored to a spec (not vibes).

## 2) `/chat` (non-streaming contract)

**Spec (excerpt)**

```markdown
# Spec: Chat Endpoint (v1)

Request
- POST /chat {session_id: str, user_message: str}

Response (structured)
- ChatReply { text: str, used_tool?: str, handoff: bool }

Errors
- 400 {error_code:"MISSING_USER_MESSAGE"}
- 415 for wrong content-type (future)

Behavior
- Maintain session state by session_id.
- Default path: CustomerAgent produces concise text under 1200 chars.
```

**PDD move:**

* **Red:** tests `test_chat_missing_user_message_returns_400`, `test_chat_happy_path_returns_chatreply_shape`.
* **Green:** minimal implementation that returns valid `ChatReply`.
  Your AI implements to the **contract you wrote**, not whatever it “thinks.”

## 3) Streaming via **SSE**

**Spec (excerpt)**

```markdown
# Spec: Chat Streaming (SSE)

Trigger
- If request Accept: text/event-stream, stream tokens.

Protocol
- Content-Type: text/event-stream
- Events: "data:<token>\n\n"
- Terminator: "data:[DONE]\n\n"

Fallback
- If Accept != SSE => return JSON ChatReply.

Acceptance
- SSE test asserts correct headers and at least one "data:" line.
```

**PDD move:**

* **Red:** streaming tests.
* **Green:** minimal SSE code path.
* **ADR:** “Why SSE (vs WS/long-poll) for v1?” (link it).
  This is pure SDD: **protocol first**, code second.

## 4) **Tools** & **Guardrails** (Agent policy)

**Spec (excerpt)**

```markdown
# Spec: Agent Tools & Guardrails

Agent
- CustomerAgent: helpful, concise, ≤1200 chars.

Tools
- calculator(expression) -> str
- now(tz?) -> ISO timestamp

Policy
- Math/time -> prefer tools; do not guess.
- Output must satisfy Pydantic ChatReply.
- On validation failure, retry once; else return friendly error.

Acceptance
- When asked "18% tip on $62.50", response includes correct value.
- "used_tool" may surface, or EDD proves tool-first behavior.
```

**PDD move:**

* **Red:** unit tests for contract + **EDD smoke** for behavior (using `promptfoo`).
* **Green:** wire tool calls to meet tests and behavior thresholds.
  This is *exactly* what the New Stack piece means by scaling beyond vibe coding—**codify behavior and policy**, not just “make it work.” ([The New Stack][1])

## 5) **Handoff** to a ResearchAgent

**Spec (excerpt)**

```markdown
# Spec: Agent Handoff

Rule
- If intent = RESEARCH (confidence ≥0.7), hand off to ResearchAgent.

Traceability
- Include "handoff_reason" in logs and response metadata.

Acceptance
- Mocked test forces handoff path and asserts presence of handoff_reason.
```

**PDD move:**

* **Red:** tests for handoff.
* **Green:** minimal routing + metadata.
  The spec keeps **multi-agent complexity** understandable for humans, not just models.

---

# Example: SDD-to-PDD prompt (ready to paste)

> “You are acting as a software engineer implementing to a written specification. Use the attached spec `docs/specs/spec-chat-v1.md`.
> **Task:** Add `/chat` (non-streaming).
> **Constraints:** minimal diff; touch only `app/main.py`, `app/guards/schemas.py`, `tests/test_chat_contract.py`; no new deps; output diff-only.
> **Acceptance:** implement tests in `tests/test_chat_contract.py` for (a) 400 when `user_message` missing, (b) 200 with `ChatReply` shape.
> **After implementing,** produce a short explainer (≤8 bullets) and update `README.md` with a curl example.”

This is **PDD execution** *against* a **pre-written SDD spec**.

---

# How SDD integrates with ADRs, PRs, and EDD

* **ADRs**: Use ADRs to document **why** a spec makes certain choices (e.g., *SSE over WebSocket*). Link ADRs *from the spec* and in PRs.
* **PRs**: Small diffs, **link to spec + PHR(s) + ADR(s)**; CI must pass contract tests; reviewers check **spec compliance** not just code style.
* **EDD (promptfoo)**: Add **behavior suites** that reflect the spec’s rules (e.g., “math uses calculator”). Gate PRs with a **smoke** suite and run a **full** suite nightly to detect drift. (This pattern is common in modern SDD toolkits and aligns with the New Stack article’s emphasis on scalable, testable agent behavior.) ([The GitHub Blog][3])

---

# Anti-patterns SDD helps you avoid

1. **Prompt drift** — different prompts implying different requirements.
   *Mitigation:* one **versioned spec**; prompts reference that spec ID. ([The New Stack][1])
2. **Hidden behavior** — agents “feel right” but lack explicit rules.
   *Mitigation:* write **behavioral policy** (tools, handoffs, guardrails) in the spec and test with EDD. ([The New Stack][1])
3. **Unbounded scope** — “add summarize” leads to cascading changes.
   *Mitigation:* spec a **thin slice** with explicit non-goals first (our `/summarize` case study illustrated how PDD+TDD beat vibes). ([The New Stack][1])

---

# A minimal SDD template (drop in `docs/specs/…`)

```markdown
# Spec: <feature-id and title>
Version: v1
Status: Draft | Accepted
Owner: <team/person>
Linked ADRs: <list>

## 1) Scope & Outcomes
- Problem, users, non-goals.

## 2) Interfaces & Contracts
- Endpoints, schema, errors, streaming/timeout limits.

## 3) Agent Behavior & Policies
- Roles, tools & “when to use,” handoff rules.
- Guardrails (output shape, length caps, retries).

## 4) Acceptance (tests you expect to pass)
- Given/When/Then checks.
- Contract tests & (optionally) EDD behaviors.

## 5) Ops & Constraints
- Observability/tracing, PII/keys, allowed external calls.

## 6) Change Control
- ADR links, PR checklist, versioning/migration.
```

---

# Where OpenAI Agents SDK fits

SDD defines **what** to build; the **OpenAI Agents SDK** gives you minimal primitives to build it—**Agents**, **Tools**, **Sessions**, **Handoffs**, **Guardrails**, **Tracing**—with just enough structure to map your spec cleanly into code and tests. It’s intentionally lightweight and production-oriented, which makes it a good match for SDD. ([openai.github.io][2])

---

# Putting it all together (step-by-step)

1. **Write the spec** for a tiny slice (e.g., `/chat` contract).
2. **Architect prompt** (PDD) says: “Implement to Spec X; minimal diff; files Y/Z only; produce tests first (RED).”
3. **Run tests (RED)** → **Green** minimal code → **Explain** diff → **Record** ADR/PHR.
4. **Add EDD** checks that mirror behavior policy (e.g., tool-first math).
5. **Open PR** linking spec + ADR + PHR, gated by CI (lint, unit, EDD smoke).
6. **Iterate**: extend the spec for streaming, tools, handoffs; repeat.

---

## TL;DR

* **SDD**: **Spec first, implementation second**—especially critical for **agentic** systems. ([The New Stack][1])
* **PDD**: Use **sequenced prompts** to implement the spec in **baby steps** with tests. ([Capgemini Software Engineering][4])
* **Together**: SDD gives you **clarity & scale**; PDD gives you **speed & iteration**; **ADRs/PRs/EDD** keep it **governed & stable**.
* **Tooling**: OpenAI **Agents SDK** maps directly to SDD sections (agents, tools, handoffs, guardrails, sessions). ([openai.github.io][2])

If you want, I can convert our earlier `/chat` and SSE specifications into ready-to-commit `docs/specs/` files and add a **prompt that enforces “implement to spec”** in Cursor or Codex.

[1]: https://thenewstack.io/spec-driven-development-the-key-to-scalable-ai-agents/?utm_source=chatgpt.com "Spec-Driven Development: The Key to Scalable AI Agents"
[2]: https://openai.github.io/openai-agents-python/?utm_source=chatgpt.com "OpenAI Agents SDK"
[3]: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/?utm_source=chatgpt.com "Spec-driven development with AI: Get started with a new ..."
[4]: https://capgemini.github.io/ai/prompt-driven-development/?utm_source=chatgpt.com "Prompt Driven Development - Capgemini Software Engineering"

## Attachment

Done! I’ve created ready-to-commit **SDD spec files** and matching **“implement-to-spec” PHR prompts** you can drop into either repo (Cursor or VS Code + Codex).

**Download the bundle:**
specs-pdd-sdd-bundle.zip

### What’s inside

* `docs/specs/spec-chat-v1.md` — **/chat (non-streaming) spec**: scope, contract, behaviors, acceptance tests, ops & change control.
* `docs/specs/spec-chat-streaming-sse-v1.md` — **SSE streaming spec**: trigger, protocol, terminator, fallback, tests.
* `docs/adr/0002-streaming-protocol-choice.md` — ADR draft comparing **SSE vs WebSocket vs long-poll** and the v1 decision.
* `docs/prompts/0102-implement-to-spec-chat-green.prompt.md` — **Green** prompt instructing the AI to implement strictly to the **/chat** spec (diff-only, minimal scope, acceptance checks).
* `docs/prompts/0103-implement-to-spec-sse-green.prompt.md` — **Green** prompt for **SSE** per the streaming spec (headers, `data:<token>\n\n`, `data:[DONE]\n\n`, JSON fallback).

### How to use

1. Unzip into the root of your repo (Cursor or VS Code project).
2. Open the relevant **PHR prompt** in your IDE (Codex or Cursor) and paste it to run the **Green** step against the spec.
3. Add **Red tests** first if you haven’t already (per the “Acceptance” sections).
4. Commit with the PHR/ADR links in your PR description.

## Second Attachment

Here you go — **RED tests ready to drop in**. They target the layout we’ve been using (`app/main.py` FastAPI app; `/chat` endpoint) and will fail until you implement to the **specs** we created.

* **Download:** red-tests-bundle.zip

### What’s inside

* `tests/test_chat_contract.py`

  * `test_chat_missing_user_message_returns_400_top_level_error_code()`

    * **FAILS now** by design: it expects a **top-level** error body `{"error_code":"MISSING_USER_MESSAGE"}`.
      Your current implementation raises `HTTPException(detail={...})`, which FastAPI renders as `{"detail": {...}}`.
      Fix: return a top-level error JSON for 400s to satisfy the spec.
  * `test_chat_happy_path_returns_chatreply_shape()`

    * Should pass once `/chat` returns `{"text": "...", "handoff": false, "used_tool": null}`.

* `tests/test_chat_streaming.py`

  * `test_streaming_sends_event_stream_headers()`
  * `test_streaming_emits_at_least_one_data_line_and_done()`

    * **Both FAIL now** until you implement SSE per the streaming spec:

      * `Content-Type: text/event-stream`
      * Event lines as `data:<token>\n\n`
      * Terminator `data:[DONE]\n\n`

### How to run (VS Code Tasks or terminal)

```bash
uv run pytest -q
# Expect: 1 failing (contract 400 shape) + 2 failing (SSE) = RED
```

### Next steps (spec → PDD loop)

1. **RED:** drop these tests into your repo and run them.
2. **GREEN (non-streaming):** use the “Implement to Spec — /chat (non-streaming)” prompt we generated to:

   * Return top-level `{"error_code": ...}` on 400.
   * Preserve the `ChatReply` shape on 200.
3. **GREEN (SSE):** use the SSE “Implement to Spec” prompt to:

   * Add `Accept: text/event-stream` handling.
   * Stream `data:<token>\n\n` and close with `data:[DONE]\n\n`.

## Update

Here’s an updated **`.github/PULL_REQUEST_TEMPLATE.md`** with a dedicated **“Spec compliance”** checkbox (and a small section to link the spec you implemented against).

```markdown
# PR Title

## Summary
What changed and why.

## Linked Spec(s)
- Spec: `docs/specs/<spec-file>.md` (version & status)
- ADRs: `docs/adr/<id>-*.md` (if applicable)
- PHRs: `docs/prompts/<id>-*.prompt.md` (architect/red/green/refactor/explainer)

## Test Plan
Commands, screenshots, or `curl` showing success paths and error paths.
- `uv run pytest -q`
- (optional) `promptfoo eval --suite smoke` results

## Risks & Rollback
Known risks; how to revert safely.

---

## Checklist
- [ ] **Small diff** (scoped to files listed in PHR/spec)
- [ ] **Spec compliance**  
      — Links to spec above; contracts, behaviors, and constraints implemented as written  
      — All **acceptance tests** from the spec are present and passing  
      — (If applicable) **EDD smoke** suite passes (no regression)
- [ ] **CI green** (ruff + pytest; EDD if configured)
- [ ] **PHR linked** (the exact prompts used)
- [ ] **ADR linked** (for consequential design decisions)
- [ ] **No secrets** (uses `.env`; no keys in code or prompts)
- [ ] **Docs updated** (README/examples if public surface changed)
```

### How to apply

Replace your existing template at:

```
.github/PULL_REQUEST_TEMPLATE.md
```

### Notes

* The **Linked Spec(s)** section makes reviewers check the actual spec file alongside the diff.
* The **Spec compliance** checkbox is explicit: you affirm contracts, behaviors, and constraints from the spec—and that the spec’s acceptance tests (and optional EDD smoke) are green.



