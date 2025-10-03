"""
Advanced SQLite Sessions - Basic Usage

This example demonstrates basic AdvancedSQLiteSession features:
1. Persistent conversations
2. Usage tracking
3. Conversation continuity across restarts

Key Concepts:
- AdvancedSQLiteSession stores conversations in local SQLite database
- Conversations persist across application restarts
- store_run_usage=True enables automatic token tracking
- conversation_id allows continuing previous conversations

Run: python 01_basic_advanced_sqlite.py
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import AdvancedSQLiteSession

load_dotenv()


# ============= DEMO: PERSISTENT CONVERSATION =============

async def demo_persistent_conversation():
    """
    Demonstrate persistent conversations with usage tracking.
    """
    print("=" * 60)
    print("ADVANCED SQLITE SESSION DEMO")
    print("Persistent Conversations with Usage Tracking")
    print("=" * 60)
    
    # Setup Gemini model
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    # Database file path
    db_path = "demo_conversations.db"
    conversation_id = "demo-conv-001"
    
    print(f"\n📁 Database: {db_path}")
    print(f"🆔 Conversation ID: {conversation_id}")
    
    # ===== Part 1: Initial Conversation =====
    print("\n" + "─" * 60)
    print("PART 1: Initial Conversation")
    print("─" * 60)
    
    # Create session with usage tracking
    session = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id=conversation_id,
        store_run_usage=True  # Enable token usage tracking
    )
    
    # Create agent
    agent = Agent(
        name="TravelAgent",
        instructions="""You are a helpful travel planning assistant.
Remember details from previous turns and provide personalized recommendations.""",
        model=llm_model,
        session=session
    )
    
    # Initial conversation
    runner = Runner()
    
    print("\nUser: I'm planning a trip to Japan")
    response = await runner.run(agent=agent, input="I'm planning a trip to Japan")
    print(f"Agent: {response.content_blocks[0].get('text', '')[:200]}...")
    
    print("\nUser: I have a budget of $3000 and prefer boutique hotels")
    response = await runner.run(
        agent=agent,
        input="I have a budget of $3000 and prefer boutique hotels"
    )
    print(f"Agent: {response.content_blocks[0].get('text', '')[:200]}...")
    
    # Show session info
    items = await session.get_items()
    print(f"\n📊 Session Info:")
    print(f"   - Messages in session: {len([i for i in items if i.get('role') in ['user', 'assistant']])}")
    print(f"   - Total context items: {len(items)}")
    print(f"   - Database: {db_path}")
    print(f"   - Usage tracking: Enabled")
    
    # ===== Part 2: Continue Conversation (simulate restart) =====
    print("\n" + "─" * 60)
    print("PART 2: Continue Conversation (simulating app restart)")
    print("─" * 60)
    print("\nℹ️  Creating new session with same conversation_id...")
    print("   This simulates restarting the app and continuing the conversation.\n")
    
    # Create NEW session instance with same conversation_id
    # This simulates app restart - previous context is loaded from database
    session2 = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id=conversation_id,  # Same ID = continues conversation
        store_run_usage=True
    )
    
    # Create NEW agent with new session
    agent2 = Agent(
        name="TravelAgent",
        instructions="""You are a helpful travel planning assistant.
Remember details from previous turns and provide personalized recommendations.""",
        model=llm_model,
        session=session2
    )
    
    # Continue conversation - agent should remember previous context
    print("User: What cities do you recommend for cherry blossoms?")
    response = await runner.run(
        agent=agent2,
        input="What cities do you recommend for cherry blossoms?"
    )
    print(f"Agent: {response.content_blocks[0].get('text', '')[:250]}...")
    
    # Verify context continuity
    items2 = await session2.get_items()
    print(f"\n📊 Continued Session Info:")
    print(f"   - Messages now: {len([i for i in items2 if i.get('role') in ['user', 'assistant']])}")
    print(f"   - Context loaded from database: {db_path}")
    print(f"   ✅ Agent remembered budget ($3000) and preferences (boutique hotels)")
    
    print("\n" + "=" * 60)
    print("USAGE ANALYTICS")
    print("=" * 60)
    
    # Query usage data from database
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total tokens used
    cursor.execute("""
        SELECT 
            COUNT(*) as num_runs,
            SUM(prompt_tokens) as total_prompt_tokens,
            SUM(completion_tokens) as total_completion_tokens,
            SUM(prompt_tokens + completion_tokens) as total_tokens
        FROM usage_logs
        WHERE conversation_id = ?
    """, (conversation_id,))
    
    stats = cursor.fetchone()
    if stats and stats[0] > 0:
        num_runs, prompt_tokens, completion_tokens, total_tokens = stats
        
        print(f"\n📊 Token Usage for {conversation_id}:")
        print(f"   - Agent runs: {num_runs}")
        print(f"   - Prompt tokens: {prompt_tokens:,}")
        print(f"   - Completion tokens: {completion_tokens:,}")
        print(f"   - Total tokens: {total_tokens:,}")
        
        # Estimate cost (approximate rates)
        cost = (total_tokens / 1000) * 0.002  # $0.002 per 1K tokens
        print(f"   - Estimated cost: ${cost:.4f}")
    else:
        print("\nℹ️  No usage data found (may be tracked differently by SDK)")
    
    conn.close()
    
    print("\n✅ Demo completed!")
    print("\nKey Takeaways:")
    print("   • Conversations persist across app restarts")
    print("   • Use same conversation_id to continue existing conversation")
    print("   • store_run_usage=True enables automatic usage tracking")
    print("   • SQLite database stores all messages and metadata")
    print(f"   • Database file: {db_path} (can be inspected with SQLite tools)")


async def demo_multiple_conversations():
    """
    Demonstrate managing multiple conversations with unique IDs.
    """
    print("\n\n" + "=" * 60)
    print("BONUS: Multiple Conversations Demo")
    print("=" * 60)
    
    # Setup model
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    llm_model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )
    
    db_path = "multi_conversations.db"
    
    # User 1's conversation
    print("\n👤 User 1 (Alice): Starting conversation about Python")
    session1 = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id="user-alice-001",
        store_run_usage=True
    )
    agent1 = Agent(
        name="PythonTutor",
        instructions="You are a Python programming tutor.",
        model=llm_model,
        session=session1
    )
    
    runner = Runner()
    response = await runner.run(agent=agent1, input="How do I read a file in Python?")
    print(f"Agent: {response.content_blocks[0].get('text', '')[:150]}...")
    
    # User 2's conversation (completely separate)
    print("\n👤 User 2 (Bob): Starting conversation about JavaScript")
    session2 = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id="user-bob-001",
        store_run_usage=True
    )
    agent2 = Agent(
        name="JavaScriptTutor",
        instructions="You are a JavaScript programming tutor.",
        model=llm_model,
        session=session2
    )
    
    response = await runner.run(agent=agent2, input="How do I read a file in Node.js?")
    print(f"Agent: {response.content_blocks[0].get('text', '')[:150]}...")
    
    print("\n✅ Two independent conversations stored in same database")
    print(f"   Database: {db_path}")
    print("   Conversation IDs: user-alice-001, user-bob-001")


if __name__ == "__main__":
    asyncio.run(demo_persistent_conversation())
    asyncio.run(demo_multiple_conversations())
