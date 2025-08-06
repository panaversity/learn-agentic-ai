# RBAC and Network Policies in Kubernetes

## Objective
This guide provides detailed instructions for implementing Role-Based Access Control (RBAC) and Network Policies in your Kubernetes cluster, ensuring proper security and access management.

## Prerequisites
- Kubernetes cluster with admin access
- kubectl configured
- Basic understanding of Kubernetes security concepts
- Access to create and modify RBAC resources

## Step-by-Step Instructions

### 1. Configure RBAC

#### 1.1 Create Namespaces
```bash
# Create namespaces for different environments
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production
```

#### 1.2 Create Service Accounts
```bash
# Create service accounts for applications
kubectl create serviceaccount app-sa -n development
kubectl create serviceaccount ci-sa -n staging
kubectl create serviceaccount ops-sa -n production
```

#### 1.3 Define Roles
```yaml
# development-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: development
  name: developer-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

```yaml
# production-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: operator-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
```

#### 1.4 Create RoleBindings
```yaml
# development-rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: development
subjects:
- kind: ServiceAccount
  name: app-sa
  namespace: development
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rbac.authorization.k8s.io
```

### 2. Implement Network Policies

#### 2.1 Create Namespace Isolation
```yaml
# namespace-isolation.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

#### 2.2 Allow Internal Communication
```yaml
# allow-internal.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-internal
  namespace: production
spec:
  podSelector: {}
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: production
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: production
```

#### 2.3 Configure External Access
```yaml
# allow-external.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
```

### 3. Apply Security Contexts

#### 3.1 Configure Pod Security
```yaml
# secure-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: production
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: secure-container
    image: nginx:latest
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

## Validation

### 1. Verify RBAC Configuration
```bash
# Check roles
kubectl get roles --all-namespaces

# Check role bindings
kubectl get rolebindings --all-namespaces

# Test access
kubectl auth can-i create pods --as=system:serviceaccount:development:app-sa
```

### 2. Test Network Policies
```bash
# Check network policies
kubectl get networkpolicies --all-namespaces

# Test connectivity
kubectl run test-pod --image=busybox -n production -- sleep 3600
kubectl exec -it test-pod -n production -- wget -qO- web-service
```

### 3. Verify Security Contexts
```bash
# Check pod security context
kubectl get pod secure-app -n production -o jsonpath='{.spec.securityContext}'

# Verify container security
kubectl get pod secure-app -n production -o jsonpath='{.spec.containers[0].securityContext}'
```

## Common Issues and Solutions

### Issue 1: Access Denied
- **Solution**: Verify role bindings and service accounts
- **Prevention**: Regular access reviews

### Issue 2: Network Connectivity Issues
- **Solution**: Check network policies and namespace labels
- **Prevention**: Document network requirements

### Issue 3: Security Context Violations
- **Solution**: Review security context settings
- **Prevention**: Use security policies

## Best Practices

### 1. RBAC Management
- Principle of least privilege
- Regular access reviews
- Clear role definitions
- Service account usage
- Audit logging

### 2. Network Security
- Default deny policies
- Namespace isolation
- Explicit allow rules
- Regular policy reviews
- Documentation

### 3. Security Contexts
- Non-root users
- Read-only root filesystem
- Dropped capabilities
- Resource limits
- Regular updates

## Next Steps
- Implement Pod Security Policies
- Set up audit logging
- Configure monitoring and alerting
- Regular security assessments
