# Helm Tutorial

Below is a detailed tutorial on Helm, the package manager for Kubernetes. This tutorial will cover what Helm is, why it’s useful, how to install it, and how to use it to deploy applications on a Kubernetes cluster. We have broken it down into clear sections for beginners and intermediate users alike.

---

### What is Helm?

Helm is a tool that simplifies the deployment and management of applications on Kubernetes. Think of it as a "package manager" for Kubernetes, similar to how `apt` works for Ubuntu or `npm` for Node.js. Helm uses pre-configured packages called **charts**, which are collections of Kubernetes resource manifests (e.g., Deployments, Services, ConfigMaps) bundled together with customizable variables.

#### Key Concepts
1. **Chart**: A Helm package that contains all the resource definitions needed to run an application, along with a `values.yaml` file for configuration.
2. **Release**: An instance of a chart deployed to a Kubernetes cluster.
3. **Repository**: A place where charts are stored and shared (e.g., Artifact Hub).
4. **Tiller**: The server-side component of Helm (used in Helm 2 but removed in Helm 3 in favor of a client-only architecture).

Helm 3 (the current version) is widely adopted due to its simplicity and improved security over Helm 2.

---

### Why Use Helm?

- **Simplifies Deployment**: Instead of manually applying dozens of YAML files, Helm lets you deploy an app with a single command.
- **Reusability**: Charts can be templated and reused across environments (e.g., dev, staging, prod).
- **Versioning**: Helm tracks releases, allowing you to roll back or upgrade applications easily.
- **Community Support**: Thousands of pre-built charts are available for popular software (e.g., Nginx, MySQL, Prometheus).

---

### Prerequisites

Before starting, ensure you have:
1. A Kubernetes cluster (e.g., Minikube for local testing or a cloud provider like GKE, EKS, or AKS).
2. `kubectl` installed and configured to communicate with your cluster.
3. Basic familiarity with Kubernetes concepts (Pods, Deployments, Services).

---

### Step 1: Install Helm

#### On macOS (using Homebrew)
```bash
brew install helm
```

#### On Linux (using a script)
```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod +x get_helm.sh
./get_helm.sh
```

#### On Windows (using Chocolatey)
```powershell
choco install kubernetes-helm
```

#### Verify Installation
Run the following to check the Helm version:
```bash
helm version
```
Output should look like: `version.BuildInfo{Version:"v3.x.x", ...}`.

---

### Step 2: Set Up a Kubernetes Cluster (Optional)

If you don’t have a cluster, use Minikube for local testing:
```bash
minikube start
```
Verify `kubectl` is working:
```bash
kubectl get nodes
```

---

### Step 3: Explore Helm Commands

Here are some basic Helm commands to get started:
- `helm search hub <keyword>`: Search for charts in Artifact Hub.
- `helm repo add <name> <url>`: Add a chart repository.
- `helm install <release-name> <chart>`: Deploy a chart.
- `helm list`: List all releases in the current namespace.
- `helm upgrade <release-name> <chart>`: Update a release.
- `helm rollback <release-name> <revision>`: Roll back to a previous release.
- `helm uninstall <release-name>`: Delete a release.

---

### Step 4: Deploy Your First Application

Let’s deploy a simple Nginx web server using a Helm chart.

#### 1. Add a Chart Repository
Add the Bitnami repository, which hosts many popular charts:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

#### 2. Search for the Nginx Chart
```bash
helm search repo nginx
```
Look for `bitnami/nginx` in the output.

#### 3. Install the Nginx Chart
Deploy Nginx with the release name `my-nginx`:
```bash
helm install my-nginx bitnami/nginx
```
Helm will output details about the deployment, including how to access it.

#### 4. Verify the Deployment
Check the pods:
```bash
kubectl get pods
```
You should see a pod like `my-nginx-xxxxx`.

#### 5. Access Nginx
The chart creates a Service. Expose it locally with Minikube:
```bash
minikube service my-nginx
```
This opens your browser to the Nginx welcome page.

---

### Step 5: Customize a Chart

Charts are customizable via the `values.yaml` file or command-line overrides.

#### Example: Customize Nginx
1. Inspect the default values:
```bash
helm show values bitnami/nginx
```
2. Create a custom `my-values.yaml` file:
```yaml
replicaCount: 2
service:
  type: LoadBalancer
```
3. Install with custom values:
```bash
helm install my-nginx -f my-values.yaml bitnami/nginx
```
This deploys Nginx with 2 replicas and a LoadBalancer service.

