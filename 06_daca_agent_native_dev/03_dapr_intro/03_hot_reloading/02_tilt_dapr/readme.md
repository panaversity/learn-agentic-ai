# 2. Tilt Dapr Hands On

## Configure Tilt with Dapr and Test in Dapr Dashboard

### What’s Happening?

In Step 1, we set up Tilt to enable hot-reloading for our FastAPI application running in a Kubernetes cluster (Rancher Desktop) with a basic `Tiltfile`. Now, we will create a new `Tiltfile` to manage the Dapr infrastructure (Control Plane, Dashboard, Redis, and components) that was deployed in Document 01. This step focuses on using Tilt to deploy and monitor the Dapr ecosystem independently, ensuring the Dapr Dashboard is accessible for verification. This aligns with the DACA principle of maintaining a production-like environment during development.

### Prerequisites

- You have completed all steps in Document 01 (Dapr Control Plane, Dashboard, Redis, Dapr Components deployed in Kubernetes).
- Your Kubernetes cluster (Rancher Desktop) is running.
- The Dapr component YAML files (`redis-state.yaml`, `redis-pubsub.yaml`, `subscriptions.yaml`) are present in the `./components/` directory of your `hello_dapr_fastapi` project.
- Tilt is installed (from Step 1).

### 1. Create a Tiltfile for Dapr

Create a new `Tiltfile` in the root of your `hello_dapr_fastapi` project directory to manage the Dapr infrastructure. This `Tiltfile` will deploy the Dapr Control Plane, Dashboard, Redis, and components, and set up port-forwarding for the Dapr Dashboard.

Add the following content to `Tiltfile`:

```python
# Tiltfile for Dapr Development

# Load Helm extension
load('ext://helm_remote', 'helm_remote')

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
```

Next create a components directory and copy/add these three files
- redis-state.yaml
- redis-pubsub.yaml
- subscriptions.yaml

```redis-state.yaml
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

```redis-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.default.svc.cluster.local:6379
  - name: redisPassword
    value: ""

```

```subscriptions.yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: message-subscription
  namespace: default
spec:
  pubsubname: pubsub
  topic: message-updated
  routes:
    rules:
      - match: event.type == "update"
        path: /subscribe
```

### 2. Run Tilt with Dapr

From the project root directory, start Tilt:

```bash
tilt up
```

Tilt will:
1. Start its UI at `http://localhost:10350`.
2. Create the `dapr-system` namespace.
3. Deploy the Dapr Control Plane and Dashboard via Helm.
4. Deploy Redis via Helm in the default namespace.
5. Apply the Dapr components (`redis-state.yaml`, `redis-pubsub.yaml`, `subscriptions.yaml`).
6. Set up port-forwarding for the Dapr Dashboard (`localhost:8080`).

Open the Tilt UI (`http://localhost:10350`) and verify that the following resources are healthy (green):
- `dapr` (Dapr Control Plane)
- `dapr-dashboard` (Dapr Dashboard)
- `redis` (Redis instance)

### 3. Test Dapr Dashboard

Access the Dapr Dashboard at `http://localhost:8080` to confirm that the Dapr infrastructure is running correctly. In the dashboard, you should see:
- The Dapr runtime status (e.g., Operator, Placement Service, Sentry).
- The Redis state store and pub/sub components listed under the "Components" section.
- No applications yet (since FastAPI is not deployed in this step).

If the dashboard loads and displays the Dapr runtime and components, the Dapr setup is successful.

### 4. Test in CLI:

```bash
kubectl get components.dapr.io -n default
```

Output:
```bash
NAME         AGE
pubsub       10m
statestore   10m
```

Try:
```bash
kubectl get pods -n dapr-system
```

Output:
```bash
NAME                                     READY   STATUS    RESTARTS      AGE
dapr-dashboard-644df7bcd5-sgbbv          1/1     Running   0             11m
dapr-operator-6c78ccc7f8-42qv6           1/1     Running   0             11m
dapr-placement-server-0                  1/1     Running   0             11m
dapr-scheduler-server-0                  1/1     Running   0             11m
dapr-scheduler-server-1                  1/1     Running   0             11m
dapr-scheduler-server-2                  1/1     Running   0             11m
dapr-sentry-7b85c48cfd-dtl8q             1/1     Running   0             11m
dapr-sidecar-injector-5dd6745867-gw4lg   1/1     Running   2 (10m ago)   11m
mjs@Muhammads-MacBook-Pro-3 learn-agentic-ai % 
```

### 5. Stop and Clean Up

When done, stop Tilt and clean up:

1. Press `Ctrl+C` in the terminal running `tilt up`.
2. Remove all Tilt-managed resources:
   ```bash
   tilt down
   ```

This step ensures that Tilt can manage the Dapr infrastructure independently, with the Dapr Dashboard accessible for monitoring and verification.