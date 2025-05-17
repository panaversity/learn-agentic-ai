import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from contextlib import AsyncExitStack

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_trace_processors
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from langsmith.wrappers import OpenAIAgentsTracingProcessor

_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP servers
MCP_SERVER_URLS = [
    "http://localhost:8001/mcp",
    "http://localhost:8002/mcp",
]

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

async def main():
    print("Before entering MCP context")
    print(f"--- Agent Connection Test Start ---")
    print(f"Attempting to connect agent to MCP server at {MCP_SERVER_URLS}")

    mcp_servers = []

    async with AsyncExitStack() as stack:
        for url in MCP_SERVER_URLS:
            mcp_params = MCPServerStreamableHttpParams(url=url)
            mcp_server_client = await stack.enter_async_context(
                MCPServerStreamableHttp(params=mcp_params, name=f"MCPServerClient_{url}")
            )
            mcp_servers.append(mcp_server_client)

        try:
            assistant = Agent(
                name="MyMCPConnectedAssistant",
                instructions="You are a helpful assistant designed to test MCP connections.",
                mcp_servers=mcp_servers,
                model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
            )

            print("\n\nRunning a simple agent interaction...")
            result = await Runner.run(assistant, "What is Junaid's mood and what is the weather in London?")
            print(f"\n\n[AGENT RESPONSE]: {result.final_output}")

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}")
            print("Please ensure your API key is set and MCP servers are running.")

    print(f"--- Agent Connection Test End ---")


if __name__ == "__main__":
    print("Starting agent connection test...")
    try:
        set_trace_processors([OpenAIAgentsTracingProcessor()])
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Agent script interrupted by user.")
    except Exception as e:
        print(f"An unhandled error occurred in the agent script: {e}")
