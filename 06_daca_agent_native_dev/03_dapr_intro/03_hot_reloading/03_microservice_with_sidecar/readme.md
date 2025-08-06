# 3. Tilt with a Microservice with Sidecar Hands On

### What’s Happening?

In Step 1, we configured Tilt for hot-reloading with our FastAPI application. In Step 2, we set up Tilt to manage the Dapr infrastructure and verified it using the Dapr Dashboard. Now, we will combine these setups into a single `Tiltfile` that manages both the FastAPI application and the Dapr infrastructure, enabling a complete local development environment. 

The FastAPI application will be updated to interact with Dapr’s state store and pub/sub features, with Tilt providing hot-reloading and real-time feedback via its UI. This completes the DACA Stage 1 workflow by enabling rapid iteration in a production-like Kubernetes environment with Dapr integration.

### Prerequisites

- You have completed Step 1 (Tilt setup for FastAPI with hot-reloading).
- You have completed Step 2 (Tilt setup with Dapr and Dashboard verification).
- Your Kubernetes cluster (Rancher Desktop) is running.
- The Dapr component YAML files (`redis-state.yaml`, `redis-pubsub.yaml`, `subscriptions.yaml`) are in the `./components/` directory.
- The FastAPI project files (`main.py`, `Dockerfile`, `kubernetes/deployment.yaml`, `kubernetes/service.yaml`) are set up (from Document 02 and Step 1).
- Ensure you are in the root directory of your `hello_dapr_fastapi` project.

### 1. Initial Setup

1. Copy the FastAPI Project from step 01_tilt_fastapi and the components directory from 02_tilt_dapr. This is our starter code.
2. In kubernetes/deployment.yaml change spec replicas: to 1.
3. In rancher desktop open Preferences > Virtual Machine and in Hardware change memory to be at least 3.

### 2. Update FastAPI Application to Use Dapr

Modify `main.py` to interact with Dapr’s state store and pub/sub features using the Dapr Python SDK. This assumes your FastAPI app has basic endpoints (from Document 02).

Update `main.py` with the following content:

```python
from fastapi import FastAPI, HTTPException
import httpx
import os

app = FastAPI(title="Dapr FastAPI Hello World")

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
STATE_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore"
PUBSUB_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/pubsub/message-updated"

@app.get("/")
async def root():
    return {"message": "Hello from AGI!"}

@app.post("/messages")
async def save_message(user_id: str, message: str):
    async with httpx.AsyncClient() as client:
        try:
            state_payload = [{"key": user_id, "value": {"user_id": user_id, "message": message}}]
            response = await client.post(STATE_URL, json=state_payload)
            response.raise_for_status()
            event_payload = {"user_id": user_id, "message": message}
            response = await client.post(PUBSUB_URL, json=event_payload)
            response.raise_for_status()
            return {"status": f"Stored and published message for {user_id}"}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages/{user_id}")
async def get_message(user_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{STATE_URL}/{user_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=404, detail="Message not found")

@app.post("/subscribe")
async def subscribe_message(data: dict):
    event_data = data.get("data", {})
    user_id = event_data.get("user_id", "unknown")
    message = event_data.get("message", "no message")
    print(f"Received event: User {user_id} updated message to '{message}'")
    return {"status": "Event processed"}
```

### 3. Create a Combined Tiltfile

Replace the `Tiltfile` in the project root with a combined version that manages both the Dapr infrastructure and the FastAPI application. This merges the configurations from Steps 1 and 2.

Add the following content to `Tiltfile`:

