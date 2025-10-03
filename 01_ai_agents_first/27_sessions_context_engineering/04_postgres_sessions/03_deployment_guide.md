# PostgreSQL Deployment Guide

## Docker Setup (Recommended)

### Local Development

```bash
# Start PostgreSQL container
docker run --name agents-postgres \
  -e POSTGRES_USER=agent_user \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=agents_db \
  -p 5432:5432 \
  -d postgres:16

# Verify it's running
docker ps | grep agents-postgres

# Test connection
docker exec -it agents-postgres psql -U agent_user -d agents_db
```

**Connection URL:**

```
DATABASE_URL=postgresql://agent_user:mysecretpassword@localhost:5432/agents_db
```

### Docker Compose (Production-like)

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16
    container_name: agents-postgres
    environment:
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: agents_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql # Optional: seed data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent_user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Start:**

```bash
# Set password
export DB_PASSWORD=your_secure_password

# Start
docker-compose up -d

# Check logs
docker-compose logs -f postgres
```

## Cloud Deployment

### AWS RDS PostgreSQL

1. **Create RDS Instance:**

   - Engine: PostgreSQL 16
   - Instance class: db.t3.micro (dev) or db.t3.medium (prod)
   - Storage: 20GB gp3 (adjustable)
   - Multi-AZ: Yes (production)

2. **Connection URL:**

```
DATABASE_URL=postgresql://agent_user:password@your-instance.region.rds.amazonaws.com:5432/agents_db
```

3. **Security Group:**
   - Allow inbound on port 5432 from your app servers

### Google Cloud SQL

```bash
# Create instance
gcloud sql instances create agents-postgres \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create agents_db --instance=agents-postgres

# Create user
gcloud sql users create agent_user \
  --instance=agents-postgres \
  --password=your_password
```

**Connection URL:**

```
DATABASE_URL=postgresql://agent_user:password@/agents_db?host=/cloudsql/project:region:agents-postgres
```

### Azure Database for PostgreSQL

```bash
# Create resource group
az group create --name agents-rg --location eastus

# Create PostgreSQL server
az postgres server create \
  --resource-group agents-rg \
  --name agents-postgres \
  --location eastus \
  --admin-user agent_user \
  --admin-password YourPassword123! \
  --sku-name B_Gen5_1 \
  --version 16

# Create database
az postgres db create \
  --resource-group agents-rg \
  --server-name agents-postgres \
  --name agents_db
```

## Environment Configuration

### .env File (Development)

```bash
# Database
DATABASE_URL=postgresql://agent_user:mysecretpassword@localhost:5432/agents_db

# API Keys
GEMINI_API_KEY=your_gemini_key_here

# Optional: Tracing
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Environment Variables (Production)

**Docker:**

```bash
docker run -d \
  -e DATABASE_URL=postgresql://... \
  -e GEMINI_API_KEY=... \
  your-app-image
```

**Kubernetes:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  database-url: postgresql://agent_user:password@postgres-service:5432/agents_db
  gemini-api-key: your_key_here
```

## Schema Migration

The OpenAI Agents SDK auto-creates tables, but you can also manage schema explicitly:

### Initial Schema (init.sql)

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

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_usage_conversation ON usage_logs(conversation_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);
```

### Migration Tools

**Using Alembic (Python):**

```bash
# Install
pip install alembic psycopg2-binary

# Initialize
alembic init migrations

# Create migration
alembic revision -m "Initial schema"

# Apply
alembic upgrade head
```

## Monitoring

### Connection Monitoring

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'agents_db';

-- Long-running queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 seconds';

-- Kill long query
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = 12345;
```

### Performance Metrics

```sql
-- Table sizes
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Index usage
SELECT
    schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="agents_db"
DB_USER="agent_user"
DB_HOST="localhost"

# Create backup
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" s3://your-bucket/backups/

# Keep only last 7 days locally
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${DB_NAME}_${TIMESTAMP}.sql.gz"
```

**Schedule with cron:**

```bash
# Daily at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/postgres-backup.log 2>&1
```

### Restore

```bash
# Restore from backup
gunzip < agents_db_20240115_020000.sql.gz | psql -h localhost -U agent_user agents_db
```

## Security Best Practices

1. **Use SSL/TLS:**

   ```
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

2. **Principle of Least Privilege:**

   ```sql
   CREATE USER agent_app WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE agents_db TO agent_app;
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO agent_app;
   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO agent_app;
   ```

3. **Connection Limits:**

   ```sql
   ALTER USER agent_app CONNECTION LIMIT 20;
   ```

4. **Never Commit Credentials:**
   - Use environment variables
   - Use secret managers (AWS Secrets Manager, Vault)

## Troubleshooting

### Can't Connect

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs agents-postgres

# Test connection
psql -h localhost -U agent_user -d agents_db
```

### Connection Pool Exhausted

Increase pool size in DATABASE_URL:

```
postgresql://user:pass@host:5432/db?pool_size=30&max_overflow=20
```

### Slow Queries

```sql
-- Enable query logging
ALTER DATABASE agents_db SET log_min_duration_statement = 100;  -- log queries > 100ms

-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM messages WHERE conversation_id = 'conv-123';
```

## Production Checklist

- [ ] PostgreSQL 16+ installed
- [ ] Database and user created
- [ ] SSL/TLS enabled
- [ ] Connection pooling configured
- [ ] Indexes created
- [ ] Backup script automated
- [ ] Monitoring configured
- [ ] Credentials in environment variables
- [ ] Security group / firewall configured
- [ ] Test restore procedure
