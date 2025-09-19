# Database Geo-Replication Strategies

## Overview
This document outlines the geo-replication strategies for our databases, including the transition plan from managed services to self-hosted Kubernetes deployments.

## Current Managed Services (Phase 1)
- CockroachDB Serverless (to be transitioned to Postgres on Kubernetes)
- Upstash Redis (to be transitioned to Redis on Kubernetes)
- CloudAMQP RabbitMQ (to be transitioned to Kafka)

## CockroachDB Replication (Phase 1)

### Primary-Secondary Replication
- Primary cluster in US-East
- Secondary cluster in US-West
- Synchronous replication for critical data
- Asynchronous replication for non-critical data

### Configuration
```yaml
# cockroachdb-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cockroachdb-config
  namespace: production
data:
  consistency-level: "STRONG"
  replication-factor: "3"
  max-staleness: "300s"
  automatic-failover: "true"
```

## Redis Replication (Phase 1)

### Master-Slave Replication
- Master node in US-East
- Slave nodes in US-West
- Redis Sentinel for automatic failover
- Read replicas for scaling read operations

### Configuration
```yaml
# redis-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-config
  namespace: production
data:
  replication-mode: "master-slave"
  sentinel-enabled: "true"
  read-replicas: "2"
  persistence-enabled: "true"
```

## Transition Plan

### Phase 1: Managed Services
1. CockroachDB Serverless
   - Use for initial development and testing
   - Implement data migration strategy
   - Document schema and queries

2. Upstash Redis
   - Use for caching and session management
   - Prepare Redis data migration plan
   - Document key patterns and TTLs

3. CloudAMQP RabbitMQ
   - Use for message queuing
   - Plan Kafka migration
   - Document queue configurations

### Phase 2: Kubernetes Deployment
1. Postgres Migration
   - Set up Kubernetes Postgres cluster
   - Implement data migration
   - Test replication and failover
   - Switch traffic gradually

2. Redis Migration
   - Deploy Redis cluster on Kubernetes
   - Migrate data from Upstash
   - Test replication and failover
   - Switch traffic gradually

3. Kafka Migration
   - Deploy Kafka on Kubernetes
   - Migrate from RabbitMQ
   - Test message processing
   - Switch traffic gradually

## Health Monitoring
- Prometheus metrics for both CockroachDB and Redis
- Custom health checks for replication status
- Alerting on replication lag
- Automated failover testing

## Backup Strategy
- Daily snapshots of both databases
- Point-in-time recovery capability
- Cross-region backup storage
- Automated backup verification

## Migration Checklist
- [ ] Document current database schemas
- [ ] Create data migration scripts
- [ ] Set up monitoring for both environments
- [ ] Implement rollback procedures
- [ ] Schedule maintenance windows
- [ ] Test failover scenarios
- [ ] Update application configurations
- [ ] Update CI/CD pipelines
