# Azure Container Apps Provisioning Guide

## Objective
This guide will help you provision and configure Azure Container Apps for your prototype deployment, providing a serverless environment for your AI application.

## Prerequisites
- Azure subscription with contributor access
- Azure CLI installed and configured
- Rancher installed locally - with dockerd for docker CLI
- Basic understanding of container concepts

## Step-by-Step Instructions

### 1. Install Required Tool

Install Azure CLI if not already installed

https://learn.microsoft.com/en-us/cli/azure/

For Windows:

- https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?pivots=winget

For Mac:

https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-macos

For Linux:

https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt


```powershell
# Install the Container Apps extension
az extension add --name containerapp --upgrade
```

### 2. Login to Azure

https://learn.microsoft.com/en-us/cli/azure/reference-index?view=azure-cli-latest#az-login

```powershell
az login
```

### 3. Create Resource Group

https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-cli

```powershell
az group create \
  --name daca-prototype-rg \
  --location eastus
```

### 4. Create Container Apps Environment
```powershell
az containerapp env create \
  --name daca-prototype-env \
  --resource-group daca-prototype-rg \
  --location eastus
```

### 5. Create Container App
```powershell
az containerapp create \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --environment daca-prototype-env \
  --image yourcontainerregistry.azurecr.io/your-image:latest \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 10
```

### 6. Configure Environment Variables
```powershell
az containerapp update \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --set-env-vars \
    "ENVIRONMENT=development" \
    "API_KEY=your-api-key"
```

### 7. Set Up Dapr Integration
```powershell
az containerapp update \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --enable-dapr \
  --dapr-app-id daca-prototype-app \
  --dapr-app-port 80
```

## Validation

### 1. Verify Container App Status
```powershell
az containerapp show \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg
```

### 2. Check Application Logs
```powershell
az containerapp logs show \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg
```

### 3. Test Application Endpoint
```powershell
# Get the application URL
az containerapp show \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv
```

## Common Issues and Solutions

### Issue 1: Container App Fails to Start
- **Solution**: Check container logs for errors
- **Prevention**: Ensure all environment variables are properly set

### Issue 2: Dapr Integration Issues
- **Solution**: Verify Dapr configuration and restart the container app
- **Prevention**: Double-check Dapr app ID and port settings

### Issue 3: Scaling Problems
- **Solution**: Review scaling rules and resource limits
- **Prevention**: Set appropriate min/max replicas based on expected load

## Next Steps
- Configure Dapr sidecar (see Dapr-Sidecar-Configuration.md)
- Set up secrets management (see Secrets-Management-Azure-KeyVault.md)
- Implement CI/CD pipeline (see GitHub-Actions-Build-and-Deploy.md) 