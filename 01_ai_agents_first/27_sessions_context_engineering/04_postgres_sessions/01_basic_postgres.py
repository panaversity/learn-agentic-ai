"""
PostgreSQL Sessions - Basic Usage

Prerequisites:
1. PostgreSQL running (use Docker: docker run --name agents-postgres -e POSTGRES_PASSWORD=mysecret -e POSTGRES_DB=agents_db -p 5432:5432 -d postgres:16)
2. DATABASE_URL in .env file

Run: python 01_basic_postgres.py
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import PostgreSQLSession

load_dotenv()


async def demo_postgres_session():
    print("=" * 60)
    print("POSTGRESQL SESSION DEMO")
    print("=" * 60)
    
    # Check for DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("\n❌ ERROR: DATABASE_URL not found in .env file")
        print("\nPlease add to .env:")
        print("DATABASE_URL=postgresql://user:password@localhost:5432/agents_db")
        print("\nOr start PostgreSQL with Docker:")
        print("docker run --name agents-postgres \\")
        print("  -e POSTGRES_PASSWORD=mysecret \\")
        print("  -e POSTGRES_DB=agents_db \\")
        print("  -p 5432:5432 \\")
        print("  -d postgres:16")
        return
    
    print(f"\n✅ Connected to: {database_url.split('@')[1] if '@' in database_url else 'PostgreSQL'}")
    
    # Setup Gemini model
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    # Create PostgreSQL session
    conversation_id = "demo-postgres-001"
    session = PostgreSQLSession(
        database_url=database_url,
        conversation_id=conversation_id
    )
    
    print(f"🆔 Conversation ID: {conversation_id}")
    
    # Create agent
    agent = Agent(
        name="ShoppingAssistant",
        instructions="You are a helpful shopping assistant. Remember user preferences.",
        model=llm_model,
        session=session
    )
    
    # Have conversation
    runner = Runner()
    
    print("\n" + "─" * 60)
    print("CONVERSATION")
    print("─" * 60)
    
    messages = [
        "I'm looking for a laptop",
        "My budget is around $1200",
        "I prefer lightweight models with good battery life"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\nTurn {i}")
        print(f"User: {msg}")
        response = await runner.run(agent=agent, input=msg)
        print(f"Agent: {response.content_blocks[0].get('text', '')[:200]}...")
    
    print("\n" + "=" * 60)
    print("SESSION INFO")
    print("=" * 60)
    
    items = await session.get_items()
    print(f"\nMessages in session: {len([i for i in items if i.get('role') in ['user', 'assistant']])}")
    print(f"Total context items: {len(items)}")
    print(f"\n✅ Conversation stored in PostgreSQL database")
    print(f"   Can be accessed from any server with same DATABASE_URL")


if __name__ == "__main__":
    asyncio.run(demo_postgres_session())
