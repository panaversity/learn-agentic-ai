# Step 8: Agile Spec Integration

**Goal:** weave Spec-Driven Development artifacts into your agile rituals so specs, plans, and tasks stay in lockstep with sprints.

## Inputs

- Approved constitution, spec, plan, and tasks
- Current sprint backlog or program increment roadmap
- `/clarify`, `/plan`, `/tasks`, and `/analyze` transcripts
- Team working agreements for agile ceremonies (planning, refinement, review)

## Actions

1. **Backlog mapping**
   - Break the spec into epics/stories and link each work item to spec sections.
   - Capture acceptance criteria verbatim from the spec in your backlog tool.
2. **Sprint readiness review**
   - During refinement, walk through `/clarify` outcomes to ensure the team understands scope.
   - Validate task estimates against velocity and constitution limits (< 1 day per task).
3. **Ceremony integration**
   - Kickoff: recap constitution updates and spec changes since last sprint.
   - Daily standup: report progress by task ID and spec section.
   - Review/demo: show working features alongside the spec tests that prove them.
4. **Feedback loop**
   - Feed sprint learnings back into the spec (update assumptions, risks, non-goals).
   - Raise ADRs when agile insights result in structural changes.
5. **Tooling hooks**
   - Automate links from stories/cards to spec files (e.g., GitHub issues templates, Jira smart links).
   - Use `SPECIFY_FEATURE` env var when branching per-feature without Git flow.

## Deliverables

- Updated agile backlog with traceability to spec sections and tasks
- Sprint review notes referencing tests and evaluation outcomes
- Retro action items captured as spec/constitution updates

## Quality Gates ✅

- Every active story references a spec section and task ID
- Sprint commitments map to acceptance criteria verified in CI
- Retro outcomes result in concrete spec or constitution changes (or ADRs)

## Common Pitfalls

- Treating the spec as documentation rather than the source of truth for backlog items
- Letting agile estimates drift from task sizing rules in the constitution
- Failing to close the loop when sprint feedback exposes gaps in the spec or plan

## References

- Spec Kit repo: https://github.com/github/spec-kit
- Spec Kit Video Overview: https://www.youtube.com/watch?v=a9eR1xsfvHg
