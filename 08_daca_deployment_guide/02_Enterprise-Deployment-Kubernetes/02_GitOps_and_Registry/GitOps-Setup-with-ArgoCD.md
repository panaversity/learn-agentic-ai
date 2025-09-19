# GitOps Setup with ArgoCD

## Objective
This guide provides step-by-step instructions for setting up and configuring ArgoCD for GitOps-based deployments in your Kubernetes cluster, ensuring automated and declarative application management.

## Prerequisites
- Kubernetes cluster with admin access
- kubectl configured
- Helm installed
- Git repository for application manifests
- Basic understanding of GitOps principles

## Step-by-Step Instructions

### 1. Install ArgoCD

#### 1.1 Create Namespace
```bash
# Create argocd namespace
kubectl create namespace argocd
```

#### 1.2 Install ArgoCD
```bash
# Add ArgoCD Helm repository
helm repo add argo https://argoproj.github.io/argo-helm

# Install ArgoCD
helm install argocd argo/argo-cd \
  --namespace argocd \
  --set server.ingress.enabled=true \
  --set server.ingress.hosts[0]=argocd.your-domain.com \
  --set server.extraArgs[0]="--insecure" \
  --set controller.args.appResyncPeriod=30
```

### 2. Configure ArgoCD

#### 2.1 Get Initial Admin Password
```bash
# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

#### 2.2 Access ArgoCD UI
```bash
# Port-forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access UI at https://localhost:8080
# Login with admin and the password from step 2.1
```

### 3. Set Up Git Repository

#### 3.1 Create Application Manifests
```yaml
# apps/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
  - configmap.yaml
```

```yaml
# apps/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
patchesStrategicMerge:
  - deployment-patch.yaml
```

#### 3.2 Push to Git Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-org/your-repo.git
git push -u origin main
```

### 4. Create ArgoCD Application

#### 4.1 Create Application Manifest
```yaml
# argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: production-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/your-repo.git
    targetRevision: main
    path: apps/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

#### 4.2 Apply Application Manifest
```bash
# Apply application manifest
kubectl apply -f argocd-app.yaml
```

### 5. Configure RBAC

#### 5.1 Create Project
```yaml
# argocd-project.yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Production environment
  destinations:
  - namespace: production
    server: https://kubernetes.default.svc
  sourceRepos:
  - '*'
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
```

#### 5.2 Apply Project Configuration
```bash
# Apply project configuration
kubectl apply -f argocd-project.yaml
```

## Validation

### 1. Verify ArgoCD Installation
```bash
# Check ArgoCD pods
kubectl get pods -n argocd

# Check ArgoCD services
kubectl get svc -n argocd
```

### 2. Test GitOps Workflow
```bash
# Make a change to your application manifests
# Push changes to git repository
git add .
git commit -m "Update application configuration"
git push

# Watch ArgoCD sync the changes
kubectl get application production-app -n argocd -w
```

### 3. Check Application Health
```bash
# Check application status
argocd app get production-app

# Check application resources
argocd app resources production-app
```

## Common Issues and Solutions

### Issue 1: Sync Failures
- **Solution**: Check application logs and manifests
- **Prevention**: Validate manifests before pushing

### Issue 2: Access Issues
- **Solution**: Verify RBAC configuration
- **Prevention**: Regular access reviews

### Issue 3: Resource Conflicts
- **Solution**: Check resource definitions
- **Prevention**: Use namespaces properly

## Best Practices

### 1. Repository Structure
- Separate environments
- Clear directory structure
- Version control
- Documentation
- Review process

### 2. Deployment Strategy
- Automated sync
- Self-healing
- Prune resources
- Health checks
- Rollback capability

### 3. Security
- RBAC configuration
- Secret management
- Access control
- Audit logging
- Regular reviews

## Next Steps
- Set up monitoring and alerting
- Configure backup and recovery
- Implement security policies
