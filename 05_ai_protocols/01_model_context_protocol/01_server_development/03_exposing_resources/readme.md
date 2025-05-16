# 03: Exposing [MCP Resources](https://modelcontextprotocol.io/specification/2025-03-26/server/resources): Providing Context to Agents

**Objective:** This guide will walk you through defining, registering, and serving contextual data as Model Context Protocol (MCP) Resources using the Python MCP SDK. You'll learn how to make various types of information accessible to AI agents, enabling them to perform more informed actions.

**Recap from "Defining MCP Tools":** In the previous step, we learned how to create executable functions (Tools) that an AI agent can call. Now, we'll focus on providing the data and information (Resources) that agents need to understand their environment and tasks better.

## Core Concepts for Exposing MCP Resources

### What are MCP Resources?

MCP Resources represent data or content exposed by your `FastMCP` server that an AI client (or an Agent interacting through a client) can read and use as context. Unlike Tools that perform actions, Resources provide information.

- **Reference:** [MCP Specification - Resources](https://modelcontextprotocol.io/specification/2025-03-26/server/resources)
- **Examples:**
  - Content of a file (e.g., source code, configuration, text documents).
  - Data from a database (e.g., a user's profile, product information).
  - Real-time information (e.g., current weather, stock prices, server status).
  - Structured data like JSON, CSV, or Markdown.

### Resource URI (Uniform Resource Identifier)

Each resource is uniquely identified by a URI. Clients use this URI to request a specific resource.

- **Format:** URIs can follow common schemes like `file:///path/to/your/file.txt`, `http://`, `https://`, or custom schemes defined by your application (e.g., `database:///orders/123`, `config:///app_settings`).
- **Reference:** [MCP Specification - Common URI Schemes](https://modelcontextprotocol.io/specification/2025-03-26/server/resources#common-uri-schemes)

### Defining Resource Logic with Python Functions

The content for a resource is typically generated or retrieved by a Python function (often `async def` for I/O-bound operations, but can be synchronous). This function is the "resource provider" or "handler."

### Registering Resources with `FastMCP`

You register resource providers using a decorator, typically `@mcp.resource()`, on the function that provides the resource content. `FastMCP` uses this registration to route `resources/read` requests.

- **Key Decorator Arguments (based on SDK patterns):**
  - `uri_pattern` (str): A URI or a pattern (e.g., using path parameters like `/files/{filename}`) that this provider handles.
  - `content_type` (str, optional): The MIME type of the resource (e.g., `"text/plain"`, `"application/json"`). Defaults might apply.
  - `name` (str, optional): A human-readable name for the resource or resource pattern.
  - `description` (str, optional): A description for the resource.

### Content Types (MIME Types)

Specifying the correct MIME type is crucial for the client to interpret the resource content correctly.

- **Examples:** `text/plain`, `text/markdown`, `application/json`, `text/x-python`.

## Practical Steps: Building Your Resource-Enabled Server

1.  **Create Project Directory:**

    ```bash
    uv init my_resources_server
    cd my_resources_server
    ```

2.  **Initialize Python Environment with `uv`:**

    ```bash
    deactivate
    uv venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate    # On Windows
    ```

3.  **Install Dependencies:**

    ```bash
    uv add "mcp[cli]" pydantic
    ```

    - `mcp[cli]`: The core MCP SDK with `FastMCP` and CLI tools.
    - `pydantic`: For any data models (though less common for simple resources than for tools).

4.  **Create `main.py`:**
    This file will contain your server logic and resource definitions.

5.  **Populate `main.py`:**
    Refer to the "Full Code Example" section below. It will include:

    - Imports: `FastMCP`, `datetime`.
    - `FastMCP` app instance.
    - **Resource 1:** A static welcome message resource.
    - **Resource 2:** A dynamic resource providing the current server time.
    - **Resource 3:** A resource simulating access to a project file.

6.  **Running Your MCP Server:**
    Execute the following command in your project directory:

    ```bash
    uv run mcp dev main.py
    ```

    This starts your server and the MCP Inspector (e.g., at `http://127.0.0.1:MCP_PORT` where `MCP_PORT` is shown in the console, often 6274 or 5173 for the inspector, proxying to your app usually on 6277).

7.  **Testing Your Resources:**
    - Open the MCP Inspector in your web browser.
    - Use the "Resources" section to:
      - List available resources (you should see the ones you defined).
      - Select a resource to view its metadata (URI, content type, etc.).
      - Read the content of each resource.
    - For parameterized resources (if you implement them using URI templates), the Inspector might allow you to provide parameters.

## Full Code Example (`my_resources_server/main.py`)

```python
import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP application
mcp = FastMCP(name="my-resources-server")

# --- Resource 1: Static Welcome Message ---
WELCOME_MESSAGE_URI = "app:///messages/welcome"


@mcp.resource(
    uri=WELCOME_MESSAGE_URI,  # Exact URI match
    name="Welcome Message",
    description="A static welcome message from the server.",
    mime_type="text/plain"
)
async def get_welcome_message() -> str:
    """Provides a static welcome message."""
    return "Hello from the MCP Resource Server! Welcome."

# --- Resource 2: Dynamic Current Server Time ---
SERVER_TIME_URI = "app:///system/time"


@mcp.resource(
    uri=SERVER_TIME_URI,
    name="Current Server Time",
    description="Provides the current date and time of the server.",
    mime_type="application/json"  # Example: returning as JSON
)
async def get_server_time() -> dict:
    """Provides the current server time as a JSON object."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "iso_timestamp": now.isoformat(),
        "pretty_time": now.strftime("%Y-%m-%d %H:%M:%S %Z")
    }


# --- Resource 3: Simulated Project File Content ---
# This demonstrates a slightly more complex URI and simulates file access.
# For actual file serving, consider security implications carefully (e.g., path traversal).


PROJECT_README_URI = "file:///project/docs/README.md"
SIMULATED_README_CONTENT = """
# My Project README

This is a simulated README file content provided as an MCP Resource.
It demonstrates how file-like resources can be exposed.

- Feature A
- Feature B
"""


@mcp.resource(
    uri=PROJECT_README_URI,
    name="Project README",
    description="Simulated content of the project's README.md file.",
    mime_type="text/markdown"
)
async def get_project_readme() -> str:
    """Provides the simulated content of a project README file."""
    print(f"[Server Log] Resource requested: {PROJECT_README_URI}")
    # In a real scenario, you would read this from an actual file:
    # with open("path/to/your/project/README.md", "r") as f:
    #     return f.read()
    return SIMULATED_README_CONTENT


```


### MCP Resource Operations

- **Listing Resources (`resources/list`):** Clients use this to discover available resources. `FastMCP` would typically gather information from registered resource providers to respond to this.
  - **Reference:** [MCP Specification - Listing Resources](https://modelcontextprotocol.io/specification/2025-03-26/server/resources#listing-resources)
- **Reading Resources (`resources/read`):** Clients request the content of a specific resource by its URI. `FastMCP` routes this to the appropriate registered Python function.
  - **Reference:** [MCP Specification - Reading Resources](https://modelcontextprotocol.io/specification/2025-03-26/server/resources#reading-resources)
- **Resource Templates (`resources/templates/list` - Advanced):** Allows servers to expose parameterized resources (e.g., `file:///{path}`).
  - **Reference:** [MCP Specification - Resource Templates](https://modelcontextprotocol.io/specification/2025-03-26/server/resources#resource-templates)
- **Subscriptions (`resources/subscribe` - Advanced):** Clients can subscribe to changes in a resource if the server supports it.
  - **Reference:** [MCP Specification - Subscriptions](https://modelcontextprotocol.io/specification/2025-03-26/server/resources#subscriptions)

### Basic Error Handling

Exceptions raised in your resource provider functions are generally caught by `FastMCP` and converted into structured MCP error responses (e.g., "Resource not found" - Code `-32002`).

- **Reference:** [MCP Specification - Error Handling](https://modelcontextprotocol.io/specification/2025-03-26/server/resources#error-handling)

### Security Considerations

- Servers **MUST** validate all resource URIs.
- Access controls **SHOULD** be implemented for sensitive resources.
- Resource permissions **SHOULD** be checked before operations.
- **Reference:** [MCP Specification - Security Considerations](https://modelcontextprotocol.io/specification/2025-03-26/server/resources#security-considerations)


## Key Takeaways

- MCP Resources provide essential context to AI agents by exposing data and information.
- Define resource providers as Python functions (often `async`) and register them with `FastMCP` using a decorator like `@mcp.resource()`, specifying a URI, name, description, and content type.
- URIs are crucial for uniquely identifying resources. Choose a scheme that makes sense for your data (e.g., `file:///`, `app:///`, or custom).
- Always specify the correct `content_type` (MIME type) for your resources.
- The `resources/list` operation allows clients to discover available resources, and `resources/read` allows them to fetch resource content.
- Test your resource server thoroughly using the MCP Inspector or other client tools.

## Next Steps

With an understanding of both MCP Tools and Resources, you are now equipped to build more sophisticated MCP servers that can both perform actions and access rich contextual information.

Consider exploring:

- **Advanced Resource Patterns:** Such as using URI templates for parameterized resources (e.g., `files/{category}/{id}`).
- **Resource Subscriptions:** For scenarios where clients need real-time updates when resource content changes (if your `FastMCP` version and application require it).
- **Integrating Resources with Tools:** Tools might consume resources to gather information before acting, or produce/update resources as part of their execution.

Exposing well-defined resources is key to providing rich, contextual information to AI agents, enabling them to generate more relevant and accurate responses.
