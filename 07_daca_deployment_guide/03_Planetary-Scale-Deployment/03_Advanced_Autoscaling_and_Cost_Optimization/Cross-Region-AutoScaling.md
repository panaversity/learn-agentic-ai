# Cross-Region AutoScaling

## Overview
This guide provides detailed instructions for implementing cross-region autoscaling in Kubernetes deployments, ensuring optimal resource utilization and cost efficiency across multiple regions.

## Prerequisites
- Multi-region Kubernetes clusters
- kubectl configured
- Helm installed
- Basic understanding of autoscaling concepts
- Access to create and modify resources

## Cluster Autoscaler Setup

### 1. Install Cluster Autoscaler
```bash
# Add Helm repository
helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm repo update

# Install Cluster Autoscaler
helm install cluster-autoscaler autoscaler/cluster-autoscaler \
  --namespace kube-system \
  --set autoDiscovery.clusterName=my-cluster \
  --set awsRegion=us-east-1 \
  --set rbac.create=true \
  --set extraArgs.balance-similar-node-groups=true \
  --set extraArgs.skip-nodes-with-system-pods=false \
  --set extraArgs.scale-down-unneeded-time=10m \
  --set extraArgs.scale-down-delay-after-add=10m
```

### 2. Configure Cross-Region Scaling
```yaml
# cross-region-autoscaler.yaml
apiVersion: autoscaling.openshift.io/v1
kind: ClusterAutoscaler
metadata:
  name: cross-region-autoscaler
spec:
  resourceLimits:
    maxNodesTotal: 100
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

## Horizontal Pod Autoscaling

### 1. Configure HPA
```yaml
# cross-region-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cross-region-hpa
  namespace: my-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Pods
        value: 4
        periodSeconds: 60
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 4
        periodSeconds: 60
      - type: Percent
        value: 50
        periodSeconds: 60
```

### 2. Configure Custom Metrics
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
    - seriesQuery: 'http_requests_total{namespace!="",pod!=""}'
      resources:
        overrides:
          namespace:
            resource: "namespace"
          pod:
            resource: "pod"
      name:
        matches: "http_requests_total"
        as: "http_requests_per_second"
      metricsQuery: 'sum(rate(http_requests_total{<<.LabelMatchers>>}[2m])) by (<<.GroupBy>>)'
```

## Vertical Pod Autoscaling

### 1. Install VPA
```bash
# Add VPA Helm repository
helm repo add fairwinds-stable https://charts.fairwinds.com/stable
helm repo update

# Install VPA
helm install vpa fairwinds-stable/vpa \
  --namespace kube-system \
  --set recommender.enabled=true \
  --set updater.enabled=true \
  --set admissionController.enabled=true
```

### 2. Configure VPA
```yaml
# vpa-config.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
  namespace: my-app
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: 100m
        memory: 50Mi
      maxAllowed:
        cpu: 1
        memory: 500Mi
      controlledResources: ["cpu", "memory"]
```

## Monitoring and Alerts

### 1. Configure Prometheus Rules
```yaml
# autoscaling-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: autoscaling-alerts
  namespace: monitoring
spec:
  groups:
  - name: autoscaling
    rules:
    - alert: HighScalingActivity
      expr: rate(hpa_scaling_events_total[5m]) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High scaling activity detected
        description: More than 0.1 scaling events per minute for 5 minutes
    - alert: FailedScaling
      expr: hpa_scaling_errors_total > 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: Scaling failures detected
        description: HPA has failed to scale the deployment
```

### 2. Create Monitoring Dashboard
```yaml
# autoscaling-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: autoscaling-monitoring
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Cross-Region Autoscaling",
        "panels": [
          {
            "title": "Cluster Node Count",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "kube_node_status_capacity",
                "legendFormat": "{{node}}"
              }
            ]
          },
          {
            "title": "Pod Count",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "kube_pod_info",
                "legendFormat": "{{namespace}}"
              }
            ]
          },
          {
            "title": "Resource Utilization",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "sum(rate(container_cpu_usage_seconds_total[5m])) by (namespace)",
                "legendFormat": "CPU {{namespace}}"
              },
              {
                "expr": "sum(container_memory_usage_bytes) by (namespace)",
                "legendFormat": "Memory {{namespace}}"
              }
            ]
          }
        ]
      }
    }
```

## Best Practices

### 1. Autoscaling Configuration
- Set appropriate thresholds
- Configure stabilization windows
- Monitor scaling events
- Regular review
- Document changes

### 2. Resource Management
- Right-size resources
- Monitor utilization
- Set limits and requests
- Regular optimization
- Document policies

### 3. Cost Optimization
- Use spot instances
- Implement scaling policies
- Monitor costs
- Regular review
- Document savings

## Next Steps
1. Monitor scaling behavior
2. Optimize thresholds
3. Implement cost controls
4. Regular reviews
5. Documentation
