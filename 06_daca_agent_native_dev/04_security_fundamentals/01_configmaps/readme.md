# Managing Configuration with ConfigMaps

ConfigMaps store non-sensitive configuration data (key-value pairs or files) in Kubernetes, decoupling application settings from code for runtime injection into pods via environment variables, startup command arguments, or volumes.

- **Why Decouple?**
  - **Reuse**: Use one app image (e.g., FastAPI) across dev, test, prod with different configurations, avoiding multiple image builds.
  - **Simpler Development/Testing**: Manage configs separately, reducing rebuilds for minor changes (e.g., endpoint updates).
  - **Less-Disruptive Changes**: Update settings without redeploying, minimizing downtime in distributed systems.
  - Avoids the anti-pattern of embedding configs in images, which complicates updates and scalability.
- **DACA Relevance**:
  - ConfigMaps manage agent settings (e.g., logging levels, `/chat` endpoint for group chat), enabling dynamic behavior.
  - Ensure consistent configurations across agent pods, supporting scalable DACA deployments.
  - Facilitate debugging (e.g., toggling `DEBUG` logging) in group chat systems for **05_agent_actors**.

You can use a ConfigMap in four different ways to configure a container inside a Pod:
- Inside a container command and args
- Environment variables for a container
- Add a file in read-only volume, for the application to read
- Write code to run inside the Pod that uses the Kubernetes API to read a ConfigMap

Behind the scenes, ConfigMaps are Kubernetes objects that hold a map of key-value pairs:
- Keys are an arbitrary name that can include alphanumerics, dashes, dots, and underscores
- Values can store anything, including full configuration files with multiple lines and carriage returns
- They’re limited to 1MiB (1,048,576 bytes) in size

**Do not use ConfigMaps to store sensitive data such as your GEMINI_API_KEY as Kubernetes makes no eﬀort to
protect their contents. For sensitive data, will use secrets management solution.**

Take the `00_lab_starter_code` step code as starter code. Run it

```bash
tilt up
```

## 1. ConfigMaps Hands On with Container Startup

Follow these steps to create and use a ConfigMap for the FastAPI app:

### Step 1: Create a ConfigMap
1. **Create a ConfigMap YAML file**:
   - In your project kubernetes directory, create a file named `configmap.yaml` with the following content:
     ```yaml
     apiVersion: v1
     kind: ConfigMap
     metadata:
       name: fastapi-config
       namespace: default
     data:
       log_level: DEBUG
       api_endpoint: /health
     ```
   - This ConfigMap defines two key-value pairs:
     - `log_level: DEBUG`: Sets the app’s logging level to `DEBUG`.
     - `api_endpoint: /health`: Specifies the health check endpoint.

2. **Apply the ConfigMap**:
   - Run the following command to create the ConfigMap in the Kubernetes cluster:
     ```bash
     kubectl apply -f configmap.yaml
     ```
   
   - Get all ConfigMaps
     ```bash
      kb get configmap 
      NAME               DATA   AGE
      fastapi-config     2      12s
      kube-root-ca.crt   1      149m
     ```
     OUTPUT:
     ```bash
      NAME               DATA   AGE
      fastapi-config     2      12s
      kube-root-ca.crt   1      149m
     ```
   
   - Verify the ConfigMap was created:
     ```bash
     kubectl get configmap fastapi-config -o yaml
     ```

     Output:

     ```bash
      apiVersion: v1
      data:
        api_endpoint: /health
        log_level: DEBUG
      kind: ConfigMap
      metadata:
        annotations:
          kubectl.kubernetes.io/last-applied-configuration: |
            {"apiVersion":"v1","data":{"api_endpoint":"/health","log_level":"DEBUG"},"kind":"ConfigMap","metadata":{"annotations":{},"name":"fastapi-config","namespace":"default"}}
        creationTimestamp: "2025-05-03T12:22:08Z"
        name: fastapi-config
        namespace: default
        resourceVersion: "6916"
        uid: 4688df7d-3252-4c48-8f77-bca5d96204ca
     ```

