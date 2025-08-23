import os
import asyncio

from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, RunContextWrapper, AgentBase
from dataclasses import dataclass

_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

@dataclass
class UserScope:
    is_admin: bool

async def is_weather_allowed(ctx: RunContextWrapper[UserScope], agent: AgentBase[UserScope]) -> bool:
    print("Checking if weather is allowed...", ctx.context)
    return True if ctx.context.is_admin else False

@function_tool(is_enabled=is_weather_allowed)
def get_weather(city: str) -> str:
    return f"Sunny"

base_agent: Agent = Agent(name="WeatherAgent", model=llm_model, tools=[get_weather])

async def main():
    abdul_scope = UserScope(is_admin=False)
    res = await Runner.run(base_agent, "What is weather in Lahore", context=abdul_scope)
    print(res.final_output)

if __name__ == "__main__":
    asyncio.run(main())