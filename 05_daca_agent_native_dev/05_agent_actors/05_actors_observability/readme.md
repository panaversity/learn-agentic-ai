# Step 7: [Observability](https://docs.dapr.io/operations/observability):  (Tracing, Metrics, and Logging)

This step updates the `ChatAgent` actor from **Step 2** to include comprehensive observability, combining **tracing** (OpenTelemetry with Jaeger), and **metrics** (Prometheus). This enhances monitoring and debugging for production-grade AI agents, aligning with DACA’s goal of building reliable, observable, and scalable ai-systems.

## Overview

The **observability** step configures the `ChatAgent` to:

- Enable Dapr’s OpenTelemetry tracing and metrics export to Jaeger (traces) and Prometheus (metrics), as in the original setup.
- Monitor actor invocation counts, state store latencies, and log events (e.g., message processing, errors).
- Test observability by invoking the `ChatAgent` and verifying traces in Jaeger, and metrics in Prometheus.
- Preserve the existing `process_message` and `get_conversation_history` functionality from **Step 2**.

This setup provides a holistic view of actor performance, system health, and application behavior, critical for scaling AI agents in distributed environments.

### Learning Objectives

- Configure Dapr’s OpenTelemetry for tracing and metrics.
- Deploy Jaeger and Prometheus for trace and metric collection.
- Validate traces, metrics, and logs for actor operations.
- Maintain lightweight changes with minimal actor code modifications.

### Ties to DACA

- **Reliability**: Observability (tracing, metrics, logging) helps diagnose issues like state store failures, slow responses, or application errors.
- **Scalability**: Metrics and logs enable performance optimization for high user loads.
- **Production-Readiness**: Comprehensive observability supports monitoring and debugging in distributed AI systems.
- **Agent-Native Cloud**: Structured logging and observability align with DACA’s vision of agent-centric infrastructure, as outlined in Appendix VI.

## Key Concepts

### Dapr Observability

