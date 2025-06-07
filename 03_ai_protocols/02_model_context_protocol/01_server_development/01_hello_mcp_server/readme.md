# 01: Hello, MCP Server!

The FastMCP server is your core interface to the MCP protocol. It handles connection management, protocol compliance, and message routing:

**Objective:** Get your first, very basic Model Context Protocol (MCP) server up and running using the `FastMCP` library from the `modelcontextprotocol python sdk`.

This initial step focuses on the bare essentials: setting up the server, making it runnable, and understanding how it participates in the most fundamental part of the MCP lifecycle—the initialization handshake.

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

      uv add "mcp[cli]"
      ```

    - Test MCP CLI

    ```bash
    uv run mcp --help
    ```

    Output:

    ```bash
    Usage: mcp [OPTIONS] COMMAND [ARGS]...

    MCP development tools

    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ --help          Show this message and exit.                                                                      │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ version   Show the MCP version.                                                                                  │
    │ dev       Run a MCP server with the MCP Inspector.                                                               │
    │ run       Run a MCP server.                                                                                      │
    │ install   Install a MCP server in the Claude desktop app.                                                        │
    ╰───────────────────────────────────────────
    ```

3.  Update (`main.py`):

    - We will import `FastMCP` and create a simple tool

    ```python
    from mcp.server.fastmcp import FastMCP

    # Initialize FastMCP server
    mcp = FastMCP("weather")

    @mcp.tool()
    async def get_forecast(city: str) -> str:
        """Get weather forecast for a city.

        Args:
            city(str): The name of the city
        """
        return f"The weather in {city} will be warm and sunny"
    ```

4.  **Run the Server:**

    - Execute the command:

      ```bash
      uv run mcp dev main.py
      ```

    - This will start:
      - MCP server at: http://localhost:6277
      - MCP Inspector: http://127.0.0.1:6274

5.  **Verification:**
    - At this stage, the server will be running. It won't do much yet, but it will be capable of responding to an MCP `initialize` request.
    - Open MCP Inspector i.e: http://127.0.0.1:6274 in browser and try it out.
      - Open the url in browser: http://localhost:5173
      - Select Tools Tab and list and run the tool.

This "Hello, MCP Server!" example lays the groundwork. In subsequent sections, we'll build upon this to add tools, resources, and prompt templates, making our server progressively more useful to AI agents.

## Optional Client Integration Exercise (We will not cover in class)

Install [Claude Desktop](https://claude.ai/download)

You can install this weather server in Claude Desktop and interact with it right away by running:

    mcp install main.py

If you are a Mac user facing the error to integrate MCP with Claude desktop, then the chat below will help you. [ChatGPT 03](https://chatgpt.com/share/67c64692-9374-8007-bedc-ca1cde76c95e)
