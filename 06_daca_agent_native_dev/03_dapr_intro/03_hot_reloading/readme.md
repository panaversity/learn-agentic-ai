# Add Hot Reloading for Agentic Native Cloud Local Development Environment [(using Tilt)](https://docs.tilt.dev/index.html)

**In this module we will use tilt to get hot reloading and complete our Agent Native Cloud Local Development Environment.**

We have deployed the Dapr infrastructure (Control Plane, Dashboard, Redis, Components) in our Kubernetes cluster (Rancher Desktop) using Helm and `kubectl apply` (from Document 01). We have also set up our FastAPI project with the application code, Dockerfile, and Kubernetes manifests (from Document 02).

Now, we need an efficient way to develop our FastAPI application with rapid iteration and hot-reloading, while keeping the application running within Kubernetes alongside its Dapr sidecar and components. 

The standard cloud-native approach for this kind of rapid development loop in Kubernetes is to use a tool that watches your local filesystem and syncs code changes into the running container. We will use **Tilt** to achieve this. Tilt will automate building the development image, deploying your application to Kubernetes, and crucially, syncing your local code changes into the running pod to trigger FastAPI's hot-reloading (via Uvicorn's `--reload` flag) and tilt to sync local changes within kubernetes pod.

Steps:
- 1. Tilt FastAPI Hands On
- 2. Tilt Dapr Hands On
- 3. Tilt with a Microservice with Sidecar Hands On

Install this [Tilt Extension](https://marketplace.cursorapi.com/items?itemName=tilt-dev.Tiltfile) and in IDE and start with the first step