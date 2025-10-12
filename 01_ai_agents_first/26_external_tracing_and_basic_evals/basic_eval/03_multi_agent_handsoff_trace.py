import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from langfuse import get_client
from agents import Agent, Runner, set_default_openai_api, set_default_openai_client,set_tracing_export_api_key


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

set_default_openai_client(client=client, use_for_tracing=False)
set_default_openai_api("chat_completions")
set_tracing_export_api_key(openai_api_key)

# -----------------------------
# Initialize Langfuse client
# -----------------------------
langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("✅ Langfuse client is authenticated and ready!")
else:
    print("❌ Authentication failed. Please check your credentials and host.")


# -----------------------------
# Define async main function
# -----------------------------
async def main():

    spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
    model = "gemini-2.5-flash",
    )

    english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model = "gemini-2.5-flash",
    )
    
    triage_agent = Agent(
        name="Triage agent",
        instructions="Handoff to the appropriate agent based on the language of the request.",
        handoffs=[spanish_agent, english_agent],
        model = "gemini-2.5-flash",
    )

    result = await Runner.run(triage_agent, "Hola, ¿cómo estás?")
    print("\n--- Agent Response ---")
    print(result.final_output)


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
