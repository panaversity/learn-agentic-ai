# Quiz 4

Here’s a **fourth, MIT PhD–level 60-question MCQ quiz** centered on the *concepts* behind GPS Engineering (SDD × PDD × TDD × EDD × ADR × PHR × PR), agent architectures, governance, eval science, and reliability. **Answer key in the answer_key.md file**

---

## Multiple-Choice Questions (MIT PhD Level)

1. In GPS Engineering, which framing best captures **specs as a contract** between generative systems and deterministic components?
   A) Specs as design docs for managers only
   B) Specs as reference models constraining stochastic generators via externally verifiable obligations
   C) Specs as UI text templates for consistency
   D) Specs as Git metadata mirroring code style

2. Consider an LLM agent with tools and guardrails. Which **soundness property** is most directly enforced by TDD + contract tests?
   A) Model calibration over long horizons
   B) External behavior conformance independent of internal sampling
   C) Optimal decoding under length penalties
   D) Pareto efficiency of tool selection

3. For EDD, which evaluation protocol most robustly **detects regression** across model upgrades?
   A) Single run with temperature 0.9
   B) Paired, batched A/B with fixed seeds, multiple replicates, stratified prompts, and nonparametric tests
   C) Manual spot checks by reviewers
   D) Randomized seeds with no tracking

4. Which statement best characterizes **prompt drift** as an empirical phenomenon?
   A) Stationary process with zero variance
   B) Distributional shift in model outputs given stable inputs due to context accretion or subtle spec leakage
   C) Purely UI-driven artifact
   D) Only occurs when temperature>1

5. A rigorous **scope discipline** rubric penalizes:
   A) Omission of optional fields
   B) Inclusion of unrequested keys or formats even when semantically correct
   C) Short outputs
   D) Lowercase field names

6. When choosing **SSE over WebSocket** for v1, which formal trade-off dominates under GPS?
   A) Throughput optimality of bidirectional channels
   B) Complexity minimization and proxy compatibility for monotonic token emission
   C) Binary frame support for large tensors
   D) Server push requirements for images

7. Which property does **“smallest change to green”** optimize in the presence of flaky behaviors?
   A) Computational complexity of CI runners
   B) Causal attribution of test failures to the minimal diff
   C) Semantic coherence of docstrings
   D) Global optimality of refactor plans

8. Under GPS, **model choice** should be governed primarily by:
   A) Marketing and blog posts
   B) Spec-linked eval deltas, cost/latency constraints, and stability envelopes
   C) IDE popularity
   D) Random seed reproducibility only

9. Which statement about **PHRs** is most correct in a forensic audit?
   A) They are optional once code is merged
   B) They serve as immutable intent artifacts mapping diffs to prompts and acceptance criteria
   C) They duplicate ADRs and can be deleted
   D) They are transient CI logs

10. For adversarial robustness, which **red-team test** belongs in EDD smoke?
    A) Token count statistics
    B) Prompt injections targeting tool misuse and field exfiltration scored by policy-violation detectors
    C) GPU temperature monitoring
    D) Semantic similarity between comments

11. In multi-agent orchestration, a **handoff** can be formalized as:
    A) Syntax rewrite rule
    B) Intent-conditioned control transfer with invariants on session state and output schema
    C) Random walk between agents
    D) Static call graph expansion

12. A **thin spec** that remains enforceable over time should include:
    A) Implementation pseudocode
    B) Input/Output contracts, pre/postconditions, error envelopes, and acceptance tests
    C) Hiring policies
    D) Diagram color palettes

13. Which evaluation design best **bounds variance** in stochastic decoding while estimating performance?
    A) One sample per item with temperature 0
    B) Multiple independent samples per item with fixed seeds per version and stratified aggregation
    C) Unlimited sampling until success
    D) Random seeds each run without logging

14. What is the **primary epistemic benefit** of ADRs co-located with code?
    A) Faster merges
    B) Preservation of decision provenance enabling counterfactual reasoning during incidents
    C) Better syntax highlighting
    D) Smaller images

15. For **reliability**, which metric pair is most diagnostic in GPS dashboards?
    A) Lines of code and stars
    B) Lead time to change and change-failure rate with MTTR overlays
    C) PR description length and emoji density
    D) Docker layer count and image size

16. A **governed refactor prompt** should require:
    A) Rewriting public contracts
    B) Preservation of public behavior with test invariants; internal restructuring with formal explainer deltas
    C) Maximizing diff size
    D) Removal of guardrails

17. Which **test isolation** strategy is correct for LLM-backed services?
    A) Live calls to frontier models in unit tests
    B) Deterministic mocks for unit/contract tests; model-in-the-loop only in eval stages
    C) No mocks, pure integration
    D) Tests disabled to reduce variance

