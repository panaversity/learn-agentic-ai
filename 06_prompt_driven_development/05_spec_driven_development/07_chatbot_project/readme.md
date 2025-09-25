# Step 7: Capstone – SDD Chatbot Project

**Goal:** demonstrate end-to-end mastery by shipping a working chatbot experience using the full SDD workflow.

## Inputs

- Completed Steps 1–6 artifacts (constitution, spec, plan, tasks)
- A scoped chatbot objective (e.g., `/chat` endpoint + optional SSE streaming)
- Evaluation harness or contract tests from earlier steps

## Actions

1. Re-run the SDD loop for the capstone feature set:
	- Update constitution if the chatbot introduces new guardrails.
	- Draft/refine the chatbot spec (conversations, error handling, guardrails) and run `/clarify` until no open questions remain.
	- Produce a technical plan covering architecture, tooling, and eval strategy referencing the resolved clarifications.
	- Break the work into implementable tasks (API contracts, tool integration, streaming, evaluations) and run `/analyze` to confirm coverage.
2. Execute tasks sequentially: lean on `/implement` for automated execution or drive the PDD loop manually (RED → GREEN → REFACTOR → EXPLAIN).
3. Capture supporting artifacts:
	- ADRs for protocol/tooling choices (e.g., SSE vs WebSocket, evaluation tooling).
	- Prompt templates for slash commands or agent workflows.
4. Run full validation:
	- Unit/contract tests
	- Evaluation suites (promptfoo, smoke tests)
	- Manual QA for conversational UX and edge cases
5. Prepare a final PR or release note summarizing outcomes, metrics, and follow-up work.

## Deliverables

- Working chatbot implementation in your repo
- Updated spec, plan, tasks marked as “Completed” with references to commits/PRs
- ADRs, changelog entries, and documentation updates reflecting the shipment
- Lessons learned feeding into continuous practices (see Steps 8–10)

## Quality Gates ✅

- CI pipeline (lint, tests, evaluations) passes without manual intervention
- PR reviewers confirm traceability to spec sections and constitution rules
- Post-release checklist completed (monitoring, rollback plan, known issues)

## Common Pitfalls

- Attempting too large a scope for the capstone; start with a single endpoint and iterate
- Skipping evaluation harnesses—chatbots need behavior tests, not just unit tests
- Neglecting to document learnings and follow-up tasks after the project wraps

## References

- Spec Kit repo: https://github.com/github/spec-kit
- Microsoft Dev Blog: https://developer.microsoft.com/blog/spec-driven-development-spec-kit
