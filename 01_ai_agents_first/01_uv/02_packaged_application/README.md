# Packaged Application with `uv`

## 1. Overview

A **packaged application** in `uv` is a Python project that is structured like a distributable package.
It includes metadata, dependencies, and optional entry points so it can be:

- Installed locally or on other machines
- Maintained cleanly with versioning and dependencies under control
- Run via importable modules or CLI commands

Best for:

- Applications that will be reused or shared internally
- Projects requiring a clean, importable module structure
- Long-term maintainable projects
- Apps needing CLI entry points or libraries for other projects

Compared to a simple application, packaged applications handle:

- **Versioning** (in `pyproject.toml`)
- **Installation** in a standard way
- **Script entry points** without extra `tool.uv` config

## 2. Prerequisites

Before creating a **packaged** application, ensure:

1. **`uv` is installed** – If not, follow the instructions in [`../00_uv_installation/README.md`](../00_uv_installation/readme.md).
   Check installation:

   ```bash
   uv --version
   ```

   **Expected output (example):**

   ```
   uv 0.x.x
   ```

   _(Exact version may vary.)_

2. **Python is installed** – `uv` can manage and pin Python versions for you.
   Check availability:

   ```bash
   python --version
   ```

   **Expected output (example):**

   ```
   Python 3.x.x
   ```

## 3. Steps to Create a Packaged Application

### Step 1 — Create the Project

Open a terminal in the folder where you want to create the new project (e.g., `Projects`) and run:

```bash
uv init --package my-packaged-app
cd my-packaged-app
```

This will:

- Create the `my-packaged-app` folder
- Initialize a new `uv` packaged project using the **`src` layout**, which keeps source code separate from configuration and metadata
- Include:

  - `.gitignore`
  - `.python-version` (automatically pinned)
  - `src/my_packaged_app/` (package folder with `__init__.py`)
  - `pyproject.toml`
  - `README.md`

**Expected Project Structure:**

```
my-packaged-app/
├── .gitignore                # Pre-configured ignore rules for Python projects
├── .python-version           # Automatically pinned Python version
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # Project documentation
└── src/
    └── my_packaged_app/      # Your package directory
        └── __init__.py       # Marks this as a Python package
```

> **Why the `src` layout?**
> It prevents accidental imports from local files during development and ensures your code is tested the same way it will be installed.

### Step 2 — Create the Environment

Create the virtual environment and lock file immediately (handy for editor setup like VS Code):

```bash
uv sync
```

This will:

- Create the `.venv` folder so editors can detect the interpreter
- Generate `uv.lock`, locking dependencies to versions resolved from `pyproject.toml`

### Step 2.1 — (Optional) Activate the Environment

> You **do not** need to activate the environment to use `uv` (`uv run …` uses the project env automatically).
> Activate only if you prefer running `python`/`pip` directly without `uv run`, or for editor/REPL workflows.

If you’re in VS Code and using the built-in terminal and have set the interpreter, you do not need to activate the environment manually.

**macOS/Linux:**

```bash
source .venv/bin/activate
```

**Windows:**

```bash
.\.venv\Scripts\activate
```

- Your shell prompt will typically show `(.venv)` when activated.
- To deactivate:

  ```bash
  deactivate
  ```

**PowerShell note (if activation is blocked):**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

(Or just keep using `uv run …` without activating.)

### Step 3 — Open VS Code and Select the Interpreter

1. Open the project in VS Code:

   ```bash
   code .
   ```

2. Open the **Command Palette**:

   - **Windows/Linux**: `Ctrl+Shift+P`
   - **macOS**: `Cmd+Shift+P`
     Then select: **Python: Select Interpreter** → **Enter Interpreter Path** → **Find**.

3. Choose the interpreter from the project’s `.venv`:

   - **macOS/Linux**: `.venv/bin/python`
   - **Windows**: `.venv\Scripts\python.exe`

4. Confirm the selected interpreter appears in VS Code’s status bar.

### Step 4 — What `__init__.py` does and why `uv run my-packaged-app` works

Your package currently exposes an entry function in `src/my_packaged_app/__init__.py`:

```python
# src/my_packaged_app/__init__.py
def main() -> None:
    print("Hello from my-packaged-app!")
```

- **What `__init__.py` is for (simple):** it marks the folder as a package and is a good place to expose your package’s public API (light helpers, `__version__`, re-exports).
- **Why your command works:** in `pyproject.toml` you have:

  ```toml
  [project.scripts]
  my-packaged-app = "my_packaged_app:main"
  ```

  This maps the CLI command `my-packaged-app` to the callable `main` inside the **package module** `my_packaged_app` (i.e., `__init__.py`). No need to write `__init__` in the path.

