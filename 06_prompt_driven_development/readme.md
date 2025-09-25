# Executive Summary — Summer 2025: The AI-First Turning Point (and How to Harness It)

Summer 2025 is a structural break in software development. Frontier LLMs (e.g., GPT-5 class systems, Claude 4.1x, Gemini 2.5+), AI-first IDEs (Cursor), and production-grade development agents (GPT-5-Codex)have transformed coding from “manual by default” to **AI-assisted by default**. Adoption is mainstream; capability milestones are public; enterprises are reorganizing around agents. The new risk isn’t *whether* to use AI—it’s *how*. Teams that “vibe code” (loose, ad-hoc prompting) ship fast but brittle. Teams that apply **Prompt-Driven Development (PDD)**—small, spec-guided prompt increments—paired with **Test-Driven Development (TDD)**, **ADRs (Architecture Decision Records)**, and **PR (Pull Request) gates** ship fast **and** durable. In short: keep the creative spark, **but with a suit on**.

## State of AI-Assisted Software Development: The Evidence

## [Watch: According to Anthropic's CEO, Claude is already writing 90% of the code](https://www.facebook.com/share/v/1GiTbVdxfs/)**

---

## [Google's senior director of product explains how software engineering jobs are changing in the AI era](https://www.businessinsider.com/google-study-software-engineering-changing-ai-2025-9)**

Here is a concise, summary of the article:

* **AI adoption is mainstream.** Google Cloud’s DORA study reports that approximately **90% of software professionals now use AI**, an increase of **14 percentage points** year over year, with a **median of about two hours per day** spent using AI in core workflows. *(Business Insider)*

* **Engineering roles are evolving.** According to Google’s Ryan J. Salva, engineers will devote **less time to typing code** and **more to product architecture, problem framing, and delivery**, while adjacent roles (e.g., product managers) will increasingly build prototypes and move closer to deployment. *(Business Insider)*

* **Technical fluency remains essential.** Despite AI assistance, **knowledge of programming syntax has grown in perceived importance**. Google’s Nathen Harvey cautions that engineers who cannot read the underlying language will be **“entirely unsuccessful.”** *(Business Insider)*

* **Trust varies across teams.** Roughly **30% of respondents** trust AI **“a little” or “not at all,”** indicating continued reliance on human review and oversight. *(Business Insider)*

* **Internal productivity claims.** CEO Sundar Pichai cites an approximate **10% increase in engineering velocity** attributable to AI and indicates plans to **hire additional engineers** in the coming year. *(Business Insider)*

* **Publication details.** Business Insider; **September 23, 2025**. The article draws on **Google Cloud’s DORA research** and interviews with Google leaders. *(Business Insider)*

---

## [2025 DORA State of AI-assisted Software Development Report](https://cloud.google.com/resources/content/2025-dora-ai-assisted-software-development-report?hl=en)**

Note: The report is also available in the dora_report directory.

Here’s a crisp summary of **DORA – State of AI-assisted Software Development (2025)**:

* **Core thesis:** AI is an *amplifier*—it magnifies the strengths of high-performing orgs and the friction of struggling ones. Value comes less from tools and more from the surrounding system (platform quality, clear workflows, team alignment).

* **Method & scope:** Based on **\~5,000 survey responses** (global) plus **100+ hours of interviews**; fielded **June 13–July 21, 2025**.

* **Adoption & usage:** **\~95%** report using AI; **>80%** say it boosts productivity, yet **\~30%** have little/no trust in AI-generated code—“trust but verify” remains the norm. Median **2 hours/day** hands-on with AI; median experience **\~16 months**.

* **Delivery outcomes:** Compared with last year, **throughput now improves with AI**, but **instability still increases**—teams are getting faster, but safety nets/controls lag.

* **Seven team profiles:** The report clusters teams from **“Foundational challenges”** to **“Harmonious high-achievers.”** Top performers disprove a speed-vs-stability trade-off by excelling at both; others either suffer both or achieve impact with poor cadence/stability.

* **DORA AI Capabilities Model (7 foundations):**

  1. Clear, communicated AI stance; 
  2. Healthy data ecosystem; 
  3. AI-accessible internal data; 
  4. Strong version control; 
  5. Working in small batches; 
  6. User-centric focus; 
  7. Quality internal platform. 
  
  These *amplify* AI’s benefits when present. 

* **Platforms & VSM as multipliers:** **\~90%** report platform engineering; high-quality internal platforms correlate with better ability to unlock AI value. **Value Stream Management (VSM)** further *amplifies* AI’s impact by turning local gains into org-level outcomes. 

