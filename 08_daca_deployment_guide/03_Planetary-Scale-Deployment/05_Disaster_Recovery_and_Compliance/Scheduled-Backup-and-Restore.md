# Scheduled Backup and Restore

## Overview
This guide provides detailed instructions for implementing scheduled backup and restore procedures across multi-region Kubernetes deployments, ensuring data protection and disaster recovery capabilities.

## Prerequisites
- Multi-region Kubernetes clusters
- kubectl configured
- Helm installed
- Access to storage systems
- Basic understanding of backup concepts

## Velero Setup

### 1. Install Velero
```bash
# Add Velero Helm repository
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm repo update

# Install Velero
helm install velero vmware-tanzu/velero \
  --namespace velero \
  --create-namespace \
  --set configuration.provider=aws \
  --set configuration.backupStorageLocation.bucket=my-backup-bucket \
  --set configuration.backupStorageLocation.config.region=us-east-1 \
  --set configuration.volumeSnapshotLocation.config.region=us-east-1 \
  --set credentials.secretContents.cloud=|
    [default]
    aws_access_key_id=${AWS_ACCESS_KEY_ID}
    aws_secret_access_key=${AWS_SECRET_ACCESS_KEY}
```

### 2. Configure Backup Schedule
```yaml
# backup-schedule.yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: daily-backup
  namespace: velero
spec:
  schedule: "0 1 * * *"
  template:
    hooks: {}
    includedNamespaces:
    - '*'
    excludedNamespaces:
    - kube-system
    - velero
    - monitoring
    ttl: 720h
    storageLocation: default
    volumeSnapshotLocations:
    - default
    labelSelector:
      matchLabels:
        backup: "true"
```

## Backup Configuration

### 1. Configure Backup Storage
```yaml
# backup-storage.yaml
apiVersion: velero.io/v1
kind: BackupStorageLocation
metadata:
  name: default
  namespace: velero
spec:
  provider: aws
  objectStorage:
    bucket: my-backup-bucket
  config:
    region: us-east-1
---
apiVersion: velero.io/v1
kind: VolumeSnapshotLocation
metadata:
  name: default
  namespace: velero
spec:
  provider: aws
  config:
    region: us-east-1
```

### 2. Configure Backup Policies
```yaml
# backup-policies.yaml
apiVersion: velero.io/v1
kind: Backup
metadata:
  name: full-backup
  namespace: velero
spec:
  hooks: {}
  includedNamespaces:
  - '*'
  excludedNamespaces:
  - kube-system
  - velero
  - monitoring
  ttl: 720h
  storageLocation: default
  volumeSnapshotLocations:
  - default
  labelSelector:
    matchLabels:
      backup: "true"
```

## Restore Configuration

### 1. Configure Restore Process
```yaml
# restore-config.yaml
apiVersion: velero.io/v1
kind: Restore
metadata:
  name: restore-backup
  namespace: velero
spec:
  backupName: full-backup
  includedNamespaces:
  - '*'
  excludedNamespaces:
  - kube-system
  - velero
  - monitoring
  restorePVs: true
  labelSelector:
    matchLabels:
      restore: "true"
```

### 2. Configure Restore Schedule
```yaml
# restore-schedule.yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: restore-test
  namespace: velero
spec:
  schedule: "0 0 * * 0"
  template:
    hooks: {}
    includedNamespaces:
    - '*'
    excludedNamespaces:
    - kube-system
    - velero
    - monitoring
    restorePVs: true
    labelSelector:
      matchLabels:
        restore: "true"
```

## Monitoring and Validation

### 1. Configure Backup Monitoring
```yaml
# backup-monitoring.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: backup-alerts
  namespace: monitoring
spec:
  groups:
  - name: backup
    rules:
    - alert: BackupFailed
      expr: velero_backup_failed_total > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: Backup failure detected
        description: Velero backup has failed
    - alert: RestoreFailed
      expr: velero_restore_failed_total > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: Restore failure detected
        description: Velero restore has failed
```

### 2. Create Backup Dashboard
```yaml
# backup-dashboard.yaml
apiVersion: integreatly.org/v1alpha1
kind: GrafanaDashboard
metadata:
  name: backup-monitoring
  namespace: monitoring
spec:
  json: |
    {
      "dashboard": {
        "title": "Backup and Restore",
        "panels": [
          {
            "title": "Backup Status",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "velero_backup_total",
                "legendFormat": "{{status}}"
              }
            ]
          },
          {
            "title": "Restore Status",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "velero_restore_total",
                "legendFormat": "{{status}}"
              }
            ]
          },
          {
            "title": "Backup Size",
            "type": "graph",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "velero_backup_size_bytes",
                "legendFormat": "{{backup}}"
              }
            ]
          }
        ]
      }
    }
```

## Best Practices

### 1. Backup Configuration
- Regular schedules
- Retention policies
- Monitoring setup
- Testing strategy
- Documentation

### 2. Restore Configuration
- Regular testing
- Validation process
- Monitoring setup
- Documentation
- Training

### 3. Disaster Recovery
- Regular drills
- Documentation
- Training
- Updates
- Reviews

## Next Steps
1. Implement monitoring
2. Regular testing
3. Documentation
4. Training
5. Regular reviews