#### Alternative: Inline Overrides
```bash
helm install my-nginx bitnami/nginx --set replicaCount=2,service.type=LoadBalancer
```

---

### Step 6: Manage Releases

#### List Releases
```bash
helm list
```

#### Upgrade a Release
If the chart or values change:
```bash
helm upgrade my-nginx bitnami/nginx --set replicaCount=3
```

#### Roll Back a Release
Check revision history:
```bash
helm history my-nginx
```
Roll back to revision 1:
```bash
helm rollback my-nginx 1
```

#### Uninstall a Release
```bash
helm uninstall my-nginx
```

---

### Step 7: Create Your Own Helm Chart

#### 1. Generate a Chart
```bash
helm create my-chart
```
This creates a directory `my-chart/` with:
- `Chart.yaml`: Metadata about the chart.
- `values.yaml`: Default configuration values.
- `templates/`: Kubernetes manifests with templating.

#### 2. Edit the Chart
Modify `values.yaml`:
```yaml
replicaCount: 1
image:
  repository: nginx
  tag: "latest"
```
Update `templates/deployment.yaml` to use these values (it’s pre-populated with Helm templating).

#### 3. Test the Chart
Dry-run to preview the rendered YAML:
```bash
helm install my-release ./my-chart --dry-run --debug
```

#### 4. Install the Chart
```bash
helm install my-release ./my-chart
```

---

### Step 8: Best Practices

- **Version Control**: Store charts in Git for collaboration.
- **Namespace Management**: Use `--namespace <name>` to isolate releases.
- **Secrets**: Avoid hardcoding sensitive data; integrate with tools like Kubernetes Secrets or external secret managers.
- **Lint Charts**: Run `helm lint ./my-chart` to catch errors.

---

### Troubleshooting

- **Pods Not Starting**: Check logs with `kubectl logs <pod-name>`.
- **Chart Not Found**: Ensure `helm repo update` is run.
- **Permission Issues**: Verify `kubectl` context and RBAC settings.

---

### Next Steps

- Explore advanced templating with Helm’s Go-based syntax.
- Package and share your chart on a repository like Artifact Hub.
- Integrate Helm with CI/CD pipelines (e.g., GitHub Actions).

That’s it! You now have a solid foundation for using Helm to manage Kubernetes applications. 

---

## Helm and Dapr (Distributed Application Runtime)

Helm and Dapr (Distributed Application Runtime) are connected in the context of Kubernetes as complementary tools for deploying and managing applications. Helm is a package manager for Kubernetes, while Dapr is a runtime that simplifies building distributed applications. Their connection lies in how Helm is commonly used to deploy Dapr’s control plane and components onto a Kubernetes cluster, making it easier to integrate Dapr into your application ecosystem. Let’s break this down step-by-step.

---

### What is Helm?

Helm is a tool that streamlines the deployment and management of applications on Kubernetes. It uses **charts**—pre-packaged templates of Kubernetes resources (e.g., Deployments, Services)—to define, install, upgrade, and roll back applications. Helm abstracts away the complexity of writing and managing multiple Kubernetes YAML files, providing a repeatable and versioned deployment process.

---

### What is Dapr?

Dapr is an open-source, event-driven runtime designed to simplify the development of distributed applications, particularly microservices. It provides **building blocks** (e.g., state management, pub/sub, service invocation) that abstract common distributed system challenges. Dapr runs as a **sidecar** alongside your application containers in Kubernetes, interacting via HTTP or gRPC APIs, and its control plane (e.g., `dapr-operator`, `dapr-sidecar-injector`) manages its runtime services.

---

### How Are They Connected?

Helm and Dapr intersect primarily in the deployment phase on Kubernetes:

1. **Deploying Dapr with Helm**:
   - Dapr provides an official Helm chart (`dapr/dapr`) to install its control plane components into a Kubernetes cluster. These components include:
     - `dapr-operator`: Manages Dapr components and configurations.
     - `dapr-sidecar-injector`: Automatically injects Dapr sidecars into application pods.
     - `dapr-placement`: Handles actor placement (if using Dapr’s actor model).
     - `dapr-sentry`: Manages mTLS security between sidecars.
   - Using Helm, you can install Dapr with a single command, specifying configurations like namespace or high-availability mode.

   Example:
   ```bash
   helm repo add dapr https://dapr.github.io/helm-charts/
   helm repo update
   helm install dapr dapr/dapr --namespace dapr-system --create-namespace
   ```

