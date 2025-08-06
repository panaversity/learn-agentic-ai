# Hands-On Introduction to Kubernetes (Basics)

In this guide, we’ll dive into Kubernetes fundamentals, building on the containerization concepts from the previous steps ("Introduction to Containers and Rancher Desktop"). Here, we’ll explore Kubernetes architecture, core objects (pods, deployments, services, namespaces, configmaps, secrets), and basic networking, using Rancher Desktop’s local cluster. Through practical examples with the `daca-agent` app, you’ll learn to deploy, manage, and troubleshoot Kubernetes resources, setting the stage for Dapr integration in future tutorials. Let’s begin!

---

## What You’ll Learn

- Kubernetes architecture and its core components.
- Key Kubernetes objects: pods, deployments, services, namespaces, configmaps, and secrets.
- How to use `kubectl` to manage Kubernetes resources.
- Hands-on deployment of the `daca-agent` app in a local Kubernetes cluster.
- Basic networking and troubleshooting in Kubernetes.

## Prerequisites

- Completion of the previous tutorial ("Introduction to Containers and Kubernetes with Rancher Desktop").
- Rancher Desktop installed with Kubernetes enabled (k3s cluster running, `containerd` as the engine).
- Tools: `kubectl`, `nerdctl`, and a terminal.
- Basic command-line knowledge and familiarity with containers (images, Dockerfiles).
- Recommended: 8 GB RAM, 4 CPUs.

## Understanding Kubernetes

**Kubernetes** is an open-source platform for orchestrating containers, automating deployment, scaling, and management. In DACA, Kubernetes scales our agent microservices and aligns with options like Azure Container Apps (ACA) for serverless deployment.

### Why Kubernetes?

- **Orchestration**: Manages multiple containers (e.g., agent app, CockroachDB) across clusters.
- **Scaling**: Autoscales pods (container groups) based on demand.
- **Resilience**: Restarts failed containers, ensures high availability.
- **Deployment**: Simplifies rollouts to ACA/Kubernetes clusters.

### Key Concepts

- **Pod**: Smallest unit, runs one or more containers (e.g., agent app + Dapr sidecar).
- **Deployment**: Manages pod replicas, updates, and rollbacks.
- **Service**: Exposes pods via a stable network endpoint (e.g., `agent-app:8080`).
- **Cluster**: Nodes (machines) running Kubernetes, managed by a control plane.

**Analogy**: Kubernetes is an orchestra conductor, directing containers (musicians) to play in harmony.

---

### Quick Setup Recap

If you’ve completed the previous tutorial, your environment should be ready. Verify it:

```bash
kubectl get nodes
```

Expected output:

```
NAME                   STATUS   ROLES                  AGE   VERSION
lima-rancher-desktop   Ready    control-plane,master   1h    v1.32.3+k3s1
```

If not set up, refer to the previous tutorial’s Install Rancher Desktop for instructions.

---

## 1. Introduction

### Recap of Containerization

In the last tutorial, we learned:

- **Containers**: Lightweight units packaging apps and dependencies.
- **Images**: Immutable blueprints built from Dockerfiles.
- **Rancher Desktop**: Runs containers with `containerd` and provides a local Kubernetes cluster (k3s).

We containerized a `daca-agent` FastAPI app and deployed it to Kubernetes briefly. Now, we’ll focus on Kubernetes itself.

### What is Kubernetes?

Kubernetes (K8s) is an open-source platform for orchestrating containers. It automates deployment, scaling, and management of containerized applications across clusters of nodes. It, often shortened to K8s, does the heavy lifting of managing your containerized applications. At its core, Kubernetes is:

1.  **A Cluster:** It groups multiple machines (servers) together, pooling their resources like CPU and memory[cite: 156]. These machines are called **nodes**.
2.  **An Orchestrator:** It intelligently deploys and manages your applications across the cluster's nodes. It handles scaling, self-healing, updates, and more, often automatically once configured.

Think of Kubernetes like the conductor of an orchestra. Each musician (container/application piece) knows its part, but the conductor (Kubernetes) ensures they all play together harmoniously, start and stop at the right times, and adjust volume (scale) as needed.

#### Why Use Kubernetes?

- **Orchestration**: Manages multiple containers efficiently.
- **Scalability**: Scales apps based on demand.
- **Resilience**: Restarts failed containers automatically.
- **Portability**: Works locally or in the cloud (e.g., Azure Container Apps for DACA).

#### Kubernetes Architecture

