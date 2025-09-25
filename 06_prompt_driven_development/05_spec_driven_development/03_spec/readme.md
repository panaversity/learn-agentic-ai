# Step 3: Specify & Clarify (What & Why)

**Goal:** articulate user value, behaviors, and acceptance checks before any technical commitments.

## Inputs

- Constitution clauses that apply to the feature
- Initial product intent brief or user story
- `/specify` slash command available in your agent

## Actions

1. Trigger the agent: `/specify <feature name + intent>` (e.g., `/specify tip calculator for restaurant staff`).
2. Immediately follow up with `/clarify` to surface ambiguities and underspecified areas; answer or assign every question before continuing.
3. Let the agent draft `spec.md`, then perform a human review:
	- Resolve all `TODO`/`[NEEDS CLARIFICATION]` markers immediately.
	- Tighten scope by adding explicit non-goals and success metrics.
	- Ensure the spec references relevant constitution clauses.
4. Add acceptance tests (Given/When/Then or contract examples) for every major scenario.
5. Capture risks, open questions, and required follow-up research in a dedicated section.
6. Version the spec (`Status: Draft`, `Version: 0.1`) and commit it before moving to planning.

### Spec Review Checklist

- ✅ Problem statement explains who benefits and why
- ✅ User journeys / flows describe the expected experience end-to-end
- ✅ Acceptance criteria are concrete, measurable, and testable
- ✅ Non-goals prevent accidental scope creep
- ✅ Dependencies, risks, and stakeholders are documented

## Deliverables

- `spec.md` in your workspace with reviewed content
- Backlog of clarifications or follow-up tasks captured separately (e.g., `/tasks backlog` or issue tracker)

## Quality Gates ✅

- Team sign-off (async review or short design-review meeting)
- `/clarify` output resolved with no unanswered prompts
- All acceptance criteria map to future tests or evaluation harnesses
- Spec links back to constitution clauses and any relevant ADRs

## Common Pitfalls

- Mixing technical implementation details into the spec (save those for the plan)
- Allowing ambiguous language (“fast”, “secure”) without quantitative targets
- Proceeding while `[NEEDS CLARIFICATION]` items remain unresolved

## References

- Spec Kit repo: https://github.com/github/spec-kit
