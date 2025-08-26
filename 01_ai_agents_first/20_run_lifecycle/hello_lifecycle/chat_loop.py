import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, RunResult

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
    # handoffs=[news_agent]
)


user_chat: list[dict] = []
while True:
    user_input = input("Enter your input (or 'exit' to quit): ")
    if user_input.lower() == 'exit':
        break

    if user_input.lower() == 'view':
        print("\nCurrent Chat History:", user_chat)
    
    user_message = {"role": "user", "content": user_input}
    user_chat.append(user_message)
    
    res: RunResult = Runner.run_sync(starting_agent=base_agent, input=user_chat)
    
    user_chat = res.to_input_list()

    print("\nAGENT RESPONSE:", res.final_output)


# Now check the trace in
