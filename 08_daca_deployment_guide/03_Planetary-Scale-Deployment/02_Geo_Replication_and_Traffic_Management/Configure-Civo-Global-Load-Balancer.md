# Configure Civo Global Load Balancer

## Objective
This guide provides detailed instructions for configuring Civo's global load balancer to distribute traffic across multiple regions and ensure high availability.

## Prerequisites
- Civo account with access to load balancer features
- Multiple Kubernetes clusters in different regions
- kubectl configured for all clusters
- Basic understanding of load balancing concepts
- Access to create and modify load balancer resources

## Step-by-Step Instructions

### 1. Configure Civo Load Balancer

#### 1.1 Create Load Balancer
```bash
# Create load balancer
civo loadbalancer create \
  --name global-ai-lb \
  --region NYC1 \
  --protocol http \
  --port 80 \
  --target-port 8080 \
  --algorithm round_robin \
  --health-check-path /health \
  --health-check-interval 30 \
  --health-check-timeout 5 \
  --health-check-healthy-threshold 2 \
  --health-check-unhealthy-threshold 3
```

#### 1.2 Configure Backend Pools
```bash
# Add East US backend
civo loadbalancer backend add \
  --name global-ai-lb \
  --backend-name eastus-backend \
  --instance-id eastus-cluster \
  --port 8080 \
  --weight 100

# Add West Europe backend
civo loadbalancer backend add \
  --name global-ai-lb \
  --backend-name westeurope-backend \
  --instance-id westeurope-cluster \
  --port 8080 \
  --weight 100

# Add Southeast Asia backend
civo loadbalancer backend add \
  --name global-ai-lb \
  --backend-name southeastasia-backend \
  --instance-id southeastasia-cluster \
  --port 8080 \
  --weight 100
```

### 2. Configure Health Checks

#### 2.1 Set Up Health Check Endpoint
```yaml
# health-check.yaml
apiVersion: v1
kind: Service
metadata:
  name: health-check
  namespace: production
spec:
  selector:
    app: health-check
  ports:
  - port: 8080
    targetPort: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: health-check
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: health-check
  template:
    metadata:
      labels:
        app: health-check
    spec:
      containers:
      - name: health-check
        image: health-check:latest
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
```

#### 2.2 Configure Load Balancer Health Checks
```bash
# Update health check configuration
civo loadbalancer update \
  --name global-ai-lb \
  --health-check-path /health \
  --health-check-interval 30 \
  --health-check-timeout 5 \
  --health-check-healthy-threshold 2 \
  --health-check-unhealthy-threshold 3
```

### 3. Configure SSL/TLS

#### 3.1 Set Up SSL Certificate
```bash
# Create SSL certificate
civo ssl create \
  --name global-ai-cert \
  --certificate-file cert.pem \
  --private-key-file key.pem

# Attach certificate to load balancer
civo loadbalancer update \
  --name global-ai-lb \
  --ssl-certificate global-ai-cert
```

#### 3.2 Configure SSL Policies
```bash
# Update SSL configuration
civo loadbalancer update \
  --name global-ai-lb \
  --ssl-policy modern \
  --ssl-min-version TLSv1.2 \
  --ssl-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
```

### 4. Configure Traffic Management

#### 4.1 Set Up Routing Rules
```bash
# Create path-based routing rule
civo loadbalancer rule create \
  --name global-ai-lb \
  --rule-name api-route \
  --path /api/* \
  --backend-pool eastus-backend \
  --priority 100

# Create host-based routing rule
civo loadbalancer rule create \
  --name global-ai-lb \
  --rule-name web-route \
  --host api.example.com \
  --backend-pool westeurope-backend \
  --priority 200
```

#### 4.2 Configure Session Persistence
```bash
# Enable session persistence
civo loadbalancer update \
  --name global-ai-lb \
  --session-persistence cookie \
  --session-persistence-cookie-name SESSIONID \
  --session-persistence-timeout 3600
```

## Validation

### 1. Verify Load Balancer Setup
```bash
# Check load balancer status
civo loadbalancer show global-ai-lb

# Check backend pool status
civo loadbalancer backend list global-ai-lb
```

### 2. Test Load Balancing
```bash
# Test health check endpoint
curl -I https://global-ai-lb.civo.com/health

# Test API endpoint
curl -I https://global-ai-lb.civo.com/api/health

# Test web endpoint
curl -I -H "Host: api.example.com" https://global-ai-lb.civo.com/
```

### 3. Monitor Load Balancer
```bash
# Check load balancer metrics
civo loadbalancer metrics global-ai-lb

# Check backend pool metrics
civo loadbalancer backend metrics global-ai-lb
```

## Common Issues and Solutions

### Issue 1: Health Check Failures
- **Solution**: Check health check configuration and endpoint
- **Prevention**: Monitor health check status

### Issue 2: SSL/TLS Issues
- **Solution**: Verify certificate and SSL configuration
- **Prevention**: Monitor SSL/TLS metrics

### Issue 3: Routing Problems
- **Solution**: Check routing rules and backend pools
- **Prevention**: Monitor routing metrics

## Best Practices

### 1. Load Balancer Configuration
- Use appropriate algorithm
- Configure health checks
- Monitor performance
- Regular updates
- Document setup

### 2. Backend Pool Management
- Distribute traffic evenly
- Monitor backend health
- Regular testing
- Document policies
- Implement failover

### 3. Security
- Enable SSL/TLS
- Configure security policies
- Monitor security
- Regular audits
- Document procedures

## Next Steps
- Configure monitoring
- Set up alerts
- Implement backup
- Regular reviews
