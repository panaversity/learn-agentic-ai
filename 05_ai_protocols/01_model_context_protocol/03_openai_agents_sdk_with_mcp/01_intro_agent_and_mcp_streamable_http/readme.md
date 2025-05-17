# Sub-module 01: Connecting to an MCP Server (Streamable HTTP)

**Objective:** To demonstrate the basic configuration and connection of an OpenAI Agent to an MCP server that uses the `streamable-http` transport, utilizing the `MCPServerStreamableHttp` client class from the OpenAI Agents SDK.

## Core Concept

The primary goal here is to show an `Agent` being initialized with an `MCPServerStreamableHttp` instance. This instance acts as a client that points to a running MCP server. We want to confirm that the agent, upon initialization or when it first needs to interact with MCP tools, attempts to connect to this server. A common first interaction is for the agent (or the SDK on its behalf) to call `list_tools()` on the MCP server.

## Setup

### 1. Run the Shared MCP Server

For this and subsequent examples in module `03_openai_agents_sdk_with_mcp`, we will use a shared, standalone MCP server. This server is designed to be simple and provide a consistent target for our agent examples.

- **Location:** `05_ai_protocols/01_model_context_protocol/03_openai_agents_sdk_with_mcp/shared_mcp_server/server_main.py`
- **To Run:**
  1.  Open a new terminal.
  2.  Navigate to the `shared_mcp_server` directory:
  ```bash
  cd 05_ai_protocols/01_model_context_protocol/03_openai_agents_sdk_with_mcp/shared_mcp_server/
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

### 2. Agent Script (`agent_connect_test.py`)

The Python script below will be created in the current directory (`05_ai_protocols/01_model_context_protocol/03_openai_agents_sdk_with_mcp/01_connecting_to_mcp_server_streamable_http/`).

## "Hello World" Connection Code

### Setup

```bash
uv init agent_connect
cd agent_connect

uv add openai-agents
```

Create a .env file and add GEMINI_API_KEY

### Code

Create a file named `main.py` in this directory with the following content:

```python
# 05_ai_protocols/01_model_context_protocol/03_openai_agents_sdk_with_mcp/01_connecting_to_mcp_server_streamable_http/agent_connect/main.py
import asyncio
import logging
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

# Configure basic logging to see SDK interactions and our own logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8001/mcp" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

set_tracing_disabled(disabled=True)

async def main():
    logger.info(f"--- Agent Connection Test Start ---")
    logger.info(f"Attempting to connect agent to MCP server at {MCP_SERVER_URL}")

    # 1. Configure parameters for the MCPServerStreamableHttp client
    # These parameters tell the SDK how to reach the MCP server.
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)
    logger.info(f"MCPServerStreamableHttpParams configured for URL: {mcp_params.get('url')}")

    # 2. Create an instance of the MCPServerStreamableHttp client.
    # This object represents our connection to the specific MCP server.
    # It's an async context manager, so we use `async with` for proper setup and teardown.
    # The `name` parameter is optional but useful for identifying the server in logs or multi-server setups.
    async with MCPServerStreamableHttp(params=mcp_params, name="MySharedMCPServerClient") as mcp_server_client:
        logger.info(f"MCPServerStreamableHttp client '{mcp_server_client.name}' created and entered context.")
        logger.info("The SDK will use this client to interact with the MCP server.")

        # 3. Create an agent and pass the MCP server client to it.
        # When an agent is initialized with mcp_servers, the SDK often attempts
        # to list tools from these servers to make the LLM aware of them.
        # You might see a `list_tools` call logged by your shared_mcp_server.
        try:
            assistant = Agent(
                name="MyMCPConnectedAssistant",
                instructions="You are a helpful assistant designed to test MCP connections. You can also tell Junaid's mood.",
                mcp_servers=[mcp_server_client],
                model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
            )

            logger.info(f"Agent '{assistant.name}' initialized with MCP server: '{mcp_server_client.name}'.")
            logger.info("The SDK may have implicitly called list_tools() on the MCP server.")
            logger.info("Check the logs of your shared_mcp_server for a 'tools/list' request.")

            # 4. Explicitly list tools to confirm connection and tool discovery.
            logger.info(f"Attempting to explicitly list tools from '{mcp_server_client.name}'...")
            tools = await mcp_server_client.list_tools()
            if tools:
                tool_names = [tool.name for tool in tools if tool.name] # Added if tool.name to avoid issues with None
                logger.info(f"Successfully listed tools from MCP server: {tool_names}")
                if "greet_from_shared_server" in tool_names and "mood_from_shared_server" in tool_names:
                    logger.info("Confirmed: 'greet_from_shared_server' and 'mood_from_shared_server' tools are available!")
                else:
                    logger.warning(f"'greet_from_shared_server' or 'mood_from_shared_server' tool NOT found. Check server definition. Found: {tool_names}")
            else:
                logger.warning("No tools found on the MCP server. Ensure the server is running and defines tools.")

            logger.info("\n\nRunning a simple agent interaction...")
            # Example query that might trigger the 'mood_from_shared_server' tool
            result = await Runner.run(assistant, "What is Junaid's mood?")
            logger.info(f"\n\n[AGENT RESPONSE]: {result.final_output}")

        except Exception as e:
            logger.error(f"An error occurred during agent setup or tool listing: {e}", exc_info=True)
            logger.error("Please ensure your Gemini API key is set in .env and the shared MCP server is running.")

    logger.info(f"MCPServerStreamableHttp client '{mcp_server_client.name}' context exited.")
    logger.info(f"--- Agent Connection Test End ---")

