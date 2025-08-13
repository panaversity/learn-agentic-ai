# Simple Application with `uv`

## 1. Overview

A **simple application** in `uv` is a Python project without the overhead of packaging. It’s just a folder containing scripts, managed entirely by `uv` for dependencies and environment.

Best for:

- Quick prototypes
- Internal tools
- One-off automation scripts
- Proof-of-concept projects

Simple applications can be created and run almost instantly, without defining packaging metadata or publishing to PyPI.

## 2. Prerequisites

Before creating a simple application, ensure:

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

## 3. Steps to Create a Simple Application

### Step 1 — Create the Project

1. Open a terminal in a folder of your choice (e.g., `Projects`), where you want to create the new project.
2. Run:

   ```bash
   uv init my-simple-app
   cd my-simple-app
   ```

This will:

- Create the `my-simple-app` folder
- Initialize a new `uv` project with:

  - `.gitignore`
  - `.python-version` (automatically pinned)
  - `main.py` (example script)
  - `pyproject.toml`
  - `README.md`

**Expected Project Structure:**

```
my-simple-app/
├── .gitignore         # Pre-configured ignore rules for Python projects
├── .python-version    # Automatically pinned Python version
├── main.py            # Example Python script created by uv
├── pyproject.toml     # Project configuration file
└── README.md          # Empty readme file created by uv
```

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

### Step 4 — Update the Default Code

Replace the contents of `main.py` with:

```python
def main():
    print("Hello from my-simple-app! — Hassan, PIAIC")

if __name__ == "__main__":
    main()
```

This prints a greeting when the app runs.

### Step 5 — Run the Application

Run without manual activation (recommended):

```bash
uv run python main.py
```

**Expected output:**

```
Hello from my-simple-app! — Hassan, PIAIC
```

_(If you activated the environment in Step 2.1, running `python main.py` also works.)_

## 4. Optional Running Methods (Module & Script Entry Points)

You can run your simple app in “package-style” ways without fully packaging it.

### 4.1 Run as a Module

Run the script via the module resolver (future-proof if you later refactor to a package):

```bash
uv run -m main
```

This looks for `main.py` (or a `main` package) and executes it as a module. If you rename or move your main file into a package folder, adjust the module path (e.g., `uv run -m mypackage.main`).

### 4.2 Define a Script Command in `pyproject.toml`

You can expose a friendly CLI command in a **simple application** (similar to packaged apps) by enabling packaging in `uv` and defining a script entry.

Open the `pyproject.toml` file that `uv` created and add the following sections to the end

```toml
[project.scripts]
myapp = "main:main"

[tool.uv]
package = true
```

Then, refresh the environment so `uv` installs the CLI entry point:

```bash
uv sync
```

Now you can run:

```bash
uv run myapp
```

**Notes:**

- `myapp` must match the key under `[project.scripts]`.
- `"main:main"` means: open `main.py` and run the `main()` function.
- This works in a simple app, but if your long-term goal is to distribute your project or maintain it professionally, it’s better to follow the **packaged application** workflow from the start.
  Packaged apps handle scripts, versioning, dependencies, and publishing more cleanly.

## 5. Tips for Simple Applications

- Add dependencies anytime:

  ```bash
  uv add <package-name>
  ```

- Commit these for reproducibility: `pyproject.toml`, `uv.lock`, `.gitignore`, `.python-version`.
- Share the project? Others can recreate the exact environment:

  ```bash
  uv sync --frozen
  ```

- As the project grows (multiple modules, tests, distribution needs), consider switching to a **packaged application** (see [`../02_packaged_application`](../02_packaged_application/README.md)).

## 6. Quick Commands Reference

```bash
uv init my-simple-app        # Create and initialize a new project
uv sync                      # Create .venv and uv.lock now
code .                       # Open in VS Code
# (Optional) Activate the environment
source .venv/bin/activate    # macOS/Linux
.\.venv\Scripts\activate     # Windows
uv add <package-name>        # Add a dependency
uv run python main.py        # Run file-style
uv run -m main               # Run module-style
uv run myapp                 # Run script entry point (after adding to pyproject)
uv sync --frozen             # Reproduce environment exactly
deactivate                   # Leave the virtual environment
```
