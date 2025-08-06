# **Tutorial: Setting Up Kubernetes on a Local Machine for Beginners**

#### **What is Kubernetes?**
Kubernetes (often abbreviated as K8s) is an open-source platform designed to automate the deployment, scaling, and management of containerized applications. It groups containers into logical units called "pods" and provides tools to manage them efficiently. For this tutorial, we'll set it up locally to learn the basics.

---

### **Prerequisites**
Before starting, ensure you have the following:
1. **A computer** with at least 4GB of RAM (8GB recommended) and a multi-core CPU.
2. **Operating System**: Windows, macOS, or Linux (this guide will work for all).
3. **Internet access** for downloading tools.
4. Basic familiarity with the terminal/command line.

---

### **Step 1: Install Required Tools**
To run Kubernetes locally, we’ll use **Minikube**, a tool that runs a single-node Kubernetes cluster on your machine, and **kubectl**, the command-line tool to interact with Kubernetes.

#### **1.1 Install Minikube**
- **Windows**:
  1. Download the Minikube installer from [Minikube’s official site](https://minikube.sigs.k8s.io/docs/start/).
  2. Run the installer or use a package manager like Chocolatey: `choco install minikube`.
- **macOS**:
  1. Use Homebrew: `brew install minikube`.
- **Linux**:
  1. Download the binary: `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64`.
  2. Install it: `sudo install minikube-linux-amd64 /usr/local/bin/minikube`.

#### **1.2 Install kubectl**
- **Windows**:
  1. Download the binary: `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/windows/amd64/kubectl.exe"`.
  2. Move it to a folder in your PATH (e.g., `C:\Users\YourName\bin`).
- **macOS**:
  1. Use Homebrew: `brew install kubectl`.
- **Linux**:
  1. Download: `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"`.
  2. Make it executable and move it: `chmod +x kubectl && sudo mv kubectl /usr/local/bin/`.

#### **1.3 Install a Hypervisor (Optional)**
Minikube needs a virtualization driver. If you don’t have one installed, choose one:
- **Docker Desktop** (simplest, works on all OS): Install from [Docker’s website](https://www.docker.com/products/docker-desktop/).
- **VirtualBox**: Install from [VirtualBox’s site](https://www.virtualbox.org/).
- **Hyper-V** (Windows only): Enable it via Windows Features.

Verify installations:
- `minikube version`
- `kubectl version --client`

---

### **Step 2: Start Minikube**
1. Open your terminal.
2. Start Minikube with the default driver (Docker, if installed):
   ```
   minikube start
   ```
   - If using VirtualBox or another driver, specify it: `minikube start --driver=virtualbox`.
3. Minikube will download a Kubernetes cluster image and set it up. This may take a few minutes.
4. Once complete, you’ll see output like:
   ```
   Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
   ```

Verify the cluster is running:
```
minikube status
```
You should see `host`, `kubelet`, and `apiserver` as "Running."

---

### **Step 3: Explore Kubernetes Basics**
Let’s understand some core concepts:
- **Pod**: The smallest unit in Kubernetes, containing one or more containers.
- **Deployment**: Manages a set of pods, ensuring they’re running and updated.
- **Service**: Exposes pods to the network (e.g., for external access).

Check cluster info:
```
kubectl cluster-info
```
List nodes (your local cluster has one node):
```
kubectl get nodes
```

---

### **Step 4: Deploy a Simple Application**
Let’s deploy a basic web server (NGINX) to practice.

#### **4.1 Create a Deployment**
Run this command to create a deployment named "nginx-deployment":
```
kubectl create deployment nginx-deployment --image=nginx
```
- `nginx` is a lightweight web server image pulled from Docker Hub.

Check the deployment:
```
kubectl get deployments
```
You’ll see something like:
```
NAME              READY   UP-TO-DATE   AVAILABLE   AGE
nginx-deployment   1/1     1            1           10s
```

List the pods:
```
kubectl get pods
```
Output might look like:
```
NAME                               READY   STATUS    RESTARTS   AGE
nginx-deployment-6d9f7b6f5-abcde   1/1     Running   0          20s
```

#### **4.2 Expose the Deployment**
To access the NGINX server, expose it as a service:
```
kubectl expose deployment nginx-deployment --type=NodePort --port=80
```
- `NodePort` makes the service accessible on a specific port of your local machine.

Check the service:
```
kubectl get services
```
Output:
```
NAME              TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
nginx-deployment   NodePort   10.96.0.123   <none>        80:XXXXX/TCP   10s
```
Note the port number (e.g., `XXXXX`, typically between 30000-32767).

#### **4.3 Access the Application**
Get the URL to access your app:
```
minikube service nginx-deployment --url
```
This outputs a URL like `http://192.168.49.2:XXXXX`. Open it in your browser, and you’ll see the NGINX welcome page!

---

### **Step 5: Scale the Application**
Kubernetes makes scaling easy. Increase the number of pods:
```
kubectl scale deployment nginx-deployment --replicas=3
```
Verify:
```
kubectl get pods
```
You’ll see three pods running.

---

### **Step 6: Clean Up**
When you’re done experimenting:
1. Delete the service:
   ```
   kubectl delete service nginx-deployment
   ```
2. Delete the deployment:
   ```
   kubectl delete deployment nginx-deployment
   ```
3. Stop Minikube:
   ```
   minikube stop
   ```
4. (Optional) Delete the cluster:
   ```
   minikube delete
   ```

---

### **Tips for Beginners**
- **Learn YAML**: Kubernetes often uses YAML files to define resources (e.g., deployments). For example, the deployment above could be written as:
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: nginx-deployment
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: nginx
    template:
      metadata:
        labels:
          app: nginx
      spec:
        containers:
        - name: nginx
          image: nginx
  ```
  Save this as `nginx.yaml` and apply it with `kubectl apply -f nginx.yaml`.
- **Use `kubectl describe`**: For detailed info (e.g., `kubectl describe pod <pod-name>`).
- **Explore Minikube Dashboard**: Run `minikube dashboard` to see a web UI.

---

### **Exercises for Students**
- Learn about ConfigMaps, Secrets, and Persistent Volumes.
- Experiment with multi-container pods.



---

### **Tutorial: Deploying a Custom FastAPI App on Kubernetes Locally**

#### **What is FastAPI?**
FastAPI is a modern, fast (high-performance), web framework for building APIs with Python. It’s built on top of Starlette and Pydantic, making it easy to create RESTful APIs with automatic data validation and OpenAPI documentation.

---

### **Prerequisites**
- Minikube and `kubectl` installed (from the previous tutorial).
- **Docker** installed (used to build the app’s container image).
- **Python 3.12+** installed on your local machine.
- Basic terminal knowledge.

---

### **Step 1: Create a Simple FastAPI Application**
Let’s build a basic FastAPI app with a few endpoints.

1. **Set up a project directory**:
   ```
   mkdir fastapi-k8s-demo
   cd fastapi-k8s-demo
   ```

2. **Install FastAPI and Uvicorn**:
   Uvicorn is an ASGI server to run the app. Install them using pip:
   ```
   pip install fastapi uvicorn
   ```

3. **Create the app**:
   Create a file named `main.py` with the following code:
   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/")
   def read_root():
       return {"message": "Welcome to my FastAPI app!"}

   @app.get("/items/{item_id}")
   def read_item(item_id: int, q: str = None):
       return {"item_id": item_id, "q": q}
   ```
   - This app has two endpoints:
     - `/`: Returns a welcome message.
     - `/items/{item_id}`: Takes an integer `item_id` and an optional query parameter `q`.

4. **Test the app locally**:
   Run the app with Uvicorn:
   ```
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Open your browser to `http://localhost:8000`. You should see:
   ```json
   {"message": "Welcome to my FastAPI app!"}
   ```
   Try `http://localhost:8000/items/42?q=test` to see:
   ```json
   {"item_id": 42, "q": "test"}
   ```
   Stop the server with `Ctrl+C`.

---

### **Step 2: Containerize the FastAPI App with Docker**
To deploy to Kubernetes, we need to package the app into a Docker container.

1. **Create a `requirements.txt` file**:
   ```
   fastapi
   uvicorn
   ```

2. **Create a `Dockerfile`**:
   In the same directory, create a file named `Dockerfile` with:
   ```dockerfile
   # Use official Python runtime as the base image
   FROM python:3.9-slim

   # Set working directory in the container
   WORKDIR /app

   # Copy requirements file
   COPY requirements.txt .

   # Install dependencies
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy the app code
   COPY main.py .

   # Expose the port the app runs on
   EXPOSE 8000

   # Command to run the app
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Build the Docker image**:
   Ensure Docker is running, then build the image:
   ```
   docker build -t fastapi-demo:latest .
   ```
   - `fastapi-demo` is the image name, and `latest` is the tag.

4. **Test the container locally**:
   Run the container:
   ```
   docker run -p 8000:8000 fastapi-demo:latest
   ```
   Visit `http://localhost:8000` to confirm it works. Stop it with `Ctrl+C`.

---

### **Step 3: Set Up Minikube**
Start your Minikube cluster if it’s not already running:
```
minikube start
```
Verify it’s running:
```
minikube status
```

Since Minikube runs its own Docker environment, we need to make the image available to it.

1. **Load the Docker image into Minikube**:
   Instead of pushing to a remote registry (e.g., Docker Hub), load the image directly into Minikube’s Docker daemon:
   ```
   minikube image load fastapi-demo:latest
   ```
   Alternatively, set your terminal to use Minikube’s Docker environment:
   ```
   eval $(minikube -p minikube docker-env)
   ```
   Then rebuild the image:
   ```
   docker build -t fastapi-demo:latest .
   ```

---

### **Step 4: Deploy the FastAPI App to Kubernetes**
Now, let’s deploy the app using Kubernetes resources.

#### **4.1 Create a Deployment**
Create a file named `deployment.yaml` with:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 2  # Run 2 instances of the app
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: fastapi-demo:latest
        ports:
        - containerPort: 8000
        imagePullPolicy: Never  # Use local image, don’t pull from a registry
```
Apply it:
```
kubectl apply -f deployment.yaml
```
Check the deployment:
```
kubectl get deployments
```
List pods:
```
kubectl get pods
```

#### **4.2 Expose the Deployment with a Service**
Create a file named `service.yaml` with:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: NodePort
```
Apply it:
```
kubectl apply -f service.yaml
```
Check the service:
```
kubectl get services
```
You’ll see a port mapping like `80:XXXXX/TCP`.

#### **4.3 Access the App**
Get the URL:
```
minikube service fastapi-service --url
```
Open the URL (e.g., `http://192.168.49.2:XXXXX`) in your browser. You should see the welcome message. Test the `/items/42?q=test` endpoint too!

---

### **Step 5: Explore and Scale**
1. **View logs**:
   Find a pod name with `kubectl get pods`, then:
   ```
   kubectl logs <pod-name>
   ```
2. **Scale the app**:
   Increase replicas:
   ```
   kubectl scale deployment fastapi-deployment --replicas=4
   ```
   Verify:
   ```
   kubectl get pods
   ```

3. **Interactive shell**:
   Access a pod’s container:
   ```
   kubectl exec -it <pod-name> -- /bin/bash
   ```
   (Note: `bash` may not be available in slim images; use `sh` instead.)

---

### **Step 6: Clean Up**
When finished:
1. Delete the service:
   ```
   kubectl delete -f service.yaml
   ```
2. Delete the deployment:
   ```
   kubectl delete -f deployment.yaml
   ```
3. Stop Minikube:
   ```
   minikube stop
   ```
4. (Optional) Delete the cluster:
   ```
   minikube delete
   ```

---

### **Tips for FastAPI on Kubernetes**
- **Health Checks**: Add readiness and liveness probes to your deployment for better reliability:
  ```yaml
  livenessProbe:
    httpGet:
      path: /
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 10
  ```
- **Environment Variables**: Use ConfigMaps or Secrets for sensitive data (e.g., API keys).
- **Push to a Registry**: For production, push your image to Docker Hub or another registry instead of loading it locally.

---

### **Exercises for Students**
- Add a database (e.g., PostgreSQL) and connect it to FastAPI.
- Explore Ingress for custom routing.
- Experiment with auto-scaling using HorizontalPodAutoscaler.

