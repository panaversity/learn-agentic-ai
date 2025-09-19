# What is a Pull Request?

In our software/dev context, **PR = [Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)**.

It’s a proposal to merge your changes from one branch into another (e.g., `feature/x` → `main`) on platforms like GitHub/GitLab/Bitbucket. A PR bundles:

* the **diff/commits**
* a **description** of what/why (often linking issues/ADRs)
* **checks** (CI tests, linters)
* **code review** comments/approvals

**Typical PR flow:** push branch → open PR → CI runs → reviewers comment/request changes → you push fixes → approvals → merge → PR closes.

**Good PR etiquette (the “suit on” version):**

* Small, focused scope; clear title & summary
* Link to ADRs/issues; include screenshots or curl examples if relevant
* Passing tests/linters; add/adjust tests for new behavior
* Note breaking changes and rollout steps

(Outside dev, PR can also mean **Public Relations**, but here we mean **Pull Request**.)
