# `uv`: The Unified Python Package & Project Manager

- [How to install UV - Notion Guide?](https://www.notion.so/UV-Installation-236e9749823180b7ab82d96a3b5997fd?source=copy_link)
- [Python UV: The Ultimate Guide to the Fastest Python Package Manager](https://www.datacamp.com/tutorial/python-uv)
- [Official Docs](https://docs.astral.sh/uv/)
- [Running scripts](https://docs.astral.sh/uv/guides/scripts/)
- [Working on projects](https://docs.astral.sh/uv/guides/projects/)
- [CLI Reference](https://docs.astral.sh/uv/reference/cli/)
- [Watch: Python Setup, Simplified: A Complete "uv" Tutorial!](https://www.youtube.com/watch?v=-J5SnWR4UXw)

## 1. What is `uv`?

`uv` is a fast, all-in-one tool for managing Python projects end-to-end. It can create a virtual environment, download and pin a specific Python version, add or update dependencies, maintain a lock file for reproducible installs, run code and tools without manual activation, and build/publish packages.
You mainly work with two files:

* **`pyproject.toml`** – your declared requirements
* **`uv.lock`** – the exact versions resolved and installed

## 2. Applications vs. Libraries in `uv`

`uv` supports building both **applications** and **libraries**, each serving a different role in the Python ecosystem. Applications are end-user programs meant to be run directly—examples include command-line tools, web services, and automation scripts. They contain an entry point (such as a CLI command or `__main__.py`) and are executed in a controlled runtime environment to ensure consistency.

Libraries, on the other hand, are collections of reusable code meant to be imported by other projects. They provide shared functionality and are typically published to package indexes like PyPI so other developers can depend on them. While applications deliver a final product to users, libraries act as building blocks that many applications or other libraries can leverage. Both are important: applications provide value directly to end-users, while libraries promote code reuse, maintainability, and ecosystem growth.

## 3. How Applications Are Made in `uv`

When creating applications, `uv` offers two main approaches:

* **Packaged applications** – Built as installable Python packages with a defined entry point. This structure is best for long-term projects, distribution to other environments, or when versioning and reproducibility are important. Packaged applications can be easily installed and run anywhere with the right environment.
* **Simple applications** – Created as unstructured project folders containing scripts that can be run directly with `uv run`. These are quick to set up and well-suited for prototypes, internal tools, and one-off utilities where packaging overhead is unnecessary.

Both approaches have value: packaged applications are ideal for polished, shareable software, while simple applications maximize speed and flexibility during early development or in internal use cases.

## 4. Development Lifecycle (Step-By-Step)

| Step | Title                      | Description                                                                                                                                |
| ---- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1    | Initialize the Project     | `uv init` scaffolds a clean project structure and starter `pyproject.toml`, replacing manual folder setup and template copying.            |
| 2    | Pin the Python Version     | `uv python pin 3.12` ensures everyone uses the same interpreter version, downloading it if necessary and recording it for all devs and CI. |
| 3    | Create Environment         | `uv` creates a virtual environment automatically on first dependency action. `uv run` lets you execute code without manual activation.     |
| 4    | Add Runtime Dependencies   | `uv add pkg` updates your manifest, resolves, locks, and installs in one atomic step—keeping declared and installed packages in sync.      |
| 5    | Add Dev Tools              | `uv add --dev tool` cleanly separates dev dependencies (tests, lint, format) from runtime packages, all in the same lock file.             |
| 6    | Optional Feature Groups    | `uv add --group docs mkdocs` lets you define install-on-demand groups for optional features.                                               |
| 7    | Lock Dependencies          | `uv` automatically maintains `uv.lock` after changes for reproducible installs.                                                            |
| 8    | Sync Environment           | `uv sync` ensures the environment matches the lock file exactly; `uv sync --frozen` blocks changes unless the lock is updated.             |
| 9    | Run Code & Tools           | `uv run <cmd>` runs commands in the correct environment without needing to activate the venv.                                              |
| 10   | Lint / Format / Type Check | Running tools via `uv run` ensures they use the exact locked versions locally and in CI.                                                   |
| 11   | Test                       | `uv run pytest` guarantees tests run with the locked dependency set—no “works on my machine” surprises.                                    |
| 12   | Upgrade Dependencies       | `uv upgrade` re-resolves, locks, and installs updates in one controlled step.                                                              |
| 13   | Build Artifacts            | `uv build` quickly produces both wheel and sdist artifacts with minimal config.                                                            |
| 14   | Publish                    | `uv publish` builds (if needed) and uploads to PyPI or another index in one step.                                                          |
| 15   | Use Cache                  | Shared caching speeds up installs and can be inspected or pruned.                                                                          |
| 16   | Offline / Restricted       | Cache export/import plus `uv sync --frozen` allows full offline environment recreation.                                                    |
| 17   | CI Reproducibility         | `uv sync --frozen` in CI ensures lock and manifest match before install.                                                                   |
| 18   | Inspect Environment        | `uv run pip list` and similar commands always target the project’s environment, not the global Python.                                     |
| 19   | Clean & Prune              | `uv cache prune` or environment removal frees space; everything can be rebuilt from manifest + lock.                                       |
| 20   | Monorepo Management        | Each project in a monorepo can have its own `pyproject.toml` + `uv.lock` for independent syncing.                                          |
| 21   | Migrate (Optional)         | `uv` can import specs from legacy requirement files, resolve, and lock—simplifying to the two-file model.                                  |

## 5. Common Beginner Pitfalls (and Fixes)

* **Forgetting to commit `uv.lock`** – Always commit so others get the same versions.
* **Editing `pyproject.toml` by hand** – Use `uv add` or `uv remove` so the lock updates automatically. If you do edit manually, run a command that re-locks (`uv sync` or `uv add`) to refresh.
* **Manually activating the environment** – Use `uv run` instead.
* **Mixing raw `pip install` with `uv add`** – Stick with `uv add` so the lock stays correct.

---

### Cursor System Rules

When working in Python within Cursor, always use **`uv`** as the package manager.

Whenever possible, prefer using CLI commands for common tasks instead of writing manual setup code. For example, when prompted to create a new project with `uv`:

**Packaged Applications:**
A packaged application is useful in many scenarios—for example, when building a command-line interface to be published on PyPI or when you want to keep tests in a dedicated directory.

To create a packaged application:

```bash
uv init --package example-pkg
```

**Adding Dependencies:**
To install a dependency in your project:

```bash
uv add openai-agents
```

---