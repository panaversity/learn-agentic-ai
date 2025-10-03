# Redis Sessions

## Overview

**Redis Sessions** provide ultra-fast, distributed session management for high-performance applications. Redis stores sessions in-memory with optional persistence, making it ideal for real-time applications and distributed systems requiring millisecond latency.

## Key Features

- **Ultra-Fast**: In-memory storage with microsecond latency
- **Distributed**: Native support for multi-server deployments
- **TTL (Time-To-Live)**: Automatic session expiration
- **Pub/Sub**: Real-time updates across instances
- **Clustering**: Horizontal scaling with Redis Cluster
- **Persistence**: Optional disk persistence (RDB/AOF)
- **Multi-Tenancy**: Key prefixes for isolation

## When to Use

✅ **Use Redis Sessions when:**

- Need ultra-low latency (< 1ms)
- Building real-time applications (chat, gaming)
- Deploying distributed systems
- Need automatic session expiration (TTL)
- Want caching + session storage in one
- Handling high throughput (10k+ req/sec)

❌ **Use PostgreSQL instead when:**

- Need complex SQL queries
- Require strong ACID guarantees
- Want persistent analytics history
- Budget constraints (Redis can be expensive)

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
         │    Redis Cluster        │
         │  • In-memory storage    │
         │  • Key-value pairs      │
         │  • TTL management       │
         │  • Pub/Sub              │
         └─────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Redis Installed** (local or remote)
2. **Redis URL** in format: `redis://[[username]:[password]@]host:port/database`

### Basic Setup

```python
from openai_agents.session import RedisSession

session = RedisSession(
    redis_url="redis://localhost:6379/0",
    conversation_id="user-123-conv",
    ttl=3600  # Session expires after 1 hour
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
REDIS_URL=redis://localhost:6379/0

# Code
import os
session = RedisSession(
    redis_url=os.getenv("REDIS_URL"),
    conversation_id="user-123-conv",
    ttl=3600
)
```

## Docker Setup

### Local Development

```bash
# Start Redis container
docker run --name agents-redis \
  -p 6379:6379 \
  -d redis:7-alpine

# Test connection
docker exec -it agents-redis redis-cli ping
# Should return: PONG

# Connection URL
REDIS_URL=redis://localhost:6379/0
```

### With Authentication

```bash
# Start Redis with password
docker run --name agents-redis \
  -p 6379:6379 \
  -d redis:7-alpine \
  redis-server --requirepass mysecretpassword

# Connection URL
REDIS_URL=redis://:mysecretpassword@localhost:6379/0
```

### Docker Compose (Production-like)

```yaml
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    container_name: agents-redis
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

volumes:
  redis_data:
```

## TTL (Time-To-Live) Management

### Auto-Expiring Sessions

```python
# Session expires after 1 hour of inactivity
session = RedisSession(
    redis_url=redis_url,
    conversation_id="user-123",
    ttl=3600  # seconds
)

# Session expires after 24 hours
session = RedisSession(
    redis_url=redis_url,
    conversation_id="user-123",
    ttl=86400  # 24 * 3600
)

# No expiration (persistent)
session = RedisSession(
    redis_url=redis_url,
    conversation_id="user-123",
    ttl=None  # or omit ttl parameter
)
```

### TTL Patterns

| TTL Value        | Use Case                |
| ---------------- | ----------------------- |
| 300 (5 min)      | Real-time chat sessions |
| 1800 (30 min)    | Customer support        |
| 3600 (1 hour)    | Shopping sessions       |
| 86400 (24 hours) | Long conversations      |
| None             | Permanent storage       |

## Key Prefixes (Multi-Tenancy)

Isolate conversations by tenant/user:

```python
# Tenant A conversations
session_a = RedisSession(
    redis_url=redis_url,
    conversation_id="user-123",
    key_prefix="tenant_a:"  # Keys: tenant_a:user-123
)

# Tenant B conversations
session_b = RedisSession(
    redis_url=redis_url,
    conversation_id="user-123",
    key_prefix="tenant_b:"  # Keys: tenant_b:user-123
)

# Different users can have same conversation_id across tenants
```

## Performance Optimization

### Connection Pooling

```python
# Redis SDK handles connection pooling automatically
# Configure via URL parameters
session = RedisSession(
    redis_url="redis://localhost:6379/0?max_connections=50",
    conversation_id="conv-id"
)
```

### Pipelining (Batch Operations)

```python
# SDK handles pipelining internally for bulk operations
# Multiple get/set operations are batched automatically
```

## Cloud Deployment

### AWS ElastiCache

