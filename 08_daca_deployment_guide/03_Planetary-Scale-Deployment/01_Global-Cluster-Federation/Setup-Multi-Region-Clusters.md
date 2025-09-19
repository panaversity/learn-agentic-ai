# Setting Up Multi-Region Kubernetes Clusters

## Overview
This guide provides detailed instructions for setting up and managing multi-region Kubernetes clusters, ensuring high availability and disaster recovery capabilities.

## Prerequisites
- Access to multiple cloud regions
- kubectl configured
- Helm installed
- Basic understanding of Kubernetes concepts
- Access to create and modify resources

## Cluster Setup

### 1. Create Clusters in Different Regions
```bash
# Create cluster in Region 1
civo kubernetes create cluster-1 \
  --region NYC1 \
  --nodes 3 \
  --size g4s.kube.medium

# Create cluster in Region 2
civo kubernetes create cluster-2 \
  --region LON1 \
  --nodes 3 \
  --size g4s.kube.medium

# Create cluster in Region 3
civo kubernetes create cluster-3 \
  --region FRA1 \
  --nodes 3 \
  --size g4s.kube.medium
```

### 2. Configure Cluster Access
```bash
# Get kubeconfig for each cluster
civo kubernetes config cluster-1 > cluster-1.yaml
civo kubernetes config cluster-2 > cluster-2.yaml
civo kubernetes config cluster-3 > cluster-3.yaml

# Set up kubectl contexts
kubectl config --kubeconfig=cluster-1.yaml rename-context default cluster-1
kubectl config --kubeconfig=cluster-2.yaml rename-context default cluster-2
kubectl config --kubeconfig=cluster-3.yaml rename-context default cluster-3

# Merge kubeconfigs
KUBECONFIG=cluster-1.yaml:cluster-2.yaml:cluster-3.yaml kubectl config view --flatten > config
mv config ~/.kube/config
```

## Network Configuration

### 1. Set Up VPC Peering
```yaml
# vpc-peering.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-cross-region
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          region: "region-1"
    - namespaceSelector:
        matchLabels:
          region: "region-2"
    - namespaceSelector:
        matchLabels:
          region: "region-3"
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          region: "region-1"
    - namespaceSelector:
        matchLabels:
          region: "region-2"
    - namespaceSelector:
        matchLabels:
          region: "region-3"
```

### 2. Configure DNS
```yaml
# dns-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
          pods insecure
          fallthrough in-addr.arpa ip6.arpa
        }
        prometheus :9153
        forward . /etc/resolv.conf
        cache 30
        loop
        reload
        loadbalance
    }
```

## Federation Setup

### 1. Install KubeFed
```bash
# Add KubeFed Helm repository
helm repo add kubefed https://raw.githubusercontent.com/kubernetes-sigs/kubefed/master/charts
helm repo update

# Install KubeFed
helm install kubefed kubefed/kubefed \
  --namespace kube-federation-system \
  --create-namespace \
  --version 0.9.0
```

### 2. Configure Federation
```yaml
# federation-config.yaml
apiVersion: core.kubefed.io/v1beta1
kind: KubeFedCluster
metadata:
  name: cluster-1
  namespace: kube-federation-system
spec:
  apiEndpoint: https://cluster-1.example.com
  secretRef:
    name: cluster-1
---
apiVersion: core.kubefed.io/v1beta1
kind: KubeFedCluster
metadata:
  name: cluster-2
  namespace: kube-federation-system
spec:
  apiEndpoint: https://cluster-2.example.com
  secretRef:
    name: cluster-2
---
apiVersion: core.kubefed.io/v1beta1
kind: KubeFedCluster
metadata:
  name: cluster-3
  namespace: kube-federation-system
spec:
  apiEndpoint: https://cluster-3.example.com
  secretRef:
    name: cluster-3
```

## Application Deployment

### 1. Create Federated Namespace
```yaml
# federated-namespace.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedNamespace
metadata:
  name: my-app
  namespace: default
spec:
  placement:
    clusters:
    - name: cluster-1
    - name: cluster-2
    - name: cluster-3
```

### 2. Deploy Federated Application
```yaml
# federated-deployment.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDeployment
metadata:
  name: my-app
  namespace: my-app
spec:
  template:
    metadata:
      labels:
        app: my-app
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: my-app
      template:
        metadata:
          labels:
            app: my-app
        spec:
          containers:
          - name: my-app
            image: my-app:latest
            ports:
            - containerPort: 8080
  placement:
    clusters:
    - name: cluster-1
    - name: cluster-2
    - name: cluster-3
  overrides:
  - clusterName: cluster-1
    clusterOverrides:
    - path: "/spec/replicas"
      value: 2
  - clusterName: cluster-2
    clusterOverrides:
    - path: "/spec/replicas"
      value: 3
  - clusterName: cluster-3
    clusterOverrides:
    - path: "/spec/replicas"
      value: 1
```

## Monitoring and Observability

### 1. Configure Prometheus Federation
```yaml
# prometheus-federation.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: prometheus-federation
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: prometheus
  endpoints:
  - port: web
    interval: 30s
    path: /federate
    params:
      match[]:
      - '{job="prometheus"}'
      - '{job="node-exporter"}'
```

### 2. Set Up Grafana Dashboards
```yaml
# multi-region-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: multi-region-monitoring
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Multi-Region Monitoring",
        "panels": [
          {
            "title": "Cluster Status",
            "type": "table",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "kube_cluster_status",
                "legendFormat": "{{cluster}}"
              }
            ]
          },
          {
            "title": "Cross-Region Latency",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, cluster))",
                "legendFormat": "{{cluster}}"
              }
            ]
          }
        ]
      }
    }
```

## Best Practices

### 1. Cluster Management
- Regular updates
- Backup strategy
- Monitoring setup
- Security policies
- Documentation

### 2. Network Configuration
- Secure communication
- Load balancing
- DNS management
- Regular testing
- Documentation

### 3. Application Deployment
- Consistent configuration
- Version control
- Testing strategy
- Rollback plan
- Documentation

## Next Steps
1. Configure backup and recovery
2. Set up monitoring
3. Implement security policies
4. Regular testing
5. Documentation
