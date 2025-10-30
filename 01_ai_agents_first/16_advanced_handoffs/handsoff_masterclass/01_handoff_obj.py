import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, handoff, RunContextWrapper

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
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

# Function to call when the handoff is invoked
def news_agent_handoff(ctx: RunContextWrapper[None]):
    print(f"\nHanding off to NewsAgent...\n")

news_agent: Agent = Agent(
    name="NewsAgent",
    instructions="You get latest news about tech community and share it with me.",
    model=llm_model,
    tools=[get_weather],
)

weather_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are weather expert - share weather updates as I travel a lot. For all Tech and News let the NewsAgent handle that part by delegation.",
    model=llm_model,
    tools=[get_weather],
    handoffs=[handoff(agent=news_agent, on_handoff=news_agent_handoff)] # Added callback function in on_hadoff parameter 
)

res = Runner.run_sync(weather_agent, "Check if there's any news about OpenAI after GPT-5 launch?")
print("\nAGENT NAME", res.last_agent.name)
print("\n[RESPONSE:]", res.final_output)

# Now check the trace in 
# https://platform.openai.com/traces
