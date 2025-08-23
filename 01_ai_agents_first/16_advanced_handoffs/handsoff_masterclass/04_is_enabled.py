import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, handoff, RunContextWrapper, HandoffInputData
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


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

def summarized_news_transfer(data: HandoffInputData) -> HandoffInputData:
    print("\n\n[HANDOFF] Summarizing news transfer...\n\n")
    summarized_conversation = "Get latest tech news."
    
    return HandoffInputData(
        input_history=summarized_conversation,
        pre_handoff_items=(),
        new_items=(),
    )

@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

news_agent: Agent = Agent(
    name="NewsAgent",
    instructions="You get latest news about tech community and share it with me. Always transfer back to WeatherAgent after answering the questions",
    model=llm_model,
)

planner_agent: Agent = Agent(
    name="PlannerAgent",
    instructions="You get latest news about tech community and share it with me. Always transfer back to WeatherAgent after answering the questions",
    model=llm_model,
)

def news_region(region: str):
    def is_news_allowed(ctx: RunContextWrapper, agent: Agent) -> bool:
        return True if ctx.context.get("is_admin", False) and region == "us-east-1" else False
    return is_news_allowed

weather_agent: Agent = Agent(
    name="WeatherAgent",
    instructions=f"You are weather expert - share weather updates as I travel a lot. For all Tech and News let the NewsAgent handle that part by delegation. {RECOMMENDED_PROMPT_PREFIX}",
    model=llm_model,
    handoffs=[handoff(agent=news_agent, is_enabled=news_region("us-east-1")), planner_agent]
)

res = Runner.run_sync(weather_agent, 
                      "Check if there's any news about OpenAI after GPT-5 launch - also what's the weather SF?", 
                      context={"is_admin": True}
                      )
                      
print("\nAGENT NAME", res.last_agent.name)
print("\n[RESPONSE:]", res.final_output)
print("\n[NEW_ITEMS:]", res.new_items)

# Now check the trace in 