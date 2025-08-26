import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, RunContextWrapper, RunHooks

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


# Agent Lifecycle Callbacks/Hooks
class HelloRunHooks(RunHooks):
        
    async def on_agent_start(self, context: RunContextWrapper, agent: Agent):
        print(f"\n\n[RunLifecycle] Agent {agent.name} start with context: {context}\n\n")
        
    async def on_llm_start(self, context: RunContextWrapper, agent: Agent, system_prompt, input_items):
        print(f"\n\n[RunLifecycle] LLM call for agent {agent.name} starting with system prompt: {system_prompt} and input items: {input_items}\n\n")
        
    
@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

news_agent: Agent = Agent(
    name="NewsAgent",
    instructions="You are a helpful news assistant.",
    model=llm_model,
)


base_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are a helpful assistant. Talk about weather and let news_agent handle the news things",
    model=llm_model,
    tools=[get_weather],
    handoffs=[news_agent]
)

res = Runner.run_sync(
    starting_agent=base_agent, 
    input="What's the latest news about Qwen Code - seems like it can give though time to claude code.",
    hooks=HelloRunHooks()
    )

print(res.last_agent.name)
print(res.final_output)

# Now check the trace in 