import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, AsyncOpenAI

# 🌿 Load environment variables
load_dotenv(find_dotenv())

# 🔐 Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

# Create agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant. Be friendly and remember our conversation.",
    model=model
)

# Create session memory
session = SQLiteSession("my_first_conversation")

print("=== First Conversation with Memory ===")

# Turn 1
result1 = Runner.run_sync(
    agent,
    "Hi! My name is Alex and I love pizza.",
    session=session
)
print("Agent:", result1.final_output)

# Turn 2 - Agent should remember your name!
result2 = Runner.run_sync(
    agent,
    "What's my name?",
    session=session
)
print("Agent:", result2.final_output)  # Should say "Alex"!

# Turn 3 - Agent should remember you love pizza!
result3 = Runner.run_sync(
    agent,
    "What food do I like?",
    session=session
)

print("Agent:", result3.final_output)  # Should say "Alex"!

print("\n\nNO SESSION MEMORY\n\n")
result4 = Runner.run_sync(
    agent,
    "What's my name and what do I like?"
)
print("Agent:", result4.final_output)  # Should mention pizza!