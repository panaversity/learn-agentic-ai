# Executing Load Tests with k6 or Locust

## Overview
This guide provides detailed instructions for executing load tests using either k6 or Locust to validate the performance and scalability of Kubernetes deployments.

## Prerequisites
- Kubernetes cluster
- kubectl configured
- Helm installed
- Basic understanding of load testing concepts
- Access to create and modify resources

## k6 Load Testing

### 1. Install k6
```bash
# Install k6 using Helm
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install k6 grafana/k6
```

### 2. Create Test Script
```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests should be below 200ms
    http_req_failed: ['rate<0.01'],   // Error rate should be below 1%
  },
};

export default function() {
  const res = http.get('http://my-app:8080/api/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  sleep(1);
}
```

### 3. Deploy Test Job
```yaml
# k6-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: k6-load-test
  namespace: load-testing
spec:
  template:
    spec:
      containers:
      - name: k6
        image: grafana/k6:latest
        command: ["k6", "run", "/scripts/load-test.js"]
        volumeMounts:
        - name: test-scripts
          mountPath: /scripts
      volumes:
      - name: test-scripts
        configMap:
          name: k6-test-scripts
      restartPolicy: Never
```

### 4. Execute Test
```bash
# Create ConfigMap with test script
kubectl create configmap k6-test-scripts --from-file=load-test.js -n load-testing

# Deploy test job
kubectl apply -f k6-job.yaml

# Monitor test progress
kubectl logs -f job/k6-load-test -n load-testing
```

## Locust Load Testing

### 1. Install Locust
```bash
# Install Locust using Helm
helm repo add locust https://locustio.github.io/helm-charts
helm repo update
helm install locust locust/locust
```

### 2. Create Test Script
```python
# locustfile.py
from locust import HttpUser, task, between

class MyAppUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def health_check(self):
        self.client.get("/api/health")

    @task(3)
    def api_endpoint(self):
        self.client.get("/api/data")
```

### 3. Deploy Test Configuration
```yaml
# locust-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: locust-config
  namespace: load-testing
data:
  locustfile.py: |
    from locust import HttpUser, task, between

    class MyAppUser(HttpUser):
        wait_time = between(1, 5)

        @task
        def health_check(self):
            self.client.get("/api/health")

        @task(3)
        def api_endpoint(self):
            self.client.get("/api/data")
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-master
  namespace: load-testing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: locust
      component: master
  template:
    metadata:
      labels:
        app: locust
        component: master
    spec:
      containers:
      - name: locust
        image: locustio/locust:latest
        ports:
        - containerPort: 8089
        - containerPort: 5557
        env:
        - name: LOCUST_MODE
          value: master
        - name: TARGET_HOST
          value: http://my-app:8080
        volumeMounts:
        - name: locust-config
          mountPath: /locust
      volumes:
      - name: locust-config
        configMap:
          name: locust-config
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-worker
  namespace: load-testing
spec:
  replicas: 3
  selector:
    matchLabels:
      app: locust
      component: worker
  template:
    metadata:
      labels:
        app: locust
        component: worker
    spec:
      containers:
      - name: locust
        image: locustio/locust:latest
        env:
        - name: LOCUST_MODE
          value: worker
        - name: LOCUST_MASTER_HOST
          value: locust-master
        - name: TARGET_HOST
          value: http://my-app:8080
        volumeMounts:
        - name: locust-config
          mountPath: /locust
      volumes:
      - name: locust-config
        configMap:
          name: locust-config
```

### 4. Execute Test
```bash
# Deploy Locust configuration
kubectl apply -f locust-config.yaml

# Access Locust web interface
kubectl port-forward svc/locust-master 8089:8089 -n load-testing
```

## Monitoring Test Results

### 1. Prometheus Configuration
```yaml
# prometheus-config.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: load-test-metrics
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: load-test
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### 2. Grafana Dashboard
```yaml
# load-test-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: load-test-dashboard
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Load Test Dashboard",
        "panels": [
          {
            "title": "Requests per Second",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])",
                "legendFormat": "{{pod}}"
              }
            ]
          },
          {
            "title": "Response Time",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])",
                "legendFormat": "{{pod}}"
              }
            ]
          },
          {
            "title": "Error Rate",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])",
                "legendFormat": "{{pod}}"
              }
            ]
          }
        ]
      }
    }
```

## Best Practices

### 1. Test Design
- Start with baseline tests
- Gradually increase load
- Test different scenarios
- Monitor resource usage
- Document test cases

### 2. Execution
- Run tests in isolation
- Monitor system metrics
- Capture test results
- Analyze performance
- Document findings

### 3. Analysis
- Compare with SLOs
- Identify bottlenecks
- Document improvements
- Plan optimizations
- Regular testing

## Next Steps
1. Analyze results
2. Optimize performance
3. Update SLOs
4. Regular testing
5. Documentation
