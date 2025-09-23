# Learning Quiz 1 with Inline Answers

Here’s a **graduate-level, concept-focused learning MCQ quiz** (60 questions) spanning everything we covered: **GPS Engineering** (SDD × PDD × TDD × EDD × ADR × PHR × PR), agent handoffs & guardrails, structured contracts, SSE, governance, metrics, dual-environment practice (Cursor vs VS Code + Codex), policy-as-code, and observability.
Each item includes 4 options, followed by the **correct answer inline** with **detailed explanations** (why correct; why others are wrong).

---

1. What is the core purpose of **Spec-Driven Development (SDD)** in GPS Engineering?
   A) Replace code reviews with automation
   B) Translate product intent into verifiable, testable contracts and constraints
   C) Increase token counts and creativity in generations
   D) Shorten CI runtime by skipping stages
   **Answer: B.** SDD defines behavior, constraints, and acceptance criteria so intent becomes an executable contract. **A** overstates—reviews still matter. **C** is unrelated to contracts. **D** is not the goal; reliability is.

2. Why does **PDD** emphasize “baby steps”?
   A) To produce large diffs for dramatic progress
   B) To isolate cause/effect, stabilize scope, and keep reviews precise
   C) To avoid writing tests until later
   D) To discourage ADRs and PHRs
   **Answer: B.** Small, sequenced prompts reduce confounding variables and improve reviewability. **A** harms attribution. **C** violates GPS. **D** removes traceability.

3. The most accurate description of **GPS Engineering** is:
   A) A prompt style guide
   B) Governed Prompt Software Engineering: specs + prompts + tests + evals + decisions + PR gates
   C) A Docker build trick
   D) A single-IDE feature set
   **Answer: B.** GPS unifies governance artifacts and gates. **A/C/D** are narrow or tool-specific.

4. Conceptually, **TDD** contributes by:
   A) Optimizing cost per token
   B) Encoding behavioral expectations independent of the LLM’s stochasticity
   C) Replacing specs entirely
   D) Measuring UI fidelity
   **Answer: B.** Tests assert binary behaviors regardless of model variance. **A/D** are orthogonal. **C** is wrong; TDD complements specs.

5. **EDD** adds what beyond TDD?
   A) Visual snapshots only
   B) Scenario-level behavior scoring and drift detection across versions
   C) Faster CPU instructions
   D) Automatic PR merging
   **Answer: B.** EDD evaluates model behaviors under rubrics and detects drift. **A/C/D** don’t address behavior quality.

6. **ADRs** exist primarily to:
   A) Track build artifacts
   B) Preserve decision context, options, trade-offs, and consequences
   C) Store commit hashes
   D) Replace PHRs
   **Answer: B.** ADRs capture the “why” for future reasoning. **A/C** are different artifacts. **D** is wrong—PHRs capture prompts/intent, not architecture decisions.

7. **PHRs** (Prompt History Records) are necessary because they:
   A) Replace git entirely
   B) Provide immutable evidence mapping prompts → diffs → acceptance
   C) Eliminate the need for CI
   D) Track GPU fan speed
   **Answer: B.** PHRs create auditable links between intent and changes. **A/C/D** are irrelevant.

8. The PR template’s **Spec-Compliance** checkbox exists to:
   A) Enforce branding
   B) Affirm that implementation matches spec via tests/evals before merge
   C) Skip review on small PRs
   D) Trigger production deploys automatically
   **Answer: B.** It’s a governance gate for contract alignment. **A/C/D** misrepresent intent.

9. Why prefer **structured outputs** (e.g., Pydantic models)?
   A) Nicer formatting
   B) Deterministic parsing/validation enabling safer integrations
   C) More tokens for style
   D) Faster rendering
   **Answer: B.** Structure supports validation and downstream reliability. **A/C/D** are not the aim.

10. A top-level error envelope like `{"error_code":"MISSING_USER_MESSAGE"}` is valuable because:
    A) It increases payload size
    B) It simplifies client parsing and failure handling across languages
    C) It improves color themes
    D) It reduces test needs
    **Answer: B.** A consistent, shallow shape reduces client complexity. **A/C/D** are irrelevant.

11. The **tool-first** policy primarily aims to:
    A) Maximize generation length
    B) Route deterministic subproblems (math/time) to functions to reduce hallucinations
    C) Remove model reasoning steps
    D) Disable handoffs
    **Answer: B.** Deterministic tools shrink hallucination surface. **A/C/D** are misinterpretations.

12. **Handoffs** in multi-agent systems conceptually represent:
    A) Random agent selection
    B) Intent-conditioned control transfer with schema/state invariants
    C) Static function calls only
    D) UI event hooks
    **Answer: B.** Handoffs are governed routing between specialized agents. **A/C/D** miss the intent dimension.

