# Resource Sizing Guidelines for Kubernetes

## Overview
This guide provides detailed guidelines for sizing resources in Kubernetes deployments, ensuring optimal performance and cost-efficiency.

## Resource Types

### 1. Compute Resources
- CPU: Measured in cores or millicores
- Memory: Measured in bytes, KiB, MiB, or GiB
- Storage: Measured in bytes, KiB, MiB, or GiB
- Network: Measured in bits per second

### 2. Resource Limits
```yaml
# resource-limits.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:latest
    resources:
      requests:
        cpu: "500m"
        memory: "512Mi"
      limits:
        cpu: "1000m"
        memory: "1Gi"
```

## Sizing Guidelines

### 1. CPU Sizing
```yaml
# cpu-sizing.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-sizing
spec:
  containers:
  - name: cpu-sizing
    image: my-app:latest
    resources:
      requests:
        cpu: "500m"  # 0.5 CPU cores
      limits:
        cpu: "2000m" # 2 CPU cores
```

#### CPU Sizing Rules
- Start with 500m (0.5 cores) for basic applications
- Increase based on CPU profiling
- Set limits 2-4x requests
- Monitor CPU utilization
- Adjust based on load

### 2. Memory Sizing
```yaml
# memory-sizing.yaml
apiVersion: v1
kind: Pod
metadata:
  name: memory-sizing
spec:
  containers:
  - name: memory-sizing
    image: my-app:latest
    resources:
      requests:
        memory: "512Mi"
      limits:
        memory: "1Gi"
```

#### Memory Sizing Rules
- Start with 512Mi for basic applications
- Increase based on memory profiling
- Set limits 1.5-2x requests
- Monitor memory usage
- Watch for OOM kills

### 3. Storage Sizing
```yaml
# storage-sizing.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: storage-sizing
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### Storage Sizing Rules
- Start with 10Gi for basic applications
- Increase based on data growth
- Monitor storage usage
- Plan for expansion
- Consider backup needs

## Auto-scaling Configuration

### 1. Horizontal Pod Autoscaler
```yaml
# hpa-config.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
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
```

### 2. Vertical Pod Autoscaler
```yaml
# vpa-config.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"
```

## Monitoring and Optimization

### 1. Resource Metrics
```yaml
# metrics-config.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: resource-metrics
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: my-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### 2. Optimization Dashboard
```yaml
# optimization-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: resource-optimization
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Resource Optimization",
        "panels": [
          {
            "title": "CPU Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(container_cpu_usage_seconds_total[5m])",
                "legendFormat": "{{pod}}"
              }
            ]
          },
          {
            "title": "Memory Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "container_memory_usage_bytes",
                "legendFormat": "{{pod}}"
              }
            ]
          },
          {
            "title": "Storage Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "kubelet_volume_stats_used_bytes",
                "legendFormat": "{{persistentvolumeclaim}}"
              }
            ]
          }
        ]
      }
    }
```

## Best Practices

### 1. Resource Management
- Start with conservative limits
- Monitor resource usage
- Adjust based on metrics
- Implement auto-scaling
- Regular reviews

### 2. Cost Optimization
- Right-size resources
- Use spot instances
- Implement auto-scaling
- Monitor costs
- Regular optimization

### 3. Performance
- Balance resources
- Monitor bottlenecks
- Optimize configurations
- Regular testing
- Document changes

## Next Steps
1. Implement monitoring
2. Set up auto-scaling
3. Optimize resources
4. Regular reviews
5. Documentation
