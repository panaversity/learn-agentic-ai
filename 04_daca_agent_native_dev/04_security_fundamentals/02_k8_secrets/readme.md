# Securing Sensitive Data with Secrets

Building on the previous section where we externalized non-sensitive configuration with ConfigMaps, this module focuses on securing sensitive data using Kubernetes Secrets. Secrets are designed to store sensitive information like passwords, tokens, or keys, and are intended to work as part of a more comprehensive secrets management solution.

- **Why Use Secrets?**
  - **Handling Sensitive Data**: Secrets are the designated Kubernetes resource for sensitive information, distinguishing it from non-sensitive configuration handled by ConfigMaps.
  - **Decoupling**: Separates sensitive data from application code and configuration files, reducing the risk of accidental exposure in version control or container images.
  - **Standardization**: Provides a consistent way to manage sensitive data within the Kubernetes ecosystem.

- **How Secrets Work**:
  - Secrets store key-value pairs, similar to ConfigMaps.
  - The *value* of a Secret key is stored as base64 encoded data. This *obscures* the value but is **not encryption**.
  - They are typically consumed by pods as environment variables or mounted volumes.
  - When consumed, Kubernetes decodes the base64 value, and it is surfaced as **plain text** inside the container for the application to use.

## Are Kubernetes Secrets Secure (Out-of-the-Box)?

Based on the provided context, the quick answer is **no**, not inherently on their own in a default cluster installation. A *truly* secure secrets management system requires more than just using the `Secret` object. Key considerations include:

* **Encryption at Rest**: By default, Secrets are stored **unencrypted** in the cluster's data store (etcd). Encryption at rest must be explicitly configured using `EncryptionConfiguration`.
* **Encryption in Flight**: Secrets are transferred over the network **unencrypted** to the node where the Pod is scheduled. Securing network traffic (e.g., with a service mesh like Istio or Linkerd using mTLS) is necessary for data in flight.
* **Plain Text in Containers**: Regardless of encryption at rest or in flight, Secrets are always made available as **plain text** inside the container (whether as environment variables or files in a volume) so the application can read them easily.
* **API Access Control**: Restricting who can read Secrets via the Kubernetes API using Role-Based Access Control (RBAC) is crucial.
* **etcd Access Control**: Direct access to the etcd nodes where the cluster state is stored must be strictly controlled.
* **Preventing Exposure**: Sensitive Secret data should never be stored in plain text or even base64 encoded form in source code repositories like GitHub. Secure deletion when no longer needed is also important.

Many production environments leverage **external secrets management solutions** like HashiCorp Vault or cloud provider-specific vaults, often integrated with Kubernetes using the Secrets Store CSI Driver, to handle the complexities of key management, rotation, and auditing.

For the purpose of this lab, we will focus on using the native Kubernetes `Secret` object and understanding its lifecycle and basic usage pattern, keeping in mind the security limitations unless additional cluster security features are configured.

## Typical Secrets Workflow

A typical workflow when using native Kubernetes Secrets:

1.  You create the Secret object (declaratively via YAML or imperatively via `kubectl`). Kubernetes persists it to the cluster store, base64 encoding the data but typically **without encryption** at rest in a default setup.
2.  You schedule a Pod configured to consume the Secret (via environment variable or volume).
3.  Kubernetes transfers the Secret data (potentially unencrypted over the network) to the kubelet on the node running the Pod.
4.  The kubelet starts the Pod and its containers.
5.  The container runtime makes the Secret available:
    * For environment variables, the decoded value is set directly.
    * For volumes, Kubernetes creates a temporary in-memory filesystem (`tmpfs`) in the Pod, writes each Secret key's decoded value into a file within that filesystem, and mounts it into the container.
6.  The application code inside the container reads the Secret data in **plain text**.
7.  When the Pod is deleted, Kubernetes deletes the copy of the Secret data from the node's memory (but keeps the copy in the cluster store unless the Secret object itself is deleted).

## DACA Relevance

Despite the caveats, using Kubernetes Secrets is the standard way to handle sensitive data *within* the cluster environment for DACA agents. This is essential for:

* **API Keys**: Securely providing credentials for external services like Google Gemini, OpenAI, or other cloud APIs used by agents.
* **Database Credentials**: If agents require database access, Secrets store connection strings and credentials.
* **Internal Service Credentials**: Protecting communication between different internal services or agent components if not fully covered by mTLS.

By using Secrets, you decouple sensitive data from code and standard configuration, making your agent deployments more secure than hardcoding credentials, even if additional cluster-level security measures are needed for full protection.

