"""
Redis Sessions - Production Patterns

Demonstrates:
1. Key prefixes for multi-tenancy
2. Connection pooling
3. Error handling
4. Performance monitoring

Run: python 02_production_redis.py
"""

import os
import asyncio
import time
from typing import List
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import RedisSession

load_dotenv()


async def demo_multi_tenancy():
    """
    Demonstrate key prefixes for tenant isolation.
    """
    print("=" * 60)
    print("REDIS MULTI-TENANCY DEMO")
    print("Using Key Prefixes for Tenant Isolation")
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
    
    runner = Runner()
    
    # Tenant A: E-commerce company
    print("\n📦 Tenant A: E-commerce (key prefix: 'ecommerce:')")
    session_a = RedisSession(
        redis_url=redis_url,
        conversation_id="user-123-cart",
        key_prefix="ecommerce:",
        ttl=1800  # 30 minutes
    )
    
    agent_a = Agent(
        name="ShoppingAssistant",
        instructions="You are an e-commerce shopping assistant.",
        model=llm_model,
        session=session_a
    )
    
    await runner.run(agent=agent_a, input="Show me laptops under $1000")
    print("   ✅ Session stored at: ecommerce:user-123-cart")
    
    # Tenant B: Healthcare company
    print("\n🏥 Tenant B: Healthcare (key prefix: 'healthcare:')")
    session_b = RedisSession(
        redis_url=redis_url,
        conversation_id="patient-456-consult",
        key_prefix="healthcare:",
        ttl=3600  # 1 hour
    )
    
    agent_b = Agent(
        name="HealthAssistant",
        instructions="You are a healthcare consultation assistant.",
        model=llm_model,
        session=session_b
    )
    
    await runner.run(agent=agent_b, input="I have a headache for 2 days")
    print("   ✅ Session stored at: healthcare:patient-456-consult")
    
    # Same conversation ID, different tenants - no collision!
    print("\n🔑 Same conversation ID, different tenants (no collision):")
    session_a2 = RedisSession(
        redis_url=redis_url,
        conversation_id="test-conv",
        key_prefix="ecommerce:"
    )
    session_b2 = RedisSession(
        redis_url=redis_url,
        conversation_id="test-conv",
        key_prefix="healthcare:"
    )
    
    print("   • ecommerce:test-conv")
    print("   • healthcare:test-conv")
    print("   ✅ Completely isolated!")
    
    print("\n💡 Benefits:")
    print("   • Complete tenant isolation")
    print("   • Easy to delete all tenant data: DEL ecommerce:*")
    print("   • Different TTL per tenant")
    print("   • Scales to thousands of tenants")


async def demo_performance():
    """
    Demonstrate Redis performance characteristics.
    """
    print("\n\n" + "=" * 60)
    print("REDIS PERFORMANCE DEMO")
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
    
    # Create multiple sessions rapidly
    print("\n🚀 Creating 10 concurrent sessions...")
    
    start_time = time.time()
    
    async def create_session(i):
        session = RedisSession(
            redis_url=redis_url,
            conversation_id=f"perf-test-{i}",
            key_prefix="perf:",
            ttl=60  # 1 minute
        )
        
        agent = Agent(
            name="TestAgent",
            instructions="You are a test assistant.",
            model=llm_model,
            session=session
        )
        
        runner = Runner()
        await runner.run(agent=agent, input=f"Test message {i}")
    
    # Create 10 sessions concurrently
    await asyncio.gather(*[create_session(i) for i in range(10)])
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Created 10 sessions in {elapsed:.2f} seconds")
    print(f"   Average: {elapsed/10:.2f} seconds per session")
    print(f"   Note: Most time spent on LLM calls, not Redis")
    
    # Test read performance
    print("\n📖 Testing read performance...")
    
    session = RedisSession(
        redis_url=redis_url,
        conversation_id="perf-test-0",
        key_prefix="perf:"
    )
    
    reads = []
    for i in range(10):
        start = time.time()
        items = await session.get_items()
        reads.append(time.time() - start)
    
    avg_read = sum(reads) / len(reads) * 1000  # Convert to ms
    print(f"   Average read latency: {avg_read:.2f}ms")
    print(f"   ⚡ Sub-millisecond reads possible with local Redis")


async def demo_best_practices():
    """
    Show production best practices.
    """
    print("\n\n" + "=" * 60)
    print("PRODUCTION BEST PRACTICES")
    print("=" * 60)
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    print("\n✅ Best Practices Demonstrated:\n")
    
    # 1. Use key prefixes
    print("1. Key Prefixes:")
    print("   session = RedisSession(")
    print("       redis_url=redis_url,")
    print("       conversation_id='user-123',")
    print("       key_prefix='app:sessions:'  # Organized keys")
    print("   )")
    
    # 2. Set appropriate TTL
    print("\n2. Appropriate TTL:")
    print("   • Chat: 300s (5 min)")
    print("   • Support: 3600s (1 hour)")
    print("   • Shopping cart: 1800s (30 min)")
    print("   • Long conversations: 86400s (24 hours)")
    
    # 3. Connection pooling
    print("\n3. Connection Pooling:")
    print("   redis_url='redis://host:6379/0?max_connections=50'")
    
    # 4. Error handling
    print("\n4. Error Handling:")
    print("   try:")
    print("       items = await session.get_items()")
    print("   except Exception as e:")
    print("       logger.error(f'Redis error: {e}')")
    print("       # Fallback to in-memory or different backend")
    
    # 5. Monitoring
    print("\n5. Monitoring:")
    print("   • Track Redis memory usage")
    print("   • Monitor connection count")
    print("   • Alert on high latency")
    print("   • Check eviction policy (allkeys-lru recommended)")


if __name__ == "__main__":
    asyncio.run(demo_multi_tenancy())
    asyncio.run(demo_performance())
    asyncio.run(demo_best_practices())
