"""Minimal Redis-backed session memory for OpenAI Agents SDK - protocol compliant."""

import json
from typing import List, Optional

import aioredis
from agents.memory import Session


class RedisSession(Session):
    """
    Minimal session memory using Redis for persistent conversation history.
    Implements all required methods: get_items, add_items, pop_item, clear_session.
    Stores each session as a Redis list of JSON-encoded items.
    """

    def __init__(self, session_id: str, redis_url: str = "redis://localhost:6379/0"):
        self.session_id = session_id
        self.redis_url = redis_url
        self.key = f"agent_session:{session_id}"

    async def _get_client(self):
        return await aioredis.from_url(self.redis_url, decode_responses=True)

    async def get_items(self, limit: Optional[int] = None) -> List[dict]:
        client = await self._get_client()
        items = await client.lrange(self.key, 0, -1)
        items = [json.loads(item) for item in items]
        if limit:
            items = items[-limit:]
        return items

    async def add_items(self, items: List[dict]) -> None:
        if not items:
            return
        client = await self._get_client()
        # Store as JSON strings
        await client.rpush(self.key, *[json.dumps(item) for item in items])

    async def pop_item(self) -> Optional[dict]:
        client = await self._get_client()
        item = await client.rpop(self.key)
        return json.loads(item) if item else None

    async def clear_session(self) -> None:
        client = await self._get_client()
        await client.delete(self.key)