18. The **Spec-Compliance** checkbox in PRs contributes to:
    A) UI theme consistency
    B) Enforceable linkage of artifacts: spec→tests/evals→code diffs→PHRs/ADRs
    C) Faster Docker builds
    D) Automatic tagging

19. In PDD, the **Architect prompt** functions as:
    A) Replacement for ADRs
    B) Micro-spec generator capturing scope, constraints, acceptance, and risks pre-implementation
    C) Style guide
    D) Randomizer

20. Which is a **valid grounding** for tool-first policy?
    A) It increases temperature
    B) It routes deterministic subproblems to verifiable functions, reducing hallucination surface
    C) It simplifies tracing removal
    D) It reduces observability

21. A failure to emit `data:[DONE]` in SSE violates which property?
    A) Safety type system
    B) Stream termination contract required for client completeness detection
    C) Docker healthcheck
    D) Linting invariants

22. **Model-agnosticism** at the spec level implies:
    A) Prohibiting all vendor features
    B) Maintaining contracts and evals that remain valid under provider substitution
    C) Fixing one decoding strategy
    D) Ignoring latency

23. Which is the **best justification** for “no green, no merge”?
    A) Encourages larger PRs
    B) Converts informal confidence into formal pass/fail gates that scale across teams
    C) Helps marketing
    D) Hides regressions

24. **Evaluation overfitting** occurs when:
    A) Suites are versioned
    B) Prompts are tuned to pass narrow fixtures without generalization, degrading field performance
    C) Rubrics are public
    D) Tests run in CI

25. A **grad-level** invariance to check when swapping models is:
    A) Identical tokenization
    B) Contract preservation and error envelope stability across models under the same spec
    C) Same vendor billing
    D) Identical logits

26. For PR governance, which linking pattern maximizes **traceability**?
    A) README→PR
    B) Spec + PHR IDs + ADR IDs all referenced in PR with CI/EDD artifacts attached
    C) Code only
    D) Screenshot only

27. Under **risk triage**, what should be prioritized in review?
    A) Comment grammar
    B) Delta surface area vs criticality of components touched, with explicit rollback plan
    C) Number of commits
    D) File alphabetization

28. Which **drift detector** is most appropriate for EDD?
    A) Visual inspection of random samples
    B) Aggregate metric shifts with hypothesis tests plus targeted audits on failing buckets
    C) Counting files changed
    D) Measuring repo size

29. A formal benefit of **small diffs** is:
    A) Improved aesthetics
    B) Reduction of confounding, enabling faster attribution and post-merge stability
    C) Free compute credits
    D) Automatic docs

30. Choosing **SSE** first is aligned with which **design heuristic**?
    A) YAGNI / minimize moving parts in the critical path
    B) Always prefer bidirectional
    C) Always encode binary frames
    D) Prioritize TLS renegotiation

31. **Offline tests** primarily guard against:
    A) Missing emojis
    B) Nondeterminism and external outages affecting correctness signals
    C) Faster PRs
    D) Higher billable hours

32. A **PHR ID taxonomy** should optimize for:
    A) Aesthetic ordering
    B) Temporal ordering, slice mapping, and diff reproducibility
    C) Shortest strings only
    D) Random UUIDs without meaning

33. The **Explainer prompt** contributes to governance by:
    A) Removing PR description
    B) Producing a human-readable rationale and risk notes aligned to diffs and tests
    C) Shortening tests
    D) Hiding ADRs

34. Under GPS, which **property** distinguishes tests from evals?
    A) Tests are stochastic; evals are deterministic
    B) Tests assert binary conformance; evals assign graded judgments under rubrics
    C) Tests are optional; evals required
    D) They are equivalent

35. An **ADR consequence** should explicitly note:
    A) Which memes to use
    B) Follow-ups, trade-offs, and triggers that would reopen the decision
    C) Font ligatures
    D) Editor shortcut keys

36. A sophisticated **scope discipline** eval would:
    A) Reward additional helpful fields
    B) Penalize any deviation from declared schema regardless of semantic utility
    C) Ignore structure
    D) Reward verbosity

37. The **causal model** for red→green→refactor is that:
    A) Big diffs increase discoverability
    B) Incremental isolation raises identifiability of failure sources
    C) Refactor first reduces entropy
    D) Green before red is equivalent

38. A **model governance smell** is:
    A) Specs mapped to tests
    B) Prompt changes without PHRs or evals
    C) ADRs linked to PRs
    D) CI artifacts retained

