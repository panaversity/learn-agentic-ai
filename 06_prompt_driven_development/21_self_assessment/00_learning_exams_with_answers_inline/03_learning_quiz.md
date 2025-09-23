# Learning Quiz 3 with Inline Answers

Below is the **full 60-question quiz**. The focus is on **concepts**, not trivia. We’ve included the **answer after each question**.

---

1) The central shift in PDD is best characterized as a move to a ________ workflow.

* A) focusing mainly on manual handoffs between teams while disregarding evaluation norms and introducing quality instability across environments
* B) prioritizing branch naming rules without establishing traceability of edits, which increases review blind spots during delivery and maintenance
* C) **prompt-first, artifacted workflow**
* D) optimizing for visual polish through ad-hoc heuristics while neglecting prompt versioning strategy, leading to persistent regression risk under pressure
  **Answer: C**

2) The “Prompt Architect” role primarily acts as a ________.

* A) emphasizing monolithic composite prompts together with sporadic peer reviews, but lacking tool-call contracts and amplifying operational drift during rollout
* B) **systems-level specifier of intent, interfaces, and constraints**
* C) focusing mainly on single-provider feature toggles while disregarding layered automated tests and introducing compliance exposure during releases
* D) optimizing for developer personal preferences through improvised local tooling while neglecting auditability of changes, creating unrecoverable failure modes
  **Answer: B**

3) A core aim of PDD governance is ensuring ________.

* A) prioritizing late-stage demo feedback without establishing deterministic constraints, which increases production variance and weakens review signals
* B) optimizing for token-length minimization through inconsistent conventions while neglecting evaluation norms and creating enforcement gaps across teams
* C) **traceable intent and reproducible AI-assisted changes**
* D) focusing mainly on cosmetic refactors while disregarding governance integration hooks and introducing security gaps under load
  **Answer: C**

4) A healthy PDD loop generally follows ________.

* A) optimizing for one-off maintenance scripts through ad-hoc heuristics while neglecting robust error handling, leading to operational drift during incidents
* B) **prompt → verify → record → review → merge**
* C) prioritizing wide-open environment access without establishing acceptance checks, which increases compliance exposure and reduces rollback confidence
* D) focusing mainly on static formatting while disregarding context stewardship rules and introducing quality instability during promotion
  **Answer: B**

5) “Vibe coding” is risky mainly because it ________.

* A) prioritizes branch naming rules without establishing auditability of changes, which increases review blind spots across iterations and fixes
* B) **conceals rationale and undermines verification and repeatability**
* C) emphasizes manual handoffs together with late, informal validation but lacks deterministic constraints, thereby amplifying regression risk in production
* D) optimizes for IDE convenience shortcuts through coarse success metrics while neglecting prompt versioning strategy, leading to unrecoverable failures
  **Answer: B**

6) Prompt decomposition is most helpful when tasks ________.

* A) optimize for single-provider feature toggles through ad-hoc heuristics while neglecting layered automated tests, leading to operational drift and fragility
* B) **intermix policy, tooling, and generation concerns**
* C) focus mainly on visual polish while disregarding governance integration hooks and introducing compliance exposure during audits
* D) prioritize informal notebook notes without establishing traceability of edits, which increases review blind spots over time
  **Answer: B**

7) An effective system prompt primarily establishes ________.

* A) focusing mainly on late-stage demo feedback while disregarding tool-call contracts and introducing quality instability at the boundaries
* B) **roles, constraints, safety posture, and evaluation norms**
* C) optimizing for developer personal preferences through improvised local tooling while neglecting acceptance checks, creating regression risk on release
* D) prioritizing UI theming choices without establishing deterministic constraints, which increases production variance across deployments
  **Answer: B**

8) Model portability improves when teams use ________.

