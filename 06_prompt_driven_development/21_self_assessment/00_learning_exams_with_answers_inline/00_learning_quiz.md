# Learning Quiz 0 with Inline Answers

Here’s a **learning MCQ quiz** (60 questions) covering the full GPS Engineering stack (SDD × PDD × TDD × EDD × ADR × PHR × PR), OpenAI Agents SDK patterns, SSE, CI/CD, dual IDE practice, governance, metrics, and more.
Each item lists options, then the **correct answer inline** with a brief explanation of why it’s correct and why the others are not.

---

1. What is the primary purpose of **Spec-Driven Development (SDD)** in GPS Engineering?
   * A) Replace code review entirely
   * B) Convert intent into testable contracts and constraints
   * C) Increase token counts for creativity
   * D) Reduce CI runtime only
   * **Answer: B.** SDD formalizes behavior, constraints, and acceptance so the system has an executable contract. **A** doesn’t follow—reviews still matter; **C** is unrelated; **D** is a side effect at best, not the goal.

2. In **Prompt-Driven Development (PDD)**, why use “baby steps”?
   * A) To maximize diff size for learning
   * B) To isolate cause/effect and keep changes reviewable
   * C) To bypass tests when prototyping
   * D) To avoid writing ADRs
   * **Answer: B.** Small, scoped prompts make attribution and review easier. **A** undermines control; **C** violates GPS; **D** weakens traceability.

3. The “**No green, no merge**” policy enforces what?
   * A) Fast-tracking large PRs
   * B) Passing tests/evals as gates before integration
   * C) Skipping PR reviews on weekends
   * D) Automatic release to prod on green
   * **Answer: B.** CI gates must be green to merge. **A/C/D** are not implied by the policy.

4. What uniquely distinguishes **EDD** from TDD?
   * A) EDD checks rubric-based model behaviors; TDD asserts programmatic contracts
   * B) EDD measures lint quality; TDD measures latency
   * C) EDD replaces tests; TDD becomes optional
   * D) EDD requires GPUs; TDD doesn’t
   * **Answer: A.** EDD focuses on scenario behaviors and drift; TDD on binary contracts. **B** confuses scopes; **C** wrong—EDD complements; **D** not inherent.

5. A good **ADR** must include:
   * A) Decision only
   * B) Context, options, decision, consequences
   * C) Screenshots of the IDE
   * D) Final code snippets
   * **Answer: B.** ADRs preserve rationale and trade-offs. **A/C/D** omit critical reasoning or are irrelevant.

6. **PHRs** (Prompt History Records) are kept to:
   * A) Replace commit history
   * B) Preserve prompts, scope, acceptance, outcomes per slice
   * C) Store Docker layers
   * D) Track GPU utilization
   * **Answer: B.** PHRs capture intent and evidence for each change. **A/C/D** are unrelated.

7. Why prefer **structured outputs** (e.g., Pydantic models) in AI apps?
   * A) Better syntax highlighting
   * B) Deterministic parsing and validation downstream
   * C) Larger payloads improve creativity
   * D) Faster UI rendering
   * **Answer: B.** Structure enables reliable integration. **A/C/D** are incidental or false.

8. The top-level error envelope for `/chat` on missing user\_message is:
   * A) `{"detail":"MISSING_USER_MESSAGE"}`
   * B) `{"error_code":"MISSING_USER_MESSAGE"}`
   * C) `{"error":{"code":"MISSING_USER_MESSAGE"}}`
   * D) `{"status":"MISSING_USER_MESSAGE"}`
   * **Answer: B.** Contract specifies top-level `error_code`. **A/C/D** violate the agreed shape.

9. For SSE, which terminator signals end of stream?
   * A) `data:[END]\n`
   * B) `data:[DONE]\n\n`
   * C) `event:done\n\n`
   * D) `data:complete\n`
   * **Answer: B.** `data:[DONE]` with a blank line is the agreed sentinel. Others aren’t the chosen contract.

10. Which OpenAI **Agents SDK** features we rely on for separation of concerns?
    * A) Sessions only
    * B) Agents, Tools, Sessions, Handoffs, Guardrails
    * C) Lambda layers
    * D) Ingress controllers
    * **Answer: B.** That’s the core SDK set we use. **A/C/D** are incomplete or unrelated.

11. The **tool-first** policy exists to:
    * A) Increase verbosity
    * B) Route math/time to deterministic functions to cut hallucinations
    * C) Reduce test counts
    * D) Force all work into code tools
    * **Answer: B.** Deterministic tools minimize model guessing. **A/C/D** misstate intent.

