import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams, create_static_tool_filter


_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8001/mcp/" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

tool_filter = create_static_tool_filter(allowed_tool_names=["greet_from_shared_server"], blocked_tool_names=["mood_from_shared_server"])
mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)

async def main():
    async with MCPServerStreamableHttp(params=mcp_params, name="MySharedMCPServerClient", tool_filter=tool_filter) as mcp_server_client:
        print(f"MCPServerStreamableHttp client '{mcp_server_client.name}' created and entered context.")

        try:
            assistant = Agent(
                name="MyMCPConnectedAssistant",
                mcp_servers=[mcp_server_client],
                model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
            )
            
            print(f"Attempting to explicitly list tools from '{mcp_server_client.name}'...")
            tools = await mcp_server_client.list_tools(run_context=object(), agent=object())
            print(f"\nTools: {len(tools)}")
            print(f"\nNames: {[tool.name for tool in tools]}")

            print("\n\nRunning a simple agent interaction...")
            result = await Runner.run(assistant, "Call greet_from_shared_server for Junaid")
            print(f"\n\n[AGENT RESPONSE]: {result.final_output}")

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}")

    print(f"MCPServerStreamableHttp client '{mcp_server_client.name}' context exited.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An unhandled error occurred in the agent script: {e}")
