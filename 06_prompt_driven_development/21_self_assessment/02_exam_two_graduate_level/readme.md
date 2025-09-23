# Quiz 2

Here’s a **second, graduate-level 60-question MCQ quiz** covering the full session (GPS Engineering: SDD × PDD × TDD × EDD × ADR × PHR × PR; OpenAI Agents SDK; SSE; dual IDE setup; CI/CD; metrics; governance). **Answer key is in the file answer_key.md**

---

## Multiple-Choice Questions (Graduate Level)

1. In GPS Engineering, what is the **primary mechanism** to prevent prompt drift across iterations?
   A) Larger model context windows
   B) SDD specs with acceptance criteria mapped to tests and evals
   C) Frequent refactors without tests
   D) High-entropy prompts with creative temperature

2. Which statement best captures the **contractual difference** between TDD and EDD?
   A) TDD checks model tokens; EDD checks HTTP headers
   B) TDD verifies code behavior; EDD verifies model behaviors against scenario rubrics
   C) TDD only linting; EDD only formatting
   D) TDD validates CI; EDD validates Docker

3. An ADR choosing **SSE over WebSocket** in v1 is mostly justified by:
   A) Full-duplex need and binary frames
   B) Simpler infra and easy proxy compatibility for token streams
   C) Mandatory client push channels
   D) TLS renegotiation requirements

4. For `/chat`, the spec requires a top-level 400 envelope. Which property enforces **client simplicity** most?
   A) Nested error objects
   B) Top-level `{"error_code": "..."}`
   C) Free-form error messages
   D) HTML error bodies

5. Which describes **PHR’s** governance role most precisely?
   A) Build cache
   B) Immutable record of prompts, scope, acceptance, and outcome per slice
   C) Dependency lockfile
   D) Mypy configuration

6. In a PR, **Spec-Compliance** should be checked when:
   A) Linter passes regardless of behavior
   B) Acceptance criteria in spec are demonstrably satisfied by tests/evals
   C) The README compiles
   D) The Docker image is minimal size

7. A **graduate-level risk** of vibe coding in multi-agent systems is:
   A) Too many comments
   B) Unbounded architectural drift under ambiguous prompts
   C) Excessive type hints
   D) Too few environment variables

8. What is the **most defensible order** for a new slice in GPS Engineering?
   A) Green → Red → Explain → Merge
   B) Architect → Red → Green → Refactor → Explainer → PR
   C) PR → Red → Green → Architect
   D) Refactor → Architect → Merge

9. Which **traceability edge** is essential for audits?
   A) PHR → PR linkage with exact prompt IDs
   B) Dockerfile → PR linkage
   C) Linter → ADR linkage
   D) Mermaid → CI linkage

10. Why is **offline testing** emphasized in TDD for LLM-backed services?
    A) Faster GPUs locally
    B) Determinism and stability without network/model variance
    C) Easier to leak secrets
    D) Improves container size

11. A subtle pitfall when writing specs for LLM systems is:
    A) Over-specifying UI colors
    B) Ambiguous behavioral constraints that models interpret inconsistently
    C) Too many acceptance tests
    D) Too short ADRs

12. Which OpenAI Agents SDK feature most directly supports **separation of concerns**?
    A) Sessions only
    B) Handoffs to specialized agents
    C) Single monolithic tool
    D) Disabling guardrails

13. A test asserts SSE emits `data:[DONE]`. What **failure mode** does this detect?
    A) Wrong HTTP verb
    B) Early stream termination without a terminator
    C) Linter failure
    D) Missing .env file

14. The **tool-first policy** is primarily designed to:
    A) Reduce Pydantic imports
    B) Force math/time tasks into deterministic functions before generation
    C) Increase token counts for creativity
    D) Disable handoffs entirely

15. In dual-environment practice, when should **Codex** be preferred over Cursor?
    A) Inline micro-edits
    B) Wide, agentic, repo-scale transformations and PR preparation
    C) Changing theme settings
    D) Quick tab completion mid-function

16. A sophisticated **EDD smoke** test for scope discipline should:
    A) Evaluate image size
    B) Penalize hallucinated fields or extraneous tools not in spec
    C) Ensure CI runs on ARM
    D) Sort imports

17. What is a **graduate-level criterion** indicating an ADR is warranted?
    A) Any file rename
    B) Choice impacting protocol, data contract, or reliability guarantees
    C) Comment typo fix
    D) Changing a docstring

