# Advanced SQLite Sessions

## Overview

**AdvancedSQLiteSession** is a powerful development and production-ready session manager that stores conversations in SQLite with advanced features like conversation branching, usage analytics, and soft deletion.

## Key Features

### 1. **Conversation Branching**

- Create alternate conversation paths from any point
- Explore "what-if" scenarios without losing original context
- Undo/redo functionality
- Multiple conversation threads from single starting point

### 2. **Usage Analytics**

- Track token usage per conversation
- Monitor cost per agent run
- Analyze conversation patterns
- Export data for external analysis

### 3. **Soft Deletion**

- Delete conversations without losing data permanently
- Restore deleted conversations
- Audit trail of all operations
- Production-safe deletion patterns

### 4. **Persistent Storage**

- Conversations survive app restarts
- SQLite file-based storage (zero configuration)
- Full ACID guarantees
- Works offline

## When to Use

✅ **Use AdvancedSQLiteSession when:**

- Building development/staging environments
- Need conversation branching for testing
- Want analytics without external databases
- Need persistent conversations on local machines
- Building desktop applications with local storage

❌ **Use PostgreSQL/Redis instead when:**

- Deploying distributed systems (multi-server)
- Need high concurrency (1000+ simultaneous users)
- Require advanced replication
- Building cloud-native applications

## Architecture

```
┌─────────────────────────────────────────┐
│         Your Agent                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    AdvancedSQLiteSession               │
│    • add_items() / get_items()         │
│    • create_branch()                    │
│    • store_run_usage()                  │
│    • soft_delete()                      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    SQLite Database File                 │
│    • conversations table                │
│    • messages table                     │
│    • usage_logs table                   │
│    • branches table                     │
└─────────────────────────────────────────┘
```

## Quick Start

### Basic Setup

```python
from openai_agents.session import AdvancedSQLiteSession

# Create session (auto-creates database file)
session = AdvancedSQLiteSession(
    db_path="conversations.db",
    store_run_usage=True  # Enable usage tracking
)

# Use with agent
agent = Agent(
    name="MyAgent",
    model=llm_model,
    session=session
)
```

### With Conversation ID

```python
# Continue existing conversation
session = AdvancedSQLiteSession(
    db_path="conversations.db",
    conversation_id="user-123-conv-456"
)
```

## Feature Deep Dive

### 1. Conversation Branching

**Use Case:** Test different agent responses or explore alternate conversation paths.

```python
# Main conversation
session = AdvancedSQLiteSession(db_path="app.db", conversation_id="main-conv")
# ... have conversation ...

# Create branch from current point
branch_id = await session.create_branch(
    parent_conversation_id="main-conv",
    branch_name="alternative_path"
)

# Continue on branch
branch_session = AdvancedSQLiteSession(db_path="app.db", conversation_id=branch_id)
# ... different conversation flow ...
```

**Real-World Example:**

```
Main Path: User asks for Python recommendation
  ├─ Branch A: Recommend Flask (minimalist)
  ├─ Branch B: Recommend Django (batteries-included)
  └─ Branch C: Recommend FastAPI (modern async)
```

### 2. Usage Analytics

**Track token usage and costs:**

```python
session = AdvancedSQLiteSession(
    db_path="analytics.db",
    store_run_usage=True  # Enable tracking
)

# Usage is automatically logged during agent runs
# Query usage data:
import sqlite3
conn = sqlite3.connect("analytics.db")
cursor = conn.cursor()

# Total tokens used
cursor.execute("SELECT SUM(prompt_tokens + completion_tokens) FROM usage_logs")
total_tokens = cursor.fetchone()[0]

# Cost per conversation
cursor.execute("""
    SELECT conversation_id,
           SUM(prompt_tokens + completion_tokens) as total_tokens,
           SUM((prompt_tokens * 0.002 + completion_tokens * 0.002) / 1000) as cost
    FROM usage_logs
    GROUP BY conversation_id
""")
```

### 3. Soft Deletion

**Delete safely with restore capability:**

```python
# Soft delete (marks as deleted, doesn't remove)
await session.soft_delete(conversation_id="conv-123")

# Restore if needed
await session.restore(conversation_id="conv-123")

# Hard delete (permanent, use with caution)
await session.hard_delete(conversation_id="conv-123")
```

## Database Schema

### Tables Created

**conversations**

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    deleted_at TIMESTAMP,
    metadata TEXT
);
```

**messages**

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id TEXT,
    role TEXT,
    content TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

**usage_logs** (if store_run_usage=True)

```sql
CREATE TABLE usage_logs (
    id INTEGER PRIMARY KEY,
    conversation_id TEXT,
    run_id TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    timestamp TIMESTAMP
);
```

**branches**

```sql
CREATE TABLE branches (
    id TEXT PRIMARY KEY,
    parent_conversation_id TEXT,
    branch_name TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (parent_conversation_id) REFERENCES conversations(id)
);
```

## Configuration Options

| Parameter         | Type | Default        | Description                                  |
| ----------------- | ---- | -------------- | -------------------------------------------- |
| `db_path`         | str  | Required       | Path to SQLite database file                 |
| `conversation_id` | str  | Auto-generated | Unique conversation identifier               |
| `store_run_usage` | bool | False          | Enable token usage tracking                  |
| `max_messages`    | int  | None           | Max messages to keep (for memory management) |

## Performance Considerations

### File Size Management

SQLite databases can grow large with many conversations:

```python
# Periodic cleanup of old conversations
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Delete conversations older than 30 days
thirty_days_ago = datetime.now() - timedelta(days=30)
cursor.execute("""
    DELETE FROM conversations
    WHERE deleted_at IS NOT NULL
    AND deleted_at < ?
""", (thirty_days_ago,))

conn.commit()
```

### Indexing

The SDK automatically creates indexes, but for custom queries:

```sql
-- Index for faster conversation lookups
CREATE INDEX IF NOT EXISTS idx_messages_conversation
ON messages(conversation_id);

-- Index for usage analytics
CREATE INDEX IF NOT EXISTS idx_usage_conversation
ON usage_logs(conversation_id);
```

## Production Checklist

- [ ] Set `store_run_usage=True` for analytics
- [ ] Implement periodic database cleanup (vacuum/delete old data)
- [ ] Back up database file regularly
- [ ] Set appropriate file permissions on `.db` file
- [ ] Monitor database file size
- [ ] Test branching and restore functionality
- [ ] Document conversation ID naming conventions

## Comparison: SQLite vs PostgreSQL vs Redis

| Feature          | SQLite           | PostgreSQL          | Redis              |
| ---------------- | ---------------- | ------------------- | ------------------ |
| Setup Complexity | Zero config      | Requires server     | Requires server    |
| Concurrency      | Low (file locks) | High                | Very High          |
| Branching        | ✅ Built-in      | ✅ Via SQL          | ❌ Not ideal       |
| Analytics        | ✅ SQL queries   | ✅ Advanced SQL     | ❌ Limited         |
| Distribution     | ❌ Single file   | ✅ Multi-server     | ✅ Multi-server    |
| Best For         | Dev/Desktop apps | Production web apps | High-speed caching |

## Next Steps

1. **Start with `01_basic_advanced_sqlite.py`** - See basic usage with analytics
2. **Explore `02_conversation_branching.py`** - Test branching patterns
3. **Run `03_usage_analytics.py`** - Query analytics data

## Further Reading

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [OpenAI Agents SDK: Session Management](https://github.com/openai/openai-agents-sdk)
- [SQLite Performance Tuning](https://www.sqlite.org/optoverview.html)
