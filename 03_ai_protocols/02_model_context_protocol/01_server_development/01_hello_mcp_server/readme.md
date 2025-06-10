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

      uv add mcp uvicorn
      ```

3.  Update (`main.py`):

    - We will import `FastMCP` and create a simple tool with stateless http protocol

```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather", stateless_http=True)


@mcp.tool()  # Using this mcp instance
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.

    Args:
        city(str): The name of the city
    """
    return f"The weather in {city} will be warm and sunny"

mcp_stateless = mcp.streamable_http_app()
```

4.  **Run the Server:**

    - Execute the command:

      ```bash
      uv run uvicorn main:mcp_stateless --port 8000 --reload
      ```

    - This will start:
      - MCP server at: http://localhost:8000
      

5.  **Run MCP Client:**
    We have a simple HTTP client in python

    ```bash
    uv run python 
    ```

    We can use MCP inspector to test our MCP Server

    ```bash
    npx @modelcontextprotocol/inspector
    ```
    
    - MCP Inspector: http://127.0.0.1:6274

    - At this stage, the server will be running. It won't do much yet, but it will be capable of responding to an MCP `initialize` request.
    - Open MCP Inspector i.e: http://127.0.0.1:6274 in browser and try it out. 
      - Select Tools Tab and list and run the tool.

This "Hello, MCP Server!" example lays the groundwork. In subsequent sections, we'll build upon this to add tools, resources, and prompt templates, making our server progressively more useful to AI agents.