39. Under GPS, which **artifact pair** provides the most persuasive evidence in a postmortem?
    A) Emojis + screenshots
    B) PHRs with exact prompts plus failing eval artifacts before/after
    C) Number of PR comments
    D) Code coverage percentage only

40. Which **calibration** approach is relevant to evals of graded tasks?
    A) Isotonic regression or Platt scaling on score distributions across suites
    B) Dark mode
    C) Minifying JSON
    D) Increasing temperature

41. A **privacy-aware** eval design should:
    A) Leak PII to test redaction
    B) Include synthetic PII and verify redaction policies under controlled conditions
    C) Disable logs
    D) Ignore redaction

42. **Observability spans** for agent handoffs should include:
    A) Only duration
    B) Intent signal, confidence, selected agent, handoff\_reason, and tool calls with timing
    C) File icons
    D) None; keep silent

43. A defensible **spec versioning** scheme should:
    A) Overload README headings
    B) Use semantic versioning per contract with migration notes and deprecation windows
    C) Use date emojis
    D) Avoid versions

44. What is the **primary statistical risk** of single-run evals on small suites?
    A) Overpowering
    B) High variance and Type I/II errors leading to misleading decisions
    C) Perfect power
    D) None if seeds fixed

45. An **LLM safety check** that belongs in EDD smoke is:
    A) GPU fan speed
    B) Restricted tool invocation when policy preconditions unmet
    C) Tab width
    D) Logo usage

46. Under GPS, **model substitution** should be accompanied by:
    A) New logos
    B) Re-running behavioral suites with equivalence thresholds and rollback criteria
    C) Only lints
    D) No action

47. A **well-posed architect prompt** differs from code requests because it:
    A) Asks for colors
    B) States objectives, constraints, acceptance tests, and non-goals prior to code
    C) Asks for maximal diffs
    D) Encourages free writing

48. Which **threat model** is relevant for prompt capture?
    A) None; prompts are harmless
    B) Leakage of secrets or policies via PHRs if not scrubbed and access controlled
    C) Only DoS
    D) Cache eviction

49. **Spec creep** should be managed by:
    A) Merging big batches
    B) Renegotiating scope with new micro-specs and PRs rather than mutating in-flight slices
    C) Deleting tests
    D) Turning off evals

50. A **maturity signal** for GPS is:
    A) Unstructured prompts
    B) Organization-wide prompt libraries, rules bundles, dashboards, and PR gates
    C) Ad-hoc CI
    D) Per-dev README forks

51. For **causal inference** in regressions, which counterfactual is most actionable?
    A) Post-hoc narratives
    B) Re-run previous model on current suite and new model on previous suite under matched seeds
    C) Random seeds every time
    D) Only manual QA

52. **Reproducibility** in evals depends most on:
    A) Fancy charts
    B) Fixed datasets, versioned configs, seeds, and execution environment capture
    C) Large prompts
    D) Proprietary runners

53. **Policy as code** succeeds when:
    A) CI enforces lint, tests, eval thresholds, and secret scanning as hard gates
    B) Guidelines live in slides
    C) Humans remember rules
    D) Nothing is automated

54. A theoretically justified reason to **prefer structured error envelopes** is:
    A) Aesthetic JSON
    B) Language-agnostic parseability minimizing client error handling complexity
    C) Extra bytes
    D) Nicer logs

55. The **most general definition** of GPS Engineering is:
    A) IDE automation strategy
    B) Governed Prompt Software Engineering unifying specs, prompts, tests, evals, decisions, and PR gates
    C) A Docker pattern
    D) A single vendor workflow

56. A **granularity** heuristic for slices is:
    A) Must require a week
    B) Implementable with one to three prompts and a handful of tests
    C) Require 1,000+ LOC diffs
    D) Prohibit tests

57. **Cross-functional review** adds value by:
    A) Removing CI
    B) Exposing non-functional risks (security, privacy, reliability) early within the same governance loop
    C) Beautifying diffs
    D) Shortening ADRs

58. **Tool call observability** should log at minimum:
    A) Only success
    B) Tool name, inputs/shape, duration, outcome status, and error class if any
    C) Terminal theme
    D) None

59. **Monotonicity** in streaming interfaces refers to:
    A) Only increasing bytes over time with consistent framing so clients can reconstruct outputs without backtracking
    B) Decreasing latency only
    C) Increasing temperature
    D) Growing Docker layers

60. The **conceptual shift** from PDD to GPS Engineering is best stated as:
    A) From prompts to code generation only
    B) From ad-hoc acceleration to governed, auditable velocity with formal contracts and evaluation
    C) From tests to diagrams
    D) From specs to intuition

---

