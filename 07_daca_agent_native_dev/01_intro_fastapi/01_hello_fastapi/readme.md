# Step 1: [Setting Up a FastAPI Project with UV](https://fastapi.tiangolo.com/?h=installation#dependencies)

## Step 1: Create a Project Directory and Switch to it

```bash
uv init fastdca-p1
cd fastdca-p1
```

### Create and Activate the Virtual Environment

On macOS/Linux:

```bash
uv venv
source .venv/bin/activate
```

On Windows:

```bash
uv venv
.venv\Scripts\activate
```

**Note**: With PEP 582 support (Python 3.11+), `uv` may not require manual activation for running commands.

### Add Dependencies

We’ll need FastAPI, Uvicorn (ASGI server):

```bash
uv add "fastapi[standard]"
```

The [fastapi[standard]](https://fastapi.tiangolo.com/?h=installation#dependencies) install optional dependencies especially

- `fastapi`: The web framework.
- `uvicorn`: The ASGI server to run the app.
- `httpx`: An HTTP client for testing FastAPI endpoints.

We will add `pytest` and `pytest-asyncio` for unit testing. More on them later in step 05.

To add a development dependency, use the --dev flag

```bash
uv add --dev pytest pytest-asyncio
```

This updates `pyproject.toml`:

```toml
[project]
name = "fastdca-p1"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi[standard]>=0.115.12"
]
[dependency-groups]
dev = [
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
]
```

---

## Step 2: Create your first API route.

### Hello API: Create your first API

Edit main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### Run Server

Run the server with following command in terminal:

```bash
fastapi dev main.py
```
The command `fastapi dev main.py` is used to run a FastAPI application in development mode. Here's a breakdown:

- **FastAPI**: A modern, high-performance Python web framework for building APIs.
- **dev**: A subcommand provided by FastAPI's CLI (introduced in FastAPI 0.100.0 and later) to run the application in development mode with automatic reloading.
- **main.py**: The Python file containing your FastAPI application code (typically where the `FastAPI()` instance is defined).


**Notes:**
- Requires FastAPI and Uvicorn installed (`uv add fastapi[standard]` or `pip install fastapi[standard]`).
- Use `fastapi dev` for development only, not production.
- If your app instance isn’t named `app` or is in a different file/module, you may need to specify it (e.g., `fastapi dev myapp:app`).
- If you can get any error ensure fastapi is not installed globally or remove it. Alternatively you can also use this command

OR

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Test APIs

Open in browser

http://localhost:8000

http://localhost:8000/items/5?q=somequery

You already created an API that:

- Receives HTTP requests in the paths / and /items/{item_id}.
- Both paths take GET operations (also known as HTTP methods).
- The path /items/{item_id} has a path parameter item_id that should be an int.
- The path /items/{item_id} has an optional str query parameter q.

### Interactive API docs

Now go to http://localhost:8000/docs