Kubernetes operates as a cluster with:

- **Master Node (Control Plane)**:
  - **API Server**: Handles requests (e.g., `kubectl` commands).
  - **etcd**: Stores cluster state.
  - **Controller Manager**: Ensures desired state (e.g., pod replicas).
  - **Scheduler**: Assigns pods to nodes.
- **Worker Nodes**:
  - Run pods (containers).
  - **Kubelet**: Manages pods on the node.
  - **Kube-Proxy**: Handles networking.

**Analogy**: Think of Kubernetes as a shipping port—containers (pods) are cargo, the control plane is the port authority, and worker nodes are docks.

---

## 2. Setting Up a Local Kubernetes Cluster

We’ll use Rancher Desktop’s k3s cluster (lightweight Kubernetes). It’s already set up if you followed the previous tutorial.

### Verify Cluster

Check the cluster status:

```bash
kubectl get nodes
```

### Optional: Explore Alternatives

While we use Rancher Desktop, other tools like `minikube` or `kind` can also run local clusters. The concepts here apply universally.

---

## 3. Working with Pods

### What is a Pod?

A pod is the smallest deployable unit in Kubernetes, typically running one container (e.g., `daca-agent`). Pods can contain multiple containers, but we’ll start simple.

Every app on Kubernetes runs inside a Pod.

- When you deploy an app, you deploy it in a Pod
- When you terminate an app, you terminate its Pod
- When you scale an app up, you add more Pods
- When you scale an app down, you remove Pods
- When you update an app, you deploy new Pods

Pods abstract the workload details. This means you can run containers, VMs, serverless functions, and Wasm apps inside Pods and Kubernetes doesn’t know the diﬀerence.

The following command shows a complete list of Pod attributes and returns over 1,000 lines. Press the spacebar to page through the output and press q to return to your prompt.

```bash
kubectl explain pods --recursive | more
```

Pods are lightweight and add very little overhead. The following example drills into the Pod restartPolicy attribute.

```bash
kubectl explain pod.spec.restartPolicy
```

Pods run one or more containers, and all containers in the same Pod share the Pod’s execution environment. This includes:

- Shared filesystem and volumes ( mnt namespace)
- Shared network stack ( net namespace)
- Shared memory ( IPC namespace)
- Shared process tree ( pid namespace)
- Shared hostname ( uts namespace)

Before going any further , remember that nodes are host servers that can be physical servers, virtual machines, or cloud instances. Pods wrap containers and execute on nodes.

### Hands-On: Create a Pod

Create `pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: agent-pod
spec:
  containers:
    - name: agent-app
      image: nginx
      ports:
        - containerPort: 80
```

Apply it:

```bash
kubectl apply -f pod.yaml
```

Check status:

```bash
kubectl get pods
```

Output:

```bash
mjs@Muhammads-MacBook-Pro-3 03_kubernetes_basics % kubectl get pods

NAME        READY   STATUS              RESTARTS   AGE
agent-pod   0/1     ContainerCreating   0          25s
mjs@Muhammads-MacBook-Pro-3 03_kubernetes_basics % kubectl get pods

NAME        READY   STATUS    RESTARTS   AGE
agent-pod   1/1     Running   0          96s
```

View logs:

```bash
kubectl logs agent-pod
```

Port Forward and open in browser

```bash
kubectl port-forward pod/agent-pod 8000:80
```

Delete it:

```bash
kubectl delete pod agent-pod
```

---

## 4. Understanding Deployments

### What is a Deployment?

Deployments manage pods, ensuring a specified number of replicas run, handling updates, and rollbacks. They use ReplicaSets to maintain the desired pod count and support rolling updates for zero-downtime deployments.

Note: To access a Deployment’s pods over the network, you’ll need a Service, which we’ll cover in Section 5. For now, we’ll use port-forwarding to test the app.

### Hands-On: Create a Deployment

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: agent-app
  template:
    metadata:
      labels:
        app: agent-app
    spec:
      containers:
        - name: agent-app
          image: nginx:latest
          ports:
            - containerPort: 80
```

Apply it:

```bash
kubectl apply -f deployment.yaml
```

Check pods:

```bash
kubectl get pods
```

Output:

```
NAME                         READY   STATUS    RESTARTS   AGE
agent-app-5cccf7cd67-fqfh6   1/1     Running   0          19s
agent-app-5cccf7cd67-jj7hm   1/1     Running   0          19s
```

#### Scale the Deployment

Increase replicas:

```bash
kubectl scale deployment agent-app --replicas=3
```

Verify:

```bash
kubectl get pods
```

```bash
mjs@Muhammads-MacBook-Pro-3 03_kubernetes_basics % kubectl get pods

