# Understanding Containers

**Containers** are lightweight, portable units that package an application and its dependencies (code, libraries, runtime) to run consistently across environments. In DACA, containers ensure our agentic AI microservices (e.g., Chat Service with OpenAI Agents SDK) behave the same in development and production.

## Why Containers?

- **Consistency**: Packages dependencies (e.g., Python, OpenAI SDK), avoiding “it works on my machine” issues.
- **Portability**: Runs on any compatible system, from laptops to cloud clusters.
- **Isolation**: Each container is sandboxed, preventing conflicts (e.g., different Python versions).
- **Efficiency**: Shares the host OS kernel, using less RAM than virtual machines (VMs).
- **Scalability**: Easily scaled with orchestration tools like Kubernetes.

## Containers vs. Virtual Machines

- **VMs**: Run a full OS (e.g., Ubuntu) on a hypervisor, heavy (GBs), slow to start.
- **Containers**: Share host OS, include only app dependencies, lightweight (MBs), instant start.

**Analogy**: VMs are houses with separate utilities; containers are apartments sharing a building’s infrastructure.

---

## Step 1: Core Container Concepts

Containerization packages apps into containers. Key terms:

- **Container**: A running instance of an image, isolating the app (e.g., FastAPI agent).
- **Image**: Immutable snapshot of app + dependencies (e.g., `python:3.11-slim`).
- **Dockerfile**: Script to build images (e.g., install OpenAI SDK, copy code).
- **Registry**: Stores images (e.g., Docker Hub, private registries like AWS ECR).
- **Container Engine**: Runtime to build/run containers (we’ll use `containerd` via Rancher Desktop).

Let's understand the **Core Concepts of App Containerization**. Containerization is the process of packaging an application and its dependencies into a container. Let’s break down the key concepts:

## 1.1 Containers
A **container** is a running instance of a container image. It’s an isolated environment that contains:
- The application code.
- The runtime (e.g., Python, Node.js).
- Libraries and dependencies.
- Configuration files.

Containers are ephemeral—they can be created, started, stopped, and deleted as needed. If a container crashes, you can restart it or create a new one from the same image.

### 1.2 Container Images
A **container image** is a lightweight, immutable snapshot of an application and its dependencies. It’s the blueprint for creating containers. Images are built in layers, where each layer represents a set of changes (e.g., installing a dependency, copying code).

- Images are stored in a **registry**, such as **Docker Hub** (a public registry) or a private registry (e.g., AWS ECR, Google Artifact Registry).
- Example: The `python:3.9-slim` image on Docker Hub contains a minimal Python 3.9 environment.


### 1.3 Dockerfile
A **Dockerfile** is a script that defines how to build a container image. It contains instructions like:
- Specifying a base image (e.g., `FROM python:3.9-slim`).
- Copying application code into the image.
- Installing dependencies.
- Setting environment variables.
- Defining the command to run the application.

Example Dockerfile for a Python app:
```dockerfile
# Use a base image with Python 3.9
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Define the command to run the app
CMD ["python", "app.py"]
```
---


## Step 2: Practical Example 1 – Running a Simple Container

Let’s run a container to learn container basics, using Rancher Desktop’s `containerd` engine and `nerdctl` CLI.

### Step 2.1: Run an Nginx Container

1. **Pull Nginx Image**:

   ```bash
   nerdctl pull nginx:alpine
   ```

   - Uses lightweight `alpine` (5 MB, M2-friendly).

2. **Run Container**:

   ```bash
   nerdctl run -d -p 8080:80 --name my-nginx nginx:alpine
   ```

   - `-d`: Background mode.
   - `-p 8080:80`: Maps host port 8080 to container port 80.
   - `--name my-nginx`: Names the container.

   **Note**: With `containerd`, images are namespaced (e.g., `nginx:alpine` is in the `default` namespace), but `nerdctl` handles this transparently for most commands.

