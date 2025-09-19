# M1: DACA AgentCore Initial Code Implementation Guide

This guide implements the foundational `HelloAgent` for the **DACA Actor Runtime**, a cloud-native, plug-and-play construct for AI agents using Dapr Virtual Actors. The agent, temporarily called an “Ambient Agent” for this lab, aligns with the Dapr Agentic Cloud Ascent (DACA) pattern.

## Clone and Run the Code

```bash
tilt up
```

Now in Browser Open:
- Tilt UI: http://localhost:1035
- Dapr Dashboard: http://localhost:8080
- Ambient Actor Interface: http://localhost:30080/docs
- Metrics Tracing Interface: http://localhost:9090
- Jaegur UI Interface: http://localhost:16686/

You can take it and move to next step or implement it as a challenge from scratch.

## Rebuild From Scratch

- Setup Project Structure
```bash
mkdir daca-ambient-agent
cd daca-ambient-agent

mkdir kubernetes
mkdir components

uv init --package ambient-actor
cd ambient-actor

uv venv
source .venv/bin/activate

uv add dapr
uv add dapr-ext-fastapi
uv add "fastapi[standard]"
```

Now that base project is setup let's setup Dockerfile, K8s deployment to complete our Cloud Native Development Environment. For this lab we will be calling our BaseAgent as Ambient Agent. I am excited to see the flavours all of you will create for it.

```bash
touch Dockerfile .dockerignore .gitignore
```

Fill in each file

- **.gitignore**

```.gitignore
.venv
.env
.mypy_cache
__pycache__
.pytest_cache
.ruff_cache
.vscode
```

- **.dockerignore**:

```.dockerignore
.env
.venv
__pycache__
.pytest_cache
.ruff_cache
.vscode
```

- **Dockerfile**:

```Dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY . /code/
RUN pip install uv
RUN uv sync --frozen
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.ambient_actor.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

In main.py let's get the HelloActor code - with this setup we can immediately confirm everything is setup perfectly. Later we will refactor it in modules.

```bash
touch src/ambient_actor/main.py
```

- **main.py**:

```python
import logging

from fastapi import FastAPI
from dapr.ext.fastapi import DaprActor
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="DACA Ambient Agent", description="DACA Ambient Agent")

# Add Dapr Actor Extension
actor = DaprActor(app)

# Define the actor interface
class HelloAgentInterface(ActorInterface):
    @actormethod(name="AddGreeting")
    async def add_greeting(self, greeting_data: dict) -> None:
        pass

    @actormethod(name="GetGreetingHistory")
    async def get_greeting_history(self) -> list[dict] | None:
        pass

# Implement the actor
class HelloAgent(Actor, HelloAgentInterface):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"

    async def _on_activate(self) -> None:
        """Initialize state on actor activation."""
        logging.info(f"Activating actor for {self._history_key}")
        try:
            await self._state_manager.get_state(self._history_key)
        except KeyError as e:
            logging.info(f"State not found for {self._history_key}, initializing")
            await self._state_manager.set_state(self._history_key, [])
        except Exception as e:
            logging.warning(f"Exception in _on_activate: {e}")
            raise e

    async def add_greeting(self, greeting_data: dict) -> None:
        """Add a greeting to history."""
        try:
            current_history: list = await self._state_manager.get_state(self._history_key)
            current_history.append(greeting_data)
            await self._state_manager.set_state(self._history_key, current_history)
            logging.info(f"Added greeting for {self._history_key}: {greeting_data}")
        except Exception as e:
            logging.error(f"Error adding greeting: {e}")
            raise

    async def get_greeting_history(self) -> list[dict] | None:
        """Retrieve greeting history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            return history
        except Exception as e:
            logging.error(f"Error getting history: {e}")
            return []

# Register the actor
@app.on_event("startup")
async def startup():
    await actor.register_actor(HelloAgent)
    logging.info(f"Registered actor: {HelloAgent.__name__}")

@app.get("/app-health")
def health_check():
    return {"status": "ok"}

# FastAPI endpoints to invoke the actor
@app.post("/greet/{actor_id}")
async def add_greeting(actor_id: str, greeting: dict):
    """Add a greeting to the actor's history."""
    proxy = ActorProxy.create("HelloAgent", ActorId(actor_id), HelloAgentInterface)
    await proxy.AddGreeting(greeting)
    return {"status": "Greeting added"}

@app.get("/greet/{actor_id}/history")
async def get_greeting_history(actor_id: str):
    """Retrieve the actor's greeting history."""
    proxy = ActorProxy.create("HelloAgent", ActorId(actor_id), HelloAgentInterface)
    history = await proxy.GetGreetingHistory()
    return {"history": history}
