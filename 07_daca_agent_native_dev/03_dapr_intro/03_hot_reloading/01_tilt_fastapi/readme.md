# 1. Tilt FastAPI Hands On

Live updates enable hot reloading by syncing local code changes directly to containers, ideal for fast feedback loops in agentic systems where developers iterate on autonomous logic.

Here we will use Tilt to sync our container running in pod with local changes in real time.


## Why Tilt is Better for Agentic Cloud Development

Tilt is the better choice for agentic cloud development, particularly in the development phase (DACA Stage 1), for the following reasons:

- Faster Feedback Loop: Tilt’s live update feature syncs code changes to running pods without rebuilding images, enabling rapid iteration on agentic logic (e.g., FastAPI endpoints interacting with Dapr’s state/pub-sub). This is critical for developing autonomous systems where logic evolves frequently.
- Enhanced Developer Experience: The Tilt UI provides real-time visibility into application and sidecar (e.g., Dapr) logs, resource health, and port-forwarding status, making it easier to debug complex agentic workflows involving multiple components.
Dapr Compatibility: Tilt’s flexibility in managing Kubernetes resources and port-forwarding (e.g., FastAPI on 8000, Dapr on 3500) aligns seamlessly with the tutorial’s Dapr-based setup, as demonstrated in Part 2.
- Custom Automation: The Tiltfile supports custom workflows (e.g., syncing code, restarting processes, or integrating with Dapr components), which mirrors the autonomous, goal-oriented nature of agentic systems.
- User-Friendly UI: The Tilt dashboard (http://localhost:10350) offers real-time logs, resource status, and debugging, which supports managing complex agentic workflows.
- Extensibility: Tilt’s Tiltfile (written in Starlark, a Python-like language) allows custom workflows, such as triggering database seeding or integrating with Dapr sidecars, aligning with agentic automation needs.
- Local and Remote Support: Works with local clusters (e.g., Rancher Desktop) and remote - - - Kubernetes clusters, fitting cloud-native development.

Weaknesses:
- May require more setup for complex pipelines compared to Skaffold’s structured approach.
- Less focus on CI/CD integration, which might be needed for later agentic deployment stages.

This setup aligns with the DACA principle of developing within a production-like (containerized, Kubernetes-based) environment from Stage 1.

Here we will configure it with fastapi and in next step learn to setup dapr sidecar as well.

### Prerequisites

*   You have completed all steps in Document 01 (Dapr Control Plane, Dashboard, Redis, Dapr Components deployed in Kubernetes).
*   You have completed Steps 1 and 2 in Document 02 (Project setup, `main.py`, `Dockerfile`, `.dockerignore`, `kubernetes/deployment.yaml`, `kubernetes/service.yaml` created).
*   Your Kubernetes cluster (Rancher Desktop) is running.
*   Ensure you are in the root directory of your `hello_fastapi` project.

### 1. Install Tilt

Tilt is a command-line tool and a local server with a UI. Install it on your local machine.

*   **macOS (Homebrew):**
    ```bash
    brew install tilt
    ```
*   **Windows (Chocolatey):**
    ```bash
    choco install tilt
    ```
*   **Linux:**
    ```bash
    curl -fsSL https://run.tilt.dev/install.sh | bash
    ```
*   **Other methods:** See the [official Tilt installation guide](https://docs.tilt.dev/install.html).

Verify installation:
```bash
tilt version
```

### 2. Basic Setup

### 2.1 Install Tilt Extension

[Install Tilt Extension in your IDE](https://marketplace.cursorapi.com/items?itemName=tilt-dev.Tiltfile)

#### 2.2 Modify Dockerfile for Development

For hot-reloading to work inside the container using Uvicorn, the `CMD` instruction must include the `--reload` flag.

Open your `Dockerfile` (created in Document 02) and modify the `CMD` line:

```dockerfile
# ... other layers from Document 02 Dockerfile
EXPOSE 8000
# Original: CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Modified for Development Hot-reloading:
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Note:** This `Dockerfile` with `--reload` is optimized for your *development* workflow with Tilt. When you move to subsequent DACA deployment stages (prototyping, production), you will typically use a `Dockerfile` *without* the `--reload` flag for stability and performance in non-development environments. Tilt builds a *development image* based on this modified Dockerfile.

### 3. Create the Tiltfile

The `Tiltfile` tells Tilt how to build, deploy, and manage your application for development. Create a file named `Tiltfile` in the root of your `hello_dapr_fastapi` project directory.

Add the following content to `Tiltfile`:

```python
# Tiltfile for FastAPI Hot-reloading Development

# Load the nerdctl extension for Rancher Desktop
load('ext://nerdctl', 'nerdctl_build')

# Build the image using nerdctl, optimized for containerd and Kubernetes
nerdctl_build(
    ref='dapr-fastapi-hello',
    context='.',
    dockerfile='Dockerfile',
    live_update=[
        # Sync local directory '.' to '/code' in the container
        sync('.', '/code'),
        # Optional: Restart Uvicorn if reload fails
        # run('pkill -f uvicorn', trigger=['./main.py'])
    ]
)

# Deploy Kubernetes manifests (deployment and service).
# Assumes Dapr components (Redis, statestore, pubsub) are already deployed.
k8s_yaml(['kubernetes/deployment.yaml', 'kubernetes/service.yaml'])

# Define the Kubernetes resource for Tilt to manage.
# Includes port-forwarding to access the app at http://localhost:8000.
k8s_resource(
    'dapr-fastapi-hello',
    port_forwards='8000:8000',
    extra_pod_selectors={'app': 'dapr-fastapi-hello'}
)
```


### 4. Run Tilt

Now, start Tilt from your project root directory:

```bash
tilt up
```

Tilt will:
1.  Start its UI in your browser (usually at `http://localhost:10350`).
2.  Read your `Tiltfile`.
3.  Build your Docker image (or use a cached one).
4.  Deploy your Kubernetes manifests (`deployment.yaml`, `service.yaml`) to Rancher Desktop. This will create your app pod with the Dapr sidecar injected.
5.  Start watching your local filesystem for changes.
6.  Set up the port-forwarding.

Watch the Tilt UI. You should see your `fastapi-hello` resource, its logs (including the Dapr sidecar starting and your FastAPI app starting via Uvicorn), and the port-forwarding status. Wait until the resource is green (healthy).

### 5. Verify Hot Reloading

Now that Tilt is running and managing your application in Kubernetes:



### 6. Stop and Clean Up Tilt Development Session

When you are finished with your development session:

1.  Go back to the terminal where you ran `tilt up`.
2.  Press `Ctrl+C`. Tilt will stop the process.
3.  To remove the resources Tilt deployed to Kubernetes:
    ```bash
    tilt down
    ```
    This will delete the deployment and service that Tilt created.

This completes the setup for cloud-native local development with hot-reloading using Tilt, fitting into your DACA Stage 1 workflow. You can now iterate rapidly on your FastAPI application while it runs in the ta

- https://blog.tilt.dev/2022/03/04/rancher-desktop-container-runtimes.html