3. **Verify**:

   ```bash
   nerdctl ps
   ```

   Output:

   ```
   CONTAINER ID    IMAGE                             COMMAND                   CREATED           STATUS    PORTS                   NAMES
   6c73ef9cda7a    docker.io/library/nginx:alpine    "/docker-entrypoint.…"    10 seconds ago    Up        0.0.0.0:8080->80/tcp    my-nginx
   ```

4. **Access**:

   - Open `http://localhost:8080` to see Nginx’s welcome page.

5. **Clean Up**:

   ```bash
   nerdctl stop my-nginx
   nerdctl rm my-nginx
   ```

---

## Step 3: Practical Example 2 – Building a DACA Agent Container

Let’s build a container for a DACA agent app (FastAPI with OpenAI Agents SDK), mimicking the Chat Service.

### Step 3.1: Create the App

#### Create a project:

```bash
uv init daca_agent
cd daca_agent
```

#### Setup Virtual Environment and install dependencies

On macOS/Linux:

```bash
uv venv
source .venv/bin/activate
```

On Windows:

```bash
uv venv
.venv\Scripts\activate
```

```bash
uv add "fastapi[standard]"
```

#### Create `main.py`:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": f"Hello from DACA Agent!"}
```


### Step 3.2: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /code

# Copy code
COPY . .

# Install dependencies
RUN pip install uv

RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `.dockerignore` file:
```
.venv
.git
.gitignore
.env
__pycache__
```

### Step 3.3: Build and Run

Build:

```bash
nerdctl build -t daca-agent .
```

Check Image
```bash
nerdctl images
```

OUTPUT:
```bash
(daca_agent) mjs@Muhammads-MacBook-Pro-3 daca_agent % nerdctl images

REPOSITORY    TAG       IMAGE ID        CREATED           PLATFORM       SIZE       BLOB SIZE
daca-agent    latest    35345b4bd82f    11 seconds ago    linux/arm64    338.5MB    111.1MB
nginx         alpine    65645c7bb6a0    3 minutes ago     linux/arm64    54.07MB    21.82MB
```

Run:

```bash
nerdctl run -d -p 8000:8000 --name daca-agent  daca-agent
```

- **Note**: `containerd` uses namespaces, so the image `daca-agent` is in the `default` namespace (`default/daca-agent`).

Verify:

```bash
nerdctl ps
```

Access `http://localhost:8000`:

```
{"message": "Hello from DACA Agent!"}
```

Logs:

```bash
nerdctl logs daca-agent
```

Clean up:

```bash
nerdctl stop daca-agent
nerdctl rm daca-agent
```

---


## Step 4: Key Commands

- **Container (nerdctl)**:
  - `nerdctl build -t <name> .`: Build image.
  - `nerdctl run -d -p <port> <namespace>/<image>`: Run container.
  - `nerdctl ps`: List running containers.
  - `nerdctl logs/stop/rm <container>`: Manage containers.
- **Kubernetes**:
  - `kubectl apply -f <file>`: Deploy resources.
  - `kubectl get pods/services -n <namespace>`: List resources.
  - `kubectl port-forward svc/<name> <port>`: Access Service.
  - `kubectl delete -f <file>`: Remove resources.

---

## Step 5: Why Containers and Kubernetes for DACA?

- **Consistency**: Containers ensure agent apps (e.g., Chat Service) run identically everywhere.
- **Scalability**: Kubernetes scales pods for DACA’s event-driven architecture.
- **Deployment**: Prepares for ACA/Kubernetes, avoiding Compose’s rework.
- **Resilience**: Kubernetes restarts failed pods, supporting CockroachDB state management.

Next, in we will cover kubernetes and helm basics to prepare for adding a Dapr sidecar to this agent app in Kubernetes, enabling state and pub/sub.
---

## Conclusion

We’ve covered containerization (images, `Dockerfile`, containers) and Kubernetes (pods, Deployments, Services) using Rancher Desktop with the `containerd` engine. With hands-on DACA examples, you’re ready to containerize ai agents with Dapr in Kubernetes, paving the way for scalable AI Agents and Agentic Apps.
