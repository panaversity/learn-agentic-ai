# Introduction to [Containers](https://www.docker.com/resources/what-container/) and [Kubernetes](https://kubernetes.io/docs/concepts/overview/) with [Rancher Desktop](https://docs.rancherdesktop.io/)

This tutorial lays the foundation for containerizing our agentic AI microservices by introducing **containers**, **Kubernetes**, **Helm** and **Rancher Desktop**. We’ll explore how containers package applications for consistency, how Kubernetes orchestrates them for scalability, and how Rancher Desktop simplifies both on your local machine using the `containerd` engine. Through hands-on examples, we’ll containerize a DACA agent app and deploy it in a Kubernetes cluster, setting the stage for Dapr integration in the next tutorial. Let’s get started!

---

## What You’ll Learn

- Core concepts of containerization (containers, images, Dockerfiles).
- Basics of Kubernetes (pods, Deployments, Services)  and Helm.
- How Rancher Desktop manages containers with `containerd` and provides a local Kubernetes cluster.
- Practical examples of building, running, and deploying a DACA agent app in containers and Kubernetes.
- Key commands for `nerdctl` (containerd CLI) and Kubernetes (`kubectl`).
- Download [Rancher Desktop](https://rancherdesktop.io/) and [Lens, an IDE for Kubernetes](https://k8slens.dev/download)

## Prerequisites

- A computer with administrative privileges (macOS, Windows, or Linux).
- Basic command-line familiarity (e.g., Terminal on macOS/Linux, PowerShell on Windows).
- No prior container or Kubernetes experience needed—we start from scratch!
- Recommended: 8 GB RAM, 4 CPUs.

---

##  Why Containers, Helm and Kubernetes for DACA?

- **Consistency**: Containers ensure agent apps (e.g., Chat Service) run identically everywhere.
- **Scalability**: Kubernetes scales pods for DACA’s event-driven architecture.
- **Deployment**: Prepares for ACA/Kubernetes, avoiding Compose’s rework.
- **Resilience**: Kubernetes restarts failed pods, supporting CockroachDB state management.

Next, we’ll add a Dapr sidecar to this agent app in Kubernetes, enabling state and pub/sub.

---

## Next Steps

After completion you’ve learned containers, helm and Kubernetes with Rancher Desktop!

### Optional Exercises

1. Deploy a Redis pod in Kubernetes (`redis:alpine`).
2. Push `default/daca-agent` to Docker Hub (requires `nerdctl push`).
3. Explore `kubectl describe pod` for debugging.

---

## Conclusion

We’ve covered containerization (images, `Dockerfile`, containers) and Kubernetes (pods, Deployments, Services), Helm using Rancher Desktop with the `containerd` engine. With hands-on DACA examples, you’re ready to containerize microservices with Dapr in Kubernetes, paving the way for scalable agentic AI.
