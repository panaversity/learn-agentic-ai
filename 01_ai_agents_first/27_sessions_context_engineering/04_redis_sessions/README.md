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

See https://github.com/openai/openai-agents-python/pull/1785 for Implementation