Dapr’s observability capabilities include:
- **[Tracing](https://docs.dapr.io/operations/observability/tracing/tracing-overview/)**: Tracks actor method calls (e.g., `process_message`) and state store operations (e.g., Redis get/set) using OpenTelemetry.
- **[Metrics](https://docs.dapr.io/operations/observability/metrics/metrics-overview/)**: Measures actor invocations, state store latency, and error rates, exported to Prometheus.
- **[Logging](https://docs.dapr.io/operations/observability/logging/)**: Produces structured logs to stdout in plain-text or JSON format, parsable by log collectors like Fluent Bit.

This step integrates two pillars, exporting traces to Jaeger, nd metrics to Prometheus.

### Lightweight Configuration

Observability is added with minimal changes:
Observability is added with minimal changes:
- **Tracing/Metrics**: A Dapr configuration file (`observability.yaml`) enables OpenTelemetry, with Jaeger and Prometheus deployments.
- **No Actor Code Changes**: The `ChatAgent` code from **Step 2** remains unchanged, as observability is handled by Dapr and external tools.
- **Minimal Dependencies**: Jaeger, Prometheus, keeping the setup lightweight.

### Interaction Patterns

The `ChatAgent` supports:
- **Request/Response**: FastAPI endpoints (`/chat/{actor_id}`, `/chat/{actor_id}/history`) with traced invocations and logged events.
- **Event-Driven**: Pub/sub events via `/subscribe` with traced and logged events.
- **Observable**: Traces, metrics, and logs provide insights into actor and system performance.


## Hands-On Dapr Virtual Actor

### 0. Setup Code

Use the [02_chat_actor](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/02_chat_actor/chat_actor_lab) from **Step 2**. Ensure **Step 2** is complete and you have a Kubernetes cluster setup.

### 1. Deploy Observability Tools

Deploy Jaeger and Prometheus in your Kubernetes cluster to collect traces and metrics.

**File**: `jaeger.yaml`

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

**File**: `prometheus.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: default
spec:
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
        - name: prometheus
          image: prom/prometheus:latest
          ports:
            - containerPort: 9090
          volumeMounts:
            - name: config
              mountPath: /etc/prometheus
      volumes:
        - name: config
          configMap:
            name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: default
spec:
  ports:
    - port: 9090
      targetPort: 9090
  selector:
    app: prometheus
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: default
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'dapr'
      static_configs:
      - targets: ['daca-ai-app-dapr:9090']
```

### 2. Configure Dapr Observability and Logging

Update the Dapr configuration to enable OpenTelemetry tracing, metrics, and JSON-formatted logging.

#### Dapr Observability Configuration
**File**: `components/observability.yaml`
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: observability
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    otel:
      endpointAddress: "jaeger:4317"
      isSecure: false
      protocol: grpc
  metrics:
    enabled: true
    exporter:
      type: prometheus
      address: "prometheus:9090"
```

#### Enable JSON Logging in Dapr
Update the `ChatAgent` deployment to enable JSON-formatted logs by adding the `dapr.io/log-as-json` annotation.

**File**: `deployment.yaml`
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
        dapr.io/log-as-json: "true"  # Enable JSON-formatted logging
    spec:
      containers:
      - name: app
        image: daca-ai-app
        imagePullPolicy: IfNotPresent
        ports:
          - containerPort: 8000
        env:
          - name: DAPR_HTTP_PORT
            value: "3500"
```


### 3. Use the Step 2 ChatAgent Code

No changes are needed to the **Step 2** `ChatAgent` code, as observability is handled by Dapr’s configuration. Use the **Step 2** `main.py` as-is (see **Step 4.5** README for the code).

### 4. Test the App

1. Update Titlefile

```bash
load('ext://helm_remote', 'helm_remote') # helm extension -> Dapr Helm Chart
load('ext://nerdctl', 'nerdctl_build') # nerdctl extension -> Docker Build

update_settings(k8s_upsert_timeout_secs=900) # Increase apply timeout for Helm deployments


# 1. Build the FastAPI image using nerdctl
nerdctl_build(
    ref='daca-ai-app',
    context='.',
    dockerfile='Dockerfile',
    live_update=[
        sync('.', '/code'),
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
    set=['global.mtls.enabled=false']
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

k8s_yaml(['./components/statestore.yaml', './components/pubsub.yaml', './components/observability.yaml'])

k8s_yaml(['./components/subscriptions.yaml'])

# Above Dapr setup is Completed

k8s_yaml(['kubernetes/deployment.yaml', 'kubernetes/service.yaml', 'kubernetes/jaeger.yaml', 'kubernetes/prometheus.yaml'])

k8s_resource(
    'daca-ai-app',
    port_forwards='8000:8000',
)

k8s_resource(
    'prometheus',
    port_forwards='9090:9090',
)

k8s_resource(
    'jaeger',
    port_forwards='16686:16686',
)
```

Open:
- Jaeger UI: [http://localhost:16686](http://localhost:16686)
- Prometheus UI: [http://localhost:9090](http://localhost:9090)

Test the **default** route group:
- **POST /chat/{actor_id}**: Sends a user message.
- **GET /chat/{actor_id}/history**: Retrieves the conversation history.
- **POST /subscribe**: Handles `user-chat` topic events.

Use `curl` commands to generate activity:
```bash
curl -X POST http://localhost:8000/chat/user1 -H "Content-Type: application/json" -d '{"role": "user", "content": "Hi there"}'
curl http://localhost:8000/chat/user1/history
curl -X POST http://localhost:8000/chat/user2 -H "Content-Type: application/json" -d '{"role": "user", "content": "Hello"}'
```


**Expected Output**:
- **POST user1**: `{"response": {"role": "assistant", "content": "Got your message: Hi there"}}`
- **GET user1**: `{"history": [{"role": "user", "content": "Hi there"}, {"role": "assistant", "content": "Got your message: Hi there"}]}`
- **POST user2**: `{"response": {"role": "assistant", "content": "Got your message: Hello"}}`
- **Jaeger**: Traces for `POST /chat/user1`, `GET /chat/user1/history`, and `POST /chat/user2`, showing `process_message`, `get_conversation_history`, and Redis operations.
- **Prometheus**: Metrics like `dapr_actor_invocations_total{actor_type="ChatAgent", app_id="daca-ai-app"}` increase with each request.

  ```

### 5. Understand the Setup

Review the setup:
- **No Code Changes**: The **Step 2** `main.py` remains unchanged, as observability and logging are configured via Dapr and external tools.
- **Observability Config**: `observability.yaml` enables tracing to Jaeger and metrics to Prometheus.
- **Tools**:
  - **Jaeger**: Visualizes traces (e.g., actor method calls, state store latency).
  - **Prometheus**: Collects metrics (e.g., invocation counts, errors).
- **Existing Functionality**: Preserves `process_message`, `get_conversation_history`, and pub/sub from **Step 2**.

This setup provides a unified observability solution, combining traces, metrics, and logs for comprehensive monitoring.

### 6. Observe the Dapr Dashboard

Run:
```bash
dapr dashboard
```

Check the **Actors** tab for `ChatAgent` instances (e.g., `2` for `user1`, `user2`). Use Jaeger, and Prometheus to monitor traces, metrics, and logs, complementing the dashboard’s actor counts.

## Validation

Verify observability functionality:
1. **Message Processing**: POST to `/chat/user1` and `/chat/user2` succeeds.
2. **History Retrieval**: GET `/chat/user1/history` shows the correct history.
3. **Tracing**: In Jaeger, search for `chat-agent` and confirm traces for `process_message`, `get_conversation_history`, and Redis operations (e.g., `get_state`, `set_state`).
4. **Metrics**: In Prometheus, query `dapr_actor_invocations_total{actor_type="ChatAgent"}` and `dapr_state_latency_seconds{component="statestore"}` to confirm increasing invocation counts and state store latencies.

## Troubleshooting

- **No Traces in Jaeger**:
  - Verify `observability.yaml` has `endpoint: "jaeger:4317"`.
  - Check Jaeger pod status (`kubectl get pods`).
  - Ensure `samplingRate: "1"` for full tracing.
- **No Metrics in Prometheus**:
  - Confirm `prometheus.yaml` targets `chat-agent-dapr:3500`.
  - Check Prometheus pod status and config (`kubectl get configmaps prometheus-config -o yaml`).
  **Requests Not Traced/Logged**:
  - Verify Dapr sidecar is running (`kubectl get pods`).
  - Check `components/observability.yaml` and deployment annotations.

## Key Takeaways

- **Comprehensive Observability**: Tracing, metrics, and logging provide a holistic view of actor performance and application behavior.
- **Lightweight Configuration**: Dapr’s OpenTelemetry and JSON logging, combined with Jaeger, and Prometheus require minimal changes.
- **Production-Readiness**: Enables monitoring, debugging, and optimization for scalable AI agents.
- **DACA Alignment**: Supports reliable, observable systems for conversational AI, addressing agent-centric observability needs (Appendix VI).

## Next Steps

- Proceed to **Step 6: State Encryption** to secure conversation history.
- Experiment with additional observability features:
  - Add custom metrics (e.g., pub/sub latency) in Prometheus.
  - Integrate Grafana for visualized traces and metrics.

## Resources

- [Dapr Observability](https://docs.dapr.io/operations/observability/)
- [Dapr OpenTelemetry](https://docs.dapr.io/operations/observability/telemetry/)
- [Dapr Logging](https://docs.dapr.io/operations/observability/logging/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Labs Starter Code](https://github.com/panaversity/learn-agentic-ai/tree/main/05_daca_agent_native_dev/05_agent_actors/00_lab_starter_code)