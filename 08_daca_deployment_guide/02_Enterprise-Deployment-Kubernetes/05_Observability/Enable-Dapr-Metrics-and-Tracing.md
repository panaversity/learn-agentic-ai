# Enabling Dapr Metrics and Tracing

## Overview
This guide provides detailed instructions for enabling and configuring Dapr metrics and tracing in Kubernetes deployments.

## Prerequisites
- Kubernetes cluster
- Dapr installed
- kubectl configured
- Basic understanding of Dapr concepts
- Access to create and modify resources

## Metrics Configuration

### 1. Enable Dapr Metrics
```yaml
# dapr-metrics.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-metrics
spec:
  tracing:
    samplingRate: "1"
  metric:
    enabled: true
    port: 9090
    path: /metrics
```

### 2. Configure Prometheus
```yaml
# prometheus-config.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: dapr-metrics
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: dapr
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### 3. Create Metrics Dashboard
```yaml
# dapr-metrics-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: dapr-metrics
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Dapr Metrics",
        "panels": [
          {
            "title": "Dapr Sidecar CPU",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(container_cpu_usage_seconds_total{container=\"daprd\"}[5m])",
                "legendFormat": "{{pod}}"
              }
            ]
          },
          {
            "title": "Dapr Sidecar Memory",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "container_memory_usage_bytes{container=\"daprd\"}",
                "legendFormat": "{{pod}}"
              }
            ]
          },
          {
            "title": "Dapr HTTP Requests",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(dapr_http_server_request_count[5m])",
                "legendFormat": "{{method}} {{path}}"
              }
            ]
          }
        ]
      }
    }
```

## Tracing Configuration

### 1. Configure Zipkin
```yaml
# zipkin-config.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zipkin
  namespace: dapr-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zipkin
  template:
    metadata:
      labels:
        app: zipkin
    spec:
      containers:
      - name: zipkin
        image: openzipkin/zipkin:latest
        ports:
        - containerPort: 9411
---
apiVersion: v1
kind: Service
metadata:
  name: zipkin
  namespace: dapr-system
spec:
  selector:
    app: zipkin
  ports:
  - port: 9411
    targetPort: 9411
```

### 2. Configure Dapr Tracing
```yaml
# dapr-tracing.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-tracing
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: http://zipkin.dapr-system.svc.cluster.local:9411/api/v2/spans
```

### 3. Create Tracing Dashboard
```yaml
# dapr-tracing-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: dapr-tracing
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Dapr Tracing",
        "panels": [
          {
            "title": "Trace Duration",
            "type": "graph",
            "datasource": "Zipkin",
            "targets": [
              {
                "query": "trace_duration_seconds",
                "legendFormat": "{{service}}"
              }
            ]
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "datasource": "Zipkin",
            "targets": [
              {
                "query": "error_rate",
                "legendFormat": "{{service}}"
              }
            ]
          }
        ]
      }
    }
```

## Application Configuration

### 1. Enable Metrics in Application
```yaml
# app-metrics.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "my-app"
        dapr.io/metrics-port: "9090"
        dapr.io/metrics-path: "/metrics"
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        ports:
        - containerPort: 9090
          name: metrics
```

### 2. Enable Tracing in Application
```yaml
# app-tracing.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "my-app"
        dapr.io/config: "dapr-tracing"
    spec:
      containers:
      - name: my-app
        image: my-app:latest
```

## Monitoring and Alerts

### 1. Configure Alerts
```yaml
# dapr-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: dapr-alerts
  namespace: monitoring
spec:
  groups:
  - name: dapr
    rules:
    - alert: HighDaprLatency
      expr: rate(dapr_http_server_request_duration_seconds_sum[5m]) / rate(dapr_http_server_request_duration_seconds_count[5m]) > 0.5
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High Dapr latency detected
        description: Dapr request latency is above 500ms for 5 minutes
    - alert: HighDaprErrorRate
      expr: rate(dapr_http_server_request_count{status=~"5.."}[5m]) / rate(dapr_http_server_request_count[5m]) > 0.01
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: High Dapr error rate detected
        description: Dapr error rate is above 1% for 5 minutes
```

## Best Practices

### 1. Metrics
- Enable all relevant metrics
- Set appropriate sampling rates
- Monitor resource usage
- Regular review
- Document metrics

### 2. Tracing
- Configure appropriate sampling
- Monitor trace volume
- Regular cleanup
- Document procedures
- Regular review

### 3. Monitoring
- Set up comprehensive dashboards
- Configure meaningful alerts
- Regular review
- Document findings
- Update configurations

## Next Steps
1. Configure additional metrics
2. Set up custom dashboards
3. Implement alerts
4. Regular reviews
5. Documentation