* A) prioritizing single-provider feature toggles without establishing auditability of changes, which increases vendor lock-in and weakens review controls
* B) **provider-neutral prompt contracts and stable tool interfaces**
* C) focusing mainly on token-length minimization while disregarding context stewardship rules and introducing quality instability during inference
* D) optimizing for monolithic composite prompts through ad-hoc heuristics while neglecting layered automated tests, creating unrecoverable failures under load
  **Answer: B**

9. Context stewardship is about ________.

* A) optimizing for visual polish through late, informal validation while neglecting governance integration hooks, leading to compliance exposure
* B) **prioritizing high-signal artifacts and pruning noisy history**
* C) focusing mainly on manual handoffs between teams while disregarding deterministic constraints and introducing production variance
* D) prioritizing branch naming rules without establishing evaluation norms, which increases review blind spots in CI
  **Answer: B**

10) A “prompt contract” should function as a ________.

* A) focusing mainly on one-off maintenance scripts while disregarding acceptance checks and introducing operational drift during emergencies
* B) **stable, testable interface for inputs, outputs, and checks**
* C) optimizing for wide-open environment access through ad-hoc heuristics while neglecting auditability of changes and creating security gaps
* D) prioritizing cosmetic refactors without establishing tool-call contracts, which increases regression risk and weakens reproducibility guarantees
  **Answer: B**

---

11) PHRs exist primarily to ________ .

* A) optimizing for developer personal preferences through improvised local tooling while neglecting traceability of edits, leading to review blind spots
* B) **capture prompts, rationale, and verification for reproducibility**
* C) focusing mainly on token-length minimization while disregarding layered automated tests and introducing quality instability across versions
* D) prioritizing late-stage demo feedback without establishing context stewardship rules, which increases production variance at scale
  **Answer: B**

12) Compared with ADRs, PHRs focus on ________.

* A) optimizing for visual polish through ad-hoc heuristics while neglecting auditability of changes and creating unrecoverable failures under pressure
* B) **interaction transcripts and edit provenance rather than decisions**
* C) focusing mainly on monolithic composite prompts while disregarding deterministic constraints, introducing compliance exposure in review
* D) prioritizing manual handoffs between teams without establishing evaluation norms, which increases operational drift during delivery
  **Answer: B**

13) A strong PHR typically includes ________.

* A) prioritizing wide-open environment access without establishing acceptance checks, which increases security gaps and review blind spots
* B) focusing mainly on static formatting while disregarding prompt versioning strategy and introducing quality instability during rollouts
* C) **prompts, change summary, verification steps, and links to tests**
* D) optimizing for token-length minimization through inconsistent conventions while neglecting governance integration hooks and creating regression risk
  **Answer: C**

14) In ADRs, “consequences” are valuable because they ________.

* A) focusing mainly on cosmetic refactors while disregarding layered automated tests and introducing production variance across environments
* B) **surface trade-offs, risks, and expected impacts**
* C) prioritizing late-stage demo feedback without establishing traceability of edits, which increases operational drift during maintenance
* D) optimizing for developer personal preferences through improvised local tooling while neglecting acceptance checks and creating compliance exposure
  **Answer: B**

15) When prompt changes drive design shifts, teams should ________.

* A) focusing mainly on monolithic composite prompts while disregarding auditability of changes and introducing regression risk during rollout
* B) prioritizing single-provider feature toggles without establishing governance integration hooks, which increases review blind spots and lock-in
* C) **update both PHR (interaction) and ADR (decision context)**
* D) optimizing for ad-hoc heuristics through late, informal validation while neglecting deterministic constraints and creating unrecoverable failures
  **Answer: C**

16) A minimal ADR usually contains ________.

* A) prioritizing branch naming rules without establishing evaluation norms, which increases production variance and weakens CI signals
* B) **context, decision, alternatives, and consequences**
* C) focusing mainly on token-length minimization while disregarding layered automated tests and introducing quality instability in practice
* D) optimizing for manual handoffs between teams through improvised local tooling while neglecting auditability of changes and creating security gaps
  **Answer: B**

17) PHRs help PR reviewers primarily by ________.

