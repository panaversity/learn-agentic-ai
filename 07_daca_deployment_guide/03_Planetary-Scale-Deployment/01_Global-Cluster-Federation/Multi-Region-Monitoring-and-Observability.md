# Multi-Region Monitoring and Observability

## Objective
This guide provides detailed instructions for implementing comprehensive monitoring and observability across multiple regions using Prometheus, Grafana, and Azure Monitor.

## Prerequisites
- Multiple Kubernetes clusters in different regions
- kubectl configured for all clusters
- Helm installed
- Azure subscription with Monitor access
- Basic understanding of monitoring concepts
- Access to create and modify monitoring resources

## Step-by-Step Instructions

### 1. Configure Prometheus Federation

#### 1.1 Install Prometheus in Primary Cluster
```bash
# Add Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.replicas=2 \
  --set prometheus.prometheusSpec.retention=15d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName=managed-premium \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
```

#### 1.2 Configure Federation
```yaml
# prometheus-federation.yaml
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 2
  serviceAccountName: prometheus
  serviceMonitorSelector: {}
  podMonitorSelector: {}
  ruleSelector: {}
  alertSelector: {}
  remoteWrite:
  - url: "http://prometheus-federation.monitoring.svc.cluster.local:9090/api/v1/write"
  remoteRead:
  - url: "http://prometheus-federation.monitoring.svc.cluster.local:9090/api/v1/read"
```

### 2. Configure Grafana

#### 2.1 Install Grafana
```bash
# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=true \
  --set persistence.storageClassName=managed-premium \
  --set persistence.size=10Gi \
  --set adminPassword=admin \
  --set service.type=LoadBalancer
```

#### 2.2 Configure Dashboards
```yaml
# grafana-dashboards.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: monitoring
data:
  global-overview.json: |
    {
      "dashboard": {
        "title": "Global Overview",
        "panels": [
          {
            "title": "Cluster Health",
            "type": "stat",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "up{job=\"kubernetes-nodes\"}"
              }
            ]
          },
          {
            "title": "Request Rate",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])"
              }
            ]
          }
        ]
      }
    }
```

### 3. Configure Azure Monitor

#### 3.1 Set Up Log Analytics Workspace
```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group global-monitoring-rg \
  --workspace-name global-monitoring \
  --location eastus \
  --sku PerGB2018
```

#### 3.2 Configure Container Insights
```bash
# Enable Container Insights
az aks enable-addons \
  --resource-group global-monitoring-rg \
  --name eastus-cluster \
  --addons monitoring \
  --workspace-resource-id /subscriptions/{subscription-id}/resourcegroups/global-monitoring-rg/providers/microsoft.operationalinsights/workspaces/global-monitoring
```

### 4. Configure Alerting

#### 4.1 Set Up Prometheus Alerts
```yaml
# prometheus-alerts.yaml
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
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: High error rate detected
        description: Error rate is {{ $value }} requests per second
```

#### 4.2 Configure Azure Monitor Alerts
```bash
# Create action group
az monitor action-group create \
  --name global-alerts \
  --resource-group global-monitoring-rg \
  --action email admin admin@example.com

# Create alert rule
az monitor metrics alert create \
  --name "High CPU Usage" \
  --resource-group global-monitoring-rg \
  --scopes /subscriptions/{subscription-id}/resourceGroups/global-monitoring-rg/providers/Microsoft.ContainerService/managedClusters/eastus-cluster \
  --condition "avg Percentage CPU > 80" \
  --action-group global-alerts
```

## Validation

### 1. Verify Prometheus Setup
```bash
# Check Prometheus pods
kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus

# Check federation status
curl -s http://prometheus.monitoring.svc.cluster.local:9090/-/healthy
```

### 2. Test Grafana Access
```bash
# Get Grafana URL
kubectl get svc -n monitoring grafana

# Check dashboard access
curl -s http://grafana.monitoring.svc.cluster.local:3000/api/health
```

### 3. Monitor Azure Monitor
```bash
# Check Log Analytics workspace
az monitor log-analytics workspace show \
  --resource-group global-monitoring-rg \
  --workspace-name global-monitoring

# Check Container Insights
az monitor metrics list \
  --resource /subscriptions/{subscription-id}/resourceGroups/global-monitoring-rg/providers/Microsoft.ContainerService/managedClusters/eastus-cluster \
  --metric "container_cpu_usage_percentage"
```

## Common Issues and Solutions

### Issue 1: Prometheus Federation Problems
- **Solution**: Check network connectivity and configuration
- **Prevention**: Monitor federation metrics

### Issue 2: Grafana Dashboard Issues
- **Solution**: Verify dashboard configuration
- **Prevention**: Regular dashboard testing

### Issue 3: Azure Monitor Integration Problems
- **Solution**: Check workspace configuration
- **Prevention**: Monitor integration status

## Best Practices

### 1. Monitoring Configuration
- Use appropriate retention periods
- Configure proper scraping
- Monitor system health
- Regular updates
- Document setup

### 2. Alerting
- Set meaningful thresholds
- Configure proper notifications
- Monitor alert status
- Regular testing
- Document policies

### 3. Observability
- Implement comprehensive logging
- Configure proper metrics
- Monitor system behavior
- Regular reviews
- Document findings

## Next Steps
- Configure backup
- Set up disaster recovery
- Implement automation
- Regular reviews 