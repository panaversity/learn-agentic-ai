# Sub-module 01: Connecting to an MCP Server (Streamable HTTP)

**Objective:** To demonstrate the basic configuration and connection of an OpenAI Agent to an MCP server that uses the `streamable-http` transport, utilizing the `MCPServerStreamableHttp` client class from the OpenAI Agents SDK.

## Core Concept

The primary goal here is to show an `Agent` being initialized with an `MCPServerStreamableHttp` instance. This instance acts as a client that points to a running MCP server. We want to confirm that the agent, upon initialization or when it first needs to interact with MCP tools, attempts to connect to this server. A common first interaction is for the agent (or the SDK on its behalf) to call `list_tools()` on the MCP server.

## Key SDK Concepts:

- `MCPServerStreamableHttpParams`: For configuring connection details to a `streamable-http` MCP server.
- `MCPServerStreamableHttp`: The client class in the SDK for interacting with such servers.
- `Agent(mcp_servers=[...])`: How to make an agent aware of MCP servers.
- `mcp_server_client.list_tools()`: Directly invoking tool listing (also done implicitly by the Agent).
- Asynchronous Context Management (`async with`) for `MCPServerStreamableHttp`.
- Using `Runner.run()` to execute an agent with a query.

## Setup

### 1. Run the Shared MCP Server

For this and subsequent examples in module `06_openai_agents_sdk_integration`, we will use a shared, standalone MCP server. This server is designed to be simple and provide a consistent target for our agent examples.

- **Location:** `03_ai_protocols/01_mcp/06_openai_agents_sdk_integration/shared_mcp_server/server.py`
- **To Run:**
  1.  Open a new terminal.
  2.  Navigate to the `shared_mcp_server` directory:
  ```bash
  cd 03_ai_protocols/01_mcp/06_openai_agents_sdk_integration/shared_mcp_server/
  ```
  3.  Execute the server script (using `uv run`):
      ```bash
      uv run python server.py
      ```
- **Server Details:**
  - It runs on `http://localhost:8001`.
  - Its MCP protocol endpoint is at `/mcp`. So, the full URL for clients is `http://localhost:8001/mcp`.
  - It exposes a tool named `greet_from_shared_server`.
  - It will log incoming requests to its console.

**Keep this server running in its terminal while you execute the agent scripts from this sub-module.**

### 2. "Hello World" Agent SDK Connection

#### Setup

```bash
uv init agent_connect
cd agent_connect

uv add openai-agents
```

Create a .env file and add GEMINI_API_KEY

### Code

Create a file named `main.py` in this directory with the following content:

```python
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams


_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8001/mcp/" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

async def main():
    # 1. Configure parameters for the MCPServerStreamableHttp client
    # These parameters tell the SDK how to reach the MCP server.
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)
    print(f"MCPServerStreamableHttpParams configured for URL: {mcp_params.get('url')}")

    # 2. Create an instance of the MCPServerStreamableHttp client.
    # This object represents our connection to the specific MCP server.
    # It's an async context manager, so we use `async with` for proper setup and teardown.
    # The `name` parameter is optional but useful for identifying the server in logs or multi-server setups.
    async with MCPServerStreamableHttp(params=mcp_params, name="MySharedMCPServerClient") as mcp_server_client:
        print(f"MCPServerStreamableHttp client '{mcp_server_client.name}' created and entered context.")
        print("The SDK will use this client to interact with the MCP server.")

        # 3. Create an agent and pass the MCP server client to it.
        # When an agent is initialized with mcp_servers, the SDK often attempts
        # to list tools from these servers to make the LLM aware of them.
        # You might see a `list_tools` call logged by your shared_mcp_server.
        try:
            assistant = Agent(
                name="MyMCPConnectedAssistant",
                mcp_servers=[mcp_server_client],
                model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
            )
            
            print(f"Agent '{assistant.name}' initialized with MCP server: '{mcp_server_client.name}'.")
            print("Check the logs of your shared_mcp_server for a 'tools/list' request.")

            # 4. Explicitly list tools to confirm connection and tool discovery.
            print(f"Attempting to explicitly list tools from '{mcp_server_client.name}'...")
            tools = await mcp_server_client.list_tools()
            print(f"Tools: {tools}")

            print("\n\nRunning a simple agent interaction...")
            result = await Runner.run(assistant, "What is Sir Zia mood?")
            print(f"\n\n[AGENT RESPONSE]: {result.final_output}")

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}")

    print(f"MCPServerStreamableHttp client '{mcp_server_client.name}' context exited.")
    print(f"--- Agent Connection Test End ---")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An unhandled error occurred in the agent script: {e}")


```

