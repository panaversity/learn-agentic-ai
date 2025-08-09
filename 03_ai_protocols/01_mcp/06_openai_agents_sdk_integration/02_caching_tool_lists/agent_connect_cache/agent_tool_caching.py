import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
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

    async with MCPServerStreamableHttp(params=mcp_params, name="MySharedMCPServerClient", cache_tools_list=True) as mcp_server_client:
        print(f"MCPServerStreamableHttp client '{mcp_server_client.name}' created and entered context.")

        try:
            assistant = Agent(
                name="MyMCPConnectedAssistant",
                mcp_servers=[mcp_server_client],
                model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
            )
            
            print(f"Agent '{assistant.name}' initialized with MCP server: '{mcp_server_client.name}'.")
            print("Check the logs of your shared_mcp_server for a 'tools/list' request.")

            # 4. Explicitly list tools to confirm connection and tool discovery.
            print(f"\n1. Attempting to explicitly list tools from '{mcp_server_client.name}'...")
            tools = await mcp_server_client.list_tools()
            print(f"Tools: {tools}")
            
            print(f"\n2. Attempting AGAIN to explicitly list tools 3 more times from '{mcp_server_client.name}'...")
            tools = await mcp_server_client.list_tools()
            tools = await mcp_server_client.list_tools()
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
