# Step 6: Implement (The Review Loop)

**Goal:** execute tasks through tight, test-driven loops that reference the spec and plan at every change.

## Inputs

- Prioritized items from `tasks.md`
- Relevant spec sections, plan excerpts, and constitution rules
- Agent prompts or PHR scripts for RED → GREEN → REFACTOR → EXPLAIN

## Actions

1. Select the next ready task and restate its acceptance criteria.
2. Run `/implement` with the specific task context when using Spec Kit defaults, or drive the agent manually through a Prompt-Driven Development loop:
	- **Architect:** restate task context, allowed files, and constraints.
	- **Red:** generate failing tests or evaluations first.
	- **Green:** implement the minimum code to satisfy the new tests.
	- **Refactor:** clean up while keeping tests green.
	- **Explain:** summarize changes for future reviewers.
3. Run automated checks locally (`uv run pytest -q`, linters, evaluation harnesses) after each GREEN/refactor step.
4. Review diffs yourself—reject anything not aligned with the spec/plan/constitution.
5. Update documentation (README, changelog) and link the task ID in the commit message.
6. Open a PR referencing:
	- Spec section(s)
	- Plan decisions or ADRs
	- Task identifier
	- Test evidence (logs, screenshots)

## Deliverables

- Small, traceable commits with passing tests
- PRs that link back to spec, plan, tasks, and constitution rules
- Updated automation (CI, evaluations) as needed to enforce new behavior

## Quality Gates ✅

- Unit/contract tests and evaluation suites pass locally and in CI
- PR template’s “Spec compliance” checkbox references exact sections
- Reviewer sign-off confirms acceptance criteria and tests are sufficient

## Common Pitfalls

- Skipping the RED step and relying on ad-hoc manual testing
- Allowing the agent to modify unrelated files or refactor outside task scope
- Merging without updating documentation or leaving TODOs unresolved
