# Diagram Prompts

Here’s a copy-paste pack of **Nano Banana** prompts to generate every diagram we’ve used in all our learning material in this chapter (and a few extras teams usually want). Each prompt is self-contained and tells the model what to draw, the style, constraints, and what to label. just paste one prompt at a time into Nano Banana and export as SVG/PNG.

---

## 1) System Context (high-level architecture)

**Prompt (copy-paste):**

```
You are a diagramming assistant. Create a clean SYSTEM CONTEXT diagram titled
"AI Chatbot — System Context". Style: minimal, readable, light grid, no clip art.

Include these nodes and relationships:
- Client (Web UI/CLI)
- FastAPI Service (/chat, /healthz)
- OpenAI Agents SDK (Agents, Runner, Sessions)
- Tools (calculator, now, future: RAG)
- Tracing/Logs
- Config/Secrets (.env)
- CI (lint, tests, docker build)
- Registry (container images)
- Runtime (Uvicorn container)

Edges:
- Client -> FastAPI: POST /chat (JSON or SSE)
- FastAPI -> Agents SDK: run(session, tools)
- Agents SDK -> Tools: function_tool invocations
- FastAPI -> Tracing/Logs: spans + events
- CI -> Registry -> Runtime: build/push/deploy
- FastAPI -> Config/Secrets: reads on startup

Constraints:
- Group SDK and Tools as one cluster ("Agent Runtime")
- Show protocols on edges where relevant: HTTP, SSE
- Keep labels short; prefer straight lines.

Output: export as vector (SVG). Provide a transparent background if possible.
```

---

## 2) Runtime Sequence — /chat (non-streaming)

**Prompt:**

```
Draw a SEQUENCE DIAGRAM titled "POST /chat (non-streaming)".

Lifelines:
- User
- FastAPI (/chat)
- Session Store
- CustomerAgent (via Agents SDK)
- Tools

Steps:
1) User -> FastAPI: POST /chat {session_id, user_message}
2) FastAPI -> Session Store: get_or_create(session_id)
3) FastAPI -> CustomerAgent: run(message, session, tools)
4) CustomerAgent -> Tools: (optional) calculator/now
5) Tools -> CustomerAgent: result
6) CustomerAgent -> FastAPI: ChatReply {text, used_tool?, handoff=false}
7) FastAPI -> User: 200 JSON

Notes:
- Mark optional tool call with 'alt tool-needed'
- Emphasize structured ChatReply in response

Style: compact lifelines, balanced spacing. Output SVG.
```

---

## 3) Runtime Sequence — /chat with SSE streaming

**Prompt:**

```
Create a SEQUENCE DIAGRAM titled "POST /chat (SSE streaming)".

Actors:
- User
- FastAPI (/chat)
- CustomerAgent (runner.stream)
- Tools (optional)

Flow:
- User -> FastAPI: POST /chat (Accept: text/event-stream)
- FastAPI -> CustomerAgent: stream(user_message, session)
- loop token streaming
    CustomerAgent -> FastAPI: token
    FastAPI -> User: SSE "data:<token>\n\n"
- end loop
- FastAPI -> User: SSE "data:[DONE]\n\n"

Notes:
- Indicate headers: Content-Type: text/event-stream
- Optional tool call in a separate 'opt tools' section
- Call out JSON fallback in a footnote

Style: readable chunks, thin arrows, output SVG.
```

---

## 4) Agent Handoff — intent router

**Prompt:**

```
Design a STATE/ACTIVITY diagram titled "Agent Handoff Policy".

States/Nodes:
- Parse Intent
- Confidence Check
- Route: CustomerAgent
- Route: ResearchAgent
- Handoff Reason (log)
- Respond

Transitions:
- Parse Intent -> Confidence Check
- If intent = RESEARCH AND confidence >= 0.7 -> ResearchAgent
- Else -> CustomerAgent
- Both routes -> Handoff Reason -> Respond

Style: businesslike, minimal icons. Add guard conditions on transitions.
Output SVG.
```

---

## 5) Contract/Class Model — ChatReply

**Prompt:**

```
Draw a CLASS DIAGRAM titled "Contracts: ChatReply".

Classes:
- ChatReply
  - text: str
  - used_tool: Optional[str]
  - handoff: bool
- ErrorBody
  - error_code: str
  - message: str

Notes:
- Show types, mark Optional with ?
- Indicate that ErrorBody is returned on 4xx
- Keep it small and printable

Output SVG.
```

---

## 6) Deployment (Dev → CI → Runtime)

**Prompt:**

```
Create a DEPLOYMENT diagram titled "Pipeline: Dev to Runtime".

Nodes:
- Dev Workstation (Cursor / VS Code + Codex)
- GitHub (PRs)
- CI (ruff, pytest, coverage, docker build)
- Registry (image)
- Runtime (Uvicorn container, non-root user, healthcheck)
- Observability (logs/traces)

Edges:
- Dev -> GitHub: push PR (PHR, ADR links)
- GitHub -> CI: workflow run
- CI -> Registry: push image
- Registry -> Runtime: deploy/pull image
- Runtime -> Observability: traces, logs

Style: rectangular nodes, subtle cluster for “Platform”.
Output SVG.
```

---

## 7) Data Flow — sessions, tools, guardrails