### Step 2: Update FastAPI Deployment
1. **Modify the Deployment YAML**:
   - Open `kubernetes/deployment.yaml` (from `00_starter_code` or **03_hot_reloading/**) and update the `spec` section to include environment variables from the ConfigMap. The relevant section should look like this:
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: daca-ai-app
      namespace: default  # Explicit for clarity or Omit and specify via kubectl -n default
    spec:
      replicas: 1 # Increase to 2-3 for production
      selector:
        matchLabels:
          app: daca-ai-app
      template:
        metadata:
          labels:
            app: daca-ai-app
          annotations: 
            dapr.io/enabled: "true"
            dapr.io/app-id: "daca-ai-app"
            dapr.io/app-port: "8000"
            dapr.io/log-level: "info"
        spec:
          containers:
          - name: app
            image: daca-ai-app
            imagePullPolicy: IfNotPresent
            ports:
              - containerPort: 8000
            env:
              - name: LOG_LEVEL
                valueFrom:
                  configMapKeyRef:
                    name: fastapi-config
                    key: log_level
              - name: API_ENDPOINT
                valueFrom:
                  configMapKeyRef:
                    name: fastapi-config
                    key: api_endpoint
     ```
   
   - The `env` section maps:
     - `LOG_LEVEL` to the `log_level` key in the ConfigMap.
     - `API_ENDPOINT` to the `api_endpoint` key in the ConfigMap.

2. **Update the FastAPI Application Code**:
   - Modify `main.py` to read the `LOG_LEVEL` and `API_ENDPOINT` environment variables and use them for logging and routing. Update the file to include:
     ```python
     import os
     import logging
     # Configure logging based on environment variable
     log_level = os.getenv("LOG_LEVEL", "INFO")
     logging.basicConfig(level=getattr(logging, log_level))
     logger = logging.getLogger(__name__)

     # Read API endpoint from environment variable
     health_endpoint = os.getenv("API_ENDPOINT", "/local/health")

     @app.get(health_endpoint)
     async def health_check():
         logger.debug("Health check endpoint called")
         logger.info(f"API_ENDPOINT {os.getenv("API_ENDPOINT")}")
         logger.info(f"LOG_LEVEL {os.getenv("LOG_LEVEL")}")
         return {"status": "healthy"}
     ```
   - This code:
     - Sets the logging level based on `LOG_LEVEL` (defaults to `INFO` if not set).
     - Configures the health check endpoint dynamically based on `API_ENDPOINT`.
     - Logs a `DEBUG` message when the health endpoint is called.

3. **Rebuild and Redeploy the Application**:
   - When using Tilt, save the changes to `main.py` and `kubernetes/deployment.yaml`, and Tilt will automatically rebuild and redeploy the app.

   Now open fastapi docs: http://localhost:8000/docs. Try the new health endpoint. If it have only /health path it means we get the value from ConfigMap.

   Call the /health endpoint and see the logs.

  ```bash
  daca-ai-app │ [app] DEBUG:main:Health check endpoint called
  daca-ai-app │ [app] INFO:main:API_ENDPOINT /health
  daca-ai-app │ [app] INFO:main:LOG_LEVEL DEBUG
  daca-ai-app │ [app] INFO:     127.0.0.1:41846 - "GET /health HTTP/1.1" 200 OK
  ```
  

## 2. ConfigMaps and Volumes Hands On

Now let's use ConfigMaps with volumes - they let you reference entire configuration and take updates. The process is as follows:

1. Create the ConfigMap like we did before.
2. Define a ConfigMap volume in the Pod template
3. Mount the ConfigMap volume into the container
4. ConfigMap entries will appear as files inside the container

We have already defined the ConfigMap. Now we will update deployment.yaml and in
- spec.volumes creates a volume called volmap based on our ConfigMap
- spec.containers.volumeMounts mounts the volmap volume to /etc/name in the container

1. Create a Standalone Pod

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: daca-ai-app
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: daca-ai-app
  template:
    metadata:
      labels:
        app: daca-ai-app
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "daca-ai-app"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: app
        image: daca-ai-app
        imagePullPolicy: IfNotPresent
        ports:
          - containerPort: 8000
        volumeMounts:
          - name: volmap
            mountPath: /etc/name
            readOnly: true
      volumes:
        - name: volmap
          configMap:
            name: fastapi-config
```

Now you can update the code in main.py

```python
# Read config values from mounted files
def read_config(path, default=""):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return default

log_level = read_config("/etc/name/log_level", "INFO")
api_endpoint = read_config("/etc/name/api_endpoint", "/local/health")
# Setup logging
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

@app.get(api_endpoint)
async def health_check():
    logger.debug("Health check endpoint called")
    logger.info(f"API_ENDPOINT {api_endpoint}")
    logger.info(f"LOG_LEVEL {log_level}")
    logger.debug(f"LIVE_VOLUME {read_config("/etc/name/live_volume", "not_working")}")
    return {"status": "healthy"}
```

Note: It takes 1-2 minutes to reflect the change. Here I have update tiltFile to refer our configmap as well. See last section of tiltFile.

## Reflection
- **How does using ConfigMaps improve the maintainability of DACA agents compared to hardcoding values?**
  - ConfigMaps allow configuration changes without modifying code or rebuilding images, enabling faster updates and reducing errors in distributed systems.
- **What other agent settings could be managed with ConfigMaps (e.g., retry policies, timeouts)?**
  - Examples include retry counts for API calls, timeouts for external services, feature flags, or environment-specific URLs, all of which enhance agent flexibility.

## DACA Context
ConfigMaps enable dynamic configuration of DACA agent behavior (e.g., logging levels, API endpoints) without rebuilding container images. This is crucial for scalable, maintainable agent deployments in Kubernetes, where agents may need to adapt to different environments or requirements without code changes.

## Next Steps
- Proceed to **Securing Sensitive Data with Secrets** to learn how to securely manage sensitive data, such as the Gemini API key, building on the configuration skills from this lab.

## Resources
- [Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dapr Integration with FastAPI](https://docs.dapr.io/developing-applications/sdks/python/)