```python
# Tiltfile for FastAPI and Dapr Development

# Load extensions for Helm and nerdctl
load('ext://helm_remote', 'helm_remote')
load('ext://nerdctl', 'nerdctl_build')

# Increase apply timeout for Helm deployments
update_settings(k8s_upsert_timeout_secs=300)

# 1. Define and apply the dapr-system namespace
print("Defining dapr-system namespace YAML")
k8s_yaml(local('kubectl create namespace dapr-system --dry-run=client -o yaml'))

# 2. Install Dapr runtime via Helm
print("Deploying Dapr Core Helm chart")
helm_remote(
    chart='dapr',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    version='1.15',
    release_name='dapr',
    namespace='dapr-system',
    set=['global.mtls.enabled=false'],
)

# 3. Install Dapr Dashboard via Helm
print("Deploying Dapr Dashboard Helm chart")
helm_remote(
    chart='dapr-dashboard',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    release_name='dapr-dashboard',
    namespace='dapr-system'
)

# 4. Configure Dapr Dashboard port-forwarding
print("Configuring Dapr Dashboard port-forward")
k8s_resource(
    'dapr-dashboard',
    port_forwards=[port_forward(local_port=8080, container_port=8080, name='dapr-dashboard-ui')],
    labels=['dapr-ui']
)

# 5. Deploy Redis via Helm into the default namespace
print("Deploying Redis Helm chart")
helm_remote(
    chart='redis',
    repo_url='https://charts.bitnami.com/bitnami',
    repo_name='bitnami',
    release_name='redis',
    namespace='default',
    set=['auth.enabled=false']
)

# 6. Apply Dapr components (State Store, PubSub, Subscription)
k8s_yaml(['./components/redis-state.yaml', './components/redis-pubsub.yaml', './components/subscriptions.yaml'])

# 7. Build the FastAPI image using nerdctl
nerdctl_build(
    ref='dapr-fastapi-hello',
    context='.',
    dockerfile='Dockerfile',
    live_update=[
        sync('.', '/code'),
        # Optional: Restart Uvicorn if needed
        # run('pkill -f uvicorn', trigger=['./main.py'])
    ]
)

# 8. Deploy FastAPI Kubernetes manifests
k8s_yaml(['kubernetes/deployment.yaml', 'kubernetes/service.yaml'])

# 9. Define the FastAPI resource for Tilt
k8s_resource(
    'dapr-fastapi-hello',
    port_forwards='8000:8000',
    extra_pod_selectors={'app': 'dapr-fastapi-hello'}
)
```

### 4. Run Tilt with Combined Setup

Start Tilt from the project root directory:

```bash
tilt up
```

Tilt will:
1. Start its UI at `http://localhost:10350`.
2. Deploy the Dapr infrastructure (Control Plane, Dashboard, Redis, components).
3. Build and deploy the FastAPI application with the Dapr sidecar.
4. Enable hot-reloading for `main.py` changes.
5. Set up port-forwarding for the FastAPI app (`localhost:8000`) and Dapr Dashboard (`localhost:8080`).

Open the Tilt UI (`http://localhost:10350`) and verify that all resources are healthy (green):
- `dapr` (Dapr Control Plane)
- `dapr-dashboard` (Dapr Dashboard)
- `redis` (Redis instance)
- `dapr-fastapi-hello` (FastAPI application with Dapr sidecar)

### 5. Verify Dapr Dashboard with FastAPI

Access the Dapr Dashboard at `http://localhost:8080`. You should see:
- The Dapr runtime status.
- The Redis state store and pub/sub components.
- The `fastapi-hello` application (from the `dapr.io/app-id` annotation) listed under "Applications."

### 6. Test FastAPI and Dapr Integration

Test the FastAPI application’s Dapr integration using `curl` or a tool like Postman:

1. **Health check:**
   ```bash
   curl http://localhost:8000/
   ```
   Expected response: `{"message": "Hello from FastAPI with Dapr!"}`

2. **Save state:**
   ```bash
   curl -X POST http://localhost:8000/save-state -H "Content-Type: application/json" -d '{"key": "test-key", "value": "test-value"}'
   ```
   Expected response: `{"message": "Saved state with key: test-key"}`

3. **Retrieve state:**
   ```bash
   curl http://localhost:8000/get-state/test-key
   ```
   Expected response: `{"key": "test-key", "value": "{\"data\": \"test-value\"}"}`

4. **Publish message:**
   ```bash
   curl -X POST http://localhost:8000/publish -H "Content-Type: application/json" -d '{"topic": "test-topic", "message": "Hello Dapr!"}'
   ```
   Expected response: `{"message": "Published to topic: test-topic"}`

### 7. Verify Hot Reloading

Make a change to `main.py` (e.g., update the health check message to `"Hello from FastAPI with Dapr v2!"`). Save the file, and Tilt will:
1. Sync the changed file to the `/code` directory in the FastAPI pod.
2. Trigger Uvicorn’s hot-reloading (due to the `--reload` flag in the `Dockerfile`).

Retest the health check:
```bash
curl http://localhost:8000/
```
Expected response: `{"message": "Hello from FastAPI with Dapr v2!"}`

Check the Tilt UI logs to confirm the Dapr sidecar remains operational and the application restarts correctly.

### 8. Stop and Clean Up

When done, stop Tilt and clean up:

1. Press `Ctrl+C` in the terminal running `tilt up`.
2. Remove all Tilt-managed resources:
   ```bash
   tilt down
   ```

This step completes the local development environment, combining Tilt, FastAPI, and Dapr for rapid iteration in a cloud-native, production-like Kubernetes setup.