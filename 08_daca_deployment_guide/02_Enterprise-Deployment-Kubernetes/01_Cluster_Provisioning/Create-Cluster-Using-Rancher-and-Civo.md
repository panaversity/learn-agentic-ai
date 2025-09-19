# Creating Kubernetes Cluster with Rancher and Civo

## Objective
This guide provides step-by-step instructions for creating and managing a Kubernetes cluster using Rancher and Civo, ensuring a production-ready environment for your containerized applications.

## Prerequisites
- Civo account with API key
- Rancher installed and configured
- Basic understanding of Kubernetes concepts
- Access to kubectl and civo CLI

## Step-by-Step Instructions

### 1. Install and Configure Civo CLI

```bash
# Install Civo CLI
curl -sL https://civo.com/get | sh

# Configure Civo CLI with API key
civo apikey save <your-api-key> <name>
civo apikey current <name>
```

### 2. Create Civo Kubernetes Cluster

```bash
# Create a new cluster
civo kubernetes create my-cluster \
  --size g4s.kube.medium \
  --nodes 3 \
  --region NYC1 \
  --wait

# Get cluster credentials
civo kubernetes config my-cluster > kubeconfig.yaml
export KUBECONFIG=./kubeconfig.yaml
```

### 3. Install and Configure Rancher

#### 3.1 Install Rancher using Helm
```bash
# Add Rancher Helm repository
helm repo add rancher-stable https://releases.rancher.com/server-charts/stable

# Create namespace for Rancher
kubectl create namespace cattle-system

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml

# Install Rancher
helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.my-domain.com \
  --set bootstrapPassword=admin \
  --set ingress.tls.source=letsEncrypt
```

#### 3.2 Configure Rancher
```bash
# Get Rancher URL
kubectl get ingress -n cattle-system

# Access Rancher UI and complete setup
# Set admin password and configure authentication
```

### 4. Import Civo Cluster into Rancher

#### 4.1 Generate Import Command
```bash
# In Rancher UI:
# 1. Go to Cluster Management
# 2. Click "Import Existing"
# 3. Copy the import command
```

#### 4.2 Apply Import Manifest
```bash
# Apply the import manifest
kubectl apply -f rancher-import.yaml
```

### 5. Configure Cluster Settings

#### 5.1 Set Up Monitoring
```bash
# Enable monitoring in Rancher UI
# Configure Prometheus and Grafana
```

#### 5.2 Configure Logging
```bash
# Enable logging in Rancher UI
# Set up EFK stack
```

#### 5.3 Set Up Backup
```bash
# Install Velero
kubectl apply -f https://raw.githubusercontent.com/vmware-tanzu/velero/main/config/common/00-prereqs.yaml
kubectl apply -f https://raw.githubusercontent.com/vmware-tanzu/velero/main/config/common/10-deployment.yaml
```

## Validation

### 1. Verify Cluster Status
```bash
# Check cluster status
civo kubernetes show my-cluster

# Verify nodes
kubectl get nodes

# Check Rancher connection
kubectl get pods -n cattle-system
```

### 2. Test Cluster Functionality
```bash
# Deploy test application
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80

# Verify deployment
kubectl get pods,svc
```

### 3. Check Monitoring
```bash
# Access Grafana dashboard
# Verify metrics collection
```

## Common Issues and Solutions

### Issue 1: Cluster Creation Fails
- **Solution**: Check Civo API limits and quotas
- **Prevention**: Monitor resource usage

### Issue 2: Rancher Import Issues
- **Solution**: Verify network connectivity and DNS
- **Prevention**: Test connectivity before import

### Issue 3: Monitoring Setup Problems
- **Solution**: Check resource allocation
- **Prevention**: Allocate sufficient resources

## Best Practices

### 1. Cluster Management
- Regular updates
- Resource monitoring
- Backup strategy
- Security hardening
- Access control

### 2. Performance
- Right-size nodes
- Load balancing
- Resource quotas
- Autoscaling
- Monitoring

### 3. Security
- RBAC configuration
- Network policies
- Secret management
- Regular audits
- Compliance checks

## Next Steps
- Configure node pools (see Node-Pool-Configuration.md)
- Set up GitOps workflow
- Implement monitoring and logging
