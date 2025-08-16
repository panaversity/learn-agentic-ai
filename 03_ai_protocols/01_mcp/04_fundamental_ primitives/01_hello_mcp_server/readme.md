# 01: Hello, MCP Server!

**Objective:** Get your first, very basic Model Context Protocol (MCP) server running using the `FastMCP` library in **stateless** mode.

### 🌐 MCP vs. What You Might Know

| **If you know...** | **MCP is like...** | **Key difference** |
|-------------------|-------------------|-------------------|
| **REST APIs** | A standard protocol, but for AI-tool communication | Designed specifically for AI interactions |
| **OpenAI Function Calling** | Function calling that works with any AI model | Universal, not tied to one provider |
| **Webhooks** | Two-way communication between AI and external systems | Structured specifically for AI use cases |
| **Plugin Systems** | A plugin system for AI models | Cross-platform and standardized |

This initial step focuses on the bare essentials:
1.  Creating a server that handles each request independently.
2.  Making the server accessible over Stateless Streamable HTTP.
3.  Interacting with it using a spec-compliant client that correctly performs the `initialize` handshake.

This serves as the "Hello, World!" for MCP development. It provides the simplest possible server configuration while teaching the correct client-side interaction flow.

## Key MCP Concepts

-   **`FastMCP` Server:** A Python library that handles the low-level details of the MCP `2025-06-18` specification.
-   **Stateless HTTP Transport (`stateless_http=True`):** A convenience mode in `FastMCP` where the server treats every request as a new, independent interaction. It handles and then immediately forgets the session, which is perfect for learning the basic request-response pattern without managing persistent state.

## Implementation Plan

Inside the `hello-mcp/` subdirectory, we will:

-   **`server.py`:**
    -   Instantiate a `FastMCP` server in stateless mode (`stateless_http=True`).
    -   Expose the server as a runnable ASGI application for `uvicorn`.

-   **`client.py`:**
    -   A simple Python script that uses `httpx` to make JSON-RPC requests.
    -   It will first call `initialize` to follow the spec.

-   **Postman Collection:**
    -   The `postman/` directory contains a collection to demonstrate the spec-compliant, three-step interaction flow visually.

## Key Concepts

- **`FastMCP`:** A Python library designed to simplify the creation of MCP-compliant servers. It handles much of the underlying MCP protocol complexities, allowing you to focus on defining your server's capabilities.
- **Server Instantiation:** Creating an instance of the `FastMCP` application.
- **Server Metadata:** Providing basic information about your server (like its name and version) that it will share with clients during initialization.

## Steps

1.  **Setup:**

    - Ensure you have Python installed (Python 3.12+ recommended)and uv.

    ```bash
    uv init hello-mcp
    cd hello-mcp
    ```

2.  **Installation:**

    - Install the necessary packages using `uv`:

      ```bash
      uv add mcp httpx
      ```

3.  Update (`server.py`):

    - We will import `FastMCP` and create a simple tool with the stateless http protocol.

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Initialize FastMCP server with enhanced metadata for 2025-06-18 spec
mcp = FastMCP(
    name="hello-server",
    stateless_http=True
)


mcp_app = mcp.streamable_http_app()
```

4.  **Run the Server:**

    - Execute the command:

      ```bash
      uv run uvicorn server:mcp_app --port 8000 --reload
      ```

    - This will start:
      - MCP server at: http://localhost:8000
      

5.  **Test the MCP Server:**

    **Option 1: Postman (Visual & Educational) - RECOMMENDED FOR LEARNING**
    1. Install Postman from [postman.com](https://www.postman.com/downloads/)
    2. Import the collection: `postman/Hello_MCP_Server.postman_collection.json`
    3. Run requests in sequence to understand MCP protocol
    4. See detailed documentation in `postman/README.md`

    **Option 2: MCP Inspector (Interactive)**
    ```bash
    npx @modelcontextprotocol/inspector
    ```
    - Run and Open MCP Inspector at: http://127.0.0.1:6274

    
    **Option 3: Python Client (Programmatic)**
    ```bash
    uv run python client.py
    ```

## 🔗 Next Steps

- **02_project_setup**: Start with the MCP Introduction Course.
