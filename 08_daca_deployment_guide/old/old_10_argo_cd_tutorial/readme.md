# Tutorial: Getting Started with Argo CD on Kubernetes

Below is a detailed tutorial on **Argo CD**, a declarative, GitOps continuous delivery (CD) tool for Kubernetes. This tutorial covers installation, configuration, deploying an application, monitoring, and managing it using Argo CD. I’ll provide step-by-step instructions with examples, assuming a beginner-to-intermediate audience familiar with Kubernetes basics.

---

## What is Argo CD?

Argo CD is an open-source tool that automates the deployment and management of applications on Kubernetes using the GitOps methodology. In GitOps, your Git repository serves as the single source of truth for your application’s desired state, and Argo CD ensures your Kubernetes cluster matches that state by continuously reconciling differences.

### Key Features
- **Declarative Configuration**: Define your application state in Git using YAML, Helm, or Kustomize.
- **Automated Syncing**: Automatically applies changes from Git to your cluster.
- **Drift Detection**: Monitors and corrects deviations between the live cluster state and Git.
- **Web UI and CLI**: Offers both a graphical interface and command-line tools.
- **Multi-Cluster Support**: Manages applications across multiple Kubernetes clusters.

This tutorial will guide you through setting up Argo CD, deploying a sample application, and exploring its core functionalities.

---

## Prerequisites

- A Kubernetes cluster (e.g., Minikube, Kind, or a cloud provider like GKE/EKS). For this tutorial, I’ll use Minikube.
- `kubectl` installed and configured to access your cluster.
- Helm 3 installed (optional, for Helm-based installation).
- Git installed locally and access to a Git repository (e.g., GitHub).
- Basic understanding of Kubernetes resources (pods, deployments, services).

---

## Step 1: Install Argo CD

Argo CD can be installed using raw YAML manifests or Helm. We’ll use the YAML method for simplicity, then explore Helm later.

### Install Argo CD with YAML
1. **Create a Namespace**:
   Argo CD runs in its own namespace, typically `argocd`.
   ```bash
   kubectl create namespace argocd
   ```

2. **Apply the Installation Manifest**:
   Download and apply the official manifests from the Argo CD GitHub repository:
   ```bash
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```
   This deploys:
   - The Argo CD API server.
   - Application controller.
   - Repository server.
   - Redis for caching.
   - RBAC and CRDs.

3. **Verify Installation**:
   Check the pods in the `argocd` namespace:
   ```bash
   kubectl get pods -n argocd
   ```
   You should see pods like:
   - `argocd-server-xxxxx`
   - `argocd-application-controller-xxxxx`
   - `argocd-repo-server-xxxxx`
   - `argocd-redis-xxxxx`

### Install the Argo CD CLI
The CLI enhances interaction with Argo CD. Install it based on your OS:
- **macOS (via Homebrew)**:
  ```bash
  brew install argocd
  ```
