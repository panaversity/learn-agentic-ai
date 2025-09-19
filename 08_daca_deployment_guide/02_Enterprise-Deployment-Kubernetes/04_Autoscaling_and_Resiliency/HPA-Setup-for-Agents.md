# HPA Setup for AI Agents

## Objective
This guide provides detailed instructions for configuring Horizontal Pod Autoscaling (HPA) for AI agent deployments, ensuring optimal resource utilization and performance.

## Prerequisites
- Kubernetes cluster with metrics-server installed
- kubectl configured
- Basic understanding of Kubernetes concepts
- Access to create and modify HPA resources

## Step-by-Step Instructions

### 1. Configure Metrics Server

#### 1.1 Install Metrics Server
```bash
# Add metrics-server Helm repository
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update

# Install metrics-server
helm install metrics-server metrics-server/metrics-server \
  --namespace kube-system \
  --set args={--kubelet-insecure-tls}
```

#### 1.2 Verify Metrics Collection
```bash
# Check metrics-server pods
kubectl get pods -n kube-system -l app.kubernetes.io/name=metrics-server

# Test metrics collection
kubectl top nodes
kubectl top pods
```

### 2. Configure AI Agent Deployment

#### 2.1 Create Deployment with Resource Limits
```yaml
# agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-agent
  template:
    metadata:
      labels:
        app: ai-agent
    spec:
      containers:
      - name: agent
        image: ai-agent:latest
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        ports:
        - containerPort: 8080
```

#### 2.2 Configure Custom Metrics
```yaml
# custom-metrics.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: custom-metrics-config
  namespace: kube-system
data:
  config.yaml: |
    rules:
    - seriesQuery: 'agent_requests_total{namespace!="",pod!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
          pod: {resource: "pod"}
      name:
        matches: "agent_requests_total"
        as: "requests_per_second"
      metricsQuery: 'rate(<<.Series>>{<<.LabelMatchers>>}[5m])'
```

### 3. Set Up HPA

#### 3.1 Create CPU-based HPA
```yaml
# cpu-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-agent-cpu
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### 3.2 Create Memory-based HPA
```yaml
# memory-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-agent-memory
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### 3.3 Create Custom Metrics HPA
```yaml
# custom-metrics-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-agent-custom
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: 100
```

### 4. Configure Scaling Behavior

#### 4.1 Set Up Scaling Policies
```yaml
# scaling-policy.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-agent
  namespace: production
spec:
  behavior:
    scaleUp:
      policies:
      - type: Pods
        value: 2
        periodSeconds: 60
      - type: Percent
        value: 50
        periodSeconds: 60
      selectPolicy: Max
      stabilizationWindowSeconds: 0
    scaleDown:
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
      - type: Percent
        value: 20
        periodSeconds: 60
      selectPolicy: Max
      stabilizationWindowSeconds: 300
```

## Validation

### 1. Verify HPA Configuration
```bash
# Check HPA status
kubectl get hpa -n production

# Describe HPA
kubectl describe hpa ai-agent -n production
```

### 2. Test Scaling
```bash
# Create load test
kubectl run load-test --image=busybox -n production -- /bin/sh -c "while true; do wget -qO- http://ai-agent:8080; done"

# Monitor scaling
kubectl get hpa -n production -w
kubectl get pods -n production -w
```

### 3. Verify Metrics
```bash
# Check metrics
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1/namespaces/production/pods/*/requests_per_second

# Check resource usage
kubectl top pods -n production
```

## Common Issues and Solutions

### Issue 1: Scaling Not Triggered
- **Solution**: Check metrics collection and HPA configuration
- **Prevention**: Monitor metrics and HPA events

### Issue 2: Excessive Scaling
- **Solution**: Adjust scaling policies and thresholds
- **Prevention**: Set appropriate stabilization windows

### Issue 3: Metrics Not Available
- **Solution**: Verify metrics-server and custom metrics configuration
- **Prevention**: Monitor metrics collection

## Best Practices

### 1. Configuration
- Set appropriate thresholds
- Configure scaling policies
- Monitor metrics
- Regular reviews
- Document settings

### 2. Resource Management
- Set resource requests
- Configure limits
- Monitor utilization
- Plan capacity
- Regular audits

### 3. Operations
- Monitor scaling events
- Set up alerts
- Document procedures
- Regular testing
- Backup plans

## Next Steps
- Configure cluster autoscaler
- Set up monitoring
- Implement backup
- Regular reviews
