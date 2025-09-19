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

