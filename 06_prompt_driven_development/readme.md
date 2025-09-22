# Executive Summary — Summer 2025: The AI-First Turning Point (and How to Harness It)

Summer 2025 is a structural break in software development. Frontier LLMs (e.g., GPT-5 class systems, Claude 4.1x, Gemini 2.5+), AI-first IDEs (Cursor), and production-grade development agents (GPT-5-Codex)have transformed coding from “manual by default” to **AI-assisted by default**. Adoption is mainstream; capability milestones are public; enterprises are reorganizing around agents. The new risk isn’t *whether* to use AI—it’s *how*. Teams that “vibe code” (loose, ad-hoc prompting) ship fast but brittle. Teams that apply **Prompt-Driven Development (PDD)**—small, spec-guided prompt increments—paired with **Test-Driven Development (TDD)**, **ADRs (Architecture Decision Records)**, and **PR (Pull Request) gates** ship fast **and** durable. In short: keep the creative spark, **but with a suit on**.

> ## 🚀 **AI Pair Programming or Prompt-First Agent Development (PFAD) is the New Paradigm**  
> *A methodology where developers architect, build, test, and deploy software — especially AI agents — by engineering prompts for AI-powered tools like [Cursor](https://cursor.com/) and/or [GPT-5-Codex](https://openai.com/index/introducing-upgrades-to-codex/), rather than writing code manually.*

You are a **Prompt Architect**.  
Cursor and GPT-5-Codex is your **AI Compiler**.  
The Python Interpreter and frameworks like the OpenAI Agents SDK is your **Runtime**.

![](arch.png)

> *Prompt Architect: While "prompt engineer" focuses on crafting effective individual prompts, "Prompt Architect" is an emerging, unofficial title for a role that designs and builds entire prompt-based systems. A prompt architect creates multi-agent workflows, manages context across complex tasks, and designs the overall structure of AI-driven solutions, much like a software architect designs a traditional system. This role is gaining traction in AI-native teams at companies like Anthropic and xAI.*

*The shift from writing code to engineering prompts for developing powerful AI agents is profoundly transformative.*


## What This Chapter Delivers

* **Method, not folklore.** A paste-ready workflow for **PDD × TDD** (Plan → Red → Green → Refactor → Explain → Record → PR) so the AI does the typing while your prompts define *what right looks like*.
* **Governance you’ll actually use.** Lightweight **ADRs** to record “why,” a **PR policy** (“no green, no merge”), coverage targets, contract tests, and tracing—turning velocity into maintainability.
* **Operator’s handbook.** Repo-ready prompt templates (architect, tests-only, minimal-diff, refactor, ADR, PR), uv/Docker patterns, and CI checklists that scale from solo to enterprise.

## Setting Up AI-Enhanced Dev Environments: **Dual Setup PDD**

To make PDD practical day-to-day, we recommend a **dual environment** for Python Agentic projects:

### VS Code + GPT-5 Codex (Agentic, Cloud-First)

* **What it is:** A coding-optimized GPT-5 agent (often called **GPT-5-Codex**) that executes multi-file, parallel tasks via ChatGPT/CLI/extension.
* **Best at:** Large refactors, cross-repo edits, autonomous chores (tests/docs), PR prep/review.
* **Trade-offs:** Cloud-latency for small tweaks; interactive “inline” edits depend on extension support.

### Standalone Cursor (AI-First IDE, Editor-Centric)

* **What it is:** A VS Code–derived IDE with native AI **tab completion** and repo-aware chat/composer.
* **Best at:** Rapid, in-editor iteration, predictive multi-line edits, “flow-state” coding and local refactors.
* **Trade-offs:** You still review diffs; massive, fully autonomous changes are better delegated to an agent.

#### Similarities (Why both shine)

* Modern LLMs for generation, edits, and debugging; multi-file awareness; codebase chat; measurable time savings when paired with good prompts and tests.

#### Differences (Why you want both)

| Aspect      | Cursor (Editor-centric)                                     | GPT-5-Codex (Agent-centric)                           |
| ----------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| Interaction | Inline/tab completion; real-time previews                   | Natural-language tasks; parallel autonomous runs      |
| Sweet spot  | Quick edits, tight loops, local refactors                   | Repo-wide changes, scaffolding, PRs/tests/docs        |
| Ecosystem   | Feels like VS Code; supports models from multiple providers | Deep OpenAI integration; strongest in agent workflows |

**Bottom line:** Use **GPT-5-Codex in VS Code** to *initiate projects, run broad refactors, and prepare PRs*, then **Cursor** to *iterate quickly with inline edits and predictive suggestions*. Git-sync lets you hop between them seamlessly—Swiss-army knife + laser scalpel.

## How We’ll Apply PDD × TDD in the Tutorials

* **Baby steps by prompt.** Each lesson starts with an *architect prompt* (micro-spec), adds **Red** tests, goes **Green** with the smallest diff, refactors safely, explains changes, records an **ADR**, and opens a **PR**.
* **Guardrails by default.** Pydantic output shapes, error taxonomies, and contract tests prevent regressions and keep agentic edits on the rails.
* **Evidence over anecdotes.** You’ll measure lead time, coverage, change-fail rate, and MTTR as you adopt AI-first practices.


## Why This Matters

The winners of 2025 aren’t just “using AI”; they’re **professionalizing** it. PDD gives you repeatability; TDD turns intent into executable checks; ADRs make choices explainable; PR gates make quality social and auditable. Adopt all four and you’ll move faster—with fewer 3 a.m. rollbacks and more 3 p.m. launches.

**Call to action:** Open the first tutorial. Paste the prompts. Let the AI type. You conduct.

## From Prompt-Driven Development (PDD) to **GPS Engineering** — The Progressive Journey

> **GPS Engineering** = **Spec-Driven Development (SDD)** × **Prompt-Driven Development (PDD)** × **Test-Driven Development (TDD)** × **Evaluation-Driven Development (EDD)** × **ADRs** × **PHRs** × **PR gates** — *“build with AI, but with a suit on.”*

---

## 1) Why Summer 2025 is Different

Frontier LLMs (GPT-5 class, Claude 4.1x, Gemini 2.5+) plus **AI-first IDEs** (Cursor) and **agentic coding** (GPT-5 Codex) make AI assistance the default. Teams report drastic cycle-time drops—**when** they pair speed with governance. Unstructured “vibe coding” is fast but fragile; the winners adopt a method that keeps creativity while enforcing quality.

---

## 2) From PDD → Governance: the **GPS** Mindset

* **PDD** proved we can *drive development through prompts*, incrementally (“baby steps”): Architect → Red → Green → Refactor → Explainer.
* **GPS Engineering** keeps that loop and **adds guardrails**: thin specs up front, tests/evals as executable contracts, decisions recorded, merges gated, traceability preserved.

---

## 3) The Journey in Stages (progressive, slice by slice)

Think staircase: each step is small, testable, and shippable.

### Stage 0 — Foundations (Repo hygiene)

* `.env.sample`, `pyproject.toml`, **uv** for deps, multi-stage **Dockerfile**, `Makefile`.
* Baseline **CI** (ruff, pytest; optional EDD smoke).
* **PR template** with **Spec-Compliance** checkbox.

### Stage 1 — **Specify** (SDD)

* Write a **thin spec** per slice (e.g., `/chat` JSON, then **SSE**): behavior, constraints (e.g., length ≤ 1200), acceptance checks.
* Store in `docs/specs/`.

### Stage 2 — **Prompt** (PDD, “baby steps”)

* Drive changes via sequenced prompts: **Architect → Red → Green → Refactor → Explainer**.
* Capture each step as a **PHR** in `docs/prompts/`. Cursor/Codex produce diffs; you control scope and acceptance.

### Stage 3 — **Test** (TDD)

* **Red**: add failing unit/contract tests first (offline/mocked).
* **Green**: smallest change to pass.
* **Refactor**: tidy internals, keep green.
* Tests encode the spec so the model aligns with intent.

### Stage 4 — **Evaluate** (EDD)

* Add **promptfoo** suites to detect **behavior drift** (e.g., scope discipline, “tool-first” math/time).
* Run **smoke** on PRs; **full** nightly.

### Stage 5 — **Record & Review** (ADR, PHR, PR)

* **ADR**: consequential decisions (e.g., SSE vs WebSocket)—context, options, decision, consequences.
* **PHR**: the exact prompts and outcomes for each slice.
* **PR**: small, CI-gated; links **Spec + PHR + ADR**, **Spec-Compliance** checked.

### Stage 6 — **Tools That Fit the Loop** (Dual environment)

* **VS Code + GPT-5 Codex** (agent-centric): init projects, repo-wide refactors, PR prep & reviews.
* **Cursor** (editor-centric): inline tab-completion, fast multi-file edits, composer/chat.
* Git-sync lets you switch fluidly—**Swiss-army knife + laser scalpel**.

### Stage 7 — **First Product Slice** (worked example)

1. **Spec** `/healthz` + `/chat` JSON contract.
2. **Red** tests for `/chat`:

   * 400 with top-level `{ "error_code": "MISSING_USER_MESSAGE" }`
   * 200 `ChatReply { text, used_tool?, handoff }`
3. **Green** minimal diff via PDD prompts; enforce **guardrails** (Pydantic shape, length).
4. Add **SSE**: write spec → **Red** streaming tests → **Green** with `Content-Type: text/event-stream`, `data:<token>\n\n`, end `data:[DONE]\n\n`.
5. Record **ADR** for streaming choice.
6. Open a **PR** linking Spec/PHRs/ADR; CI + EDD must pass.

### Stage 8 — **Metrics** (prove it)

Track:

* **Lead time to change** (hrs per small PR)
* **Change-failure rate** (% PRs causing rollback/hotfix)
* **MTTR**
* **Coverage & contract tests**
* **ADR density** (# decisions per significant change)
* **AI utilization** (% diffs generated via prompts)

### Stage 9 — **90-Day Rollout**

* **Days 0–10**: Repo hygiene, CI gates, PR template, baseline specs.
* **Days 10–30**: Pilot one service; 10–20 small PRs through the GPS loop.
* **Days 30–60**: Scale to more repos; add EDD smoke; strengthen contracts.
* **Days 60–90**: Institutionalize: rules bundles for Cursor/Codex, prompt libraries, dashboards.

---

## 4) Where Things Live (Artifacts)

* **Specs (SDD)** → `docs/specs/…md`
* **PHRs (prompts)** → `docs/prompts/…prompt.md`
* **Tests (TDD)** → `tests/…`
* **Evals (EDD)** → `promptfoo.config.yaml`, `evals/behavior/*.yaml`
* **ADRs** → `docs/adr/*.md`
* **PR gates** → `.github/workflows/*.yml` + `.github/PULL_REQUEST_TEMPLATE.md` (with **Spec-Compliance**)

---

## 5) Governance in One Slide

* **Thin slices, tight specs.**
* **Smallest change to green.**
* **No green, no merge.**
* **Trace everything** (PHR + ADR).
* **Model-agnostic**; tools are pluggable (Codex/Cursor/others).

---

## 6) Quality-of-Life Packs (ready to use)

* **Cursor Composer / Codex prompts** for each phase (Architect/Red/Green/Refactor/Explainer/Fix-only).
* **Nano Banana** copy-paste diagram prompts (system context, sequences, SSE, PR lifecycle, traceability, KPIs, roadmap).
* Keep them in `docs/prompts/` and `docs/diagrams/` so every repo stays aligned.

---

## TL;DR

We evolved from **PDD** (prompts drive code) to **GPS Engineering** (prompts **governed** by specs, tests, evals, decisions, and PR gates). You still move fast—just **with a suit on**: **Specify** narrowly, **Prompt** in baby steps, **Test/Evaluate** as gates, **Record** decisions and prompts, and **Review** through small, CI-green PRs.




