import os
import asyncio

from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool

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

@function_tool(description_override="", failure_error_function=)
def get_weather(city: str) -> str:
    try:
        # If Call Fails Call another service i.e get_weather_alternative
        ...
    except ValueError:
        raise ValueError("Weather service is currently unavailable.")
    except TimeoutError:
        raise TimeoutError("Weather service request timed out.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")

base_agent: Agent = Agent(name="WeatherAgent", instructions="" model=llm_model, tools=[get_weather])

async def main():
    res = await Runner.run(base_agent, "What is weather in Lahore")
    print(res.final_output)

if __name__ == "__main__":
    asyncio.run(main())