## Explanation of the Code

1.  **`MCP_SERVER_URL`:** Points to the shared MCP server.
2.  **`MCPServerStreamableHttpParams` & `MCPServerStreamableHttp`**:
    - Configures and creates the client to connect to the MCP server, as explained in previous versions.
3.  **`Agent` Initialization**:
    - The `Agent` is initialized with a `name`, `instructions`, the `mcp_servers` (pointing to our `mcp_server_client`), and a `model`.
    - The `model` is an `OpenAIChatCompletionsModel` configured with `model="gemini-2.0-flash"` and the `openai_client` (which is our Gemini client).
4.  **Explicit `list_tools()`**:
    - The script explicitly calls `await mcp_server_client.list_tools()` to verify the connection and log the available tools. It checks for the presence of both `greet_from_shared_server` and `mood_from_shared_server`.
5.  **`Runner.run(assistant, "What is Junaid's mood?")`**:
    - This line executes the agent with a specific query.
    - The `Runner.run` method handles the interaction flow: sending the query and instructions to the LLM, processing any tool calls the LLM decides to make (via the configured MCP server), and returning the final result.
    - The query "What is Junaid's mood?" is designed to potentially trigger the `mood_from_shared_server` tool if the LLM deems it appropriate.

## Expected Output/Behavior

When you run `uv run python main.py` (after starting the `shared_mcp_server/server_main.py` and ensuring your `.env` file has `GEMINI_API_KEY`):

1.  **Agent Script Terminal (`main.py` output):**

    - Logs indicating connection steps.
    - Logs from `httpx` showing HTTP requests to the MCP server (`http://localhost:8001/mcp/`) and the Gemini API (`https://generativelanguage.googleapis.com/...`).
    - Confirmation of `MySharedMCPServerClient` creation.
    - Agent initialization logs.
    - Successful listing of tools from the MCP server, including `greet_from_shared_server` and `mood_from_shared_server`.
    - Log "Running a simple agent interaction..."
    - Further `httpx` logs for interactions with MCP and Gemini during the `Runner.run` call.
    - The final agent response, similar to: `[AGENT RESPONSE]: OK. Junaid is happy.` (The exact response depends on the LLM and potential tool execution).
    - Logs indicating client context exit and test end.

2.  **Shared MCP Server Terminal (`server_main.py` output):**
    - You should see log messages indicating it received `tools/list` requests.
    - If the LLM decided to use the `mood_from_shared_server` tool (or another tool), you'll see corresponding `tool/run` requests logged by the server. For example:
      ```
      INFO:SharedStandAloneMCPServer:MCP Request ID '...' received: tools/list
      INFO:SharedStandAloneMCPServer:Responding to 'tools/list' (ID '...') with 2 tool(s).
      ...
      INFO:SharedStandAloneMCPServer:MCP Request ID '...' received: tool/run (tool_name='mood_from_shared_server')
      INFO:SharedStandAloneMCPServer:Running tool 'mood_from_shared_server' with args: {'name': 'Junaid'}
      INFO:SharedStandAloneMCPServer:Tool 'mood_from_shared_server' execution successful.
      ```

This comprehensive test confirms not only the connection and tool listing but also the agent's ability to use an LLM (Gemini) and potentially invoke MCP tools as part of its execution flow.
