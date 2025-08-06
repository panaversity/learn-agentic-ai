# Container Registry Integration Guide

## Objective
This guide provides instructions for setting up and integrating Azure Container Registry (ACR) with your containerized applications, ensuring secure and efficient image management.

## Prerequisites
- Azure subscription
- Azure CLI installed
- Docker installed locally
- GitHub repository with GitHub Actions workflow

## Step-by-Step Instructions

### 1. Create Azure Container Registry

```bash
# Create resource group if not exists
az group create \
  --name daca-prototype-rg \
  --location eastus

# Create ACR
az acr create \
  --name dacaprototypeacr \
  --resource-group daca-prototype-rg \
  --sku Standard \
  --admin-enabled true
```

### 2. Configure ACR Authentication

#### 2.1 Enable Admin User
```bash
# Enable admin user
az acr update \
  --name dacaprototypeacr \
  --admin-enabled true

# Get admin credentials
az acr credential show \
  --name dacaprototypeacr \
  --resource-group daca-prototype-rg
```

#### 2.2 Create Service Principal (Optional)
```bash
# Create service principal
az ad sp create-for-rbac \
  --name daca-prototype-acr-sp \
  --scopes /subscriptions/{subscription-id}/resourceGroups/daca-prototype-rg/providers/Microsoft.ContainerRegistry/registries/dacaprototypeacr

# Assign AcrPush role
az role assignment create \
  --assignee {service-principal-id} \
  --scope /subscriptions/{subscription-id}/resourceGroups/daca-prototype-rg/providers/Microsoft.ContainerRegistry/registries/dacaprototypeacr \
  --role AcrPush
```

### 3. Configure GitHub Secrets

Add the following secrets to your GitHub repository:
- `REGISTRY_LOGIN_SERVER`: dacaprototypeacr.azurecr.io
- `REGISTRY_USERNAME`: dacaprototypeacr
- `REGISTRY_PASSWORD`: [admin password or service principal secret]

### 4. Update GitHub Actions Workflow

Add the following to your GitHub Actions workflow:

```yaml
- name: Login to Azure Container Registry
  uses: docker/login-action@v2
  with:
    registry: ${{ secrets.REGISTRY_LOGIN_SERVER }}
    username: ${{ secrets.REGISTRY_USERNAME }}
    password: ${{ secrets.REGISTRY_PASSWORD }}

- name: Build and push Docker image
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: ${{ secrets.REGISTRY_LOGIN_SERVER }}/${{ env.CONTAINER_APP_NAME }}:${{ github.sha }}
```

### 5. Configure Image Retention Policies

```bash
# Enable retention policy
az acr config retention update \
  --registry dacaprototypeacr \
  --status enabled \
  --type UntaggedManifests \
  --days 7

# Set cleanup policy
az acr config retention update \
  --registry dacaprototypeacr \
  --status enabled \
  --type UntaggedManifests \
  --days 7 \
  --cleanup-policy "delete"
```

## Validation

### 1. Test Registry Access
```bash
# Login to ACR
az acr login --name dacaprototypeacr

# List repositories
az acr repository list --name dacaprototypeacr
```

### 2. Verify Image Push
```bash
# Tag local image
docker tag your-image:latest dacaprototypeacr.azurecr.io/your-image:latest

# Push image
docker push dacaprototypeacr.azurecr.io/your-image:latest
```

### 3. Check Image Details
```bash
# List tags
az acr repository show-tags \
  --name dacaprototypeacr \
  --repository your-image

# Show manifest
az acr repository show \
  --name dacaprototypeacr \
  --repository your-image \
  --tag latest
```

## Common Issues and Solutions

### Issue 1: Authentication Failures
- **Solution**: Verify credentials and permissions
- **Prevention**: Use managed identities where possible

### Issue 2: Image Push Failures
- **Solution**: Check network connectivity and permissions
- **Prevention**: Test connectivity before deployment

### Issue 3: Storage Quota Issues
- **Solution**: Implement retention policies
- **Prevention**: Regular cleanup of unused images

## Best Practices

### 1. Security
- Enable admin user only when necessary
- Use managed identities
- Implement network rules
- Enable vulnerability scanning
- Use private endpoints

### 2. Performance
- Use appropriate SKU
- Implement geo-replication
- Use content trust
- Optimize image layers
- Implement caching

### 3. Cost Optimization
- Clean up unused images
- Use appropriate retention policies
- Monitor storage usage
- Use appropriate SKU
- Implement tagging strategy

### 4. Operations
- Implement proper tagging
- Use semantic versioning
- Document image contents
- Monitor registry health
- Implement backup strategy

## Next Steps
- Configure GitHub Actions workflow (see GitHub-Actions-Build-and-Deploy.md)
- Set up container app deployment
- Implement monitoring and alerting 