if __name__ == "__main__":
    # It's good practice to handle potential asyncio errors or user interrupts
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent script interrupted by user.")
    except Exception as e:
        logger.error(f"An unhandled error occurred in the agent script: {e}", exc_info=True)

```

## Explanation of the Code

1.  **Imports & Setup:**
    - `asyncio`, `logging`, `os`, `load_dotenv`, `find_dotenv` for basic operations.
    - From `agents` (OpenAI Agents SDK): `Agent`, `AsyncOpenAI` (for Gemini), `OpenAIChatCompletionsModel`, `Runner`, `set_tracing_disabled`.
    - From `agents.mcp`: `MCPServerStreamableHttp`, `MCPServerStreamableHttpParams`.
2.  **Logging & Environment:**
    - Basic logging is configured.
    - `load_dotenv(find_dotenv())` loads environment variables from a `.env` file (e.g., for `GEMINI_API_KEY`).
3.  **`MCP_SERVER_URL`:** Points to the shared MCP server.
4.  **Gemini Client (`AsyncOpenAI`)**:
    - An `AsyncOpenAI` client is configured to use Google's Gemini API by providing the `api_key` and the specific `base_url`.
5.  **`set_tracing_disabled(disabled=True)`**:
    - This function disables the SDK's built-in tracing. Tracing helps in debugging and observing the agent's internal operations but can be verbose. We'll cover tracing in a later module. For this example, it's turned off.
6.  **`MCPServerStreamableHttpParams` & `MCPServerStreamableHttp`**:
    - Configures and creates the client to connect to the MCP server, as explained in previous versions.
7.  **`Agent` Initialization**:
    - The `Agent` is initialized with a `name`, `instructions`, the `mcp_servers` (pointing to our `mcp_server_client`), and a `model`.
    - The `model` is an `OpenAIChatCompletionsModel` configured with `model="gemini-2.0-flash"` and the `openai_client` (which is our Gemini client).
8.  **Explicit `list_tools()`**:
    - The script explicitly calls `await mcp_server_client.list_tools()` to verify the connection and log the available tools. It checks for the presence of both `greet_from_shared_server` and `mood_from_shared_server`.
9.  **`Runner.run(assistant, "What is Junaid's mood?")`**:
    - This line executes the agent with a specific query.
    - The `Runner.run` method handles the interaction flow: sending the query and instructions to the LLM, processing any tool calls the LLM decides to make (via the configured MCP server), and returning the final result.
    - The query "What is Junaid's mood?" is designed to potentially trigger the `mood_from_shared_server` tool if the LLM deems it appropriate.
10. **Error Handling & Context Management**: Standard `try...except` blocks and `async with` are used for robustness.

## Expected Output/Behavior

When you run `python main.py` (after starting the `shared_mcp_server/server_main.py` and ensuring your `.env` file has `GEMINI_API_KEY`):

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

## Key SDK Concepts Reinforced

- `MCPServerStreamableHttpParams`: For configuring connection details to a `streamable-http` MCP server.
- `MCPServerStreamableHttp`: The client class in the SDK for interacting with such servers.
- `Agent(mcp_servers=[...])`: How to make an agent aware of MCP servers.
- `mcp_server_client.list_tools()`: Directly invoking tool listing (also done implicitly by the Agent).
- Asynchronous Context Management (`async with`) for `MCPServerStreamableHttp`.
- Using `Runner.run()` to execute an agent with a query.
- Integration with an LLM (Gemini via `AsyncOpenAI` and `OpenAIChatCompletionsModel`).
- Disabling tracing with `set_tracing_disabled`.
