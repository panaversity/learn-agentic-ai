# PostgreSQL Sessions

## Overview

**PostgreSQL Sessions** provide production-grade session management backed by PostgreSQL database. Ideal for multi-server deployments, high concurrency applications, and enterprise environments requiring ACID guarantees and advanced database features.

## Key Features

- **Production-Ready**: Battle-tested RDBMS with ACID guarantees
- **High Concurrency**: Handle thousands of simultaneous connections
- **Advanced Queries**: Full SQL capabilities for complex analytics
- **Scalability**: Vertical and horizontal scaling options
- **Replication**: Built-in primary-replica replication
- **Backups**: Point-in-time recovery, pg_dump, continuous archiving
- **Security**: Row-level security, encryption, role-based access

## When to Use

✅ **Use PostgreSQL Sessions when:**

- Deploying production web applications
- Need high concurrency (100+ simultaneous users)
- Require advanced analytics and reporting
- Need multi-server deployment with shared state
- Compliance requires ACID transactions
- Want production-grade backup/recovery

❌ **Use SQLite instead when:**

- Building local/desktop applications
- Single-user or low concurrency
- Want zero configuration
- Don't need distributed deployment

## Architecture

```
┌─────────────────────────────────────────┐
│   Multiple Agent Instances (Servers)   │
│   Server 1  │  Server 2  │  Server 3   │
└─────────┬───────────┬───────────┬───────┘
          │           │           │
          └───────────┼───────────┘
                      ▼
         ┌─────────────────────────┐
         │  PostgreSQL Database    │
         │  • conversations table  │
         │  • messages table       │
         │  • usage_logs table     │
         │  • Connection pooling   │
         └─────────────────────────┘
```

## Quick Start

### Prerequisites

1. **PostgreSQL Installed** (local or remote)
2. **Database Created**
3. **Connection URL** in format: `postgresql://user:password@host:port/database`

### Basic Setup

```python
from openai_agents.session import PostgreSQLSession

session = PostgreSQLSession(
    database_url="postgresql://user:password@localhost:5432/agents_db",
    conversation_id="user-123-conv"
)

agent = Agent(
    name="MyAgent",
    model=llm_model,
    session=session
)
```

### Environment Variable (Recommended)

```python
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/agents_db

# Code
import os
session = PostgreSQLSession(
    database_url=os.getenv("DATABASE_URL"),
    conversation_id="user-123-conv"
)
```

## Connection Pooling

For production, use connection pooling to handle concurrent requests efficiently:

```python
from openai_agents.session import PostgreSQLSession

# SDK handles pooling internally, configure via URL parameters
session = PostgreSQLSession(
    database_url="postgresql://user:pass@host:5432/db?pool_size=20&max_overflow=10",
    conversation_id="conv-id"
)
```

## Docker Setup

### Local Development

```bash
# Start PostgreSQL container
docker run --name agents-postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=agents_db \
  -p 5432:5432 \
  -d postgres:16

# Create database (if needed)
docker exec -it agents-postgres psql -U postgres -c "CREATE DATABASE agents_db;"

# Connection URL
DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/agents_db
```

### Production (Docker Compose)

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: agents_production
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: always

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD}
    ports:
      - "5050:80"
    depends_on:
      - postgres

volumes:
  postgres_data:
```

## Schema Management

PostgreSQL sessions auto-create tables on first use:

```sql
-- conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- usage_logs table
CREATE TABLE IF NOT EXISTS usage_logs (
    id SERIAL PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE CASCADE,
    run_id TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    model TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_usage_conversation ON usage_logs(conversation_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
```

## Performance Optimization

### Indexing Strategy

```sql
-- Essential indexes (auto-created)
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_usage_logs_conversation ON usage_logs(conversation_id);

-- Additional indexes for common queries
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
CREATE INDEX idx_messages_created ON messages(created_at DESC);
```

### Query Optimization

```python
# Good: Query with specific conversation_id
SELECT * FROM messages WHERE conversation_id = 'conv-123' ORDER BY created_at;

# Good: Limit results
SELECT * FROM conversations ORDER BY created_at DESC LIMIT 100;

# Avoid: Full table scans without WHERE clause
SELECT * FROM messages;  # Bad for large tables
```

## Monitoring & Analytics

### Usage Queries

```sql
-- Total conversations
SELECT COUNT(*) FROM conversations;

-- Active conversations (last 24 hours)
SELECT COUNT(*) FROM conversations
WHERE updated_at > NOW() - INTERVAL '24 hours';

-- Top users by message count
SELECT user_id, COUNT(*) as message_count
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
GROUP BY user_id
ORDER BY message_count DESC
LIMIT 10;

-- Token usage by model
SELECT model,
       SUM(prompt_tokens) as total_prompt,
       SUM(completion_tokens) as total_completion
FROM usage_logs
GROUP BY model;
```

## Backup & Recovery

### Automated Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/agents_db_$TIMESTAMP.sql"

pg_dump -h localhost -U agent_user agents_db > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
```

### Restore

```bash
# Restore from backup
gunzip < agents_db_20240115_120000.sql.gz | psql -h localhost -U agent_user agents_db
```

## Security Best Practices

1. **Use Connection Pooling**: Never create connection per request
2. **Environment Variables**: Never hardcode credentials
3. **SSL/TLS**: Use SSL for production connections
4. **Least Privilege**: Create dedicated database user with minimal permissions
5. **Regular Updates**: Keep PostgreSQL version up to date

### Secure Connection

```python
session = PostgreSQLSession(
    database_url="postgresql://user:pass@host:5432/db?sslmode=require",
    conversation_id="conv-id"
)
```

## Comparison: PostgreSQL vs SQLite vs Redis

| Feature     | PostgreSQL          | SQLite      | Redis            |
| ----------- | ------------------- | ----------- | ---------------- |
| Concurrency | Very High           | Low         | Very High        |
| Durability  | ACID                | ACID        | Optional         |
| Setup       | Docker/Server       | Zero config | Docker/Server    |
| Analytics   | Advanced SQL        | SQL         | Limited          |
| Cost        | Server costs        | Free        | Server costs     |
| Best For    | Production web apps | Dev/Desktop | High-speed cache |

## Next Steps

1. **Setup PostgreSQL** - Use Docker for local development
2. **Run `01_basic_postgres.py`** - See basic session usage
3. **Explore `02_production_postgres.py`** - Production patterns
4. **Review `03_deployment_guide.md`** - Deploy to production

## Further Reading

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Connection Pooling Best Practices](https://wiki.postgresql.org/wiki/Number_Of_Database_Connections)
- [OpenAI Agents SDK: PostgreSQL Sessions](https://github.com/openai/openai-agents-sdk)
