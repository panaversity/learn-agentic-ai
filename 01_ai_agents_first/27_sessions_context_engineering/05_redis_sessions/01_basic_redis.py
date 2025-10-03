"""
Redis Sessions - Basic Usage

Prerequisites:
1. Redis running (use Docker: docker run --name agents-redis -p 6379:6379 -d redis:7-alpine)
2. REDIS_URL in .env file

Run: python 01_basic_redis.py
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import RedisSession

load_dotenv()


async def demo_redis_session():
    print("=" * 60)
    print("REDIS SESSION DEMO")
    print("Ultra-Fast In-Memory Sessions with TTL")
    print("=" * 60)
    
    # Check for REDIS_URL
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print(f"\n✅ Redis URL: {redis_url}")
    
    # Setup Gemini model
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    # Create Redis session with 30-minute TTL
    conversation_id = "demo-redis-001"
    session = RedisSession(
        redis_url=redis_url,
        conversation_id=conversation_id,
        ttl=1800  # 30 minutes (1800 seconds)
    )
    
    print(f"\n🆔 Conversation ID: {conversation_id}")
    print(f"⏰ TTL: 30 minutes (auto-expires)")
    
    # Create agent
    agent = Agent(
        name="FastAssistant",
        instructions="You are a helpful assistant with ultra-fast response times.",
        model=llm_model,
        session=session
    )
    
    # Have conversation
    runner = Runner()
    
    print("\n" + "─" * 60)
    print("CONVERSATION (stored in Redis)")
    print("─" * 60)
    
    messages = [
        "What's the fastest way to learn Python?",
        "How long should I practice each day?",
        "Can you recommend any projects for beginners?"
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
    print(f"\n✅ Session stored in Redis (in-memory)")
    print(f"⏰ Will auto-expire after 30 minutes of inactivity")
    print(f"🚀 Access latency: < 1ms")


async def demo_ttl_expiration():
    """
    Demonstrate TTL expiration behavior.
    """
    print("\n\n" + "=" * 60)
    print("TTL EXPIRATION DEMO")
    print("=" * 60)
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Setup model
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    # Create session with very short TTL for demo (10 seconds)
    print("\n📝 Creating session with 10-second TTL...")
    session = RedisSession(
        redis_url=redis_url,
        conversation_id="ttl-demo",
        ttl=10  # 10 seconds
    )
    
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        model=llm_model,
        session=session
    )
    
    runner = Runner()
    
    # Send message
    print("User: Hello!")
    await runner.run(agent=agent, input="Hello!")
    
    items = await session.get_items()
    print(f"✅ Session created: {len(items)} items")
    
    print("\n⏳ Waiting 5 seconds... (session still valid)")
    await asyncio.sleep(5)
    
    items = await session.get_items()
    print(f"✅ Session still exists: {len(items)} items")
    
    print("\n⏳ Waiting another 6 seconds... (total 11 seconds, exceeds TTL)")
    await asyncio.sleep(6)
    
    try:
        items = await session.get_items()
        if len(items) == 0:
            print("❌ Session expired (TTL exceeded)")
        else:
            print(f"Session still has {len(items)} items (TTL might be extended on access)")
    except Exception as e:
        print(f"❌ Session expired: {e}")
    
    print("\n💡 Key Point:")
    print("   • Redis automatically deletes expired keys")
    print("   • No manual cleanup needed")
    print("   • Perfect for temporary sessions (chat, shopping carts)")


if __name__ == "__main__":
    asyncio.run(demo_redis_session())
    asyncio.run(demo_ttl_expiration())
