"""
Example: Agent with Custom Session Backend (Redis, PostgreSQL, or Supabase)

Demonstrates how to use a production-ready session memory with the OpenAI Agents SDK.
Choose your backend by uncommenting the relevant import and initialization.

See: https://openai.github.io/openai-agents-python/sessions/
"""

import asyncio
import os

from custom_sessions.redis_session import RedisSession
from openai_agents import Agent, Runner, Tool

# from custom_sessions.supabase_session import SupabaseSessionMinimal
# from custom_sessions.postgres_session import PostgresSession

# Set your OpenAI API key (use environment variable for security)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-...your-key...")

# --- Choose your session backend ---
session = RedisSession(
    session_id="multitool_convo", redis_url="redis://localhost:6379/0"
)
# To use Supabase or Postgres, comment out above and uncomment one below:
# session = SupabaseSessionMinimal(session_id="multitool_convo")
# session = PostgresSession(session_id="multitool_convo", dsn="postgresql://user:password@localhost:5432/yourdb")


# --- Define tools ---
@Tool()
def get_weather(location: str) -> str:
    """Return a dummy weather report for a location."""
    return f"The weather in {location} is sunny."


@Tool()
def search_vector_db(query: str) -> str:
    """Simulate a vector DB search and return a dummy document."""
    return f"[VectorDB] Top result for '{query}': 'This is a relevant document chunk.'"


# --- Create agent with both tools ---
agent = Agent(
    name="MultiToolBot",
    instructions="You are a helpful assistant. Use the get_weather tool for weather questions and the search_vector_db tool for information lookup.",
    tools=[get_weather, search_vector_db],
)


async def main():
    print("=== Agent with Custom Session (Weather + Vector DB) ===")
    print("The agent will remember previous messages and can call both tools.\n")

    # First turn: weather tool
    print("User: What is the weather in Paris?")
    result = await Runner.run(agent, "What is the weather in Paris?", session=session)
    print(f"Assistant: {result.final_output}\n")

    # Second turn: vector DB tool
    print("User: Find information about quantum computing.")
    result = await Runner.run(
        agent, "Find information about quantum computing.", session=session
    )
    print(f"Assistant: {result.final_output}\n")

    # Third turn: follow-up (context preserved)
    print("User: And what about London?")
    result = await Runner.run(agent, "And what about London?", session=session)
    print(f"Assistant: {result.final_output}\n")

    print("=== Conversation Complete ===")
    print(
        "Notice how the agent remembers context and uses the correct tool when needed!"
    )


if __name__ == "__main__":
    asyncio.run(main())