Take the code from the completed `01_configmaps` step as your starter code. Ensure your FastAPI app from the previous step is running via Tilt.

## 1. Secrets Hands On with Environment Variables

Follow these steps to create and use a Secret for a sensitive value, like a placeholder for a Gemini API key, in your FastAPI app:

### Step 1: Create a Secret
1.  **Base64 Encode Your Sensitive Data**: You need to base64 encode the value you want to store. For this example, let's use a dummy value like `your-gemini-api-key-here`. **Remember this is NOT encryption.** In terminal run:
    ```bash
    echo -n "your-gemini-api-key-here" | base64
    ```
    (Replace `"your-gemini-api-key-here"` with your actual key when you move to a more secure environment, but for this lab, a placeholder is fine. Keep the output of this command handy.)


2.  **Create a Secret YAML file**:
    - In your project `kubernetes` directory, create a file named `secret.yaml` with the following content. Replace `[your-base64-encoded-key]` with the output from the previous step.
      ```yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: daca-sensitive-data
        namespace: default # Explicit for clarity or Omit and specify via kubectl -n default
      type: Opaque # Standard type for arbitrary user-defined data
      data:
        gemini_api_key: your-base64-encoded-key # Replace with your base64 encoded key
      ```
    - This Secret defines one key:
      - `gemini_api_key`: Stores the base64 encoded placeholder API key.

3.  **Apply the Secret**:
    - Run the following command to create the Secret in the Kubernetes cluster:
      ```bash
      kubectl apply -f secret.yaml
      ```

    - Get all Secrets:
      ```bash
      kubectl get secrets
      ```
      You should see `daca-sensitive-data` listed.

    - Verify the Secret was created and inspect its structure (note the `data` is base64 encoded). Remember, this `get` command retrieves it from the cluster store, and by default, it's likely unencrypted here.
      ```bash
      kubectl get secret daca-sensitive-data -o yaml
      ```

### Step 2: Update FastAPI Deployment
1.  **Modify the Deployment YAML**:
    - Open `kubernetes/deployment.yaml` and update the `spec` section to include an environment variable sourced from the Secret. Add a new entry to the `env` list within the application container spec:
      ```yaml
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: daca-ai-app
        namespace: default
      spec:
        replicas: 1
        selector:
          matchLabels:
            app: daca-ai-app
        template:
          metadata:
            labels:
              app: daca-ai-app
            annotations:
              dapr.io/enabled: "true"
              dapr.io/app-id: "daca-ai-app"
              dapr.io/app-port: "8000"
              dapr.io/log-level: "info"
          spec:
            containers:
            - name: app
              image: daca-ai-app
              imagePullPolicy: IfNotPresent
              ports:
                - containerPort: 8000
              env:
                # New environment variable from Secret
                - name: GEMINI_API_KEY # Name of the environment variable in the container
                  valueFrom:
                    secretKeyRef:
                      name: daca-sensitive-data # Name of the Secret object
                      key: gemini_api_key      # Key within the Secret data
        volumeMounts:
          - name: volmap
            mountPath: /etc/name
            readOnly: true
      volumes:
        - name: volmap
          configMap:
            name: fastapi-config
      ```
    - The new `env` entry maps the environment variable `GEMINI_API_KEY` inside the container to the value of the `gemini_api_key` key within the `daca-sensitive-data` Secret.

2.  **Update the FastAPI Application Code**:
    - Modify `main.py` to read the `GEMINI_API_KEY` environment variable. **Crucially, do NOT log the value of the API key directly in your application logs.** You can use it internally within your application logic (e.g., to initialize an AI client).
      ```python
      # Read Gemini API Key from environment variable (from Secret)
      # IMPORTANT: Do NOT log this value! It is available in plain text in the container's environment.
      @app.get("/secret")
      def get_secret():
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        return {"gemini_api_key": gemini_api_key}
          # In a real app, you might raise an error or handle this appropriately
      ```
    - This code reads the `GEMINI_API_KEY` environment variable. It includes a check and a log message indicating whether the key was successfully loaded, but *without* printing the key itself. Remember that the key is now present in plain text within the container's environment.

3.  **Rebuild and Redeploy the Application**:
    - If using Tilt, save the changes to `main.py` and `kubernetes/deployment.yaml`. Tilt will automatically rebuild and redeploy the app.

