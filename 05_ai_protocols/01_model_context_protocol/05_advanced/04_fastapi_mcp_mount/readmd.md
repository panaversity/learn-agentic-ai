# 04: Mounting an MCP Application within FastAPI

**Objective:** This guide will demonstrate how to integrate a Model Context Protocol (MCP) application, built with `FastMCP`, into a standard FastAPI web application. This allows you to serve both your MCP services and other regular HTTP API endpoints from a single FastAPI server.

## Understanding "Mounting" in Web Applications

Before we dive into the specifics of MCP and FastAPI, let's clarify what "mounting" means in the context of web applications.

Imagine you have a main web application (e.g., built with FastAPI) that handles various general tasks for your website or service. Now, suppose you have another, more specialized, self-contained web application (like an MCP server built with `FastMCP`). Instead of running these two applications completely separately (on different ports or servers), "mounting" allows you to integrate the specialized application _into_ the main application at a specific URL path.

**Here's the core idea:**

1.  **Path-Based Routing:** The main application delegates all HTTP requests that start with a certain URL path prefix (e.g., `/mcp_services` or `/special_app`) to the mounted sub-application.
2.  **Independent Operation:** The sub-application handles these requests as if it were running on its own, but it operates within the context of the main application's server process.
3.  **Analogy:** Think of a large department store (the main FastAPI app). Mounting is like dedicating a specific section or wing of that store to a specialized boutique (the `FastMCP` app). Customers who go to that wing are served by the boutique, but it's still part of the larger store.

**Why is this possible with FastAPI and `FastMCP`?**

This seamless integration is possible because both FastAPI and `FastMCP` are built on the **ASGI (Asynchronous Server Gateway Interface)** standard. ASGI defines a common way for Python asynchronous web servers (like Uvicorn) to communicate with asynchronous web applications and frameworks. Since both are ASGI-compliant, they can be composed together, with one acting as a sub-application within the other.

It's important to note that while the Model Context Protocol (MCP) specification itself ([https://modelcontextprotocol.io/specification/2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26)) defines the rules for communication (the "what"), it doesn't prescribe specific deployment methods like mounting. However, the design of MCP to enable "seamless integration" and the fact that tools like the `FastMCP` library produce ASGI-compliant applications are what make practical integration strategies such as mounting within FastAPI a natural and effective approach (the "how").

In our case, the `FastMCP` instance is a complete ASGI application, and FastAPI provides a `mount()` method specifically designed to incorporate other ASGI applications.

Now, let's look at why you'd specifically want to mount an MCP app within FastAPI.

## Why Mount an MCP App in FastAPI?

While `FastMCP` can run as a standalone server (as seen in module `02_mcp_over_http`), there are several scenarios where you might want to embed it within a larger FastAPI application:

1.  **Unified API Gateway:** You can expose both your specialized MCP agentic services (tools, resources, prompts) and general-purpose REST/GraphQL APIs through the same server and port. This simplifies deployment and access.
2.  **Leverage FastAPI Features:** You can utilize FastAPI's rich ecosystem for the non-MCP parts of your application, including:
    - Advanced request validation with Pydantic.
    - Dependency injection.
    - Automatic interactive API documentation (Swagger UI, ReDoc) for your non-MCP endpoints.
    - Middleware for logging, authentication, CORS, etc., that can apply to the entire application or specific parts.
3.  **Code Organization:** Keep your agent-specific logic within the MCP app and other business logic in standard FastAPI routers and path operations.
4.  **Gradual Integration:** If you have an existing FastAPI application, you can add MCP capabilities by mounting an MCP sub-application.

## Core Concepts

1.  **ASGI (Asynchronous Server Gateway Interface):** Both FastAPI and `FastMCP` are ASGI applications. ASGI is a standard interface between web servers and Python asynchronous web applications/frameworks. This commonality is what makes mounting possible.
2.  **`FastAPI().mount()`:** FastAPI provides a `mount()` method that allows you to include another ASGI application (like our `FastMCP` app) at a specific path. All requests to that path prefix will be forwarded to the mounted sub-application.
3.  **`FastMCP` Instance as ASGI App:** Your `FastMCP` instance (e.g., `mcp_application`) is itself an ASGI-compliant application. This is what FastAPI will mount directly.
4.  **Uvicorn:** A lightning-fast ASGI server, commonly used to run FastAPI applications (and thus, our combined FastAPI + MCP app).

## Practical Steps: Building the Combined Server

We'll create a FastAPI server that also serves the MCP application we developed in `02_mcp_over_http`.

1.  **Project Setup:**
    Assume you have a directory structure like this:

    ```
    04_fastapi_mcp_mount/
    ├── server/
    │   └── main.py  # Our FastAPI + MCP server code
    └── readmd.md    # This file
    ```

    You'll also need a `pyproject.toml` for your server's dependencies.

2.  **Initialize Python Environment and Install Dependencies (if not already done for a similar setup):**
    Navigate to your project's root or the `04_fastapi_mcp_mount` directory.

    ```bash
    uv init server # if you don't have a pyproject.toml
    uv venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate    # Windows
    ```

    Install necessary packages:

    ```bash
    uv add fastapi "mcp[cli]" "fastapi[standard]"
    ```

    - `fastapi`: The FastAPI framework.
    - `mcp[cli]`: The MCP SDK (includes `FastMCP`).

3.  **Create `server/main.py`:**
    This file will contain both your FastAPI app and the mounted MCP app.

