"""
Advanced SQLite Sessions - Conversation Branching

This example demonstrates conversation branching:
1. Creating alternate conversation paths
2. Exploring "what-if" scenarios
3. Undo/redo patterns
4. Testing different agent responses

Use Cases:
- A/B testing agent responses
- Exploring multiple solutions to same problem
- Debugging conversation flows
- User-facing "try different approach" feature

Run: python 02_conversation_branching.py
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import AdvancedSQLiteSession

load_dotenv()


# ============= BRANCHING UTILITIES =============

async def show_conversation_tree(db_path: str, root_id: str):
    """
    Display conversation tree structure.
    """
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n🌳 Conversation Tree (root: {root_id}):")
    
    # Get all branches
    cursor.execute("""
        SELECT id, parent_conversation_id, branch_name, created_at
        FROM branches
        WHERE parent_conversation_id = ?
        ORDER BY created_at
    """, (root_id,))
    
    branches = cursor.fetchall()
    
    print(f"   └─ {root_id} (main)")
    for branch_id, parent_id, branch_name, created_at in branches:
        print(f"      ├─ {branch_id} ({branch_name})")
    
    conn.close()


async def count_messages(session: AdvancedSQLiteSession) -> int:
    """Count messages in session."""
    items = await session.get_items()
    return len([i for i in items if i.get('role') in ['user', 'assistant']])


# ============= DEMO: PRODUCT RECOMMENDATION BRANCHING =============

async def demo_product_recommendation_branching():
    """
    Demonstrate branching to test different recommendation approaches.
    
    Scenario: Customer asks for laptop recommendation.
    We'll create 3 branches to test different recommendation strategies.
    """
    print("=" * 60)
    print("CONVERSATION BRANCHING DEMO")
    print("Testing Different Product Recommendation Approaches")
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
    
    db_path = "branching_demo.db"
    main_conv_id = "main-product-recommendation"
    
    # ===== Main Conversation Path =====
    print("\n" + "─" * 60)
    print("MAIN CONVERSATION")
    print("─" * 60)
    
    main_session = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id=main_conv_id,
        store_run_usage=True
    )
    
    # Initial turns (common to all branches)
    agent = Agent(
        name="ProductAdvisor",
        instructions="You are a helpful product recommendation assistant.",
        model=llm_model,
        session=main_session
    )
    
    runner = Runner()
    
    print("\nUser: I need a laptop for software development")
    response = await runner.run(
        agent=agent,
        input="I need a laptop for software development"
    )
    print(f"Agent: {response.content_blocks[0].get('text', '')[:200]}...")
    
    print("\nUser: My budget is around $1500")
    response = await runner.run(
        agent=agent,
        input="My budget is around $1500"
    )
    print(f"Agent: {response.content_blocks[0].get('text', '')[:200]}...")
    
    main_messages = await count_messages(main_session)
    print(f"\n📊 Main conversation: {main_messages} messages")
    
    # ===== Branch A: Performance-Focused =====
    print("\n" + "─" * 60)
    print("BRANCH A: Performance-Focused Recommendations")
    print("─" * 60)
    
    # Create branch
    branch_a_id = await main_session.create_branch(
        parent_conversation_id=main_conv_id,
        branch_name="performance_focused"
    )
    print(f"✅ Created branch: {branch_a_id}")
    
    # Continue on branch A
    branch_a_session = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id=branch_a_id,
        store_run_usage=True
    )
    
    agent_a = Agent(
        name="ProductAdvisor",
        instructions="""You are a product advisor focusing on HIGH PERFORMANCE.
Recommend laptops with powerful CPUs, lots of RAM, and fast SSDs.
Emphasize performance benchmarks and specs.""",
        model=llm_model,
        session=branch_a_session
    )
    
    print("\nUser: What specific models do you recommend?")
    response = await runner.run(
        agent=agent_a,
        input="What specific models do you recommend?"
    )
    print(f"Agent: {response.content_blocks[0].get('text', '')[:300]}...")
    
    branch_a_messages = await count_messages(branch_a_session)
    print(f"\n📊 Branch A: {branch_a_messages} messages (includes inherited context)")
    
    # ===== Branch B: Budget-Focused =====
    print("\n" + "─" * 60)
    print("BRANCH B: Budget-Focused Recommendations")
    print("─" * 60)
    
    # Create branch from main (not from Branch A)
    branch_b_id = await main_session.create_branch(
        parent_conversation_id=main_conv_id,
        branch_name="budget_focused"
    )
    print(f"✅ Created branch: {branch_b_id}")
    
    branch_b_session = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id=branch_b_id,
        store_run_usage=True
    )
    
    agent_b = Agent(
        name="ProductAdvisor",
        instructions="""You are a product advisor focusing on BEST VALUE.
