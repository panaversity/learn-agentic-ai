import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams


_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8000/mcp/" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")
# load openai api key from env for tracing
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

async def main():
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)
    async with MCPServerStreamableHttp(params=mcp_params, name="MemoryServer", cache_tools_list=True) as mcp_server_client:
        try:
            assistant = Agent(
                name="HRAgent",
                mcp_servers=[mcp_server_client],
                model=OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client),
                instructions="You are a helpful assistant that can use tools to share information.",
            )

            
            result = await Runner.run(assistant, "Can you check Ahmad Hassan Profile??")
            print(f"\n\n[AGENT RESPONSE - AHMAD PROFILE]: {result.final_output}")
            
            # Let's share some faces about another expert and see if they are saved
            result = await Runner.run(assistant, "We hired Jay as Agent Native Cloud Expert. He is a senior cloud architect at Microsoft Azure. He has expertise in Kubernetes, Azure DevOps, and cloud security. He has worked on large-scale cloud migrations and is known for his deep understanding of cloud-native architectures.")
            print(f"\n\n[AGENT RESPONSE - JAY PROFILE]: {result.final_output}")

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An unhandled error occurred in the agent script: {e}")