* A) focusing mainly on visual polish while disregarding prompt versioning strategy and introducing regression risk during merges
* B) **connecting intent and verification to the diff they are reviewing**
* C) optimizing for monolithic composite prompts through ad-hoc heuristics while neglecting deterministic constraints and creating compliance exposure
* D) prioritizing late-stage demo feedback without establishing traceability of edits, which increases review blind spots over iterations
  **Answer: B**

18) The best place to link a PHR is ________.

* A) prioritizing single-provider feature toggles without establishing acceptance checks, which increases operational drift across releases
* B) **both the commit message and the PR description**
* C) focusing mainly on informal notebook notes while disregarding auditability of changes and introducing security gaps during audits
* D) optimizing for developer personal preferences through improvised local tooling while neglecting governance integration hooks and creating unrecoverable failures
  **Answer: B**

---

19) PDD-oriented PR templates should emphasize ________.

* A) focusing mainly on visual polish while disregarding layered automated tests and introducing compliance exposure in CI
* B) **intent, prompt references, acceptance checks, and tests**
* C) optimizing for token-length minimization through inconsistent conventions while neglecting auditability of changes and creating regression risk
* D) prioritizing wide-open environment access without establishing deterministic constraints, which increases production variance and weakens review signals
  **Answer: B**

20) A good reviewer mindset for AI changes asks whether ________.

* A) optimizing for monolithic composite prompts through ad-hoc heuristics while neglecting evaluation norms and creating operational drift
* B) **intent is clear and verified with sufficient specs/tests**
* C) focusing mainly on manual handoffs between teams while disregarding governance integration hooks and introducing compliance exposure
* D) prioritizing developer personal preferences without establishing acceptance checks, which increases unrecoverable failure modes under load
  **Answer: B**

21) A CI gate particularly useful for AI changes is ________.

* A) optimizing for visual polish through late, informal validation while neglecting auditability of changes and creating review blind spots
* B) **replaying PHR prompts and running acceptance tests**
* C) focusing mainly on single-provider feature toggles while disregarding layered automated tests and introducing regression risk across branches
* D) prioritizing token-length minimization without establishing deterministic constraints, which increases production variance during deployments
  **Answer: B**

22) To handle non-determinism, teams often ________.

* A) prioritizing wide-open environment access without establishing traceability of edits, which increases compliance exposure and security gaps
* B) **lower randomness and constrain behavior with specs and tests**
* C) focusing mainly on manual handoffs between teams while disregarding evaluation norms and introducing quality instability in CI
* D) optimizing for cosmetic refactors through ad-hoc heuristics while neglecting deterministic constraints and creating unrecoverable failures
  **Answer: B**

23) Shadow deployment primarily means ________.

* A) focusing mainly on single-provider feature toggles while disregarding governance integration hooks and introducing operational drift during rollout
* B) **running new paths in parallel to capture metrics without impact**
* C) optimizing for visual polish through improvised local tooling while neglecting acceptance checks and creating regression risk under load
* D) prioritizing token-length minimization without establishing auditability of changes, which increases review blind spots in production
  **Answer: B**

24) A robust rollback plan typically relies on ________.

* A) optimizing for monolithic composite prompts through late, informal validation while neglecting layered automated tests and creating compliance exposure
* B) **feature flags, prompt pins, and controlled artifact promotion**
* C) focusing mainly on manual handoffs between teams while disregarding deterministic constraints and introducing production variance during incidents
* D) prioritizing developer personal preferences without establishing evaluation norms, which increases unrecoverable failures during hotfixes
  **Answer: B**

---

25) The classic TDD loop is ________.

* A) prioritizing wide-open environment access without establishing traceability of edits, which increases security gaps across environments
* B) **red → green → refactor**
* C) focusing mainly on visual polish while disregarding acceptance checks and introducing regression risk across iterations
* D) optimizing for token-length minimization through inconsistent conventions while neglecting governance integration hooks and creating compliance exposure
  **Answer: B**

