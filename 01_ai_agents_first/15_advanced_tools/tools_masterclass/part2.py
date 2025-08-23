import os
import asyncio

from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, MaxTurnsExceeded

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

@function_tool
def get_weather(city: str) -> str:
    return f"Sunny"

base_agent: Agent = Agent(name="WeatherAgent", model=llm_model, tools=[get_weather])
print(base_agent.tools)

async def main():
    try:
        res = await Runner.run(base_agent, "What is weather in Lahore", max_turns=2)
        print(res.new_items)
    except MaxTurnsExceeded as e:
        print(f"Max turns exceeded: {e}")

if __name__ == "__main__":
    asyncio.run(main())