12. **Cursor** is strongest at:
    * A) Repo-wide autonomous refactors without oversight
    * B) Inline tab-completion, predictive multi-file edits, interactive flow
    * C) License scanning by default
    * D) GPU provisioning
    * **Answer: B.** Cursor shines in interactive editor flows. **A/C/D** not its core value.

13. **VS Code + Codex** is strongest at:
    * A) Pure tab-completion
    * B) Agentic, repo-scale tasks and PR preparation
    * C) Managing container registries
    * D) Uvicorn tuning
    * **Answer: B.** Codex excels at broader agentic tasks. **A/C/D** are not its main strengths.

14. A **thin spec** should avoid:
    * A) Contract examples
    * B) Implementation detail that overconstrains design
    * C) Acceptance checks
    * D) Error envelopes
    * **Answer: B.** Specs state *what*, not detailed *how*. **A/C/D** belong.

15. Why keep tests **offline/mocked** by default?
    * A) To hide bugs
    * B) To ensure determinism and avoid network/model variance
    * C) To skip CI
    * D) To bypass coverage
    * **Answer: B.** Offline tests stabilize signals. **A/C/D** are bad practice.

16. In PDD, the **Architect prompt** should:
    * A) Request code immediately
    * B) State micro-spec, constraints, acceptance, risks before code
    * C) Change unrelated files
    * D) Ask to skip tests
    * **Answer: B.** Architect prompts set scope and checks. **A/C/D** contradict process.

17. The purpose of the **Explainer prompt** is to:
    A) Replace PR description
    B) Summarize diffs, trade-offs, residual risk succinctly
    C) Generate architecture diagrams automatically
    D) Compile docs
    **Answer: B.** It clarifies intent and changes. **A/C/D** aren’t the goal.

18. The **smallest change to green** principle primarily reduces:
    * A) CI bill
    * B) Confounding variables in failure diagnosis
    * C) Token usage only
    * D) Reviewers needed
    * **Answer: B.** It improves causal attribution. **A/C/D** are secondary or wrong.

19. In GPS, **refactor** means:
    * A) Changing public contracts routinely
    * B) Improving internals with tests kept green
    * C) Rewriting specs mid-PR
    * D) Skipping evaluations
    * **Answer: B.** Behavior preserved, internals improved. **A/C/D** oppose governance.

20. **Traceability** is best achieved by linking:
    * A) Logs to screenshots
    * B) Spec ↔ PHR ↔ ADR ↔ PR ↔ CI artifacts
    * C) README ↔ LICENSE only
    * D) Branch ↔ Tag alone
    * **Answer: B.** That end-to-end chain is the backbone. Others are partial.

21. The PR template’s **Spec-Compliance** checkbox ensures:
    * A) Style consistency
    * B) Implementation matches spec/acceptance (tests/evals)
    * C) Automatic release notes
    * D) Version bump
    * **Answer: B.** It’s a gate for contract adherence. **A/C/D** not guaranteed.

22. Why choose **SSE** for v1 streaming?
    * A) Binary frame support
    * B) Simplicity, proxy compatibility, low infra complexity
    * C) Mandatory bidirectional control
    * D) Built-in compression
    * **Answer: B.** SSE fits minimal, one-way token flow. **A/C/D** not decisive.

23. Which CI gate most increases reliability for LLM apps?
    * A) Build first, test later
    * B) Lint + contract tests + EDD smoke **before** build/publish
    * C) Only lint
    * D) Post-deploy tests only
    * **Answer: B.** Upfront gates catch issues earlier. Others miss risks.

24. A **scope discipline** eval should:
    * A) Reward extra fields
    * B) Penalize unrequested fields/format drift
    * C) Ignore structure
    * D) Score verbosity higher
    * **Answer: B.** We enforce schema. **A/C/D** conflict with discipline.

25. **Model-agnosticism** at spec level means:
    * A) Hard-coding a vendor
    * B) Contracts/evals valid across providers
    * C) Ignoring latency
    * D) Fixing a single decoding strategy forever
    * **Answer: B.** We keep portability. **A/C/D** narrow or ignore realities.

26. Why keep **PHRs** in the repo (not chat only)?
    * A) Emoji reactions
    * B) Versioned, reviewable, linkable evidence tied to diffs
    * C) Lower token bills
    * D) Better Docker layers
    * **Answer: B.** Governance requires permanence and links. Others are irrelevant.

27. A **good acceptance test** for `/chat` checks:
    * A) Server uptime
    * B) Response matches `ChatReply` schema and required fields
    * C) README exists
    * D) Docker layer count
    * **Answer: B.** Contract tests validate schema/fields. **A/C/D** are orthogonal.

