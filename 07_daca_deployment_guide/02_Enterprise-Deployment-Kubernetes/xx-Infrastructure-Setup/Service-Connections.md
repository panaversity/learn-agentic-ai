# Service Connections Configuration

## Overview
This document outlines the configuration for connecting to external services in our Kubernetes deployment.

## Prerequisites
- Kubernetes cluster configured
- kubectl installed and configured
- Helm installed
- Access to create and modify Kubernetes resources

## Service Connections

### 1. Database Connections

#### 1.1 CockroachDB Serverless
```yaml
# cockroachdb-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cockroachdb-connection
  namespace: production
type: Opaque
stringData:
  connection-string: "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/ai_database?sslmode=verify-full&options=--cluster%3Dyour-cluster"
```

#### 1.2 Upstash Redis
```yaml
# redis-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: redis-connection
  namespace: production
type: Opaque
stringData:
  connection-string: "redis://default:password@us1-redis.upstash.io:6379"
```

### 2. Message Queue Connections

#### 2.1 CloudAMQP RabbitMQ
```yaml
# rabbitmq-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: rabbitmq-connection
  namespace: production
type: Opaque
stringData:
  connection-string: "amqps://user:password@your-instance.cloudamqp.com/vhost"
```

### 3. LLM API Connections

#### 3.1 Google Gemini
```yaml
# gemini-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: gemini-connection
  namespace: production
type: Opaque
stringData:
  api-key: "your-gemini-api-key"
```

### 4. Application Configuration

#### 4.1 Environment Variables
```yaml
# env-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-environment
  namespace: production
data:
  COCKROACHDB_URL: "postgresql://user:password@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/ai_database?sslmode=verify-full&options=--cluster%3Dyour-cluster"
  REDIS_URL: "redis://default:password@us1-redis.upstash.io:6379"
  RABBITMQ_URL: "amqps://user:password@your-instance.cloudamqp.com/vhost"
  GEMINI_API_KEY: "your-gemini-api-key"
```

#### 4.2 Deployment Configuration
```yaml
# app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
      - name: app
        image: app:latest
        envFrom:
        - configMapRef:
            name: app-environment
        env:
        - name: COCKROACHDB_URL
          valueFrom:
            secretKeyRef:
              name: cockroachdb-connection
              key: connection-string
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-connection
              key: connection-string
        - name: RABBITMQ_URL
          valueFrom:
            secretKeyRef:
              name: rabbitmq-connection
              key: connection-string
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-connection
              key: api-key
```

## Validation

### 1. Verify Secrets
```bash
# Check CockroachDB secret
kubectl get secret cockroachdb-connection -n production

# Check Redis secret
kubectl get secret redis-connection -n production

# Check RabbitMQ secret
kubectl get secret rabbitmq-connection -n production

# Check Gemini secret
kubectl get secret gemini-connection -n production
```

### 2. Test Connections
```bash
# Test CockroachDB connection
kubectl exec -it <pod-name> -n production -- cockroach sql --url "$COCKROACHDB_URL" --execute "SHOW DATABASES;"

# Test Redis connection
kubectl exec -it <pod-name> -n production -- redis-cli -u "$REDIS_URL" ping

# Test RabbitMQ connection
kubectl exec -it <pod-name> -n production -- curl -u user:password "https://your-instance.cloudamqp.com/api/overview"

# Test Gemini API
kubectl exec -it <pod-name> -n production -- curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
```

## Common Issues and Solutions

### Issue 1: Connection Timeouts
- **Solution**: Check network policies and firewall rules
- **Prevention**: Implement proper timeout handling

### Issue 2: Authentication Failures
- **Solution**: Verify credentials and permissions
- **Prevention**: Use proper error handling

### Issue 3: Resource Limits
- **Solution**: Adjust resource quotas
- **Prevention**: Monitor resource usage

## Best Practices

### 1. Security
- Use secrets for sensitive data
- Implement proper RBAC
- Monitor access patterns
- Regular credential rotation

### 2. Configuration
- Use ConfigMaps for non-sensitive data
- Implement proper validation
- Document configurations
- Version control

### 3. Monitoring
- Set up proper logging
- Configure alerts
- Monitor performance
- Regular reviews

## Next Steps
- Set up monitoring
- Configure backup
- Implement disaster recovery
- Regular testing 