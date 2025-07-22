"""Minimal PostgreSQL-backed session memory for OpenAI Agents SDK - protocol compliant."""

import datetime
from typing import List, Optional

import asyncpg
from agents.memory import Session


class PostgresSession(Session):
    """
    Minimal session memory using PostgreSQL for persistent conversation history.
    Implements all required methods: get_items, add_items, pop_item, clear_session.
    Assumes a table 'agent_sessions' with columns (session_id, role, content, created_at, id serial primary key).
    """

    def __init__(
        self,
        session_id: str,
        dsn: str = "postgresql://user:password@localhost:5432/yourdb",
    ):
        self.session_id = session_id
        self.dsn = dsn

    async def _get_conn(self):
        return await asyncpg.connect(self.dsn)

    async def get_items(self, limit: Optional[int] = None) -> List[dict]:
        conn = await self._get_conn()
        try:
            query = """
                SELECT role, content FROM agent_sessions
                WHERE session_id = $1
                ORDER BY created_at
            """
            if limit:
                query += " LIMIT $2"
                rows = await conn.fetch(query, self.session_id, limit)
            else:
                rows = await conn.fetch(query, self.session_id)
            return [{"role": r["role"], "content": r["content"]} for r in rows]
        finally:
            await conn.close()

    async def add_items(self, items: List[dict]) -> None:
        if not items:
            return
        conn = await self._get_conn()
        try:
            now = datetime.datetime.utcnow()
            for i, item in enumerate(items):
                await conn.execute(
                    """
                    INSERT INTO agent_sessions (session_id, role, content, created_at)
                    VALUES ($1, $2, $3, $4)
                    """,
                    self.session_id,
                    item.get("role", "assistant"),
                    item.get("content", ""),
                    now + datetime.timedelta(microseconds=i),
                )
        finally:
            await conn.close()

    async def pop_item(self) -> Optional[dict]:
        conn = await self._get_conn()
        try:
            row = await conn.fetchrow(
                """
                SELECT id, role, content FROM agent_sessions
                WHERE session_id = $1
                ORDER BY created_at DESC
                LIMIT 1
                """,
                self.session_id,
            )
            if not row:
                return None
            await conn.execute("DELETE FROM agent_sessions WHERE id = $1", row["id"])
            return {"role": row["role"], "content": row["content"]}
        finally:
            await conn.close()

    async def clear_session(self) -> None:
        conn = await self._get_conn()
        try:
            await conn.execute(
                "DELETE FROM agent_sessions WHERE session_id = $1", self.session_id
            )
        finally:
            await conn.close()
