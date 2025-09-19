# Installing Prometheus and Grafana

## Overview
This guide provides detailed instructions for installing and configuring Prometheus and Grafana for monitoring Kubernetes deployments.

## Prerequisites
- Kubernetes cluster
- kubectl configured
- Helm installed
- Basic understanding of monitoring concepts
- Access to create and modify resources

## Installation

### 1. Add Helm Repositories
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### 2. Create Monitoring Namespace
```bash
kubectl create namespace monitoring
```

### 3. Install Prometheus
```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues=false \
  --set grafana.enabled=true \
  --set grafana.adminPassword=admin \
  --set grafana.service.type=LoadBalancer
```

## Configuration

### 1. Configure Prometheus
```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    scrape_configs:
    - job_name: 'kubernetes-apiservers'
      kubernetes_sd_configs:
      - role: endpoints
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
    - job_name: 'kubernetes-nodes'
      kubernetes_sd_configs:
      - role: node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
```

### 2. Configure Grafana
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
```

### 3. Create Sample Dashboard
```yaml
# grafana-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: kubernetes-cluster-monitoring
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Kubernetes Cluster Monitoring",
        "panels": [
          {
            "title": "Cluster CPU Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "sum(rate(container_cpu_usage_seconds_total[5m]))",
                "legendFormat": "CPU Usage"
              }
            ]
          },
          {
            "title": "Cluster Memory Usage",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "sum(container_memory_usage_bytes)",
                "legendFormat": "Memory Usage"
              }
            ]
          },
          {
            "title": "Pod Status",
            "type": "table",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "kube_pod_status_phase",
                "legendFormat": "{{pod}}"
              }
            ]
          }
        ]
      }
    }
```

## Access Configuration

### 1. Configure Ingress (Optional)
```yaml
# monitoring-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: monitoring-ingress
  namespace: monitoring
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  rules:
  - host: prometheus.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prometheus-server
            port:
              number: 80
  - host: grafana.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 80
```

### 2. Configure Authentication (Optional)
```yaml
# grafana-auth.yaml
apiVersion: v1
kind: Secret
metadata:
  name: grafana-auth
  namespace: monitoring
type: Opaque
data:
  GF_SECURITY_ADMIN_USER: YWRtaW4=  # admin
  GF_SECURITY_ADMIN_PASSWORD: YWRtaW4=  # admin
```

## Monitoring Configuration

### 1. Configure Alerts
```yaml
# prometheus-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: prometheus-alerts
  namespace: monitoring
spec:
  groups:
  - name: kubernetes
    rules:
    - alert: HighCPUUsage
      expr: sum(rate(container_cpu_usage_seconds_total[5m])) > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High CPU usage detected
        description: CPU usage is above 80% for 5 minutes
    - alert: HighMemoryUsage
      expr: sum(container_memory_usage_bytes) / sum(machine_memory_bytes) > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High memory usage detected
        description: Memory usage is above 80% for 5 minutes
```

## Best Practices

### 1. Prometheus
- Configure appropriate retention period
- Set up backup strategy
- Monitor Prometheus metrics
- Regular review
- Document configurations

### 2. Grafana
- Organize dashboards
- Set up authentication
- Configure alerts
- Regular review
- Document dashboards

### 3. Monitoring
- Set up comprehensive dashboards
- Configure meaningful alerts
- Regular review
- Document findings
- Update configurations

## Next Steps
1. Configure additional dashboards
2. Set up alert notifications
3. Implement backup strategy
4. Regular reviews
5. Documentation
