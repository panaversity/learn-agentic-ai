import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from langfuse import get_client
from agents import Agent, Runner, function_tool, set_default_openai_api, set_default_openai_client,set_tracing_export_api_key, OpenAIChatCompletionsModel


# -----------------------------
# Load environment and configure
# -----------------------------
load_dotenv(find_dotenv())  # Load local .env file

# Instrumentation setup
OpenAIAgentsInstrumentor().instrument()

# Load environment variables
os.getenv("LANGFUSE_PUBLIC_KEY")
os.getenv("LANGFUSE_SECRET_KEY")
os.getenv("LANGFUSE_HOST")

# Set OpenAI API key
# --- Environment setup
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")


client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


# -----------------------------
# Initialize Langfuse client
# -----------------------------
langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("✅ Langfuse client is authenticated and ready!")
else:
    print("❌ Authentication failed. Please check your credentials and host.")

# Example function tool.
@function_tool
def get_city_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

# -----------------------------
# Define async main function
# -----------------------------
async def main():

    agent = Agent(
        name="Assistant",
        instructions="You are a helpful agent.",
        tools=[get_city_weather],
        model=OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=client),
    )

    result = await Runner.run(agent, "What's the weather in Karachi?")
    print("\n--- Agent Response ---")
    print(result.final_output)

    result = await Runner.run(agent, "What's the weather in Islamabad?")
    print("\n--- Agent Response ---")
    print(result.final_output)


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
