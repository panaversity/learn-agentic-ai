# Centralized Logging with Loki or EFK

## Overview
This guide provides detailed instructions for setting up centralized logging in Kubernetes using either Loki or the EFK (Elasticsearch, Fluentd, Kibana) stack.

## Prerequisites
- Kubernetes cluster
- kubectl configured
- Helm installed
- Basic understanding of logging concepts
- Access to create and modify resources

## Loki Setup

### 1. Install Loki Stack
```bash
# Add Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Loki stack
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set promtail.enabled=true \
  --set grafana.enabled=true \
  --set prometheus.enabled=true \
  --set prometheus.alertmanager.persistentVolume.enabled=false \
  --set prometheus.server.persistentVolume.enabled=false
```

### 2. Configure Loki
```yaml
# loki-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: loki-config
  namespace: monitoring
data:
  loki.yaml: |
    auth_enabled: false
    server:
      http_listen_port: 3100
    ingester:
      lifecycler:
        address: 127.0.0.1
        ring:
          kvstore:
            store: inmemory
          replication_factor: 1
      chunk_idle_period: 5m
      chunk_retain_period: 30s
    schema_config:
      configs:
        - from: 2020-05-15
          store: boltdb
          object_store: filesystem
          schema: v11
          index:
            prefix: index_
            period: 24h
    storage_config:
      boltdb:
        directory: /data/loki/index
      filesystem:
        directory: /data/loki/chunks
    limits_config:
      enforce_metric_name: false
      reject_old_samples: true
      reject_old_samples_max_age: 168h
```

### 3. Configure Promtail
```yaml
# promtail-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: promtail-config
  namespace: monitoring
data:
  promtail.yaml: |
    server:
      http_listen_port: 9080
      grpc_listen_port: 0
    positions:
      filename: /tmp/positions.yaml
    clients:
      - url: http://loki:3100/loki/api/v1/push
    scrape_configs:
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_name]
            target_label: __service__
          - source_labels: [__meta_kubernetes_pod_node_name]
            target_label: __host__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_pod_container_name]
            target_label: container
          - replacement: /var/log/pods/*$1/*.log
            separator: /
            source_labels:
              - __meta_kubernetes_pod_uid
              - __meta_kubernetes_pod_container_name
            target_label: __path__
```

## EFK Setup

### 1. Install Elasticsearch
```bash
# Add Elastic Helm repository
helm repo add elastic https://helm.elastic.co
helm repo update

# Install Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --set replicas=1 \
  --set minimumMasterNodes=1 \
  --set persistence.enabled=false
```

### 2. Install Fluentd
```yaml
# fluentd-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: logging
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      time_format %Y-%m-%dT%H:%M:%S.%NZ
      tag kubernetes.*
      format json
      read_from_head true
    </source>
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch-master
      port 9200
      logstash_format true
      logstash_prefix kubernetes
      include_tag_key true
      type_name fluentd
    </match>
```

### 3. Install Kibana
```bash
# Install Kibana
helm install kibana elastic/kibana \
  --namespace logging \
  --set elasticsearchHosts=http://elasticsearch-master:9200
```

## Log Collection Configuration

### 1. Application Logging
```yaml
# app-logging.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:latest
    env:
    - name: LOG_LEVEL
      value: "INFO"
    - name: LOG_FORMAT
      value: "json"
```

### 2. Log Rotation
```yaml
# log-rotation.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: log-rotation
  namespace: logging
data:
  logrotate.conf: |
    /var/log/containers/*.log {
      daily
      rotate 7
      compress
      delaycompress
      missingok
      notifempty
      create 0644 root root
    }
```

## Monitoring and Visualization

### 1. Loki Dashboard
```yaml
# loki-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: loki-dashboard
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Loki Logs",
        "panels": [
          {
            "title": "Log Volume",
            "type": "graph",
            "datasource": "Loki",
            "targets": [
              {
                "expr": "rate(loki_log_entries_total[5m])",
                "legendFormat": "{{namespace}}"
              }
            ]
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "datasource": "Loki",
            "targets": [
              {
                "expr": "rate(loki_log_entries_total{level=\"error\"}[5m])",
                "legendFormat": "{{namespace}}"
              }
            ]
          }
        ]
      }
    }
```

### 2. Kibana Dashboard
```yaml
# kibana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kibana-dashboard
  namespace: logging
data:
  dashboard.json: |
    {
      "title": "Application Logs",
      "panels": [
        {
          "type": "visualization",
          "id": "log-volume",
          "attributes": {
            "title": "Log Volume",
            "type": "line",
            "params": {
              "type": "line",
              "grid": {
                "categoryLines": false
              },
              "categoryAxes": [
                {
                  "id": "CategoryAxis-1",
                  "type": "category",
                  "position": "bottom"
                }
              ],
              "valueAxes": [
                {
                  "id": "ValueAxis-1",
                  "type": "value",
                  "position": "left"
                }
              ]
            }
          }
        }
      ]
    }
```

## Best Practices

### 1. Log Management
- Use structured logging
- Implement log rotation
- Set appropriate log levels
- Monitor log volume
- Regular cleanup

### 2. Performance
- Optimize log collection
- Monitor resource usage
- Scale log storage
- Implement retention
- Regular optimization

### 3. Security
- Encrypt log data
- Control access
- Monitor access
- Regular audits
- Document procedures

## Next Steps
1. Configure alerts
2. Set up retention
3. Optimize performance
4. Regular reviews
5. Documentation
