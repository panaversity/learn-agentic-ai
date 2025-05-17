# 02: Understanding [MCP's Streamable HTTP Transport](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http)

**Supersedes HTTP+SSE:** Streamable HTTP is the recommended transport for production MCP deployments, replacing the older HTTP+SSE transport (from protocol version 2024-11-05).

**Objective:** This guide will walk you through creating a simple Python MCP **server** that communicates over Streamable HTTP, and then a Python MCP **client** to interact with it. We'll use the `mcp` Python SDK for both. This will help you understand the fundamentals of networked MCP communication. Later, these concepts can be applied when integrating MCP with agentic engines like the OpenAI Agents SDK.

## What is Streamable HTTP in MCP? (High-Level Overview)

Imagine you have two programs that need to talk to each other over a network (like the internet or your local computer network). One is an **MCP Server** (it offers services like tools or data), and the other is an **MCP Client** (it wants to use those services).

Streamable HTTP is a standardized way for them to have this conversation.

- It uses common web technologies: HTTP POST (client sends a message) and HTTP GET (client asks to listen for server messages).
- The server runs as a separate program, waiting for clients to connect.
- It's "streamable" because it can efficiently handle ongoing interactions, making it feel like a continuous connection even though it's using HTTP.
- This is different from `stdio` transport, which is simpler and usually for processes running on the same machine. Streamable HTTP is built for networked applications.

For all the precise details, you can always refer to the [Official MCP Specification for Streamable HTTP Transport](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http).

## Part 1: Building the MCP HTTP Server

Let's start by creating a server. Our server will offer a simple "greet" tool, a welcome message resource, a user profile resource template, and a simple question prompt template.

### Key Server Concepts

1.  **`FastMCP`:** This is the main class from the `mcp` Python SDK that we use to create our server application. We'll define our tools, resources, and prompts on an instance of this class.
2.  **`@mcp.tool()` Decorator:** A special marker we put on a Python function to tell `FastMCP` that this function should be exposed as a callable tool to clients.
3.  **`@mcp.resource()` Decorator:** Similar to tools, this marks a function that provides data (a resource) to clients. It can define a static URI or a URI template for dynamic resources.
4.  **`@mcp.prompt()` Decorator:** This marks a function that generates prompt messages, often used to guide LLM interactions.
5.  **Running the Server with `mcp_app.run()`:** The `FastMCP` object has a built-in `run()` method that can start an HTTP server for us. This is convenient for these examples.
    - _(Alternative for more control: `FastMCP` is also an ASGI application, meaning it can be run by more advanced ASGI servers like Uvicorn. For simplicity now, we will use `mcp_app.run()` which internally uses an ASGI server like Hypercorn by default for HTTP. We will learn about this after learning to connect MCP servers with Agentic Engines like OpenAI Agents SDK.)_
6.  **The MCP Endpoint:** When our server runs, it makes its MCP services available at a specific URL path, typically `/mcp` on the host and port it's running on (e.g., `http://localhost:8000/mcp`).

### Server Project Setup & Dependencies

1.  **Create Project Directories:**
    It's good practice to have separate directories for your server and client code. We assume you are in the `02_mcp_over_http` main project directory.

    ```bash
    uv init client
    uv init server
    cd server
    uv venv # This creates a virtual environment .venv
    source .venv/bin/activate # On Linux/macOS
    # .venv\Scripts\activate # On Windows
    ```

3.  **Install `mcp` SDK for the Server (in its environment):**
    Make sure you are in the `02_mcp_over_http/server` directory or specify the `pyproject.toml` path for `uv`.
    ```bash
    # Assuming you are in 02_mcp_over_http/server:
    uv add "mcp[cli]"
    ```

### Server Code (`02_mcp_over_http/server/main.py`)

Create a file named `main.py` inside your `02_mcp_over_http/server` directory:

