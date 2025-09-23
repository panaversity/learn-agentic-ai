# Quiz 1

Here’s a **60-question MCQ quiz** that spans everything we covered: SDD, PDD, TDD, EDD, ADR, PHR, PR gates, GPS Engineering, Cursor vs VS Code + Codex, OpenAI Agents SDK, SSE, error handling, CI, metrics, roadmap, repo layout, and more. Each item has 4 options with varied lengths. The **answer key** is in the file answer_key.md

---

### Multiple-Choice Questions

1. In GPS Engineering, what primarily turns intent into an executable contract?
   A) ADRs
   B) Unit tests
   C) Prompt history
   D) Commit messages

2. Which pairing best describes GPS Engineering in one line?
   A) Specs plus prompts without testing
   B) Prompts governed by specs, tests, evals, decisions, PRs
   C) Linting plus CI gates only
   D) IDE automation without review

3. Which artifact captures **why** a decision was made?
   A) PHR
   B) ADR
   C) CI log
   D) README

4. The **Spec-Compliance** checkbox in PRs mainly enforces:
   A) Coding style
   B) Contract adherence
   C) Docker image size
   D) Commit naming

5. In the PDD loop, which ordered trio is correct?
   A) Green → Red → Refactor
   B) Architect → Red → Green
   C) Red → Refactor → Green
   D) Explain → Red → Green

6. Which belongs to **EDD**?
   A) promptfoo behavior suites
   B) Uvicorn reload flag
   C) .env.sample variables
   D) Ruff configuration

7. “No green, no merge” refers to:
   A) Lint warnings
   B) Passing tests and gates
   C) Branch protection removal
   D) Local dev only

8. A thin SDD spec for `/chat` should primarily include:
   A) Full code samples
   B) Behavior, constraints, acceptance criteria
   C) Cloud billing charts
   D) UI mockups only

9. In our service, the 400 error for missing `user_message` must be:
   A) `{"detail": "MISSING_USER_MESSAGE"}`
   B) `{"error_code": "MISSING_USER_MESSAGE"}`
   C) `{"error": {"code": "MISSING_USER_MESSAGE"}}`
   D) `{"status": "MISSING_USER_MESSAGE"}`

10. For SSE, the correct end-of-stream marker is:
    A) `data:[EOF]\n`
    B) `data:[DONE]\n\n`
    C) `event: done\n\n`
    D) `data:complete\n`

11. Cursor is strongest at:
    A) Autonomous multi-repo refactors without review
    B) Inline tab completion and predictive multi-file edits
    C) License scanning
    D) Build artifact signing

12. VS Code + GPT-5 Codex shines for:
    A) Animated UML export
    B) Repo-wide agentic tasks and PR prep
    C) Container runtime tweaks
    D) GPU provisioning

13. Which **tooling** belongs to the OpenAI Agents SDK use in our design?
    A) Agents, Tools, Sessions, Handoffs, Guardrails
    B) Lambdas, Layers, Gateways, Groups
    C) Controllers, Sagas, Repositories, DTOs
    D) Pods, Services, Ingress, CRDs

14. Guardrails in our chatbot ensure:
    A) Model version pinning only
    B) Output shape and length constraints
    C) Horizontal autoscaling
    D) URL routing rules

15. In TDD, “Red” means:
    A) Failing tests introduced first
    B) All tests skipped
    C) Refactor step finished
    D) CI rerun needed

16. The **PHR** primarily stores:
    A) Docker layers
    B) Exact prompts, scope, acceptance, outcome
    C) Binary logs
    D) GPU configs

17. For `/chat` SSE, the **response header** must include:
    A) `Content-Type: application/json`
    B) `Accept: text/event-stream`
    C) `Content-Type: text/event-stream`
    D) `Cache-Control: immutable`

18. The PR template’s governance role is to:
    A) Replace unit tests
    B) Gate merges with traceability and checks
    C) Auto-deploy to production
    D) Pin dependencies

19. Our repo uses **uv** to:
    A) Serve static files
    B) Manage Python env and dependencies
    C) Sign commits
    D) Render docs

20. “Baby steps” in PDD means:
    A) Large diffs after week-long cycles
    B) Minimal, test-scoped changes
    C) Refactor without tests
    D) Commit squashing only

21. ADR-0002 recorded the choice of:
    A) ORM frameworks
    B) Streaming protocol (SSE vs WS vs long-poll)
    C) Database engine
    D) Frontend theme

22. A **traceability** chain in GPS links:
    A) Spec → PHR → ADR → PR → CI
    B) README → Dockerfile → Makefile
    C) Linter → Formatter → Type checker
    D) Secrets → Key vault → Token

23. The ChatReply model includes:
    A) `text`, `used_tool?`, `handoff`
    B) `content`, `tooling`, `state`
    C) `body`, `selected_tool`, `route`
    D) `message`, `tool`, `stage`

24. EDD smoke on PRs is for:
    A) Load testing
    B) Behavior drift detection
    C) GPG verification
    D) Traffic shaping

25. The **best place** for SDD specs is:
    A) `docs/specs/`
    B) `app/guards/`
    C) `tests/`
    D) `evals/datasets/`

26. For secrets, the rule is:
    A) Inline in code for speed
    B) Stored only in README
    C) In `.env` with `.env.sample`
    D) In git submodules

27. A correct SSE event line is:
    A) `data:<token>\n\n`
    B) `token:<data>\n`
    C) `emit:token\n\n`
    D) `line token\n`