28. The **handoff** concept in agents supports:
    * A) Random switching
    * B) Specialization via intent-conditioned control transfer
    * C) Token pooling
    * D) Cache flushing
    * **Answer: B.** Handoffs route to specialized agents. Others are unrelated.

29. The best reason to **version specs** is to:
    * A) Change IDE shortcuts
    * B) Align behavior changes with artifacts and migrations
    * C) Reduce CI logs
    * D) Improve font rendering
    * **Answer: B.** Versioned specs track evolution and deprecations. Others are cosmetic.

30. Which **metric pair** is most diagnostic for delivery health?
    * A) Lines of code + stars
    * B) Lead time to change + change-failure rate (with MTTR)
    * C) Image size + theme
    * D) PR emoji count + velocity
    * **Answer: B.** Those directly reflect flow and stability. Others are noise.

31. A **red-team EDD** check should include:
    * A) GIFs in PR
    * B) Prompt-injection tests scoring policy violations/tool misuse
    * C) GPU fan speed
    * D) Screenshot diffs
    * **Answer: B.** Safety is a behavior domain. Others are irrelevant.

32. **Offline unit tests** guard primarily against:
    * A) Model/provider outages and nondeterminism
    * B) Spelling errors in comments
    * C) Color themes
    * D) Disk quotas
    * **Answer: A.** They stabilize correctness signals. Others are minor.

33. A **governed refactor prompt** should require:
    * A) Change public contract
    * B) Keep tests green, preserve behavior; summarize rationale
    * C) Add new dependencies freely
    * D) Delete flaky tests
    * **Answer: B.** Preserve interfaces; document intent. Others are anti-patterns.

34. A **governance smell** is when PRs:
    * A) Link specs and ADRs
    * B) Merge on red or without PHR/ADR references
    * C) Are small and reviewed
    * D) Include EDD artifacts
    * **Answer: B.** That breaks gates/traceability. **A/C/D** are good.

35. A **prompt library** should be:
    * A) Ephemeral & untracked
    * B) Versioned, ID’d, mapped to specs/tests
    * C) Screenshots only
    * D) Hidden from reviewers
    * **Answer: B.** Reuse + governance needs versioned prompts. Others defeat purpose.

36. **Observability** for agents should record:
    * A) Only total tokens
    * B) Spans of tools/handoffs with inputs (shape), outputs, timing, errors
    * C) Theme changes
    * D) Editor font
    * **Answer: B.** Observability supports debugging/governance. Others irrelevant.

37. A **thin slice** heuristic:
    * A) Requires large diffs
    * B) 1–3 prompts plus a handful of tests to done
    * C) Spans multiple subsystems at once
    * D) Always excludes tests
    * **Answer: B.** Keep scope small and testable. **A/C/D** are wrong.

38. **Evaluation drift** is best mitigated by:
    * A) Longer prompts
    * B) Versioned suites re-run on changes with thresholds
    * C) Skipping evals after initial pass
    * D) Manual screenshots
    * **Answer: B.** Regularized, versioned evals guard against regressions. Others don’t.

39. A statistically sound eval protocol uses:
    * A) One shot at temp 1.0
    * B) Replicates with fixed seeds per version and stratified analysis
    * C) No logging
    * D) Changing datasets at random
    * **Answer: B.** Replication + controls detect change reliably. Others increase noise.

40. A **privacy-aware** eval should:
    * A) Use real PII in logs
    * B) Use synthetic PII and verify redaction policies
    * C) Ignore privacy
    * D) Disable outputs
    * **Answer: B.** Test redaction safely. **A/C/D** unsafe or useless.

41. **uv** is recommended because it:
    * A) Replaces Docker entirely
    * B) Provides fast, reproducible Python dependency management suited for CI
    * C) Is a new linter
    * D) Generates UML
    * **Answer: B.** uv speeds and locks deps. **A/C/D** are wrong.

42. **SSE** requires the server to set:
    * A) `Content-Type: application/json`
    * B) `Content-Type: text/event-stream`
    * C) `Accept: text/event-stream`
    * D) `X-Stream: yes`
    * **Answer: B.** Server response header must be SSE. **C** is a client request header; **A/D** wrong.

43. A **contract test** ensures:
    * A) Training corpus freshness
    * B) Interface stability regardless of internal changes
    * C) GPU utilization limits
    * D) Repo size thresholds
    * **Answer: B.** That’s the essence of contract tests. Others are not.

