# 02: Defining Tools

**Objective:** Understand how to define and expose multiple tools with various data types using the `@mcp.tool()` decorator in `FastMCP`.

This lesson expands on our "Hello, World!" example by creating a server that offers a small suite of tools. This demonstrates how to build a capable and versatile MCP server that can handle different tasks.

## Key MCP Concepts

-   **`@mcp.tool()` Decorator:** We will explore this decorator further. `FastMCP` automatically inspects the decorated function's signature (parameter names, type hints like `int` and `str`) and its docstring to generate a complete and accurate tool schema for the client.
-   **Tool Schema:** The structured description of a tool, including its `name`, `description`, and a schema for its `parameters`. Clients use this to understand how to call the tool correctly.
-   **Type Safety:** `FastMCP` leverages Python's type hints to automatically validate incoming arguments for tool calls. If a client provides a string where an integer is expected, the server will automatically reject the request with a validation error.
-   **Synchronous and Asynchronous Tools:** `FastMCP` seamlessly supports both standard (`def`) and asynchronous (`async def`) functions as tools.

## Implementation Plan

Inside the `my_tools_server/` subdirectory:

-   **`server.py`:**
    -   We will define multiple functions, each decorated with `@mcp.tool()`.
    -   Examples will include:
        -   A simple calculator `add(a: int, b: int) -> int`.
        -   A string manipulation tool `greet(name: str) -> str`.
        -   The code will demonstrate clear docstrings and type hints, which are automatically used to build the tool schema.

-   **`client.py`:**
    -   The client will first call `tools/list` to discover all the available tools and print their descriptions.
    -   It will then demonstrate calling each tool with valid parameters and printing the results.
    -   We will also show an example of calling a tool with *invalid* parameters to see how the server's automatic validation responds.

-   **Postman Collection:**
    -   The `postman/` collection will be updated to include requests for listing tools and calling each new tool, along with examples of both successful calls and expected validation errors.

## Project Structure

```
02_defining_tools/
└── my_tools_server/
    ├── main.py         # The MCP server code
    └── call_mcp.py     # Our simple client to test the server
```

## 1. The Server Code (`main.py`)

This is the code that defines our tools. It's simple and clean.

```python
from mcp.server.fastmcp import FastMCP

# Initialize a stateless FastMCP server
mcp = FastMCP(name="my-tools-server")

# --- Tool 1: A simple calculator tool ---
@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds two integers together."""
    return a + b

# --- Tool 2: A simple greeter tool ---
@mcp.tool()
async def greet(name: str) -> str:
    """Provides a friendly greeting."""
    return f"Hello, {name}! Welcome to the world of MCP tools."

# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()
```

## 2. The Simplified Client (`call_mcp.py`)

This client shows how to talk to our server. We've made it extra simple, with comments explaining each step.

```python
# The full, simplified client code is in the call_mcp.py file.
# It contains a helper function to make requests and a main function
# that demonstrates the step-by-step process of using the server.
```

## 3. How to Run: A Step-by-Step Guide

You will need two separate terminals to see the client and server interact.

### **Terminal 1: Start the Server**

This terminal will run the `main.py` script, which waits for connections.

1.  **Navigate to the directory:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/02_defining_tools/my_tools_server
    ```
2.  **Install libraries:** (You only need to do this once)
    ```bash
    uv add httpx mcp uvicorn
    ```
3.  **Run the server:**
    ```bash
    uvicorn server:mcp_app --host 0.0.0.0 --port 8000
    ```

    You'll see output from `uvicorn` indicating the server is running. It is now waiting for a client to connect.

### **Terminal 2: Run the Client**

This terminal will run the `client.py` script, which sends requests to the server.

1.  **Navigate to the *same* directory as Terminal 1:**
    ```bash
    cd 03_ai_protocols/02_model_context_protocol/01_server_development/02_defining_tools/my_tools_server
    ```
2.  **Run the client:**
    ```bash
    uv run python client.py
    ```

## 4. What Happens When You Run the Client

The client will print a step-by-step explanation of what it's doing. This is the **Expected Output** in Terminal 2:

```
--- MCP Tool Client Demonstration for Students ---

[Step 1: Discovering Tools]
We ask the server what tools it has with a 'tools/list' request.
   -> Sending tools/list request...
   -> Success! Server has 2 tools:
      - add: Adds two integers together.
      - greet: Provides a friendly greeting.

[Step 2: Calling the 'add' tool]
Now, we'll call the 'add' tool with numbers 5 and 7.
   -> Sending tools/call request...
   -> Success! The server returned the result: '12'

[Step 3: Calling the 'greet' tool]
Finally, we'll call the 'greet' tool with the name 'Student'.
   -> Sending tools/call request...
   -> Success! The server returned the greeting: 'Hello, Student! Welcome to the world of MCP tools.'
```

This example shows the fundamental pattern of MCP: a client discovers what a server can do (`tools/list`) and then asks it to perform an action (`tools/call`).

## 5. Testing with Postman

For a more interactive testing experience, we've included a comprehensive Postman collection in the `postman/` directory:

- **Collection**: `MCP_Defining_Tools.postman_collection.json`
- **Documentation**: `postman/README.md`

The Postman collection includes:
- Tool discovery requests
- Multiple test scenarios for both `add` and `greet` tools
- Error handling examples
- Parameter validation tests

This provides an excellent way to experiment with the server and understand how MCP tools work without writing code.