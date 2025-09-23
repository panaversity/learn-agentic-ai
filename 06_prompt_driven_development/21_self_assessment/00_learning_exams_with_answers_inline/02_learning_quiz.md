# Learning Quiz 2 with Inline Answers

We’ve built a 60-question, graduate-level MCQ quiz that emphasizes concepts (not trivia) from our “Prompt-Driven Development” materials (PHRs, ADRs, PRs, Cursor workflow, TDD/SDD, prompt-driven chatbots, diagram prompts, governance, evals, safety, and the “Prompt Architect” mindset). 

---

## Prompt-Driven Development (PDD) & Prompt Architecting

1. PDD’s primary shift in software practice is best described as:

* A) Replacing design with rapid coding
* B) Moving from code-first to prompt-first workflows that are versioned, verified, and reviewed
* C) Eliminating tests in favor of interactive prototyping
* D) Outsourcing specs to external vendors
  **Answer: B**

2. In the AI-compiler analogy, the “Prompt Architect” role most closely aligns with:

* A) A UI designer creating mockups
* B) A compiler engineer controlling register allocation
* C) A systems architect specifying intent, interfaces, constraints, and acceptance criteria for AI execution
* D) A release manager issuing version tags
  **Answer: C**

3. Which outcome is *not* a core goal of PDD governance?

* A) Reproducibility of AI-assisted changes
* B) Traceable intent behind changes
* C) Stronger review signals on non-deterministic edits
* D) Maximizing model temperature for creativity in production
  **Answer: D**

4. A healthy PDD loop is typically:

* A) Ideate → ship → refactor later if needed
* B) Prompt → verify → record → review → merge
* C) Code → comment → commit → push
* D) Prototype → demo → freeze
  **Answer: B**

5. “Vibe coding” is an anti-pattern because it:

* A) Produces too many unit tests
* B) Hides decision context, reduces reproducibility, and bypasses verification
* C) Requires complex build systems
* D) Uses too many small prompts
  **Answer: B**

6. Prompt decomposition is most useful when:

* A) You want a single mega-prompt for every task
* B) The task mixes policy, tooling, and code-gen concerns that benefit from modular prompts
* C) You want to minimize version control noise
* D) Determinism is guaranteed by the model
  **Answer: B**

7. A good “system” prompt in PDD primarily:

* A) Changes API keys dynamically
* B) Establishes role, constraints, safety posture, and evaluation norms across turns
* C) Forces deterministic decoding
* D) Reduces token usage only
  **Answer: B**

8. Model portability in PDD is improved by:

* A) Binding prompts to a single provider’s features
* B) Using provider-neutral prompt contracts and keeping tool interfaces stable
* C) Hard-coding sampling parameters in code
* D) Mixing multiple system prompts at random
  **Answer: B**

9. Context-window stewardship is mainly about:

* A) Increasing temperature when the window is full
* B) Prioritizing high-signal artifacts (specs, contracts, tests) while pruning noisy history
* C) Always truncating the newest content
* D) Turning off function-calling
  **Answer: B**

10. An effective “prompt contract” is:

* A) A non-versioned comment block in code
* B) A stable, testable interface describing inputs, outputs, tools, and acceptance checks
* C) A private note from the PM
* D) A temporary scratchpad
  **Answer: B**

---

## Prompt History Records (PHRs) & Architecture Decision Records (ADRs)

11. PHRs exist primarily to:

* A) Store release notes
* B) Capture the exact prompts, intent, and verification for reproducible AI changes
* C) Replace unit tests
* D) Track cloud costs
  **Answer: B**

12. The most important difference between PHRs and ADRs:

* A) PHRs are legal documents; ADRs are not
* B) PHRs record interactions and edits; ADRs record architectural decisions, context, and consequences
* C) ADRs are private; PHRs are public
* D) ADRs are about UI; PHRs are about backend
  **Answer: B**

13. A strong PHR typically includes:

