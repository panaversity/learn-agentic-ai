from __future__ import annotations

import asyncio, os
from dotenv import load_dotenv

from typing import Deque, List
from collections import deque

from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, SessionABC, TResponseInputItem

load_dotenv()

ROLE_USER = "user"

def _is_user_msg(item: TResponseInputItem) -> bool:
    """Return True if the item represents a user message."""
    # Common dict-shaped messages
    if isinstance(item, dict):
        role = item.get("role")
        if role is not None:
            return role == ROLE_USER
        # Some SDKs: {"type": "message", "role": "..."}
        if item.get("type") == "message":
            return item.get("role") == ROLE_USER
    # Fallback: objects with a .role attr
    return getattr(item, "role", None) == ROLE_USER


class TrimmingSession(SessionABC):
    """
    Keep only the last N *user turns* in memory.

    A turn = a user message and all subsequent items (assistant/tool calls/results)
    up to (but not including) the next user message.
    """

    def __init__(self, session_id: str, max_turns: int = 8):
        self.session_id = session_id
        self.max_turns = max(1, int(max_turns))
        self._items: Deque[TResponseInputItem] = deque()  # chronological log
        self._lock = asyncio.Lock()

    # ---- SessionABC API ----

    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        """Return history trimmed to the last N user turns (optionally limited to most-recent `limit` items)."""
        async with self._lock:
            trimmed = self._trim_to_last_turns(list(self._items))
            return trimmed[-limit:] if (limit is not None and limit >= 0) else trimmed

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        """Append new items, then trim to last N user turns."""
        if not items:
            return
        async with self._lock:
            self._items.extend(items)
            trimmed = self._trim_to_last_turns(list(self._items))
            self._items.clear()
            self._items.extend(trimmed)

    async def pop_item(self) -> TResponseInputItem | None:
        """Remove and return the most recent item (post-trim)."""
        async with self._lock:
            return self._items.pop() if self._items else None

    async def clear_session(self) -> None:
        """Remove all items for this session."""
        async with self._lock:
            self._items.clear()

    # ---- Helpers ----

    def _trim_to_last_turns(self, items: List[TResponseInputItem]) -> List[TResponseInputItem]:
        """
        Keep only the suffix containing the last `max_turns` user messages and everything after
        the earliest of those user messages.

        If there are fewer than `max_turns` user messages (or none), keep all items.
        """
        if not items:
            return items

        count = 0
        start_idx = 0  # default: keep all if we never reach max_turns

        # Walk backward; when we hit the Nth user message, mark its index.
        for i in range(len(items) - 1, -1, -1):
            if _is_user_msg(items[i]):
                count += 1
                if count == self.max_turns:
                    start_idx = i
                    break

        return items[start_idx:]

    # ---- Optional convenience API ----

    async def set_max_turns(self, max_turns: int) -> None:
        async with self._lock:
            self.max_turns = max(1, int(max_turns))
            trimmed = self._trim_to_last_turns(list(self._items))
            self._items.clear()
            self._items.extend(trimmed)

    async def raw_items(self) -> List[TResponseInputItem]:
        """Return the untrimmed in-memory log (for debugging)."""
        async with self._lock:
            return list(self._items)



# ============================================================================
# SETUP FUNCTIONS
# ============================================================================

def setup_gemini_model():
    """Configure Gemini model using OpenAI-compatible API."""
    api_key = os.getenv("GEMINI_API_KEY")

    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    return OpenAIChatCompletionsModel(
        model="gemini-2.5-flash-lite",
        openai_client=external_client
    )


# ============================================================================
# DEMO: CUSTOMER SUPPORT AGENT
# ============================================================================

# Keep only the last 8 turns (user + assistant/tool interactions)
session = TrimmingSession("my_session", max_turns=3)

# Create Gemini model
llm_model = setup_gemini_model()

# Create support agent
support_agent = Agent(
    name="Support Assistant",
    model=llm_model,
    instructions=(
        "You are a patient IT support assistant. "
        "Help users troubleshoot issues step by step. "
        "Be concise and ask one question at a time."
    )
)
async def main():

    message = "There is a red light blinking on my laptop."

    result = await Runner.run(
            support_agent,
            message,
            session=session
        )

    print(f"\nAssistant: {result.final_output}\n")

    history = await session.get_items()
    print(f"\n\n[HISTORY]: {history}\n\n")

    # Example flow
    await session.add_items([{"role": "user", "content": "I am using a macbook pro and it has some overheating issues too."}])
    await session.add_items([{"role": "assistant", "content": "I see. Let's check your firmware version."}])
    await session.add_items([{"role": "user", "content": "Firmware v1.0.3; still failing."}])
    await session.add_items([{"role": "assistant", "content": "Could you please try a factory reset?"}])
    await session.add_items([{"role": "user", "content": "Reset done; error 42 now."}])
    await session.add_items([{"role": "assistant", "content": "Leave it on charge for 30 minutes in case the battery is critically low. Is there any other error message?"}])
    await session.add_items([{"role": "user", "content": "Yes, I see error 404 now."}])
    await session.add_items([{"role": "assistant", "content": "Do you see it on the browser while accessing a website?"}])
    # At this point, with max_turns=3, everything *before* the earliest of the last 3 user
    # messages is summarized into a synthetic pair, and the last 3 turns remain verbatim.

    history = await session.get_items()
    print(f"\n\n[HISTORY_LENGTH AFTER ADD ITEMS]: {len(history)}\n\n")
    print(f"\n\n[HISTORY AFTER ADD ITEMS]: {history}\n\n")

    # Call agent again
    result = await Runner.run(
        support_agent,
        "Share total messages I sent on this session",
        session=session
    )
    print(f"\nAssistant: {result.final_output}\n")

# Pass `history` into your agent runner / responses call as the conversation context.

if __name__ == "__main__":
    asyncio.run(main())
