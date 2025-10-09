import os
import asyncio
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from langfuse import get_client, observe
from agents import Agent, Runner, set_default_openai_api, set_default_openai_client, set_tracing_export_api_key


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
# Define async main function with @observe decorator
# -----------------------------
@observe()
async def main():
    """Run an AI agent that replies in haikus."""
    input_text = "Tell me about recursion in programming."
    
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model="gemini-2.5-flash",
    )

    result = await Runner.run(agent, input_text)
    output = result.final_output
    
    # Add metadata to the trace
    langfuse.update_current_trace(
        input=input_text,
        output=output,
        user_id="user_gemini_001",
        session_id="session_haiku_demo",
        tags=["agent", "haiku", "gemini", "recursion"],
        metadata={
            "model": "gemini-2.5-flash",
            "agent_type": "haiku_generator",
            "topic": "recursion"
        },
        version="1.0.0"
    )
    
    print("\n--- Agent Response ---")
    print(output)
    
    return output


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
    
    # Flush events to ensure they're sent to Langfuse
    langfuse.flush()