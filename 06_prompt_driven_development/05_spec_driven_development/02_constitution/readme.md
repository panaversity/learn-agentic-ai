# Step 2: Define Constitution

**Goal:** document the non-negotiable principles that every spec, plan, and task must honor.

## Inputs

- The generated `.specify/memory/constitution.md`
- Any existing engineering guardrails (testing policy, security requirements, coding standards)
- Stakeholder alignment on mandatory practices

## Actions

1. In your agent chat, run `/constitution` to generate or update the baseline document.
2. Open `.specify/memory/constitution.md` and replace placeholders with concise, testable rules.
3. Group rules by theme (e.g., Quality, Security, Delivery).
4. For each rule, add an enforcement note: where will it be checked (CI, PR template, manual review)?
5. Commit the first version as `v1.0` and create an ADR if the rules encode significant organizational policy.
6. Schedule a recurring review (e.g., once per quarter) to keep the constitution current.

### Sample Structure

```markdown
# Constitution v1.0

## Quality
- Specs must contain acceptance tests before implementation starts.
- Every PR references the spec section and links to passing contract tests.

## Delivery
- Tasks are limited to < 4 hours of focused work and ship with tests.
- Feature branches require small, reviewable diffs (< 400 LOC).

## Security & Compliance
- No secrets committed; use environment variables and secret managers.
- Personal data must remain in-region; see Compliance ADR-001.

## Enforcement
- GitHub Action `constitution-check.yml` blocks merges lacking spec/task links.
- Weekly review ensures constitution revisions follow ADR process.
```

## Deliverables

- Canonical constitution stored in Git and referenced by every downstream artifact
- Change-management notes (ADR or PR description) capturing the reasoning for initial rules

## Quality Gates ✅

- Every rule is binary (pass/fail) and has an enforcement mechanism
- Specs/Plans created afterward explicitly link back to relevant constitution clauses
- Constitution updates require PR review (no direct pushes)

## Common Pitfalls

- Writing vague aspirations (“write clean code”) instead of enforceable rules
- Allowing the constitution to drift from reality—review it alongside major releases
- Leaving the file outside version control (loses traceability)

## References

- GitHub Spec Kit repo: https://github.com/github/spec-kit
- Microsoft Dev Blog (Spec Kit intro): https://developer.microsoft.com/blog/spec-driven-development-spec-kit
