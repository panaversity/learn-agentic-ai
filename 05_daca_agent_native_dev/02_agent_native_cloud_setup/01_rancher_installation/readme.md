# Install [Rancher Desktop](https://docs.rancherdesktop.io/)

This tutorial lays the foundation setup for containerizing our agentic AI microservices with **containers**, **Kubernetes**, and **Rancher Desktop**. We’ll install Rancher Desktop and see how it simplifies `containerd` engine for containers and Kubernetes locally. 

---

## What You’ll Learn
- Install Rancher Desktop
- How Rancher Desktop manages containers with `containerd` and provides a local Kubernetes cluster.
- Download [Rancher Desktop](https://rancherdesktop.io/)

## Prerequisites

- A computer with administrative privileges (macOS, Windows, or Linux).
- Basic command-line familiarity (e.g., Terminal on macOS/Linux, PowerShell on Windows).
- No prior container or Kubernetes experience needed—we start from scratch!
- Recommended: 8 GB RAM, 4 CPUs.

---

## Step 1: Introducing Rancher Desktop

**Rancher Desktop** is a lightweight app for container management and Kubernetes on macOS, Windows, and Linux. It uses `containerd` as the container engine (with `nerdctl` CLI) and includes a built-in Kubernetes cluster (k3s), ideal for DACA’s ACA/Kubernetes focus.

### Why Rancher Desktop?

- **Containers**: Build/run images with `containerd` and `nerdctl`.
- **Kubernetes**: Provides k3s, a low-RAM cluster (2-3 GB).
- **Simplicity**: GUI + CLI for managing containers/pods.
- **DACA Fit**: Prepares for building Daca Agent Actors with Dapr and Kubernetes.

---

## Step 2: [Install Rancher Desktop](https://rancherdesktop.io/)

Let’s install Rancher Desktop to manage containers and Kubernetes, selecting `containerd` as the container engine.

### Step 2.1: System Requirements

- **macOS**: Ventura (13) or higher, 8 GB RAM, 4 CPUs.
- **Windows**: Windows 10/11 (Home OK), WSL 2, 8 GB RAM, 4 CPUs.
- **Linux**: .deb/.rpm/AppImage support, /dev/kvm access, 8 GB RAM, 4 CPUs.
- Internet connection for initial image downloads.

### Step 2.2: Download and Install

1. **Download**:

   - Visit Rancher Desktop releases.
   - Choose your OS:
     - **macOS**: `Rancher.Desktop-X.Y.Z.dmg` (e.g., for M2, aarch64).
     - **Windows**: `Rancher.Desktop.Setup.X.Y.Z.msi`.
     - **Linux**: `.deb`, `.rpm`, or AppImage.

2. **Install**:

   - **macOS**:

     - Open the `.dmg` file.
     - Drag Rancher Desktop to Applications.
     - Launch from Applications.

   - **Windows**:

     - Run the `.msi` installer.
     - Enable WSL 2 if prompted.
     - Choose “Install for all users” for full features.
     - Complete the wizard.

   - **Linux** (e.g., Ubuntu):

     ```bash
     curl -s https://download.opensuse.org/repositories/isv:/Rancher:/stable/deb/Release.key | gpg --dearmor | sudo dd status=none of=/usr/share/keyrings/isv-rancher-stable-archive-keyring.gpg
     echo 'deb [signed-by=/usr/share/keyrings/isv-rancher-stable-archive-keyring.gpg] https://download.opensuse.org/repositories/isv:/Rancher:/stable/deb/ ./' | sudo dd status=none of=/etc/apt/sources.list.d/isv-rancher-stable.list
     sudo apt update
     sudo apt install rancher-desktop
     ```

     - Ensure `/dev/kvm` access:

       ```bash
       [ -r /dev/kvm ] && [ -w /dev/kvm ] || echo 'insufficient privileges'
       sudo usermod -a -G kvm "$USER"
       ```

     - Reboot if needed.

3. **Configure Rancher Desktop**:

   - Launch the app. On first run, a setup window appears:
     - **Enable Kubernetes**: Check this box (enables k3s).
     - **Kubernetes Version**: Select `v1.32.3 (stable, latest)` for stability and Dapr compatibility.
     - **Container Engine**: Select `containerd` (uses `nerdctl` CLI, namespaced images).
     - **Configure PATH**: Choose `Automatic` to add `nerdctl`, `kubectl`, and `helm` to your PATH.
   - Click **OK**. Rancher Desktop downloads k3s images (\~5-10 min first run).

![Rancher Desktop Installation](../install-ranch-dekstop.png)

4. **Verify in GUI**:

   - Open Rancher Desktop and check the Containers, Images, and Kubernetes tabs.

### Step 5.3: Verify Installation

Open a terminal:

```bash
nerdctl --version
```

Output:

```
nerdctl version 2.0.3
```

Verify Kubernetes:

```bash
kubectl version --client
```

Output:

```
Client Version: v1.32.3
Kustomize Version: v5.6.0
```

Check cluster:

```bash
kubectl get nodes
```

Output:

```
NAME                   STATUS   ROLES                  AGE   VERSION
lima-rancher-desktop   Ready    control-plane,master   14m   v1.32.3+k3s1
```

**Note**: If `nerdctl` or `kubectl` commands aren’t found, restart your terminal or ensure PATH is updated (`$HOME/.rd/bin`).

- If kubectl get nodes command fails then you will have to check and configure context to rancher desktop. I faced this issue as a user switching from Docker. Run the following commands to set context and verify it.

```bash
kubectl config current-context
kubectl config get-contexts
kubectl config use-context rancher-desktop
kubectl config current-context
kubectl get nodes
```

---

