# Deploying DACA to Civo Kubernetes

Welcome to the twenty-first tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll continue our journey toward **Planet-Scale** by deploying the `chat_service`, `analytics_service`, and `review_ui` to a managed Kubernetes cluster on Civo, one of the most economical managed Kubernetes services available. We’ll start with a two-node cluster using Civo’s “Small” nodes ($10/month per node) and a $10/month load balancer, totaling $30/month. As our load increases, we’ll scale the cluster to handle planetary-scale traffic with no API limits, leveraging Google Gemini to bypass OpenAI’s 10,000 RPM limit. We’ll also integrate Kafka for messaging, Kubernetes CronJobs for scheduling, Postgres and Redis on Kubernetes for storage, and Dapr for cluster-wide resilience. Let’s ascend to planet-scale on Civo Kubernetes!

---

## What You’ll Learn
- Setting up a managed Kubernetes cluster on Civo with 2 “Small” nodes ($30/month total, including a load balancer).
- Deploying the DACA application (`chat_service`, `analytics_service`, `review_ui`) to Civo Kubernetes.
- Configuring Kafka on Kubernetes for high-throughput messaging.
- Using Kubernetes CronJobs for scheduling tasks (e.g., resetting analytics data).
- Deploying Postgres and Redis on Kubernetes for database and in-memory storage.
- Enabling Dapr on Kubernetes for cluster-wide resilience.
- Scaling the cluster dynamically as load increases to achieve planetary scale with no API limits using Google Gemini.

## Prerequisites
- Completion of **20_daca_planet_scale_kubernetes_deployment_on_oracle** (Kubernetes deployment on Oracle Cloud).
- A Civo account with $250 free credit for new users (valid for the first month after adding a payment card).
- Basic familiarity with Kubernetes, Civo’s managed Kubernetes service, and the Civo CLI.
- Existing accounts for:
  - Google Gemini (for LLM API, replacing OpenAI to avoid API limits).
  - CloudAMQP RabbitMQ (we’ll transition to Kafka, but credentials may be reused for testing).
  - CockroachDB Serverless (we’ll transition to Postgres on Kubernetes).
  - Upstash Redis (we’ll transition to Redis on Kubernetes).
- Tools installed:
  - `kubectl` (Kubernetes CLI).
  - `civo` CLI (for managing Civo Kubernetes clusters).
  - `helm` (for installing Kafka, Postgres, Redis, and Dapr on Kubernetes).

---

## Step 1: Set Up a Managed Kubernetes Cluster on Civo
Civo Kubernetes is a managed service built on k3s, offering fast cluster creation (under 90 seconds) and economical pricing. We’ll start with a two-node cluster using “Small” nodes ($10/month per node) and a $10/month load balancer, totaling $30/month.

