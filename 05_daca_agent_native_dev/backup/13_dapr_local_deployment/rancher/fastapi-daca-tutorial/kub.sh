#!/bin/bash

set -e  # Exit on error

echo "🚀 Starting Kubernetes Deployment..."

### Step 0: Initialize Dapr
echo "🔧 Initializing Dapr..."
dapr uninstall -k || true
dapr init -k --wait --enable-mtls=false # local

### Step 1: Create Namespace
echo "📦 Creating namespace 'daca'..."
kubectl create namespace daca || echo "Namespace 'daca' already exists."

### Step 2: Create Secret
echo "🔐 Creating Gemini API Key secret..."
kubectl create secret generic gemini-api-key --from-literal=gemini-api-key=$GEMINI_API_KEY -n daca || echo "Secret already exists."

### Step 3: Deploy Redis
echo "📦 Deploying Redis..."
kubectl apply -f kubernetes/redis-deployment.yaml
kubectl wait --for=condition=ready pod -l app=redis -n daca --timeout=60s

### Step 4: Deploy Dapr Components
echo "📦 Applying Dapr components..."
kubectl apply -f components/statestore.yaml -n daca
kubectl apply -f components/pubsub.yaml -n daca
kubectl apply -f components/subscriptions.yaml -n daca

### Step 5: Load Local Images to Kubernetes
echo "📦 Loading local Docker images into k8s registry..."
nerdctl save chat-service:latest | nerdctl --namespace k8s.io load
nerdctl save agent-memory-service:latest | nerdctl --namespace k8s.io load

### Step 6: Deploy Chat Service
echo "🤖 Deploying chat-service..."
kubectl apply -f kubernetes/chat-service-deployment.yaml

### Step 7: Deploy Agent Memory Service
echo "🧠 Deploying agent-memory-service..."
kubectl apply -f kubernetes/agent-memory-service-deployment.yaml

### Step 8: Verify All Pods
echo "🔍 Verifying pods in 'daca' namespace..."
kubectl get pods -n daca

echo "✅ Deployment completed successfully!"
