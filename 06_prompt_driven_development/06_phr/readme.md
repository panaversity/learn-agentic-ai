# Prompt History Records

**PHRs = Prompt History Records.**

They’re short, versioned markdown files that capture each meaningful **prompt you gave to the AI** (and its intended outcome) during development. Think of them as *commit messages for prompts*—a paper trail that lets you (and reviewers) see **what you asked, why, what changed, and how it was verified**.

### Why use PHRs?

* **Traceability:** Reproduce a change by replaying the exact prompt(s).
* **Reviewability:** PR reviewers can judge intent vs. diff quickly.
* **Team learning:** Good prompts become reusable patterns.
* **Risk control:** Avoids “mystery code” from undocumented AI edits.

### What’s inside a PHR?

* **Metadata:** id, title, date, stage (architect/red/green/refactor/explainer/adr-draft/pr-draft), model used.
* **Scope & constraints:** files to touch, acceptance criteria, out-of-scope, “minimal diff.”
* **The exact prompt text** you pasted into Cursor/Codex.
* **Outcome notes:** files changed, tests added, follow-ups.

### Typical filename

```
docs/prompts/0007-chat-endpoint-green.prompt.md
```

### Minimal template (what we put in your repo)

```markdown
---
id: 0007
title: Chat Endpoint
stage: green            # architect | red | green | refactor | explainer | adr-draft | pr-draft
date: 2025-09-21
surface: cursor-composer
model: gpt-5-codex
repo_ref: <branch-or-commit>
scope_files:
  - app/main.py
  - tests/test_chat_contract.py
links:
  adr: docs/adr/0002-streaming-protocol.md
  issue: null
  pr: null
acceptance:
  - Given POST /chat with user_message -> Then 200 and ChatReply shape
constraints:
  - minimal diff, no new deps
  - offline tests (mocks)
out_of_scope:
  - auth, db, tracing
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

### How PHRs fit the workflow

* **PDD + TDD loop:**

  * **Architect PHR** (micro-spec) → **Red PHR** (tests only) → **Green PHR** (smallest diff to pass) → **Refactor PHR** (keep tests green) → **Explainer PHR** (bullets)
* **PRs:** Link relevant PHR ids so reviewers can see the prompts behind the diff.
* **ADRs:** When you make a consequential decision, create an ADR and link the related PHR(s).

### Using the helper scripts we shipped

From the repo root:

```bash
# Create a new PHR file with next sequence number
make prompt-new SLUG=chat-endpoint STAGE=architect

# Rebuild the index of PHRs
make prompt-index
```

Git hooks will nudge you to include a PHR whenever you stage code changes.

### Do / Don’t

**Do**

* Write PHRs for *every meaningful step* (architect/red/green/refactor…).
* Keep prompts specific, testable, and scoped to a tiny change.
* Record outcomes right after accepting the diff.

**Don’t**

* Paste secrets into prompts (use `.env`).
* Bundle multiple unrelated changes in one PHR.
* Skip the PHR when you hot-edit code—capture *how* you asked the AI.

## Examples

Added four concrete PHR example files to your repo and packaged an updated zip:

docs/prompts/0001-healthz-architect.prompt.md

docs/prompts/0002-healthz-green.prompt.md

docs/prompts/0003-chat-architect.prompt.md

docs/prompts/0004-chat-green.prompt.md

Download the updated repo here:

ai-agent-playbook-starter-with-phr-examples.zip

Want want to also have a example PR description that references these PHRs and an ADR stub for the upcoming streaming choice (SSE vs WebSocket) so you can open your first PR immediately?

Ready-to-paste PR description:
docs/pr/0001-bootstrap-and-chat-contract.md

ADR stub for streaming choice:
docs/adr/0002-streaming-protocol-choice.md (Status: Draft)

Grab the updated bundle here:

ai-agent-playbook-starter-with-pr-and-adr.zip