> **Recommendation:** keep `__init__.py` light. Put most of your application logic in `main.py` and point a script there.

### Step 5 — Create `main.py` and Add a Second CLI Entry (Keep the Original)

Right now your CLI command `my-packaged-app` is wired to run the `main()` function in `__init__.py`.
We’ll **add** a second command that runs a new `main.py` file — without removing the first — and also note what happens if you put **top-level code** in it.

#### 1) Create `main.py` inside your package

```
src/
  my_packaged_app/
    __init__.py
    main.py
```

**`src/my_packaged_app/main.py`:**

```python
print("Top-level hello from main.py!")  # runs immediately when file is executed or imported

def main() -> None:
    print("Hello from my-packaged-app! — running main.py")
```

#### 2) Add a new script entry in `pyproject.toml`

Commands in `[project.scripts]` use the form:

```
command-name = "module_path:function_name"
```

- **command-name** → The name you’ll type after `uv run`
- **module_path** → The Python module path (dots for folders, no `.py` extension)
- **function_name** → The callable inside that module

```toml
[project.scripts]
my-packaged-app = "my_packaged_app:main"           # Runs main() from __init__.py
my-packaged-app-main = "my_packaged_app.main:main" # Runs main() from main.py
```

> In packaged apps, `uv` resolves script entries at runtime, so you can run the new command right away after saving `pyproject.toml`.

#### 3) Run either command

```bash
# Original entry point (__init__.py:main)
uv run my-packaged-app
# Output:
# Hello from my-packaged-app!

# New entry point (main.py:main)
uv run my-packaged-app-main
# Output:
# Top-level hello from main.py!
# Hello from my-packaged-app! — running main.py
```

**About top-level code:**
Any statements (like `print(...)`) not inside a function/class run **as soon as the module is imported or executed**.
That’s why the top-level print appears before `main()` prints.

### Step 6 — Run your app (four reliable ways)

You now have two CLI entries:

- `my-packaged-app` → calls `my_packaged_app:main` (from `__init__.py`)
- `my-packaged-app-main` → calls `my_packaged_app.main:main` (from `main.py`)

Pick whichever run style fits your workflow:

#### 6.1 Run by **CLI script** (best DX for packaged apps)

Uses `[project.scripts]` in `pyproject.toml`:

```bash
uv run my-packaged-app
uv run my-packaged-app-main
```

#### 6.2 Run as a **module** (package-aware; no file paths)

Respects package imports:

```bash
uv run -m my_packaged_app.main
```

#### 6.3 Run by **file path** (quick, less package-aware)

- **Windows**

  ```powershell
  uv run python .\src\my_packaged_app\main.py
  ```

- **macOS/Linux**

  ```bash
  uv run python ./src/my_packaged_app/main.py
  ```

_Note:_ path execution runs the file as `__main__`; relative imports like `from .utils import foo` will fail. Prefer 6.1 or 6.2 beyond quick checks.

#### 6.4 One-liner (handy for quick sanity checks)

```bash
uv run python -c "from my_packaged_app.main import main; main()"
```

**Remember about top-level code:** if `main.py` (or any module) has statements like `print("Hello")` at the top level, they execute **before** `main()` because the module is imported first.

### Step 7 — Add dependencies (runtime & dev)

Add a runtime dependency:

```bash
uv add <package-name>
```

Add a dev tool (linters/formatters/type checkers):

```bash
uv add --dev ruff black mypy
```

`uv` will resolve and update `uv.lock` automatically.

### Step 8 — Tips & good practices

- Keep `__init__.py` light (metadata, re-exports). Put real logic in modules like `main.py`.
- Prefer **CLI scripts** (Step 6.1) or **module runs** (Step 6.2) for day-to-day use.
- Commit: `pyproject.toml`, `uv.lock`, `.gitignore`, `.python-version`, and your `src/` folder.
- Use `uv sync --frozen` in CI or on teammates’ machines to ensure the environment exactly matches the lock file.

### Step 9 — Quick commands reference

```bash
# Create & enter project
uv init --package my-packaged-app
cd my-packaged-app

# Env & lock
uv sync

# Run (script entries)
uv run my-packaged-app
uv run my-packaged-app-main

# Run (module and file)
uv run -m my_packaged_app.main
uv run python ./src/my_packaged_app/main.py   # (Windows: .\src\my_packaged_app\main.py)

# Dependencies & dev tools
uv add <package-name>          # runtime
uv add --dev ruff black mypy   # dev tools (example)

# Reproduce exact env
uv sync --frozen
```