28. “Smallest change to green” discourages:
    A) Over-refactoring before tests pass
    B) Any unit tests
    C) Any CI usage
    D) Prompt capture

29. Cursor “Rules for AI” should encode:
    A) Editor font size
    B) SDD×PDD×TDD×EDD guardrails
    C) GPU driver versions
    D) Branch naming regex

30. In the dual setup, **switching tools** is easiest because:
    A) Both use the same license server
    B) Git-synced repo and shared artifacts
    C) They share local caches
    D) Identical UI skins

31. The **400** error envelope shape is validated by:
    A) Docker entrypoint
    B) Contract tests
    C) Mermaid diagrams
    D) Lint rules

32. Which metric is a GPS KPI?
    A) Pixels per chart
    B) Lead time to change
    C) API spelling count
    D) IDE open time

33. “No green, no merge” typically sits between:
    A) Build and Publish
    B) Tests/EDD and Build
    C) Lint and Publish
    D) ADR and PR

34. Prompt library reuse helps by:
    A) Replacing specs entirely
    B) Standardizing high-leverage prompts
    C) Eliminating tests
    D) Avoiding reviews

35. The repo map places **SSE helpers** in:
    A) `app/streaming.py`
    B) `docs/diagrams/`
    C) `.githooks/`
    D) `evals/behavior/`

36. An example EDD check we used:
    A) Tool-first math/time policy
    B) Container UID mapping
    C) IPv6 routing
    D) TLS renegotiation

37. ADRs typically include:
    A) Decision, context, options, consequences
    B) Sprint velocity charts only
    C) Unit test reports
    D) Binary artifacts

38. PHRs should be kept:
    A) In ephemeral chat only
    B) In `docs/prompts/` with IDs
    C) Inside compiled wheels
    D) In CI caches

39. A minimal `/healthz` endpoint primarily:
    A) Returns service config
    B) Streams tokens
    C) Returns `{ "status": "ok" }`
    D) Executes tools

40. A correct JSON ChatReply example is:
    A) `{"text":"hi","handoff":false,"used_tool":null}`
    B) `{"message":"hi","tool":"x","route":"y"}`
    C) `{"content":"hi","meta":{}}`
    D) `{"say":"hi","flag":false}`

41. Which belongs in **CI** for our starter?
    A) Ruff + Pytest (+ optional EDD)
    B) GPU kernel updates
    C) DB schema migrations
    D) UI snapshot diffs only

42. Nano Banana diagrams help mainly with:
    A) Executable code generation
    B) Team visualization and onboarding
    C) Binary compression
    D) Token caching

43. SSE is preferred over WS for v1 because:
    A) Full-duplex messaging is required
    B) Simplicity and easy proxying
    C) Needs binary frames
    D) Mandatory backpressure

44. Which acceptance test ensures error contract?
    A) `test_healthz_ok`
    B) `test_chat_missing_user_message_returns_400_top_level_error_code`
    C) `test_streaming_emits_json`
    D) `test_readme_renders`

45. “Tool-first” means the agent should:
    A) Guess times and math
    B) Use tools for math/time requests
    C) Avoid any function calls
    D) Disable handoffs

46. The **Spec → PHR → ADR → PR → CI** chain enables:
    A) Faster GPU clocks
    B) Auditable change history
    C) Static linking
    D) Theme switching

47. The `Accept: text/event-stream` header is sent by:
    A) Server
    B) Client request
    C) CI workflow
    D) Docker daemon

48. The SSE `Content-Type` is set by:
    A) Client only
    B) Server response
    C) Promptfoo
    D) Git hooks

49. In GPS, refactoring should occur:
    A) Before tests exist
    B) After green, keeping tests passing
    C) Without any tests
    D) Only in main branch

50. A **thin** SDD spec avoids:
    A) Behavior and constraints
    B) Over-detailed implementation
    C) Acceptance criteria
    D) Contract examples

51. The starter’s error helper lives in:
    A) `app/http_errors.py`
    B) `docs/adr/`
    C) `.github/workflows/`
    D) `evals/behavior/`

52. The PR template adds which governance item?
    A) GPU utilization table
    B) **Spec-Compliance** checkbox
    C) Billing approvals
    D) Editor themes

53. Which is true about PHRs?
    A) Optional for governance
    B) One per repo only
    C) One per slice or step with IDs
    D) Stored in Docker registry

54. An example of **progressive slicing** we used is:
    A) SSE first, then JSON
    B) JSON `/chat`, then SSE streaming
    C) Docker before specs
    D) EDD before unit tests always

55. In dual IDE use, Codex is better for:
    A) Inline tab completions
    B) Parallel agentic tasks and PR prep
    C) Mermaid export
    D) Managing .env

56. The **EDD smoke** suite runs:
    A) Only on main branch
    B) On PRs to catch behavior drift
    C) On client browsers
    D) After deployment only

57. A correct “done” condition for a slice is:
    A) Explainer written only
    B) Spec acceptance tests + unit tests green
    C) Diagram exported
    D) Docker image built

58. “No secrets in prompts” is enforced by:
    A) Editor theme
    B) Team policy + PR checks
    C) Unit test fixture
    D) Docker healthcheck

59. The minimal SSE tokenizer used in the green zip:
    A) Streams fixed words like “Hello”, “ from”, “ SSE”
    B) Performs subword BPE
    C) Requires GPU
    D) Uses external API

60. A key migration milestone within 90 days is:
    A) Remove all tests
    B) Publish internal rules bundles and prompt libraries
    C) Delete ADRs
    D) Disable CI

---


