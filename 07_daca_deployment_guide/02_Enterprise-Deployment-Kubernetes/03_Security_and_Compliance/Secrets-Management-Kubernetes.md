# Secrets Management in Kubernetes

## Objective
This guide provides detailed instructions for securely managing secrets in Kubernetes using various tools and best practices, ensuring proper encryption and access control.

## Prerequisites
- Kubernetes cluster with admin access
- kubectl configured
- Access to create and modify secrets
- Basic understanding of Kubernetes security concepts

## Step-by-Step Instructions

### 1. Basic Secrets Management

#### 1.1 Create Opaque Secrets
```bash
# Create secret from literal
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=secret \
  -n production

# Create secret from file
kubectl create secret generic tls-cert \
  --from-file=tls.crt=./cert.pem \
  --from-file=tls.key=./key.pem \
  -n production
```

#### 1.2 Create Docker Registry Secret
```bash
# Create registry secret
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=admin \
  --docker-password=secret \
  --docker-email=admin@example.com \
  -n production
```

### 2. External Secrets Management

#### 2.1 Install External Secrets Operator
```bash
# Add Helm repository
helm repo add external-secrets https://charts.external-secrets.io

# Install operator
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets \
  --create-namespace \
  --set installCRDs=true
```

#### 2.2 Configure AWS Secrets Manager
```yaml
# aws-secret-store.yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secret-store
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        secretRef:
          accessKeyID:
            name: aws-secret
            key: access-key
          secretAccessKey:
            name: aws-secret
            key: secret-key
```

#### 2.3 Create External Secret
```yaml
# external-secret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secret-store
    kind: SecretStore
  target:
    name: db-credentials
  data:
  - secretKey: username
    remoteRef:
      key: /production/db/username
  - secretKey: password
    remoteRef:
      key: /production/db/password
```

### 3. Secrets Encryption

#### 3.1 Configure Encryption at Rest
```bash
# Create encryption config
cat > encryption-config.yaml <<EOF
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: $(head -c 32 /dev/urandom | base64)
    - identity: {}
EOF

# Apply encryption config
kubectl create secret generic encryption-config \
  --from-file=encryption-config.yaml \
  -n kube-system
```

#### 3.2 Enable Encryption
```bash
# Update API server configuration
kubectl edit deployment kube-apiserver -n kube-system
# Add --encryption-provider-config=/etc/kubernetes/encryption-config.yaml
```

### 4. Secrets Rotation

#### 4.1 Create Rotation Script
```bash
# rotate-secrets.sh
#!/bin/bash
NAMESPACE=$1
SECRET_NAME=$2

# Generate new secret
NEW_PASSWORD=$(openssl rand -base64 32)

# Update secret
kubectl create secret generic $SECRET_NAME \
  --from-literal=password=$NEW_PASSWORD \
  -n $NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods using the secret
kubectl rollout restart deployment -n $NAMESPACE
```

#### 4.2 Schedule Rotation
```bash
# Create CronJob for rotation
kubectl create cronjob secret-rotation \
  --image=bitnami/kubectl \
  --schedule="0 0 * * *" \
  -- /bin/sh -c "kubectl create secret generic db-credentials --from-literal=password=\$(openssl rand -base64 32) -n production --dry-run=client -o yaml | kubectl apply -f -"
```

## Validation

### 1. Verify Secrets
```bash
# Check secrets
kubectl get secrets -n production

# Verify secret content
kubectl get secret db-credentials -n production -o jsonpath='{.data.password}' | base64 -d
```

### 2. Test External Secrets
```bash
# Check external secrets
kubectl get externalsecrets -n production

# Verify secret sync
kubectl get secret db-credentials -n production -o yaml
```

### 3. Verify Encryption
```bash
# Check etcd content
kubectl exec -it etcd-master -n kube-system -- etcdctl get /registry/secrets/production/db-credentials
```

## Common Issues and Solutions

### Issue 1: Secret Access Denied
- **Solution**: Check RBAC permissions
- **Prevention**: Regular access reviews

### Issue 2: Secret Sync Failures
- **Solution**: Verify external secret configuration
- **Prevention**: Monitor sync status

### Issue 3: Encryption Issues
- **Solution**: Check encryption configuration
- **Prevention**: Regular encryption audits

## Best Practices

### 1. Secret Management
- Use external secret providers
- Regular rotation
- Access control
- Audit logging
- Encryption at rest

### 2. Security
- Least privilege access
- Secret encryption
- Regular audits
- Monitoring
- Backup strategy

### 3. Operations
- Automated rotation
- Version control
- Documentation
- Testing
- Recovery procedures

## Next Steps
- Implement secret backup
- Set up monitoring
- Configure alerting
- Regular security audits
