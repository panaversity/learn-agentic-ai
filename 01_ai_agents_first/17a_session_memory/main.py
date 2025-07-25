import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI

from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel

load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GOOGLE_API_KEY")

# Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

agent = Agent(
    name="Assistant",
    instructions="you are a basic math assistant. Reply very concisely.",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.5-flash",
        openai_client=client
    ),
)

session = SQLiteSession(
    session_id="user_123",
    db_path="maths_db.db"
)

def main():
    result1 = Runner.run_sync(
        agent,
        "what is 2+2?",
        session=session
    )

    result2 = Runner.run_sync(
        agent,
        "Multiply whatever response you get by 2.",
        session=session
    )

    print(f"Result 1: {result1.final_output}")
    print(f"Result 2: {result2.final_output}")


if __name__ == "__main__":
    main()


# RESULTS = 
# Result 1: 2 + 2 = 4
# Result 2: Okay, since my previous response was 4, multiplying that by 2 gives me:

# 4 * 2 = 8