### Step 1.1: Sign Up for Civo and Install the Civo CLI
1. **Create a Civo Account**:
   - Sign up at [Civo](https://www.civo.com) to get $250 in free credit (valid for the first month after adding a payment card).
   - Add a payment card to your account to claim the credit.

2. **Install the Civo CLI**:
   - Follow the official instructions to install the Civo CLI:
     ```bash
     curl -sL https://civo.com/get | sh
     ```
   - Verify the installation:
     ```bash
     civo version
     ```

3. **Authenticate the CLI**:
   - Generate an API key in the Civo Dashboard under **Account > API Keys**.
   - Set the API key:
     ```bash
     civo apikey add my-key <your-api-key>
     civo apikey current my-key
     ```

### Step 1.2: Create a Two-Node Kubernetes Cluster
We’ll create a cluster with 2 “Small” nodes (1 vCPU, 2 GB RAM each) in the NYC1 region.

1. **List Available Node Sizes**:
   ```bash
   civo kubernetes size
   ```
   - Look for the “Small” size (`g4s.kube.small`), which is $10/month per node.

2. **Create the Cluster**:
   ```bash
   civo kubernetes create daca-cluster \
     --size g4s.kube.small \
     --nodes 2 \
     --region NYC1 \
     --merge \
     --save \
     --switch \
     --wait \
     --remove-applications=Traefik
   ```
   - This command:
     - Creates a cluster named `daca-cluster` with 2 “Small” nodes.
     - Uses the NYC1 region (Civo also supports other regions like SVG1; adjust as needed).
     - Merges the cluster’s kubeconfig with your local `~/.kube/config`.
     - Saves the config and switches the context to the new cluster.
     - Removes the default Traefik Ingress controller (we’ll use Nginx instead).
   - The cluster will be ready in under 90 seconds.

3. **Verify the Cluster**:
   ```bash
   kubectl get nodes
   ```
   Output:
   ```
   NAME                                   STATUS   ROLES    AGE   VERSION
   k3s-daca-cluster-node-pool-xxxx   Ready    <none>   2m    v1.28.8+k3s1
   k3s-daca-cluster-node-pool-yyyy   Ready    <none>   2m    v1.28.8+k3s1
   ```

### Step 1.3: Install Nginx Ingress Controller
Since we removed Traefik, we’ll install the Nginx Ingress Controller for external access.

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

2. **Get the Cluster’s Public IP**:
   - Civo assigns one public IP per cluster. Check the cluster details:
     ```bash
     civo kubernetes show daca-cluster
     ```
   - Look for the `Public IP` field (e.g., `<cluster-ip>`). We’ll use this to access services.

### Step 1.4: Add a Load Balancer
Civo charges $10/month for a load balancer, which we’ll add to distribute traffic.

1. **Create a Load Balancer Service**:
   - Create a file `loadbalancer.yaml`:
     ```yaml
     apiVersion: v1
     kind: Service
     metadata:
       name: ingress-nginx-controller
       namespace: ingress-nginx
       annotations:
         kubernetes.civo.com/max-concurrent-requests: "20000"
     spec:
       type: LoadBalancer
       selector:
         app.kubernetes.io/name: ingress-nginx
         app.kubernetes.io/component: controller
       ports:
       - protocol: TCP
         port: 80
         targetPort: 80
         name: http
       - protocol: TCP
         port: 443
         targetPort: 443
         name: https
     ```
   - Apply the configuration:
     ```bash
     kubectl apply -f loadbalancer.yaml
     ```
   - This creates a Civo Load Balancer ($10/month) that routes traffic to the Nginx Ingress controller, supporting up to 20,000 concurrent requests (default is 10,000, adjusted via the annotation).

2. **Get the Load Balancer’s Public IP**:
   ```bash
   kubectl get svc -n ingress-nginx ingress-nginx-controller
   ```
   - Note the `EXTERNAL-IP` (e.g., `<loadbalancer-ip>`). This will be used to access services.

---

## Step 2: Deploy Managed Services on Kubernetes
We’ll deploy Kafka, Postgres, and Redis on Kubernetes, transitioning from external managed services (CloudAMQP, CockroachDB, Upstash Redis) to self-managed services.

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
         replicas: 2
         listeners:
           - name: plain
             port: 9092
             type: internal
             tls: false
         config:
           offsets.topic.replication.factor: 2
           transaction.state.log.replication.factor: 2
           transaction.state.log.min.isr: 1
         storage:
           type: ephemeral
       zookeeper:
         replicas: 2
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
   - You should see 2 Kafka brokers and 2 ZooKeeper nodes running.

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

## Step 4: Deploy the DACA Application to Civo Kubernetes
We’ll reuse the `chat_service`, `analytics_service`, and `review_ui` from the previous tutorial, deploying them to Civo Kubernetes with Dapr annotations.

### Step 4.1: Build and Push Docker Images
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

### Step 4.2: Deploy `chat_service`
Create `chat-service-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chat-service
  namespace: default
spec:
  replicas: 2
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

### Step 4.3: Deploy `analytics_service`
Create `analytics-service-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-service
  namespace: default
spec:
  replicas: 2
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

### Step 4.4: Deploy `review_ui`
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

### Step 4.5: Set Up a Kubernetes CronJob for Scheduling
We’ll use a Kubernetes CronJob to reset analytics data daily.

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

## Step 5: Test the Civo Kubernetes Deployment
Let’s test the deployed application to ensure it’s ready for planetary scale.

### Step 5.1: Access the Services
- Update your local `/etc/hosts` file to map the Ingress hosts to the load balancer’s public IP:
  ```
  <loadbalancer-ip> chat.daca.local review.daca.local
  ```
- Access the chat service at `http://chat.daca.local/`.
- Access the review UI at `http://review.daca.local/`.

### Step 5.2: Initialize Analytics Data
Initialize message counts for `alice` and `bob`:
- For `alice`:
  ```bash
  curl -X POST http://chat.daca.local/analytics/alice/initialize -H "Content-Type: application/json" -d '{"message_count": 5}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "alice", "message_count": 5}
  ```
- For `bob`:
  ```bash
  curl -X POST http://chat.daca.local/analytics/bob/initialize -H "Content-Type: application/json" -d '{"message_count": 3}'
  ```
  Output:
  ```json
  {"status": "success", "user_id": "bob", "message_count": 3}
  ```

### Step 5.3: Send a Message Requiring Human Review
Send a message with a sensitive keyword:
```bash
curl -X POST http://chat.daca.local/chat/ -H "Content-Type: application/json" -d '{"user_id": "bob", "text": "This is an urgent request!", "metadata": {"timestamp": "2025-04-06T14:03:00Z", "session_id": "123e4567-e89b-12d3-a456-426614174001"}, "tags": ["greeting"]}'
```

The request will hang, waiting for human review.

### Step 5.4: Approve the Message in the Streamlit UI
Open the Streamlit UI at `http://review.daca.local/` and approve the message. The `curl` request should complete with a response like:
```json
{
  "user_id": "bob",
  "reply": "Hi Bob! You've sent 3 messages so far. No previous conversation. I understand your request is urgent—how can I assist you?",
  "metadata": {
    "timestamp": "2025-04-06T14:04:00Z",
    "session_id": "some-uuid"
  }
}
```

### Step 5.5: Simulate Load to Test Scalability
Use `ab` (Apache Benchmark) to simulate high load:
```bash
ab -n 10000 -c 1000 http://chat.daca.local/health
```
- **Expected Behavior**: The `chat_service` should handle the load, but the 2 “Small” nodes (1 vCPU, 2 GB RAM each) may struggle with high concurrency due to limited resources.

---

## Step 6: Scale the Cluster as Load Increases
The initial two-node cluster may not handle planetary-scale traffic. Let’s scale up by adding more nodes and upgrading to larger node sizes.

### Step 6.1: Scale the Node Pool
Increase the number of nodes in the existing node pool to 4:
```bash
civo kubernetes node-pool scale daca-cluster <pool-id> --nodes 4
```
- Replace `<pool-id>` with the node pool ID (find it using `civo kubernetes show daca-cluster`).
- This scales the cluster to 4 “Small” nodes ($40/month).

### Step 6.2: Add a New Node Pool with Larger Nodes
Add a new node pool with “Medium” nodes (2 vCPUs, 4 GB RAM, $20/month per node):
```bash
civo kubernetes node-pool create daca-cluster \
  --size g4s.kube.medium \
  --nodes 2
```
- This adds 2 “Medium” nodes ($40/month), bringing the total to 4 “Small” nodes + 2 “Medium” nodes ($80/month + $10 load balancer = $90/month).

### Step 6.3: Install the Cluster Autoscaler
Civo supports the cluster autoscaler to dynamically scale nodes based on load.

1. **Add the Cluster Autoscaler**:
   ```bash
   civo kubernetes applications add civo-cluster-autoscaler -c daca-cluster
   ```

2. **Configure Autoscaling**:
   - Edit the autoscaler configuration to set the minimum and maximum nodes:
     ```bash
     kubectl edit deployment cluster-autoscaler -n kube-system
     ```
   - Update the `--nodes` flag in the `args` section, e.g., `--nodes=2:10:node-pool-id` (replace `node-pool-id` with the ID of the “Medium” node pool).
   - Save and exit to apply the changes.

3. **Test Autoscaling**:
   - Increase the load again using `ab`:
     ```bash
     ab -n 50000 -c 5000 http://chat.daca.local/health
     ```
   - The autoscaler should add nodes to the “Medium” node pool (up to 10 nodes) based on resource usage.

---

## Step 7: Monitor Costs and Scalability
- **Initial Cost (2 “Small” Nodes)**: $10/node × 2 + $10 load balancer = $30/month.
- **After Scaling (4 “Small” + 2 “Medium” Nodes)**: $10/node × 4 + $20/node × 2 + $10 load balancer = $90/month.
- **With Autoscaling (Up to 10 “Medium” Nodes)**: $20/node × 10 + $10 load balancer = $210/month (maximum, assuming full scaling).
- **Google Gemini API**: ~$0.0005/1K tokens → ~$5/month for high usage (e.g., 10M tokens/month).
- **Kafka, Postgres, Redis**: Self-managed on Kubernetes, so no additional costs beyond the cluster nodes.

**Total Estimated Cost**: $30/month initially, scaling to ~$95–$215/month with increased load (including Gemini API usage).

**Scalability**: With the cluster autoscaler and “Medium” nodes, the cluster can handle tens of thousands of requests per minute, limited by the account quota (check your quota in the Civo Dashboard). Google Gemini ensures no API limits, enabling planetary scale.

---

## Step 8: Why Civo Kubernetes for Planet-Scale?
- **Economical Pricing**: Starting at $30/month for a two-node cluster with a load balancer, Civo is one of the most cost-effective managed Kubernetes services.
- **Fast Cluster Creation**: Clusters are ready in under 90 seconds, thanks to k3s.
- **Free Control Plane**: Civo doesn’t charge for the control plane, reducing costs.
- **Scalability**: Easily scale nodes and add larger node pools as load increases, with cluster autoscaler support.
- **Kafka on Kubernetes**: High-throughput messaging with a multi-broker setup.
- **Kubernetes CronJobs**: Built-in scheduling for tasks like resetting analytics data.
- **Postgres and Redis on Kubernetes**: Self-managed database and in-memory store, minimizing external service costs.
- **Dapr on Kubernetes**: Provides cluster-wide resilience, service discovery, and pub/sub via Kafka.
- **Google Gemini**: Removes API limits, enabling planetary scale.

---

## Step 9: Next Steps
You’ve successfully deployed the DACA application to Civo Kubernetes, starting with a $30/month cluster and scaling to handle planetary-scale traffic! In the next tutorial, we’ll explore advanced monitoring with Prometheus and Grafana, implement CI/CD with GitHub Actions, and optimize for even higher throughput.

### Optional Exercises
1. Enable the Cilium CNI on Civo for enhanced networking and observability (available under “Advanced options” during cluster creation).
2. Deploy Prometheus and Grafana to monitor the cluster and application metrics.
3. Set up persistent storage for Kafka, Postgres, and Redis using Longhorn (available in the Civo Marketplace).

---

## Conclusion
In this tutorial, we set up a managed Kubernetes cluster on Civo with 2 “Small” nodes for $30/month, deployed the DACA application with Kafka, Postgres, Redis, and Dapr, and scaled the cluster to handle planetary-scale traffic with no API limits using Google Gemini. The application now supports tens of thousands of requests per minute at a cost of $30–$215/month, depending on the scale. 