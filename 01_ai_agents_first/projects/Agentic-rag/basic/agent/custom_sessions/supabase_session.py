"""Minimal Supabase-backed session memory for OpenAI Agents SDK - follows protocol exactly."""

import datetime
from typing import List, Optional

from agents.memory import Session

from ..database.connection import supabase_manager
from ..utils.logger import logger


class SupabaseSessionMinimal(Session):
    """
    Minimal session memory using Supabase for persistent conversation history.
    Follows OpenAI Agents SDK Session protocol exactly.

    Protocol Compliance:
    - Implements all required methods: get_items, add_items, pop_item, clear_session
    - Returns items in standard format: {"role": str, "content": str}
    - Supports optional limit parameter in get_items
    - Handles session_id as constructor parameter
    - Uses proper type hints matching the official SDK
    """

    def __init__(self, session_id: str):
        if not session_id or not isinstance(session_id, str):
            raise ValueError("session_id must be a non-empty string")
        self.session_id = session_id

    async def get_items(self, limit: Optional[int] = None) -> List[dict]:
        """
        Retrieve session items with optional limit.

        Protocol compliance: Returns items in format {"role": str, "content": str}
        """
        try:
            client = await supabase_manager.ensure_connected()
            query = (
                client.table("agent_sessions")
                .select("role, content")
                .eq("session_id", self.session_id)
                .order("created_at")
            )
            if limit:
                query = query.limit(limit)

            response = query.execute()
            data = response.data if response.data else []

            return [
                {
                    "role": row["role"],
                    "content": row["content"],
                }
                for row in data
            ]
        except Exception as e:
            logger.warning(
                f"Error retrieving session items for {self.session_id}: {str(e)}"
            )
            return []

    async def add_items(self, items: List[dict]) -> None:
        """
        Add multiple items to session with batch insert for performance.

        Protocol compliance: Accepts list[TResponseInputItem] -> List[dict]
        Filters out non-message items and transforms function calls appropriately.
        """
        if not items:
            return

        try:
            client = await supabase_manager.ensure_connected()

            # Validate and prepare batch data
            batch_data = []
            for i, item in enumerate(items):
                # Skip items that don't have the required structure
                if not isinstance(item, dict):
                    logger.warning(f"Skipping non-dict item: {type(item)}")
                    continue

                # Handle different item types from OpenAI Agents SDK
                if "role" in item and "content" in item:
                    # Standard message item
                    role = item["role"]
                    content = item["content"]
                elif item.get("type") == "function_call":
                    # Function call item - convert to assistant message
                    role = "assistant"
                    content = f"Function call: {item.get('name', 'unknown')}"
                elif item.get("type") == "function_call_output":
                    # Function call output - convert to assistant message
                    role = "assistant"
                    content = f"Function result: {item.get('output', 'No output')}"
                else:
                    # Skip unrecognized items
                    logger.warning(
                        f"Skipping unrecognized item type: {item.get('type', 'unknown')}"
                    )
                    continue

                # Use provided created_at or generate unique timestamp
                if item.get("created_at"):
                    created_at = item["created_at"]
                else:
                    # Add microsecond offset to ensure uniqueness
                    now = datetime.datetime.utcnow()
                    created_at = (now + datetime.timedelta(microseconds=i)).isoformat()

                batch_data.append(
                    {
                        "session_id": self.session_id,
                        "role": role,
                        "content": content,
                        "created_at": created_at,
                    }
                )

            if not batch_data:
                logger.info(f"No valid items to add for session {self.session_id}")
                return

            # Batch insert for better performance
            response = client.table("agent_sessions").insert(batch_data).execute()
            logger.info(f"Added {len(batch_data)} items to session {self.session_id}")

        except Exception as e:
            logger.error(f"Failed to add session items for {self.session_id}: {str(e)}")
            raise Exception(f"Failed to add session items: {str(e)}") from e

    async def pop_item(self) -> Optional[dict]:
        """
        Remove and return the most recent item from session with transaction safety.

        Protocol compliance: Returns TResponseInputItem | None -> Optional[dict]
        """
        try:
            client = await supabase_manager.ensure_connected()

            # Use transaction to prevent race conditions
            async with client.transaction():
                response = (
                    client.table("agent_sessions")
                    .select("id, role, content")
                    .eq("session_id", self.session_id)
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )

                data = response.data if response.data else []

                if not data:
                    return None

                last_item = data[0]
                client.table("agent_sessions").delete().eq(
                    "id", last_item["id"]
                ).execute()

                return {
                    "role": last_item["role"],
                    "content": last_item["content"],
                }

        except Exception as e:
            logger.warning(
                f"Error popping session item for {self.session_id}: {str(e)}"
            )
            return None

    async def clear_session(self) -> None:
        """
        Clear all items for this session.

        Handles empty sessions gracefully - no error if session doesn't exist.
        """
        try:
            client = await supabase_manager.ensure_connected()
            response = (
                client.table("agent_sessions")
                .delete()
                .eq("session_id", self.session_id)
                .execute()
            )

            logger.info(f"Cleared session {self.session_id}")

        except Exception as e:
            logger.warning(f"Error clearing session {self.session_id}: {str(e)}")

    async def has_items(self) -> bool:
        """
        Check if the session has any items.

        Returns:
            True if session has items, False otherwise
        """
        try:
            items = await self.get_items(limit=1)
            return len(items) > 0
        except Exception as e:
            logger.warning(
                f"Error checking session items for {self.session_id}: {str(e)}"
            )
            return False

    async def get_session_info(self) -> dict:
        """
        Get session information including item count and timestamps.

        Returns:
            Dictionary with session metadata
        """
        try:
            client = await supabase_manager.ensure_connected()
            response = (
                client.table("agent_sessions")
                .select("created_at, role")
                .eq("session_id", self.session_id)
                .order("created_at")
                .execute()
            )

            data = response.data if response.data else []

            if not data:
                return {
                    "session_id": self.session_id,
                    "item_count": 0,
                    "first_message": None,
                    "last_message": None,
                    "has_items": False,
                }

            return {
                "session_id": self.session_id,
                "item_count": len(data),
                "first_message": data[0]["created_at"] if data else None,
                "last_message": data[-1]["created_at"] if data else None,
                "has_items": True,
            }

        except Exception as e:
            logger.warning(
                f"Error getting session info for {self.session_id}: {str(e)}"
            )
            return {
                "session_id": self.session_id,
                "item_count": 0,
                "first_message": None,
                "last_message": None,
                "has_items": False,
                "error": str(e),
            }
