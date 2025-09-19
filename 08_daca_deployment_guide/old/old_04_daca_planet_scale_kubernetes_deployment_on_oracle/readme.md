# Deploying DACA to a Kubernetes Cluster on Oracle Cloud

Welcome to the twentieth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll ascend to the **Planet-Scale** stage by deploying the `chat_service`, `analytics_service`, and `review_ui` to a Kubernetes cluster on Oracle Cloud’s free forever Arm VMs. We’ll first set up a k3s cluster using Oracle Cloud’s 4 free Arm VMs (24 GB RAM, 4 OCPUs total), then deploy the DACA application with Kafka for messaging, Kubernetes CronJobs for scheduling, Postgres and Redis on Kubernetes, and Dapr for cluster-wide resilience. This setup will achieve planetary scale with no API limits, moving beyond the constraints of OpenAI’s 10,000 RPM limit by using Google Gemini. Let’s ascend to planet-scale!

---

## What You’ll Learn
- Setting up a k3s cluster on Oracle Cloud’s free forever Arm VMs (4 VMs, 24 GB RAM, 4 OCPUs).
- Deploying the DACA application (`chat_service`, `analytics_service`, `review_ui`) to Kubernetes.
- Configuring Kafka on Kubernetes for high-throughput messaging.
- Using Kubernetes CronJobs for scheduling tasks (e.g., resetting analytics data).
- Deploying Postgres and Redis on Kubernetes for database and in-memory storage.
- Enabling Dapr on Kubernetes for cluster-wide resilience.
- Scaling to planetary scale with no API limits using Google Gemini.

## Prerequisites
- Completion of **19_daca_medium_scale_aca_deployment** (Azure Container Apps deployment).
- An Oracle Cloud account with access to the Always Free tier (4 Arm VMs: 24 GB RAM, 4 OCPUs total).
- Basic familiarity with Kubernetes, k3s, and Oracle Cloud Infrastructure (OCI).
- Existing accounts for:
  - Google Gemini (for LLM API, replacing OpenAI to avoid API limits).
  - CloudAMQP RabbitMQ (we’ll transition to Kafka, but credentials may be reused for testing).
  - CockroachDB Serverless (we’ll transition to Postgres on Kubernetes).
  - Upstash Redis (we’ll transition to Redis on Kubernetes).
- Tools installed:
  - `kubectl` (Kubernetes CLI).
  - `k3sup` (for bootstrapping k3s).
  - `helm` (for installing Kafka, Postgres, Redis, and Dapr on Kubernetes).

---

## Step 1: Set Up a k3s Cluster on Oracle Cloud’s Free Forever Arm VMs
Oracle Cloud’s Always Free tier provides 4 Arm-based VMs (VM.Standard.A1.Flex) with a total of 24 GB RAM and 4 OCPUs. We’ll configure a k3s cluster with 1 control-plane node and 3 worker nodes.