```python
# 02_mcp_over_http/server/main.py
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent # For prompt templates

# 1. Initialize FastMCP
# We're making it stateless and enabling json_response optimization
mcp_app = FastMCP(
    name="my-simple-http-server",
    description="A basic MCP server for HTTP client demonstration.",
    stateless_http=True,      # Makes the server treat each HTTP request independently
    json_response=True,       # Allows single JSON responses for non-streaming calls (optimization)
)

# 2. Define a simple tool
@mcp_app.tool()
def greet(name: str = "World") -> str:
    """Returns a greeting message."""
    print(f"[Server Log] greet tool called with name: {name}")
    return f"Hello, {name} from the MCP HTTP server!"

# 3. Define a simple static resource
APP_WELCOME_MSG_URI = "app:///messages/welcome" # URI for this specific resource
@mcp_app.resource(
    uri=APP_WELCOME_MSG_URI, # Register with this exact URI
    name="Welcome Message",
    description="A static welcome message from the server.",
    mime_type="text/plain"
)
async def get_welcome_message_resource() -> str:
    """Provides a static welcome message."""
    print(f"[Server Log] Welcome resource ('{APP_WELCOME_MSG_URI}') requested.")
    return "This is a welcome resource from the HTTP server!"

# 4. Define a resource template (parameterized URI)
@mcp_app.resource("users://{user_id}/profile") # URI template
async def get_user_profile(user_id: str) -> str:
    """Provides dynamic profile data for a given user ID."""
    print(f"[Server Log] User profile requested for user_id: {user_id}")
    return f"Profile data for user {user_id}"

# 5. Define a simple prompt template
@mcp_app.prompt(
    name="simple_question",
    description="Generates a prompt asking a simple question."
)
async def simple_question_prompt(entity: str = "the sky") -> list[PromptMessage]:
    """Generates a prompt asking why something is a certain color."""
    print(f"[Server Log] simple_question prompt requested for entity: {entity}")
    return [
        PromptMessage(
            role="user",
            content=TextContent(text=f"Why is {entity} blue?", type="text")
        )
    ]

# 6. Make the server runnable
if __name__ == "__main__":
    print(f"Starting MCP server '{mcp_app.name}'...")
    # This uses the built-in server runner from the MCP SDK.
    mcp_app.run(transport="streamable-http")

```

**Explanation of `server/main.py`:**

- We initialize `FastMCP`. The `stateless_http=True` and `json_response=True` settings configure it for efficient, stateless handling of simple requests.
- `@mcp_app.tool()` exposes the `greet` function as a tool.
- `@mcp_app.resource(...)` exposes `get_welcome_message_resource` at the fixed URI `app:///messages/welcome` and `get_user_profile` as a template at `users://{user_id}/profile`.
- `@mcp_app.prompt()` exposes `simple_question_prompt` as a prompt template.
- The `if __name__ == "__main__": ... mcp_app.run(...)` block makes the script directly executable. It starts an HTTP server (usually Hypercorn via the SDK) listening on `http://localhost:8000`, with the MCP services available at the `/mcp` path.

### Running the Server

1.  Ensure your terminal is in the `02_mcp_over_http/server` directory and the server's virtual environment (`.venv`) is activated.
2.  Run the server script:
    ```bash
    python main.py
    ```
    You should see output like: `Starting MCP server 'my-simple-http-server' on http://localhost:8000/mcp ...`
    The server is now running. Keep this terminal window open.

## Part 2: Building the MCP HTTP Client

With the server running, let's create a client to interact with it.

### Key Client Concepts

1.  **`streamablehttp_client`:** This function from `mcp.client.streamable_http` is what the client uses to make the initial HTTP connection to our server's MCP endpoint (e.g., `http://localhost:8000/mcp`).
2.  **`ClientSession`:** After `streamablehttp_client` connects, it provides communication streams. We wrap these with a `ClientSession` object from the `mcp` SDK. This session object handles the MCP-specific protocol details, like formatting requests and parsing responses.
3.  **`session.initialize()`:** This is the mandatory first step after creating a `ClientSession`. It's a handshake where the client and server exchange initial information (like server name, version, and capabilities).
4.  **Session Methods (e.g., `session.call_tool()`):** The `ClientSession` object provides methods for all standard MCP operations. For example, `session.call_tool("greet", ...)` tells the client to send an MCP `tools/call` request to the server to execute the "greet" tool.