* A) Only the final diff
* B) The prompt(s), rationale, change summary, verification steps, and links to tests/PRs
* C) A marketing brief
* D) CI runtime logs only
  **Answer: B**

14. ADR “consequences” are valuable because they:

* A) Record the refactor backlog for auditors
* B) Make the decision reversible
* C) Surface trade-offs, risks, and expected impact to guide future decisions
* D) Reduce repository size
  **Answer: C**

15. When a prompt change drives a design shift, you should:

* A) Update PHR only
* B) Update ADR with decision context and leave PHR empty
* C) Update both: ADR for the decision, PHR for the prompt interaction and verification
* D) Do neither until after release
  **Answer: C**

16. A minimal ADR usually contains:

* A) Context, decision, alternatives, consequences
* B) Roadmap and budget
* C) Test suite listings
* D) Deployment manifests
  **Answer: A**

17. PHRs help PR reviewers by:

* A) Hiding exploratory prompts
* B) Summarizing intent vs. diff and how correctness was established
* C) Replacing code comments
* D) Compressing binaries
  **Answer: B**

18. The best place to link a PHR is:

* A) In the commit message and PR description
* B) In a private chat
* C) Inside compiled artifacts
* D) Only in the README
  **Answer: A**

---

## Pull Requests (PRs), Reviews, and CI Gates

19. In PDD, PR templates should emphasize:

* A) Colors and fonts
* B) Intent, prompt references, acceptance checks, and regression tests
* C) Branch naming conventions only
* D) Only screenshots
  **Answer: B**

20. A useful PR reviewer mindset for AI changes is:

* A) “Does the diff look clever?”
* B) “Is intent clear and verified? Are specs/tests sufficient for future maintainers?”
* C) “Is the model brand the same?”
* D) “Is the code shorter?”
  **Answer: B**

21. A CI gate uniquely important for AI-assisted changes:

* A) Linting only
* B) Static type checks only
* C) Replay of PHR prompts and running acceptance tests to verify deterministically constrained behavior
* D) Code coverage thresholds only
  **Answer: C**

22. For non-deterministic generations, a common mitigation is:

* A) Disable tests
* B) Fix seeds or lower temperature; constrain with specs/tests and validate semantic equivalence
* C) Ignore failures and re-run until green
* D) Increase context length automatically
  **Answer: B**

23. Shadow deployment of a new AI path means:

* A) Turning off old paths
* B) Running the new path in parallel, capturing metrics without user impact
* C) Manual testing only
* D) Replacing the data store
  **Answer: B**

24. A rollback plan in PDD typically relies on:

* A) Feature flags, prompt version pins, and immutable artifact promotion
* B) Force-pushing to main
* C) Deleting ADRs
* D) Hot-fixing in production only
  **Answer: A**

---

## TDD / SDD / Specs and Tests

25. The TDD core loop is:

* A) Plan → Prototype → Present
* B) Red → Green → Refactor
* C) Build → Break → Fix
* D) Ship → Learn → Repeat
  **Answer: B**

26. TDD best supports AI-assisted coding when tests:

* A) Are written after generation
* B) Are small, isolated, and executable quickly to anchor each incremental behavior
* C) Are replaced by demos
* D) Are randomized
  **Answer: B**

27. In SDD (Spec-Driven Development), the spec functions as:

* A) Marketing collateral
* B) The acceptance contract driving generation, tooling, and tests
* C) A log of CI runs
* D) A diagram only
  **Answer: B**

28. “Red tests bundle” usage primarily ensures:

* A) Higher latency
* B) There is a failing spec-aligned test suite before generation begins
* C) The linter runs first
* D) Fewer PR comments
  **Answer: B**

29. Unit vs. integration vs. end-to-end tests in PDD:

* A) Are unnecessary with LLMs
* B) Provide layered confidence: small correctness, subsystem interactions, and user-visible flows
* C) Should all be end-to-end only
* D) Replace ADRs
  **Answer: B**

