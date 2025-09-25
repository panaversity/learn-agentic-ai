# What is ADR?

Great question—**ADR** stands for **Architecture Decision Record**.

It’s a short, permanent note that captures a **significant technical decision**, the **context** in which you made it, the **options** you considered, the **choice** you made, and the **consequences** (trade-offs). Think of it as a timestamped “why we did it this way” so future you (and teammates) don’t have to reverse-engineer your thinking.

# Why use ADRs

* **Traceability:** Link code to the reasoning behind it.
* **Onboarding:** New devs learn the system’s “why,” not just the “what.”
* **Consistency:** Prevents decision drift and repeated debates.
* **Auditability:** Helpful for security/compliance reviews.

# When to write one

* Picking a framework/SDK, runtime, or hosting model
* Defining APIs/contracts or data models
* Choosing cross-cutting concerns: auth, logging, observability, persistence
* Committing to patterns (events vs. RPC, monorepo vs. polyrepo, etc.)

# Typical ADR template (keep it 1–2 pages)

**Title:** Short and action oriented (e.g., “Use OpenAI Agents SDK for Chat Orchestration”)
**Status:** Proposed | Accepted | Superseded | Deprecated
**Date:** YYYY-MM-DD
**Context:** What problem/constraints led to this decision?
**Options:** Option A / Option B / Option C (pros/cons)
**Decision:** The chosen option and why
**Consequences:** Positive (benefits) and negative (costs/trade-offs)
**References:** Links to docs, issues, benchmarks, POCs

# Mini example

**ADR-0001: Use OpenAI Agents SDK for chatbot orchestration**

* **Status:** Accepted — 2025-09-19
* **Context:** We need multi-agent orchestration (tools, handoffs, sessions) with minimal boilerplate and strong streaming support.
* **Options:**

  * A) OpenAI Agents SDK (Python): native tools/sessions/handoffs, simple API, fast to iterate.
  * B) General agent frameworks (CrewAI/LangGraph): powerful graphs, but more setup and abstractions we don’t need now.
  * C) Custom orchestration: full control, slower to build, harder to maintain.
* **Decision:** Choose **OpenAI Agents SDK** to minimize complexity and ship faster.
* **Consequences:**

  * ✅ Faster delivery, straightforward tools + handoffs, good streaming ergonomics.
  * ⚠️ Some lock-in to SDK APIs; must track SDK changes.
* **References:** Project README, spike notes, performance test results.

**ADR-0002: Use SSE for streaming responses**

* **Status:** Accepted — 2025-09-19
* **Context:** Frontend requires token-level streaming; we prefer HTTP-friendly setup.
* **Options:** SSE vs. WebSocket vs. polling.
* **Decision:** **SSE** for simplicity and broad compatibility; keep WebSocket as future option.
* **Consequences:**

  * ✅ Easy to implement/deploy; works with proxies/CDNs.
  * ⚠️ One-way stream; for bi-directional features we’ll revisit WebSockets.

# Practical tips

* Keep ADRs **small and specific** (one decision per ADR).
* Use a **numbered folder** like `docs/adr/0001-...md`.
* Update **Status** when a decision is replaced; link to the superseding ADR.
* Reference ADR IDs in PR descriptions when the change implements a decision.

## Our Protocol for Maintaining a History of Prompts in Addition to ADRs

Love that. Treat prompts as **first-class engineering artifacts**—right next to ADRs—so anyone can replay how a change was conceived, constrained, and verified.

Here’s a lightweight, production-ready way to do it.

# Prompt History (PHR) — “ADRs for Prompts”

## Goals

* **Traceability:** Link every meaningful code change to the prompt(s) that produced it.
* **Reproducibility:** Make it easy to rerun or adapt a prior prompt with today’s context.
* **Governance:** Ensure prompts follow house rules (tests-first, smallest diff, no secrets).
* **Learning loop:** Build a searchable library of effective prompts and anti-patterns.

---

## Directory & Naming

```
docs/
  adr/
    0001-streaming-protocol.md
  prompts/
    0001-healthz-architect.prompt.md
    0002-healthz-red.prompt.md
    0003-healthz-green.prompt.md
    0004-healthz-refactor.prompt.md
    0005-chat-endpoint-architect.prompt.md
    index.md
```

**Convention**

* `NNNN-<slug>-<stage>.prompt.md`

  * `NNNN` = zero-padded sequence
  * `<stage>` ∈ {architect, red, green, refactor, explainer, adr-draft, pr-draft}
* One file per step keeps diffs tiny and lets you link specific moments in the PDD×TDD loop.

> Prefer **one “vertical slice” per PR** and a contiguous block of prompt files (e.g., 010–016).

---

## Minimal Schema (front-matter + body)

Put this at the top of each prompt file:

```markdown
---
id: 0005
title: Add /chat endpoint (non-streaming)
stage: architect           # architect | red | green | refactor | explainer | adr-draft | pr-draft
date: 2025-09-20
surface: cursor-composer   # cursor-inline | cursor-chat | cursor-composer | codex-cloud | codex-cli
model: gpt-5-codex         # or claude, gemini, etc.
repo_ref: commit:abc1234   # or branch name at time of prompt
scope_files:
  - app/main.py
  - tests/test_chat_contract.py
links:
  adr: docs/adr/0002-streaming-choice-sse.md
  issue: https://github.com/org/repo/issues/123
  pr: null
acceptance:
  - Given missing user_message, When POST /chat, Then HTTP 400 with code MISSING_USER_MESSAGE
  - Given valid payload, Then 200 JSON {text, used_tool, handoff}
constraints:
  - minimal diff, no new deps
  - tests offline (mocks)
out_of_scope:
  - streaming (handled later)
secrets_policy: "No secrets; use .env"
---
```