NAME                         READY   STATUS              RESTARTS   AGE
agent-app-5cccf7cd67-d7c9s   0/1     ContainerCreating   0          2s
agent-app-5cccf7cd67-fqfh6   1/1     Running             0          35s
agent-app-5cccf7cd67-jj7hm   1/1     Running             0          35s
```

#### Update the Deployment

Edit `deployment.yaml`, change `replicas` to `1`, and reapply:

```bash
kubectl apply -f deployment.yaml
```

Cleanup

```bash
mjs@Muhammads-MacBook-Pro-3 03_kubernetes_basics % kubectl delete -f deployment.yaml
deployment.apps "agent-app" deleted
```

## 4.1 Deploy: Practical Example 3 – Deploying last step container to Kubernetes

Let’s deploy the DACA agent app to Rancher Desktop’s k3s cluster, introducing Kubernetes.

### Step 4.1: Create Kubernetes Manifest

Create `agent-deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: daca
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-app
  namespace: daca
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agent-app
  template:
    metadata:
      labels:
        app: agent-app
    spec:
      containers:
        - name: agent-app
          image: nginx:latest
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: agent-app
  namespace: daca
spec:
  selector:
    app: agent-app
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```

Here's a breakdown of the `agent-deployment.yaml` Kubernetes manifest:

---

#### 🔧 **Purpose**:

This YAML file defines resources for deploying a **Kubernetes application** in a custom namespace called `daca`. It includes:

1. A **Namespace**
2. A **Deployment** (to run the app container)
3. A **Service** (to expose the container internally in the cluster)

---

#### ✅ Step-by-Step Explanation:

---

##### 1. **Namespace**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: daca
```

- **Purpose**: Creates a separate environment called `daca` to logically isolate your app's resources.
- Namespaces help in organizing workloads in large clusters.

---

##### 2. **Deployment**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-app
  namespace: daca
spec:
  replicas: 1
```

- **Deployment**: Manages the creation and lifecycle of pods.
- **replicas: 1**: Runs a single instance (pod) of your app.

```yaml
selector:
  matchLabels:
    app: agent-app
```

- Links this deployment to pods with the label `app: agent-app`.

```yaml
template:
  metadata:
    labels:
      app: agent-app
```

- **Pod template** metadata. Labels here must match the selector.

```yaml
spec:
  containers:
    - name: agent-app
      image: nginx:latest
      ports:
        - containerPort: 80
```

- **Containers**: Specifies the container to run.
  - `image`: The Docker image to use.
  - `containerPort: 80`: Exposes port 80 from inside the container (your app listens here).

---

##### 3. **Service**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: agent-app
  namespace: daca
```

- **Service**: Provides a stable way to access the pod(s) managed by the deployment.

```yaml
spec:
  selector:
    app: agent-app
```

- Matches the pods using the label `app: agent-app`.

```yaml
ports:
  - port: 80
    targetPort: 80
```

- **port**: Port exposed by the service internally.
- **targetPort**: Port on the container the traffic will be forwarded to (same here: `80`).

```yaml
type: ClusterIP
```

- **ClusterIP**: Default service type, exposes the service **internally within the cluster** (not accessible from outside unless exposed via Ingress or NodePort).

---

#### 🧠 Summary:

You're:

- Creating a namespace `daca`.
- Deploying an app as a pod in that namespace.
- Exposing it via an internal service on port `80`.

### Step 4.2: Deploy

Apply:

```bash
kubectl apply -f agent-deployment.yaml
```

Output:

```bash
namespace/daca created
deployment.apps/agent-app created
service/agent-app created
```

Verify:

```bash
kubectl get pods -n daca
```

Output:

```
NAME                         READY   STATUS    RESTARTS   AGE
agent-app-6cd8d64b48-5n4cz   1/1     Running   0          12s
```

Access:

```bash
kubectl port-forward svc/agent-app 8000:80 -n daca
```

Open `http://localhost:8000` to see the agent app.

Stop Port Forwarding.

---

## Next Steps

You’ve covered Kubernetes basics:

- Architecture and core objects.
- Deploying and managing a container app.

In the DACA series, Kubernetes will orchestrate agents with Dapr for scalability and resilience. 