18. The **smallest change to green** principle primarily reduces:
    A) PR frequency
    B) Confounding variables during failure diagnosis
    C) CPU usage
    D) Docs length

19. In the repo, placing **SSE helpers** in a separate module improves:
    A) Coupling
    B) Cohesion and testability of streaming logic
    C) Docker layer caching only
    D) Prompt tokenization

20. A **well-formed spec** for `/chat` would **not** include:
    A) Request/response shape
    B) Error envelopes and codes
    C) Hand-written code samples for all branches
    D) Limits and acceptance checks

21. For secrets, the most robust operational control is:
    A) Checking API keys into git
    B) Using `.env`/env vars and rotating keys with zero-downtime
    C) Putting secrets in README
    D) Printing them to logs

22. When adopting GPS across teams, which metric best indicates **governance maturity**?
    A) Average PR size decreasing while pass rates hold
    B) Higher token counts in prompts
    C) More Docker layers
    D) More branches per developer

23. If **SSE** is chosen for v1, a **future ADR** might most likely reconsider:
    A) Monorepo vs polyrepo
    B) Upgrade to WebSocket for bidirectional tool UIs
    C) JSON schema version
    D) README license badge

24. A **PHR ID convention** helps with:
    A) Git LFS usage
    B) Deterministic referencing in PRs, CI logs, and retrospectives
    C) GPU pinning
    D) Docker digest shortening

25. In EDD, a behavior suite for **tool-first math** should score:
    A) Higher when the model guesses mental arithmetic
    B) Lower when math is not solved via the calculator tool
    C) Higher when long narratives are produced
    D) Neutral regardless of method

26. A **graduate-level anti-pattern** for PDD is:
    A) Architect prompts that specify acceptance tests
    B) Combining multiple features in one Green prompt creating large diffs
    C) Explainer summaries under 8 bullets
    D) Red tests isolated from network

27. Which **CI gate** increases reliability most for LLM apps?
    A) Single linter
    B) Contract tests + EDD smoke + lint before build
    C) Build first, test later
    D) Release before CI

28. What’s the **strongest reason** to keep tests offline by default even with mocks of the SDK?
    A) Model providers mandate it
    B) Prevent nondeterminism from model changes and rate limits
    C) Improves typing speed
    D) Enables larger logs

29. For `/chat`, why is `Content-Type: text/event-stream` essential?
    A) Enables SSE framing semantics for chunk handling by clients
    B) Reduces latency via HTTP/3
    C) Prevents DNS caching
    D) Triggers JSON parsing

30. A **governed refactor** should be executed:
    A) Before tests exist
    B) After Green, with tests unchanged and still passing
    C) Only on main
    D) Only if CI is disabled

31. A rigorous spec often improves **model controllability** by:
    A) Increasing inference temperature
    B) Tightening output structure and constraints
    C) Removing guardrails
    D) Disabling retries

32. “No green, no merge” impacts org culture by:
    A) Encouraging speculative merges
    B) Lowering the social cost of requesting changes early
    C) Eliminating reviews
    D) Making tests optional

33. In the OpenAI Agents SDK, **handoff** is appropriate when:
    A) Any answer is short
    B) Intent requires specialized skills the primary agent shouldn’t emulate
    C) The model wants fewer tokens
    D) The request is static text

34. An EDD rubric for **scope discipline** should penalize:
    A) Returning exactly the requested fields
    B) Adding unrequested fields or formats
    C) Matching the spec
    D) Using structured outputs

35. Cursor “Rules for AI” should **not** include:
    A) PDD loop and constraints
    B) Security posture and secret handling
    C) Model-agnosticism
    D) Personal editor theme color

36. A mature GPS rollout often introduces **which** artifact library?
    A) Prompt libraries (architect, red, green, refactor, explainer) with IDs
    B) Binary wheels for all prompts
    C) Only Mermaid exports
    D) Single monolithic ADR

37. A reason to store **PHRs** in-repo rather than in chat logs is:
    A) Easier emoji reactions
    B) Versioned, reviewable, linkable evidence for each code delta
    C) Lower token costs
    D) Better Docker layers

38. For `/chat`, the most **defensible** contract decision is to:
    A) Place error code under a nested `detail` field
    B) Use top-level `error_code` for minimal parsing
    C) Return HTML
    D) Encode errors as CSV

39. A **graduate design smell** in SSE handling is:
    A) Using a generator for event lines
    B) Missing final sentinel `data:[DONE]`
    C) Testing with mocks
    D) Returning 200

