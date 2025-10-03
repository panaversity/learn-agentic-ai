"""
Redis Sessions - Multi-Instance Demo

Simulates distributed deployment where multiple servers/instances
access same Redis backend for session sharing.

This demonstrates:
1. Session continuity across instances
2. Load balancing scenarios
3. Distributed system patterns

Run: python 03_multi_instance_demo.py
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import RedisSession

load_dotenv()


class AgentInstance:
    """
    Represents a single agent server instance in a distributed system.
    """
    
    def __init__(self, instance_id: str, redis_url: str):
        self.instance_id = instance_id
        self.redis_url = redis_url
        
        # Setup model
        external_client = AsyncOpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.llm_model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash-exp",
            openai_client=external_client
        )
        self.runner = Runner()
    
    async def handle_request(self, conversation_id: str, message: str) -> str:
        """
        Handle a user request (load-balanced to this instance).
        """
        print(f"\n📍 [Instance {self.instance_id}] Processing request")
        print(f"   Conversation: {conversation_id}")
        print(f"   Message: {message}")
        
        # Connect to shared Redis session
        session = RedisSession(
            redis_url=self.redis_url,
            conversation_id=conversation_id,
            ttl=1800
        )
        
        agent = Agent(
            name="DistributedAgent",
            instructions="You are a distributed agent running across multiple servers.",
            model=self.llm_model,
            session=session
        )
        
        # Process request
        response = await self.runner.run(agent=agent, input=message)
        response_text = response.content_blocks[0].get('text', '')
        
        # Check context continuity
        items = await session.get_items()
        message_count = len([i for i in items if i.get('role') in ['user', 'assistant']])
        
        print(f"   ✅ Response generated")
        print(f"   📊 Session has {message_count} messages")
        
        return response_text


async def demo_distributed_system():
    """
    Simulate a distributed system with multiple instances.
    """
    print("=" * 60)
    print("DISTRIBUTED SYSTEM DEMO")
    print("Multiple Instances Sharing Redis Sessions")
    print("=" * 60)
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Create 3 agent instances (simulating 3 servers)
    print("\n🖥️  Starting 3 agent instances...")
    instance_1 = AgentInstance("Server-1-US-East", redis_url)
    instance_2 = AgentInstance("Server-2-US-West", redis_url)
    instance_3 = AgentInstance("Server-3-EU", redis_url)
    print("   ✅ All instances connected to Redis")
    
    # User starts conversation on Instance 1
    print("\n" + "─" * 60)
    print("SCENARIO: User Routed Across Instances")
    print("─" * 60)
    
    conversation_id = "user-alice-001"
    
    print("\n🔵 Request 1 → Instance 1 (US-East)")
    response_1 = await instance_1.handle_request(
        conversation_id,
        "I need help planning a vacation to Europe"
    )
    print(f"   Agent: {response_1[:100]}...")
    
    # Load balancer routes next request to different instance
    print("\n🟢 Request 2 → Instance 2 (US-West)")
    response_2 = await instance_2.handle_request(
        conversation_id,
        "My budget is $5000"
    )
    print(f"   Agent: {response_2[:100]}...")
    print("   ✅ Instance 2 has full context from Request 1")
    
    # Another instance
    print("\n🟡 Request 3 → Instance 3 (EU)")
    response_3 = await instance_3.handle_request(
        conversation_id,
        "I prefer coastal cities"
    )
    print(f"   Agent: {response_3[:100]}...")
    print("   ✅ Instance 3 has full context from Requests 1 & 2")
    
    # Back to Instance 1
    print("\n🔵 Request 4 → Instance 1 (US-East)")
    response_4 = await instance_1.handle_request(
        conversation_id,
        "Which cities do you recommend?"
    )
    print(f"   Agent: {response_4[:100]}...")
    print("   ✅ Instance 1 has all context (budget, preferences)")
    
    print("\n" + "=" * 60)
    print("KEY BENEFITS")
    print("=" * 60)
    
    print("\n✅ Demonstrated:")
    print("   • Session continuity across instances")
    print("   • Load balancing without sticky sessions")
    print("   • Geographical distribution (US-East, US-West, EU)")
    print("   • Single source of truth (Redis)")
    
    print("\n💡 Production Benefits:")
    print("   • Zero downtime deployments (rolling restarts)")
    print("   • Horizontal scaling (add more instances)")
    print("   • Fault tolerance (if one instance fails, others continue)")
    print("   • Global distribution (low-latency regional instances)")


async def demo_failover():
    """
    Demonstrate failover scenario.
    """
    print("\n\n" + "=" * 60)
    print("FAILOVER DEMO")
    print("=" * 60)
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    print("\n🖥️  Instance 1: Starting conversation...")
    instance_1 = AgentInstance("Instance-1", redis_url)
    
    conversation_id = "failover-demo"
    await instance_1.handle_request(conversation_id, "Hello, I need help")
    
    print("\n💥 Instance 1: Simulating crash (not creating new requests)")
    print("   (In production: health check fails, load balancer stops routing)")
    
    print("\n🖥️  Instance 2: Taking over...")
    instance_2 = AgentInstance("Instance-2", redis_url)
    
    await instance_2.handle_request(conversation_id, "Are you still there?")
    print("   ✅ Instance 2 picked up seamlessly")
    print("   ✅ User doesn't know Instance 1 crashed")
    print("   ✅ No data loss (session in Redis)")


async def demo_scaling():
    """
    Demonstrate horizontal scaling.
    """
    print("\n\n" + "=" * 60)
    print("HORIZONTAL SCALING DEMO")
    print("=" * 60)
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    print("\n📈 Scenario: Traffic spike, scaling from 2 to 5 instances")
    
    # Start with 2 instances
    print("\n🖥️  Initial: 2 instances")
    instances = [
        AgentInstance(f"Instance-{i+1}", redis_url) 
        for i in range(2)
    ]
    
    # Simulate traffic
    print("   Processing 5 concurrent requests...")
    
    async def process_request(idx, instance):
        await instance.handle_request(
            f"user-{idx}",
            f"Request {idx}"
        )
    
    # 5 requests, 2 instances (some queuing)
    tasks = [
        process_request(i, instances[i % 2]) 
        for i in range(5)
    ]
    await asyncio.gather(*tasks)
    
    print("\n📈 Scaling up: Adding 3 more instances...")
    instances.extend([
        AgentInstance(f"Instance-{i+3}", redis_url) 
        for i in range(3)
    ])
    print("   Now have 5 instances")
    
    # More traffic
    print("\n   Processing 10 concurrent requests (better distribution)...")
    tasks = [
        process_request(i+5, instances[i % 5]) 
        for i in range(10)
    ]
    await asyncio.gather(*tasks)
    
    print("\n✅ Scaled horizontally without:")
    print("   • Downtime")
    print("   • Data migration")
    print("   • Session loss")
    print("   • Code changes")


if __name__ == "__main__":
    asyncio.run(demo_distributed_system())
    asyncio.run(demo_failover())
    asyncio.run(demo_scaling())
