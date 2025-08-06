# Tutorial: Monitoring Kubernetes with the Prometheus Operator

Below is a detailed tutorial on using the Prometheus Operator with Kubernetes to set up and manage monitoring for your cluster and applications. This tutorial builds on the concept of Kubernetes Operators, focusing specifically on the Prometheus Operator, a prebuilt Operator for deploying and managing Prometheus instances. I’ll cover installation, configuration, monitoring applications, and visualization with Grafana, using practical examples.

---

## Overview
The Prometheus Operator simplifies the deployment and management of Prometheus, a powerful time-series monitoring system, on Kubernetes. It uses Custom Resource Definitions (CRDs) to define Prometheus instances, service monitors, and alerting rules, automating tasks like scaling, configuration, and discovery.

### What You’ll Learn
- How to install the Prometheus Operator.
- How to deploy a Prometheus instance using its Custom Resources.
- How to monitor Kubernetes cluster components and custom applications.
- How to set up alerting and visualize metrics with Grafana.

### Prerequisites
- A Kubernetes cluster (e.g., Minikube, GKE, EKS).
- `kubectl` installed and configured.
- Helm 3 installed (optional, but recommended for easier deployment).
- Basic familiarity with Kubernetes and YAML.

---

## Step 1: Install the Prometheus Operator

The Prometheus Operator is typically installed as part of the `kube-prometheus-stack` Helm Chart, which includes Prometheus, the Operator, Grafana, and additional tools. This is the recommended approach for a full monitoring stack.

### Using Helm
1. **Add the Helm Repository**:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update
   ```

2. **Install the Prometheus Operator**:
   Create a namespace for monitoring:
   ```bash
   kubectl create namespace monitoring
   ```
   Install the stack:
   ```bash
   helm install prometheus-stack prometheus-community/kube-prometheus-stack --namespace monitoring
   ```
   This deploys:
   - The Prometheus Operator (manages Prometheus instances).
   - A default Prometheus instance.
   - Grafana for visualization.
   - Alertmanager for alerting.

3. **Verify Installation**:
   Check the pods:
   ```bash
   kubectl get pods -n monitoring
   ```
   You should see pods like:
   - `prometheus-stack-kube-prom-operator-xxxxx` (the Operator).
   - `prometheus-prometheus-stack-kube-prom-prometheus-0` (Prometheus instance).
   - `prometheus-stack-grafana-xxxxx` (Grafana).

### Alternative: Raw YAML
If you prefer not to use Helm, apply the raw manifests:
```bash
curl -sL https://github.com/prometheus-operator/prometheus-operator/releases/latest/download/bundle.yaml | kubectl apply -f -
```
Then deploy additional components manually (Prometheus, Grafana, etc.), but Helm is simpler for a full stack.

---

## Step 2: Deploy a Prometheus Instance

The Prometheus Operator uses a `Prometheus` Custom Resource (CR) to define Prometheus instances. The Helm chart already deploys a default instance, but let’s create a custom one to understand the process.

### Create a Prometheus CR
1. Create a file named `custom-prometheus.yaml`:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: Prometheus
   metadata:
     name: custom-prometheus
     namespace: monitoring
   spec:
     replicas: 2
     resources:
       requests:
         memory: "400Mi"
         cpu: "200m"
       limits:
         memory: "800Mi"
     serviceMonitorSelector:
       matchLabels:
         app: monitored-app
     ruleSelector:
       matchLabels:
         role: prometheus-rules
     storage:
       volumeClaimTemplate:
         spec:
           storageClassName: standard
           resources:
             requests:
               storage: 8Gi
   ```
   - `replicas`: Runs 2 Prometheus pods for high availability.
   - `serviceMonitorSelector`: Specifies which `ServiceMonitor` resources this instance will use.
   - `storage`: Configures persistent storage for metrics.

2. Apply it:
   ```bash
   kubectl apply -f custom-prometheus.yaml
   ```