40. The **dual IDE** recommendation yields productivity because:
    A) They share the same proprietary engine
    B) Each environment optimizes for a different cognitive mode (agentic vs interactive)
    C) Only one supports Python
    D) One eliminates PRs

41. A nuanced reason to adopt **uv** is:
    A) It compiles C extensions
    B) Deterministic, fast dependency resolution suited for CI reproducibility
    C) It replaces Docker
    D) It runs browsers

42. A **graduate governance** signal in PRs is:
    A) Screenshots only
    B) Linkage to Spec, PHRs, ADRs and passing CI/EDD annotations
    C) GIFs of terminals
    D) Fonts configured in editor

43. An ADR’s **Consequences** section should cover:
    A) Emoji usage
    B) Trade-offs, follow-ups, and migration triggers
    C) Screenshot galleries
    D) Random links

44. The **best** reason to gate merges on EDD smoke is:
    A) It measures coverage
    B) It catches behavioral drift that unit tests may miss in LLM flows
    C) It speeds Docker builds
    D) It simplifies secrets

45. A solid acceptance test for `/chat` JSON path asserts:
    A) The README exists
    B) Response matches `ChatReply` schema and field presence
    C) The server uptime
    D) Docker layer count

46. In Prompt-Driven Development, **Architect prompts** should primarily:
    A) Demand code immediately
    B) Express micro-specs, constraints, acceptance checks, and scope
    C) Change the Docker base image
    D) Alter CI runners

47. A rigorous **Refactor prompt** must:
    A) Change public contracts
    B) Keep public behavior and tests green while improving internals
    C) Add new dependencies
    D) Delete tests

48. When should a new **ADR** be rejected?
    A) If it repeats an existing accepted decision without new context
    B) If it mentions options
    C) If it cites trade-offs
    D) If it lists consequences

49. “Auditable velocity” in GPS means:
    A) Raw speed without checks
    B) Fast iteration with recorded specs/prompts/decisions and green gates
    C) Skipping PHRs
    D) Merging on red

50. A subtle way to **overfit** PDD to a single model is to:
    A) Keep specs model-agnostic
    B) Bake model-specific stopwords into contracts
    C) Use structured outputs
    D) Use tools for math

51. A **graduate-level** CI smell in LLM apps is:
    A) Unit tests only
    B) Missing behavior evals while shipping prompt changes
    C) Too many small PRs
    D) Using ruff

52. A metric indicating **healthy slice sizing** is:
    A) Average PR > 2,000 lines
    B) Frequent small PRs with high pass rates and low rework
    C) One monthly PR that changes everything
    D) Constant hotfixes

53. For **SSE buffering** behind proxies, a mitigation is to:
    A) Increase event chunk frequency and disable compression if needed
    B) Convert to HTML
    C) Only send `[DONE]`
    D) Use binary frames

54. A **graduate** reason to prefer top-level `error_code` over nested objects is:
    A) JSON aesthetics
    B) Parsing cost and failure-mode isolation for clients in multiple languages
    C) Easier to add emojis
    D) Faster Docker builds

55. A resilient **prompt library** should be:
    A) Stored in ephemeral docs
    B) Versioned, ID’d, and mapped to specs/tests
    C) Encrypted and hidden
    D) Written as screenshots

56. A defensible **go-live checklist** item for GPS is:
    A) Ensure ADR links in PR, CI green, EDD smoke passing, and secrets rotated
    B) Merge on red to save time
    C) Delete specs after deploy
    D) Skip behavior tests

57. A **graduate** streaming test might additionally assert:
    A) Line endings only
    B) Correct headers, at least one data event, and a termination sentinel with no trailing junk
    C) Dockerfile presence
    D) README size

58. Handoffs should log **handoff\_reason** to:
    A) Amuse reviewers
    B) Enable tracing of agent routing decisions for debuggability and governance
    C) Reduce tokens
    D) Warm caches

59. A nuanced **metrics pitfall** is to:
    A) Track lead time and change-failure rate together
    B) Optimize for coverage alone without scenario quality
    C) Use ADR density as a proxy for decisions
    D) Track MTTR

60. A 90-day **institutionalization** milestone for GPS is to:
    A) Remove CI for speed
    B) Publish rules bundles, prompt libraries, and dashboards org-wide
    C) Centralize all prompts in private chats
    D) Skip PR reviews

---

