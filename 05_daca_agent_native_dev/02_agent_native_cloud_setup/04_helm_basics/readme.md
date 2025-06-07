# Hands-on Helm (Basics)

This guide provides a practical introduction to Helm, the package manager for Kubernetes. It covers the theory, verification of Helm installation, understanding Helm charts, and basic Helm commands for managing charts. We'll use an analogy to explain Helm charts and demonstrate installing an NGINX chart. 

- Note: This guide focuses on basics to get you ready for dapr, so we won't cover chart creation or advanced templating.

## 1. What is Helm?

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. It allows you to define, install, and upgrade complex Kubernetes applications using pre-configured packages called **charts**. Think of Helm as a tool that streamlines the process of deploying applications on Kubernetes, much like `apt` for Ubuntu or `Homebrew` for macOS.

Helm provides:
- A way to package Kubernetes manifests (like Deployments, Services, ConfigMaps) into a single chart.
- Tools to manage these charts, including installation, upgrades, and rollbacks.
- A repository system to share and discover charts.

## 2. Verifying Helm Installation

Since Helm is already installed with Rancher, we need to verify it's available. Run the following command to check the Helm version:

```bash
helm version
```

This should output something like:

```
version.BuildInfo{Version:"v3.x.x", GitCommit:"...", GitTreeState:"...", GoVersion:"..."}
```

If you see this, Helm is installed and ready. If not, consult your Rancher documentation to ensure Helm is properly set up.

## 3. Understanding Helm Charts

### Analogy: Helm Charts as Recipes

Imagine you're cooking a complex dish, like a multi-layer cake. Instead of gathering ingredients and following a long recipe from scratch, you buy a pre-packaged cake mix. The mix includes all the dry ingredients, instructions, and maybe even frosting—just add water, eggs, and oil. Helm charts are like these cake mixes for Kubernetes:

- **Ingredients**: Kubernetes resources (e.g., Pods, Services, ConfigMaps).
- **Instructions**: Templates that define how these resources are configured.
- **Customization**: Values you provide to tweak the recipe (e.g., changing the cake flavor or Kubernetes service type).

**Why use Helm charts?**
- **Simplicity**: Charts bundle all Kubernetes resources into a single package, reducing manual configuration.
- **Reusability**: Install the same chart multiple times with different configurations (e.g., multiple NGINX instances).
- **Versioning**: Easily upgrade or roll back to specific chart versions.
- **Community**: Access a wide range of pre-built charts on Artifact Hub.

### Exploring Artifact Hub

Artifact Hub (https://artifacthub.io) is a centralized repository for finding Helm charts. It hosts charts from various sources, like Bitnami, which maintains high-quality, well-documented charts. For example, you can find charts for NGINX, Drupal, or WordPress. We'll use the Bitnami NGINX chart for our hands-on example.

## 4. Hands-on: Installing an NGINX Chart

Let’s walk through the process of installing the Bitnami NGINX chart using Helm. We’ll cover adding a repository, searching for the chart, installing it, and managing the installation.

### Step 1: Add the Bitnami Repository

Helm 3 doesn’t come with default repositories, so we need to add the Bitnami repository:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
```

Verify the repository was added:

```bash
helm repo list
```

Output:
```
NAME    URL
bitnami https://charts.bitnami.com/bitnami
```

Update the repository cache to get the latest charts:

```bash
helm repo update
```

### Step 2: Search for the NGINX Chart

Search for the NGINX chart in the Bitnami repository:

```bash
helm search repo nginx
```

Output (example):
```
NAME            CHART VERSION   APP VERSION     DESCRIPTION
bitnami/nginx   19.1.1          1.27.5          NGINX Open Source is a web server that can be a...
```

To see available versions:

```bash
helm search repo nginx --versions
```

This lists all chart versions and their corresponding NGINX app versions.

### Step 3: Install the NGINX Chart

Install the NGINX chart with the installation name `my-nginx` in the `default` namespace:

```bash
helm install my-nginx bitnami/nginx
```

This command:
- Downloads the chart from the Bitnami repository.
- Renders the chart’s templates with default values.
- Deploys the resulting Kubernetes resources (e.g., Deployment, Service).

After installation, Helm provides instructions to access the NGINX service. For example, if it’s exposed via a `ClusterIP` service, you may need to use `kubectl port-forward` to access it locally:

```bash
kubectl port-forward svc/my-nginx 8080:80
```

Then visit `http://localhost:8080` in your browser to see the NGINX welcome page.

### Step 4: List Installed Charts

Check the installed Helm releases:

```bash
helm list
```

Output (example):
```
NAME      NAMESPACE REVISION UPDATED               STATUS   CHART         APP VERSION
my-nginx  default   1        2025-04-24 10:00:00   deployed nginx-19.1.1 1.27.5
```

### Step 5: Upgrade the Installation

To upgrade the chart (e.g., to a newer version or with new configuration), use:

```bash
helm upgrade my-nginx bitnami/nginx --set service.type=LoadBalancer
```

This changes the NGINX service type to `LoadBalancer`. You can also specify a different chart version with `--version <version>`.

### Step 6: Uninstall the Chart

When you’re done, remove the installation:

```bash
helm uninstall my-nginx
```

This deletes all Kubernetes resources associated with the `my-nginx` release.

## 5. Key Helm Commands

Here’s a summary of essential Helm commands for managing charts:

- **Repository Management**:
  ```bash
  helm repo add <name> <url>    # Add a chart repository
  helm repo list                # List added repositories
  helm repo update              # Update repository cache
  ```

- **Search and Discover**:
  ```bash
  helm search repo <keyword>    # Search for charts
  helm search repo <keyword> --versions  # List all versions
  ```

- **Installation and Management**:
  ```bash
  helm install <release-name> <chart>  # Install a chart
  helm list                           # List installed releases
  helm upgrade <release-name> <chart>  # Upgrade a release
  helm uninstall <release-name>       # Delete a release
  ```

- **Debugging**:
  ```bash
  helm install <release-name> <chart> --dry-run  # Simulate installation
  helm template <release-name> <chart>           # Render templates locally
  ```

- **Release Information**:
  ```bash
  helm get all <release-name>  # Get details about a release
  helm history <release-name>  # View release history
  ```

## 6. Conclusion

This hands-on guide introduced Helm, verified its installation with Rancher, explored Helm charts using an NGINX example, and covered essential Helm commands. Helm simplifies Kubernetes application management by packaging resources into reusable, versioned charts. By leveraging repositories like Bitnami on Artifact Hub, you can quickly deploy applications like NGINX, Drupal, or WordPress.

For further learning, explore Artifact Hub for more charts or experiment with custom values to configure installations. This guide avoids chart creation and advanced templating, but those are great next steps for mastering Helm.