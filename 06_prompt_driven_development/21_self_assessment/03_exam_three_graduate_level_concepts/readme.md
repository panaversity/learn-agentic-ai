# Quiz 3

Here’s a **third, graduate-level 60-question MCQ quiz** focused on the **concepts** (not example particulars) from our GPS Engineering method: SDD × PDD × TDD × EDD × ADR × PHR × PR, agent architectures, evaluation, governance, metrics, and dual-environment practice. **Answer key in the file answer_key.md**

---

## Multiple-Choice Questions (Concept-Focused)

1. The most fundamental purpose of **SDD** in AI-assisted engineering is to:
   A) Maximize model creativity
   B) Convert intent into testable contracts and constraints
   C) Replace code review meetings
   D) Eliminate refactoring

2. Compared to ad-hoc prompting, **PDD** primarily improves outcomes by:
   A) Raising temperature
   B) Sequencing prompts with scope, constraints, and acceptance checks
   C) Removing tests
   D) Enlarging diffs

3. The **governance gap** addressed by GPS Engineering is best defined as:
   A) Lack of GPUs
   B) Speed without traceability and quality gates
   C) Missing UI mockups
   D) Insufficient logs

4. **TDD** in LLM systems is most valuable because it:
   A) Guarantees perfect model outputs
   B) Encodes behavioral expectations independent of the model
   C) Eliminates the need for specs
   D) Removes the need for evaluation

5. **EDD** supplements TDD by focusing on:
   A) CPU usage metrics
   B) Scenario-level behavior and drift across versions
   C) Binary serialization formats
   D) Editor ergonomics

6. A well-formed **ADR** should capture:
   A) Only the winning option
   B) Context, options, decision, and consequences
   C) A single screenshot
   D) Team bios

7. **PHRs** are essential because they:
   A) Replace version control
   B) Preserve prompt intent, scope, and outcomes as auditable artifacts
   C) Eliminate the need for tests
   D) Serve as marketing copy

8. The **Spec-Compliance** check in PRs mainly ensures:
   A) Branding consistency
   B) Implementation aligns with written contracts and acceptance criteria
   C) Larger PRs
   D) Integration without reviewers

9. The principle of **“smallest change to green”** reduces:
   A) Reviewer count
   B) Confounding variables during diagnosis and review
   C) Lint warnings
   D) CI duration only

10. In agentic systems, **handoff** primarily supports:
    A) Random agent selection
    B) Separation of concerns via specialization
    C) Token pooling
    D) Cache warming

11. **Guardrails** provide value because they:
    A) Increase verbosity
    B) Constrain outputs to shape, bounds, and policies
    C) Replace authorization
    D) Disable retries

12. **Structured outputs** in LLM apps are desirable primarily to:
    A) Improve font rendering
    B) Enable deterministic downstream handling and validation
    C) Increase token usage
    D) Disable caching

13. **Offline tests** are emphasized because they:
    A) Reduce cloud costs and remove nondeterminism from network dependencies
    B) Improve GPU throughput
    C) Generate diagrams
    D) Replace CI

14. The conceptual difference between **tests** and **evals** is that:
    A) Tests are visual; evals are numeric
    B) Tests assert program behaviors; evals score model behaviors against rubrics
    C) Tests are optional; evals are mandatory
    D) They are identical

15. In a governed process, **traceability** is best achieved by linking:
    A) Logs to screenshots
    B) Spec ↔ PHR ↔ ADR ↔ PR ↔ CI
    C) README ↔ LICENSE
    D) Branch ↔ Tag only

16. A **thin spec** should avoid:
    A) Behavior, constraints, acceptance
    B) Implementation detail that overconstrains design
    C) Contract examples
    D) Input/output definitions

17. A key risk of **vibe coding** in multi-agent systems is:
    A) Excessive type hints
    B) Architecture drift due to ambiguous, shifting prompts
    C) Too many unit tests
    D) Short ADRs

