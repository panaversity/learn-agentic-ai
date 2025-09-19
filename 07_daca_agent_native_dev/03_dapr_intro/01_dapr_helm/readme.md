# Deploy [Dapr on a Kubernetes cluster with Helm](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/#install-with-helm)

Now let's get hand's on with dapr. This step sets up Dapr from scratch using Helm on Rancher Desktop, following a beginner-friendly flow:

1. Deploy Dapr’s control plane and Dashboard with Helm.
2. Verify Dapr and explore the CLI (briefly, focusing on the Kubernetes aspect).
3. Deploy Redis and configure state/pub-sub components.
4. Test Dapr APIs with `curl` via a test app.
5. Verify state data in Redis.
6. Explore the Dapr Dashboard.

## 1. Deploy Dapr Control Plane with Helm

Dapr on Kubernetes is deployed via a set of control plane services that provide first-class integration for running your applications with Dapr. These services manage Dapr's runtime within the cluster. The Dapr Helm chart deploys these key services:

* **dapr-operator**: Manages component updates and Kubernetes service endpoints for Dapr (like state stores, pub/subs, etc.).
* **dapr-sidecar-injector**: Automatically injects the Dapr sidecar container into annotated application pods, setting environment variables like `DAPR_HTTP_PORT` and `DAPR_GRPC_PORT` for easy communication.
* **dapr-placement**: Used specifically for Dapr Actors, it creates mapping tables that map actor instances to pods.
* **dapr-sentry**: Manages mTLS authentication between Dapr sidecars for secure service-to-service communication and acts as a certificate authority.
* **dapr-scheduler**: Provides distributed job scheduling capabilities for Dapr's Jobs API, Workflow API, and Actor Reminders.

[![Dapr Kubernetes Diagram](./dapr-k8.png)](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-overview/)

## 1, Deploy Dapr Control Plane with Helm

We’ll deploy Dapr `1.15` in the `dapr-system` namespace.

1. **Add Dapr Helm Repo**:
   ```bash
   helm repo add dapr https://dapr.github.io/helm-charts/
   helm repo update
   ```

2. **Install Dapr Control Plane**:
   ```bash
   helm upgrade --install dapr dapr/dapr \
   --version=1.15 \
   --namespace dapr-system \
   --create-namespace \
   --wait
   ```

   For Windows
   ```bash
    helm upgrade --install dapr dapr/dapr --version=1.15 --namespace dapr-system --create-namespace --wait
   ```

3. **Verify Dapr Pods**:
   ```bash
   kubectl get pods -n dapr-system
   ```
   - Expected:
     ```
     NAME                                     READY   STATUS    RESTARTS   AGE
     dapr-operator-5fbcb75589-q4dcd           1/1     Running   0          56s
     dapr-placement-server-0                  1/1     Running   0          56s
     dapr-scheduler-server-0                  1/1     Running   0          56s
     dapr-scheduler-server-1                  1/1     Running   0          56s
     dapr-scheduler-server-2                  1/1     Running   0          56s
     dapr-sentry-75b55cbb9-z765n              1/1     Running   0          56s
     dapr-sidecar-injector-76545c8c59-dg62r   1/1     Running   0          56s
     ```

## 2: Deploy Dapr Dashboard

The Dapr Dashboard provides a web UI to visualize components, apps, and subscriptions.

1. **Install Dapr Dashboard**:
   ```bash
   helm install dapr-dashboard dapr/dapr-dashboard --namespace dapr-system
   ```

2. **Verify Dashboard Pod**:
   ```bash
   kubectl get pods -n dapr-system
   ```
   - Expected: Includes `dapr-dashboard-...` with `1/1` readiness.

   Output:

   ```bash
    NAME                                     READY   STATUS              RESTARTS      AGE
    dapr-dashboard-5cb455db6f-wsjpm          0/1     ContainerCreating   0             23s
    dapr-operator-5fbcb75589-gzvm7           1/1     Running             0             83s
    dapr-placement-server-0                  1/1     Running             0             83s
    dapr-scheduler-server-0                  1/1     Running             1 (43s ago)   83s
    dapr-scheduler-server-1                  1/1     Running             1 (43s ago)   82s
    dapr-scheduler-server-2                  1/1     Running             1 (43s ago)   82s
    dapr-sentry-75b55cbb9-5j2zq              1/1     Running             0             83s
    dapr-sidecar-injector-76545c8c59-2jvsn   1/1     Running             1 (39s ago)   83s

   ```

   Wait till all status are Running.

3. **Port-Forward**:
  ```bash
  kubectl port-forward service/dapr-dashboard 8080:8080 -n dapr-system
  ```

Open http://localhost:8080 and explore the dashboard. Right now it's empty.

## 3: Deploy Redis and Configure Dapr Components

### What’s Happening?
We’ll deploy Redis as the backend for state and pub/sub, and configure Dapr components with YAML files.

