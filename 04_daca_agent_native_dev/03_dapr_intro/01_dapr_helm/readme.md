# Dapr FastAPI Hands On with Helm, Dapr State, Dapr Pub/Sub

Now let's get hand's on with dapr.

## Overview
This tutorial sets up Dapr from scratch using Helm on Rancher Desktop, following a beginner-friendly flow:

1. Install the Dapr CLI.
2. Deploy Dapr’s control plane and Dashboard with Helm.
3. Verify Dapr and explore the CLI.
4. Deploy Redis and configure state/pub-sub components.
5. Test Dapr APIs with `curl` via a test app.
6. Verify state data in Redis.
7. Explore the Dapr Dashboard.
8. Build a FastAPI app with hot reloading, using Dapr’s state and pub/sub.

## 1, Deploy Dapr Control Plane with Helm

Dapr’s **control plane** includes services (operator, placement, scheduler, sentry, sidecar injector) that manage Dapr’s runtime. We’ll deploy Dapr `1.15` in the `dapr-system` namespace.

1. **Add Dapr Helm Repo**:
   ```bash
   helm repo add dapr https://dapr.github.io/helm-charts/
   helm repo update
   ```
  
2. **Install Dapr Control Plane**:
   
   **For MacOS**
   ```bash
   helm upgrade --install dapr dapr/dapr \
   --version=1.15 \
   --namespace dapr-system \
   --create-namespace \
   --wait
   ```

   **For Windows**
   ```bash
   helm upgrade --install dapr dapr/dapr --version 1.15 --namespace dapr-system --create-namespace --wait
   ```
  

4. **Verify Dapr Pods**:
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

3. **Port-Forward**:
  ```bash
  kubectl port-forward service/dapr-dashboard 8080:8080 -n dapr-system
  ```

Open localhost:8080 and explore the dashboard. Right now it's empty.

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
       - name: actorStateStore
         value: "true"
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
     apiVersion: dapr.io/v1alpha1
     kind: Subscription
     metadata:
       name: message-subscription
       namespace: default
     spec:
       pubsubname: pubsub
       topic: message-updated
       route: /subscribe
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
Dapr’s sidecar exposes HTTP APIs on port 3500 for state (saving/retrieving data in Redis) and pub/sub (publishing events). Since no app is deployed, we’ll create a temporary test app with a Dapr sidecar to test these APIs with `curl`. The test app uses Nginx as a placeholder (on port 8080), but we interact only with the sidecar (port 3500).

1. **Deploy Test App**:
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

2. **Verify Pod**:
   ```bash
   kubectl get pods
   ```
   - Expected: `dapr-test-app-...` with `2/2` readiness (Nginx + sidecar).
   

3. **Port-Forward to Sidecar**:

   **For MacOS**
   
   ```bash
   kubectl get pods | grep dapr-test-app
   ```

    ```bash
   kubectl port-forward pod/dapr-test-app-<pod-suffix> 3500:3500 -n default
   ```

   **For Windows**
   ```bash
   kubectl get pods
   ```
   
   ```bash
   kubectl port-forward pod/dapr-test-app-<pod-suffix> 3500:3500 -n default
   ```
   
   - Example:
     ```bash
     kubectl port-forward pod/dapr-test-app-79469c967b-stlgj 3500:3500 -n default
     ```
   - Expected:
     ```
     Forwarding from 127.0.0.1:3500 -> 3500
     Forwarding from [::1]:3500 -> 3500
     ```

5. **Test State Store**:
   - Save State:
     ```bash
     curl -X POST http://localhost:3500/v1.0/state/statestore \
     -H "Content-Type: application/json" \
     -d '[{"key": "test-key", "value": {"user_id": "user123", "message": "Hello, Dapr!"}}]'
     ```
     - Expected: No output (200 OK).
   - Retrieve State:
     ```bash
     curl http://localhost:3500/v1.0/state/statestore/test-key
     ```
     - Expected:
       ```json
       {"user_id": "user123", "message": "Hello, Dapr!"}
       ```

