# Step 4: Define Plan (How)

**Goal:** translate the approved spec into technical strategy, respecting constitution rules and organizational constraints.

## Inputs

- Approved `spec.md`
- Constitution clauses and relevant ADRs
- Platform/runtime constraints (cloud provider, languages, compliance requirements)
- Resolved `/clarify` transcript with outstanding questions answered

## Actions

1. Prompt the agent with `/plan` plus the desired stack and guardrails (e.g., `/plan FastAPI + Postgres + pytest + contract tests`).
2. Review the generated `plan.md` and iterate until it covers:
	- Architecture & component diagrams (textual or linked visual)
	- Data contracts (schemas, error envelopes, streaming protocols)
	- Deployment and CI/CD considerations
	- Research & spikes required before implementation
	- Quickstart instructions for new contributors
3. Cross-check plan decisions against the constitution; annotate any intentional deviations with rationale and TODOs.
4. Record open questions and create follow-up tasks (issues or backlog items).
5. Commit the plan when the team agrees it is actionable and bounded.

### Plan Review Checklist

- ✅ Every functional requirement from the spec maps to a technical component
- ✅ Non-functional constraints (performance, security, compliance) have concrete tactics
- ✅ Diagrams or tables clarify component relationships and data flow
- ✅ Tooling (tests, observability, infra) is specified with owners
- ✅ Rollout/rollback strategy and success metrics are defined

## Deliverables

- `plan.md` aligned with the spec and constitution
- List of research spikes or proofs-of-concept (with owners and due dates)
- Updated ADRs if the plan introduces significant architectural choices

## Quality Gates ✅

- Architecture review sign-off (async comments or meeting)
- `/plan` prompt references the exact spec version and all clarifications
- No unresolved “TBD” for critical path items
- Quickstart steps successfully reproduce a local dev environment

## Common Pitfalls

- Allowing the plan to restate the spec without adding technical detail
- Introducing new scope not present in the spec
- Forgetting operational readiness (monitoring, alerting, SLOs)

## References

- GitHub blog overview: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