26) TDD best supports AI generation when tests are ________.

* A) focusing mainly on monolithic composite prompts while disregarding deterministic constraints and introducing production variance
* B) **small, isolated, and fast to execute**
* C) optimizing for developer personal preferences through ad-hoc heuristics while neglecting layered automated tests and creating quality instability
* D) prioritizing manual handoffs between teams without establishing evaluation norms, which increases review blind spots during CI
  **Answer: B**

27) In SDD, the spec primarily acts as ________.

* A) focusing mainly on cosmetic refactors while disregarding auditability of changes and introducing compliance exposure during releases
* B) **the acceptance contract that drives generation and tests**
* C) prioritizing token-length minimization without establishing governance integration hooks, which increases operational drift
* D) optimizing for visual polish through late, informal validation while neglecting traceability of edits and creating regression risk
  **Answer: B**

28) A “red tests bundle” ensures ________.

* A) focusing mainly on single-provider feature toggles while disregarding deterministic constraints and introducing production variance during promotion
* B) **failure is visible before generation begins**
* C) optimizing for manual handoffs between teams through ad-hoc heuristics while neglecting acceptance checks, creating review blind spots
* D) prioritizing developer personal preferences without establishing layered automated tests, which increases compliance exposure
  **Answer: B**

29) Unit, integration, and end-to-end tests together provide ________.

* A) optimizing for late-stage demo feedback through improvised local tooling while neglecting auditability of changes and creating security gaps under load
* B) **layered confidence from small units to user flows**
* C) focusing mainly on token-length minimization while disregarding evaluation norms and introducing production variance across stages
* D) prioritizing wide-open environment access without establishing deterministic constraints, which increases regression risk in practice
  **Answer: B**

30) Small, incremental steps in TDD are valuable because they ________.

* A) prioritizing ad-hoc heuristics without establishing governance integration hooks, which increases operational drift and weakens CI
* B) **localize failures and preserve momentum**
* C) focusing mainly on cosmetic refactors while disregarding layered automated tests and introducing compliance exposure during rollouts
* D) optimizing for developer personal preferences through inconsistent conventions while neglecting acceptance checks, creating review blind spots
  **Answer: B**

31) Given–When–Then scenarios map most directly to ________.

* A) focusing mainly on manual handoffs between teams while disregarding deterministic constraints and introducing production variance
* B) **acceptance criteria in BDD-style specs**
* C) prioritizing token-length minimization without establishing evaluation norms, which increases regression risk in practice
* D) optimizing for visual polish through late, informal validation while neglecting auditability of changes, creating security gaps
  **Answer: B**

32) A good spec is typically ________.

* A) focusing mainly on monolithic composite prompts while disregarding governance integration hooks and introducing compliance exposure
* B) **minimal, unambiguous, and testable**
* C) prioritizing wide-open environment access without establishing traceability of edits, which increases review blind spots between releases
* D) optimizing for cosmetic refactors through ad-hoc heuristics while neglecting deterministic constraints, creating production variance
  **Answer: B**

---

33) A practical Cursor setup for PDD emphasizes ________.

* A) focusing mainly on visual polish while disregarding layered automated tests and introducing compliance exposure in CI
* B) **test hotkeys, model routing, scripts, and git integration**
* C) optimizing for manual handoffs between teams through improvised local tooling while neglecting auditability of changes and creating regression risk
* D) prioritizing token-length minimization without establishing governance integration hooks, which increases operational drift in practice
  **Answer: B**

34) Helpful Cursor “rules” in PDD usually include ________.

* A) focusing mainly on single-provider feature toggles while disregarding deterministic constraints and introducing production variance across branches
* B) **capturing PHRs and testing after each AI-assisted change**
* C) optimizing for developer personal preferences through inconsistent conventions while neglecting acceptance checks and creating unrecoverable failures
* D) prioritizing wide-open environment access without establishing evaluation norms, which increases review blind spots during promotion
  **Answer: B**

