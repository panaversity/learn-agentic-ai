import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
from typing import Callable
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool, RunContextWrapper, ItemHelpers
from openai.types.responses import ResponseTextDeltaEvent

_: bool = load_dotenv(find_dotenv())

gemini_api_key: str | None = os.environ.get("GEMINI_API_KEY")

# Tracing disabled
set_tracing_disabled(disabled=True)

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(api_key=gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

@dataclass
class UserContext:
    username: str
    email: str | None = None

@function_tool()
async def search(local_context: RunContextWrapper[UserContext], query: str) -> str:
    import time
    time.sleep(30)  # Simulating a delay for the search operation
    return "No results found."

def special_prompt(special_context: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    # who is user?
    # which agent
    print(f"\nUser: {special_context.context},\n Agent: {agent.name}\n")
    return f"You are a math expert. User: {special_context.context.username}, Agent: {agent.name}. Please assist with math-related queries."

math_agent: Agent = Agent(name="Genius", instructions=special_prompt, model=llm_model, tools=[search])
# [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
async def call_agent():
    # Call the agent with a specific input
    user_context = UserContext(username="abdullah")

    output = Runner.run_streamed(
        starting_agent=math_agent, 
        input="search for the best math tutor in my area",
        context=user_context
        )
    async for event in output.stream_events():
        print(event)
        # See this for more details and to add different filters: 
        # https://openai.github.io/openai-agents-python/streaming/

asyncio.run(call_agent())