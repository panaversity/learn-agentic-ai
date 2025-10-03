"""
Context Summarization - Basic Implementation

This example demonstrates how to use LLMSummarizer and SummarizingSession
to compress older conversation history while preserving key information.

Key Concepts:
1. LLMSummarizer - Uses LLM to create concise summaries
2. SummarizingSession - Keeps recent turns + summary of older context
3. keep_turns - Number of recent turns to keep verbatim

Run: python 01_basic_summarization.py
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai_agents import Agent, Runner
from openai_agents.models import OpenAIChatCompletionsModel
from openai_agents.session import LLMSummarizer, SummarizingSession

load_dotenv()


# ============= LLM SUMMARIZER =============

def create_summarizer(llm_model) -> LLMSummarizer:
    """
    Create an LLM-based summarizer that compresses conversation history.
    
    The summarizer uses a system prompt to guide summary creation.
    """
    return LLMSummarizer(
        model=llm_model,
        system_message="""Summarize the conversation history, preserving:
1. User's main goals and preferences
2. Key decisions or commitments made
3. Important names, dates, or numbers
4. Open questions or next steps

Keep the summary concise (under 150 words).""",
        max_tokens=300  # Limit summary token usage
    )


# ============= DEMO: TRAVEL PLANNING AGENT =============

async def demo_travel_planning():
    """
    Demonstrate summarization with a long travel planning conversation.
    
    We'll simulate 10+ turns and show how summarization keeps context manageable.
    """
    print("=" * 60)
    print("CONTEXT SUMMARIZATION DEMO")
    print("Travel Planning Agent with Long Conversation")
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
    
    # Create summarizer and session
    summarizer = create_summarizer(llm_model)
    session = SummarizingSession(
        summarizer=summarizer,
        keep_turns=3  # Keep only last 3 turns verbatim, summarize rest
    )
    
    # Create travel planning agent
    agent = Agent(
        name="TravelPlanningAgent",
        instructions="""You are a helpful travel planning assistant.
Help users plan their trips by asking about destination, dates, budget, and preferences.
Be conversational and remember details from earlier in the conversation.""",
        model=llm_model,
        session=session
    )
    
    # Simulate a long conversation (10 turns)
    conversation_turns = [
        "I'm planning a trip to Japan",
        "Next April, around the 10th to 20th",
        "I have about $3000 budget",
        "I prefer boutique hotels over chains",
        "I'm interested in temples and traditional culture",
        "Yes, especially in Kyoto",
        "What about cherry blossoms? Will they be blooming?",
        "That sounds perfect! What areas in Kyoto should I stay?",
        "I'd like to visit Tokyo too. How many days in each city?",
        "Can you recommend specific hotels in Kyoto?"
    ]
    
    print("\nStarting conversation...\n")
    
    runner = Runner()
    for i, user_message in enumerate(conversation_turns, 1):
        print(f"\n{'─' * 60}")
        print(f"Turn {i}/10")
        print(f"{'─' * 60}")
        print(f"User: {user_message}")
        
        # Run agent
        response = await runner.run(agent=agent, input=user_message)
        print(f"Agent: {response.content_blocks[0].get('text', '')[:200]}...")
        
        # Show session state
        items = await session.get_items()
        
        # Count summary vs verbatim messages
        summary_count = sum(1 for item in items 
                          if item.get("role") == "system" 
                          and "summary" in item.get("content", "").lower())
        message_count = len([item for item in items if item.get("role") in ["user", "assistant"]])
        
        print(f"\n📊 Session State:")
        print(f"   - Summary messages: {summary_count}")
        print(f"   - Verbatim messages: {message_count}")
        print(f"   - Total context items: {len(items)}")
        
        # Show when summarization happened
        if i > 3 and summary_count > 0:
            print(f"   ✅ Older context has been summarized")
    
    print("\n" + "=" * 60)
    print("FINAL SESSION STATE")
    print("=" * 60)
    
    final_items = await session.get_items()
    print(f"\nTotal items in session: {len(final_items)}")
    
    # Show the summary if it exists
    for item in final_items:
        if item.get("role") == "system" and "summary" in item.get("content", "").lower():
            print(f"\n📝 Summary of older context:")
            print(f"{item['content'][:300]}...")
            break
    
    print(f"\n✅ Recent turns kept verbatim: {session.keep_turns}")
    print("\nℹ️  Without summarization, all 10 turns would be in context.")
    print("   With summarization, only last 3 turns + summary are kept.")


if __name__ == "__main__":
    asyncio.run(demo_travel_planning())
