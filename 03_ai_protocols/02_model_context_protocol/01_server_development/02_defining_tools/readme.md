# 02: Defining MCP Tools

**Objective:** Understand how to define and expose multiple tools using the `FastMCP` server.

This tutorial focuses on the core concept of creating tools that an AI agent can discover and execute. We will build a simple server that offers a basic calculator and a greeter, and then use a simple client to interact with them, explaining each step along the way.

## Key Concepts for Students

- **`@mcp.tool()` decorator:** This is like putting a "Use Me" sign on a Python function. `FastMCP` sees this sign and automatically tells any connected AI about the function: its name, what arguments it needs (from your type hints like `a: int`), and what it does (from your docstring).
- **Stateless Server:** Think of the server as having no memory. Each time you call a tool, it's a fresh start. This makes the server simple and reliable.
- **Client/Server:** The "Server" (`main.py`) is a program that waits for requests. The "Client" (`call_mcp.py`) is a program that sends requests. They talk to each other over HTTP, just like your web browser talks to a website.

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