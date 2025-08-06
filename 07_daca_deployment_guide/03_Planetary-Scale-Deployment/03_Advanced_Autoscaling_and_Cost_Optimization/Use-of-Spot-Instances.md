# Using Spot Instances in Kubernetes

## Overview
This guide provides instructions for leveraging spot instances in Kubernetes deployments to optimize costs while maintaining reliability. Spot instances offer significant cost savings but require careful management due to their interruptible nature.

## Prerequisites
- Kubernetes cluster with spot instance support
- kubectl configured with cluster access
- Helm installed
- Basic understanding of spot instances and their characteristics

## Configuration Steps

### 1. Create Node Pool with Spot Instances
```bash
# Create a node pool with spot instances
civo kubernetes node-pool create \
  --cluster my-cluster \
  --name spot-pool \
  --size g4s.kube.medium \
  --count 3 \
  --spot-instances
```

### 2. Configure Node Labels and Taints
```yaml
# spot-node-config.yaml
apiVersion: v1
kind: Node
metadata:
  labels:
    node.kubernetes.io/instance-type: spot
    spot-instance: "true"
spec:
  taints:
  - key: spot-instance
    value: "true"
    effect: NoSchedule
```

### 3. Workload Configuration

#### Create Tolerations for Spot Instances
```yaml
# spot-tolerations.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spot-workload
spec:
  template:
    spec:
      tolerations:
      - key: spot-instance
        operator: Equal
        value: "true"
        effect: NoSchedule
      nodeSelector:
        spot-instance: "true"
```

#### Configure Pod Disruption Budget
```yaml
# spot-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: spot-workload-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: spot-workload
```

### 4. Autoscaling Configuration

#### Cluster Autoscaler Configuration
```yaml
# cluster-autoscaler-config.yaml
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
      min: 32
      max: 512
  scaleDown:
    enabled: true
    delayAfterAdd: 10m
    delayAfterDelete: 10m
    delayAfterFailure: 3m
    unneededTime: 10m
```

#### Node Group Autoscaler
```yaml
# node-group-autoscaler.yaml
apiVersion: autoscaling.openshift.io/v1
kind: MachineAutoscaler
metadata:
  name: spot-pool-autoscaler
spec:
  minReplicas: 1
  maxReplicas: 5
  scaleTargetRef:
    apiVersion: machine.openshift.io/v1beta1
    kind: MachineSet
    name: spot-pool
```

### 5. Monitoring and Alerting

#### Prometheus Rules for Spot Instances
```yaml
# spot-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: spot-instance-alerts
spec:
  groups:
  - name: spot-instances
    rules:
    - alert: SpotInstanceTerminationWarning
      expr: kube_node_status_condition{condition="Ready",status="true"} * on(node) kube_node_labels{label_spot_instance="true"}
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: Spot instance termination warning
        description: Spot instance {{ $labels.node }} may be terminated soon
```

#### Grafana Dashboard for Spot Instance Monitoring
```json
{
  "dashboard": {
    "title": "Spot Instance Monitoring",
    "panels": [
      {
        "title": "Spot Instance Count",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "count(kube_node_labels{label_spot_instance=\"true\"})",
            "legendFormat": "Spot Instances"
          }
        ]
      },
      {
        "title": "Spot Instance Cost Savings",
        "type": "stat",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "sum(spot_instance_cost_savings)",
            "legendFormat": "Total Savings"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

### Workload Management
- Use spot instances for stateless, fault-tolerant workloads
- Implement graceful shutdown procedures
- Use multiple availability zones for better availability
- Monitor spot instance termination notices

### Cost Optimization
- Set appropriate bid prices
- Use mixed instance types
- Implement auto-scaling based on spot instance availability
- Monitor and adjust spot instance usage patterns

### Reliability
- Implement proper health checks
- Use pod disruption budgets
- Configure appropriate replica counts
- Monitor spot instance interruption rates

## Next Steps
1. Monitor spot instance usage and cost savings
2. Optimize spot instance configurations
3. Implement cost controls and budgets
4. Document spot instance usage patterns and best practices