**Body (the actual prompt you pasted):**

```text
You are the software architect…
<full prompt text here>
```

**Outcome (append after run):**

```markdown
### Outcome
- Files changed: app/main.py, tests/test_chat_contract.py
- Tests added: test_missing_user_message_returns_400
- Next prompts: 0006 (red), 0007 (green)
- Notes: Cursor suggested adding pydantic model; accepted.
```

---

## Workflow Integration

### In PRs

* **Checklist**: “Prompt files linked?” (yes → list `docs/prompts/00xx-*.prompt.md`)
* **Body**: Link the architect/red/green prompt files and the ADR.
* **Policy**: **No green, no merge**; PR must reference at least the architect + red + green prompts.

### In Commits

* Include the prompt ID(s) in commit messages:

  ```
  feat(chat): add /chat contract (+tests)
  refs: PHR-0005, PHR-0006
  ```

### In ADRs

* Add a “Prompts” section with links to the architect and explainer prompts that led to the decision.

---

## Automation (nice-to-have, tiny scripts)

* **`make prompt:new SLUG=chat-endpoint STAGE=architect`**
  Generates a numbered `.prompt.md` with today’s date and your defaults.
* **Pre-commit hook**: If `app/**` changed and there’s no new `docs/prompts/**.prompt.md` or no reference to an existing prompt ID, warn or block.
* **`make prompt:index`**: Rebuild `docs/prompts/index.md` with a table of ID, title, stage, PR, ADR, and status.

Example `docs/prompts/index.md` row:

| ID   | Title                         | Stage     | PR   | ADR  | Date       |
| ---- | ----------------------------- | --------- | ---- | ---- | ---------- |
| 0005 | Add /chat endpoint (contract) | architect | #128 | 0003 | 2025-09-20 |

---

## Content Quality Tips

* **Write prompts like Issues**: file paths, acceptance criteria, constraints, out-of-scope.
* **Smallest viable unit**: one prompt per step (architect, red, green…), not mega-prompts.
* **Redact & reference**: never paste tokens or customer data; reference `${ENV}` or fixtures.
* **Determinism**: state “offline tests” and time/network mocking in constraints.
* **Explainers**: capture the 5–8 bullet “why and what changed” as part of the history.

---

## Example Files (short)

**`docs/prompts/0010-sse-streaming-architect.prompt.md`**

```markdown
---
id: 0010
title: Add SSE streaming to /chat (fallback JSON)
stage: architect
date: 2025-09-20
surface: cursor-composer
model: gpt-5-codex
scope_files: [app/main.py, app/streaming.py, tests/test_chat_streaming.py]
links: { adr: docs/adr/0004-streaming-protocol.md, issue: null, pr: null }
acceptance:
  - SSE: Content-Type text/event-stream; events: data:<token>\n\n
  - Fallback JSON when Accept != text/event-stream
  - Tests: headers asserted; event format validated; 200 OK
constraints:
  - minimal diff; no new deps
  - do it similar to app/notifications.py style
out_of_scope: ["WebSocket"]
secrets_policy: "No secrets; use .env"
---
Plan the minimal slice as above. Return files to touch, public interface, test list, risks, rollback.
```

**`docs/prompts/0011-sse-streaming-red.prompt.md`**

```markdown
---
id: 0011
title: SSE tests for /chat
stage: red
date: 2025-09-20
surface: cursor-composer
model: gpt-5-codex
scope_files: [tests/test_chat_streaming.py]
links: { pr: null }
acceptance:
  - Failing tests for SSE headers + event format
  - JSON fallback test
constraints: ["no production code"]
---
Add failing tests only; run offline with mocks.
```

---

## Security & Compliance

* **Never store secrets** in prompt bodies; point to `.env` keys.
* **Scrub PII** and customer identifiers; use synthetic data/fixtures.
* **License notes**: If a prompt leads to code derived from an external snippet, cite the source in the prompt file and PR.

---

## Retrieval & Learning

* Tag prompts with labels in front-matter (`labels: [api, streaming, guardrails]`).
* Quarterly, mine `docs/prompts/` to extract reusable **prompt patterns** and add them to your internal “prompt cookbook.”
* Use the index to measure **AI utilization** (prompts per merged PR) and **cycle time** per stage.

---

## TL;DR

* Create `docs/prompts/` alongside `docs/adr/`.
* Number every meaningful prompt step.
* Link prompt IDs in commits, PRs, and ADRs.
* Keep prompts **small, test-guarded, and reproducible**.

## Minimal Repo Skeleton

All set! We have created a minimal repo skeleton with your Prompt History Kit and packaged it as a zip, and they are included in this directory.

Note: We have also included it as a md file also.

What’s inside:

docs/adr/0000-template.md — ADR template

docs/prompts/0000-template.prompt.md — Prompt History Record template

scripts/ — prompt_new.py, prompt_index.py, prompt_guard.py

.githooks/ — pre-commit, commit-msg (remember to enable with git config core.hooksPath .githooks)

Makefile — targets: prompt-new, prompt-index, prompt-guard

README.md — quick start

Quick start after unzipping:

cd ai-prompt-history-starter

git init

git config core.hooksPath .githooks

chmod +x .githooks/* scripts/*.py

make prompt-new SLUG=hello-world STAGE=architect

make prompt-index


