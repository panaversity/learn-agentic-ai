# Cluster Autoscaler Configuration

## Objective
This guide provides detailed instructions for configuring and managing the Kubernetes Cluster Autoscaler to automatically adjust the size of your cluster based on workload demands.

## Prerequisites
- Kubernetes cluster with admin access
- kubectl configured
- Helm installed
- Cloud provider credentials configured
- Basic understanding of Kubernetes concepts

## Step-by-Step Instructions

### 1. Install Cluster Autoscaler

#### 1.1 Add Helm Repository
```bash
# Add autoscaler Helm repository
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm repo update
```

#### 1.2 Install Cluster Autoscaler
```bash
# Create namespace
kubectl create namespace cluster-autoscaler

# Install cluster autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --namespace cluster-autoscaler \
  --set autoDiscovery.clusterName=my-cluster \
  --set cloudProvider=civo \
  --set extraArgs.scale-down-enabled=true \
  --set extraArgs.scale-down-delay-after-add=10m \
  --set extraArgs.scale-down-unneeded-time=10m \
  --set extraArgs.scale-down-utilization-threshold=0.5
```

### 2. Configure Node Groups

#### 2.1 Define Node Group Labels
```yaml
# node-group-labels.yaml
apiVersion: v1
kind: Node
metadata:
  name: worker-node-1
  labels:
    node.kubernetes.io/instance-type: g4s.kube.medium
    topology.kubernetes.io/region: NYC1
    node.kubernetes.io/group: worker
```

#### 2.2 Configure Node Group Autoscaling
```yaml
# node-group-autoscaling.yaml
apiVersion: autoscaling.openshift.io/v1
kind: MachineAutoscaler
metadata:
  name: worker-autoscaler
  namespace: openshift-machine-api
spec:
  minReplicas: 2
  maxReplicas: 5
  scaleTargetRef:
    apiVersion: machine.openshift.io/v1beta1
    kind: MachineSet
    name: worker
```

### 3. Set Up Scaling Policies

#### 3.1 Configure Scale Down
```yaml
# scale-down-policy.yaml
apiVersion: autoscaling.openshift.io/v1
kind: ClusterAutoscaler
metadata:
  name: default
spec:
  resourceLimits:
    maxNodesTotal: 10
    cores:
      min: 8
      max: 128
    memory:
      min: 4
      max: 512
  scaleDown:
    enabled: true
    delayAfterAdd: 10m
    delayAfterDelete: 10m
    delayAfterFailure: 3m
    unneededTime: 10m
```

#### 3.2 Configure Scale Up
```yaml
# scale-up-policy.yaml
apiVersion: autoscaling.openshift.io/v1
kind: ClusterAutoscaler
metadata:
  name: default
spec:
  scaleUp:
    delayAfterAdd: 10m
    delayAfterDelete: 10m
    delayAfterFailure: 3m
    enabled: true
    maxNodeProvisionTime: 15m
```

### 4. Configure Monitoring

#### 4.1 Set Up Metrics Collection
```yaml
# autoscaler-metrics.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cluster-autoscaler
  namespace: cluster-autoscaler
spec:
  selector:
    matchLabels:
      app.kubernetes.io/instance: cluster-autoscaler
  endpoints:
  - port: metrics
    interval: 30s
```

#### 4.2 Configure Alerts
```yaml
# autoscaler-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: cluster-autoscaler-alerts
  namespace: cluster-autoscaler
spec:
  groups:
  - name: cluster-autoscaler
    rules:
    - alert: ClusterAutoscalerScalingFailed
      expr: cluster_autoscaler_scaling_failed > 0
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: Cluster Autoscaler scaling failed
        description: Cluster Autoscaler failed to scale cluster for {{ $labels.reason }}
```

## Validation

### 1. Verify Installation
```bash
# Check cluster autoscaler pods
kubectl get pods -n cluster-autoscaler

# Check cluster autoscaler logs
kubectl logs -f deployment/cluster-autoscaler -n cluster-autoscaler
```

### 2. Test Scaling
```bash
# Create test deployment
kubectl create deployment test-autoscaler --image=nginx --replicas=10

# Monitor node scaling
kubectl get nodes -w

# Check autoscaler events
kubectl get events -n cluster-autoscaler
```

### 3. Verify Metrics
```bash
# Check metrics endpoint
kubectl port-forward svc/cluster-autoscaler -n cluster-autoscaler 8080:8080
curl localhost:8080/metrics
```

## Common Issues and Solutions

### Issue 1: Scaling Not Triggered
- **Solution**: Check resource requests and limits
- **Prevention**: Monitor resource utilization

### Issue 2: Scale Down Not Working
- **Solution**: Verify scale down configuration
- **Prevention**: Check pod disruption budgets

### Issue 3: Node Provisioning Delays
- **Solution**: Check cloud provider quotas
- **Prevention**: Monitor provisioning metrics

## Best Practices

### 1. Configuration
- Right-size node groups
- Set appropriate thresholds
- Configure delays
- Monitor metrics
- Regular reviews

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
- Configure HPA
- Set up monitoring
- Implement backup
- Regular reviews