13. Why is **SSE** often chosen for v1 streaming?
    A) Binary frame support
    B) Simpler infra, proxy-friendly, monotonic token emission
    C) Full-duplex control channels
    D) Mandatory compression
    **Answer: B.** SSE is minimal and deploys easily for one-way token streams. **A/C/D** aren’t primary needs.

14. The **SSE** terminator `data:[DONE]\n\n` exists to:
    A) Reduce payload size
    B) Signal stream completion so clients finalize safely
    C) Activate backpressure
    D) Enable binary transfer
    **Answer: B.** The sentinel provides a clear completion contract. **A/C/D** not applicable.

15. “**Smallest change to green**” optimizes:
    A) CI billing
    B) Causal attribution for failing/growing tests
    C) Token creativity
    D) Reviewer humor
    **Answer: B.** Small diffs isolate causes, speeding diagnosis. **A/C/D** off-target.

16. The dual environment approach (Cursor + Codex) is justified because:
    A) They are identical tools
    B) Each optimizes different cognitive modes (interactive edits vs agentic wide tasks)
    C) Only Cursor supports Python
    D) Codex replaces CI
    **Answer: B.** Use the right environment for the task. **A/C/D** are false.

17. **Model-agnosticism** at the spec level means:
    A) Vendor-specific contracts
    B) Contracts/evals stay valid when swapping providers
    C) Ignoring latency or cost
    D) Fixing one decoding strategy permanently
    **Answer: B.** Specs/evals must survive provider changes. **A/C/D** contradict portability.

18. The key difference between **tests** and **evals** is:
    A) Tests are visuals; evals are numeric
    B) Tests assert binary conformance; evals score scenario behaviors via rubrics
    C) Tests are optional; evals mandatory
    D) They are equivalent
    **Answer: B.** Tests = binary; evals = graded behaviors. **A/C/D** incorrect.

19. A **thin spec** should avoid:
    A) Pre/postconditions and examples
    B) Implementation detail that overconstrains design choices
    C) Error envelopes
    D) Acceptance criteria
    **Answer: B.** Specs express “what,” not “how.” **A/C/D** belong.

20. Why keep **offline/mocked tests** by default?
    A) To avoid writing docs
    B) To minimize nondeterminism from networks/providers and keep signals stable
    C) To skip CI
    D) To remove coverage needs
    **Answer: B.** Determinism improves reliability. **A/C/D** are anti-patterns.

21. **Observability** in agent systems should capture at minimum:
    A) Editor theme
    B) Spans for tools/handoffs with inputs shape, outputs, timing, errors
    C) Token art
    D) Window titles
    **Answer: B.** These signals enable debugging and governance. Others are noise.

22. **Policy-as-code** succeeds when:
    A) Rules live in slides
    B) CI enforces lint, unit/contract tests, eval thresholds, and secret scanning as merge gates
    C) Humans remember
    D) Everything is manual
    **Answer: B.** Automated gates make governance real. **A/C/D** are brittle.

23. A **PHR ID** scheme should optimize:
    A) Aesthetics only
    B) Temporal ordering, slice mapping, and reproducibility in audits
    C) Random UUIDs with no meaning
    D) Minimal length regardless of clarity
    **Answer: B.** IDs must support traceability and analysis. **A/C/D** hinder audits.

24. The **Explainer prompt** adds value by:
    A) Generating code samples
    B) Summarizing intent, diffs, rationale, and residual risks concisely
    C) Replacing the PR entirely
    D) Hiding ADR links
    **Answer: B.** It makes reasoning explicit for reviewers. **A/C/D** miss the purpose.

25. A **governed refactor** should:
    A) Change public contracts freely
    B) Preserve external behavior and keep tests green while improving internals
    C) Skip documentation
    D) Add dependencies casually
    **Answer: B.** Behavior preservation is the point. **A/C/D** reduce safety.

26. **Traceability** in GPS is best delivered by linking:
    A) README ↔ LICENSE
    B) Spec ↔ PHR ↔ ADR ↔ PR ↔ CI artifacts
    C) Branch ↔ Tag only
    D) Screenshot ↔ Slack
    **Answer: B.** That chain reconstructs decisions and outcomes. Others are partial.

27. A **scope discipline** eval should penalize:
    A) Matching schema exactly
    B) Adding unrequested fields or formats, even if “helpful”
    C) Returning required fields only
    D) Using structured outputs
    **Answer: B.** Discipline requires staying inside contract. **A/C/D** are compliant.