Recommend laptops that maximize bang-for-buck.
Emphasize cost savings, good-enough specs, and deals.""",
        model=llm_model,
        session=branch_b_session
    )
    
    print("\nUser: What specific models do you recommend?")
    response = await runner.run(
        agent=agent_b,
        input="What specific models do you recommend?"
    )
    print(f"Agent: {response.content_blocks[0].get('text', '')[:300]}...")
    
    branch_b_messages = await count_messages(branch_b_session)
    print(f"\n📊 Branch B: {branch_b_messages} messages")
    
    # ===== Branch C: Portability-Focused =====
    print("\n" + "─" * 60)
    print("BRANCH C: Portability-Focused Recommendations")
    print("─" * 60)
    
    branch_c_id = await main_session.create_branch(
        parent_conversation_id=main_conv_id,
        branch_name="portability_focused"
    )
    print(f"✅ Created branch: {branch_c_id}")
    
    branch_c_session = AdvancedSQLiteSession(
        db_path=db_path,
        conversation_id=branch_c_id,
        store_run_usage=True
    )
    
    agent_c = Agent(
        name="ProductAdvisor",
        instructions="""You are a product advisor focusing on PORTABILITY.
Recommend lightweight laptops with long battery life.
Emphasize weight, battery hours, and travel-friendliness.""",
        model=llm_model,
        session=branch_c_session
    )
    
    print("\nUser: What specific models do you recommend?")
    response = await runner.run(
        agent=agent_c,
        input="What specific models do you recommend?"
    )
    print(f"Agent: {response.content_blocks[0].get('text', '')[:300]}...")
    
    branch_c_messages = await count_messages(branch_c_session)
    print(f"\n📊 Branch C: {branch_c_messages} messages")
    
    # ===== Show Tree Structure =====
    await show_conversation_tree(db_path, main_conv_id)
    
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    
    print("\n✅ Branching Benefits Demonstrated:")
    print("   • Tested 3 different recommendation strategies")
    print("   • Each branch inherits initial context (budget, use case)")
    print("   • Different agent instructions per branch")
    print("   • Original conversation (main) remains unchanged")
    print("\n💡 Use Cases:")
    print("   • A/B testing agent prompts")
    print("   • Exploring multiple solutions")
    print("   • User-facing 'try different approach' button")
    print("   • Debugging conversation flows")


async def demo_undo_redo_pattern():
    """
    Demonstrate undo/redo pattern using branching.
    """
    print("\n\n" + "=" * 60)
    print("UNDO/REDO PATTERN DEMO")
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
    
    db_path = "undo_redo_demo.db"
    conv_id = "writing-assistant"
    
    # Initial conversation
    session = AdvancedSQLiteSession(db_path=db_path, conversation_id=conv_id)
    agent = Agent(
        name="WritingAssistant",
        instructions="You are a creative writing assistant. Help improve text.",
        model=llm_model,
        session=session
    )
    
    runner = Runner()
    
    print("\n📝 User writes draft:")
    print("   'The cat jumped over the fence quickly.'")
    
    response = await runner.run(
        agent=agent,
        input="Improve this: 'The cat jumped over the fence quickly.'"
    )
    version_1 = response.content_blocks[0].get('text', '')
    print(f"\n✏️  Version 1: {version_1[:150]}...")
    
    print("\n❌ User doesn't like it, wants to try different style")
    
    # Create branch for alternate version
    alt_branch_id = await session.create_branch(
        parent_conversation_id=conv_id,
        branch_name="alternate_style"
    )
    
    alt_session = AdvancedSQLiteSession(db_path=db_path, conversation_id=alt_branch_id)
    alt_agent = Agent(
        name="WritingAssistant",
        instructions="You are a creative writing assistant. Make text more poetic and descriptive.",
        model=llm_model,
        session=alt_session
    )
    
    response = await runner.run(
        agent=alt_agent,
        input="Make it more poetic"
    )
    version_2 = response.content_blocks[0].get('text', '')
    print(f"\n✏️  Version 2 (alternate): {version_2[:150]}...")
    
    print("\n✅ User can now:")
    print("   • Continue with version 1 (original conversation)")
    print("   • Continue with version 2 (alternate branch)")
    print("   • Create more branches to try other styles")
    print("   • Compare results side-by-side")


if __name__ == "__main__":
    asyncio.run(demo_product_recommendation_branching())
    asyncio.run(demo_undo_redo_pattern())
