# Custom Session Memory Backends for OpenAI Agents SDK

This folder contains examples of custom session memory implementations for the OpenAI Agents SDK, enabling persistent conversation history beyond the default in-memory or SQLite options. These are useful for production systems where you need scalable, reliable storage for agent sessions.

## Why Custom Sessions?

- **Persistence:** Store chat history beyond process restarts.
- **Scalability:** Use robust databases for multi-user, distributed deployments.
- **Flexibility:** Integrate with your existing infrastructure (e.g., Supabase, Redis, PostgreSQL).

All examples implement the `Session` protocol from the OpenAI Agents SDK, so you can drop them into your agent code with minimal changes.

---

## 1. Supabase Session (Minimal Example)

- **File:** `supabase_session.py`
- **Backend:** [Supabase](https://supabase.com/) (PostgreSQL + REST API)
- **Purpose:** Demonstrates how to use a cloud database for session memory.
- **Usage:**
  ```python
  from custom_sessions.supabase_session import SupabaseSessionMinimal
  session = SupabaseSessionMinimal(session_id="my-session-id")
  # Use with your agent as session=session
  ```
- **Note:** You must implement the actual Supabase connection logic.

---

## 2. Redis Session (Production-Ready)

- **File:** `redis_session.py`
- **Backend:** [Redis](https://redis.io/) (via `aioredis`)
- **Purpose:** Fast, scalable, in-memory session storage for production systems.
- **Requirements:**
  - Redis server running (local or cloud)
  - `aioredis` Python package (`uv add aioredis`)
- **Usage:**
  ```python
  from custom_sessions.redis_session import RedisSession
  session = RedisSession(session_id="my-session-id", redis_url="redis://localhost:6379/0")
  # Use with your agent as session=session
  ```
- **Protocol Compliance:** Implements all required methods (`get_items`, `add_items`, `pop_item`, `clear_session`).

---

## 3. PostgreSQL Session (Production-Ready)

- **File:** `postgres_session.py`
- **Backend:** [PostgreSQL](https://www.postgresql.org/) (via `asyncpg`)
- **Purpose:** Durable, scalable session storage using a relational database.
- **Requirements:**
  - PostgreSQL server running
  - `asyncpg` Python package (`uv add asyncpg`)
  - Table `agent_sessions` with columns:
    - `id SERIAL PRIMARY KEY`
    - `session_id TEXT`
    - `role TEXT`
    - `content TEXT`
    - `created_at TIMESTAMP`
- **Usage:**
  ```python
  from custom_sessions.postgres_session import PostgresSession
  session = PostgresSession(session_id="my-session-id", dsn="postgresql://user:password@localhost:5432/yourdb")
  # Use with your agent as session=session
  ```
- **Protocol Compliance:** Implements all required methods (`get_items`, `add_items`, `pop_item`, `clear_session`).

---

## How to Use

1. Choose the backend that fits your deployment (Supabase, Redis, PostgreSQL, or build your own).
2. Instantiate the session class with a unique `session_id` for each user/conversation.
3. Pass the session instance to your agent:
   ```python
   agent = MyAgent(..., session=session)
   ```
4. The agent will now use your custom backend for storing and retrieving conversation history.

---

## Extending Further

- You can implement your own session backend by following the same protocol.
- Add authentication, encryption, or custom logic as needed for your use case.

---

## See Also

- [OpenAI Agents SDK: Sessions Documentation](https://openai.github.io/openai-agents-python/sessions/)
