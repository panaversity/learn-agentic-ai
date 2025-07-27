import os
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
    set_default_openai_client,
    set_tracing_disabled,
)

# Load environment variables
load_dotenv() 

# Optional: keep tracing off for simplicity
set_tracing_disabled(disabled=True)

# 1) Env + client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/" #your task is to set in .env file

external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url=BASE_URL,
)

# 2) Model 
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",     
    openai_client=external_client 
)

# 3) Define tools 
@function_tool
def multiply(a: int, b: int) -> int:
    """Exact multiplication (use this instead of guessing math)."""
    return a * b

@function_tool
def sum(a: int, b: int) -> int:
    """Exact addition (use this instead of guessing math)."""
    return a + b

# 4) Create agent with tools
agent: Agent = Agent(
    name="Assistant",
    instructions=(
        "You are a helpful assistant. "
        "Always use tools for math questions. Always follow DMAS rule (division, multiplication, addition, subtraction)."
        "Explain answers clearly and briefly for beginners."
    ),
    model=model,
    tools=[multiply, sum],   # <-- register tools here
)

# 5) Run: the agent should call both tools automatically
prompt = "what is 19 + 23 * 2?"
result = Runner.run_sync(agent, prompt)

print("\nCALLING AGENT\n")
print(result.final_output)