2. **Simplifying Dapr Installation**:
   - Without Helm, you’d need to manually apply multiple Kubernetes manifests to deploy Dapr’s control plane. Helm packages these into a chart, reducing complexity and ensuring consistency.
   - The Helm chart also supports customization via a `values.yaml` file or `--set` flags, allowing you to tweak settings like resource limits, logging levels, or enabling HA mode.

3. **Dapr Sidecar Injection**:
   - Once the Dapr control plane is deployed via Helm, the `dapr-sidecar-injector` watches for pods with specific annotations (e.g., `dapr.io/enabled: "true"`). It then injects the Dapr sidecar container into your application pods. Helm doesn’t manage this injection directly, but it sets up the infrastructure that enables it.

4. **Application Deployment with Dapr**:
   - You can create your own Helm charts for your applications and configure them to work with Dapr. For example, your chart might include annotations to enable Dapr sidecars or reference Dapr components (e.g., a Redis state store).
   - Alternatively, you can use Helm to deploy dependencies like Redis or Kafka alongside Dapr, which Dapr’s building blocks can then leverage.

5. **Upgrades and Rollbacks**:
   - Helm’s upgrade and rollback features apply to Dapr’s control plane. For instance, to upgrade Dapr to a new version:
     ```bash
     helm upgrade dapr dapr/dapr --namespace dapr-system --set global.tag=<new-version>
     ```
   - This ensures Dapr’s runtime evolves without manual manifest edits.

---

### Practical Example

Imagine deploying a microservices app with Dapr on Kubernetes:
1. **Install Dapr**:
   ```bash
   helm install dapr dapr/dapr --namespace dapr-system
   ```
   This sets up Dapr’s control plane.

2. **Deploy a Sample App**:
   Create a Helm chart for a Node.js app with a `values.yaml`:
   ```yaml
   replicaCount: 1
   image:
     repository: my-node-app
     tag: latest
   dapr:
     enabled: true
     appId: my-app
   ```
   And a `deployment.yaml` template:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: {{ .Release.Name }}-deployment
   spec:
     replicas: {{ .Values.replicaCount }}
     selector:
       matchLabels:
         app: {{ .Release.Name }}
     template:
       metadata:
         labels:
           app: {{ .Release.Name }}
         annotations:
           dapr.io/enabled: "{{ .Values.dapr.enabled }}"
           dapr.io/app-id: "{{ .Values.dapr.appId }}"
       spec:
         containers:
         - name: app
           image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
   ```
   Install it:
   ```bash
   helm install my-app ./my-chart
   ```
   The Dapr sidecar is injected automatically thanks to the control plane deployed by Helm.

3. **Verify**:
   ```bash
   kubectl get pods -n default
   ```
   You’ll see your app pod with two containers: your app and the Dapr sidecar.

---

### Key Points of Connection

- **Deployment Tool vs. Runtime**: Helm is a deployment tool, while Dapr is a runtime. Helm deploys Dapr’s infrastructure, and Dapr runs alongside your apps.
- **Complementary Roles**: Helm handles packaging and lifecycle management; Dapr provides distributed system capabilities at runtime.
- **No Direct Runtime Dependency**: Helm isn’t required to use Dapr—you could deploy Dapr with raw YAML or other tools—but Helm is the recommended and most practical method for Kubernetes.

---

### Are They Tightly Coupled?

Not really. Helm is just one way to deploy Dapr. You could use the Dapr CLI (`dapr init -k`) or manual manifests instead. However, Helm’s ease of use and integration with Kubernetes workflows make it a natural fit, especially for production environments where versioning and repeatability matter.

---

### Conclusion

Helm connects to Dapr by serving as the primary mechanism to deploy and manage Dapr’s control plane on Kubernetes. It simplifies the setup process, enabling Dapr’s sidecar architecture to enhance your applications with distributed system features. Together, they form a powerful duo: Helm for deployment, Dapr for runtime capabilities—streamlining the journey from code to a fully operational distributed application.

