# Steps to Deploy Azure Container App with GitHub Actions

### Prerequisites

1. **Azure Subscription:** Ensure you have an Azure account. If not, create one [here](https://azure.microsoft.com/free/).
2. **Azure CLI:** Install Azure CLI from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
3. **GitHub Repository:** Have a repository with your container app code.


#### 1. **Set Up Azure Environment**
- **Login to Azure:**
    ```sh
    az login
    ```

- **Create Resource Group:**
    ```sh
    az group create --name myresourcegroup --location eastus
    ```

- **Create Container App Environment:**
    ```sh
    az containerapp env create --name mycontainerappenv --resource-group myresourcegroup --location eastus
    ```
- **Create the Service Principal:**
    ```sh
    az ad sp create-for-rbac --name "myServicePrincipal" --role contributor --scopes /subscriptions/{subscription-id} --sdk-auth
    ```

    ```json
    {
    "clientId": "e7f8c3bd-fe7c-484d-bd022a-2892edf151e5",
    "clientSecret": "xas8Q~t4Kb4tlQ-eh222o~Esr_z2kAMkM6ybcsgGag_",
    "subscriptionId": "06ddb3b9-9f0ba-4e1b-9e0e-1190ba64ff07",
    "tenantId": "e5d64a62-32ec6e-4a87-84fa-d64cda031416",
    "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
    "resourceManagerEndpointUrl": "https://management.azure.com/",
    "activeDirectoryGraphResourceId": "https://graph.windows.net/",
    "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
    "galleryEndpointUrl": "https://gallery.azure.com/",
    "managementEndpointUrl": "https://management.core.windows.net/"
    }
    ```

#### 2. **Create Docker Image**

- **Build Docker Image:**
    ```sh
    docker build -t your-dockerhub-username/myapp:latest .
    ```

- **Push Docker Image to Docker Hub:**
    - **Login to Docker Hub:**
        ```sh
        docker login --username your-dockerhub-username
        ```

    - **Tag and Push Image:**
        ```sh
        docker tag myapp:latest your-dockerhub-username/myapp:latest
        docker push your-dockerhub-username/myapp:latest
        ```

#### 3. **Configure GitHub Secrets**

Go to your GitHub repository.
Navigate to `Settings` > `Secrets and variables` > `Actions`.
Add the following secrets:

- `DOCKER_HUB_USERNAME`: Your Docker Hub username.
- `DOCKER_HUB_ACCESS_TOKEN`: Your Docker Hub access token (You can create an access token from Docker Hub instead of using your password).
- `AZURE_CREDENTIALS`: Your Azure credentials in JSON format:

```sh
az ad sp create-for-rbac --name "myServicePrincipal" --role contributor --scopes /subscriptions/{subscription-id} --sdk-auth
```

```json
{
"clientId": "e7f8c3bd-fe7c-484d-bd022a-2892edf151e5",
"clientSecret": "xas8Q~t4Kb4tlQ-eh222o~Esr_z2kAMkM6ybcsgGag_",
"subscriptionId": "06ddb3b9-9f0ba-4e1b-9e0e-1190ba64ff07",
"tenantId": "e5d64a62-32ec6e-4a87-84fa-d64cda031416",
"activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
"resourceManagerEndpointUrl": "https://management.azure.com/",
"activeDirectoryGraphResourceId": "https://graph.windows.net/",
"sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
"galleryEndpointUrl": "https://gallery.azure.com/",
"managementEndpointUrl": "https://management.core.windows.net/"
}
```



#### 4. **Create GitHub Action Workflow**
- In your GitHub repository, create a `.github/workflows/deploy.yml` file with the following content:

    ```yaml
    name: Deploy to Azure Container Apps

    on:
      push:
        branches:
          - main

    jobs:
      build-and-deploy:
        runs-on: ubuntu-latest

        steps:
          - name: Checkout code
            uses: actions/checkout@v2

          - name: Set up Docker Buildx
            uses: docker/setup-buildx-action@v1

          - name: Log in to Azure Container Registry
            uses: azure/docker-login@v1
            with:
              login-server: myacrregistry.azurecr.io
              username: ${{ secrets.REGISTRY_USERNAME }}
              password: ${{ secrets.REGISTRY_PASSWORD }}

          - name: Build and push Docker image
            run: |
              docker build -t myacrregistry.azurecr.io/myapp:latest .
              docker push myacrregistry.azurecr.io/myapp:latest

          - name: Azure Login
            uses: azure/login@v1
            with:
              creds: ${{ secrets.AZURE_CREDENTIALS }}

          - name: Deploy to Azure Container Apps
            run: |
              az containerapp update \
                --name mycontainerapp \
                --resource-group myresourcegroup \
                --image myacrregistry.azurecr.io/myapp:latest \
                --env-vars 'APP_SETTING=my-setting'
    ```

    - Replace placeholders (e.g., `myacrregistry`, `myapp`, `myresourcegroup`, `mycontainerapp`) with your actual values, ensuring they are all in lowercase.
    - Ensure `AZURE_CREDENTIALS` is a JSON object containing `clientId`, `clientSecret`, `subscriptionId`, and `tenantId`.

#### 5. **Run GitHub Action**
- Push your code to the `main` branch, and the GitHub Actions workflow will trigger automatically, building and deploying your container app to Azure.

### Additional Tips
- **Testing Locally:** Before deploying, ensure your Docker container works as expected locally.
- **Monitoring:** Use Azure Portal to monitor your container app’s health and logs.

This setup ensures that the names are correctly formatted in lowercase, which should resolve the registry name error.