4.  **Populate `server/main.py`:**
    See the "Full Code Example" section below. It will include:

    - Imports: `FastAPI`, `FastMCP`, and types for MCP definitions.
    - An `FastMCP` instance (`mcp_application`) with a tool, resource, and prompt (similar to `02_mcp_over_http/server/main.py`).
    - A `FastAPI` instance (`fastapi_app`).
    - Mounting the `mcp_application` (the `FastMCP` instance itself) onto `fastapi_app` at a path like `/mcp`.
    - A simple FastAPI root endpoint (e.g., `/`) for demonstration.

5.  **Running the FastAPI + MCP Server:**
    Execute the following command in your terminal (from the directory containing `server/main.py`, which is `04_fastapi_mcp_mount/server` if you followed the structure):

    ```bash
    uvicorn main:fastapi_app --reload --port 8000
    ```

    - `main`: Refers to `main.py`.
    - `fastapi_app`: Refers to the `FastAPI()` instance variable inside `main.py`.
    - `--reload`: Uvicorn will automatically restart the server when code changes are detected (useful for development).
    - `--port 8000`: Specifies the port to run on.

6.  **Testing:**
    - **FastAPI root endpoint:** Open your browser to `http://localhost:8000/`. You should see the response from your FastAPI root endpoint.
    - **MCP services:** Use the client from `02_mcp_over_http/client/main.py`. Ensure its `SERVER_MCP_ENDPOINT_URL` is set to `http://localhost:8000/mcp` (or whatever path you mounted the MCP app to). The client should connect and interact with the tools, resources, and prompts just as before.
    - **FastAPI docs (for non-MCP routes):** Navigate to `http://localhost:8000/docs` in your browser to see the auto-generated Swagger UI for any regular FastAPI path operations you defined.

## Full Code Example (`04_fastapi_mcp_mount/server/main.py`)

```python
# 04_fastapi_mcp_mount/server/main.py
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent

# --- 1. Create and Configure the MCP Application (FastMCP instance) ---
mcp_application = FastMCP(
    name="my-mounted-mcp-server",
    description="An MCP server mounted within a FastAPI application.",
    stateless_http=True,
    json_response=True,
)

# Define a simple tool for the MCP app
@mcp_application.tool()
def greet_mounted(name: str = "Mounted World") -> str:
    """Returns a greeting message from the mounted MCP app."""
    print(f"[Mounted MCP Server Log] greet_mounted tool called with name: {name}")
    return f"Hello, {name}, from the MCP application mounted in FastAPI!"

# Define a simple static resource for the MCP app
MOUNTED_WELCOME_MSG_URI = "app:///messages/mounted_welcome"
@mcp_application.resource(
    uri=MOUNTED_WELCOME_MSG_URI,
    name="Mounted Welcome Message",
    description="A static welcome message from the mounted MCP app.",
    mime_type="text/plain"
)
async def get_mounted_welcome_resource() -> str:
    """Provides a static welcome message from the mounted MCP app."""
    print(f"[Mounted MCP Server Log] Welcome resource ('{MOUNTED_WELCOME_MSG_URI}') requested.")
    return "This is a welcome resource from the MCP app, served via FastAPI mount!"

# Define a simple prompt template for the MCP app
@mcp_application.prompt(
    name="mounted_simple_question",
    description="Generates a simple question from the mounted MCP app."
)
async def mounted_simple_question_prompt(entity: str = "the universe") -> list[PromptMessage]:
    """Generates a prompt asking why something is a certain color, from the mounted app."""
    print(f"[Mounted MCP Server Log] mounted_simple_question prompt requested for entity: {entity}")
    return [
        PromptMessage(
            role="user",
            content=TextContent(text=f"From the mounted app: Why is {entity} so vast?", type="text")
        )
    ]

# --- 2. Create the FastAPI Application ---
fastapi_app = FastAPI(
    title="Main FastAPI Application",
    description="This app demonstrates mounting an MCP sub-application.",
    version="1.0.0"
)

# --- 3. Mount the MCP Application onto FastAPI ---
# The FastMCP instance itself is an ASGI-compatible app
fastapi_app.mount("/mcp", mcp_application.streamable_http_app(), name="mcp_services")

# --- 4. Add other FastAPI specific routes (optional) ---
@fastapi_app.get("/")
async def read_root():
    """A simple root endpoint for the FastAPI application."""
    return {
        "message": "Welcome to the main FastAPI application!",
        "mcp_endpoint": "/mcp",
        "fastapi_docs": "/docs"
    }

# To run this server (save as main.py in your server directory):
# uvicorn main:fastapi_app --reload --port 8000
```

## Key Takeaways

- Mounting allows you to seamlessly integrate `FastMCP` services into a broader FastAPI application.
- You use `fastapi_instance.mount("/path_prefix", mcp_app_instance)` where `mcp_app_instance` is your `FastMCP` object.
- The MCP client interacts with the mounted app via the prefixed URL (e.g., `http://host:port/path_prefix`).
- This approach provides flexibility and allows you to leverage the strengths of both FastAPI and MCP in a single, cohesive server deployment.

## Next Steps

- Adapt the client from `02_mcp_over_http` to connect to the MCP app mounted at `http://localhost:8000/mcp`.
- Explore adding more complex FastAPI routes alongside your MCP application.
- Consider how FastAPI's middleware or dependency injection could be used to enhance your overall application, potentially even interacting with or providing context to your MCP services (though direct interaction requires careful design).
- This setup is a robust way to prepare for integrating with systems like the OpenAI Agents SDK, where the agent might interact with an MCP server that is part of a larger application infrastructure.