18. The **dual-environment** recommendation (e.g., interactive editor + agentic tool) reflects that:
    A) One editor is always superior
    B) Different environments optimize different cognitive modes
    C) Only one can run tests
    D) Both must be cloud-only

19. **Evaluation drift** is best mitigated by:
    A) Longer prompts
    B) Versioned behavior suites and periodic re-runs
    C) Removing guardrails
    D) Disabling test retries

20. **Spec versioning** matters because:
    A) JSON is unstable
    B) It situates behavior changes and keeps artifacts aligned in time
    C) It changes IDE shortcuts
    D) It prevents CI runners from caching

21. In GPS Engineering, **refactor** should:
    A) Change public contracts
    B) Preserve behaviors and interfaces while improving internals
    C) Remove tests after green
    D) Rewrite ADRs

22. The **primary advantage** of small PRs is:
    A) Stylish diffs
    B) Faster, higher-quality review with clearer scope
    C) More merge conflicts
    D) Bigger coverage gaps

23. **Model-agnosticism** is important because it:
    A) Locks a vendor
    B) Enables portability and comparability across providers
    C) Reduces PHRs
    D) Eliminates EDD

24. The **objective** of an architect prompt is to:
    A) Produce code immediately
    B) Establish micro-spec, constraints, and acceptance before generation
    C) Edit unrelated files
    D) Change CI runners

25. **Scope discipline** in evals should penalize:
    A) Returning only requested fields
    B) Adding fields or formats not specified
    C) Matching schema exactly
    D) Using structured outputs

26. A governance smell is when PRs:
    A) Link spec and ADRs
    B) Merge on red or without PHR/ADR references
    C) Are small and reviewed
    D) Pass CI with evals

27. The **most resilient** secrets policy is:
    A) Embed keys within prompts
    B) Use environment variables and rotate routinely
    C) Store in README
    D) Commit to VCS for convenience

28. A **metric** suited to assess slice health is:
    A) Lines of code added
    B) Lead time to change for small diffs
    C) Number of comments per PR
    D) Refactor count

29. The primary reason to **prefer structured contracts** in AI services is:
    A) Easier CSS theming
    B) Enables typed validation and safer integration points
    C) More tokens
    D) Lazier clients

30. The **PHR ID convention** helps teams:
    A) Hide prompts
    B) Reference precise change intents in reviews and retros
    C) Collapse histories
    D) Avoid CI

31. A **responsible** use of retries in LLM flows is to:
    A) Retry indefinitely
    B) Retry boundedly when guardrails or schema validation fails
    C) Disable caching
    D) Reset CI

32. **Thin slices** matter because they:
    A) Inflate diffs
    B) Reduce cognitive load and limit blast radius of mistakes
    C) Increase flakiness
    D) Replace documentation

33. The most conceptual reason to **store ADRs with code** is:
    A) Cheaper hosting
    B) Co-evolution of decisions with implementation
    C) Easier emojis
    D) Larger PDFs

34. An **effective prompt library** should be:
    A) Ephemeral and private
    B) Versioned, reusable, mapped to specs and evals
    C) Only screenshots
    D) Untagged and ad-hoc

35. In agent design, **tool-first** policy aims to:
    A) Prevent deterministic operations from being free-form generations
    B) Remove tools entirely
    C) Raise temperature
    D) Reduce observability

36. The **best** conceptual justification for small diffs is:
    A) They look elegant
    B) They isolate causality, therefore speed up learning and review
    C) They pass CI faster by magic
    D) They produce more merges

37. **Observability** in LLM workflows is primarily to:
    A) Style dashboards
    B) Reveal steps, tool calls, and routing for debugging and governance
    C) Increase token usage
    D) Decrease test coverage

38. The term **auditable velocity** means:
    A) Unreviewed speed
    B) Fast iteration with recorded specs, prompts, and decisions under green gates
    C) Merge on failure
    D) Bypass CI

39. **Contract tests** in AI apps ensure:
    A) Training data freshness
    B) Stability of interfaces despite internal changes
    C) GPU savings
    D) Diagram accuracy

