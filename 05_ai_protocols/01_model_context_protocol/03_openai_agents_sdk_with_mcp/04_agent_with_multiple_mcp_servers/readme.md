# 04: Agent with Multiple MCP Servers

**Objective:** To learn how to configure a single OpenAI Agent to connect to and utilize tools from multiple MCP servers simultaneously.

### 🧪 What This Module Covers Practically

This sub-module provides:

- Working Python scripts for multi-MCP integration
- Simulated or mock MCP server configurations
- An agent that interacts with tools hosted across these servers
- Insights into error handling, server isolation, and scalability

[Example Trace](https://smith.langchain.com/public/1a4bfa57-791d-4b8c-97da-bf0fbdf3b874/r): Here both tools are on separate servers called by an Agent created using OpenAI Agents SDK.

---

### 🧠 Use Cases and Advantages

- **🔌 Distributed Toolsets:** Access tools hosted across different MCP servers — for example, one for weather, one for finance.
- **🧱 Modular Architecture:** Individual teams can host their tools independently while exposing a standard MCP interface.
- **📈 Scalability and Resilience:** Load can be distributed across MCPs; one server being down won't necessarily block agent capabilities.
- **🌐 3rd-Party Integrations:** Any external service exposing an MCP-compatible endpoint can be added seamlessly.

---

### ⚙️ Configuration & Requirements

- The agent's `mcp_servers` parameter accepts a **list of active MCP client instances**.
- Each client should be configured via `MCPServerStreamableHttpParams` and managed inside an `AsyncExitStack`.

#### ✅ Recommended Async Pattern

```python
import asyncio
from contextlib import AsyncExitStack
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner

# Define all MCP server URLs
MCP_SERVER_URLS = [
    "http://localhost:8001/mcp",
    "http://localhost:8002/mcp",
]

# Setup client (e.g., OpenAI/Gemini-compatible)
client = AsyncOpenAI(
    api_key="your-api-key",
    base_url="https://your-base-url",
)

async def main():
    mcp_servers = []

    async with AsyncExitStack() as stack:
        for url in MCP_SERVER_URLS:
            mcp_params = MCPServerStreamableHttpParams(url=url)
            mcp_server_client = await stack.enter_async_context(
                MCPServerStreamableHttp(params=mcp_params, name=f"MCPClient_{url}")
            )
            mcp_servers.append(mcp_server_client)

        assistant = Agent(
            name="MultiMCPAgent",
            instructions="You are a multi-server agent.",
            mcp_servers=mcp_servers,
            model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
        )

        result = await Runner.run(assistant, "Get today's weather and Tesla stock price.")
        print(f"[AGENT RESPONSE]: {result.final_output}")

asyncio.run(main())
```

---

### 🚀 Running the Example Step-by-Step

To run the example and see an agent connect to multiple MCP servers:

1.  **Start the MCP Servers:**
    You need to run two MCP servers: one for mood and one for weather. These servers are located in the `mcp_servers` subdirectory within this example module (`04_agent_with_multiple_mcp_servers`). Open two separate terminals.

    - **Mood Server (runs on port 8001):**
      In your first terminal, navigate to the `mcp_servers` directory:
      ```bash
      cd mcp_servers
      uv run python mood_server.py
      ```
      This server provides a `mood_from_shared_server` tool.
    - **Weather Server (runs on port 8002):**
      In your second terminal, also navigate to the `mcp_servers` directory:
      ```bash
      cd mcp_servers
      uv run python weather_server.py
      ```
      This server provides a `get_forecast` tool.

    Ensure both servers start successfully. They will log information to their respective terminals (e.g., "INFO: Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)"). You can leave these terminals running.

2.  **Configure Environment Variables:**
    The agent code, located in `agent_connect/main.py` (within this example module), uses an API key for a Gemini model via `AsyncOpenAI`.

    - Navigate to the `agent_connect` subdirectory.
    - Create a `.env` file (e.g., `agent_connect/.env`) if it doesn't already exist.
    - Add your `GEMINI_API_KEY` to this file:
      ```env
      GEMINI_API_KEY="your_actual_api_key_here"
      ```
    - The `main.py` script is also configured for LangSmith tracing. If you wish to use LangSmith, ensure your `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2="true"`, and `LANGCHAIN_PROJECT="your-project-name"` environment variables are set (e.g., in the same `.env` file or your shell environment).

3.  **Run the Agent:**
    If you're not already there, navigate to the `agent_connect` subdirectory from the root of this example module (`04_agent_with_multiple_mcp_servers`):

    ```bash
    cd agent_connect
    ```

    Then, run the main agent script:

    ```bash
    uv run python main.py
    ```

    The agent will attempt to connect to both MCP servers, aggregate their tools (`mood_from_shared_server` and `get_forecast`), and then process a query like "What is Junaid's mood and what is the weather in London?". You should see output in the terminal indicating the agent's interaction (including tool calls identified by the MCP server client names) and its final response.

4.  **Observe Tracing (Optional but Recommended):**
    As `agent_connect/main.py` is configured with `OpenAIAgentsTracingProcessor` (using `typing.cast` for linter compatibility), if your LangSmith environment variables are correctly set up:
    - You can navigate to your project in LangSmith to view the detailed trace of the agent's execution.
    - This trace will clearly show the agent's decision-making process, which tools were invoked, which MCP server handled each call (identifiable by the client name like `MCPServerClient_http://localhost:8001/mcp`), and the data flowing through the system. This is invaluable for debugging, understanding multi-MCP interactions, and verifying that tools from different servers are being utilized correctly.

---

### 🧰 Aggregated Tool Management

- When an agent connects to **multiple MCP servers**, it aggregates the toolset into one **logical registry**.
- Calls to `agent.tools` or decisions by the LLM automatically consider **all tools** from all MCP sources.

---

### 🚨 Tool Name Uniqueness & Conflict Handling

- **Important:** Tool names **must be unique** across all connected MCPs.
- Conflicts (e.g., two `get_weather` tools) can cause unpredictable behavior, depending on internal resolution order.
- **Best Practice:** Use **namespacing or prefixing** conventions like:

  - `finance_get_stock_price`
  - `weather_get_forecast`

The SDK does **not** currently resolve these conflicts automatically — this is **developer responsibility**.

---

This sub-module will provide Python code examples to illustrate these concepts, including setting up mock MCP servers and an agent that interacts with them.
