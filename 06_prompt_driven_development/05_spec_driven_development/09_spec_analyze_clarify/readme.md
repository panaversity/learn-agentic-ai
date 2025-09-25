# Step 9: Clarify & Analyze Deep Dive

**Goal:** master the feedback loops powered by `/clarify` and `/analyze` so specs, plans, and tasks stay coherent as context evolves.

## Inputs

- Latest `spec.md`, `plan.md`, and `tasks.md`
- Transcript exports from `/clarify` and `/analyze`
- Stakeholder feedback, issue comments, and unanswered questions
- Constitution clauses governing change management

## Actions

1. **Clarification loop**
   - Run `/clarify` whenever intent changes or new stakeholders join.
   - Categorize questions (scope, UX, data, compliance) and assign owners.
   - Document answers inline in the spec or as linked ADRs.
2. **Gap analysis**
   - Execute `/analyze` after any update to spec, plan, or tasks.
   - Work through the coverage report: close missing links, add tasks, or adjust the plan.
3. **Decision logging**
   - Use ADRs or decision logs to capture resolutions surfaced during clarification.
   - Update constitution if patterns emerge (e.g., recurring compliance constraints).
4. **Automation**
   - Set up CI to run `/analyze` (via `specify check` scripts) on PR branches to prevent drift.
   - Store transcripts in `.specify/memory/` or `docs/logs/clarify/` for auditability.
5. **Ready-to-plan signal**
   - Before running `/plan`, confirm all `/clarify` items are resolved and `/analyze` is green.

## Deliverables

- Consolidated clarification log with statuses (Open, Answered, Deferred)
- Updated spec/plan/task artifacts reflecting answers and gap closures
- Automation script or checklist ensuring `/clarify` → `/plan` → `/tasks` remains orderly

## Quality Gates ✅

- `/clarify` queue empty (all questions answered or explicitly deferred with owners)
- `/analyze` reports zero blocking gaps prior to implementation
- Decision log/ADR list updated for every significant clarification outcome

## Common Pitfalls

- Skipping `/clarify` after spec edits, leading to hidden ambiguity
- Ignoring `/analyze` warnings (often exposes missing tests or constitution violations)
- Losing track of decisions because transcripts aren’t stored or linked to artifacts

## References

- Spec Kit repo: https://github.com/github/spec-kit
- Spec Kit Video Overview: https://www.youtube.com/watch?v=a9eR1xsfvHg
