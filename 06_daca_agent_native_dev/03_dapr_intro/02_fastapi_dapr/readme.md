# Build the FastAPI Hello World App with Dapr SideCar

This is in continuity from our last step. First go through it and ensure you have dapr setup and running.

### What’s Happening?

We’ll build a FastAPI app that uses Dapr’s state and pub/sub APIs, with hot reloading for development.

### 1 Project Setup

1. **Initialize Project**:

   ```bash
   uv init hello_dapr_fastapi
   uv venv
   source .venv/bin/activate
   uv add "fastapi[standard]" httpx
   ```

### 2 Write the FastAPI App

Here we are using same endpoints that we tried with CURL before.

1. Create `main.py`:

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
       return {"message": "Hello from Dapr FastAPI!"}

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

2. **Create Dockerfile** (for production):

   ```dockerfile
    FROM python:3.12-slim
    WORKDIR /code
    COPY . /code/
    RUN pip install uv
    RUN uv sync --frozen
    EXPOSE 8000
    CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Create `.dockerignore`**:

   ```
   .venv
   .git
   .gitignore
   .env
   __pycache__
   ```

4. **Create Kubernetes Manifests**:

   - `kubernetes/deployment.yaml`:
     ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dapr-fastapi-hello
    namespace: default
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: dapr-fastapi-hello
    template:
      metadata:
        labels:
          app: dapr-fastapi-hello
        annotations:
          dapr.io/enabled: "true"
          dapr.io/app-id: "dapr-fastapi-hello"
          dapr.io/app-port: "8000"
          dapr.io/enable-api-logging: "true"
      spec:
        containers:
          - name: app
            image: dapr-fastapi-hello:latest
            ports:
              - containerPort: 8000
            imagePullPolicy: Never
     ```

   - `kubernetes/service.yaml`:
     ```yaml
     apiVersion: v1
     kind: Service
     metadata:
       name: dapr-fastapi-hello
       namespace: default
     spec:
       selector:
         app: dapr-fastapi-hello
       ports:
         - protocol: TCP
           port: 80
           targetPort: 8000
       type: ClusterIP
     ```

### 3 Build and Deploy

1. **Build Image**:

   ```bash
   nerdctl build -t dapr-fastapi-hello:latest .
   ```

2. **Load into `containerd`**:

   ```bash
   nerdctl save dapr-fastapi-hello:latest | nerdctl --namespace k8s.io load
   ```

3. **Verify Image**:

   ```bash
   nerdctl --namespace k8s.io images
   ```

4. **Deploy**:

   ```bash
   kubectl apply -f kubernetes/deployment.yaml
   kubectl apply -f kubernetes/service.yaml
   ```

5. **Verify Deployment**:
   ```bash
   kubectl get pods
   ```
   - Expected: `dapr-fastapi-hello-...` with `2/2` readiness.

## 4: Test the FastAPI Application

### What’s Happening?

The FastAPI app uses Dapr’s APIs to store/retrieve state and publish/subscribe to events.

1. **Port-Forward**:

   ```bash
   kubectl port-forward service/dapr-fastapi-hello 8000:80 -n default
   ```

2. **Test Root Endpoint**:

   ```bash
   curl http://localhost:8000/
   ```

   - Expected:
     ```json
     { "message": "Hello from Dapr FastAPI!" }
     ```

3. **Store a Message**:

   ```bash
   curl -X POST "http://localhost:8000/messages?user_id=junaid&message=hello" \
   -H "Content-Type: application/json"
   ```

   - Expected:
     ```json
     { "status": "Stored and published message for junaid" }
     ```

4. **Retrieve a Message**:

   ```bash
   curl http://localhost:8000/messages/junaid
   ```

   - Expected:
     ```json
     { "user_id": "junaid", "message": "hello" }
     ```

5. **Verify Pub/Sub**:
   ```bash
   kubectl logs -l app=dapr-fastapi-hello -c app
   ```
   - Expected:
     ```
     Received event: User junaid updated message to 'hello'
     ```

## Step 5: Revisit Dapr Dashboard

### What’s Happening?

Check the Dashboard to see the FastAPI app integrated with Dapr.

1. **Port-Forward**:

   ```bash
   kubectl port-forward service/dapr-dashboard 8080:8080 -n dapr-system
   ```

2. **Open Dashboard**:

   - Visit `http://localhost:8080`.
   - Check:
     - **Applications**: `dapr-fastapi-hello`.
     - **Components**: `statestore`, `pubsub`.
     - **Subscriptions**: `message-subscription`.

3. **Stop Port-Forwarding**:
   - Press `Ctrl+C`.

## Step 6: Troubleshooting

- **Dapr Installation**:
  - If pods fail: `kubectl describe pod <pod-name> -n dapr-system`.
- **Redis Issues**:
  - Check logs: `kubectl logs redis-master-0`.
  - Test: `kubectl exec -it redis-client -- redis-cli -h redis-master PING` (expect `PONG`).
- **Component Issues**:
  - Verify: `dapr components -k`.
  - Re-apply: `kubectl apply -f <file>`.
- **Pod Issues**:
  - If `CrashLoopBackOff`: `kubectl describe pod <pod-name>`.
  - Logs: `kubectl logs <pod-name> -c <container>`.
- **Port-Forwarding**:
  - Confirm service: `kubectl get svc`.
- **FastAPI Issues**:
  - Check logs: `kubectl logs -l app=dapr-fastapi-hello -c app`.