### Client Project Setup & Dependencies

1.  **Navigate to Client Directory and Setup Environment:**
    Open a **new, separate terminal window**. Navigate from your project root `02_mcp_over_http` into the `client` directory.

    ```bash
    cd client
   uv venv
    source .venv/bin/activate # On Linux/macOS
    # .venv\Scripts\activate # On Windows
    ```

2.  **Install `mcp` SDK for the Client:**
    Ensure you are in the `02_mcp_over_http/client` directory for this command or specify pyproject.toml path for uv.
    ```bash
    # Assuming you are in 02_mcp_over_http/client:
    uv add "mcp[cli]"
    ```

### Client Code (`02_mcp_over_http/client/main.py`)

Create a file named `main.py` inside your `02_mcp_over_http/client` directory:

```python
# client/main.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Define the MCP server endpoint URL
SERVER_MCP_ENDPOINT_URL = "http://localhost:8000/mcp"

# WELCOME_MSG_URI for client-side checks, must match server definition
WELCOME_MSG_URI = "app:///messages/welcome"


async def run_http_client():
    print(
        f"Starting MCP HTTP client to connect to {SERVER_MCP_ENDPOINT_URL}...")
    try:
        async with streamablehttp_client(SERVER_MCP_ENDPOINT_URL) as (read_stream, write_stream, _):
            print("Streamable HTTP client connected to server.")
            async with ClientSession(read_stream, write_stream, sampling_callback=None) as session:
                print("ClientSession created. Initializing...")
                init_response = await session.initialize()
                print(
                    f"Initialization successful. Server: {init_response.serverInfo.name} v{init_response.serverInfo.version}")
                print(f"Server Capabilities: {init_response.capabilities}")
                print("-" * 30)

                # 1. List and Call a Tool
                print("Listing tools...")
                tools = await session.list_tools()
                if not tools.tools:
                    print("No tools found on server.")
                else:
                    print(
                        f"Available tools: {[tool.name for tool in tools.tools]}")
                    greet_tool_info = next(
                        (t for t in tools.tools if t.name == "greet"), None)
                    if greet_tool_info:
                        print("\nCalling 'greet' tool with default param...")
                        result_default = await session.call_tool("greet")
                        print(f"Tool 'greet' (default) responded: {result_default.content[0].text}")

                        print("\nCalling 'greet' tool with param 'User'...")
                        result_user = await session.call_tool("greet", arguments={"name": "User"})
                        print(
                            f"Tool 'greet' ('User') responded: {result_user.content[0].text}")
                    else:
                        print("Tool 'greet' not found.")
                print("-" * 30)

                # 2. List and Read a Resource
                print("Listing resources...")
                resources_list = await session.list_resources()
                if not resources_list.resources:
                    print("No resources found on server.")
                else:
                    print(
                        f"Available resources (names only): {[res.name for res in resources_list.resources if res.name]}")

                    # Find the resource by its URI, ensuring URI is treated as a string for comparison
                    welcome_res_info = next(
                        (r for r in resources_list.resources if r.uri and str(
                            r.uri) == WELCOME_MSG_URI),
                        None
                    )

                    if welcome_res_info:
                        # Ensure URI is treated as string for display/use if it's an AnyUrl object
                        display_uri = str(
                            welcome_res_info.uri) if welcome_res_info.uri else "N/A"
                        print(
                            f"\nReading resource: {welcome_res_info.name} ({display_uri})...")

                        # Use the client-side WELCOME_MSG_URI for reading, as it's a confirmed string.
                        # Alternatively, could use str(welcome_res_info.uri) if confident it's always populated.
                        resource_data = await session.read_resource(WELCOME_MSG_URI)

                        if resource_data.contents and hasattr(resource_data.contents[0], 'text'):
                            print(
                                f"Resource content: {resource_data.contents[0].text}")
                            print(
                                f"Resource MIME type: {resource_data.contents[0].mimeType}")
                        else:
                            print(
                                f"Could not read or parse text content from {WELCOME_MSG_URI}")
                    else:
                        print(
                            f"Resource with URI '{WELCOME_MSG_URI}' not found in the listed resources.")
                print("-" * 30)

                # 3. List and Get a Prompt
                print("Listing prompts...")
                prompts_list = await session.list_prompts()
                if not prompts_list.prompts:
                    print("No prompts found on server.")
                else:
                    print(
                        f"Available prompts: {[p.name for p in prompts_list.prompts]}")
                    simple_question_prompt_info = next(
                        (p for p in prompts_list.prompts if p.name == "simple_question"), None)

                    if simple_question_prompt_info:
                        print(
                            "\nGetting 'simple_question' prompt with default param...")
                        prompt_response_default = await session.get_prompt("simple_question")
                        print(
                            f"Prompt 'simple_question' (default) messages: {prompt_response_default.messages}")

                        print(
                            "\nGetting 'simple_question' prompt with entity 'the moon'...")
                        prompt_response_moon = await session.get_prompt("simple_question", arguments={"entity": "the moon"})
                        print(
                            f"Prompt 'simple_question' ('the moon') messages: {prompt_response_moon.messages}")
                    else:
                        print("Prompt 'simple_question' not found.")

                print("-" * 30)
                print("HTTP Client operations complete.")

    except ConnectionRefusedError:
        print(
            f"Error: Connection refused. Ensure the MCP server is running at {SERVER_MCP_ENDPOINT_URL}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_http_client())
```

