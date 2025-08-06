# Cross-Region Data Replication

## Objective
This guide provides detailed instructions for implementing cross-region data replication to ensure data availability and disaster recovery across multiple regions.

## Prerequisites
- Multiple Kubernetes clusters in different regions
- CockroachDB Serverless (transitioning to Postgres on Kubernetes)
- Upstash Redis (transitioning to Redis on Kubernetes)
- kubectl configured for all clusters
- Helm installed
- Basic understanding of data replication concepts
- Access to create and modify database resources

## Step-by-Step Instructions

### 1. Configure CockroachDB Serverless

#### 1.1 Create CockroachDB Serverless Cluster
```bash
# Create CockroachDB Serverless cluster
cockroach sql --url "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Dyour-cluster"

# Create database
CREATE DATABASE ai_database;

# Create tables
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name STRING,
    region STRING,
    created_at TIMESTAMP DEFAULT now()
);
```

#### 1.2 Configure Database Access
```yaml
# cockroachdb-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cockroachdb-connection
  namespace: production
type: Opaque
stringData:
  connection-string: "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/ai_database?sslmode=verify-full&options=--cluster%3Dyour-cluster"
```

### 2. Configure Upstash Redis

#### 2.1 Set Up Redis Connection
```yaml
# redis-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: redis-connection
  namespace: production
type: Opaque
stringData:
  connection-string: "redis://default:password@us1-redis.upstash.io:6379"
```

#### 2.2 Configure Redis Client
```yaml
# redis-client.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-client
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: redis-client
  template:
    metadata:
      labels:
        app: redis-client
    spec:
      containers:
      - name: client
        image: redis-client:latest
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-connection
              key: connection-string
        ports:
        - containerPort: 6379
```

### 3. Configure Data Replication

#### 3.1 Set Up Replication Policies
```yaml
# replication-policy.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: replication-policy
  namespace: production
data:
  consistencyLevel: "STRONG"
  maxStalenessPrefix: "100000"
  maxIntervalInSeconds: "300"
  automaticFailover: "true"
```

#### 3.2 Configure Connection Strings
```yaml
# connection-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-connection
  namespace: production
type: Opaque
stringData:
  cockroachdb-url: "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/ai_database?sslmode=verify-full&options=--cluster%3Dyour-cluster"
  redis-url: "redis://default:password@us1-redis.upstash.io:6379"
```

### 4. Configure Application Access

#### 4.1 Set Up Database Client
```yaml
# db-client.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db-client
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: db-client
  template:
    metadata:
      labels:
        app: db-client
    spec:
      containers:
      - name: client
        image: db-client:latest
        env:
        - name: COCKROACHDB_URL
          valueFrom:
            secretKeyRef:
              name: db-connection
              key: cockroachdb-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: db-connection
              key: redis-url
        ports:
        - containerPort: 5432
        - containerPort: 6379
```

#### 4.2 Configure Read/Write Preferences
```yaml
# db-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-config
  namespace: production
data:
  read-preference: "nearest"
  write-concern: "majority"
  retry-writes: "true"
  max-pool-size: "100"
  min-pool-size: "10"
```

### 5. Configure Monitoring

#### 5.1 Set Up Metrics Collection
```yaml
# metrics-config.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: db-metrics
  namespace: production
spec:
  selector:
    matchLabels:
      app: db-client
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

#### 5.2 Configure Alerts
```yaml
# alerts-config.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: db-alerts
  namespace: production
spec:
  groups:
  - name: database
    rules:
    - alert: HighReplicationLag
      expr: db_replication_lag_seconds > 300
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High replication lag detected
        description: Replication lag is {{ $value }} seconds
```

## Validation

### 1. Verify Database Setup
```bash
# Check CockroachDB status
cockroach sql --url "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/ai_database?sslmode=verify-full&options=--cluster%3Dyour-cluster" --execute "SHOW DATABASES;"

# Check Redis status
redis-cli -u redis://default:password@us1-redis.upstash.io:6379 ping
```

### 2. Test Data Replication
```bash
# Insert test data into CockroachDB
cockroach sql --url "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/ai_database?sslmode=verify-full&options=--cluster%3Dyour-cluster" --execute "INSERT INTO agents (name, region) VALUES ('test-agent', 'eastus');"

# Verify data in Redis
redis-cli -u redis://default:password@us1-redis.upstash.io:6379 set test-key test-value
redis-cli -u redis://default:password@us1-redis.upstash.io:6379 get test-key
```

### 3. Monitor Replication Status
```bash
# Check replication metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/production/pods

# Check client metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/production/pods
```

## Common Issues and Solutions

### Issue 1: High Replication Latency
- **Solution**: Check network connectivity and adjust consistency level
- **Prevention**: Monitor replication metrics

### Issue 2: Write Conflicts
- **Solution**: Implement conflict resolution policies
- **Prevention**: Use appropriate write concerns

### Issue 3: Connection Issues
- **Solution**: Verify connection strings and network policies
- **Prevention**: Monitor connection metrics

## Best Practices

### 1. Database Configuration
- Use appropriate consistency levels
- Configure automatic failover
- Monitor replication
- Regular backups
- Document setup

### 2. Application Access
- Use connection pooling
- Implement retry logic
- Monitor performance
- Regular testing
- Document procedures

### 3. Monitoring
- Set up comprehensive metrics
- Configure alerts
- Monitor performance
- Regular reviews
- Document findings

## Next Steps
- Configure backup
- Set up disaster recovery
- Implement monitoring
- Regular reviews 