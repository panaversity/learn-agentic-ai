# GitHub Actions Build and Deploy Guide

## Objective
This guide provides a comprehensive setup for GitHub Actions CI/CD pipeline to build, test, and deploy containerized applications to Azure Container Apps.

## Prerequisites
- GitHub repository
- Azure subscription
- Azure Container Registry
- Azure Container Apps environment
- Docker installed locally (for testing)

## Step-by-Step Instructions

### 1. Configure GitHub Secrets

Add the following secrets to your GitHub repository:
- `AZURE_CREDENTIALS`: Azure service principal credentials
- `REGISTRY_LOGIN_SERVER`: Azure Container Registry login server
- `REGISTRY_USERNAME`: Azure Container Registry username
- `REGISTRY_PASSWORD`: Azure Container Registry password
- `RESOURCE_GROUP`: Azure resource group name
- `CONTAINER_APP_NAME`: Azure Container App name
- `CONTAINER_APP_ENVIRONMENT`: Azure Container Apps environment name

### 2. Create GitHub Actions Workflow

Create `.github/workflows/azure-container-apps.yml`:

```yaml
name: Build and Deploy to Azure Container Apps

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY_NAME: yourregistry
  CONTAINER_APP_NAME: your-app
  RESOURCE_GROUP: your-resource-group
  CONTAINER_APP_ENVIRONMENT: your-environment

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install UV
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH

    - name: Install dependencies
      run: |
        uv pip install --system
        uv pip install pytest

    - name: Run tests
      run: |
        pytest

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Login to Azure Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY_NAME }}.azurecr.io
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ env.REGISTRY_NAME }}.azurecr.io/${{ env.CONTAINER_APP_NAME }}:${{ github.sha }}

    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Deploy to Azure Container Apps
      uses: azure/container-apps-deploy-action@v1
      with:
        app-name: ${{ env.CONTAINER_APP_NAME }}
        resource-group: ${{ env.RESOURCE_GROUP }}
        container-app-environment: ${{ env.CONTAINER_APP_ENVIRONMENT }}
        image: ${{ env.REGISTRY_NAME }}.azurecr.io/${{ env.CONTAINER_APP_NAME }}:${{ github.sha }}
```

### 3. Configure Azure Service Principal

```bash
# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-sp" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth
```

### 4. Add Environment Variables

Create `.github/workflows/environments.yml`:

```yaml
name: Environments

on:
  push:
    branches: [ main ]

jobs:
  create-environments:
    runs-on: ubuntu-latest
    steps:
      - name: Create environments
        run: |
          echo "Creating environments..."
          echo "::set-output name=environments::development,staging,production"
```

## Validation

### 1. Test Workflow Locally
```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act -l
```

### 2. Monitor Deployments
```bash
# Check deployment status
az containerapp show \
  --name your-app \
  --resource-group your-resource-group \
  --query "properties.latestRevisionName"
```

### 3. Verify Application
```bash
# Get application URL
az containerapp show \
  --name your-app \
  --resource-group your-resource-group \
  --query "properties.configuration.ingress.fqdn" \
  --output tsv
```

## Common Issues and Solutions

### Issue 1: Authentication Failures
- **Solution**: Verify Azure credentials and permissions
- **Prevention**: Use least privilege principle for service principal

### Issue 2: Build Failures
- **Solution**: Check Dockerfile and build context
- **Prevention**: Test builds locally before pushing

### Issue 3: Deployment Issues
- **Solution**: Check container app configuration
- **Prevention**: Validate configuration before deployment

## Best Practices

### 1. Security
- Use environment-specific secrets
- Implement branch protection rules
- Regular security audits
- Use managed identities where possible

### 2. Performance
- Implement caching
- Use matrix builds for testing
- Optimize Docker builds
- Parallelize jobs where possible

### 3. Reliability
- Implement proper error handling
- Use retry mechanisms
- Monitor deployment health
- Implement rollback strategies

## Next Steps
- Set up container registry integration (see Container-Registry-Integration.md)
- Implement smoke testing (see Smoke-Testing-Checklist.md)
- Configure monitoring and alerting 