3. Verify:
   ```bash
   kubectl get prometheus -n monitoring
   kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus
   ```
   Look for pods like `custom-prometheus-0` and `custom-prometheus-1`.

The Operator will create the Prometheus pods, a service, and manage their lifecycle.

---

## Step 3: Monitor Kubernetes Cluster Components

The `kube-prometheus-stack` Helm chart automatically monitors cluster components (e.g., nodes, pods, kubelets) using predefined `ServiceMonitor` and `PodMonitor` resources. Let’s explore how this works and customize it.

### Default Monitoring
The chart includes:
- **ServiceMonitors** for Kubernetes components (e.g., `kube-apiserver`, `kube-scheduler`).
- A `Prometheus` instance configured to scrape these endpoints.

Check existing ServiceMonitors:
```bash
kubectl get servicemonitor -n monitoring
```

### Customize Cluster Monitoring
To adjust what’s monitored, modify the Helm values. Create a `values.yaml`:
```yaml
prometheus:
  prometheusSpec:
    additionalScrapeConfigs:
      - job_name: "extra-kube-component"
        static_configs:
          - targets: ["kube-controller-manager:10252"]
```
Upgrade the release:
```bash
helm upgrade prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring -f values.yaml
```

---

## Step 4: Monitor a Custom Application

To monitor your own application, define a `ServiceMonitor` to tell Prometheus where to scrape metrics.

### Example Application
Deploy a simple app that exposes metrics (e.g., an Nginx server with a metrics endpoint):
```yaml
# app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-app
  template:
    metadata:
      labels:
        app: nginx-app
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-app-service
  namespace: default
spec:
  selector:
    app: nginx-app
  ports:
  - port: 80
    targetPort: 80
    name: http
```
Apply it:
```bash
kubectl apply -f app.yaml
```

### Create a ServiceMonitor
1. Create `nginx-servicemonitor.yaml`:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: ServiceMonitor
   metadata:
     name: nginx-app-monitor
     namespace: monitoring
     labels:
       app: monitored-app
   spec:
     selector:
       matchLabels:
         app: nginx-app
     endpoints:
     - port: http
       path: /metrics
   ```
   - `selector`: Matches the service’s labels.
   - `endpoints`: Specifies the port and path for metrics (Note: Nginx doesn’t expose `/metrics` by default; this is an example. For real metrics, use an app like a Python Flask app with Prometheus client libraries).

2. Apply it:
   ```bash
   kubectl apply -f nginx-servicemonitor.yaml
   ```

3. Verify:
   The `custom-prometheus` instance (from Step 2) will scrape this endpoint because its `serviceMonitorSelector` matches the `app: monitored-app` label.

---

## Step 5: Set Up Alerting

The Prometheus Operator supports alerting via the `PrometheusRule` CR.

### Create an Alert Rule
1. Create `alert-rules.yaml`:
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: PrometheusRule
   metadata:
     name: custom-alerts
     namespace: monitoring
     labels:
       role: prometheus-rules
   spec:
     groups:
     - name: example
       rules:
       - alert: HighPodMemory
         expr: sum(rate(container_memory_usage_bytes[5m])) by (pod) > 100000000
         for: 5m
         labels:
           severity: warning
         annotations:
           summary: "High memory usage detected in pod {{ $labels.pod }}"
           description: "Pod {{ $labels.pod }} has been using >100MB memory for 5 minutes."
   ```
   - `expr`: Defines the condition (memory usage > 100MB).
   - `for`: Waits 5 minutes before firing the alert.

2. Apply it:
   ```bash
   kubectl apply -f alert-rules.yaml
   ```

3. The `custom-prometheus` instance will load this rule because its `ruleSelector` matches `role: prometheus-rules`.

### Configure Alertmanager
The Helm chart includes Alertmanager. Access it:
```bash
kubectl port-forward -n monitoring svc/prometheus-stack-kube-prom-alertmanager 9093:9093
```
Open `http://localhost:9093` to view alerts.

---

## Step 6: Visualize with Grafana

The Helm chart deploys Grafana with preconfigured dashboards.

