# Module 3: Challenge - Tracing MCP Interactions via SDK Logging

## Introduction

This module challenges you to use **Tracing concepts for 01_agents_first** as a primary means to trace MCP tool interactions.

## The Challenge: Uncovering Traces in Logs

Your goal is to observe the detailed flow of an agent calling a tool provided by an MCP server, by analyzing the verbose logs produced by the SDK.

Steps
- Get code from 01_intro_agent and run the mcp server
- Add this new package:

```bash
uv add "langsmith[openai-agents]"
```
Here's an [example trace using LangSmith](https://smith.langchain.com/public/7a330667-d069-42b3-b21a-44d7e31bcb0f/r)

- Follow this [quickstart for langtrace tracing](https://docs.smith.langchain.com/observability/how_to_guides/trace_with_openai_agents_sdk)

Note: For langsmith you need to add `LANGCHAIN_API_KEY` in `.env`.

```python
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_trace_processors
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from langsmith.wrappers import OpenAIAgentsTracingProcessor

_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8001/mcp" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

async def main():
    print("Before entering MCP context")
    print(f"--- Agent Connection Test Start ---")
    print(f"Attempting to connect agent to MCP server at {MCP_SERVER_URL}")

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
                instructions="You are a helpful assistant designed to test MCP connections.",
                mcp_servers=[mcp_server_client],
                model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
            )
            
            print(f"Agent '{assistant.name}' initialized with MCP server: '{mcp_server_client.name}'.")
            print("The SDK may have implicitly called list_tools() on the MCP server.")
            print("Check the logs of your shared_mcp_server for a 'tools/list' request.")

            # 4. Explicitly list tools to confirm connection and tool discovery.
            print(f"Attempting to explicitly list tools from '{mcp_server_client.name}'...")
            tools = await mcp_server_client.list_tools()
            print(f"Tools: {tools}")

            print("\n\nRunning a simple agent interaction...")
            result = await Runner.run(assistant, "What is Junaid mood?")
            print(f"\n\n[AGENT RESPONSE]: {result.final_output}")

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}", exc_info=True)
            print("Please ensure your OpenAI API key is set if using OpenAI models, and the shared MCP server is running.")

    print(f"MCPServerStreamableHttp client '{mcp_server_client.name}' context exited.")
    print(f"--- Agent Connection Test End ---")

if __name__ == "__main__":
    print("Starting agent connection test...")
    # It's good practice to handle potential asyncio errors or user interrupts
    try:
        set_trace_processors([OpenAIAgentsTracingProcessor()])
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Agent script interrupted by user.")
    except Exception as e:
        print(f"An unhandled error occurred in the agent script: {e}", exc_info=True)

```

Good luck, and happy tracing!