```

Finally we need an actor enabled Dapr state store and deployment file

- In **components/statestore.yaml**

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
      value: redis-master.default.svc.cluster.local:6379
    - name: redisPassword
      value: ""
    - name: actorStateStore
      value: "true"
```

- In **kubernetes/ambient-agent-deploy.yaml**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ambient-agent-deployment
  namespace: default # Consider using a dedicated namespace for your app
  labels: # Added top-level labels for better organization/selection
    app: ambient-agent
    environment: development # Example: useful for different configs
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ambient-agent
  # Strategy for updates, useful even with 1 replica for future scaling
  # and ensures zero-downtime updates if configured properly with probes
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0 # Or 25% if replicas > 1
      maxSurge: 1       # Or 25% if replicas > 1
  template:
    metadata:
      labels:
        app: ambient-agent # Pod Label matches selector
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "ambient-agent"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info" # Change to "debug" for more verbose Dapr logs during troubleshooting
        # dapr.io/enable-metrics: "true"
        # dapr.io/config: "tracing" # Ensure 'tracing' Dapr Configuration CRD exists and is correct
    spec:
      # Optional: Specify a service account if you use RBAC
      # serviceAccountName: <your-service-account>
      containers:
      - name: ambient-agent-container
        image: ambient-agent # Must Match Your Image (e.g., from tiltfile nerdctl_build)
        imagePullPolicy: IfNotPresent # Good for local dev with Tilt. For prod, consider "Always" with specific tags.
        ports:
        - name: http # Naming the port is good practice
          containerPort: 8000
          protocol: TCP
        # --- RECOMMENDED: RESOURCE REQUESTS AND LIMITS ---
        # Set these based on your application's needs to ensure stable performance and scheduling.
        # Start with small values and monitor/adjust.
        resources:
          requests: # Amount of resources reserved for your pod
            cpu: "200m" # 0.2 CPU core
            memory: "256Mi" # 256 Megabytes
          limits:   # Maximum amount of resources your pod can consume
            cpu: "500m" # 0.5 CPU core
            memory: "512Mi" # 512 Megabytes
---
apiVersion: v1
kind: Service
metadata:
  name: ambient-agent-service
  namespace: default # Match the Deployment namespace
  labels: # Consistent labels
    app: ambient-agent
spec:
  selector:
    app: ambient-agent # Must match the Pod labels defined in the Deployment template
  ports:
    - name: http-svc # Naming the port
      protocol: TCP
      port: 80 # Port the service is available on *within* the cluster
      targetPort: http # Name of the port on the Pod (containerPort name) or the port number (8000)
      nodePort: 30080 # NodePort is okay for local dev/testing or specific needs.
                      # For production or general internal access, ClusterIP (default if 'type' is omitted) is often better.
                      # If external access is needed in prod, consider an Ingress controller.
  type: NodePort # Or ClusterIP / LoadBalancer as needed
```

Finally we need a Tiltfile

```python
load('ext://helm_remote', 'helm_remote')
load('ext://nerdctl', 'nerdctl_build')

update_settings(k8s_upsert_timeout_secs=1800)

# 1. Build the FastAPI image using nerdctl
nerdctl_build(
    ref='ambient-agent',
    context='./ambient-actor',
    dockerfile='./ambient-actor/Dockerfile',
    live_update=[
        sync('./ambient-actor', '/code'),
    ]
)


helm_remote(
    chart='dapr',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    version='1.15',
    release_name='dapr',
    namespace='dapr-system',
    create_namespace=True,
    set=['global.mtls.enabled=false', 'global.ha.enabled=false', 'dapr_scheduler.ha=true', 'dapr_placement.ha=true']
)

helm_remote(
    chart='dapr-dashboard',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    release_name='dapr-dashboard',
    namespace='dapr-system',
)


k8s_resource(
    'dapr-dashboard',
    port_forwards=[port_forward(local_port=8080, container_port=8080, name='dapr-dashboard-ui')],
    labels=['dapr-ui']
)

helm_remote(
    chart='redis',
    repo_url='https://charts.bitnami.com/bitnami',
    repo_name='bitnami',
    release_name='redis',
    namespace='default',
    set=['auth.enabled=false']
)

k8s_yaml(['./components/statestore.yaml'])

# Above Dapr setup is Completed
k8s_yaml(['kubernetes/ambient-agent-deploy.yaml'])
```

Now let's run and Test it

```
tilt up
```

Open:

- Tilt UI: http://localhost:1035
- Dapr Dashboard: http://localhost:8080
- Ambient Actor Interface: http://localhost:30080/docs

If you get into any errors with tilt try the following and restart:

```bash
tilt down
tilt docker-prune