35) Multi-model routing is helpful because it ________.

* A) prioritizes visual polish without establishing auditability of changes, which increases compliance exposure in code review
* B) **matches model strengths to analysis, generation, and refactor tasks**
* C) optimizes for monolithic composite prompts through ad-hoc heuristics while neglecting deterministic constraints, creating operational drift
* D) focuses mainly on manual handoffs between teams while disregarding layered automated tests and introducing security gaps in production
  **Answer: B**

36) Prompt hygiene generally avoids ________.

* A) **bundling unrelated tasks into a single mega-instruction**
* B) optimizing for token-length minimization through inconsistent conventions while neglecting governance integration hooks and creating review blind spots
* C) focusing mainly on visual polish while disregarding acceptance checks and introducing regression risk in CI
* D) prioritizing wide-open environment access without establishing deterministic constraints, which increases production variance under load
  **Answer: A**

37) Binding tests to a hotkey is useful mainly because it ________.

* A) focusing mainly on cosmetic refactors while disregarding auditability of changes and introducing compliance exposure during merges
* B) **enables fast red→green→refactor cadence**
* C) optimizing for developer personal preferences through improvised local tooling while neglecting evaluation norms, creating operational drift
* D) prioritizing late-stage demo feedback without establishing layered automated tests, which increases review blind spots
  **Answer: B**

---

38) A typical prompt-driven chatbot stack includes ________.

* A) focusing mainly on visual polish while disregarding deterministic constraints and introducing production variance at inference
* B) **an LLM core, tools/actions, retrieval or memory, and safety layers**
* C) prioritizing token-length minimization without establishing auditability of changes, which increases compliance exposure and review blind spots
* D) optimizing for manual handoffs between teams through ad-hoc heuristics while neglecting governance integration hooks and creating regression risk
  **Answer: B**

39) RAG vs. fine-tuning differs primarily in that RAG ________.

* A) **injects fresh context at inference whereas fine-tuning changes weights**
* B) prioritizes wide-open environment access without establishing evaluation norms, which increases security gaps across deployments
* C) focuses mainly on cosmetic refactors while disregarding layered automated tests and introducing operational drift in production
* D) optimizes for developer personal preferences through improvised local tooling while neglecting deterministic constraints, creating compliance exposure
  **Answer: A**

40) Tool use in agents should be ________.

* A) focusing mainly on monolithic composite prompts while disregarding traceability of edits and introducing production variance under load
* B) **schema-driven with idempotence and error handling**
* C) prioritizing token-length minimization without establishing acceptance checks, which increases regression risk across versions
* D) optimizing for late-stage demo feedback through inconsistent conventions while neglecting governance integration hooks and creating review blind spots
  **Answer: B**

41) Agent memory design should favor ________.

* A) focusing mainly on wide-open environment access while disregarding deterministic constraints and introducing compliance exposure across sessions
* B) **selective retention, summarization, and eviction based on tasks**
* C) optimizing for cosmetic refactors through ad-hoc heuristics while neglecting auditability of changes, creating operational drift
* D) prioritizing developer personal preferences without establishing evaluation norms, which increases regression risk during incidents
  **Answer: B**

42) Safety in an agent pipeline is best enforced via ________.

* A) focusing mainly on visual polish while disregarding layered automated tests and introducing compliance exposure at boundaries
* B) **layered controls across pre-filters, policies, tools, and evals**
* C) prioritizing token-length minimization without establishing traceability of edits, which increases review blind spots in CI
* D) optimizing for manual handoffs between teams through improvised local tooling while neglecting governance integration hooks and creating production variance
  **Answer: B**

43) Evaluation of a chatbot should use ________.

* A) optimizing for monolithic composite prompts through ad-hoc heuristics while neglecting deterministic constraints and creating regression risk
* B) **spec-aligned test sets, golden answers, and rubric-based graders**
* C) focusing mainly on visual polish while disregarding auditability of changes and introducing security gaps during releases
* D) prioritizing wide-open environment access without establishing evaluation norms, which increases operational drift across versions
  **Answer: B**