30. “Small steps” in TDD matter because they:

* A) Reduce token usage only
* B) Make failures local, support quick fixes, and preserve momentum with guardrails
* C) Increase PR size intentionally
* D) Delay learning
  **Answer: B**

31. Given-When-Then scenarios are most directly tied to:

* A) Build scripting
* B) Acceptance criteria in BDD-style specs
* C) Vendor contracts
* D) Prompt caching
  **Answer: B**

32. A spec is “good” when it:

* A) Is verbose and ambiguous
* B) Is minimal, testable, unambiguous about inputs/outputs/constraints
* C) Contains UI screenshots only
* D) Lists future ideas
  **Answer: B**

---

## Cursor-centric Workflow & Prompt Hygiene

33. A practical Cursor setup for PDD emphasizes:

* A) Multiple unrelated workspaces at once
* B) Project scripts (make/uv), tests wired to hotkeys, model routing, and git integration
* C) Disabling git
* D) Editing JSON by hand only
  **Answer: B**

34. Cursor “rules” in a PDD context usually include:

* A) Allowing AI edits without tests
* B) Demanding PHR capture, running tests after each AI change, and keeping prompts modular
* C) Bypassing reviews for small diffs
* D) Randomizing providers
  **Answer: B**

35. Multi-model routing helps because:

* A) It reduces human oversight
* B) Different tasks (analysis, code-gen, refactor) benefit from models optimized for those modes
* C) It eliminates tests
* D) It locks you into one vendor
  **Answer: B**

36. Prompt hygiene generally *does not* include:

* A) Using clear roles and constraints
* B) Including acceptance checks and example IO
* C) Bundling unrelated tasks into one mega instruction
* D) Versioning prompt artifacts
  **Answer: C**

37. Cursor with tests on a hotkey is valuable because:

* A) It hides failures
* B) It makes the “red→green→refactor” cadence quick and habitual
* C) It replaces PHRs
* D) It increases PR size
  **Answer: B**

---

## Prompt-Driven Chatbots & Agents

38. A prompt-driven chatbot architecture typically includes:

* A) LLM core, tool interfaces/actions, retrieval or memory, safety and evaluation layers
* B) Only a front-end
* C) A database and nothing else
* D) Prompts but no persistence
  **Answer: A**

39. RAG vs. fine-tuning in this context:

* A) RAG injects fresh context at inference; fine-tuning changes model weights with curated data
* B) Both modify weights identically
* C) Fine-tuning is always cheaper
* D) RAG requires no indexing
  **Answer: A**

40. Tool-use in agents should be:

* A) Implicit and undocumented
* B) Declarative with explicit schemas, idempotence concerns, and error handling
* C) Avoided in production
* D) Hidden from tests
  **Answer: B**

41. Memory design for agents stresses:

* A) Storing everything forever
* B) Selective retention, summarization, and eviction tied to tasks and privacy constraints
* C) Client-side only
* D) Disabling context updates
  **Answer: B**

42. Safety in an agent pipeline is best enforced:

* A) Only at UI level
* B) With layered pre-filters, system policies, tool constraints, and post-hoc evaluation
* C) By disabling tools
* D) In PR description text only
  **Answer: B**

43. Evaluation of a chatbot should:

* A) Rely solely on subjective demos
* B) Use spec-aligned test sets, golden answers, and rubric-based graders where possible
* C) Avoid regression data
* D) Vary sampling parameters randomly
  **Answer: B**

44. Prompt injection risks are mitigated by:

* A) Blindly following user-provided content
* B) Defining tool call policies, sanitizing inputs, and using allow-lists for actions and domains
* C) Letting the agent “decide later”
* D) Disabling logs
  **Answer: B**

---

## Diagram Prompts & Communication

45. Diagram prompts should emphasize:

* A) Decorative shapes
* B) Clear entities, labeled relationships, constraints, and directionality that map to the architecture
* C) Only color themes
* D) Freehand drawings
  **Answer: B**