* **Practical stance:** Don’t rush AI adoption blindly. Treat it as an **organizational transformation**—invest in platform quality, data, and user-centric practices; train teams to guide and validate AI outputs.

---

Here’s a beginner-friendly take on the **DORA – State of AI-Assisted Software Development (2025)**—plain English, no buzzword bingo:

* **What this report is about:** It looks at how software teams use AI at work and what actually improves results. Think of it as “what’s real vs. hype” for coding with AI. (Magic wands not included 🪄)

* **Who they asked:** Thousands of people across many companies, plus lots of interviews. So it’s not just one team’s story. (More than a couple of coffee chats ☕)

* **Big picture:** AI acts like an **amplifier**. If your team’s processes are good, AI makes them better. If your processes are messy, AI can make the mess faster. (Louder is not the same as better 🔊)

* **How much people use AI:** Almost everyone uses it now, usually **about 2 hours a day**. Most say it helps productivity—but many still **double-check** AI’s work. (Trust, but verify… like checking the oven twice 🍪)

* **Impact on delivery:** Teams are getting **faster**, but if they don’t improve testing and safeguards, they can get **less stable** (more bugs, more rollbacks). (Speed without seatbelts is… exciting, but risky 🚗)

* **What high-performing teams do well:**

  1. **Clear AI policy** (what to use it for, and what not).
  2. **Good data** (clean, accessible, and safe).
  3. **Easy access to internal knowledge** (docs, code, designs).
  4. **Version control discipline** (Git done right).
  5. **Small, frequent changes** (tiny steps beat giant leaps).
  6. **User focus** (build what people need, not just what’s cool).
  7. **Solid internal platforms** (tools and pipelines that “just work”).
     (It’s like a kitchen: sharp knives, clean counters, clear recipes 🍽️)

* **Why platforms matter:** When your internal tools and pipelines are smooth, AI’s benefits **stack up** across the whole org—not just one coder’s laptop. (Team sport, not solo speedrun 🏟️)

* **What to do next (simple plan):**

  * Start with **small, safe tasks** for AI (drafts, tests, refactoring).
  * Keep **humans in the loop** for review.
  * Invest in **tests, CI/CD, and monitoring** so speed doesn’t break things.
  * Improve **docs and data hygiene** so AI has good info to work with.
  * Teach teams **how to prompt and verify** AI results.
    (Measure twice, cut once—then let AI sand the edges 🪚)


---

## [Watch: Spec-Driven Development in the Real World](https://www.youtube.com/watch?v=3le-v1Pme44)

Here’s a crisp summary of the video “Watch: Spec-Driven Development in the Real World”:

### What the talk argues

The speaker says the industry is converging on **spec-driven development (SDD)**—writing a durable, reviewable **spec** (intent, behavior, constraints, and success criteria) first, then using AI/tools to implement against it. This moves teams away from “vibe coding” and toward predictable delivery, especially on multi-person, multi-repo work. ([YouTube][1])

### The 3 things you need for SDD to actually work

1. **Alignment first.** Hash out the problem, scope, user journeys, non-goals, risks, and acceptance criteria so everyone (PM, Eng, Design, QA, stakeholders) agrees before code is generated. ([YouTube][1])
2. **Durable artifacts.** Keep the spec, plan, and acceptance tests as living files in the repo (PR-reviewed), not in ephemeral chats. Treat them as the source of truth that survives code churn. ([The New Stack][2])
3. **Integrated enforcement.** Tie the spec to verification: executable examples/tests, CI checks, and traceable tasks so regressions or spec drift are caught automatically. ([apideck.com][3])

### A practical SDD workflow (as shown/discussed)

* **Intent brief → AI-drafted spec → human review loop.** Start from a high-level product brief; let AI expand to a detailed spec; iterate with the team until acceptance criteria are unambiguous.
* **Plan → tasks → implementation.** Break the spec into verifiable tasks; let AI/agents implement; keep the spec and tests side-by-side with the code.
* **Continuous verification.** PRs must cite the spec sections they fulfill and include tests/examples that prove the behavior. ([YouTube][1])

### Why it beats “vibe coding”

* Captures decisions in a **reviewable artifact** instead of buried chat threads.
* **Speeds onboarding** and cross-team collaboration.
* Reduces **rework and drift** because tests/examples anchor behavior. ([The New Stack][2])

### Tools & patterns mentioned/adjacent in the ecosystem

* **Spec-Kit** (GitHub’s open-source toolkit) — templates and helpers for running an SDD loop with your AI tool of choice. ([The GitHub Blog][4])
* Broader coverage in recent articles summarizing SDD’s rise and best practices. ([The New Stack][2])

