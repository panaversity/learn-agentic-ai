# Step 10: Evaluate & Govern

**Goal:** operationalize continuous verification and governance so SDD artifacts stay trustworthy long after initial delivery.

## Inputs

- CI/CD pipeline definitions
- Contract tests, unit tests, evaluation harnesses (e.g., promptfoo suites)
- Constitution enforcement scripts, PR templates, and automation hooks
- Monitoring/observability tooling (logs, traces, dashboards)

## Actions

1. **Evaluation strategy**
   - Map each spec acceptance criterion to automated checks (unit, integration, EDD).
   - Schedule smoke vs. full evaluation suites (e.g., smoke on PRs, full nightly).
2. **Governance automation**
   - Enforce constitution and spec compliance via PR templates, checklists, or GitHub Actions.
   - Run `specify check` (or custom scripts) in CI to ensure environment and agent prerequisites stay valid.
3. **Monitoring & alerting**
   - Instrument the implementation according to the plan’s observability section.
   - Feed runtime metrics back into specs/ADRs when behavior assumptions change.
4. **Review cadence**
   - Hold periodic spec reviews (monthly/quarterly) to evaluate drift and retire obsolete sections.
   - Audit closed tasks vs. spec sections to confirm coverage remains accurate.
5. **Versioning & release notes**
   - Tag spec and plan versions alongside releases.
   - Capture “spec deltas” in release notes so downstream teams know what changed.

## Deliverables

- CI pipeline enforcing spec/constitution checks
- Evaluation dashboards or reports tied to acceptance criteria
- Governance runbook documenting review cadences and escalation paths

## Quality Gates ✅

- All mandatory checks (tests, evaluations, constitution validations) block merges when failing
- Monitoring alerts tied to spec-defined SLOs are active and reviewed
- Spec/plan versions incremented with each release and archived for traceability

## Common Pitfalls

- Treating evaluations as optional, leading to drift between spec and reality
- Allowing governance scripts to fall behind as constitution rules evolve
- Forgetting to version specs/plans, making it hard to audit historical intent

## References

- Spec Kit repo: https://github.com/github/spec-kit
- Spec Kit Video Overview: https://www.youtube.com/watch?v=a9eR1xsfvHg
- Promptfoo docs: https://promptfoo.dev/
