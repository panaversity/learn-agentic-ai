# Pod Disruption Budget and Readiness Probes

## Objective
This guide provides detailed instructions for configuring Pod Disruption Budgets (PDB) and Readiness Probes to ensure high availability and graceful handling of pod disruptions in your Kubernetes cluster.

## Prerequisites
- Kubernetes cluster with admin access
- kubectl configured
- Basic understanding of Kubernetes concepts
- Access to create and modify PDB and probe resources

## Step-by-Step Instructions

### 1. Configure Readiness Probes

#### 1.1 HTTP Readiness Probe
```yaml
# http-readiness.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
  namespace: production
spec:
  replicas: 3
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
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
```

#### 1.2 TCP Readiness Probe
```yaml
# tcp-readiness.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
  namespace: production
spec:
  replicas: 3
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
        readinessProbe:
          tcpSocket:
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
```

#### 1.3 Command Readiness Probe
```yaml
# command-readiness.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
  namespace: production
spec:
  replicas: 3
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
        readinessProbe:
          exec:
            command:
            - cat
            - /tmp/healthy
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          successThreshold: 1
          failureThreshold: 3
```

### 2. Configure Pod Disruption Budgets

#### 2.1 MinAvailable PDB
```yaml
# min-available-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-agent-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: ai-agent
```

#### 2.2 MaxUnavailable PDB
```yaml
# max-unavailable-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-agent-pdb
  namespace: production
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: ai-agent
```

#### 2.3 Percentage-based PDB
```yaml
# percentage-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-agent-pdb
  namespace: production
spec:
  maxUnavailable: 30%
  selector:
    matchLabels:
      app: ai-agent
```

### 3. Configure Graceful Shutdown

#### 3.1 Set Termination Grace Period
```yaml
# termination-grace-period.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-agent
  template:
    metadata:
      labels:
        app: ai-agent
    spec:
      terminationGracePeriodSeconds: 30
      containers:
      - name: agent
        image: ai-agent:latest
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]
```

#### 3.2 Configure PreStop Hook
```yaml
# prestop-hook.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agent
  namespace: production
spec:
  replicas: 3
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
        lifecycle:
          preStop:
            httpGet:
              path: /shutdown
              port: 8080
              scheme: HTTP
```

## Validation

### 1. Verify Readiness Probes
```bash
# Check pod status
kubectl get pods -n production

# Check readiness probe status
kubectl describe pod ai-agent-xxxxx -n production | grep -A 10 "Readiness"
```

### 2. Test Pod Disruption
```bash
# Check PDB status
kubectl get pdb -n production

# Test pod disruption
kubectl drain node-name --ignore-daemonsets --delete-emptydir-data
```

### 3. Verify Graceful Shutdown
```bash
# Check pod termination
kubectl delete pod ai-agent-xxxxx -n production

# Monitor pod termination
kubectl get pods -n production -w
```

## Common Issues and Solutions

### Issue 1: Readiness Probe Failures
- **Solution**: Check probe configuration and application health
- **Prevention**: Monitor probe status and logs

### Issue 2: PDB Violations
- **Solution**: Adjust PDB settings or scale deployment
- **Prevention**: Monitor PDB status and pod count

### Issue 3: Graceful Shutdown Issues
- **Solution**: Check termination grace period and preStop hooks
- **Prevention**: Monitor pod termination events

## Best Practices

### 1. Readiness Probes
- Set appropriate timeouts
- Configure proper thresholds
- Monitor probe status
- Regular testing
- Document settings

### 2. Pod Disruption Budgets
- Set realistic limits
- Monitor PDB status
- Regular reviews
- Document policies
- Test disruptions

### 3. Graceful Shutdown
- Configure appropriate grace period
- Implement preStop hooks
- Monitor termination
- Regular testing
- Document procedures

## Next Steps
- Configure liveness probes
- Set up monitoring
- Implement backup
- Regular reviews