### Take-home checklist

* Start every feature with a **one-page intent brief** and **acceptance criteria**.
* Store **spec.md**, **plan.md**, and **examples/tests** in the repo; review them like code.
* Make every PR link to the spec section it implements; **fail CI** if required examples/tests are missing.
* Periodically **refactor the spec** (not just the code) as understanding evolves. ([The New Stack][2])


[1]: https://www.youtube.com/watch?v=3le-v1Pme44&utm_source=chatgpt.com "Spec-Driven Development in the Real World"
[2]: https://thenewstack.io/spec-driven-development-the-key-to-scalable-ai-agents/?utm_source=chatgpt.com "Spec-Driven Development: The Key to Scalable AI Agents"
[3]: https://www.apideck.com/blog/spec-driven-development-part-1?utm_source=chatgpt.com "An introduction to spec-driven API development"
[4]: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/?utm_source=chatgpt.com "Spec-driven development with AI: Get started with a new ..."


---


> ## 🚀 **AI Pair Programming or Prompt-First Agent Development (PFAD) is the New Paradigm**  
> *A methodology where developers architect, build, test, and deploy software — especially AI agents — by engineering prompts for AI-powered tools like [Cursor](https://cursor.com/) and/or [GPT-5-Codex](https://openai.com/index/introducing-upgrades-to-codex/), rather than writing code manually. Other options are Gemini CLI and Qwen Code.*

You are a **Prompt Architect**.  
Cursor and GPT-5-Codex is your **AI Compiler**.  
The Python Interpreter and frameworks like the OpenAI Agents SDK is your **Runtime**.

![](arch.png)

> *Prompt Architect: While "prompt engineer" focuses on crafting effective individual prompts, "Prompt Architect" is an emerging, unofficial title for a role that designs and builds entire prompt-based systems. A prompt architect creates multi-agent workflows, manages context across complex tasks, and designs the overall structure of AI-driven solutions, much like a software architect designs a traditional system. This role is gaining traction in AI-native teams at companies like Anthropic and xAI.*

*The shift from writing code to engineering prompts for developing powerful AI agents is profoundly transformative.*


---

## Prompt-Driven Development: The Cost Advantage

AI has reset the economics of software. The fastest, lowest-cost path to delivery is to put prompts—clear intent, constraints, and acceptance criteria—at the center of engineering.

**Why this wins**

* **Radical cost compression:** Token-priced generation and automated repetition cut build and rework costs while accelerating cycle time.
* **Focus on value:** Engineers spend less time producing code and more time on architecture, quality, security, and reliability.
* **Compounding leverage:** Reusable prompts, patterns, and evaluation suites improve with every project, driving down marginal cost.

**How to execute PDD**

1. **Define:** State outcomes, interfaces, non-functional requirements, and test oracles as precise prompts.
2. **Compose:** Use AI to draft code, tests, and docs aligned to those prompts.
3. **Evaluate:** Auto-check with linters, unit/prop tests, security scans, and benchmark gates.
4. **Integrate:** Refine with human review, enforce governance, and ship via automated CI/CD.
5. **Learn:** Capture winning prompts and failures in a shared library; measure throughput, quality, and cost per release.

**Operating principles**

* Specify before you generate.
* Automate everything repeatable.
* Guard with tests, policies, and telemetry.
* Promote reusable prompt assets as first-class IP.

**Commitment**
Adopt PDD across teams, tools, and governance. Automate the repeatable, elevate human judgment, and scale delivery with confidence and control.

## What This Chapter Delivers

* **Method, not folklore.** A paste-ready workflow for **PDD × TDD** (Plan → Red → Green → Refactor → Explain → Record → PR) so the AI does the typing while your prompts define *what right looks like*.
* **Governance you’ll actually use.** Lightweight **ADRs** to record “why,” a **PR policy** (“no green, no merge”), coverage targets, contract tests, and tracing—turning velocity into maintainability.
* **Operator’s handbook.** Repo-ready prompt templates (architect, tests-only, minimal-diff, refactor, ADR, PR), uv/Docker patterns, and CI checklists that scale from solo to enterprise.


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

## TL;DR

We evolved from **PDD** (prompts drive code) to **GPS Engineering** (prompts **governed** by specs, tests, evals, decisions, and PR gates). You still move fast—just **with a suit on**: **Specify** narrowly, **Prompt** in baby steps, **Test/Evaluate** as gates, **Record** decisions and prompts, and **Review** through small, CI-green PRs.