40. A **graduate-level** failure mode for eval suites is:
    A) Too many rubrics
    B) Overfitting prompts to eval fixtures rather than general behaviors
    C) Running nightly
    D) Using numeric scoring

41. The most conceptual value of **PR templates** is:
    A) Design aesthetics
    B) Normalizing governance and traceability checklists across all changes
    C) Auto-merging code
    D) Muting reviewers

42. **Ethical source handling** in AI development emphasizes:
    A) Copy-pasting licenses
    B) Attribution, license compliance, and data governance
    C) Avoiding documentation
    D) Maximizing token counts

43. **Handoffs** should log routing metadata because it:
    A) Impresses dashboards
    B) Supports post-hoc analysis of decision quality and debugging
    C) Adds latency
    D) Lowers coverage

44. A **graduate signal** of GPS maturity is:
    A) Massive PRs
    B) High spec/test alignment with short lead times and low change failure rate
    C) Single-step merges
    D) Random evals

45. **Retry prompts** should be used when:
    A) The UI is slow
    B) Guardrails or contract checks fail and a correction hint is available
    C) The editor theme changes
    D) Any flakiness occurs anywhere

46. **Diff-only** responses from AI assistants help because they:
    A) Hide the spec
    B) Minimize accidental changes and encourage focused review
    C) Increase token usage
    D) Lower coverage

47. **Model choice** should be treated as:
    A) Irrelevant to behavior
    B) A replaceable dependency governed by specs and evals
    C) A permanent decision
    D) A personal preference

48. **Cross-functional reviews** are helpful because they:
    A) Slow teams
    B) Surface non-functional concerns like security, privacy, and reliability
    C) Replace tests
    D) Remove ADRs

49. **Version pinning** of dependencies and models primarily serves:
    A) Branding
    B) Reproducibility for tests and evals
    C) UI previews
    D) Token budget

50. **Prompt hygiene** includes:
    A) Hidden rules
    B) Clear scope, constraints, inputs/outputs, and acceptance mapping
    C) Long narratives
    D) Unbounded edits

51. **Spec creep** can be contained by:
    A) Merging early
    B) Micro-slicing and renegotiating scope via new specs and PRs
    C) Deleting tests
    D) Disabling evals

52. The conceptual benefit of **structured error envelopes** is:
    A) Fancier logs
    B) Consistent failure handling across clients and languages
    C) Larger payloads
    D) Removal of tests

53. **Behavioral KPIs** for GPS include:
    A) Window size
    B) Lead time, change-failure rate, MTTR, coverage, ADR density
    C) File size
    D) Color scheme

54. **Test isolation** matters because it:
    A) Reduces CI workers
    B) Prevents interdependence and flakiness from shared state
    C) Rewrites diffs
    D) Forces GPU usage

55. **Reproducibility** in evals requires:
    A) Non-determinism
    B) Fixed seeds, fixed suites, and versioned configs
    C) Elastic prompts
    D) Hidden rubrics

56. **Governed refactor prompts** should specify:
    A) Any change you like
    B) Preserve public behavior, keep tests green, summarize rationale
    C) Remove tests to move fast
    D) Skip documentation

57. **Risk triage** in PRs conceptually prioritizes:
    A) UI polish
    B) Surface area of change vs criticality of touched components
    C) Font settings
    D) Number of comments

58. **Causality** in GPS is enhanced by:
    A) Larger batches
    B) Smaller, independent slices with explicit acceptance
    C) Nightly merges
    D) Hidden diffs

59. **Policy as code** for governance succeeds when:
    A) It is optional
    B) CI enforces lint, tests, and evals as merge gates
    C) It is documented only
    D) It is manual

60. The overarching conceptual shift from PDD to **GPS Engineering** is:
    A) From prompts to programming languages
    B) From speed alone to speed with formalized governance, traceability, and evaluation
    C) From tests to diagrams
    D) From tools to intuition

---