**Prompt:**

```
Produce a DATA FLOW diagram titled "Chat Execution Data Flow".

Elements:
- Request: {session_id, user_message}
- Session Store (in-memory)
- Agent (instructions + tools)
- Tools (calculator, now)
- Guardrails (validate ChatReply; MAX_LEN=1200)
- Response: ChatReply

Arrows:
Request -> Agent
Agent <-> Session Store
Agent -> Tools (optional)
Tools -> Agent (result)
Agent -> Guardrails -> Response

Annotate constraints:
- No secrets in payload
- Validate ChatReply shape, length <= 1200

Style: left-to-right, labeled edges. SVG output.
```

---

## 8) Error Taxonomy — quick map

**Prompt:**

```
Draw a MIND MAP titled "Error Taxonomy".

Center: Errors
Branches:
- 400 Bad Request
  - Missing user_message (MISSING_USER_MESSAGE)
  - Invalid payload shape
- 415 Unsupported Media Type
  - Non-JSON POST
- 500 Internal Error
  - Tool failure
  - Runner exception
- Streaming
  - SSE headers missing
  - Proxy buffering issues

Style: compact, monochrome. Output SVG, printable.
```

---

## 9) CI Pipeline — gates & artifacts

**Prompt:**

```
Create a PIPELINE diagram titled "CI Gates".

Stages:
- Lint (ruff)
- Unit Tests (offline)
- Contract Tests (/chat)
- Build (Docker, uv)
- Publish (registry)
- Optional: Deploy (manual approval)

Artifacts:
- Test reports
- Docker image

Rules:
- "No green, no merge" gate between Tests and Build
- PR requires PHR/ADR links

Style: horizontal flow, check icons on gates. Output SVG.
```

---

## 10) Repository Map — folders & purpose

**Prompt:**

```
Render a REPOSITORY STRUCTURE diagram titled "Repo Map".

Folders:
- app/
  - agents/ (core, tools, customer, research)
  - guards/ (schemas, rules)
  - streaming.py
  - main.py
- tests/
- docs/
  - adr/
  - prompts/
  - diagrams/
  - pr/
- scripts/ (prompt_new.py, prompt_index.py, prompt_guard.py)
- .githooks/
- .github/workflows/

Annotate each folder with a 3-6 word purpose.
Style: tree layout, monospace labels. Output SVG.
```

---

## 11) Prompt-Driven Development — loop

**Prompt:**

```
Make a CYCLE diagram titled "PDD × TDD Loop (…but with a suit on)".

Nodes (in order):
- Plan (Architect Prompt)
- Red (Tests only)
- Green (Smallest diff)
- Refactor (keep tests green)
- Explain (Explainer prompt)
- Record (ADR)
- Share (PR w/ CI gates)

Arrows connect in a loop. Add tiny notes under each node (1 line).
Style: circular arrows, professional palette. Output SVG.
```

---

## 12) PR Lifecycle — with governance

**Prompt:**

```
Build a FLOWCHART titled "PR Lifecycle".

Steps:
- Open PR (includes PHR/ADR links)
- CI runs (lint/tests/build)
- Review (small diffs preferred)
- Gate: 'No green, no merge'
- Merge to main
- Tag & Release notes (optional)

Add side notes:
- Security: No secrets in prompts
- Observability: enable tracing on release

Style: swimlane feel (Dev vs CI/Review). Output SVG.
```

---

## 13) Knowledge/Prompt Artifacts — traceability

**Prompt:**

```
Design a RELATIONSHIP diagram titled "Traceability: Prompts ↔ ADRs ↔ PRs".

Entities:
- PHR (Prompt History Record)
- ADR (Architecture Decision Record)
- PR (Pull Request)
- Commit(s)

Links:
- PHR -> Commit (evidence of prompt-driven change)
- PR aggregates 1..n PHRs
- PR references 0..n ADRs
- ADR references supporting PHRs and PR
- Commit -> CI run

Style: crow's-foot notation or simple cardinalities (1..n). SVG output.
```

---

## 14) Streaming Headers — tiny reference card (bonus)

**Prompt:**

```
Create a SMALL REFERENCE CARD titled "SSE Headers & Events".

Show:
- Request: Accept: text/event-stream
- Response: Content-Type: text/event-stream
- Event format lines:
  - data:<token>\n\n
  - data:[DONE]\n\n

Add a note: "JSON fallback when Accept header is missing."
Style: index card layout, code font for header lines. Output SVG.
```

---

## 15) Security & Secrets — flow (bonus)

**Prompt:**

```
Draw a SIMPLE FLOW diagram titled "Secrets & Config Flow".

Nodes:
- .env (OPENAI_API_KEY, MODEL)
- Settings loader
- FastAPI app
- Agents SDK

Arrows:
.env -> Settings -> FastAPI -> Agents SDK

Add rule: "Never hardcode secrets. Use .env.sample and env vars."
Style: minimalist. Output SVG.
```

---

### Tips for Nano Banana

* If the tool supports **“revise”**, ask: *“tighten spacing”*, *“reduce label size”*, *“export with transparent background”*.
* Keep node counts modest; split big ideas into separate diagrams (above) rather than cramming.
* Use **consistent titles**—they become your document headings.


