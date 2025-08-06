# Centralized Monitoring Aggregation

## Overview
This guide provides detailed instructions for implementing centralized monitoring aggregation in multi-region Kubernetes deployments, ensuring comprehensive observability across all regions.

## Prerequisites
- Multi-region Kubernetes clusters
- kubectl configured
- Helm installed
- Basic understanding of monitoring concepts
- Access to create and modify resources

## Prometheus Federation Setup

### 1. Install Prometheus
```bash
# Add Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues=false \
  --set grafana.enabled=true
```

### 2. Configure Federation
```yaml
# prometheus-federation.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-federation
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    scrape_configs:
    - job_name: 'federate'
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
          - '{job="prometheus"}'
          - '{job="node-exporter"}'
          - '{job="kube-state-metrics"}'
      static_configs:
        - targets:
          - 'prometheus-region-1.monitoring.svc.cluster.local:9090'
          - 'prometheus-region-2.monitoring.svc.cluster.local:9090'
          - 'prometheus-region-3.monitoring.svc.cluster.local:9090'
```

## Thanos Setup

### 1. Install Thanos
```bash
# Add Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Thanos
helm install thanos bitnami/thanos \
  --namespace monitoring \
  --set objstore.config=|
    type: S3
    config:
      bucket: thanos-data
      endpoint: s3.amazonaws.com
      access_key: ${AWS_ACCESS_KEY_ID}
      secret_key: ${AWS_SECRET_ACCESS_KEY}
```

### 2. Configure Thanos Components
```yaml
# thanos-config.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: thanos-query
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: thanos-query
  template:
    metadata:
      labels:
        app: thanos-query
    spec:
      containers:
      - name: thanos-query
        image: thanosio/thanos:v0.28.0
        args:
        - query
        - --http-address=0.0.0.0:10902
        - --grpc-address=0.0.0.0:10901
        - --store=thanos-store.monitoring.svc.cluster.local:10901
        - --store=thanos-sidecar-region-1.monitoring.svc.cluster.local:10901
        - --store=thanos-sidecar-region-2.monitoring.svc.cluster.local:10901
        - --store=thanos-sidecar-region-3.monitoring.svc.cluster.local:10901
        ports:
        - name: http
          containerPort: 10902
        - name: grpc
          containerPort: 10901
```

## Grafana Configuration

### 1. Configure Data Sources
```yaml
# grafana-datasources.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  prometheus.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: http://prometheus-server.monitoring.svc.cluster.local
      access: proxy
      isDefault: true
    - name: Thanos
      type: prometheus
      url: http://thanos-query.monitoring.svc.cluster.local:10902
      access: proxy
```

### 2. Create Global Dashboard
```yaml
# global-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: global-monitoring
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Global Monitoring",
        "panels": [
          {
            "title": "Cluster Status",
            "type": "table",
            "datasource": "Thanos",
            "targets": [
              {
                "expr": "kube_cluster_status",
                "legendFormat": "{{region}}"
              }
            ]
          },
          {
            "title": "Resource Usage",
            "type": "graph",
            "datasource": "Thanos",
            "targets": [
              {
                "expr": "sum(rate(container_cpu_usage_seconds_total[5m])) by (region)",
                "legendFormat": "CPU {{region}}"
              },
              {
                "expr": "sum(container_memory_usage_bytes) by (region)",
                "legendFormat": "Memory {{region}}"
              }
            ]
          },
          {
            "title": "Request Rate",
            "type": "graph",
            "datasource": "Thanos",
            "targets": [
              {
                "expr": "sum(rate(http_requests_total[5m])) by (region)",
                "legendFormat": "{{region}}"
              }
            ]
          }
        ]
      }
    }
```

## Alerting Configuration

### 1. Configure Alertmanager
```yaml
# alertmanager-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
    route:
      group_by: ['alertname', 'region']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
      receiver: 'slack'
    receivers:
    - name: 'slack'
      slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#alerts'
        send_resolved: true
```

### 2. Configure Alert Rules
```yaml
# alert-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: global-alerts
  namespace: monitoring
spec:
  groups:
  - name: global
    rules:
    - alert: HighErrorRate
      expr: sum(rate(http_requests_total{status=~"5.."}[5m])) by (region) / sum(rate(http_requests_total[5m])) by (region) > 0.01
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: High error rate in {{ $labels.region }}
        description: Error rate is above 1% in {{ $labels.region }}
    - alert: HighLatency
      expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, region)) > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High latency in {{ $labels.region }}
        description: 95th percentile latency is above 1s in {{ $labels.region }}
```

## Best Practices

### 1. Monitoring Configuration
- Set appropriate scrape intervals
- Configure retention policies
- Monitor resource usage
- Regular review
- Document configurations

### 2. Data Management
- Implement data retention
- Configure backup strategy
- Monitor storage usage
- Regular cleanup
- Document procedures

### 3. Alert Management
- Set meaningful thresholds
- Configure notification channels
- Regular review
- Document procedures
- Update configurations

## Next Steps
1. Monitor system performance
2. Optimize configurations
3. Implement backup strategy
4. Regular reviews
5. Documentation
