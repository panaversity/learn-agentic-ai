# TLS Certificates using Cert-Manager

## Objective
This guide provides detailed instructions for managing TLS certificates in Kubernetes using Cert-Manager, including installation, configuration, and best practices for certificate management.

## Prerequisites
- Kubernetes cluster with admin access
- kubectl configured
- Helm installed
- Domain name and DNS access
- Basic understanding of TLS/SSL concepts

## Step-by-Step Instructions

### 1. Install Cert-Manager

#### 1.1 Add Helm Repository
```bash
# Add Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io
helm repo update
```

#### 1.2 Install Cert-Manager
```bash
# Create namespace
kubectl create namespace cert-manager

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.12.0 \
  --set installCRDs=true \
  --set prometheus.enabled=true \
  --set webhook.timeoutSeconds=30
```

### 2. Configure Cluster Issuers

#### 2.1 Create Let's Encrypt Issuer
```yaml
# letsencrypt-staging.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
```

#### 2.2 Create Production Issuer
```yaml
# letsencrypt-prod.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### 3. Request Certificates

#### 3.1 Create Certificate
```yaml
# certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com
  namespace: production
spec:
  secretName: example-com-tls
  duration: 2160h # 90d
  renewBefore: 360h # 15d
  subject:
    organizations:
    - Example Inc
  commonName: example.com
  dnsNames:
  - example.com
  - www.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
```

#### 3.2 Configure Ingress with TLS
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - example.com
    - www.example.com
    secretName: example-com-tls
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### 4. Certificate Monitoring

#### 4.1 Create Certificate Monitoring
```yaml
# certificate-monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cert-manager
  namespace: cert-manager
spec:
  selector:
    matchLabels:
      app.kubernetes.io/instance: cert-manager
  endpoints:
  - port: http
    interval: 30s
```

#### 4.2 Set Up Alerts
```yaml
# certificate-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: cert-manager-alerts
  namespace: cert-manager
spec:
  groups:
  - name: cert-manager
    rules:
    - alert: CertificateExpiringSoon
      expr: certmanager_certificate_expiration_timestamp_seconds - time() < 86400 * 30
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: Certificate expiring soon
        description: Certificate {{ $labels.name }} in namespace {{ $labels.namespace }} is expiring in less than 30 days
```

## Validation

### 1. Verify Cert-Manager Installation
```bash
# Check cert-manager pods
kubectl get pods -n cert-manager

# Check cluster issuers
kubectl get clusterissuers

# Check certificates
kubectl get certificates --all-namespaces
```

### 2. Test Certificate Issuance
```bash
# Check certificate status
kubectl describe certificate example-com -n production

# Check certificate secret
kubectl get secret example-com-tls -n production -o yaml
```

### 3. Verify TLS Configuration
```bash
# Test HTTPS connection
curl -v https://example.com

# Check certificate details
openssl s_client -connect example.com:443 -servername example.com | openssl x509 -noout -text
```

## Common Issues and Solutions

### Issue 1: Certificate Not Issued
- **Solution**: Check issuer status and DNS configuration
- **Prevention**: Monitor certificate status

### Issue 2: Certificate Renewal Failed
- **Solution**: Check renewal logs and issuer configuration
- **Prevention**: Set up monitoring and alerts

### Issue 3: Ingress TLS Issues
- **Solution**: Verify ingress configuration and secret
- **Prevention**: Test TLS configuration regularly

## Best Practices

### 1. Certificate Management
- Use staging environment for testing
- Monitor certificate expiration
- Regular renewal checks
- Backup certificates
- Document procedures

### 2. Security
- Use strong key sizes
- Regular key rotation
- Secure private keys
- Access control
- Audit logging

### 3. Operations
- Automated renewal
- Monitoring and alerts
- Regular testing
- Documentation
- Recovery procedures

## Next Steps
- Set up wildcard certificates
- Implement certificate backup
- Configure monitoring and alerting
- Regular security audits