- **Linux/Windows**:
  Download the binary from the [releases page](https://github.com/argoproj/argo-cd/releases) and add it to your PATH:
  ```bash
  curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
  chmod +x argocd
  sudo mv argocd /usr/local/bin/
  ```

Verify:
```bash
argocd version --client
```

---

## Step 2: Access the Argo CD Web UI

By default, the Argo CD API server isn’t exposed externally. Use port-forwarding to access it locally.

1. **Port-Forward the Server**:
   ```bash
   kubectl port-forward svc/argocd-server -n argocd 8080:443
   ```

2. **Get the Admin Password**:
   Argo CD generates an initial admin password stored in a secret:
   ```bash
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```
   Copy the output (e.g., `abcd1234`).

3. **Log In to the Web UI**:
   Open your browser to `https://localhost:8080`. Accept the self-signed certificate warning (it’s safe for local use).
   - Username: `admin`
   - Password: The value from the previous step.

   You’ll see the Argo CD dashboard, which is empty until we add applications.

4. **Log In via CLI** (Optional):
   ```bash
   argocd login localhost:8080 --username admin --password <your-password> --insecure
   ```

---

## Step 3: Deploy a Sample Application

We’ll deploy a simple Nginx application from a Git repository using Argo CD.

### Prepare the Git Repository
1. **Create a Repository**:
   Use an existing GitHub repository or create a new one. For this tutorial, we’ll use a public example repo: `https://github.com/argoproj/argocd-example-apps.git`.

   The `guestbook` directory in this repo contains a basic Nginx deployment:
   - `deployment.yaml`
   - `service.yaml`

2. **Inspect the Manifests** (Optional):
   Clone the repo locally to explore:
   ```bash
   git clone https://github.com/argoproj/argocd-example-apps.git
   cd argocd-example-apps/guestbook
   ```
   - `deployment.yaml`: Defines an Nginx deployment with 2 replicas.
   - `service.yaml`: Exposes Nginx on port 80.

### Define the Application in Argo CD
1. **Create an Application**:
   Use the CLI to define an application that syncs the `guestbook` manifests to your cluster:
   ```bash
   argocd app create guestbook \
     --repo https://github.com/argoproj/argocd-example-apps.git \
     --path guestbook \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace default
   ```
   - `--repo`: Git repository URL.
   - `--path`: Directory containing manifests.
   - `--dest-server`: Kubernetes API server (default for the local cluster).
   - `--dest-namespace`: Target namespace.

2. **Sync the Application**:
   Manually trigger the sync to deploy the app:
   ```bash
   argocd app sync guestbook
   ```

3. **Verify Deployment**:
   Check the resources in the `default` namespace:
   ```bash
   kubectl get pods,svc -n default
   ```
   You’ll see an Nginx deployment and service running.

4. **View in the Web UI**:
   Refresh `https://localhost:8080`. The `guestbook` app appears as a tile. Click it to see a visual representation of the deployment and service, including sync status and health.

---

## Step 4: Automate Syncing and Self-Healing

Argo CD can automatically sync changes and correct drift.

### Enable Auto-Sync
1. **Update the Application**:
   Edit the `guestbook` app to enable auto-sync:
   ```bash
   argocd app set guestbook --sync-policy automated
   ```
   - `automated`: Syncs whenever Git changes are detected.
   Add pruning and self-healing:
   ```bash
   argocd app set guestbook --auto-prune --self-heal
   ```
   - `--auto-prune`: Deletes resources no longer in Git.
   - `--self-heal`: Reverts manual changes to match Git.

2. **Test Auto-Sync**:
   Fork the `argocd-example-apps` repo, modify `guestbook/deployment.yaml` (e.g., change `replicas: 2` to `replicas: 3`), and push the change. Update the app to use your fork:
   ```bash
   argocd app set guestbook --repo <your-fork-url>
   ```
   Wait a minute—Argo CD will detect the change and update the cluster automatically.

3. **Test Self-Healing**:
   Manually scale the deployment:
   ```bash
   kubectl scale deployment guestbook -n default --replicas=5
   ```
   Argo CD will revert it to 3 within moments due to self-healing.

---

## Step 5: Use Helm with Argo CD (Optional)

Argo CD supports Helm Charts for templated deployments.

1. **Create a Helm Chart**:
   Use the `helm-guestbook` example from the same repo:
   ```bash
   argocd app create helm-guestbook \
     --repo https://github.com/argoproj/argocd-example-apps.git \
     --path helm-guestbook \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace default \
     --helm-set replicaCount=2
   ```

2. **Sync the Helm App**:
   ```bash
   argocd app sync helm-guestbook
   ```

3. **Verify**:
   ```bash
   kubectl get pods -n default -l app=helm-guestbook
   ```

---

## Step 6: Monitor and Manage

### Web UI Features
- **Sync Status**: Green (in sync) or yellow (out of sync).
- **History and Rollback**: Click “History and Rollback” to view past syncs and revert to a previous state.
- **Logs**: View pod logs directly in the UI.

### CLI Commands
- List apps:
  ```bash
  argocd app list
  ```
- Get app details:
  ```bash
  argocd app get guestbook
  ```
- Delete an app:
  ```bash
  argocd app delete guestbook
  ```

---

## Step 7: Clean Up

1. **Remove the Application**:
   ```bash
   argocd app delete guestbook
   argocd app delete helm-guestbook
   ```

2. **Uninstall Argo CD**:
   ```bash
   kubectl delete -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   kubectl delete namespace argocd
   ```

---

## Conclusion

In this tutorial, you’ve installed Argo CD, deployed a sample Nginx application using GitOps, enabled automation, and explored Helm integration. Argo CD simplifies Kubernetes deployments by keeping your cluster in sync with Git, offering visibility through its UI, and automating operational tasks. You can extend this setup by:
- Managing multiple clusters.
- Integrating with CI tools (e.g., GitHub Actions).
- Adding RBAC for team access.

---

## Argo CD and Dapr (Distributed Application Runtime)

Argo CD and Dapr (Distributed Application Runtime) are two distinct tools in the cloud-native ecosystem that serve different purposes but can be powerfully combined to streamline the development, deployment, and runtime management of microservices-based applications, including AI agents in "agentic microservices." Below, I’ll explain their individual roles, how they connect, and how they can work together, with a focus on their relevance to deploying and managing distributed systems.

---

## Overview of Argo CD and Dapr

### Argo CD
- **What it is**: A declarative, GitOps continuous delivery (CD) tool for Kubernetes.
- **Focus**: Automates the deployment and lifecycle management of applications by synchronizing Kubernetes resources with manifests stored in a Git repository.
- **How it works**: Runs as a controller in the Kubernetes cluster, continuously reconciling the live cluster state with the desired state defined in Git, supporting YAML, Helm, Kustomize, and more.
- **Layer**: Operates at the **deployment and orchestration layer**, managing infrastructure and application manifests.

### Dapr
- **What it is**: A runtime that simplifies building distributed applications by providing standardized building blocks for microservices patterns.
- **Focus**: Application-level features like service invocation, state management, pub/sub messaging, secret management, and actor models, abstracting these from the application code.
- **How it works**: Deploys as a sidecar alongside each microservice, offering an HTTP/gRPC API that applications use to interact with distributed system components (e.g., databases, message brokers).
- **Layer**: Operates at the **application runtime layer**, enhancing microservices functionality.

---

## How Argo CD and Dapr Are Connected

Argo CD and Dapr are not directly dependent on each other—they address different aspects of the microservices lifecycle—but they complement each other in a GitOps-driven workflow:

1. **Deployment vs. Runtime**:
   - **Argo CD**: Handles the "how" and "where" of deployment, ensuring microservices (including those using Dapr) are deployed to Kubernetes according to Git-defined manifests.
   - **Dapr**: Handles the "what" and "how" of runtime behavior, providing capabilities like service-to-service communication and state persistence once the application is running.

2. **Sidecar Integration**:
   - Argo CD deploys applications with Dapr sidecars by including Dapr annotations in the Kubernetes manifests stored in Git.
   - Dapr’s sidecar is then injected into the pods during deployment, managed by Argo CD’s sync process.

3. **GitOps Workflow**:
   - Argo CD uses Git as the single source of truth for application configuration, including Dapr-specific settings (e.g., component definitions for pub/sub or state stores).
   - Changes to Dapr configurations in Git (e.g., switching from Redis to Cosmos DB) are automatically applied by Argo CD, ensuring consistency.

4. **Ecosystem Alignment**:
   - Both are cloud-native tools designed for Kubernetes, with Argo CD being part of the Argo project (a CNCF incubating project) and Dapr also a CNCF incubating project (as of April 2025). Their shared focus on microservices and Kubernetes fosters interoperability.

---

## How Argo CD and Dapr Work Together

When combined, Argo CD and Dapr create a seamless pipeline from deployment to runtime:
- **Argo CD**: Deploys the application and Dapr sidecars, ensuring the cluster matches the Git repository.
- **Dapr**: Enhances the deployed application with distributed system capabilities, such as communication between microservices or state management.

### Integration Mechanics
1. **Manifests in Git**:
   - Argo CD manages Kubernetes manifests that include Dapr annotations (e.g., `dapr.io/enabled: "true"`, `dapr.io/app-id`).
   - Dapr components (e.g., pub/sub brokers, state stores) are also defined as Kubernetes resources in Git, deployed by Argo CD.

2. **Deployment Process**:
   - Argo CD syncs the manifests, deploying the application pods with Dapr sidecars injected by the Dapr runtime.
   - Dapr’s sidecars then handle runtime interactions, such as calling another service or publishing a message.

3. **Configuration Updates**:
   - Changes to Dapr configurations (e.g., updating a pub/sub component) are committed to Git, and Argo CD applies them to the cluster automatically.

4. **Monitoring and Rollback**:
   - Argo CD provides visibility into deployment status and supports rollbacks if a Dapr-enabled deployment fails.
   - Dapr’s telemetry (integrated with tools like Prometheus) complements Argo CD’s deployment health checks.

### Example Workflow
- **Scenario**: Deploying two FastAPI-based AI agents (Recommendation Agent and Data Agent) with Dapr for communication and Argo CD for deployment.
- **Argo CD**: Deploys the agents and Dapr sidecars from Git manifests.
- **Dapr**: Enables Agent A to invoke Agent B or subscribe to data updates from Agent B via pub/sub.

---

## Use Cases in AI Agents and Agentic Microservices

In the context of "agentic microservices"—microservices hosting AI agents—Argo CD and Dapr together streamline deployment and runtime management, particularly for agent-to-agent communication.

### Example Setup
- **Agent A (Recommendation Agent)**: A FastAPI app using Dapr for service invocation to query Agent B.
- **Agent B (Data Agent)**: A FastAPI app using Dapr’s pub/sub to publish processed data.

#### How They Complement Each Other
1. **Deployment Automation**:
   - **Argo CD**: Deploys both agents and their Dapr sidecars, ensuring consistent rollouts and rollbacks from Git.
   - **Dapr**: Provides runtime features like service invocation (`/invoke`) or pub/sub for agent communication.

2. **Agent Communication**:
   - **Dapr**: Simplifies Agent A calling Agent B (e.g., `http://localhost:3500 Bosnia and Herzegovina/v1.0/invoke/data/method/get_data`) or subscribing to Agent B’s data updates.
   - **Argo CD**: Ensures the Dapr components (e.g., Redis pub/sub) are deployed and updated as defined in Git.

3. **Scalability and Updates**:
   - **Argo CD**: Scales agent replicas or updates models by syncing Git changes (e.g., increasing `replicas` or updating image tags).
   - **Dapr**: Manages load distribution and communication between scaled instances.

4. **Consistency**:
   - **Argo CD**: Maintains a single source of truth in Git, including Dapr configurations, preventing drift.
   - **Dapr**: Abstracts infrastructure details (e.g., switching message brokers), with Argo CD applying these changes.

#### Practical Benefits for AI Agents
- **Rapid Deployment**: Argo CD automates deploying AI agents with Dapr, speeding up experimentation with new models.
- **Reliable Communication**: Dapr’s service invocation and pub/sub ensure agents interact seamlessly, while Argo CD keeps the setup consistent.
- **Version Control**: Argo CD’s GitOps approach tracks agent versions and Dapr configurations, enabling rollbacks if an update fails.
- **Distributed Coordination**: Dapr’s actor model or state management supports complex agent workflows, deployed via Argo CD.

---

## Practical Example: Argo CD + Dapr with FastAPI Agents

### Setup
1. **Install Dapr**:
   Initialize Dapr in your cluster:
   ```bash
   dapr init -k
   ```
   Verify:
   ```bash
   kubectl get pods -n dapr-system
   ```

2. **Install Argo CD**:
   Deploy Argo CD:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

3. **Create a Git Repository**:
   - Create a repo (e.g., on GitHub) with the following structure:
     ```
     my-agents/
     ├── recommendation.yaml
     ├── data.yaml
     └── components/
         └── redis-pubsub.yaml
     ```

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

   - **Dapr Component (Redis Pub/Sub)**:
     ```yaml
     # components/redis-pubsub.yaml
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

4. **Configure Argo CD Application**:
   ```bash
   argocd app create agents \
     --repo https://github.com/your-username/my-agents.git \
     --path . \
     --dest-server https://kubernetes.default.svc \
     --dest-namespace default \
     --sync-policy automated \
     --auto-prune \
     --self-heal
   ```

5. **Sync the Application**:
   ```bash
   argocd app sync agents
   ```

6. **Test**:
   ```bash
   kubectl port-forward svc/recommendation 8000:8000
   ```
   Open `http://localhost:8000/recommend`—Agent A calls Agent B via Dapr, deployed by Argo CD.

---

## Conclusion

Argo CD and Dapr are connected through their complementary roles: Argo CD automates deployment and lifecycle management from Git, while Dapr enhances runtime capabilities for distributed applications. Together, they provide a robust solution for AI agents in agentic microservices, with Argo CD ensuring consistent deployments and Dapr enabling seamless agent-to-agent communication. This integration supports rapid iteration, scalability, and reliability for FastAPI-based AI systems.