28. **Spec versioning** matters because it:
    A) Changes editor shortcuts
    B) Aligns behavior changes with migrations, deprecations, and historical analysis
    C) Reduces PR text
    D) Improves font ligatures
    **Answer: B.** Versioned specs enable safe evolution. **A/C/D** irrelevant.

29. Which metric pair best reflects **delivery health**?
    A) Stars and image size
    B) Lead time to change + change-failure rate (with MTTR context)
    C) Lines of code and comments
    D) PR emojis and velocity
    **Answer: B.** These directly correlate with flow and stability. Others are proxies/noise.

30. **Red-team EDD** checks should include:
    A) GIF counts
    B) Prompt-injection attempts and policy-violation scoring against tool misuse
    C) PR word counts
    D) Readme length
    **Answer: B.** Safety is behavioral; test it. **A/C/D** don’t measure safety.

31. The **SSE** response header must be:
    A) `Content-Type: application/json`
    B) `Content-Type: text/event-stream`
    C) `Accept: text/event-stream`
    D) `X-Stream: on`
    **Answer: B.** The server sets SSE content type. **C** is a client request header.

32. A **contract test** ensures:
    A) Training dataset freshness
    B) Interface stability regardless of internal implementation changes
    C) GPU throttle correctness
    D) CLI color fidelity
    **Answer: B.** That’s the essence of contract testing. Others unrelated.

33. **Spec creep** should be handled by:
    A) Mutating scope inside an ongoing PR
    B) Creating new micro-spec + PR for the extra scope
    C) Deleting tests to fit schedule
    D) Ignoring evals
    **Answer: B.** New scope → new slice/PR. **A/C/D** erode governance.

34. A mature **prompt library** ought to be:
    A) Ephemeral and private
    B) Versioned, ID’d, and mapped to specs/tests/evals
    C) Screenshots only
    D) Opaque to reviewers
    **Answer: B.** Reuse with governance. Others block traceability.

35. The **best justification** for “No green, no merge” is:
    A) It looks strict
    B) It converts informal confidence into formal, scalable quality gates
    C) It saves CI credits
    D) It prevents PR creation
    **Answer: B.** Formal gates scale quality. **A/C/D** aren’t the reason.

36. **Evaluation drift** is mitigated by:
    A) Longer prompts
    B) Versioned suites run on changes with thresholds and replicates
    C) Random spot checks only
    D) Turning evals off after v1
    **Answer: B.** Regular controlled runs detect regressions. **A/C/D** are weak.

37. A statistically sound eval protocol includes:
    A) One sample per item with random seed
    B) Replicates with fixed seeds per model version and stratified aggregation
    C) No logging to save time
    D) Changing datasets without tracking
    **Answer: B.** Replication + control reduces variance. **A/C/D** undermine inference.

38. **Model substitution** should be accompanied by:
    A) New logos
    B) Re-running suites with equivalence thresholds and rollback criteria
    C) Skipping tests to move fast
    D) Manual QA only
    **Answer: B.** Verify parity; protect against regressions. Others unsafe.

39. A **thin slice** is ideally:
    A) 1–3 prompts and a handful of tests from spec to green
    B) A week-long mega-change
    C) An untested refactor
    D) Diagram-only deliverable
    **Answer: A.** Keep slices small and testable. **B/C/D** miss the point.

40. **Observability** should include handoff metadata to:
    A) Entertain dashboards
    B) Support debugging and post-hoc analysis of routing decisions
    C) Inflate logs
    D) Reduce tests
    **Answer: B.** It makes routing auditable. **A/C/D** add no reliability.

41. The **Explainer prompt** differs from codegen by:
    A) Asking for colors
    B) Stating rationale, risks, and summary of changes tied to tests
    C) Changing public API
    D) Increasing temperature
    **Answer: B.** It communicates reasoning, not code. **A/C/D** irrelevant/harmful.

42. A **governance smell** is when:
    A) PRs link Spec + PHR + ADR + CI
    B) Merges happen on red tests or without PHR/ADR references
    C) CI enforces eval thresholds
    D) Prompt libraries are versioned
    **Answer: B.** This breaks gates/traceability. Others are good practice.

43. **Guardrails** add value by:
    A) Enforcing output shape/limits/policies and enabling corrective retries
    B) Replacing tests entirely
    C) Removing evals
    D) Increasing token counts
    **Answer: A.** Guardrails constrain outputs; tests/evals still needed. **B/C/D** wrong.

44. **Retry logic** is warranted when:
    A) Guardrail/schema checks fail and a correction hint can be applied
    B) The IDE freezes briefly
    C) Any flake occurs anywhere
    D) Coverage drops
    **Answer: A.** Targeted retries recover from structured violations. **B/C/D** misuse.