44. A **Spec creep** control is to:
    * A) Mutate scope mid-PR
    * B) Split into new micro-specs and PRs
    * C) Delete tests
    * D) Merge everything at once
    * **Answer: B.** Micro-slicing keeps control. Others add risk.

45. Why keep **ADRs next to code**?
    * A) Emojis render better
    * B) Decisions co-evolve with implementation; change context is preserved
    * C) Save repo space
    * D) Shorter URLs
    * **Answer: B.** Co-location aids discovery and maintenance. Others trivial.

46. In GPS, **model substitution** should be accompanied by:
    * A) Logo updates
    * B) Re-running suites with equivalence thresholds and rollback rules
    * C) Only lint
    * D) Skipping tests for speed
    **Answer: B.** Behavior parity must be verified. Others unsafe.

47. The **dual-environment** recommendation rests on:
    * A) Identical UI skins
    * B) Different cognitive modes (agentic vs interactive) improve productivity
    * C) One tool is always superior
    * D) Avoiding Git
    * **Answer: B.** Each environment is best at different tasks. Others false.

48. The **PR** is the place to:
    * A) Attach links to Spec, PHR IDs, ADR IDs, and CI/EDD artifacts
    * B) Paste raw model dumps only
    * C) Skip description
    * D) Merge on yellow
    * **Answer: A.** PR centralizes traceability. Others degrade governance.

49. **Retry logic** should be used when:
    * A) Guardrails/schema fail and a correction hint is provided
    * B) The editor lags
    * C) Tests are red for any reason
    * D) You want more tokens
    * **Answer: A.** Retries help recover from structured failures. **B/C/D** misuse.

50. A **good scope discipline** failure looks like:
    * A) Exact fields per spec
    * B) Extra keys and formats not requested
    * C) Matching schema precisely
    * D) Validated structure
    * **Answer: B.** Extra fields violate the contract. **A/C/D** are compliant.

51. A **post-mortem** with strongest evidence uses:
    * A) Emojis + screenshots
    * B) PHRs (exact prompts) and before/after eval artifacts
    * C) Lines of code changed
    * D) README diffs
    * **Answer: B.** These directly show cause & effect. Others are weak.

52. **Monotonic streaming** means:
    * A) Only decreasing latency
    * B) Append-only token emission with stable framing so clients reconstruct progressively
    * C) Binary frames only
    * D) Fixed chunk sizes
    * **Answer: B.** That’s the property clients rely on. Others off.

53. A mature **policy-as-code** setup:
    * A) Posts guidelines in slides
    * B) Enforces lint/tests/evals/secret scanning as CI merge gates
    * C) Trusts memory
    * D) Uses manual checklists only
    * **Answer: B.** Automation makes governance reliable. Others stale.

54. A **learning KPI** that indicates slice health:
    * A) Comment length
    * B) Frequent small PRs with high pass rate and low rework
    * C) LOC growth
    * D) Number of files touched
    * **Answer: B.** That correlates with healthy, testable slices. Others are poor proxies.

55. The **Explainer prompt** should:
    * A) Just restate code
    * B) Summarize intent, diffs, risks, next steps in ≤8 bullets
    * C) Change public API
    * D) Increase temperature
    * **Answer: B.** It clarifies impact and risk. Others misapply.

56. **Guardrails** add value by:
    * A) Restricting output to shape/length/policy, enabling retries on violation
    * B) Replacing tests
    * C) Removing evals
    * D) Increasing GPU usage
    * **Answer: A.** They constrain outputs and enable recovery. Others false.

57. **Contract stability** across models is verified by:
    * A) Reading docs
    * B) Running the same contract tests & error envelopes after substitution
    * C) Asking a teammate
    * D) Skipping CI for speed
    * **Answer: B.** Execute contracts to prove stability. Others are anecdotal.

58. A **risk triage** lens for review prioritizes:
    * A) UI polish first
    * B) Change surface × component criticality, with rollback noted
    * C) Commit message puns
    * D) Removing CI steps
    * **Answer: B.** Focus on impact and reversibility. Others distract.

59. The **governed definition** of GPS Engineering is:
    * A) Prompting technique only
    * B) Governed Prompt Software Engineering unifying specs, prompts, tests, evals, decisions, PR gates
    * C) A Dockerfile recipe
    * D) A single IDE feature
    * **Answer: B.** It’s a method combining these artifacts and gates. Others narrow it.

60. The shift from **PDD → GPS** is best described as:
    * A) From prompts to pure coding
    * B) From speed alone to auditable velocity with formal contracts & evaluation
    * C) From tests to drawings
    * D) From specs to vibes
    * **Answer: B.** GPS adds governance and traceability to PDD speed. Others are regressions.

---