4.  **Verification**:
    - Once the pod is running, open /docs and call the /secret endpoint.
    - You should get the value confirming that the `GEMINI_API_KEY` environment variable is set.
    - **Caution**: For educational purposes, you can execute a shell inside the pod to verify the environment variable, but **be extremely cautious with this in production environments** as it exposes the plain-text secret:
      ```bash
      kubectl exec -it <your-pod-name> -- env | grep GEMINI_API_KEY
      ```
      You should see `GEMINI_API_KEY=your-gemini-api-key-here` (or whatever placeholder you used). This confirms the Secret value was injected correctly as an environment variable and decoded from base64 by Kubernetes.

## 2. Secrets and Volumes Hands On

Secrets can also be mounted as volumes, making each key in the Secret appear as a file in the mounted directory. The content of these files will be the plain text value of the Secret data.

1.  **Modify Deployment YAML (Volumes)**:
    - Update `kubernetes/deployment.yaml` to define a Secret volume and mount it. Add a new volume and volume mount definition (you can add this alongside the environment variables, but typically you'd choose one method for a specific piece of data):
      ```yaml
      # ... (previous parts of deployment.yaml)
          spec:
            containers:
            - name: app
              image: daca-ai-app
              # ... (other container settings)
              volumeMounts:
                # ... (ConfigMap volume mount if still present)
                - name: secret-volume
                  mountPath: /etc/secrets # Choose a secure mount path inside the container
                  readOnly: true # Mounted as read-only by default for security
            volumes:
              # ... (ConfigMap volume if still present)
              - name: secret-volume
                secret:
                  secretName: daca-sensitive-data # Name of your Secret
      ```
    - This configuration will create a directory `/etc/secrets` in the container, containing a file named `gemini_api_key` with the plain text content `your-gemini-api-key-here`.

2.  **Update FastAPI Application Code (Read from Volume)**:
    - Modify `main.py` to read the sensitive data from the mounted file. You can adapt the `read_config` function you might have used for ConfigMap volumes.
      ```python
        @app.get("/secret")
        def get_secret():
            gemini_api_key_vol = read_config("/etc/secrets/gemini_api_key")
            another_secret = read_config("/etc/secrets/name")
            return {"gemini_api_key": gemini_api_key_vol, "another_secret": another_secret}
      ```
    - This approach requires your application to read the content of the mounted file at runtime. The file content is the plain text value of the Secret data.

Choose either the environment variable or the volume mount method based on your application's needs and how it expects to consume sensitive data. Environment variables are often simpler for single key-value pairs like an API key, while volumes are useful for full configuration files or multiple keys presented as individual files. For this module, sticking with environment variables is sufficient to demonstrate the core concept, but understanding volumes is also valuable.

## Reflection
- **What are the key differences between Kubernetes ConfigMaps and Secrets, particularly regarding their intended use and security implications?**
  - ConfigMaps are for non-sensitive configuration; Secrets are for sensitive data. Secrets use base64 encoding (obfuscation, not encryption) and are surfaced as plain text in containers. Default Secrets are typically unencrypted at rest and in flight, unlike ConfigMaps which have no specific security features.
- **Why is base64 encoding not sufficient for protecting highly sensitive data in Secrets, and what additional measures are necessary for a truly secure solution?**
  - Base64 is just encoding; it's easily reversible. True security requires encryption at rest (etcd encryption), encryption in flight (e.g., service mesh), strong RBAC, secure etcd access, and ideally, integration with external vaults for robust key management and auditing.
- **How does using Kubernetes Secrets (even with their limitations) improve the security posture of a DACA agent deployment compared to hardcoding credentials in code or configuration files?**
  - Secrets prevent sensitive credentials from being checked into source control, significantly reducing the risk of accidental exposure. They provide a centralized mechanism for managing secrets within the cluster, which is a foundational step towards a more secure deployment, even if further security layers are needed.

## DACA Context
Securing API keys and other credentials for external AI services (like Gemini, OpenAI) or internal resources is critical for the security and integrity of DACA agents. Using Kubernetes Secrets provides a standard method to inject these sensitive values into agent pods without embedding them in images or configuration files. While recognizing the security limitations of default Secrets, this practice is a necessary step towards building secure cloud-native agents. Integrating with more advanced secrets management solutions would be a next logical step in a production DACA environment.

## Next Steps
- With configuration (ConfigMaps) and sensitive data (Secrets) management covered, proceed to **API-endpoint Security with JWT/OAuth2 Scopes** to learn how to secure the network endpoints of your DACA FastAPI application itself.

## Resources
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Kubernetes Security Concepts - Secrets](https://kubernetes.io/docs/concepts/security/#secrets)
- [Encrypting Secret Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Base64 Explained](https://www.freecodecamp.org/news/what-is-base64-encoding-explained/)