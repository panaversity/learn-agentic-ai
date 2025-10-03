"""
02_production_trimming.py

Production-grade TrimmingSession with logging, metadata tracking, and runtime configuration.

Enhancements over basic version:
- Detailed logging of trim operations
- Metadata preservation (timestamps, user IDs)
- Runtime max_turns adjustment
- Debug mode for troubleshooting
"""

import os
import asyncio
import logging
from collections import deque
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents import Agent, Runner
from agents.models import OpenAIChatCompletionsModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PRODUCTION TRIMMING SESSION
# ============================================================================

class ProductionTrimmingSession:
    """
    Production-grade trimming session with logging and metadata tracking.
    """
    
    def __init__(
        self,
        session_id: str,
        max_turns: int = 5,
        debug: bool = False
    ):
        """
        Args:
            session_id: Unique identifier for this session
            max_turns: Maximum number of user turns to keep
            debug: Enable verbose debug logging
        """
        self.session_id = session_id
        self.max_turns = max(1, int(max_turns))
        self.debug = debug
        self._items: deque = deque()
        self._lock = asyncio.Lock()
        self._trim_count = 0  # Track number of trim operations
        
        logger.info(f"Created TrimmingSession '{session_id}' with max_turns={max_turns}")
    
    async def get_items(self, limit: int | None = None) -> List[Dict[str, Any]]:
        """Return trimmed history."""
        async with self._lock:
            trimmed = self._trim_to_last_turns(list(self._items))
            result = trimmed[-limit:] if (limit is not None and limit >= 0) else trimmed
            
            if self.debug:
                logger.debug(f"get_items: Returning {len(result)} items")
            
            return result
    
    async def add_items(self, items: List[Dict[str, Any]]) -> None:
        """Add items and trim if necessary."""
        if not items:
            return
        
        async with self._lock:
            original_count = len(self._items)
            self._items.extend(items)
            
            # Trim
            trimmed = self._trim_to_last_turns(list(self._items))
            items_dropped = len(self._items) - len(trimmed)
            
            if items_dropped > 0:
                self._trim_count += 1
                logger.info(
                    f"Session '{self.session_id}': Trimmed {items_dropped} items "
                    f"(trim operation #{self._trim_count})"
                )
            
            self._items.clear()
            self._items.extend(trimmed)
            
            if self.debug:
                logger.debug(
                    f"add_items: Added {len(items)} items, "
                    f"context: {original_count} -> {len(self._items)}"
                )
    
    async def pop_item(self) -> Dict[str, Any] | None:
        """Remove and return the most recent item."""
        async with self._lock:
            if self._items:
                item = self._items.pop()
                logger.debug(f"Popped item: {item.get('role', 'unknown')}")
                return item
            return None
    
    async def clear_session(self) -> None:
        """Remove all items."""
        async with self._lock:
            count = len(self._items)
            self._items.clear()
            logger.info(f"Session '{self.session_id}': Cleared {count} items")
    
    async def set_max_turns(self, max_turns: int) -> None:
        """
        Update max_turns at runtime and re-trim if necessary.
        
        Args:
            max_turns: New maximum turn count
        """
        async with self._lock:
            old_max = self.max_turns
            self.max_turns = max(1, int(max_turns))
            
            # Re-trim with new limit
            trimmed = self._trim_to_last_turns(list(self._items))
            items_dropped = len(self._items) - len(trimmed)
            
            self._items.clear()
            self._items.extend(trimmed)
            
            logger.info(
                f"Session '{self.session_id}': Updated max_turns {old_max} -> {self.max_turns}, "
                f"dropped {items_dropped} items"
            )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        async with self._lock:
            history = list(self._items)
            user_turns = sum(1 for item in history if self._is_user_msg(item))
            
            return {
                "session_id": self.session_id,
                "max_turns": self.max_turns,
                "current_items": len(history),
                "current_user_turns": user_turns,
                "total_trim_operations": self._trim_count,
                "debug_enabled": self.debug
            }
    
    def _trim_to_last_turns(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Keep only the last max_turns user messages and everything after."""
        if not items:
            return items
        
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
        """Check if item is a user message."""
        if isinstance(item, dict):
            role = item.get("role")
            if role is not None:
                return role == "user"
            if item.get("type") == "message":
                return item.get("role") == "user"
        
        return getattr(item, "role", None) == "user"


# ============================================================================
# SETUP & DEMO
# ============================================================================

def setup_gemini_model():
    """Configure Gemini model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    return OpenAIChatCompletionsModel(
        model="gemini-2.0-flash-exp",
        openai_client=external_client
    )


async def run_production_demo():
    """Demonstrate production trimming session with logging and stats."""
    print("=" * 80)
    print("PRODUCTION CONTEXT TRIMMING DEMO")
    print("=" * 80)
    print("Features:")
    print("- Detailed logging of trim operations")
    print("- Session statistics tracking")
    print("- Runtime max_turns adjustment")
    print("- Debug mode\n")
    
    # Create model and agent
    llm_model = setup_gemini_model()
    agent = Agent(
        name="Support Assistant",
        model=llm_model,
        instructions=(
            "You are an IT support assistant. "
            "Help with technical issues concisely. "
            "Ask one clarifying question at a time."
        )
    )
    
    # Create production session with debug enabled
    session = ProductionTrimmingSession(
        session_id="prod_demo",
        max_turns=3,
        debug=True
    )
    
    # Test messages
    messages = [
        "My computer is running slow",
        "I have 16GB RAM",
        "There are many browser tabs open",
        "I closed the tabs, still slow",
        "Task manager shows high CPU usage",
        "It's called 'chrome_renderer.exe'",
    ]
    
    for i, user_msg in enumerate(messages, 1):
        print(f"\n{'─' * 80}")
        print(f"TURN {i}")
        print(f"{'─' * 80}")
        print(f"User: {user_msg}")
        
        # Run agent
        result = await Runner.run(agent, user_msg, session=session)
        print(f"Assistant: {result.final_output}")
        
        # Print stats after each turn
        stats = await session.get_stats()
        print(f"\n📊 Stats: {stats['current_user_turns']} turns, "
              f"{stats['current_items']} items, "
              f"{stats['total_trim_operations']} trim ops")
        
        # Demonstrate runtime adjustment after turn 3
        if i == 3:
            print("\n⚙️  Adjusting max_turns from 3 to 5...")
            await session.set_max_turns(5)
    
    # Final statistics
    print("\n" + "=" * 80)
    print("FINAL STATISTICS")
    print("=" * 80)
    final_stats = await session.get_stats()
    for key, value in final_stats.items():
        print(f"{key}: {value}")


async def main():
    """Run production demo."""
    try:
        await run_production_demo()
        
        print("\n✅ Production demo complete!")
        print("💡 Check the logs above to see trim operations")
        print("💡 Next: Try 03_evaluate_trimming.py to measure effectiveness")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