helm repo remove dapr
rm -rf ~/Library/Application\ Support/tilt-dev/.helm/dapr
rm -rf ~/.tilt-dev
```

#### 2. Setup Observibility and Tracing

Now let's stop i.e: `bash tilt down` and add the remaining base optimizations we have learnt in project setup. Let's setup **Jaeger**, and **Prometheus**

✅ **1. Jaeger** – _Distributed Tracing_

- Use Jaeger if you want to **trace requests across microservices**.
- Helps you understand **latency**, **bottlenecks**, and the flow of requests.
- Good for debugging **performance issues in distributed systems**.

🔧 Example use case: You want to see how a request travels from `frontend → API → database`.

✅ **2. Prometheus** – _Metrics Monitoring_

- Use Prometheus for **monitoring metrics** like CPU, memory, request counts, error rates, etc.
- Ideal for setting **alerts** and creating **dashboards** with Grafana.
- It’s **pull-based**, scraping metrics from your services' `/metrics` endpoint.

🔧 Example use case: You want to track how many requests per second your API gets, and get alerts if error rate increases.

We have to deploy jaegor and prometheus first. Let's use helm commands for them

- **Prometheus Setup: [Observe metrics with Prometheus](https://docs.dapr.io/operations/observability/metrics/prometheus/)**

1. Create kubernetes/monitoring/prometheus-values.yaml

```yaml
alertmanager:
  persistence:
    enabled: false
pushgateway:
  persistentVolume:
    enabled: false
server:
  persistentVolume:
    enabled: false

# Adds additional scrape configurations to prometheus.yml
# Uses service discovery to find Dapr and Dapr sidecar targets
extraScrapeConfigs: |-
  - job_name: dapr-sidecars
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - action: keep
        regex: "true"
        source_labels:
          - __meta_kubernetes_pod_annotation_dapr_io_enabled
      - action: keep
        regex: "true"
        source_labels:
          - __meta_kubernetes_pod_annotation_dapr_io_enable_metrics
      - action: replace
        replacement: ${1}
        source_labels:
          - __meta_kubernetes_namespace
        target_label: namespace
      - action: replace
        replacement: ${1}
        source_labels:
          - __meta_kubernetes_pod_name
        target_label: pod
      - action: replace
        regex: (.*);daprd
        replacement: ${1}-dapr
        source_labels:
          - __meta_kubernetes_pod_annotation_dapr_io_app_id
          - __meta_kubernetes_pod_container_name
        target_label: service
      - action: replace
        replacement: ${1}:9090
        source_labels:
          - __meta_kubernetes_pod_ip
        target_label: __address__

  - job_name: dapr
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - action: keep
        regex: dapr
        source_labels:
          - __meta_kubernetes_pod_label_app_kubernetes_io_name
      - action: keep
        regex: dapr
        source_labels:
          - __meta_kubernetes_pod_label_app_kubernetes_io_part_of
      - action: replace
        replacement: ${1}
        source_labels:
          - __meta_kubernetes_pod_label_app
        target_label: app
      - action: replace
        replacement: ${1}
        source_labels:
          - __meta_kubernetes_namespace
        target_label: namespace
      - action: replace
        replacement: ${1}
        source_labels:
          - __meta_kubernetes_pod_name
        target_label: pod
      - action: replace
        replacement: ${1}:9090
        source_labels:
          - __meta_kubernetes_pod_ip
        target_label: __address__
```

Update Tilt File

```python
load('ext://helm_remote', 'helm_remote')
load('ext://nerdctl', 'nerdctl_build')

update_settings(k8s_upsert_timeout_secs=1800)

# 1. Build the FastAPI image using nerdctl
nerdctl_build(
    ref='ambient-agent',
    context='./ambient-actor',
    dockerfile='./ambient-actor/Dockerfile',
    live_update=[
        sync('./ambient-actor', '/code'),
    ]
)


helm_remote(
    chart='dapr',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    version='1.15',
    release_name='dapr',
    namespace='dapr-system',
    create_namespace=True,
    set=['global.mtls.enabled=false', 'global.ha.enabled=false', 'dapr_scheduler.ha=true', 'dapr_placement.ha=true']
)

helm_remote(
    chart='dapr-dashboard',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    release_name='dapr-dashboard',
    namespace='dapr-system',
)

# Monitoring
# helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# helm repo update
# helm install dapr-prom prometheus-community/prometheus -n dapr-monitoring

helm_remote(
    chart='prometheus',
    repo_url='https://prometheus-community.github.io/helm-charts',
    repo_name='prometheus-community',
    release_name='dapr-prom',
    namespace='dapr-monitoring',
    create_namespace=True,
    values=['./kubernetes/monitoring/prometheus-values.yaml']
)

