"""
01_basic_trimming.py

Minimal TrimmingSession implementation demonstrating context trimming pattern.

This script shows how to:
1. Implement a custom session that keeps only the last N turns
2. Define turn boundaries (user message + all responses until next user)
3. Automatically trim older context

Based on: https://cookbook.openai.com/examples/agents_sdk/session_memory
"""

import os
import asyncio
from collections import deque
from typing import List, Dict, Any
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents import Agent, Runner
from agents.models import OpenAIChatCompletionsModel

# Load environment variables
load_dotenv()

# ============================================================================
# TRIMMING SESSION IMPLEMENTATION
# ============================================================================

class TrimmingSession:
    """
    Keep only the last N user turns in memory.
    
    A turn = one user message + all subsequent items (assistant/tool calls/results)
    up to (but not including) the next user message.
    """
    
    def __init__(self, session_id: str, max_turns: int = 5):
        """
        Args:
            session_id: Unique identifier for this session
            max_turns: Maximum number of user turns to keep (default: 5)
        """
        self.session_id = session_id
        self.max_turns = max(1, int(max_turns))
        self._items: deque = deque()  # Chronological message log
        self._lock = asyncio.Lock()
    
    async def get_items(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """
        Return history trimmed to the last N user turns.
        
        Args:
            limit: Optional limit to most recent items (applied after trimming)
            
        Returns:
            List of message dictionaries
        """
        async with self._lock:
            trimmed = self._trim_to_last_turns(list(self._items))
            return trimmed[-limit:] if (limit is not None and limit >= 0) else trimmed
    
    async def add_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Append new items, then trim to last N user turns.
        
        Args:
            items: List of new messages to add
        """
        if not items:
            return
        
        async with self._lock:
            self._items.extend(items)
            trimmed = self._trim_to_last_turns(list(self._items))
            self._items.clear()
            self._items.extend(trimmed)
    
    async def pop_item(self) -> Dict[str, Any] | None:
        """Remove and return the most recent item."""
        async with self._lock:
            return self._items.pop() if self._items else None
    
    async def clear_session(self) -> None:
        """Remove all items for this session."""
        async with self._lock:
            self._items.clear()
    
    def _trim_to_last_turns(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keep only the last `max_turns` user messages and everything after
        the earliest of those user messages.
        
        Args:
            items: Full message history
            
        Returns:
            Trimmed message history
        """
        if not items:
            return items
        
        # Count user messages from end, find where to start keeping
        count = 0
        start_idx = 0
        
        for i in range(len(items) - 1, -1, -1):
            if self._is_user_msg(items[i]):
                count += 1
                if count == self.max_turns:
                    start_idx = i
                    break
        
        return items[start_idx:]
    
    @staticmethod
    def _is_user_msg(item: Dict[str, Any]) -> bool:
        """Check if item is a user message (not synthetic)."""
        if isinstance(item, dict):
            role = item.get("role")
            if role is not None:
                return role == "user"
            # Handle message type format
            if item.get("type") == "message":
                return item.get("role") == "user"
        
        # Fallback: check .role attribute
        return getattr(item, "role", None) == "user"


# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def setup_gemini_model():
    """Configure Gemini model using OpenAI-compatible API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    return OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )


# ============================================================================
# DEMO: CUSTOMER SUPPORT AGENT
# ============================================================================

async def run_demo():
    """
    Demonstrate context trimming with a customer support scenario.
    
    The agent helps with multiple issues over several turns. With max_turns=3,
    only the last 3 user turns are kept in context.
    """
    print("=" * 80)
    print("CONTEXT TRIMMING DEMO")
    print("=" * 80)
    print(f"Configuration: max_turns=3")
    print(f"Scenario: Customer support with multiple issues\n")
    
    # Create Gemini model
    llm_model = setup_gemini_model()
    
    # Create support agent
    agent = Agent(
        name="Support Assistant",
        model=llm_model,
        instructions=(
            "You are a patient IT support assistant. "
            "Help users troubleshoot issues step by step. "
            "Be concise and ask one question at a time."
        )
    )
    
    # Create trimming session (keep last 3 turns)
    session = TrimmingSession("demo_session", max_turns=3)
    
    # Simulate multi-turn conversation
    messages = [
        "My laptop won't start. There's a red light blinking.",
        "I tried that, still not working. What else can I try?",
        "Okay, it's charging now. But now I have a different issue - my WiFi won't connect.",
        "I restarted the router but still can't connect.",
        "Great, WiFi is working! One more thing - my battery drains really fast.",
        "I checked, it's set to balanced mode.",
    ]
    
    for i, user_msg in enumerate(messages, 1):
        print(f"\n{'─' * 80}")
        print(f"TURN {i}")
        print(f"{'─' * 80}")
        print(f"User: {user_msg}\n")
        
        # Run agent
        result = await Runner.run(agent, user_msg, session=session)
        
        print(f"Assistant: {result.final_output}\n")
        
        # Show current context size
        history = await session.get_items()
        user_turns = sum(1 for item in history if session._is_user_msg(item))
        total_items = len(history)
        
        print(f"Context: {user_turns} user turns, {total_items} total items")
        
        # Show what's in context
        if i >= 4:  # After turn 4, trimming starts
            print(f"⚠️  Note: Only last 3 turns kept in context (older turns dropped)")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run the demo."""
    try:
        await run_demo()
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("✅ Successfully demonstrated context trimming")
        print("📊 Key observations:")
        print("   - First 3 turns: Context grows normally")
        print("   - Turn 4+: Oldest turns dropped, context size stabilizes")
        print("   - Agent maintains focus on recent issues")
        print("\n💡 Next: Try 02_production_trimming.py for enhanced version")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure GEMINI_API_KEY is set in .env file")


if __name__ == "__main__":
    asyncio.run(main())