6. **Test Pub/Sub**:
   ```bash
   curl -X POST http://localhost:3500/v1.0/publish/pubsub/message-updated \
   -H "Content-Type: application/json" \
   -d '{"user_id": "user123", "message": "Hello, Dapr!"}'
   ```
   - Expected: No output (200 OK).

7. **Stop Port-Forwarding**:
   - Press `Ctrl+C`.

## 5: Verify Redis Data
### What’s Happening?
We saved a state key (`test-key`) in Redis via Dapr’s `statestore`. Let’s confirm the data is stored in Redis.

1. **Run Redis Client Pod**:
   
   **For MacOS**
   ```bash
   kubectl run redis-client --namespace default --restart='Never' --image docker.io/bitnami/redis:7.4.2-debian-12-r11 --command -- sleep infinity
   ```
   **For Windows**
   ```bash
   kubectl run redis-client --namespace default --restart="Never" --image=docker.io/bitnami/redis:7.4.2-debian-12-r11 --command -- sleep infinity
   ```

   Wait for the container to start
   
   ```bash
   kubectl get pods
   ```

    - Expeted Output:
      
      ```bash
       NAME                             READY   STATUS              RESTARTS   AGE
       redis-client                     0/1     ContainerCreating   0          48s
      ```

3. **Connect to Redis**:
   ```bash
   kubectl exec -it redis-client --namespace default -- redis-cli -h redis-master
   ```

4. **Check Keys**:
   ```
   KEYS *
   ```
   - Expected:
     ```
     1) "message-updated"
     2) "dapr-test-app||test-key"
     ```

5. **Retrieve Value**:
   ```
   HGETALL dapr-test-app||test-key
   ```
   - Expected:
     ```
     1) "data"
     2) "{\"user_id\":\"user123\",\"message\":\"Hello, Dapr!\"}"
     3) "version"
     4) "1"
     ```


6. **Inspect the type of a key in Redis**:
  ```bash
  redis-master:6379> TYPE dapr-test-app||test-key
  hash
  ```

  Depending on the result, you can then use the appropriate command to inspect it:
  - If it's a hash: HGETALL dapr-test-app||test-key
  - If it's a list: LRANGE dapr-test-app||test-key 0 -1
  - If it's a set: SMEMBERS dapr-test-app||test-key
  - If it's a zset: ZRANGE dapr-test-app||test-key 0 -1 WITHSCORES
  - XRANGE for stream: XRANGE message-updated - +

  Retrieve the value again:

  ```bash
  HGETALL dapr-test-app||test-key
  ```
  Expected:
  ```json
  1) "data"
  2) "{\"user_id\":\"user123\",\"message\":\"Hello, Dapr!\"}"
  3) "version"
  4) "1"
  ```
  - Explanation: Confirms Dapr stored the state in Redis correctly.

5. Exit Redis CLI and Cleanup:

  ```bash
  EXIT
  ```

  ```bash
  kubectl delete pod redis-client --namespace default
  ```

7. **Clean Up Test App**:
   ```bash
   kubectl delete -f nginx-app.yaml
   ```

## DACA Context
This setup supports DACA:
- **Stateless Computing**: FastAPI app offloads state to Redis.
- **Event-Driven Architecture**: Pub/sub enables reactive workflows.
- **Cloud-First**: Helm ensures portability.
- **Resilience**: Dapr’s sidecar handles retries.

## Clean Up

```bash
kubectl delete -f kubernetes/deployment.yaml
kubectl delete -f kubernetes/service.yaml
kubectl delete -f redis-state.yaml
kubectl delete -f redis-pubsub.yaml
kubectl delete -f subscriptions.yaml
kubectl delete -f test-app.yaml
helm uninstall redis -n default
helm uninstall dapr-dashboard -n dapr-system
helm uninstall dapr -n dapr-system
kubectl delete namespace dapr-system
```

## Resources
- Dapr Kubernetes Deployment: https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/
- Dapr Helm Chart: https://github.com/dapr/dapr/tree/master/charts/dapr
- Dapr Dashboard: https://docs.dapr.io/operations/monitoring/dashboard/
- FastAPI: https://fastapi.tiangolo.com/
- UV: https://docs.astral.sh/uv/