1. **Install Redis**:
   ```bash
   helm install redis bitnami/redis --set auth.enabled=false --namespace default
   ```

2. **Verify Redis**:
   ```bash
   kubectl get pods
   ```
   - Expected: `redis-master-0` with `1/1` readiness.

3. **Configure State Store**:
   - Create `redis-state.yaml`:
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
    ```
   - Apply:
     ```bash
     kubectl apply -f redis-state.yaml
     ```

4. **Configure Pub/Sub**:
   - Create `redis-pubsub.yaml`:
     ```yaml
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
   - Apply:
     ```bash
     kubectl apply -f redis-pubsub.yaml
     ```

5. **Configure Subscription**:
   - Create `subscriptions.yaml`:
     ```yaml
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
   - Apply:
     ```bash
     kubectl apply -f subscriptions.yaml
     ```

6. **Verify Components**:
   ```bash
    kubectl get components -n default
   ```
   - Expected:
     ```bash
    NAME         AGE
    pubsub       112s
    statestore   2m25s
     ```

Open http://localhost:8080/components and see the components there.

## 4: Test Dapr APIs

### What’s Happening?
Dapr's sidecar exposes HTTP APIs (typically on port 3500 by default) that applications use to interact with Dapr's building blocks. These APIs allow saving/retrieving data using a configured state store (like Redis) and publishing/subscribing to events using a configured pub/sub component. Since we haven't deployed our final application yet, we'll deploy a temporary test application with a Dapr sidecar attached to demonstrate how to interact with these APIs using `curl`. The test app uses a simple Nginx container as a placeholder (running on its default port 80), but our interaction will solely be with the Dapr sidecar (on its default port 3500).

1.  **Deploy Test App**: Deploy a simple Nginx deployment with Dapr annotations to ensure a sidecar is injected.

   - Create `nginx-app.yaml`:
     ```yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       name: dapr-test-app
       namespace: default
     spec:
       replicas: 1
       selector:
         matchLabels:
           app: dapr-test-app
       template:
         metadata:
           labels:
             app: dapr-test-app
           annotations:
             dapr.io/enabled: "true"
             dapr.io/app-id: "dapr-test-app"
             dapr.io/app-port: "8080"
             dapr.io/enable-api-logging: "true"
         spec:
           containers:
           - name: app
             image: nginx:latest
             ports:
             - containerPort: 8080
     ---
     apiVersion: v1
     kind: Service
     metadata:
       name: dapr-test-app
       namespace: default
     spec:
       selector:
         app: dapr-test-app
       ports:
       - protocol: TCP
         port: 80
         targetPort: 8080
       type: ClusterIP
     ```
   - Apply:
     ```bash
     kubectl apply -f nginx-app.yaml
     ```

2.  **Verify Pod**: Check that the test application pod is running and has both the Nginx container and the Dapr sidecar container.
   ```bash
   kubectl get pods
   ```
   - Expected: `dapr-test-app-...` with `2/2` readiness (Nginx + sidecar).
   

3.  **Port-Forward to Sidecar**: Establish a local port-forward to the Dapr sidecar's HTTP API port (3500) on the test application pod. You'll need to find the specific pod name.
   ```bash
   kubectl get pods | grep dapr-test-app
   kubectl port-forward pod/dapr-test-app-<pod-suffix> 3500:3500 -n default
   ```
   - Example:
     ```bash
     kubectl port-forward pod/dapr-test-app-79469c967b-bhvbm 3500:3500 -n default
     ```
   - Expected:
     ```
     Forwarding from 127.0.0.1:3500 -> 3500
     Forwarding from [::1]:3500 -> 3500
     ```

4.  **Test State Store**: Use `curl` to interact with the state store component via the Dapr sidecar.
   - Save State:
     ```bash
     curl -X POST http://localhost:3500/v1.0/state/statestore \
     -H "Content-Type: application/json" \
     -d '[{"key": "test-key", "value": {"user_id": "user123", "message": "Hello, Dapr!"}}]'
     ```
     - Expected: No output (200 OK).

    - Retrieve State: Send a GET request to retrieve the state for the `test-key` using the `statestore` component.
     ```bash
     curl http://localhost:3500/v1.0/state/statestore/test-key
     ```
     - Expected:
       ```json
       {"user_id": "user123", "message": "Hello, Dapr!"}
       ```

5.  **Test Pub/Sub**: Use `curl` to interact with the pub/sub component via the Dapr sidecar.
   ```bash
   curl -X POST http://localhost:3500/v1.0/publish/pubsub/message-updated \
   -H "Content-Type: application/json" \
   -d '{"user_id": "user123", "message": "Hello, Dapr!"}'
   ```
   - Expected: No output (200 OK).

6.  **Stop Port-Forwarding**: Go back to the terminal where `kubectl port-forward` is running and press `Ctrl+C` to stop the forwarding.
   - Press `Ctrl+C`.

## 5: Verify Redis Data

### What’s Happening?
When we saved state using the Dapr sidecar and the `statestore` component, Dapr communicated with Redis to store the data. Dapr typically prefixes keys in the state store with the application's Dapr ID (`dapr-test-app` in this case). We'll connect directly to Redis to confirm the data is stored there under the expected key format.

1.  **Run Redis Client Pod**: Deploy a temporary pod with a Redis client image to interact with the Redis service within the cluster.
   ```bash
   kubectl run redis-client --namespace default --restart='Never' --image docker.io/bitnami/redis:7.4.2-debian-12-r11 --command -- sleep infinity
   ```

   Wait for the container to start

   ```bash
    mjs@Muhammads-MacBook-Pro-3 learn-agentic-ai % kubectl get pods
    NAME                             READY   STATUS              RESTARTS   AGE
    redis-client                     0/1     ContainerCreating   0          48s
   ```

2.  **Connect to Redis**: Execute a shell inside the `redis-client` pod and run the `redis-cli` command to connect to the Redis master service.
   ```bash
   kubectl exec -it redis-client --namespace default -- redis-cli -h redis-master
   ```

3.  **Check Keys**: Use the Redis `KEYS` command to see all keys currently stored.
   ```
   KEYS *
   ```
   - Expected:
     ```
     1) "message-updated"
     2) "dapr-test-app||test-key"
     ```

4.  **Inspect the type of a key in Redis**: Before retrieving the value, check the data type of the state key.
    ```bash
    TYPE dapr-test-app||test-key
    ```
    - Expected:
      ```
      hash
      ```
      Dapr's default Redis state store implementation stores state as a Redis Hash, including the data, ETag (version), and potentially metadata.

    Depending on the result of `TYPE`, you can then use the appropriate command to inspect it. Since it's a `hash`:

    Retrieve the value again using `HGETALL` for Redis Hashes:
    ```bash
    HGETALL dapr-test-app||test-key
    ```
    - Expected output: The components of the Redis Hash representing the state.
      ```json
      1) "data"
      2) "{\"user_id\":\"user123\",\"message\":\"Hello, Dapr!\"}" # The actual JSON data stored
      3) "version"
      4) "1" # The ETag/version managed by Dapr
      ```
    - Explanation: This confirms that Dapr successfully stored the state data in Redis under the expected key format (`<dapr-app-id>||<key>`) and structure.

    You can also inspect the pub/sub stream key, which is a Redis Stream:
    ```bash
    TYPE message-updated
    ```
    - Expected:
      ```
      stream
      ```
    You can inspect the stream using `XRANGE`:
    ```bash
    XRANGE message-updated - +
    ```
    - Expected: Output showing messages in the stream (the message you published). The format will be detailed, including message IDs and the data payload.


5.  Exit Redis CLI and Cleanup:
    ```bash
    EXIT
    ```
    Delete the temporary Redis client pod:
    ```bash
    kubectl delete pod redis-client --namespace default
    ```

6.  **Clean Up Test App**: Delete the test deployment and service.
   ```bash
   kubectl delete -f nginx-app.yaml
   ```

## DACA Context
This setup supports DACA principles:
- **Stateless Computing**: Applications (like the potential FastAPI app) offload state persistence to external stores like Redis, allowing them to be stateless and easily scaled.
- **Event-Driven Architecture**: Dapr's pub/sub building block enables reactive workflows and decoupling of services via message topics.
- **Cloud-First**: Using Kubernetes and Helm ensures the deployment is portable and aligns with cloud-native practices.
- **Resilience**: Dapr’s sidecar can handle retries and other resilience patterns when interacting with components like state stores and pub/sub brokers.

## Clean Up

To clean up all resources created in this tutorial:

```bash
# Delete application-specific resources (adjust file names if necessary)
kubectl delete -f redis-state.yaml --ignore-not-found=true
kubectl delete -f redis-pubsub.yaml --ignore-not-found=true
kubectl delete -f subscriptions.yaml --ignore-not-found=true
kubectl delete -f nginx-app.yaml --ignore-not-found=true # Ensure this matches your test app file

# Uninstall Helm charts
helm uninstall redis -n default
helm uninstall dapr-dashboard -n dapr-system
helm uninstall dapr -n dapr-system

# Delete the dapr-system namespace
kubectl delete namespace dapr-system --ignore-not-found=true
```

## Resources
- Dapr Kubernetes Deployment: https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/
- Dapr Helm Chart: https://github.com/dapr/dapr/tree/master/charts/dapr
- Dapr Dashboard: https://docs.dapr.io/operations/monitoring/dashboard/
- FastAPI: https://fastapi.tiangolo.com/
- UV: https://docs.astral.sh/uv/