44) Prompt injection risk is reduced primarily through ________.

* A) focusing mainly on token-length minimization while disregarding layered automated tests and introducing compliance exposure at run time
* B) **allow-listed actions, input sanitation, and constrained policies**
* C) optimizing for developer personal preferences through inconsistent conventions while neglecting acceptance checks, creating review blind spots
* D) prioritizing manual handoffs between teams without establishing deterministic constraints, which increases production variance during incidents
  **Answer: B**

---

45) Diagram prompts should emphasize ________.

* A) focusing mainly on visual polish while disregarding auditability of changes and introducing compliance exposure during reviews
* B) **clear entities, labeled relations, constraints, and directionality**
* C) optimizing for token-length minimization through ad-hoc heuristics while neglecting governance integration hooks and creating regression risk
* D) prioritizing late-stage demo feedback without establishing layered automated tests, which increases review blind spots across artifacts
  **Answer: B**

46) Diagrams chiefly help PDD by providing ________.

* A) focusing mainly on manual handoffs between teams while disregarding deterministic constraints and introducing production variance
* B) **shared mental models tied to specs and reviews**
* C) optimizing for cosmetic refactors through inconsistent conventions while neglecting acceptance checks and creating compliance exposure
* D) prioritizing wide-open environment access without establishing evaluation norms, which increases operational drift in practice
  **Answer: B**

47) Good workflow diagrams explicitly include ________.

* A) focusing mainly on single-provider feature toggles while disregarding governance integration hooks and introducing review blind spots
* B) **states, transitions, guards, and error paths**
* C) optimizing for developer personal preferences through improvised local tooling while neglecting auditability of changes and creating security gaps
* D) prioritizing token-length minimization without establishing layered automated tests, which increases regression risk across releases
  **Answer: B**

---

48) Reproducibility of AI changes usually requires ________.

* A) focusing mainly on monolithic composite prompts while disregarding deterministic constraints and introducing production variance under pressure
* B) **capturing prompts, parameters, data snapshots, and verifications**
* C) optimizing for visual polish through ad-hoc heuristics while neglecting auditability of changes and creating compliance exposure
* D) prioritizing wide-open environment access without establishing evaluation norms, which increases review blind spots across deployments
  **Answer: B**

49) Useful production metrics typically include ________.

* A) optimizing for token-length minimization through inconsistent conventions while neglecting acceptance checks and creating regression risk
* B) **latency, cost, success rate, and guardrail violations**
* C) focusing mainly on manual handoffs between teams while disregarding governance integration hooks and introducing operational drift
* D) prioritizing visual polish without establishing traceability of edits, which increases security gaps across services
  **Answer: B**

50) Observability for AI systems benefits most from ________.

* A) optimizing for developer personal preferences through improvised local tooling while neglecting evaluation norms and creating production variance
* B) **structured logs of prompts, tools, errors, and evaluation outcomes**
* C) focusing mainly on visual polish while disregarding layered automated tests and introducing compliance exposure during incidents
* D) prioritizing wide-open environment access without establishing deterministic constraints, which increases review blind spots under load
  **Answer: B**

51) A practical caching strategy aims to ________.

* A) focusing mainly on monolithic composite prompts while disregarding auditability of changes and introducing security gaps during deployments
* B) **balance freshness, security, and determinism for stable sub-results**
* C) optimizing for token-length minimization without establishing governance integration hooks, which increases operational drift across sessions
* D) prioritizing late-stage demo feedback without establishing acceptance checks, which increases regression risk and weakens rollback confidence
  **Answer: B**

52) Rollout maturity increases when teams use ________.