### Step 1.1: Sign Up for Oracle Cloud and Configure VMs
1. **Create an Oracle Cloud Account**:
   - Sign up at [Oracle Cloud](https://www.oracle.com/cloud/free/).
   - The Always Free tier includes 4 Arm VMs (24 GB RAM, 4 OCPUs total). You may need to upgrade to a paid account to access Arm instances in some regions due to capacity constraints, but the resources remain free.

2. **Create 4 Arm VMs**:
   - Log in to the Oracle Cloud Console.
   - Navigate to **Compute > Instances > Create Instance**.
   - For each VM:
     - **Name**: `k3s-master` (for the control-plane node), `k3s-worker1`, `k3s-worker2`, `k3s-worker3`.
     - **Image**: Select **Ubuntu 22.04**.
     - **Shape**: Choose **VM.Standard.A1.Flex** (Arm-based).
     - **Resources**: Allocate 1 OCPU and 6 GB RAM per VM (4 VMs × 6 GB = 24 GB, 4 OCPUs total).
     - **Networking**: Place all VMs in the same Virtual Cloud Network (VCN) with a public subnet. Assign a public IP to each VM.
     - **SSH Key**: Add your public SSH key for access.
   - Create the VMs and note their public IPs:
     - `k3s-master`: `<master-ip>`
     - `k3s-worker1`: `<worker1-ip>`
     - `k3s-worker2`: `<worker2-ip>`
     - `k3s-worker3`: `<worker3-ip>`

3. **Configure Networking**:
   - Go to **Networking > Virtual Cloud Networks > [Your VCN] > Security Lists**.
   - Add inbound rules to allow:
     - Port 6443/TCP (Kubernetes API server).
     - Port 8472/UDP (Flannel for k3s networking).
     - Port 10250/TCP (Metrics server).
     - Port 22/TCP (SSH access).
     - Ports 80/TCP and 443/TCP (for ingress traffic).
   - Example rules:
     - Source: `0.0.0.0/0`, Destination: `0.0.0.0/0`, Protocol: TCP, Port: 6443.
     - Source: `10.0.0.0/8`, Destination: `10.0.0.0/8`, Protocol: UDP, Port: 8472.
     - Source: `10.0.0.0/8`, Destination: `10.0.0.0/8`, Protocol: TCP, Port: 10250.

### Step 1.2: Install k3s Using k3sup
We’ll use `k3sup` to bootstrap the k3s cluster with 1 control-plane node and 3 worker nodes.

1. **Install k3sup on Your Local Machine**:
   ```bash
   curl -sLS https://get.k3sup.dev | sh
   sudo mv k3sup /usr/local/bin/
   ```

2. **Bootstrap the Control-Plane Node**:
   - Run the following command to install k3s on `k3s-master`:
     ```bash
     k3sup install \
       --ip <master-ip> \
       --user ubuntu \
       --sudo \
       --cluster \
       --k3s-channel stable \
       --merge \
       --local-path $HOME/.kube/config \
       --context oracle \
       --ssh-key ~/.ssh/id_rsa \
       --k3s-extra-args "--no-deploy=traefik --no-deploy=servicelb --disable servicelb --disable traefik --flannel-backend=wireguard-native"
     ```
   - This command:
     - Installs k3s on the master node.
     - Disables Traefik and ServiceLB (we’ll use Nginx Ingress instead).
     - Uses WireGuard for Flannel networking (better performance).
     - Updates your local `~/.kube/config` with the cluster context.

3. **Join Worker Nodes**:
   - For each worker node (`k3s-worker1`, `k3s-worker2`, `k3s-worker3`):
     ```bash
     k3sup join \
       --ip <worker-ip> \
       --server-ip <master-ip> \
       --user ubuntu \
       --sudo \
       --k3s-channel stable \
       --ssh-key ~/.ssh/id_rsa
     ```
   - Replace `<worker-ip>` with the IP of each worker node.

4. **Verify the Cluster**:
   - Check the nodes:
     ```bash
     kubectl get nodes
     ```
     Output:
     ```
     NAME         STATUS   ROLES                  AGE   VERSION
     k3s-master   Ready    control-plane,master   5m    v1.28.8+k3s1
     k3s-worker1  Ready    <none>                 3m    v1.28.8+k3s1
     k3s-worker2  Ready    <none>                 2m    v1.28.8+k3s1
     k3s-worker3  Ready    <none>                 1m    v1.28.8+k3s1
     ```

### Step 1.3: Install Nginx Ingress Controller
Since we disabled Traefik, we’ll install the Nginx Ingress Controller for external access.

1. **Install Nginx Ingress Controller**:
   ```bash
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm repo update
   helm install ingress-nginx ingress-nginx/ingress-nginx \
     --namespace ingress-nginx \
     --create-namespace \
     --set controller.service.type=NodePort \
     --set controller.service.nodePorts.http=30080 \
     --set controller.service.nodePorts.https=30443
   ```
   - This exposes the Ingress controller on NodePorts 30080 (HTTP) and 30443 (HTTPS).

2. **Get the Public IP**:
   - Use the public IP of any node (e.g., `<master-ip>`) to access services via the Ingress controller.

---

## Step 2: Deploy Managed Services on Kubernetes
We’ll transition from external managed services (CloudAMQP, CockroachDB, Upstash Redis) to self-managed services on Kubernetes: Kafka for messaging, Postgres for the database, and Redis for the in-memory store.

### Step 2.1: Deploy Kafka on Kubernetes
We’ll use the Strimzi Kafka operator to deploy a multi-broker Kafka cluster.

1. **Install the Strimzi Kafka Operator**:
   ```bash
   helm repo add strimzi https://strimzi.io/charts/
   helm repo update
   helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
     --namespace kafka \
     --create-namespace
   ```

2. **Create a Kafka Cluster**:
   - Create a file `kafka-cluster.yaml`:
     ```yaml
     apiVersion: kafka.strimzi.io/v1beta2
     kind: Kafka
     metadata:
       name: daca-kafka
       namespace: kafka
     spec:
       kafka:
         version: 3.6.0
         replicas: 3
         listeners:
           - name: plain
             port: 9092
             type: internal
             tls: false
         config:
           offsets.topic.replication.factor: 3
           transaction.state.log.replication.factor: 3
           transaction.state.log.min.isr: 2
         storage:
           type: ephemeral
       zookeeper:
         replicas: 3
         storage:
           type: ephemeral
     ```
   - Apply the configuration:
     ```bash
     kubectl apply -f kafka-cluster.yaml
     ```

3. **Verify Kafka Deployment**:
   ```bash
   kubectl get pods -n kafka
   ```
   - You should see 3 Kafka brokers and 3 ZooKeeper nodes running.

4. **Get Kafka Bootstrap Servers**:
   - The Kafka bootstrap servers will be `daca-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092`.

### Step 2.2: Deploy Postgres on Kubernetes
We’ll use the Bitnami Postgres Helm chart to deploy Postgres.

1. **Install Postgres**:
   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm repo update
   helm install postgres bitnami/postgresql \
     --namespace database \
     --create-namespace \
     --set auth.database=daca_db \
     --set auth.username=daca_user \
     --set auth.password=your-secure-password \
     --set primary.persistence.enabled=false
   ```
   - This deploys Postgres with an ephemeral volume (for simplicity; in production, use persistent storage).

2. **Get Postgres Connection Details**:
   - Host: `postgres-postgresql.database.svc.cluster.local`
   - Port: `5432`
   - Database: `daca_db`
   - Username: `daca_user`
   - Password: `your-secure-password`

### Step 2.3: Deploy Redis on Kubernetes
We’ll use the Bitnami Redis Helm chart to deploy Redis.

1. **Install Redis**:
   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm repo update
   helm install redis bitnami/redis \
     --namespace redis \
     --create-namespace \
     --set auth.password=your-redis-password \
     --set master.persistence.enabled=false
   ```

2. **Get Redis Connection Details**:
   - Host: `redis-master.redis.svc.cluster.local`
   - Port: `6379`
   - Password: `your-redis-password`

---

## Step 3: Enable Dapr on Kubernetes
We’ll install Dapr on the Kubernetes cluster to provide cluster-wide resilience.

1. **Install Dapr**:
   ```bash
   helm repo add dapr https://dapr.github.io/helm-charts/
   helm repo update
   helm install dapr dapr/dapr \
     --namespace dapr-system \
     --create-namespace
   ```

2. **Verify Dapr Installation**:
   ```bash
   kubectl get pods -n dapr-system
   ```
   - You should see Dapr components like `dapr-operator`, `dapr-sidecar-injector`, and `dapr-sentry`.

3. **Configure Dapr Components**:
   - Create a Kafka pub/sub component (`kafka-pubsub.yaml`):
     ```yaml
     apiVersion: dapr.io/v1alpha1
     kind: Component
     metadata:
       name: pubsub
       namespace: default
     spec:
       type: pubsub.kafka
       version: v1
       metadata:
         - name: brokers
           value: "daca-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
         - name: consumerGroup
           value: "daca-group"
         - name: authType
           value: "none"
     ```
   - Create a Redis state store component (`redis-statestore.yaml`):
     ```yaml
     apiVersion: dapr.io/v1alpha1
     kind: Component
     metadata:
       name: statestore
       namespace: default
     spec:
       type: state.redis
       version: v1
       metadata:
         - name: redisHost
           value: "redis-master.redis.svc.cluster.local:6379"
         - name: redisPassword
           value: "your-redis-password"
     ```
   - Apply the components:
     ```bash
     kubectl apply -f kafka-pubsub.yaml
     kubectl apply -f redis-statestore.yaml
     ```

---

## Step 4: Update the DACA Application for Kubernetes
We’ll update the `chat_service` to use Google Gemini (to avoid OpenAI’s API limits), Kafka for messaging, Postgres for the database, and Redis for the state store. The `analytics_service` and `review_ui` will also be updated accordingly.

### Step 4.1: Update `chat_service` for Google Gemini and Kafka
Modify `chat_service/main.py` to use Google Gemini and Kafka via Dapr.

#### Updated `chat_service/main.py`
```python
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowContext, WorkflowActivityContext
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateOptions, Concurrency, Consistency
import uuid
from datetime import datetime, timezone
import json
import time
import os
from sqlmodel import SQLModel, Session, create_engine
from models import Conversation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChatService")

app = FastAPI()

# Database setup with SQLModel (Postgres)
connection_string = os.getenv("DB_CONNECTION")
engine = create_engine(connection_string, echo=True)
SQLModel.metadata.create_all(engine)

# Pydantic models
class ChatRequest(BaseModel):
    user_id: str
    text: str
    metadata: Dict[str, Any]
    tags: list[str] = []

class ChatResponse(BaseModel):
    user_id: str
    reply: str
    metadata: Dict[str, Any]

# Sensitive keywords requiring human review
SENSITIVE_KEYWORDS = ["urgent", "help", "emergency"]

# Dapr client for interacting with Dapr APIs
dapr_client = DaprClient()

# Google Gemini client setup
def get_gemini_client():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=gemini_api_key)
    return genai

def generate_reply(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    message = input["message"]
    message_count = input["message_count"]
    history = input["history"]
    
    prompt = f"User {user_id} has sent {message_count} messages. History: {history}\nMessage: {message}\nReply as a helpful assistant:"
    client = get_gemini_client()
    model = client.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.strip()

def fetch_message_count(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> int:
    user_id = input["user_id"]
    with DaprClient() as d:
        resp = d.invoke_method(
            app_id="analytics-service",
            method_name=f"analytics/{user_id}",
            http_verb="GET"
        )
        data = resp.json()
        return data.get("message_count", 0)

def get_conversation_history(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> str:
    user_id = input["user_id"]
    with Session(engine) as session:
        conversations = session.query(Conversation).filter(Conversation.user_id == user_id).all()
        if not conversations:
            return "No previous conversation."
        history = "\n".join([f"User: {conv.message}\nAssistant: {conv.reply}" for conv in conversations])
        return history

def store_conversation(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    reply = input["reply"]
    conversation = Conversation(user_id=user_id, message=message, reply=reply)
    with Session(engine) as session:
        session.add(conversation)
        session.commit()

def publish_message_sent_event(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="messages",
            data=json.dumps({"user_id": user_id, "event_type": "MessageSent"}),
            data_content_type="application/json"
        )

def check_sensitive_content(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    message = input["message"]
    is_sensitive = any(keyword in message.lower() for keyword in SENSITIVE_KEYWORDS)
    return {"is_sensitive": is_sensitive, "message": message}

def request_human_review(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> None:
    user_id = input["user_id"]
    message = input["message"]
    proposed_reply = input["proposed_reply"]
    instance_id = input["instance_id"]
    with DaprClient() as d:
        d.publish_event(
            pubsub_name="pubsub",
            topic_name="human-review",
            data=json.dumps({
                "user_id": user_id,
                "message": message,
                "proposed_reply": proposed_reply,
                "instance_id": instance_id,
                "event_type": "HumanReviewRequired"
            }),
            data_content_type="application/json"
        )

def wait_for_human_decision(ctx: WorkflowActivityContext, input: Dict[str, Any]) -> Dict[str, Any]:
    instance_id = input["instance_id"]
    with DaprClient() as d:
        while True:
            state_key = f"human-decision-{instance_id}"
            state = d.get_state(
                store_name="statestore",
                key=state_key,
                state_options=StateOptions(concurrency=Concurrency.first_write, consistency=Consistency.strong)
            )
            if state.data:
                decision_data = json.loads(state.data.decode('utf-8'))
                d.delete_state(store_name="statestore", key=state_key)
                return decision_data
            time.sleep(1)

def chat_workflow(context: DaprWorkflowContext, input: Dict[str, Any]) -> Dict[str, Any]:
    user_id = input["user_id"]
    message = input["message"]
    instance_id = context.instance_id

    logger.info(f"Starting workflow for user {user_id} with message: {message}")

    message_count = yield context.call_activity(fetch_message_count, input={"user_id": user_id})
    history = yield context.call_activity(get_conversation_history, input={"user_id": user_id})
    proposed_reply = yield context.call_activity(generate_reply, input={
        "user_id": user_id,
        "message": message,
        "message_count": message_count,
        "history": history
    })
    sensitive_result = yield context.call_activity(check_sensitive_content, input={"message": message})
    is_sensitive = sensitive_result["is_sensitive"]

    if is_sensitive:
        logger.info(f"Sensitive content detected in message: {message}. Requesting human review.")
        yield context.call_activity(request_human_review, input={
            "user_id": user_id,
            "message": message,
            "proposed_reply": proposed_reply,
            "instance_id": instance_id
        })
        decision = yield context.call_activity(wait_for_human_decision, input={"instance_id": instance_id})
        approved = decision["approved"]

        if not approved:
            logger.info(f"Human rejected the response for user {user_id}. Aborting workflow.")
            return {
                "user_id": user_id,
                "reply": "Message rejected by human reviewer.",
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
            }

    yield context.call_activity(store_conversation, input={
        "user_id": user_id,
        "message": message,
        "reply": proposed_reply
    })
    yield context.call_activity(publish_message_sent_event, input={"user_id": user_id})

    logger.info(f"Completed workflow for user {user_id}")
    return {
        "user_id": user_id,
        "reply": proposed_reply,
        "metadata": {"timestamp": datetime.now(timezone.utc).isoformat(), "session_id": str(uuid.uuid4())}
    }

workflow_runtime = WorkflowRuntime()
workflow_runtime.register_workflow(chat_workflow)
workflow_runtime.register_activity(fetch_message_count)
workflow_runtime.register_activity(get_conversation_history)
workflow_runtime.register_activity(generate_reply)
workflow_runtime.register_activity(store_conversation)
workflow_runtime.register_activity(publish_message_sent_event)
workflow_runtime.register_activity(check_sensitive_content)
workflow_runtime.register_activity(request_human_review)
workflow_runtime.register_activity(wait_for_human_decision)

@app.on_event("startup")
async def start_workflow_runtime():
    await workflow_runtime.start()

@app.on_event("shutdown")
async def stop_workflow_runtime():
    await workflow_runtime.shutdown()

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Received chat request for user {request.user_id}: {request.text}")
    instance_id = f"chat-{request.user_id}-{int(time.time())}"
    logger.info(f"Scheduling workflow with instance_id: {instance_id}")

    with DaprClient() as d:
        d.start_workflow(
            workflow_component="dapr",
            workflow_name="chat_workflow",
            input={
                "user_id": request.user_id,
                "message": request.text
            },
            instance_id=instance_id
        )

        while True:
            state = d.get_workflow(instance_id=instance_id, workflow_component="dapr")
            if state.runtime_status == "COMPLETED":
                result = state.result
                return ChatResponse(**result)
            elif state.runtime_status == "FAILED":
                raise HTTPException(status_code=500, detail="Workflow failed")
            time.sleep(0.5)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Step 4.2: Update Environment Variables
Set the following environment variables in the Kubernetes deployment:
- `DB_CONNECTION`: `postgresql://daca_user:your-secure-password@postgres-postgresql.database.svc.cluster.local:5432/daca_db`
- `GEMINI_API_KEY`: Your Google Gemini API key.

---

## Step 5: Deploy the DACA Application to Kubernetes
We’ll create Kubernetes manifests for `chat_service`, `analytics_service`, and `review_ui`, and deploy them with Dapr annotations.

### Step 5.1: Build and Push Docker Images
We’ll push the images to a container registry (e.g., Docker Hub).

1. **Build and Tag Images**:
   ```bash
   docker build -t <your-dockerhub-username>/chat-service:latest --target chat-service .
   docker build -t <your-dockerhub-username>/analytics-service:latest --target analytics-service .
   docker build -t <your-dockerhub-username>/review-ui:latest --target review-ui .
   ```

2. **Push Images**:
   ```bash
   docker push <your-dockerhub-username>/chat-service:latest
   docker push <your-dockerhub-username>/analytics-service:latest
   docker push <your-dockerhub-username>/review-ui:latest
   ```

### Step 5.2: Deploy `chat_service`
Create `chat-service-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-service
  namespace: default
spec:
  replicas: 3
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
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: chat-service
        image: <your-dockerhub-username>/chat-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_CONNECTION
          value: "postgresql://daca_user:your-secure-password@postgres-postgresql.database.svc.cluster.local:5432/daca_db"
        - name: GEMINI_API_KEY
          value: "<your-gemini-api-key>"
---
apiVersion: v1
kind: Service
metadata:
  name: chat-service
  namespace: default
spec:
  selector:
    app: chat-service
  ports:
  - port: 8000
    targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: chat-service-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: chat.daca.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: chat-service
            port:
              number: 8000
```

Apply the deployment:
```bash
kubectl apply -f chat-service-deployment.yaml
```

### Step 5.3: Deploy `analytics_service`
Create `analytics-service-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-service
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analytics-service
  template:
    metadata:
      labels:
        app: analytics-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "analytics-service"
        dapr.io/app-port: "8001"
    spec:
      containers:
      - name: analytics-service
        image: <your-dockerhub-username>/analytics-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: REDIS_URL
          value: "redis://:your-redis-password@redis-master.redis.svc.cluster.local:6379"
---
apiVersion: v1
kind: Service
metadata:
  name: analytics-service
  namespace: default
spec:
  selector:
    app: analytics-service
  ports:
  - port: 8001
    targetPort: 8001
```

Apply the deployment:
```bash
kubectl apply -f analytics-service-deployment.yaml
```

### Step 5.4: Deploy `review_ui`
Create `review-ui-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: review-ui
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: review-ui
  template:
    metadata:
      labels:
        app: review-ui
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "review-ui"
        dapr.io/app-port: "8501"
    spec:
      containers:
      - name: review-ui
        image: <your-dockerhub-username>/review-ui:latest
        ports:
        - containerPort: 8501
---
apiVersion: v1
kind: Service
metadata:
  name: review-ui
  namespace: default
spec:
  selector:
    app: review-ui
  ports:
  - port: 8501
    targetPort: 8501
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: review-ui-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: review.daca.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: review-ui
            port:
              number: 8501
```

Apply the deployment:
```bash
kubectl apply -f review-ui-deployment.yaml
```

### Step 5.5: Set Up a Kubernetes CronJob for Scheduling
Replace the ACA Job with a Kubernetes CronJob to reset analytics data daily.

Create `analytics-reset-cronjob.yaml`:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: analytics-reset
  namespace: default
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: analytics-reset
            image: curlimages/curl
            command: ["curl", "-X", "POST", "http://analytics-service.default.svc.cluster.local:8001/analytics/reset"]
          restartPolicy: OnFailure
```

Apply the CronJob:
```bash
kubectl apply -f analytics-reset-cronjob.yaml
```

---

## Step 6: Test the Kubernetes Deployment
Let’s test the deployed application to ensure it scales to planetary levels.

### Step 6.1: Access the Services
- Update your local `/etc/hosts` file to map the Ingress hosts to the cluster’s public IP:
  ```
  <master-ip> chat.daca.local review.daca.local
  ```
- Access the chat service at `http://chat.daca.local:30080/chat/`.
- Access the review UI at `http://review.daca.local:30080/`.

### Step 6.2: Initialize Analytics Data
Initialize message counts for `alice` and `bob`:
- For `alice`:
  ```bash
  curl -X POST http://chat.daca.local:30080/analytics/alice/initialize -H "Content-Type: application/json" -d '{"message_count": 5}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "alice", "message_count": 5}
  ```
- For `bob`:
  ```bash
  curl -X POST http://chat.daca.local:30080/analytics/bob/initialize -H "Content-Type: application/json" -d '{"message_count": 3}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "bob", "message_count": 3}
  ```

### Step 6.3: Send a Message Requiring Human Review
Send a message with a sensitive keyword:
```bash
curl -X POST http://chat.daca.local:30080/chat/ -H "Content-Type: application/json" -d '{"user_id": "bob", "text": "This is an urgent request!", "metadata": {"timestamp": "2025-04-06T13:47:00Z", "session_id": "123e4567-e89b-12d3-a456-426614174001"}, "tags": ["greeting"]}'
```

The request will hang, waiting for human review.

### Step 6.4: Approve the Message in the Streamlit UI
Open the Streamlit UI at `http://review.daca.local:30080/` and approve the message. The `curl` request should complete with a response like:
```json
{
  "user_id": "bob",
  "reply": "Hi Bob! You've sent 3 messages so far. No previous conversation. I understand your request is urgent—how can I assist you?",
  "metadata": {
    "timestamp": "2025-04-06T13:48:00Z",
    "session_id": "some-uuid"
  }
}
```

### Step 6.5: Simulate Load to Test Scalability
Use `ab` (Apache Benchmark) to simulate high load:
```bash
ab -n 10000 -c 1000 http://chat.daca.local:30080/health
```
- **Expected Behavior**: The `chat_service` should handle the load, with Kubernetes automatically scaling pods if needed (based on resource usage).

---

## Step 7: Monitor Costs and Scalability
- **Oracle Cloud Free Tier**: The 4 Arm VMs (24 GB RAM, 4 OCPUs) are free forever. No additional costs for compute, networking, or load balancing within the free tier limits.
- **Google Gemini API**: No strict RPM limits like OpenAI, allowing planetary scale. Cost: ~$0.0005/1K tokens → ~$5/month for high usage (e.g., 10M tokens/month).
- **Kafka, Postgres, Redis**: Self-managed on Kubernetes, so no additional costs beyond the free VMs.

**Total Estimated Cost**: ~$5/month (for Gemini API usage), with no compute costs on Oracle Cloud’s free tier.

**Scalability**: This setup supports planetary scale with no API limits, thanks to Google Gemini and Kafka’s high-throughput messaging. The k3s cluster can handle tens of thousands of requests per minute, limited only by the 24 GB RAM and 4 OCPUs.

---

## Step 8: Why Kubernetes on Oracle Cloud for Planet-Scale?
- **Oracle Cloud Free Tier**: 4 Arm VMs (24 GB RAM, 4 OCPUs) provide a cost-free foundation for a Kubernetes cluster.
- **k3s**: Lightweight Kubernetes distribution, ideal for resource-constrained environments like free VMs.
- **Kafka on Kubernetes**: High-throughput messaging with multi-broker setup, replacing CloudAMQP.
- **Kubernetes CronJobs**: Built-in scheduling for tasks like resetting analytics data.
- **Postgres and Redis on Kubernetes**: Self-managed database and in-memory store, reducing external service costs.
- **Dapr on Kubernetes**: Provides cluster-wide resilience, service discovery, and pub/sub via Kafka.
- **Google Gemini**: Removes API limits, enabling planetary scale.

---

## Step 9: Next Steps
You’ve successfully deployed the DACA application to a Kubernetes cluster on Oracle Cloud, achieving planetary scale with no API limits! In the next tutorial, we’ll explore advanced monitoring with Prometheus and Grafana, implement CI/CD with GitHub Actions, and optimize for even higher throughput.

### Optional Exercises
1. Add Horizontal Pod Autoscaling (HPA) to `chat_service` based on CPU usage.
2. Deploy Prometheus and Grafana to monitor the cluster and application metrics.
3. Set up persistent storage for Kafka, Postgres, and Redis using Longhorn.

---

## Conclusion
In this tutorial, we set up a k3s cluster on Oracle Cloud’s free forever Arm VMs, deployed the DACA application with Kafka, Postgres, Redis, and Dapr on Kubernetes, and achieved planetary scale with no API limits using Google Gemini. The application now supports thousands of requests per minute at a minimal cost of ~$5/month. 
