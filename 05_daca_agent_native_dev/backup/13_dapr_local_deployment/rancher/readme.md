# Containerizing DACA Microservices with Rancher Desktop, Dapr, and Lens

Welcome to the thirteenth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll containerize the **Chat Service** and **Agent Memory Service** from **07_dapr_pubsub_messaging** using **Rancher Desktop** with the `containerd` engine and `nerdctl` CLI. We’ll create optimized Dockerfiles, build lightweight container images, test them locally with Dapr sidecars and **Redis** for state and pub/sub, and deploy them to a Kubernetes cluster (k3s). **Lens** will help visualize and manage the cluster, making debugging intuitive. This prepares us for **Tutorial 14**, where we’ll use Helm for streamlined Kubernetes deployments, targeting Azure Container Apps (ACA).

---

## What You’ll Learn

- How to create optimized Dockerfiles for the Chat Service and Agent Memory Service using Python 3.12.
- Building lightweight container images with `nerdctl` and `containerd`.
- Running containers locally with `nerdctl` to verify Dapr sidecars and Redis integration.
- Deploying containerized services with Dapr sidecars in Kubernetes using Rancher Desktop’s k3s.
- Configuring **Redis** as a Dapr state store and pub/sub backend, aligning with Step 7.
- Using **Lens** to visualize Kubernetes resources (pods, deployments, services) and debug logs.
- Verifying event-driven functionality (pub/sub and state management) from **07_dapr_pubsub_messaging**.
- Understanding containerization benefits for consistency, isolation, and scalability.

---

## Prerequisites

