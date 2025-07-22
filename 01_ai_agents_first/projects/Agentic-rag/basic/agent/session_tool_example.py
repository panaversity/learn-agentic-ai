# Example: OpenAI Agents SDK session with tool calls (weather + vector DB)
# Docs: https://openai.github.io/openai-agents-python/sessions/
# Install: uv add openai-agents

import asyncio
import os

from agents import Agent, Runner, SQLiteSession, Tool

# Set your OpenAI API key (use environment variable for security)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-...your-key...")


# Define a simple weather tool
@Tool()
def get_weather(location: str) -> str:
    """Return a dummy weather report for a location."""
    return f"The weather in {location} is sunny."


# Define a simple vector DB search tool
@Tool()
def search_vector_db(query: str) -> str:
    """Simulate a vector DB search and return a dummy document."""
    # In a real app, this would query Qdrant or another vector DB
    return f"[VectorDB] Top result for '{query}': 'This is a relevant document chunk.'"


# Create an agent with both tools
agent = Agent(
    name="MultiToolBot",
    instructions="You are a helpful assistant. Use the get_weather tool for weather questions and the search_vector_db tool for information lookup.",
    tools=[get_weather, search_vector_db],
)

# Create a persistent session (conversation history)
session = SQLiteSession("multitool_convo")


async def main():
    print("=== Session Tool Example (Weather + Vector DB) ===")
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
