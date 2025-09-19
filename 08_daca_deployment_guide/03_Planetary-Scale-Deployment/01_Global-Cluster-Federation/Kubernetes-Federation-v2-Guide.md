# Kubernetes Federation v2 Guide

## Objective
This guide provides detailed instructions for setting up and managing Kubernetes Federation v2 (KubeFed) to enable multi-cluster management and deployment across different regions and cloud providers.

## Prerequisites
- Multiple Kubernetes clusters (at least 2)
- kubectl configured for all clusters
- Helm installed
- Cluster admin access
- Basic understanding of Kubernetes concepts
- Access to create and modify federation resources

## Step-by-Step Instructions

### 1. Install KubeFed

#### 1.1 Add KubeFed Helm Repository
```bash
helm repo add kubefed https://raw.githubusercontent.com/kubernetes-sigs/kubefed/master/charts
helm repo update
```

#### 1.2 Install KubeFed
```bash
helm install kubefed kubefed/kubefed \
  --namespace kube-federation-system \
  --create-namespace \
  --version v0.10.0
```

#### 1.3 Verify Installation
```bash
kubectl get pods -n kube-federation-system
kubectl get federatedtypeconfigs
```

### 2. Configure Host Cluster

#### 2.1 Create Host Cluster Context
```bash
kubectl config use-context host-cluster
```

#### 2.2 Initialize Federation Control Plane
```bash
kubefedctl init federation \
  --host-cluster-context=host-cluster \
  --dns-provider=azure-dns \
  --dns-zone-name=example.com \
  --dns-provider-config=azure-dns-config.yaml
```

### 3. Join Member Clusters

#### 3.1 Join First Member Cluster
```bash
kubefedctl join cluster1 \
  --host-cluster-context=host-cluster \
  --cluster-context=cluster1 \
  --v=2
```

#### 3.2 Join Second Member Cluster
```bash
kubefedctl join cluster2 \
  --host-cluster-context=host-cluster \
  --cluster-context=cluster2 \
  --v=2
```

#### 3.3 Verify Cluster Membership
```bash
kubectl get kubefedclusters
```

### 4. Deploy Federated Resources

#### 4.1 Create Federated Namespace
```yaml
# federated-namespace.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedNamespace
metadata:
  name: production
  namespace: production
spec:
  placement:
    clusters:
    - name: cluster1
    - name: cluster2
```

#### 4.2 Create Federated Deployment
```yaml
# federated-deployment.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDeployment
metadata:
  name: ai-agent
  namespace: production
spec:
  template:
    metadata:
      labels:
        app: ai-agent
    spec:
      replicas: 3
      selector:
        matchLabels:
          app: ai-agent
      template:
        metadata:
          labels:
            app: ai-agent
        spec:
          containers:
          - name: agent
            image: ai-agent:latest
            ports:
            - containerPort: 8080
  placement:
    clusters:
    - name: cluster1
    - name: cluster2
  overrides:
  - clusterName: cluster1
    clusterOverrides:
    - path: "/spec/replicas"
      value: 5
```

#### 4.3 Create Federated Service
```yaml
# federated-service.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedService
metadata:
  name: ai-agent
  namespace: production
spec:
  template:
    metadata:
      labels:
        app: ai-agent
    spec:
      selector:
        app: ai-agent
      ports:
      - port: 80
        targetPort: 8080
  placement:
    clusters:
    - name: cluster1
    - name: cluster2
```

### 5. Configure Cross-Cluster Discovery

#### 5.1 Create Federated Ingress
```yaml
# federated-ingress.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedIngress
metadata:
  name: ai-agent
  namespace: production
spec:
  template:
    metadata:
      annotations:
        kubernetes.io/ingress.class: nginx
    spec:
      rules:
      - host: ai-agent.example.com
        http:
          paths:
          - path: /
            backend:
              serviceName: ai-agent
              servicePort: 80
  placement:
    clusters:
    - name: cluster1
    - name: cluster2
```

#### 5.2 Configure DNS
```yaml
# federated-dns.yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedDNS
metadata:
  name: ai-agent
  namespace: production
spec:
  template:
    spec:
      rules:
      - host: ai-agent.example.com
        paths:
        - path: /
          serviceName: ai-agent
          servicePort: 80
  placement:
    clusters:
    - name: cluster1
    - name: cluster2
```

## Validation

### 1. Verify Federation Setup
```bash
# Check federation control plane
kubectl get pods -n kube-federation-system

# Check cluster membership
kubectl get kubefedclusters

# Check federated resources
kubectl get federateddeployments
kubectl get federatedservices
kubectl get federatedingresses
```

### 2. Test Cross-Cluster Communication
```bash
# Test service access
kubectl exec -it test-pod -- curl http://ai-agent.production.svc.cluster.local

# Test ingress access
curl http://ai-agent.example.com
```

### 3. Monitor Federation Status
```bash
# Check resource distribution
kubectl get deployments --all-namespaces

# Check service status
kubectl get services --all-namespaces

# Check ingress status
kubectl get ingresses --all-namespaces
```

## Common Issues and Solutions

### Issue 1: Federation Control Plane Issues
- **Solution**: Check logs and restart components
- **Prevention**: Monitor control plane health

### Issue 2: Cross-Cluster Communication Failures
- **Solution**: Verify network policies and DNS
- **Prevention**: Regular connectivity tests

### Issue 3: Resource Synchronization Problems
- **Solution**: Check placement policies and overrides
- **Prevention**: Monitor resource status

## Best Practices

### 1. Federation Setup
- Use dedicated host cluster
- Implement proper RBAC
- Monitor control plane
- Regular backups
- Document configuration

### 2. Resource Management
- Use placement policies
- Implement overrides
- Monitor distribution
- Regular audits
- Document policies

### 3. Cross-Cluster Communication
- Configure proper networking
- Implement DNS strategy
- Monitor connectivity
- Regular testing
- Document setup

## Next Steps
- Configure monitoring
- Implement backup
- Set up disaster recovery
- Regular reviews