1. **Access Grafana**:
   ```bash
   kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80
   ```
   Open `http://localhost:3000`.

2. **Log In**:
   - Username: `admin`
   - Password: Get it with:
     ```bash
     kubectl get secret -n monitoring prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
     ```

3. **Explore Dashboards**:
   Grafana includes dashboards for Kubernetes cluster metrics (e.g., nodes, pods). Add a custom dashboard for your app by importing a JSON file or creating one manually using Prometheus queries (e.g., `rate(http_requests_total[5m])`).

---

## Step 7: Clean Up (Optional)

Uninstall the stack:
```bash
helm uninstall prometheus-stack -n monitoring
kubectl delete namespace monitoring
```

---

## Conclusion

This tutorial walked you through setting up the Prometheus Operator on Kubernetes using Helm, deploying a custom Prometheus instance, monitoring cluster components and applications, setting up alerts, and visualizing data with Grafana. The Operator automates Prometheus management, making it scalable and maintainable. You can extend this setup by adding more `ServiceMonitors`, `PrometheusRules`, or integrating with external systems.


---

## Prometheus and Dapr (Distributed Application Runtime)

Prometheus and Dapr (Distributed Application Runtime) are two cloud-native tools that serve distinct but complementary purposes in a microservices ecosystem, particularly within Kubernetes. While they don’t have a direct dependency, they can be integrated to provide comprehensive monitoring and observability for applications leveraging Dapr’s runtime capabilities. Below, I’ll explain their individual roles, how they connect, and how they work together, with a focus on their relevance to monitoring AI agents in "agentic microservices."

---

## Overview of Prometheus and Dapr

### Prometheus
- **What it is**: An open-source monitoring and alerting toolkit designed for time-series data.
- **Focus**: Collects, stores, and queries metrics from applications and infrastructure, providing visibility into system performance and health.
- **How it works**: Scrapes metrics from HTTP endpoints exposed by targets (e.g., applications, services), stores them in a time-series database, and supports querying via PromQL. It’s often paired with Grafana for visualization and Alertmanager for notifications.
- **Layer**: Operates at the **monitoring and observability layer**, focusing on metrics collection and analysis.

### Dapr
- **What it is**: A runtime that simplifies building distributed applications by offering standardized building blocks for microservices patterns.
- **Focus**: Application-level features like service invocation, state management, pub/sub messaging, secret management, and actors, abstracting these from the application code.
- **How it works**: Runs as a sidecar alongside each microservice, providing an HTTP/gRPC API that applications use to interact with distributed system components (e.g., message brokers, databases).
- **Layer**: Operates at the **application runtime layer**, enhancing microservices functionality.

---

## How Prometheus and Dapr Are Connected

Prometheus and Dapr are not inherently dependent on each other, but they connect through their shared goal of supporting microservices in Kubernetes:

1. **Metrics Exposure**:
   - **Dapr**: Exposes built-in telemetry, including metrics, via its sidecar. These metrics cover runtime operations like service invocation, pub/sub events, and actor interactions.
   - **Prometheus**: Scrapes these metrics from Dapr’s sidecar endpoints, enabling monitoring of Dapr-enabled applications.

2. **Observability**:
   - **Dapr**: Provides application-level telemetry (e.g., request latency, error rates) that complements infrastructure-level metrics.
   - **Prometheus**: Aggregates and stores these metrics, offering a unified view of both application and Dapr runtime performance.

3. **Kubernetes Integration**:
   - Both are designed for Kubernetes, where Prometheus can monitor the cluster (e.g., nodes, pods) and Dapr’s sidecars, while Dapr enhances application behavior within those pods.

4. **Ecosystem Alignment**:
   - Prometheus is a graduated CNCF project, and Dapr is a CNCF incubating project (as of April 2025). Their cloud-native focus ensures compatibility and integration via standard protocols like HTTP and OpenTelemetry.

---

## How Prometheus and Dapr Work Together