**Explanation of `client/main.py` (Simplified):**

- **Connects to Server:** `streamablehttp_client(SERVER_MCP_ENDPOINT_URL)` makes the network connection.
- **Starts MCP Session:** `ClientSession(...)` and then `session.initialize()` perform the MCP handshake.
- **Using Tools:**
  - `session.list_tools()`: Asks the server, "What tools can you do?"
  - `session.call_tool("greet", ...)`: Tells the server, "Run your 'greet' tool with these arguments (or defaults)."
- **Using Resources:**
  - `session.list_resources()`: Asks the server, "What data resources do you have?"
  - `session.read_resource("app:///messages/welcome")`: Asks, "Give me the content of the resource at this specific URI."
- **Using Prompts:**
  - `session.list_prompts()`: Asks, "What prompt templates do you offer?"
  - `session.get_prompt("simple_question", ...)`: Asks, "Prepare your 'simple_question' prompt template using these arguments."
- **Async/Await:** The `async` and `await` keywords are used because network operations can take time, and this allows the program to do other things while waiting, making it efficient.

### Running the Client

1.  Ensure your MCP server (`02_mcp_over_http/server/main.py`) is running in its terminal.
2.  In your second terminal, ensure you are in the `02_mcp_over_http/client` directory and its virtual environment is activated.
3.  Run the client script:
    ```bash
    python main.py
    ```

### Expected Client Output (Example)

You should see output similar to the following (the server version might differ slightly):

```bash
Starting MCP HTTP client to connect to http://localhost:8000/mcp...
Streamable HTTP client connected to server.
ClientSession created. Initializing...
Initialization successful. Server: my-simple-http-server v1.9.0
Server Capabilities: experimental={} logging=None prompts=PromptsCapability(listChanged=False) resources=ResourcesCapability(subscribe=False, listChanged=False) tools=ToolsCapability(listChanged=False)
------------------------------
Listing tools...
Available tools: ['greet']

Calling 'greet' tool with default param...
Tool 'greet' (default) responded: Hello, World from the MCP HTTP server!

Calling 'greet' tool with param 'User'...
Tool 'greet' ('User') responded: Hello, User from the MCP HTTP server!
------------------------------
Listing resources...
Available resources (names only): ['Welcome Message']

Reading resource: Welcome Message (app:///messages/welcome)...
Resource content: This is a welcome resource from the HTTP server!
Resource MIME type: text/plain
------------------------------
Listing prompts...
Available prompts: ['simple_question']

Getting 'simple_question' prompt with default param...
Prompt 'simple_question' (default) messages: [PromptMessage(role='user', content=TextContent(type='text', text='{\n  "role": "user",\n  "content": {\n    "type": "text",\n    "text": "Why is the sky blue?",\n    "annotations": null\n  }\n}', annotations=None))]

Getting 'simple_question' prompt with entity 'the moon'...
Prompt 'simple_question' ('the moon') messages: [PromptMessage(role='user', content=TextContent(type='text', text='{\n  "role": "user",\n  "content": {\n    "type": "text",\n    "text": "Why is the moon blue?",\n    "annotations": null\n  }\n}', annotations=None))]
------------------------------
HTTP Client operations complete.
```

