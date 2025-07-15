import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, trace
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams, MCPServer


_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8001/mcp/" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

async def get_instructions_from_prompt(mcp_server: MCPServer, prompt_name: str, **kwargs) -> str:
    """Get agent instructions by calling MCP prompt endpoint (user-controlled)"""
    print(f"Getting instructions from prompt: {prompt_name}")

    try:
        prompt_result = await mcp_server.get_prompt(prompt_name, kwargs)
        content = prompt_result.messages[0].content
        if hasattr(content, "text"):
            instructions = content.text
        else:
            instructions = str(content)
        print("Generated instructions")
        return instructions
    except Exception as e:
        print(f"Failed to get instructions: {e}")
        return f"You are a helpful assistant. Error: {e}"


async def demo_code_review(mcp_server: MCPServer):
    """Demo: Code review with user-selected prompt"""
    print("=== CODE REVIEW DEMO ===")

    # User explicitly selects prompt and parameters
    instructions = await get_instructions_from_prompt(
        mcp_server,
        "generate_code_review_instructions",
        focus="security vulnerabilities",
        language="python",
    )

    agent = Agent(
        name="Code Reviewer Agent",
        instructions=instructions,  # Instructions from MCP prompt
        model=OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client),
    )

    message = """Please review this code:

def process_user_input(user_input):
    command = f"echo {user_input}"
    os.system(command)
    return "Command executed"

"""

    print(f"Running: {message[:60]}...")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)
    print("\n" + "=" * 50 + "\n")


async def show_available_prompts(mcp_server: MCPServer):
    """Show available prompts for user selection"""
    print("=== AVAILABLE PROMPTS ===")

    prompts_result = await mcp_server.list_prompts()
    print("User can select from these prompts:")
    for i, prompt in enumerate(prompts_result.prompts, 1):
        print(f"  {i}. {prompt.name} - {prompt.description}")
    print()


async def main():
    async with MCPServerStreamableHttp(
        name="Simple Prompt Server",
        params={"url": MCP_SERVER_URL},
    ) as server:
        with trace(workflow_name="Simple Prompt Demo"):
            await show_available_prompts(server)
            await demo_code_review(server)


if __name__ == "__main__":
    asyncio.run(main())
