# Secrets Management with Azure Key Vault

## Objective
This guide will help you implement secure secrets management using Azure Key Vault for your Azure Container Apps deployment, ensuring sensitive information is properly protected.

## Prerequisites
- Azure Container Apps environment created (see [Azure-Container-Apps-Provisioning.md](Azure-Container-Apps-Provisioning.md))
- Azure Key Vault created
- Azure CLI installed and configured
- Basic understanding of Azure security concepts

## Step-by-Step Instructions

### 1. Create Azure Key Vault
```bash
# Create Key Vault
az keyvault create \
  --name daca-prototype-kv \
  --resource-group daca-prototype-rg \
  --location eastus \
  --enable-rbac-authorization true
```

### 2. Configure Access Policies

#### 2.1 Get Managed Identity
```bash
# Get the managed identity of your container app
MANAGED_IDENTITY=$(az containerapp show \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --query "identity.principalId" \
  --output tsv)
```

#### 2.2 Assign Key Vault Access
```bash
# Assign Key Vault Secrets User role
az role assignment create \
  --assignee $MANAGED_IDENTITY \
  --role "Key Vault Secrets User" \
  --scope "/subscriptions/{subscription-id}/resourceGroups/daca-prototype-rg/providers/Microsoft.KeyVault/vaults/daca-prototype-kv"
```

### 3. Store Secrets in Key Vault

#### 3.1 Store Application Secrets
```bash
# Store API key
az keyvault secret set \
  --vault-name daca-prototype-kv \
  --name "api-key" \
  --value "your-api-key"

# Store database connection strings
az keyvault secret set \
  --vault-name daca-prototype-kv \
  --name "postgres-url" \
  --value "postgresql://user:password@postgres-service:5432/dbname"

az keyvault secret set \
  --vault-name daca-prototype-kv \
  --name "redis-url" \
  --value "redis://redis-service:6379"

# Store Google Gemini API key
az keyvault secret set \
  --vault-name daca-prototype-kv \
  --name "gemini-api-key" \
  --value "your-gemini-api-key"

# Store CloudAMQP connection string
az keyvault secret set \
  --vault-name daca-prototype-kv \
  --name "rabbitmq-url" \
  --value "amqps://user:password@your-instance.cloudamqp.com/vhost"
```

### 4. Configure Container App to Use Key Vault

#### 4.1 Update Container App with Key Vault Reference
```bash
az containerapp update \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --set-env-vars \
    "API_KEY=@Microsoft.KeyVault(SecretUri=https://daca-prototype-kv.vault.azure.net/secrets/api-key)" \
    "DB_CONNECTION_STRING=@Microsoft.KeyVault(SecretUri=https://daca-prototype-kv.vault.azure.net/secrets/db-connection-string)" \
    "GEMINI_API_KEY=@Microsoft.KeyVault(SecretUri=https://daca-prototype-kv.vault.azure.net/secrets/gemini-api-key)" \
    "RABBITMQ_URL=@Microsoft.KeyVault(SecretUri=https://daca-prototype-kv.vault.azure.net/secrets/rabbitmq-url)"
```

### 5. Implement Secret Access in Your Application

#### 5.1 Python Example
```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Initialize the credential
credential = DefaultAzureCredential()

# Create a secret client
vault_url = "https://daca-prototype-kv.vault.azure.net"
secret_client = SecretClient(vault_url=vault_url, credential=credential)

# Retrieve secrets
api_key = secret_client.get_secret("api-key").value
db_connection_string = secret_client.get_secret("db-connection-string").value
gemini_api_key = secret_client.get_secret("gemini-api-key").value
rabbitmq_url = secret_client.get_secret("rabbitmq-url").value
```

## Validation

### 1. Verify Key Vault Access
```bash
# Test secret retrieval
az keyvault secret show \
  --vault-name daca-prototype-kv \
  --name api-key
```

### 2. Check Container App Environment Variables
```bash
az containerapp show \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --query "properties.template.containers[0].env"
```

### 3. Test Application Secret Access
```bash
# Check application logs for secret access errors
az containerapp logs show \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg
```

## Common Issues and Solutions

### Issue 1: Access Denied to Key Vault
- **Solution**: Verify RBAC assignments and managed identity configuration
- **Prevention**: Use proper role assignments and test access before deployment

### Issue 2: Secret Not Found
- **Solution**: Check secret names and Key Vault references
- **Prevention**: Validate secret names and references during deployment

### Issue 3: Managed Identity Issues
- **Solution**: Verify managed identity configuration and permissions
- **Prevention**: Test managed identity access before deployment

## Best Practices

1. **Security**
   - Use managed identities instead of service principals
   - Implement proper RBAC assignments
   - Enable soft delete and purge protection
   - Rotate secrets regularly

2. **Organization**
   - Use consistent naming conventions
   - Group related secrets
   - Document secret purposes
   - Implement versioning

3. **Access Control**
   - Follow principle of least privilege
   - Use separate Key Vaults for different environments
   - Implement proper audit logging
   - Monitor access patterns

## Next Steps
- Implement Dapr sidecar configuration (see Dapr-Sidecar-Configuration.md)
- Set up monitoring and alerting
- Configure CI/CD pipeline (see GitHub-Actions-Build-and-Deploy.md) 