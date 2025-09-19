# Global Load Balancing and Traffic Management

## Objective
This guide provides detailed instructions for implementing global load balancing and traffic management across multiple regions using Azure Traffic Manager and Kubernetes Ingress controllers.

## Prerequisites
- Multiple Kubernetes clusters in different regions
- Azure subscription with Traffic Manager access
- kubectl configured for all clusters
- Helm installed
- Basic understanding of networking concepts
- Access to create and modify load balancing resources

## Step-by-Step Instructions

### 1. Configure Azure Traffic Manager

#### 1.1 Create Traffic Manager Profile
```bash
# Create resource group
az group create --name global-lb-rg --location eastus

# Create Traffic Manager profile
az network traffic-manager profile create \
  --name global-ai-app \
  --resource-group global-lb-rg \
  --routing-method Performance \
  --unique-dns-name global-ai-app
```

#### 1.2 Configure Endpoints
```bash
# Add East US endpoint
az network traffic-manager endpoint create \
  --name eastus-endpoint \
  --profile-name global-ai-app \
  --resource-group global-lb-rg \
  --type externalEndpoints \
  --target eastus-cluster.eastus.cloudapp.azure.com \
  --endpoint-status enabled \
  --weight 100

# Add West Europe endpoint
az network traffic-manager endpoint create \
  --name westeurope-endpoint \
  --profile-name global-ai-app \
  --resource-group global-lb-rg \
  --type externalEndpoints \
  --target westeurope-cluster.westeurope.cloudapp.azure.com \
  --endpoint-status enabled \
  --weight 100

# Add Southeast Asia endpoint
az network traffic-manager endpoint create \
  --name southeastasia-endpoint \
  --profile-name global-ai-app \
  --resource-group global-lb-rg \
  --type externalEndpoints \
  --target southeastasia-cluster.southeastasia.cloudapp.azure.com \
  --endpoint-status enabled \
  --weight 100
```

### 2. Configure Regional Load Balancers

#### 2.1 Install NGINX Ingress Controller
```bash
# Add Helm repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.nodeSelector."kubernetes\.io/os"=linux \
  --set defaultBackend.nodeSelector."kubernetes\.io/os"=linux
```

#### 2.2 Configure Ingress Resources
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-agent-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  tls:
  - hosts:
    - ai-agent.example.com
    secretName: tls-secret
  rules:
  - host: ai-agent.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-agent
            port:
              number: 80
```

### 3. Configure Health Checks

#### 3.1 Set Up Traffic Manager Health Probes
```bash
# Configure health probe
az network traffic-manager profile update \
  --name global-ai-app \
  --resource-group global-lb-rg \
  --protocol HTTPS \
  --port 443 \
  --path /health \
  --interval 30 \
  --timeout 10 \
  --tolerated-number-of-failures 3
```

#### 3.2 Configure Ingress Health Checks
```yaml
# ingress-health.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: health-check-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/health-check: "true"
    nginx.ingress.kubernetes.io/health-check-path: "/health"
    nginx.ingress.kubernetes.io/health-check-interval: "30s"
    nginx.ingress.kubernetes.io/health-check-timeout: "10s"
    nginx.ingress.kubernetes.io/health-check-failures: "3"
spec:
  rules:
  - host: health-check.example.com
    http:
      paths:
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: health-check
            port:
              number: 8080
```

### 4. Configure Traffic Routing

#### 4.1 Set Up Traffic Manager Routing Methods
```bash
# Configure performance routing
az network traffic-manager profile update \
  --name global-ai-app \
  --resource-group global-lb-rg \
  --routing-method Performance

# Configure weighted routing
az network traffic-manager profile update \
  --name global-ai-app \
  --resource-group global-lb-rg \
  --routing-method Weighted
```

#### 4.2 Configure Ingress Traffic Rules
```yaml
# ingress-rules.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-agent-rules
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      if ($http_x_forwarded_proto = 'http') {
        return 301 https://$host$request_uri;
      }
spec:
  rules:
  - host: ai-agent.example.com
    http:
      paths:
      - path: /api(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /web(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

## Validation

### 1. Verify Traffic Manager Configuration
```bash
# Check Traffic Manager profile
az network traffic-manager profile show \
  --name global-ai-app \
  --resource-group global-lb-rg

# Check endpoint status
az network traffic-manager endpoint list \
  --profile-name global-ai-app \
  --resource-group global-lb-rg
```

### 2. Test Load Balancing
```bash
# Test global endpoint
curl -I https://global-ai-app.trafficmanager.net

# Test regional endpoints
curl -I https://eastus-cluster.eastus.cloudapp.azure.com
curl -I https://westeurope-cluster.westeurope.cloudapp.azure.com
curl -I https://southeastasia-cluster.southeastasia.cloudapp.azure.com
```

### 3. Monitor Traffic Distribution
```bash
# Check Traffic Manager metrics
az monitor metrics list \
  --resource /subscriptions/{subscription-id}/resourceGroups/global-lb-rg/providers/Microsoft.Network/trafficManagerProfiles/global-ai-app \
  --metric "QpsByEndpoint"

# Check Ingress metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/ingress-nginx/pods
```

## Common Issues and Solutions

### Issue 1: Traffic Manager Failover Issues
- **Solution**: Check health probe configuration
- **Prevention**: Monitor endpoint health

### Issue 2: Ingress Controller Problems
- **Solution**: Verify Ingress configuration
- **Prevention**: Monitor Ingress controller logs

### Issue 3: SSL/TLS Issues
- **Solution**: Check certificate configuration
- **Prevention**: Regular certificate renewal

## Best Practices

### 1. Traffic Manager
- Use appropriate routing method
- Configure health probes
- Monitor endpoint health
- Regular testing
- Document configuration

### 2. Ingress Controllers
- Use multiple replicas
- Configure SSL/TLS
- Monitor performance
- Regular updates
- Document setup

### 3. Health Checks
- Set appropriate intervals
- Configure timeouts
- Monitor health status
- Regular testing
- Document procedures

## Next Steps
- Configure monitoring
- Implement backup
- Set up disaster recovery
- Regular reviews 