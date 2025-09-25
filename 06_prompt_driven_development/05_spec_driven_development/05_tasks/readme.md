# Step 5: Generate Task List

**Goal:** turn the spec and plan into sequenced, testable work items that an agent (or human) can deliver incrementally.

## Inputs

- Approved `spec.md`
- Approved `plan.md`
- Constitution rules on task sizing and branching

## Actions

1. Invoke `/tasks` to have the agent draft `tasks.md`.
2. Follow up with `/analyze` to validate coverage across constitution, spec, plan, and tasks; address every flagged gap before proceeding.
3. Review each task and ensure it includes:
	- A clear objective tied back to a spec section
	- Acceptance criteria / tests to run when complete
	- Dependencies or prerequisites
	- Suggested file touchpoints and guardrails (e.g., “limit diff to X files”)
4. Re-order tasks into phases or milestones; keep early tasks focused on scaffolding and validation.
5. Split tasks that exceed the constitution’s workload limits.
6. Tag tasks with owners and expected effort (story points or ideal hours).
7. Commit `tasks.md` and, if needed, create corresponding issues in your tracker.

### Task Review Checklist

- ✅ Every task references the spec and/or plan section it fulfills
- ✅ Tasks are independent wherever possible and list dependencies when not
- ✅ Acceptance criteria mention automated checks (unit, E2E, evaluation harness)
- ✅ “Definition of Done” includes documentation and PR expectations

## Deliverables

- Curated `tasks.md` grouped by phase/milestone
- Backlog entries or tickets linked to each task (optional but recommended)

## Quality Gates ✅

- Team agrees the tasks cover 100% of the spec scope
- `/analyze` report shows no open coverage gaps
- No single task is larger than one iteration (≤ 0.5–1 day for a single contributor)
- Each task can be verified through tests or observable outputs

## Common Pitfalls

- Dumping the agent-generated list without review (often contains vague or overlapping tasks)
- Forgetting to include tasks for tests, docs, and release work
- Allowing tasks that require touching unrelated code paths (increases risk)