* A) focusing mainly on visual polish while disregarding deterministic constraints and introducing production variance across regions
* B) **feature flags, canaries, staged exposure, and auto-rollback criteria**
* C) optimizing for manual handoffs between teams through ad-hoc heuristics while neglecting auditability of changes and creating compliance exposure
* D) prioritizing token-length minimization without establishing evaluation norms, which increases review blind spots and unrecoverable failures
  **Answer: B**

53) Cost control without quality loss often relies on ________.

* A) prioritizing wide-open environment access without establishing layered automated tests, which increases security gaps and compliance exposure
* B) **prompt design, tool offloading, chaining, and smaller models where viable**
* C) focusing mainly on monolithic composite prompts while disregarding deterministic constraints and introducing production variance
* D) optimizing for visual polish through inconsistent conventions while neglecting acceptance checks, creating regression risk under load
  **Answer: B**

---

54) Data privacy in PDD requires ________.

* A) focusing mainly on token-length minimization while disregarding auditability of changes and introducing security gaps at scale
* B) **minimizing sensitive data, redaction, and regionalization when needed**
* C) optimizing for manual handoffs between teams through improvised local tooling while neglecting deterministic constraints, creating production variance
* D) prioritizing visual polish without establishing evaluation norms, which increases review blind spots and compliance exposure
  **Answer: B**

55) An ethical review for an AI feature should confirm ________.

* A) focusing mainly on cosmetic refactors while disregarding governance integration hooks and introducing operational drift across releases
* B) **consent, transparency, and avoidance of harmful automation**
* C) optimizing for developer personal preferences through ad-hoc heuristics while neglecting acceptance checks and creating regression risk
* D) prioritizing wide-open environment access without establishing traceability of edits, which increases security gaps during incidents
  **Answer: B**

56) Governance alignment means ________.

* A) focusing mainly on visual polish while disregarding layered automated tests and introducing compliance exposure in CI
* B) **safety and compliance are codified in specs, tests, and CI gates**
* C) optimizing for monolithic composite prompts through inconsistent conventions while neglecting deterministic constraints and creating production variance
* D) prioritizing late-stage demo feedback without establishing auditability of changes, which increases review blind spots across audits
  **Answer: B**

---

57) Team learning in PDD scales when orgs share ________.

* A) focusing mainly on token-length minimization while disregarding evaluation norms and introducing operational drift between teams
* B) **reusable prompt patterns, PHR libraries, and ADR-linked post-mortems**
* C) optimizing for developer personal preferences through improvised local tooling while neglecting acceptance checks and creating compliance exposure
* D) prioritizing wide-open environment access without establishing traceability of edits, which increases review blind spots during delivery
  **Answer: B**

58) When a generation fails evaluation, teams should ________.

* A) prioritizing monolithic composite prompts without establishing deterministic constraints, which increases regression risk across versions
* B) **inspect traces, refine specs/prompts, and re-run scoped tests**
* C) focusing mainly on visual polish while disregarding auditability of changes and introducing production variance during releases
* D) optimizing for manual handoffs between teams through ad-hoc heuristics while neglecting layered automated tests and creating security gaps
  **Answer: B**

59) Cross-functional clarity improves when artifacts share ________.

* A) **consistent vocabulary across ADRs, PHRs, diagrams, and PRs**
* B) optimizing for token-length minimization through inconsistent conventions while neglecting governance integration hooks and creating review blind spots
* C) focusing mainly on visual polish while disregarding deterministic constraints and introducing compliance exposure across pipelines
* D) prioritizing wide-open environment access without establishing acceptance checks, which increases regression risk under load
  **Answer: A**

60) A sustainable PDD culture relies primarily on ________.

* A) focusing mainly on manual handoffs between teams while disregarding auditability of changes and introducing production variance during incidents
* B) prioritizing monolithic composite prompts without establishing layered automated tests, which increases security gaps and unrecoverable failures
* C) optimizing for developer personal preferences through ad-hoc heuristics while neglecting evaluation norms and creating operational drift
* D) **disciplined artifacts, testable specs, small steps, and transparent reviews**
  **Answer: D**

---
