# Dapr Sidecar Configuration Guide

## Objective
This guide will help you configure the Dapr sidecar for your Azure Container Apps deployment, enabling service-to-service communication and state management capabilities.

## Prerequisites
- Azure Container Apps environment created (see [Azure-Container-Apps-Provisioning.md](Azure-Container-Apps-Provisioning.md))
- Basic understanding of Dapr concepts
- Access to Azure CLI

## Step-by-Step Instructions

### 1. Enable Dapr on Container App
```bash
az containerapp update \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --enable-dapr \
  --dapr-app-id daca-prototype-app \
  --dapr-app-port 80 \
  --dapr-app-protocol http
```

### 2. Configure Dapr Components

#### 2.1 Create State Store Component
```bash
az containerapp env dapr-component set \
  --name daca-prototype-env \
  --resource-group daca-prototype-rg \
  --dapr-component-name statestore \
  --yaml '
    componentType: state.azure.blobstorage
    version: v1
    metadata:
    - name: accountName
      value: "yourstorageaccount"
    - name: accountKey
      secretRef: storage-account-key
    - name: containerName
      value: "statestore"
    secrets:
    - name: storage-account-key
      value: "your-storage-account-key"
  '
```

#### 2.2 Create Pub/Sub Component
```bash
az containerapp env dapr-component set \
  --name daca-prototype-env \
  --resource-group daca-prototype-rg \
  --dapr-component-name pubsub \
  --yaml '
    componentType: pubsub.azure.servicebus
    version: v1
    metadata:
    - name: connectionString
      secretRef: servicebus-connection-string
    secrets:
    - name: servicebus-connection-string
      value: "your-servicebus-connection-string"
  '
```

### 3. Configure Dapr Application Settings

#### 3.1 Set Dapr Configuration
```bash
az containerapp update \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --set-env-vars \
    "DAPR_HTTP_PORT=3500" \
    "DAPR_GRPC_PORT=50001"
```

### 4. Implement Dapr Client in Your Application

#### 4.1 Python Example
```python
from dapr.clients import DaprClient

with DaprClient() as d:
    # Save state
    d.save_state(
        store_name="statestore",
        key="mykey",
        value="myvalue"
    )
    
    # Publish message
    d.publish_event(
        pubsub_name="pubsub",
        topic_name="mytopic",
        data="mymessage"
    )
```

## Validation

### 1. Verify Dapr Sidecar Status
```bash
az containerapp show \
  --name daca-prototype-app \
  --resource-group daca-prototype-rg \
  --query "properties.template.containers[?name=='daprd']"
```

### 2. Test Dapr Functionality
```bash
# Test state store
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key": "test", "value": "value"}]'

# Test pub/sub
curl -X POST http://localhost:3500/v1.0/publish/pubsub/mytopic \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Common Issues and Solutions

### Issue 1: Dapr Sidecar Not Starting
- **Solution**: Check container logs and verify Dapr configuration
- **Prevention**: Ensure all required environment variables are set

### Issue 2: State Store Connection Issues
- **Solution**: Verify storage account credentials and permissions
- **Prevention**: Use managed identities where possible

### Issue 3: Pub/Sub Message Delivery Problems
- **Solution**: Check Service Bus connection string and topic configuration
- **Prevention**: Implement proper error handling and retry logic

## Best Practices

1. **Security**
   - Use managed identities instead of connection strings
   - Implement proper secret management
   - Enable TLS for Dapr communication

2. **Performance**
   - Configure appropriate resource limits for Dapr sidecar
   - Implement connection pooling
   - Use bulk operations for state management

3. **Reliability**
   - Implement retry policies
   - Use circuit breakers for external calls
   - Monitor Dapr metrics

## Next Steps
- Implement secrets management (see [Secrets-Management-Azure-KeyVault.md](Secrets-Management-Azure-KeyVault.md))
- Set up monitoring and observability
- Configure CI/CD pipeline (see [GitHub-Actions-Build-and-Deploy.md](../3-CI-CD-Pipeline/GitHub-Actions-Build-and-Deploy.md)) 