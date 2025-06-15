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
      uv run uvicorn server:mcp_stateless --port 8000 --reload
      ```

    - This will start:
      - MCP server at: http://localhost:8000
      

5.  **Test the MCP Server:**
    
    **Option 1: Python Client (Programmatic)**
    ```bash
    uv run python client.py
    ```

    **Option 2: Postman (Visual & Educational) - RECOMMENDED FOR LEARNING**
    1. Install Postman from [postman.com](https://www.postman.com/downloads/)
    2. Import the collection: `postman/Hello_MCP_Server.postman_collection.json`
    3. Run requests in sequence to understand MCP protocol
    4. See detailed documentation in `postman/README.md`

    **Option 3: MCP Inspector (Interactive)**
    ```bash
    npx @modelcontextprotocol/inspector
    ```
    - Run and Open MCP Inspector at: http://127.0.0.1:6274
    - Select Tools Tab and list and run the tool

## 🎓 Why Use Postman for Learning?

**Postman provides the best educational experience** because it:
- **Visualizes the Protocol**: See raw JSON-RPC requests and responses
- **Hands-on Learning**: Modify parameters and experiment easily
- **Better Debugging**: Clear error messages and response inspection
- **No Coding Required**: Focus on understanding MCP without Python complexity
- **Shareable**: Export collections to share with classmates/students

**Learning Path**:
1. Start with Postman to understand the protocol
2. Move to Python client to see programmatic usage
3. Use MCP Inspector for debugging later and testing

This "Hello, MCP Server!" example lays the groundwork. In subsequent sections, we'll build upon this to add tools, resources, and prompt templates, making our server progressively more useful to AI agents.

## 🔗 Next Steps

- **02_adding_resources**: Learn to provide contextual data to AI agents
- **03_prompt_templates**: Create reusable prompt templates
- **04_error_handling**: Handle errors gracefully
- **05_server_initialization**: Deep dive into MCP connection lifecycle and initialization handshake

For detailed understanding of the MCP initialization process, protocol version negotiation, and capability management, see the `05_server_initialization` example.