k8s_resource(
    'dapr-dashboard',
    port_forwards=[port_forward(local_port=8080, container_port=8080, name='dapr-dashboard-ui')],
    labels=['dapr-ui']
)

helm_remote(
    chart='redis',
    repo_url='https://charts.bitnami.com/bitnami',
    repo_name='bitnami',
    release_name='redis',
    namespace='default',
    set=['auth.enabled=false']
)

k8s_yaml(['./components/statestore.yaml'])

# kubectl port-forward svc/dapr-prom-prometheus-server 9090:80 -n dapr-monitoring
k8s_resource(
    'dapr-prom-prometheus-server',
    port_forwards=[port_forward(local_port=9090, container_port=9090, name='prometheus-server')],
    labels=['dapr-prom']
)

# Above Dapr setup is Completed
k8s_yaml(['kubernetes/ambient-agent-deploy.yaml'])

```

Now let's try it again

```bash
tilt up
```

Open:

- Tilt UI: http://localhost:1035
- Dapr Dashboard: http://localhost:8080
- Ambient Actor Interface: http://localhost:30080/docs
- Tracing Interface: http://localhost:9090

In Tracing try a query like `dapr_http_client_completed_count`.

Finally let's setup jaegor - you can setup Grafana as well if you want

- kubernetes/monitoring/jaegor.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: default
spec:
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:latest
          ports:
            - containerPort: 16686
            - containerPort: 4317
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
  namespace: default
spec:
  ports:
    - port: 16686
      targetPort: 16686
      name: ui
    - port: 4317
      targetPort: 4317
      name: otlp
  selector:
    app: jaeger
```

- components/observability.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
  namespace: default # Sentry runs in dapr-system
spec:
  tracing:
    samplingRate: "1"
    otel:
      endpointAddress: "jaeger.default.svc.cluster.local:4317"
      isSecure: false
      protocol: grpc
  metrics:
    enabled: true
```

Update Deployment annotations

```yaml
        dapr.io/enable-metrics: "true"
        dapr.io/config: "tracing" # Ensure 'tracing' Dapr Configuration CRD exists and is correct
```

Update Tilefile:

```python
load('ext://helm_remote', 'helm_remote')
load('ext://nerdctl', 'nerdctl_build')

update_settings(k8s_upsert_timeout_secs=1800)

# 1. Build the FastAPI image using nerdctl
nerdctl_build(
    ref='ambient-agent',
    context='./ambient-actor',
    dockerfile='./ambient-actor/Dockerfile',
    live_update=[
        sync('./ambient-actor', '/code'),
    ]
)


helm_remote(
    chart='dapr',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    version='1.15',
    release_name='dapr',
    namespace='dapr-system',
    create_namespace=True,
    set=['global.mtls.enabled=false', 'global.ha.enabled=true']
)

helm_remote(
    chart='dapr-dashboard',
    repo_url='https://dapr.github.io/helm-charts/',
    repo_name='dapr',
    release_name='dapr-dashboard',
    namespace='dapr-system',
)

helm_remote(
    chart='prometheus',
    repo_url='https://prometheus-community.github.io/helm-charts',
    repo_name='prometheus-community',
    release_name='dapr-prom',
    namespace='dapr-monitoring',
    create_namespace=True,
    values=['./kubernetes/monitoring/prometheus-values.yaml']
)

k8s_resource(
    'dapr-dashboard',
    port_forwards=[port_forward(local_port=8080, container_port=8080, name='dapr-dashboard-ui')],
    labels=['dapr-ui']
)

helm_remote(
    chart='redis',
    repo_url='https://charts.bitnami.com/bitnami',
    repo_name='bitnami',
    release_name='redis',
    namespace='default',
    set=['auth.enabled=false']
)

k8s_yaml(['./components/statestore.yaml'])
k8s_yaml(['./components/observability.yaml'])

# Above Dapr setup is Completed
k8s_yaml(['kubernetes/ambient-agent-deploy.yaml'])
k8s_yaml(['kubernetes/monitoring/jaeger.yaml'])

k8s_resource(
    'dapr-prom-prometheus-server',
    port_forwards=[port_forward(local_port=9090, container_port=9090, name='prometheus-server')],
    labels=['dapr-prom']
)

k8s_resource(
    'jaeger',
    port_forwards='16686:16686'
)
```

Now start and test:

- Tilt UI: http://localhost:1035
- Dapr Dashboard: http://localhost:8080
- Ambient Actor Interface: http://localhost:30080/docs
- Metrics Tracing Interface: http://localhost:9090
- Jaegur UI Interface: http://localhost:16686/