```bash
# Create Redis cluster (AWS Console or CLI)
aws elasticache create-cache-cluster \
  --cache-cluster-id agents-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# Connection URL (from AWS Console)
REDIS_URL=redis://your-cluster.cache.amazonaws.com:6379/0
```

### Google Cloud Memorystore

```bash
# Create Redis instance
gcloud redis instances create agents-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0

# Get connection info
gcloud redis instances describe agents-redis --region=us-central1
```

### Azure Cache for Redis

```bash
# Create Redis cache
az redis create \
  --name agents-redis \
  --resource-group agents-rg \
  --location eastus \
  --sku Basic \
  --vm-size c0

# Get connection info
az redis show --name agents-redis --resource-group agents-rg
```

## Monitoring

### Redis CLI Commands

```bash
# Connect to Redis
redis-cli -h localhost -p 6379 -a yourpassword

# Check memory usage
INFO memory

# Count keys
DBSIZE

# List keys (use with caution in production)
KEYS conv:*

# Get key TTL
TTL conv:user-123

# Monitor real-time commands
MONITOR

# Check connection count
CLIENT LIST
```

### Performance Metrics

```bash
# Get stats
INFO stats

# Latency monitoring
LATENCY DOCTOR

# Slowlog (slow queries)
SLOWLOG GET 10
```

## Backup & Recovery

### Redis Persistence

**RDB (Point-in-time Snapshots):**

```bash
# Save snapshot manually
redis-cli SAVE

# Automatic snapshots (redis.conf)
save 900 1      # Save if 1 key changed in 15 min
save 300 10     # Save if 10 keys changed in 5 min
save 60 10000   # Save if 10k keys changed in 1 min
```

**AOF (Append-Only File):**

```bash
# Enable AOF (redis.conf)
appendonly yes
appendfsync everysec  # fsync every second
```

### Backup to S3

```bash
#!/bin/bash
# backup-redis.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="dump_${TIMESTAMP}.rdb"

# Trigger save
redis-cli SAVE

# Copy RDB file
docker cp agents-redis:/data/dump.rdb $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://your-bucket/redis-backups/

# Cleanup
rm $BACKUP_FILE
```

## Security Best Practices

1. **Use Authentication:**

   ```bash
   redis-server --requirepass strongpassword
   ```

2. **Bind to Specific Interface:**

   ```bash
   redis-server --bind 127.0.0.1 ::1  # localhost only
   ```

3. **Disable Dangerous Commands:**

   ```bash
   # redis.conf
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""
   rename-command CONFIG ""
   ```

4. **Use TLS/SSL:**
   ```
   REDIS_URL=rediss://password@host:6380/0  # Note: rediss (with s)
   ```

## Comparison: Redis vs PostgreSQL vs SQLite

| Feature      | Redis            | PostgreSQL      | SQLite      |
| ------------ | ---------------- | --------------- | ----------- |
| Latency      | < 1ms            | 5-10ms          | 1-5ms       |
| Throughput   | 100k+ ops/sec    | 10k ops/sec     | 1k ops/sec  |
| Persistence  | Optional         | Always          | Always      |
| Queries      | Key-value        | SQL             | SQL         |
| TTL          | Native           | Manual          | Manual      |
| Memory Usage | High (in-memory) | Medium          | Low         |
| Best For     | Real-time/cache  | Production apps | Dev/Desktop |

## Use Case Examples

### 1. Real-Time Chat

```python
# 5-minute session expiration
session = RedisSession(
    redis_url=redis_url,
    conversation_id=f"chat-{room_id}-{user_id}",
    ttl=300,
    key_prefix="chat:"
)
```

### 2. E-Commerce Shopping Cart

```python
# 30-minute cart expiration
session = RedisSession(
    redis_url=redis_url,
    conversation_id=f"cart-{user_id}",
    ttl=1800,
    key_prefix="cart:"
)
```

### 3. Customer Support

```python
# 1-hour support session
session = RedisSession(
    redis_url=redis_url,
    conversation_id=f"support-{ticket_id}",
    ttl=3600,
    key_prefix="support:"
)
```

## Next Steps

1. **Setup Redis** - Use Docker for local development
2. **Run `01_basic_redis.py`** - See basic session usage with TTL
3. **Explore `02_production_redis.py`** - Production patterns with prefixes
4. **Try `03_multi_instance_demo.py`** - Simulate distributed deployment

## Further Reading

- [Redis Documentation](https://redis.io/docs/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [OpenAI Agents SDK: Redis Sessions](https://github.com/openai/openai-agents-sdk)
