# Global Service Mesh Configuration

## Objective
This guide provides detailed instructions for implementing a global service mesh using Istio to manage service-to-service communication across multiple regions.

## Prerequisites
- Multiple Kubernetes clusters in different regions
- kubectl configured for all clusters
- Helm installed
- Istio CLI installed
- Basic understanding of service mesh concepts
- Access to create and modify mesh resources

## Step-by-Step Instructions

### 1. Install Istio

#### 1.1 Install Istio CLI
```bash
# Download Istio CLI
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Verify installation
istioctl version
```

#### 1.2 Install Istio in Primary Cluster
```bash
# Create namespace
kubectl create namespace istio-system

# Install Istio with multi-cluster configuration
istioctl install \
  --set profile=demo \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=eastus-cluster \
  --set values.global.network=network1
```

#### 1.3 Install Istio in Secondary Clusters
```bash
# Install in West Europe cluster
istioctl install \
  --set profile=demo \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=westeurope-cluster \
  --set values.global.network=network1

# Install in Southeast Asia cluster
istioctl install \
  --set profile=demo \
  --set values.global.meshID=mesh1 \
  --set values.global.multiCluster.clusterName=southeastasia-cluster \
  --set values.global.network=network1
```

### 2. Configure Multi-Cluster Mesh

#### 2.1 Set Up Remote Cluster Secrets
```bash
# Create remote cluster secret for West Europe
istioctl x create-remote-secret \
  --name=westeurope-cluster \
  --context=westeurope-cluster > westeurope-secret.yaml

# Create remote cluster secret for Southeast Asia
istioctl x create-remote-secret \
  --name=southeastasia-cluster \
  --context=southeastasia-cluster > southeastasia-secret.yaml

# Apply secrets to primary cluster
kubectl apply -f westeurope-secret.yaml
kubectl apply -f southeastasia-secret.yaml
```

#### 2.2 Configure Service Discovery
```yaml
# service-discovery.yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: external-svc
  namespace: istio-system
spec:
  hosts:
  - ai-agent.global
  location: MESH_INTERNAL
  ports:
  - number: 80
    name: http
    protocol: HTTP
  resolution: DNS
  endpoints:
  - address: eastus-cluster.eastus.cloudapp.azure.com
    ports:
      http: 80
    locality: eastus
  - address: westeurope-cluster.westeurope.cloudapp.azure.com
    ports:
      http: 80
    locality: westeurope
  - address: southeastasia-cluster.southeastasia.cloudapp.azure.com
    ports:
      http: 80
    locality: southeastasia
```

### 3. Configure Traffic Management

#### 3.1 Set Up Virtual Services
```yaml
# virtual-service.yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: ai-agent
  namespace: production
spec:
  hosts:
  - ai-agent.global
  http:
  - route:
    - destination:
        host: ai-agent.global
        subset: v1
      weight: 80
    - destination:
        host: ai-agent.global
        subset: v2
      weight: 20
```

#### 3.2 Configure Destination Rules
```yaml
# destination-rule.yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: ai-agent
  namespace: production
spec:
  host: ai-agent.global
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
  trafficPolicy:
    loadBalancer:
      localityLbSetting:
        enabled: true
        distribute:
        - from: eastus/*
          to:
            "eastus/*": 80
            "westeurope/*": 10
            "southeastasia/*": 10
```

### 4. Configure Security

#### 4.1 Set Up mTLS
```yaml
# mtls-policy.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

#### 4.2 Configure Authorization Policies
```yaml
# authorization-policy.yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: ai-agent-policy
  namespace: production
spec:
  selector:
    matchLabels:
      app: ai-agent
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/ai-agent"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

## Validation

### 1. Verify Istio Installation
```bash
# Check Istio components
kubectl get pods -n istio-system

# Check mesh configuration
istioctl analyze
```

### 2. Test Service Communication
```bash
# Deploy test pod
kubectl apply -f test-pod.yaml

# Test service access
kubectl exec -it test-pod -- curl http://ai-agent.global/api/health
```

### 3. Monitor Mesh Status
```bash
# Check mesh status
istioctl proxy-status

# Check traffic distribution
kubectl get virtualservice ai-agent -n production -o yaml
```

## Common Issues and Solutions

### Issue 1: Service Discovery Problems
- **Solution**: Check ServiceEntry configuration
- **Prevention**: Monitor service discovery metrics

### Issue 2: Traffic Routing Issues
- **Solution**: Verify VirtualService and DestinationRule
- **Prevention**: Monitor traffic distribution

### Issue 3: Security Configuration Problems
- **Solution**: Check mTLS and authorization policies
- **Prevention**: Monitor security metrics

## Best Practices

### 1. Service Mesh Configuration
- Use appropriate mesh settings
- Configure proper discovery
- Monitor mesh health
- Regular updates
- Document setup

### 2. Traffic Management
- Implement proper routing
- Configure load balancing
- Monitor traffic
- Regular testing
- Document policies

### 3. Security
- Enable mTLS
- Configure authorization
- Monitor security
- Regular audits
- Document procedures

## Next Steps
- Configure monitoring
- Set up observability
- Implement backup
- Regular reviews 