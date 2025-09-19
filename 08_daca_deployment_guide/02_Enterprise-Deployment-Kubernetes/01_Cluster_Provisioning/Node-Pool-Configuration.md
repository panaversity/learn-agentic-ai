# Node Pool Configuration Guide

## Objective
This guide provides instructions for configuring and managing node pools in your Kubernetes cluster, ensuring optimal resource allocation and workload distribution.

## Prerequisites
- Kubernetes cluster created with Civo
- Access to kubectl and civo CLI
- Basic understanding of Kubernetes concepts
- Rancher access (if using Rancher)

## Step-by-Step Instructions

### 1. Create Node Pools

#### 1.1 Create General Purpose Node Pool
```bash
# Create a general purpose node pool
civo kubernetes node-pool create my-cluster \
  --name general-purpose \
  --size g4s.kube.medium \
  --count 3 \
  --label workload=general
```

#### 1.2 Create GPU Node Pool
```bash
# Create a GPU node pool
civo kubernetes node-pool create my-cluster \
  --name gpu-pool \
  --size g4s.kube.large \
  --count 2 \
  --label workload=gpu
```

#### 1.3 Create Memory Optimized Node Pool
```bash
# Create a memory optimized node pool
civo kubernetes node-pool create my-cluster \
  --name memory-optimized \
  --size g4s.kube.xlarge \
  --count 2 \
  --label workload=memory-intensive
```

### 2. Configure Node Labels and Taints

#### 2.1 Add Labels to Nodes
```bash
# Label nodes in a pool
kubectl label nodes -l workload=general purpose=general
kubectl label nodes -l workload=gpu accelerator=nvidia
kubectl label nodes -l workload=memory-intensive memory=high
```

#### 2.2 Add Taints to Nodes
```bash
# Add taints to GPU nodes
kubectl taint nodes -l workload=gpu gpu=true:NoSchedule

# Add taints to memory optimized nodes
kubectl taint nodes -l workload=memory-intensive memory-intensive=true:NoSchedule
```

### 3. Configure Node Autoscaling

#### 3.1 Enable Cluster Autoscaler
```bash
# Install cluster autoscaler
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --set autoDiscovery.clusterName=my-cluster \
  --set cloudProvider=civo \
  --set extraArgs.scale-down-enabled=true
```

#### 3.2 Configure Node Pool Autoscaling
```bash
# Update node pool with autoscaling
civo kubernetes node-pool update my-cluster general-purpose \
  --min-nodes 2 \
  --max-nodes 5 \
  --enable-autoscaling
```

### 4. Set Up Resource Quotas

#### 4.1 Create Resource Quotas
```yaml
# resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 100Gi
    limits.cpu: "40"
    limits.memory: 200Gi
```

```bash
# Apply resource quotas
kubectl apply -f resource-quota.yaml
```

#### 4.2 Configure Limit Ranges
```yaml
# limit-range.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
```

```bash
# Apply limit ranges
kubectl apply -f limit-range.yaml
```

## Validation

### 1. Verify Node Pool Configuration
```bash
# List node pools
civo kubernetes node-pool list my-cluster

# Check node labels
kubectl get nodes --show-labels

# Verify taints
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```

### 2. Test Workload Distribution
```yaml
# gpu-workload.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-workload
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gpu-workload
  template:
    metadata:
      labels:
        app: gpu-workload
    spec:
      tolerations:
      - key: "gpu"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      nodeSelector:
        workload: gpu
      containers:
      - name: gpu-workload
        image: nvidia/cuda:11.0-base
        resources:
          limits:
            nvidia.com/gpu: 1
```

```bash
# Deploy test workload
kubectl apply -f gpu-workload.yaml

# Verify pod placement
kubectl get pods -o wide
```

### 3. Check Autoscaling
```bash
# Monitor autoscaler logs
kubectl logs -f deployment/cluster-autoscaler -n kube-system

# Check node pool status
civo kubernetes node-pool show my-cluster general-purpose
```

## Common Issues and Solutions

### Issue 1: Node Pool Creation Fails
- **Solution**: Check resource quotas and limits
- **Prevention**: Plan resource allocation

### Issue 2: Workload Scheduling Issues
- **Solution**: Verify node labels and taints
- **Prevention**: Test scheduling before production

### Issue 3: Autoscaling Problems
- **Solution**: Check autoscaler configuration
- **Prevention**: Monitor scaling events

## Best Practices

### 1. Node Pool Design
- Right-size node pools
- Use appropriate instance types
- Implement proper labeling
- Consider workload requirements
- Plan for scaling

### 2. Resource Management
- Set resource quotas
- Configure limit ranges
- Monitor resource usage
- Implement autoscaling
- Regular capacity planning

### 3. Workload Distribution
- Use node affinity
- Implement proper taints
- Consider workload types
- Balance resource usage
- Monitor distribution

## Next Steps
- Set up monitoring and alerting
- Configure backup and recovery
- Implement security policies