When integrated, Prometheus and Dapr provide a robust observability solution:
- **Dapr**: Generates and exposes metrics about its runtime operations and application interactions.
- **Prometheus**: Collects, stores, and analyzes these metrics, enabling monitoring, alerting, and visualization.

### Integration Mechanics
1. **Dapr Metrics Endpoint**:
   - Dapr’s sidecar exposes metrics at `http://localhost:9090/metrics` (default port configurable) in Prometheus format.
   - Metrics include:
     - `dapr_runtime_service_invocation_req_sent_total`: Total requests sent via service invocation.
     - `dapr_runtime_pubsub_event_published_total`: Total events published via pub/sub.
     - `dapr_runtime_state_store_operations_total`: State store operation counts.

2. **Prometheus Scraping**:
   - Prometheus is configured to scrape Dapr’s metrics endpoint from each pod’s sidecar.
   - A `ServiceMonitor` or `PodMonitor` (used with the Prometheus Operator) targets Dapr-enabled services.

3. **Visualization and Alerting**:
   - Prometheus feeds Dapr metrics to Grafana for dashboards or Alertmanager for notifications (e.g., alert on high latency in service invocation).

4. **Correlation with Application Metrics**:
   - Applications (e.g., FastAPI apps) can expose custom metrics, which Prometheus scrapes alongside Dapr’s metrics, providing a holistic view.

### Example Workflow
- **Scenario**: Two FastAPI-based AI agents (Recommendation Agent and Data Agent) using Dapr for communication.
- **Dapr**: Facilitates service invocation (Agent A calls Agent B) and exposes metrics on request latency and success rates.
- **Prometheus**: Scrapes these metrics, monitors performance, and triggers alerts if thresholds are exceeded.

---

## Use Cases in AI Agents and Agentic Microservices

In "agentic microservices"—microservices hosting AI agents—Prometheus and Dapr together enhance observability, critical for managing distributed AI systems.

### Example Setup
- **Agent A (Recommendation Agent)**: A FastAPI app using Dapr to invoke Agent B or subscribe to data updates.
- **Agent B (Data Agent)**: A FastAPI app using Dapr’s pub/sub to publish processed data.

#### How They Complement Each Other
1. **Monitoring Agent Communication**:
   - **Dapr**: Handles service invocation (e.g., Agent A queries Agent B) and exposes metrics like request latency and error rates.
   - **Prometheus**: Collects these metrics, enabling you to monitor communication performance and detect issues (e.g., slow inference).

2. **Pub/Sub Observability**:
   - **Dapr**: Manages pub/sub (e.g., Agent B publishes data, Agent A subscribes) and tracks event counts and delivery times.
   - **Prometheus**: Scrapes these metrics, allowing you to ensure timely data exchange between agents.

3. **Performance Optimization**:
   - **Dapr**: Provides runtime telemetry (e.g., state store latency for caching model outputs).
   - **Prometheus**: Analyzes trends, helping optimize agent performance (e.g., reducing state access times).

4. **Alerting**:
   - **Dapr**: Exposes failure metrics (e.g., failed service invocations).
   - **Prometheus**: Triggers alerts (e.g., if Agent B fails repeatedly), ensuring rapid response to issues.

#### Practical Benefits for AI Agents
- **Real-Time Insights**: Prometheus monitors Dapr’s metrics, providing visibility into agent interactions (e.g., latency spikes during inference).
- **Reliability**: Alerts on Dapr failures (e.g., pub/sub delays) ensure agents remain operational.
- **Scalability**: Metrics help identify bottlenecks as agent replicas scale.
- **Debugging**: Correlating Dapr’s application-level metrics with Prometheus’s cluster-wide data pinpoints issues in agent workflows.

---

## Practical Example: Prometheus + Dapr with FastAPI Agents

### Setup
1. **Install Dapr**:
   ```bash
   dapr init -k
   ```
   Verify:
   ```bash
   kubectl get pods -n dapr-system
   ```