46. Using diagrams in PDD chiefly helps with:

* A) Token cost only
* B) Shared mental models across roles (PM, QA, Dev, Sec) and traceability to specs
* C) Replacing tests
* D) Random brainstorming
  **Answer: B**

47. A good diagram prompt for workflow modeling includes:

* A) Only boxes
* B) Explicit states, transitions, guards, and error paths
* C) Fonts and palettes
* D) Marketing slogans
  **Answer: B**

---

## Reproducibility, Metrics, and Operations

48. Reproducibility of AI changes typically requires:

* A) Hard-coding provider IP addresses
* B) Capturing prompts, seeds/params when relevant, data snapshots, and verifications
* C) Removing randomness entirely in all stages
* D) Avoiding PRs
  **Answer: B**

49. Key production metrics for AI features *do not* usually include:

* A) Latency and cost per call
* B) Task success rate and guardrail violation rate
* C) Blue/green parity and drift
* D) Keyboard layout preferences
  **Answer: D**

50. Observability for AI systems benefits from:

* A) Suppressing logs
* B) Structured logs for prompts, tool calls, errors, and evaluation outcomes with PII minimization
* C) Screenshots only
* D) Ad-hoc debug prints in production
  **Answer: B**

51. A practical caching strategy aims to:

* A) Cache every response forever
* B) Balance freshness, security, and determinism; cache safe, stable sub-results behind feature flags
* C) Disable invalidation
* D) Cache only failures
  **Answer: B**

52. Rollout maturity increases when teams:

* A) Merge directly to main
* B) Use feature flags, staged exposure, canaries, and automatic rollback criteria
* C) Disable metrics to reduce noise
* D) Avoid documentation
  **Answer: B**

53. Cost control without quality loss often comes from:

* A) Deeper prompt engineering, tool offloading, prompt chaining, and smaller models where acceptable
* B) Randomly choosing cheaper providers
* C) Cutting tests entirely
* D) Disabling safety layers
  **Answer: A**

---

## Ethics, Privacy, and Risk

54. Data privacy in PDD requires:

* A) Sending everything to third parties for convenience
* B) Minimizing sensitive data in prompts, redaction, differential access, and regionalization as needed
* C) Testing only in production
* D) Turning off encryption
  **Answer: B**

55. An ethical review for an AI feature should confirm:

* A) It is entertaining
* B) It respects user consent, explains limitations, and avoids harmful automation risks
* C) It has the most advanced model
* D) It uses dark patterns to increase engagement
  **Answer: B**

56. Governance alignment means:

* A) Security is a post-merge concern
* B) Safety and compliance are codified in specs, tests, CI gates, and PR policy
* C) Everyone approves manually each time
* D) Ignoring audits
  **Answer: B**

---

## Collaboration & Continuous Improvement

57. Team learning in PDD is amplified by:

* A) Private notes only
* B) Reusable prompt patterns, shared PHR libraries, and post-mortems tied to ADRs
* C) Ad-hoc chat threads
* D) Solo experiments
  **Answer: B**

58. When a generation fails evaluation, the next best step is:

* A) Ship anyway if “looks fine”
* B) Inspect failure traces, refine spec or prompt, and re-run tests with smaller scoped changes
* C) Increase randomness
* D) Remove tests that fail
  **Answer: B**

59. Cross-functional clarity improves when:

* A) Specs are hidden from QA
* B) ADRs, PHRs, diagrams, and PR templates use consistent vocabulary for artifacts and outcomes
* C) Only PMs see the plan
* D) Design is optional
  **Answer: B**

60. A sustainable culture around PDD most relies on:

* A) Heroic debugging and late nights
* B) Disciplined artifacts (ADRs, PHRs), testable specs, small steps, and transparent review rituals
* C) Outsourcing reviews
* D) Eliminating documentation
  **Answer: B**

---