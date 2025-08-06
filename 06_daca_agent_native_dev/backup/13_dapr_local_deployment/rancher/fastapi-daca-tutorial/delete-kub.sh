#!/bin/bash

echo "🚨 WARNING: This will delete ALL Kubernetes resources in your cluster (except kube-system)."
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "❌ Aborted."
  exit 1
fi

echo "🧹 Deleting all resources in all namespaces (except kube-system & kube-public)..."

# Delete all resources in non-system namespaces
for ns in $(kubectl get ns --no-headers -o custom-columns=":metadata.name" | grep -vE 'kube-system|kube-public|default'); do
  echo "🔻 Deleting resources in namespace: $ns"
  kubectl delete all --all -n $ns
  kubectl delete pvc --all -n $ns
  kubectl delete configmap --all -n $ns
  kubectl delete secret --all -n $ns
  kubectl delete serviceaccount --all -n $ns
done

echo "🗑️ Deleting custom namespaces (except kube-system, kube-public, default)..."
kubectl delete ns $(kubectl get ns --no-headers -o custom-columns=":metadata.name" | grep -vE 'kube-system|kube-public|default')

echo "✅ All user-defined resources and namespaces removed."