2. **Install Prometheus Operator**:
   Use the `kube-prometheus-stack` Helm chart:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update
   helm install prometheus-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
   ```

3. **Deploy FastAPI Agents with Dapr**:
   - **Recommendation Agent**:
     ```yaml
     # recommendation.yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: recommendation
     spec:
       replicas: 2
       selector:
         matchLabels:
           app: recommendation
       template:
         metadata:
           labels:
             app: recommendation
           annotations:
             dapr.io/enabled: "true"
             dapr.io/app-id: "recommendation"
             dapr.io/app-port: "8000"
         spec:
           containers:
           - name: recommendation
             image: my-recommendation-agent:latest
             ports:
             - containerPort: 8000
     ---
     apiVersion: v1
     kind: Service
     metadata:
       name: recommendation
     spec:
       selector:
         app: recommendation
       ports:
       - port: 8000
         targetPort: 8000
     ```
     ```python
     # recommendation/main.py
     from fastapi import FastAPI
     import httpx

     app = FastAPI()

     @app.get("/recommend")
     async def get_recommendation():
         async with httpx.AsyncClient() as client:
             response = await client.get("http://localhost:3500/v1.0/invoke/data/method/data")
             return {"recommendation": "Based on data", "data": response.json()}
     ```

   - **Data Agent**:
     ```yaml
     # data.yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: data
     spec:
       replicas: 2
       selector:
         matchLabels:
           app: data
       template:
         metadata:
           labels:
             app: data
           annotations:
             dapr.io/enabled: "true"
             dapr.io/app-id: "data"
             dapr.io/app-port: "8000"
         spec:
           containers:
           - name: data
             image: my-data-agent:latest
             ports:
             - containerPort: 8000
     ---
     apiVersion: v1
     kind: Service
     metadata:
       name: data
     spec:
       selector:
         app: data
       ports:
       - port: 8000
         targetPort: 8000
     ```
     ```python
     # data/main.py
     from fastapi import FastAPI

     app = FastAPI()

     @app.get("/data")
     async def get_data():
         return {"processed_data": "some_insights"}
     ```
     ```bash
     kubectl apply -f recommendation.yaml -f data.yaml
     ```

4. **Configure Prometheus to Scrape Dapr Metrics**:
   Create a `ServiceMonitor` for Dapr:
   ```yaml
   # dapr-servicemonitor.yaml
   apiVersion: monitoring.coreos.com/v1
   kind: ServiceMonitor
   metadata:
     name: dapr-metrics
     namespace: monitoring
     labels:
       release: prometheus-stack
   spec:
     selector:
       matchLabels:
         app: recommendation
     endpoints:
     - port: dapr-metrics
       path: /metrics
       targetPort: 9090
     - port: dapr-metrics
       path: /metrics
       targetPort: 9090
       relabelings:
       - sourceLabels: [__meta_kubernetes_pod_label_app]
         targetLabel: app
         replacement: data
   ```
   ```bash
   kubectl apply -f dapr-servicemonitor.yaml
   ```
   Note: Dapr’s metrics port (9090) must be exposed in the pod, which requires a custom Dapr configuration if not already enabled.

5. **Verify Metrics**:
   Access Prometheus:
   ```bash
   kubectl port-forward -n monitoring svc/prometheus-stack-kube-prom-prometheus 9090:9090
   ```
   Open `http://localhost:9090` and query `dapr_runtime_service_invocation_req_sent_total` to see metrics from the agents.

6. **Visualize in Grafana**:
   ```bash
   kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80
   ```
   Log in (default: `admin`/`prom-operator`) and create a dashboard for Dapr metrics.

---

## Conclusion

Prometheus and Dapr are connected through their roles in observability: Dapr exposes application-level metrics from its runtime, and Prometheus collects and analyzes them alongside cluster metrics. For AI agents in agentic microservices, this integration provides deep visibility into agent interactions (e.g., service invocation, pub/sub), enabling performance monitoring, alerting, and optimization. With FastAPI-based agents, Prometheus and Dapr together ensure reliable, observable AI workflows.