_(You should also see corresponding `[Server Log]` messages appearing in your running server's terminal window.)_

## How Streamable HTTP Works (A Bit More Detail)

Now that you've seen a client and server communicate, let's briefly touch on what happens "under the hood" with Streamable HTTP for the operations our client performed:

1.  **Client Sends a Request (e.g., `tools/call` for `greet`):**

    - Your `client/main.py` calls `await session.call_tool(...)`.
    - The `ClientSession` and `streamablehttp_client` work together to send an HTTP **POST** request to `http://localhost:8000/mcp`.
    - The body of this POST request is a JSON-RPC message asking to execute the "greet" tool.
    - The client includes an `Accept` header saying it can understand `application/json` or `text/event-stream` (the SDK handles this).

2.  **Server Receives and Responds:**

    - Your `server/main.py` (running via `mcp_app.run()`) receives this POST request.
    - `FastMCP` routes it to your `greet` function.
    - Since `greet` is a simple function that returns a string immediately (and we set `json_response=True` on the server), `FastMCP` sends back a single HTTP response with `Content-Type: application/json`. The body is a JSON-RPC response containing the "Hello, World..." string.

3.  **Client Receives Response:**
    - `streamablehttp_client` gets this HTTP response.
    - `ClientSession` parses the JSON-RPC response and gives the result back to your `await session.call_tool(...)` line.

This is a simplified view. If the tool involved streaming data back or if the server needed to send multiple messages, it would use `Content-Type: text/event-stream` and Server-Sent Events (SSE), making the "streamable" part more apparent. Our `json_response=True` server optimization handles simple cases efficiently.

_(The MCP specification link provided earlier has full diagrams and details if you're curious about the deeper protocol interactions for SSE, GET requests for server-to-client streams, etc.)_

## Server State: Stateful vs. Stateless (Important!)

When you initialize `FastMCP` in `server/main.py`, you have choices that affect how it handles "state" (memory of past interactions).

```python
# Stateful (Default, if you omit stateless_http and json_response):
# app = FastMCP("MyStatefulServer")

# Our Example - Stateless and Optimized:
mcp_app = FastMCP(
    name="my-simple-http-server",
    stateless_http=True,
    json_response=True
)
```

1.  **Stateful Server (e.g., `app = FastMCP("MyStatefulServer")`)**

    - This is the default if you don't specify `stateless_http`.
    - The server _tries_ to remember things about a particular client's session (e.g., results of previous tool calls, if designed to do so).
    - Useful for conversations or multi-step tasks where context needs to be carried over _by the server_.

2.  **Stateless Server (`stateless_http=True`)**

    - This tells `FastMCP` to treat **every HTTP request as independent.** It doesn't try to remember anything about prior requests from the same client at the HTTP transport level.
    - **Why use it?**
      - **Scalability:** If any server instance can handle any request without needing prior context stored _on that specific instance_, it's much easier to distribute load across many server machines.
      - **Simplicity:** For services where each request is self-contained.
    - **Managing State (If Needed):** If your _application_ still needs state (e.g., who the user is), you'd typically pass necessary identifiers in each request, and the server logic would fetch context from a shared database or cache.

3.  **JSON Response Optimization (`json_response=True`)**
    - This is an **optimization specifically for `stateless_http=True` servers.**
    - If a request (like our `greet` tool call) can be answered with a single, immediate JSON response (no streaming, no partial results), the server sends it directly as `application/json`.
    - **Benefit:** Avoids the small overhead of setting up a full Server-Sent Event (SSE) stream for simple cases, making it faster.
    - If the operation _did_ need streaming, `FastMCP` would still correctly use SSE.

For our simple example, `stateless_http=True` and `json_response=True` make the server very efficient. For more complex agents that need to remember conversation history, a stateful approach (or stateless with external state management) would be chosen.

## Key Protocol Rules & Considerations for Streamable HTTP

(These are simplified from the official MCP specification for quick understanding)

- **Single MCP Endpoint:** The server has one main URL path (e.g., `/mcp`) for all MCP communication.
- **Client POSTs Messages:** Clients always send their JSON-RPC messages (requests, notifications) to the server using an HTTP POST to this endpoint.
- **`Accept` Header is Key:** The client's POST must tell the server what kind of responses it can handle (typically `application/json` and `text/event-stream`). The SDK usually handles this header.
- **Server Response Types (Simplified):**
  - For simple, non-streaming requests on a stateless server with `json_response=True`: Server likely sends `application/json`.
  - For streaming, or if `json_response=False`, or for stateful interactions needing multiple messages: Server likely sends `text/event-stream`.
  - For client messages that are purely informational (notifications/responses only): Server sends HTTP 202 Accepted.
- **Client GET for Server-to-Client Stream (Optional/Advanced):** A client can make an HTTP GET to the MCP endpoint (accepting `text/event-stream`) to open a channel for the server to proactively send messages to the client. Our example doesn't use this, but it's part of the protocol for more advanced scenarios.

## Essential Security Considerations (from MCP Specification)

When you build real MCP servers that might be exposed to a network, these are critical:

1.  **Origin Validation:** Servers **MUST** check the `Origin` header on requests to prevent certain web attacks (DNS rebinding).
2.  **Localhost Binding (for local development):** When running a server just on your machine for testing, it **SHOULD** only listen on `localhost` (127.0.0.1), not all network interfaces (`0.0.0.0`), for safety. Our `mcp_app.run(host="localhost", ...)` command does this.
3.  **Authentication:** Real servers **SHOULD** have a way to verify who the client is (authentication) before allowing access to tools or resources. (Our simple example skips this for brevity).

## Session Management (Brief Introduction)

Even if a server is `stateless_http=True` at the transport layer, applications often need a way to link a series of requests from the same client into a logical "session."

- A server can give a client an `Mcp-Session-Id` (a unique string) in an HTTP header when a session starts (usually in the response to the `initialize` request).
- The client then **MUST** send this `Mcp-Session-Id` back in the headers of all its later requests for that logical session.
- This helps the overall application (which might include load balancers or separate state stores) to associate related requests. The `FastMCP` server itself, if `stateless_http=True`, won't use this ID to look up internal state, but the application logic running on top of it might use it to retrieve state from an external database or cache.

## Key Takeaways

- Streamable HTTP is MCP's way of enabling robust, networked communication.
- You build an MCP server using `FastMCP`, defining tools, resources, and prompts with decorators.
- You run the server (e.g., using `mcp_app.run()` for simplicity, or an ASGI server like Uvicorn for more control in production).
- MCP clients use `streamablehttp_client` to establish a connection and `ClientSession` to manage the MCP protocol (initialize, call tools, read resources, etc.).
- Server configuration choices like `stateless_http` and `json_response` are important for designing scalable and efficient services.
- Always consider security and how session context (if needed) will be managed in real-world applications.

## Next Steps

Now that you have a foundational understanding of MCP client-server communication over Streamable HTTP:

- You could explore more **advanced MCP server features** like:
  - Tools that stream partial results (if the Python SDK has clear support for this).
  - More complex resource definitions or subscriptions.
  - Lifespan events for managing server-wide resources (e.g., database connections) using `@asynccontextmanager` with `FastMCP(lifespan=...)`.
- Begin sketching out a simple application that utilizes an MCP server as part of a larger DACA-inspired system.
