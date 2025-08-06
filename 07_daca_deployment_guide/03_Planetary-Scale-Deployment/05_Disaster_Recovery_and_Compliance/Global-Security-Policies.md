# Global Security Policies

## Overview
This guide provides detailed instructions for implementing and managing global security policies across multi-region Kubernetes deployments, ensuring consistent security posture and compliance.

## Prerequisites
- Multi-region Kubernetes clusters
- kubectl configured
- Helm installed
- Basic understanding of security concepts
- Access to create and modify resources

## Policy Management Setup

### 1. Install OPA Gatekeeper
```bash
# Add Gatekeeper Helm repository
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm repo update

# Install Gatekeeper
helm install gatekeeper gatekeeper/gatekeeper \
  --namespace gatekeeper-system \
  --create-namespace \
  --set auditInterval=60 \
  --set controllerManager.resources.requests.cpu=100m \
  --set controllerManager.resources.requests.memory=512Mi \
  --set audit.resources.requests.cpu=100m \
  --set audit.resources.requests.memory=512Mi
```

### 2. Configure Global Policies
```yaml
# global-policies.yaml
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("you must provide labels: %v", [missing])
        }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-global-labels
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
      - apiGroups: ["apps"]
        kinds: ["Deployment", "StatefulSet", "DaemonSet"]
  parameters:
    labels:
      - "region"
      - "environment"
      - "owner"
```

## Network Security

### 1. Configure Network Policies
```yaml
# network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-cross-region
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          region: "region-1"
    - namespaceSelector:
        matchLabels:
          region: "region-2"
    - namespaceSelector:
        matchLabels:
          region: "region-3"
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          region: "region-1"
    - namespaceSelector:
        matchLabels:
          region: "region-2"
    - namespaceSelector:
        matchLabels:
          region: "region-3"
```

### 2. Configure TLS Policies
```yaml
# tls-policies.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: security@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: global-tls
  namespace: default
spec:
  secretName: global-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - "*.example.com"
```

## Access Control

### 1. Configure RBAC
```yaml
# rbac-policies.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: global-admin
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: global-admin-binding
subjects:
- kind: Group
  name: "system:masters"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: global-admin
  apiGroup: rbac.authorization.k8s.io
```

### 2. Configure Pod Security Policies
```yaml
# pod-security-policies.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: global-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  fsGroup:
    rule: 'MustRunAs'
    ranges:
      - min: 1
        max: 65535
  readOnlyRootFilesystem: false
```

## Monitoring and Compliance

### 1. Configure Security Monitoring
```yaml
# security-monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: security-alerts
  namespace: monitoring
spec:
  groups:
  - name: security
    rules:
    - alert: UnauthorizedAccess
      expr: sum(rate(kube_audit_events_total{verb=~"create|update|delete|patch"}[5m])) by (user) > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: Unauthorized access detected
        description: User {{ $labels.user }} has performed sensitive operations
    - alert: PolicyViolation
      expr: sum(rate(gatekeeper_violations_total[5m])) by (constraint) > 0
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: Policy violation detected
        description: Constraint {{ $labels.constraint }} has been violated
```

### 2. Configure Compliance Dashboard
```yaml
# compliance-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: security-compliance
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Security Compliance",
        "panels": [
          {
            "title": "Policy Violations",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "sum(rate(gatekeeper_violations_total[5m])) by (constraint)",
                "legendFormat": "{{constraint}}"
              }
            ]
          },
          {
            "title": "Access Attempts",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "sum(rate(kube_audit_events_total[5m])) by (user)",
                "legendFormat": "{{user}}"
              }
            ]
          },
          {
            "title": "Security Events",
            "type": "table",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "kube_security_events_total",
                "legendFormat": "{{event}}"
              }
            ]
          }
        ]
      }
    }
```

## Best Practices

### 1. Policy Management
- Regular policy reviews
- Version control
- Testing strategy
- Documentation
- Compliance checks

### 2. Security Configuration
- Least privilege
- Regular audits
- Monitoring setup
- Incident response
- Documentation

### 3. Compliance
- Regular assessments
- Documentation
- Training
- Updates
- Reviews

## Next Steps
1. Implement monitoring
2. Regular audits
3. Policy updates
4. Training
5. Documentation