- **Completion of Tutorial 7**: Chat Service and Agent Memory Service working with Dapr pub/sub and state management ([Step 7 Tutorial](#)).
- **Completion of Tutorial 12**: Familiarity with Rancher Desktop, `nerdctl`, and Kubernetes (k3s) setup ([Step 12 Tutorial](#)).
- **Rancher Desktop**: Installed with `containerd` engine and k3s enabled ([Rancher Desktop Guide](https://docs.rancherdesktop.io/)).
- **Dapr CLI**: Version 1.15 installed ([Dapr CLI Installation](https://docs.dapr.io/getting-started/install-dapr-cli/)).
- **Python 3.12+**: For local development (containers handle runtime).
- **Gemini API Key**: Set in `chat_service/.env` and `agent_memory_service/.env` as `GEMINI_API_KEY=<your-key>`.
- **kubectl**: Configured for k3s (included in Rancher Desktop).
- **Lens**: Desktop version for macOS ([Lens Download](https://k8slens.dev/)).

---

## Step 1: Recap of the Current Setup

In **07_dapr_pubsub_messaging**, we built an event-driven system:

- **Chat Service**:
  - Handles user messages, fetches metadata/history via Dapr service invocation.
  - Uses a Gemini-powered LLM to generate replies.
  - Publishes “ConversationUpdated” events to a `conversations` topic via Dapr pub/sub.
  - Runs on port `8080`.
- **Agent Memory Service**:
  - Stores user metadata (`name`, `preferred_style`, `user_summary`) and conversation history in a Dapr state store.
  - Subscribes to the `conversations` topic to update history and generate `user_summary` using an LLM.
  - Runs on port `8001`.

### Current Limitations (from Tutorial 7)

- **Non-Containerized**: Services run on the host with `uv run uvicorn`, risking inconsistencies.
- **Dependency Management**: Local installs may conflict.
- **Production Readiness**: Without containers and Kubernetes, scaling or deployment to ACA is challenging.

### Goal for This Tutorial

- Containerize both services using `nerdctl` and `containerd`.
- Test them locally with `nerdctl`, Dapr sidecars, and **Redis** (matching Step 7’s `localhost:6379`, no password).
- Deploy to k3s with Dapr and Redis, using Lens to visualize and debug.
- Verify pub/sub and state management in both local and Kubernetes environments.

### Project Structure

```
fastapi-daca-tutorial/
├── chat_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env
│   └── .dockerignore
├── agent_memory_service/
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env
│   └── .dockerignore
├── components/
│   ├── subscriptions.yaml
│   ├── statestore.yaml
│   ├── pubsub.yaml
├── kubernetes/
│   ├── chat-service-deployment.yaml
│   ├── agent-memory-service-deployment.yaml
│   ├── redis-deployment.yaml
└── README.md
```

---

## Why Containerize with Rancher Desktop, Dapr, and Lens?

- **Consistency**: Ensures identical environments across development and production using `containerd`.
- **Isolation**: Encapsulates dependencies, avoiding conflicts.
- **Scalability**: Kubernetes (k3s) enables orchestration, aligning with ACA.
- **Dapr Integration**: Sidecars provide seamless pub/sub and state management with Redis.
- **Visualization**: Lens simplifies Kubernetes management, showing pods, services, and logs graphically.
- **Lightweight**: Optimized for M2’s 8-16 GB RAM constraints.

This builds on Step 12’s Kubernetes foundation, preparing for ACA, with Lens making the cluster accessible.

---

## Step 2: Setup

Let’s set up **Lens** and verify tools.

1. **Install Lens**:

   - Download from [k8slens.dev](https://k8slens.dev/) (macOS Desktop).
   - Drag to Applications folder.
   - Open Lens and ensure it detects the k3s cluster:
     ```bash
     kubectl config view
     ```

2. **Verify Tools**:

   ```bash
   nerdctl --version
   kubectl version --client
   dapr --version
   ```

   **Expected**:

   ```
   nerdctl version 2.0.3
   Client Version: v1.32.3
   Kustomize Version: v5.5.0
   CLI version: 1.15.0
   ```

3. **Prepare Environment**:
   - Set `GEMINI_API_KEY=<your-key>` in `chat_service/.env` and `agent_memory_service/.env`.
   - Create directories:
     ```bash
     mkdir -p components kubernetes
     ```

---

## Step 3: Update Code and Components

To support local and Kubernetes environments:

- Update `main.py` files to use environment variables for Dapr communication (`localhost` locally, Kubernetes DNS in k3s).
- Configure Dapr components to use **Redis** for state and pub/sub, matching Step 7.

### Step 3.1: Update Chat Service Code

Modify `chat_service/main.py` for flexible Dapr host resolution.

**`chat_service/main.py`** (key changes only; full code as in original):

```python
# ... imports and setup ...
dapr_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
dapr_host = os.getenv("DAPR_HOST", "localhost")
memory_service_host = os.getenv("MEMORY_SERVICE_HOST", "agent-memory-service.daca.svc.cluster.local")
```

**Changes**:

- `DAPR_HOST` defaults to `localhost` for local runs; Kubernetes uses pod-local Dapr.
- `MEMORY_SERVICE_HOST` defaults to Kubernetes DNS, overridden to `localhost` locally.
- `DAPR_HTTP_PORT` set to `3500` for Chat Service’s sidecar.

### Step 3.2: Update Agent Memory Service Code

Modify `agent_memory_service/main.py`.

**`agent_memory_service/main.py`** (key changes):

```python
# ... imports and setup ...
dapr_host = os.getenv("DAPR_HOST", "localhost")
dapr_port = int(os.getenv("DAPR_HTTP_PORT", "3501"))
```

**Changes**:

- `DAPR_HOST` defaults to `localhost`.
- `DAPR_HTTP_PORT` set to `3501` for Agent Memory Service’s sidecar.

### Step 3.3: Update Component Files

Configure Redis for state and pub/sub, matching Step 7 (`localhost:6379`, no password).

**`components/statestore.yaml`**:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: redis:6379
    - name: redisPassword
      value: ""
    - name: actorStateStore
      value: "true"
```

**`components/pubsub.yaml`**:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.redis
  version: v1
  metadata:
    - name: redisHost
      value: redis:6379
    - name: redisPassword
      value: ""
```

**`components/subscriptions.yaml`**:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: conversations-subscription
spec:
  pubsubname: pubsub
  topic: conversations
  route: /conversations
scopes:
  - agent-memory-service # Only this app subscribes
```

**Instructions**:

1. Save files in `components/`.
2. **Note**: `${REDIS_HOST:-redis}` allows `redis.daca.svc.cluster.local` in Kubernetes, defaulting to `localhost` locally.

---

## Step 4: Create Optimized Dockerfiles

Use `python:3.12-slim` with `uv` for efficient builds.

### Step 4.1: Chat Service Dockerfile

**`chat_service/Dockerfile`**:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN pip install uv
RUN uv sync --frozen
COPY . /app
EXPOSE 8080
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**`chat_service/.dockerignore`**:

```
.venv
.mypy_cache
__pycache__
.pytest_cache
.env
```

### Step 4.2: Agent Memory Service Dockerfile

**`agent_memory_service/Dockerfile`**:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock /app/
RUN pip install uv
RUN uv sync --frozen
COPY . /app
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**`agent_memory_service/.dockerignore`**:

```
.venv
.mypy_cache
__pycache__
.pytest_cache
.env
```

**Note**: `.env` excluded; `GEMINI_API_KEY` is passed via env vars or Secrets.

---

## Step 5: Build the Container Images

Build images with `nerdctl`.

### Step 5.1: Build Chat Service

```bash
cd chat_service
nerdctl build -t chat-service:latest .
cd ..
```

### Step 5.2: Build Agent Memory Service

```bash
cd agent_memory_service
nerdctl build -t agent-memory-service:latest .
cd ..
```

### Step 5.3: Verify Images

```bash
nerdctl images
```

**Expected**:

```
REPOSITORY              TAG       IMAGE ID        CREATED           PLATFORM       SIZE       BLOB SIZE
agent-memory-service    latest    54dcd55ec0ea    26 minutes ago    linux/arm64    350.6MB    112.6MB
chat-service            latest    d8ab8385e3b9    27 minutes ago    linux/arm64    350.2MB    112.5MB
```

---

## Step 6: Run Containers Locally with nerdctl

Test locally to ensure reliability.

### Step 6.1: Create Network

```bash
nerdctl network create dapr-network
```

### Step 6.2: Run Redis

```bash
nerdctl run -d --name redis \
  --network dapr-network \
  -p 6379:6379 \
  redis:7.0
```

Verify:

```bash
nerdctl ps
```

**Expected**:

```
CONTAINER ID   IMAGE        COMMAND                  STATUS         PORTS
abc123def456   redis:7.0    "docker-entrypoint..."   Up 10s         0.0.0.0:6379->6379/tcp
```

### Step 6.3: Run Agent Memory Service

1. **App**:

```bash
nerdctl run -d --name agent-memory-service-app \
  --network dapr-network \
  -p 8001:8001 \
  -e DAPR_HOST=agent-memory-service-dapr \
  -e MEMORY_SERVICE_HOST=agent-memory-service-app \
  agent-memory-service:latest
```

2. **Dapr Sidecar**:

```bash
nerdctl run -d --name agent-memory-service-dapr \
  --network dapr-network \
  -p 3501:3501 \
  -v $(pwd)/components:/components \
  -e DAPR_HTTP_PORT=3501 \
  -e REDIS_HOST=redis \
  daprio/dapr:1.15.1 \
  ./daprd \
  --app-id agent-memory-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --log-level debug \
  --components-path /components \
  --app-protocol http \
  --app-channel-address agent-memory-service-app
```

### Step 6.4: Run Chat Service

1. **App**:

```bash
nerdctl run -d --name chat-service-app \
  --network dapr-network \
  -p 8080:8080 \
  -e DAPR_HOST=chat-service-dapr \
  -e MEMORY_SERVICE_HOST=agent-memory-service-dapr \
  chat-service:latest
```

2. **Dapr Sidecar**:

```bash
nerdctl run -d --name chat-service-dapr \
  --network dapr-network \
  -p 3500:3500 \
  -v $(pwd)/components:/components \
  -e DAPR_HTTP_PORT=3500 \
  -e REDIS_HOST=redis \
  daprio/dapr:1.15.1 \
  ./daprd \
  --app-id chat-service \
  --app-port 8080 \
  --dapr-http-port 3500 \
  --log-level debug \
  --components-path /components \
  --app-protocol http \
  --app-channel-address chat-service-app
```

### Step 6.5: Verify Containers

```bash
nerdctl ps
```

**Expected**:

```
CONTAINER ID   IMAGE                             COMMAND                  STATUS         PORTS
xyz789abc012   daprio/dapr:1.15                  "./daprd ..."            Up 5s          0.0.0.0:3500->3500/tcp
def456ghi789   chat-service:latest               "uvicorn main:app..."    Up 10s         0.0.0.0:8080->8080/tcp
jkl012mno345   daprio/dapr:1.15                  "./daprd ..."            Up 15s         0.0.0.0:3501->3501/tcp
pqr678stu901   agent-memory-service:latest       "uvicorn main:app..."    Up 20s         0.0.0.0:8001->8001/tcp
abc123def456   redis:7.0                         "docker-entrypoint..."   Up 30s         0.0.0.0:6379->6379/tcp
```

### Step 6.6: Add a script to automate startup

run.sh

```sh
#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colorful status messages
status() {
    echo -e "${GREEN}[+] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

# Stop any existing containers
status "Cleaning up any existing containers..."
nerdctl rm -f chat-service-app chat-service-dapr agent-memory-service-app agent-memory-service-dapr redis 2>/dev/null || true
nerdctl network rm dapr-network 2>/dev/null || true

# Build the Docker images
status "Building chat-service image..."
(cd chat-service && nerdctl build -t chat-service:latest .)

status "Building agent-memory-service image..."
(cd agent_memory_service && nerdctl build -t agent-memory-service:latest .)

# Create a Docker network
status "Creating Docker network..."
nerdctl network create dapr-network

# Run Redis
status "Starting Redis container..."
nerdctl run -d --name redis \
  --network dapr-network \
  -p 6379:6379 \
  redis:7.0

# Wait for Redis to be ready
status "Waiting for Redis to be ready..."
sleep 3

# Run Agent Memory Service
status "Starting Agent Memory Service container..."
nerdctl run -d --name agent-memory-service-app \
  --network dapr-network \
  -p 8001:8001 \
  -e DAPR_HOST=agent-memory-service-dapr \
  -e MEMORY_SERVICE_HOST=agent-memory-service-app \
  agent-memory-service:latest

# Run Dapr sidecar for Agent Memory Service
status "Starting Dapr sidecar for Agent Memory Service..."
nerdctl run -d --name agent-memory-service-dapr \
  --network dapr-network \
  -p 3501:3501 \
  -v $(pwd)/components:/components \
  -e DAPR_HTTP_PORT=3501 \
  -e REDIS_HOST=redis \
  daprio/dapr:1.15.1 \
  ./daprd \
  --app-id agent-memory-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --log-level debug \
  --components-path /components \
  --app-protocol http \
  --app-channel-address agent-memory-service-app

# Run Chat Service
status "Starting Chat Service container..."
nerdctl run -d --name chat-service-app \
  --network dapr-network \
  -p 8080:8080 \
  -e DAPR_HOST=chat-service-dapr \
  -e MEMORY_SERVICE_HOST=agent-memory-service-dapr \
  chat-service:latest

# Run Dapr sidecar for Chat Service
status "Starting Dapr sidecar for Chat Service..."
nerdctl run -d --name chat-service-dapr \
  --network dapr-network \
  -p 3500:3500 \
  -v $(pwd)/components:/components \
  -e DAPR_HTTP_PORT=3500 \
  -e REDIS_HOST=redis \
  daprio/dapr:1.15.1 \
  ./daprd \
  --app-id chat-service \
  --app-port 8080 \
  --dapr-http-port 3500 \
  --log-level debug \
  --components-path /components \
  --app-protocol http \
  --app-channel-address chat-service-app

# Verify the containers are running
status "Verifying containers are running..."
nerdctl ps

# Show connection info
status "All services are running!"
echo -e "${GREEN}------------------------------------${NC}"
echo -e "Chat Service: http://localhost:8080/chat/"
echo -e "Agent Memory Service: http://localhost:8001/memories/"
echo -e "${GREEN}------------------------------------${NC}"
echo -e "You
```

After creating above script in terminal run

```bash
chmod +x ruh.sh
```

And then run it to start all containers

```bash
./run.sh
```

### Step 6.7: Test Locally

#### Initialize State

```bash
curl -X POST http://localhost:8001/memories/junaid/initialize \
  -H "Content-Type: application/json" \
  -d '{"name": "Junaid", "preferred_style": "informal", "user_summary": "Muhammad is building Agents WorkForce."}'
```

**Expected**:

```json
{"status":"success","user_id":"junaid","metadata":{"name":"Junaid","preferred_style":"informal","user_summary":"Muhammad is building Agents WorkForce."}}%
```

#### Test Chat Service

First request:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "I need to schedule a session with myself."}'
```

**Expected**:

```json
{
  "user_id": "junaid",
  "reply": "Hey Junaid,  I can't actually *schedule* things for you,  I'm just a chatbot.  I don't have access to a calendar or scheduling system. To schedule a session with yourself, you'll have to use your own calendar app or a scheduling tool.  Let me know if you have any other questions!\n",
  "metadata": {
    "timestamp": "2025-04-16T01:30:31.727122+00:00",
    "session_id": "f88e885a-03ef-43d2-8ad9-841f4790ba5d"
  }
}
```

Second request (same session):

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "What was my last msg?", "metadata": {"session_id": "f88e885a-03ef-43d2-8ad9-841f4790ba5d"}}'
```

**Expected**:

```json
  -d '{"user_id": "junaid", "text": "What was my last msg?", "metadata": {"session_id": "f88e885a-03ef-43d2-8ad9-841f4790ba5d"}}'
{"user_id":"junaid","reply":"Your last message was: \"I need to schedule a session with myself.\"\n","metadata":{"timestamp":"2025-04-16T01:31:18.478038+00:00","session_id":"f88e885a-03ef-43d2-8ad9-841f4790ba5d"}}
```

#### Verify Metadata

```bash
curl http://localhost:8001/memories/junaid
```

**Expected**:

```json
{"name":"Junaid","preferred_style":"informal","user_summary":"Junaid needs to schedule a session with himself and uses a calendar app or scheduling tool.\n"}%
```

#### Test Background Memories

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Tomorrow we will pack for SF?", "metadata": {"session_id": "f88e885a-03ef-43d2-8ad9-841f4790ba5d"}}'
```

New session:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Where was I planning to go tomorrow?"}'
```

**Expected**:

```json
{"user_id":"junaid","reply":"Hey Junaid!  Looks like you're planning a trip to San Francisco tomorrow.  Have you started packing yet?\n","metadata":{"timestamp":"2025-04-16T01:32:47.743857+00:00","session_id":"49ac5195-0f39-4773-a04f-a85e66ea5358"}}%
```

#### Check Logs

- Chat Service:

```bash
nerdctl logs chat-service-app
```

- Agent Memory Service:

```bash
nerdctl logs agent-memory-service-app
```

**Expected**:

```
INFO:main:Stored conversation history for session 98289651-62fb-45eb-804a-21c7ee59384c
INFO:main:Stored metadata for junaid: {'name': 'Junaid', 'preferred_style': 'casual', 'user_summary': 'Junaid needs to schedule a coding session.'}
```

- Dapr Sidecars:

```bash
nerdctl logs chat-service-dapr
nerdctl logs agent-memory-service-dapr
```

**Expected**: Pub/sub events and subscriptions.

### Step 6.8: Clean Up

```bash
nerdctl rm -f chat-service-app chat-service-dapr agent-memory-service-app agent-memory-service-dapr redis
nerdctl network rm dapr-network
```

---

## Step 7: Deploy to Kubernetes with Dapr

Deploy to k3s with Lens for monitoring.

### Step 7.0: Initialize Dapr

```bash
dapr init -k
```

To verify, run `dapr status -k' in your terminal

Verify in **Lens**:

- **Namespaces** → `dapr-system`.
- Check **Pods** for `dapr-dashboard`, `dapr-operator`, etc., all **Running** and **1/1**.

Verify CLI:

```bash
kubectl get pods -n dapr-system
```

**Expected**:

```
NAME                                     READY   STATUS    RESTARTS       AGE
dapr-dashboard-5cb455db6f-9s59n          1/1     Running   0              2m31s
dapr-operator-5fbcb75589-qt9dh           1/1     Running   2 (107s ago)   2m33s
dapr-placement-server-0                  1/1     Running   0              2m33s
dapr-scheduler-server-0                  1/1     Running   0              2m33s
dapr-scheduler-server-1                  1/1     Running   0              2m33s
dapr-scheduler-server-2                  1/1     Running   0              2m33s
dapr-sentry-75b55cbb9-2kp6n              1/1     Running   0              2m33s
dapr-sidecar-injector-76545c8c59-55tqx   1/1     Running   0              2m33s
...
```

### Step 7.1: Create Namespace

```bash
kubectl create namespace daca
```

**Lens**: Refresh **Namespaces**; confirm `daca` appears.

### Step 7.2: Create Secret

```bash
kubectl create secret generic gemini-api-key --from-literal=gemini-api-key=YOUR_KEY_FOR_GEMINI -n daca
```

**Lens**: **Secrets** in `daca`; verify `gemini-api-key`.

### Step 7.3: Deploy Redis

**`kubernetes/redis-deployment.yaml`**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: daca
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
      name: redis
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: daca
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7.0
          ports:
            - containerPort: 6379
              name: redis
```

Apply:

```bash
kubectl apply -f kubernetes/redis-deployment.yaml
kubectl wait --for=condition=ready pod -l app=redis -n daca --timeout=60s
```

**Lens**:

- **Workloads** → **Deployments** in `daca`.
- Verify `redis` is **1/1**; pod `redis-xxxxxx` is **Running**.

### Step 7.4: Deploy Dapr Components

Firstly we will update

- statestore.yaml
```yaml
  - name: redisHost
    # value: redis:6379
    value: redis.daca.svc.cluster.local:6379
```

- pubsub.yaml
```yaml
  - name: redisHost
    # value: redis:6379
    value: redis.daca.svc.cluster.local:6379
```

Run:

```bash
kubectl apply -f components/statestore.yaml -n daca
kubectl apply -f components/pubsub.yaml -n daca
kubectl apply -f components/subscriptions.yaml -n daca
```

Verify:

```bash
kubectl get components -n daca
kubectl get subscriptions -n daca
```

**Expected**:

```
NAME         AGE
pubsub       17s
statestore   21s
```

```
NAME                        AGE
conversation-subscription   53s
```

### Step 7.5: Load Images

When you build images with nerdctl, they're stored in the local containerd registry, but Kubernetes (k3s) has its own separate registry. This step transfers the images from your local registry to the Kubernetes registry so that when you deploy pods, Kubernetes can find and use these images.

```bash
nerdctl save chat-service:latest | nerdctl --namespace k8s.io load
nerdctl save agent-memory-service:latest | nerdctl --namespace k8s.io load
```

### Step 7.6: Deploy Chat Service

**`kubernetes/chat-service-deployment.yaml`**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-service
  namespace: daca
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chat-service
  template:
    metadata:
      labels:
        app: chat-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "chat-service"
        dapr.io/app-port: "8080"
        dapr.io/http-port: "3500"
    spec:
      containers:
        - name: app
          image: chat-service:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 8080
          env:
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gemini-api-key
                  key: gemini-api-key
            - name: REDIS_HOST
              value: "redis.daca.svc.cluster.local"
            - name: DAPR_HOST
              value: "localhost"
            - name: MEMORY_SERVICE_HOST
              value: "agent-memory-service.daca.svc.cluster.local"
---
apiVersion: v1
kind: Service
metadata:
  name: chat-service
  namespace: daca
spec:
  selector:
    app: chat-service
  ports:
    - port: 8080
      targetPort: 8080
  type: ClusterIP
```

Apply:

```bash
kubectl apply -f kubernetes/chat-service-deployment.yaml
```

**Lens**:

- **Deployments** in `daca`; `chat-service` is **1/1**.
- **Pods**; `chat-service-abc123` has **2/2** containers.

### Step 7.7: Deploy Agent Memory Service

**`kubernetes/agent-memory-service-deployment.yaml`**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-memory-service
  namespace: daca
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agent-memory-service
  template:
    metadata:
      labels:
        app: agent-memory-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "agent-memory-service"
        dapr.io/app-port: "8001"
        dapr.io/http-port: "3500"
    spec:
      containers:
        - name: app
          image: agent-memory-service:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 8001
          env:
            - name: GEMINI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: gemini-api-key
                  key: gemini-api-key
            - name: REDIS_HOST
              value: "redis.daca.svc.cluster.local"
            - name: DAPR_HOST
              value: "localhost" # Dapr sidecar runs in the same pod
            - name: MEMORY_SERVICE_HOST
              value: "agent-memory-service.daca.svc.cluster.local" # Kubernetes service name
---
apiVersion: v1
kind: Service
metadata:
  name: agent-memory-service
  namespace: daca
spec:
  selector:
    app: agent-memory-service
  ports:
    - port: 8001
      targetPort: 8001
  type: ClusterIP
```

Apply:

```bash
kubectl apply -f kubernetes/agent-memory-service-deployment.yaml
```

**Lens**:

- `agent-memory-service` is **1/1**.
- Pod `agent-memory-service-def456` has **2/2** containers.

### Step 7.8: Verify Pods

```bash
kubectl get pods -n daca
```

**Expected**:

```
NAME                                   READY   STATUS    RESTARTS   AGE
agent-memory-service-f99ffdbb8-8sw78   1/2     Running   0          66s
chat-service-54c74cb58b-2gcf8          2/2     Running   0          117s
redis-7d67489d46-jw4m9                 1/1     Running   0          10m
```

**Lens**:

- **Pods** in `daca`; all **Running** (`2/2` for services, `1/1` for Redis).

---

## Step 8: Test the Kubernetes Setup

Use `kubectl port-forward` and Lens to test.

### Step 8.1: Initialize State

```bash
kubectl port-forward svc/agent-memory-service 8001:8001 -n daca
```

**Lens**: Monitor **Logs** for `agent-memory-service-def456` (`app` container).

Test:

```bash
curl -X POST http://localhost:8001/memories/junaid/initialize \
  -H "Content-Type: application/json" \
  -d '{"name": "Junaid", "preferred_style": "casual", "user_summary": "Junaid is building Agents WorkForce."}'
```

**Expected**:

```json
{
  "status": "success",
  "user_id": "junaid",
  "metadata": {
    "name": "Junaid",
    "preferred_style": "casual",
    "user_summary": "Junaid is building Agents WorkForce."
  }
}
```

**Lens**: Logs show:

```
INFO:main:Stored metadata for junaid: ...
```

### Step 8.2: Test Chat Service

```bash
kubectl port-forward svc/chat-service 8080:8080 -n daca
```

**Lens**: Monitor `chat-service-abc123` logs.

First request:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Finally another good thing in cloud first - it is working."}'
```

**Expected**:

```json
{
  "user_id": "junaid",
  "reply": "Hey Junaid! Sounds good. What time works best for you? I can help you figure that out.",
  "metadata": {
    "timestamp": "2025-04-15T12:01:04.035603+00:00",
    "session_id": "98289651-62fb-45eb-804a-21c7ee59384c"
  }
}
```

Second request:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "What was my last msg?", "metadata": {"session_id": "98289651-62fb-45eb-804a-21c7ee59384c"}}'
```

**Expected**:

```json
{
  "user_id": "junaid",
  "reply": "Your last message was: \"I need to schedule a coding session.\"",
  "metadata": {
    "timestamp": "2025-04-15T12:02:03.001332+00:00",
    "session_id": "98289651-62fb-45eb-804a-21c7ee59384c"
  }
}
```

**Lens**: Logs show:

```
INFO:main:Published ConversationUpdated event ...
```

### Step 8.3: Verify Metadata

```bash
curl http://localhost:8001/memories/junaid
```

**Expected**:

```json
{
  "name": "Junaid",
  "preferred_style": "casual",
  "user_summary": "Junaid needs to schedule a coding session."
}
```

### Step 8.4: Test Background Memories

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Tomorrow we will pack for SF?", "metadata": {"session_id": "98289651-62fb-45eb-804a-21c7ee59384c"}}'
```

New session:

```bash
curl -X POST http://localhost:8080/chat/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "junaid", "text": "Where was I planning to go tomorrow?"}'
```

**Expected**:

```json
{
  "user_id": "junaid",
  "reply": "Based on our previous conversation, you, Junaid, are planning a trip to San Francisco tomorrow.",
  "metadata": {
    "timestamp": "2025-04-15T12:03:00Z",
    "session_id": "new-uuid"
  }
}
```

**Lens**: Check **Events** for pods; verify no errors.

### Step 8.5: Check Logs with CLI

- Chat Service:

```bash
kubectl logs -l app=chat-service -n daca -c app
```

**Expected**:

```
INFO:main:Successfully fetched metadata for junaid
...
```

- Agent Memory Service:

```bash
kubectl logs -l app=agent-memory-service -n daca -c app
```

**Expected**:

```
INFO:main:Stored conversation history ...
```

- Dapr Sidecars:

```bash
kubectl logs -l app=chat-service -n daca -c daprd
kubectl logs -l app=agent-memory-service -n daca -c daprd
```

**Expected**: Pub/sub activity.

---

## Step 9: Benefits of Containerization and Lens for DACA

- **Consistency**: Uniform environments with `containerd` and k3s.
- **Isolation**: No dependency conflicts.
- **Scalability**: Kubernetes-ready for ACA.
- **Event-Driven Integrity**: Dapr ensures Redis-backed pub/sub.
- **Reliability**: Local testing catches issues.
- **Ease of Learning**: Lens visualizes complex Kubernetes setups.

**RAM Total**: ~650 MB local, ~1.2 GB Kubernetes (Redis, services, Dapr, k3s, Lens).

---

## Step 10: Next Steps

In **Tutorial 14**, we’ll use **Helm** for simpler deployments.

### Optional Exercises

1. **Push to Docker Hub**:

   ```bash
   nerdctl tag chat-service:latest yourusername/chat-service:latest
   nerdctl push yourusername/chat-service:latest
   ```

   Update `image` in `chat-service-deployment.yaml` to `yourusername/chat-service:latest`, set `imagePullPolicy: Always`, and reapply.

2. **Dapr Dashboard**:

   ```bash
   dapr dashboard -k
   ```

   View Dapr components in browser.

3. **Scale Replicas**:
   Set `replicas: 2` in deployment YAMLs, apply, and observe in Lens.

---

## Step 11: Conclusion

We’ve containerized the Chat Service and Agent Memory Service, tested them locally with Redis and Dapr, and deployed to Kubernetes. **Lens** simplified cluster management, showing pods, deployments, and logs. The setup mirrors ACA best practices, verified by Step 7’s tests. Next, we’ll use Helm for efficiency!

---

### Additional Notes

- **Redis**: Lightweight (~50 MB) and schema-less, ideal for Dapr’s key-value needs.
- **Lens Tips**:
  - Use **Network** → **Services** to inspect `chat-service`, `agent-memory-service`, `redis`.
  - Check **Events** for troubleshooting.
  - Access pod **Shell** for debugging.
- **Cleanup**:

```bash
kubectl delete -f kubernetes/chat-service-deployment.yaml -n daca
kubectl delete -f kubernetes/agent-memory-service-deployment.yaml -n daca
kubectl delete -f kubernetes/redis-deployment.yaml -n daca
kubectl delete -f components/statestore.yaml -n daca
kubectl delete -f components/pubsub.yaml -n daca
kubectl delete -f components/subscriptions.yaml -n daca
kubectl delete namespace daca
```
