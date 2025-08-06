# Distributed Tracing Across Regions

## Overview
This guide provides detailed instructions for implementing distributed tracing across multiple regions in Kubernetes deployments, ensuring comprehensive observability of request flows.

## Prerequisites
- Multi-region Kubernetes clusters
- kubectl configured
- Helm installed
- Basic understanding of tracing concepts
- Access to create and modify resources

## Jaeger Setup

### 1. Install Jaeger
```bash
# Add Helm repository
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

# Install Jaeger
helm install jaeger jaegertracing/jaeger \
  --namespace tracing \
  --set storage.type=elasticsearch \
  --set storage.elasticsearch.host=elasticsearch-master.tracing.svc.cluster.local \
  --set storage.elasticsearch.port=9200 \
  --set storage.elasticsearch.indexPrefix=jaeger
```

### 2. Configure Jaeger
```yaml
# jaeger-config.yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger
  namespace: tracing
spec:
  strategy: production
  storage:
    type: elasticsearch
    options:
      es:
        server-urls: http://elasticsearch-master.tracing.svc.cluster.local:9200
        index-prefix: jaeger
  ingress:
    enabled: true
    annotations:
      kubernetes.io/ingress.class: nginx
    hosts:
    - jaeger.example.com
```

## OpenTelemetry Setup

### 1. Install OpenTelemetry Collector
```bash
# Add Helm repository
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

# Install OpenTelemetry Collector
helm install otel-collector open-telemetry/opentelemetry-collector \
  --namespace tracing \
  --set mode=deployment \
  --set config.receivers.otlp.protocols.grpc.endpoint=0.0.0.0:4317 \
  --set config.receivers.otlp.protocols.http.endpoint=0.0.0.0:4318 \
  --set config.exporters.jaeger.endpoint=jaeger-collector.tracing.svc.cluster.local:14250 \
  --set config.service.pipelines.traces.receivers=otlp \
  --set config.service.pipelines.traces.exporters=jaeger
```

### 2. Configure OpenTelemetry
```yaml
# otel-config.yaml
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: otel-collector
  namespace: tracing
spec:
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
          http:
    processors:
      batch:
        timeout: 1s
        send_batch_size: 1024
    exporters:
      jaeger:
        endpoint: jaeger-collector.tracing.svc.cluster.local:14250
        tls:
          insecure: true
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [jaeger]
```

## Application Configuration

### 1. Configure Tracing in Applications
```yaml
# app-tracing.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-app
spec:
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        env:
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://otel-collector.tracing.svc.cluster.local:4317"
        - name: OTEL_SERVICE_NAME
          value: "my-app"
        - name: OTEL_RESOURCE_ATTRIBUTES
          value: "region=us-east-1"
```

### 2. Configure Dapr Tracing
```yaml
# dapr-tracing.yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-tracing
  namespace: my-app
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: http://jaeger-collector.tracing.svc.cluster.local:9411/api/v2/spans
```

## Cross-Region Tracing

### 1. Configure Trace Context Propagation
```yaml
# trace-context.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trace-context
  namespace: tracing
data:
  config.yaml: |
    propagation:
      type: w3c
    sampling:
      type: probabilistic
      param: 0.1
    context:
      baggage:
        enabled: true
        restrictions:
          maxCount: 10
          maxLength: 1024
```

### 2. Configure Trace Routing
```yaml
# trace-routing.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: trace-routing
  namespace: tracing
data:
  routing.yaml: |
    routes:
    - from: us-east-1
      to: us-west-2
      sampling: 0.5
    - from: us-west-2
      to: eu-west-1
      sampling: 0.5
    - from: eu-west-1
      to: us-east-1
      sampling: 0.5
```

## Monitoring and Visualization

### 1. Configure Jaeger UI
```yaml
# jaeger-ui.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jaeger-ui
  namespace: tracing
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  rules:
  - host: jaeger.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: jaeger-query
            port:
              number: 16686
```

### 2. Create Tracing Dashboard
```yaml
# tracing-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: tracing-monitoring
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Distributed Tracing",
        "panels": [
          {
            "title": "Trace Duration",
            "type": "graph",
            "datasource": "Jaeger",
            "targets": [
              {
                "query": "histogram_quantile(0.95, sum(rate(trace_duration_seconds_bucket[5m])) by (le, service))",
                "legendFormat": "{{service}}"
              }
            ]
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "datasource": "Jaeger",
            "targets": [
              {
                "query": "sum(rate(trace_errors_total[5m])) by (service)",
                "legendFormat": "{{service}}"
              }
            ]
          },
          {
            "title": "Cross-Region Traces",
            "type": "table",
            "datasource": "Jaeger",
            "targets": [
              {
                "query": "sum(trace_count) by (source_region, target_region)",
                "legendFormat": "{{source_region}} -> {{target_region}}"
              }
            ]
          }
        ]
      }
    }
```

## Best Practices

### 1. Tracing Configuration
- Set appropriate sampling rates
- Configure context propagation
- Monitor trace volume
- Regular review
- Document configurations

### 2. Performance
- Optimize trace collection
- Monitor resource usage
- Implement rate limiting
- Regular optimization
- Document procedures

### 3. Security
- Secure trace data
- Control access
- Monitor usage
- Regular audits
- Document policies

## Next Steps
1. Monitor trace performance
2. Optimize configurations
3. Implement security controls
4. Regular reviews
5. Documentation