45. **Monotonic streaming** means:
    A) Only decreasing latency
    B) Append-only token emission with stable framing so clients reconstruct progressively
    C) Binary frames required
    D) Fixed chunk sizes
    **Answer: B.** Monotonicity ensures predictable reconstruction. Others aren’t necessary.

46. The most persuasive **postmortem evidence** pair is:
    A) Emojis and screenshots
    B) PHRs with exact prompts plus before/after eval artifacts
    C) Lines of code changed
    D) PR comment counts
    **Answer: B.** Shows intent, change, and effect. Others are weak proxies.

47. A **reproducible EDD** setup requires:
    A) Informal notes
    B) Fixed datasets, versioned configs, seeds, and captured execution environment
    C) Randomized everything
    D) Cloud only
    **Answer: B.** Reproducibility depends on controlled inputs and envs. Others lack control.

48. **Cross-functional reviews** are valuable because they:
    A) Slow teams by design
    B) Surface non-functional risks (security, privacy, reliability) within the same governance loop
    C) Replace tests with opinions
    D) Obviate specs
    **Answer: B.** They complement engineering checks. **A/C/D** are misconceptions.

49. The conceptual value of **contract tests** in LLM apps is to:
    A) Guarantee perfect reasoning
    B) Keep interfaces stable as models/tools change under the hood
    C) Save GPU time
    D) Modify UI speed
    **Answer: B.** Contracts decouple internals from clients. **A/C/D** irrelevant.

50. **KPIs** aligned with GPS include:
    A) Theme colors
    B) Lead time, change-failure rate, MTTR, coverage, ADR density
    C) Lines per file
    D) Number of branches
    **Answer: B.** These are reliability/flow metrics. Others are weak proxies.

51. A principled **risk triage** during review prioritizes:
    A) Commit message poetry
    B) Change surface × component criticality with rollback plan noted
    C) Alphabetical import order
    D) PR emoji density
    **Answer: B.** Focus on impact and reversibility. Others are stylistic.

52. The main **epistemic benefit** of ADRs is:
    A) Better syntax highlighting
    B) Decision provenance enabling counterfactual reasoning when incidents occur
    C) Fewer PRs
    D) Smaller images
    **Answer: B.** ADRs enable “what if” analyses later. Others are unrelated.

53. **Cursor** vs **Codex** at the conceptual level:
    A) Cursor only for Python, Codex only for JS
    B) Cursor optimizes interactive, inline edits; Codex optimizes agentic, repo-scale tasks and PR prep
    C) Cursor replaces CI; Codex replaces tests
    D) They are interchangeable
    **Answer: B.** Different strengths for different modes. **A/C/D** false.

54. A **thin spec** should include which trio?
    A) UI color palette, font sizes, logos
    B) I/O contracts, constraints/limits, acceptance checks
    C) IDE preferences, keybindings, theme
    D) Build flags, compiler switches, linters
    **Answer: B.** Those are enforceable contracts. Others are environment details.

55. **Evaluation overfitting** looks like:
    A) High scores on narrow fixtures without generalization in the field
    B) Stable performance across suites
    C) Slower CI times
    D) More tests than before
    **Answer: A.** Overfitting to fixtures harms real-world behavior. Others don’t define it.

56. A mature **policy-as-code** system:
    A) Provides optional guidelines
    B) Enforces lint/tests/evals/secret scanning as hard gates in CI
    C) Uses manual checklist screenshots
    D) Depends on memory
    **Answer: B.** Automation ensures consistency. **A/C/D** are brittle.

57. **Guardrail violations** should trigger:
    A) Silent ignoring
    B) A bounded retry with corrective hints or a graceful error per contract
    C) Model swap without tests
    D) Rerun CI only
    **Answer: B.** Controlled recovery or explicit error is safe. Others are unsafe.

58. The conceptual benefit of **small PRs** is:
    A) Aesthetics
    B) Clearer scope, faster review, easier attribution of effects
    C) More merges for vanity
    D) Fewer tests written
    **Answer: B.** Small deltas increase quality and speed. Others are noise.

59. **Model choice** should be governed by:
    A) Blog popularity alone
    B) Spec-linked eval deltas under cost/latency/stability constraints
    C) Long prompts by personal taste
    D) Default IDE settings
    **Answer: B.** Choose based on measured behavior vs constraints. Others are subjective.

60. The shift from **PDD → GPS** is fundamentally:
    A) From prompts to hand coding
    B) From speed alone to auditable velocity with formal contracts and evaluation
    C) From tests to diagrams
    D) From specs to intuition
    **Answer: B.** GPS keeps PDD speed but adds governance and traceability. **A/C/D** regress.

---

