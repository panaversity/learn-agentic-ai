# DAPR Theory and CLI

Let's proceed with the fourth tutorial in the **Dapr Agentic Cloud Ascent (DACA)** series. In this tutorial, we’ll focus on introducing **Dapr** (Distributed Application Runtime), a key component of DACA, and provide a comprehensive guide to the **Dapr CLI**. We’ll cover the theory behind Dapr, its building blocks, and how it simplifies building distributed systems. Then, we’ll dive into the Dapr CLI, exploring its commands with practical examples. We won’t carry forward the code examples from previous tutorials here, but we’ll set the stage for integrating Dapr with our microservices in the next tutorial.

---

## Understanding Dapr, Mastering the Dapr CLI, and Exploring the Dapr Scheduler

Welcome to the fourth tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll explore **Dapr** (Distributed Application Runtime), a powerful framework that simplifies building distributed, cloud-native applications. Dapr is a cornerstone of DACA’s architecture, enabling seamless inter-service communication, state management, and more. We’ll start with a comprehensive introduction to Dapr, its architecture, and its building blocks. Then, we’ll dive into the **Dapr CLI**, covering its installation, key commands, and practical usage examples. This tutorial will prepare you to integrate Dapr with our microservices in the next step. Let’s get started!

---

## What You’ll Learn
- What Dapr is, its architecture, and its role in DACA.
- The core building blocks of Dapr and how they address distributed system challenges.
- How to install and set up the Dapr CLI.
- A comprehensive guide to the Dapr CLI, with practical examples of its commands.
- What the Dapr Scheduler is, its role in Dapr, and how to manage it using the Dapr CLI.

## Prerequisites
- Basic familiarity with distributed systems concepts (e.g., microservices, messaging).
- A development environment with Docker installed (Dapr uses Docker for its runtime).
- Familiarity with the command line.

---

## Step 1: Introduction to Dapr
### What is Dapr?
**Dapr** (Distributed Application Runtime) is an open-source, portable runtime for building distributed applications, particularly microservices. Launched by Microsoft in 2019, Dapr provides a set of **building blocks** that abstract common distributed system challenges, such as service-to-service communication, state management, and pub/sub messaging. Dapr runs as a **sidecar** alongside your application, enabling you to focus on business logic while Dapr handles the complexities of distributed systems.

#### Key Features of Dapr
- **Language Agnostic**: Dapr works with any programming language (e.g., Python, Go, Java) via HTTP or gRPC APIs.
- **Sidecar Architecture**: Dapr runs as a separate process (sidecar) next to your app, providing isolation and portability.
- **Building Blocks**: Standardized APIs for common distributed system patterns (e.g., state, pub/sub, service invocation).
- **Pluggable Components**: Dapr supports multiple backends (e.g., Redis, Kafka, Postgres) for each building block, configurable via YAML files.
- **Cloud-Native**: Designed for containerized environments like Kubernetes, but also works locally.

#### Dapr Architecture
Dapr follows a **sidecar pattern**:
- **Application**: Your microservice (e.g., a FastAPI app).
- **Dapr Sidecar**: A separate process running alongside your app, providing Dapr’s APIs.
- **Dapr APIs**: Your app communicates with the Dapr sidecar via HTTP or gRPC (e.g., `http://localhost:3500/v1.0/invoke`).
- **Components**: Dapr interacts with external systems (e.g., Redis for state, RabbitMQ for pub/sub) via pluggable components.

For example:
- Your FastAPI app makes an HTTP call to the Dapr sidecar to save state.
- The Dapr sidecar forwards the request to a configured state store (e.g., Redis).
- The sidecar handles retries, errors, and other complexities transparently.

#### Why Dapr for DACA?
Dapr is a perfect fit for DACA’s goals of building scalable, resilient, agentic AI systems:
- **Simplified Communication**: Dapr’s service invocation and pub/sub building blocks streamline inter-service communication between microservices (e.g., Chat Service and Analytics Service).
- **State Management**: Dapr manages state for stateless services, aligning with DACA’s stateless container design.
- **Resilience**: Dapr provides retries, timeouts, and circuit breakers, ensuring fault tolerance in distributed systems.
- **Scalability**: Dapr integrates seamlessly with Kubernetes, supporting DACA’s planet-scale deployment stage.
- **Flexibility**: Dapr’s pluggable components allow us to use free-tier services (e.g., Upstash Redis, CloudAMQP) during prototyping.

---

## Step 2: Dapr Building Blocks
Dapr provides a set of **building blocks** that address common challenges in distributed systems. Each building block is accessible via a standardized API, and Dapr supports multiple implementations (components) for each block. Here’s an overview of the key building blocks relevant to DACA:

1. **Service Invocation**:
   - Enables direct, synchronous communication between services.
   - Dapr handles service discovery, retries, and load balancing.
   - Example: The Chat Service calls the Analytics Service to fetch user data.

2. **State Management**:
   - Provides a key-value store for managing state (e.g., user sessions, message counts).
   - Supports multiple backends (e.g., Redis, CockroachDB).
   - Example: Store a user’s message count in Dapr’s state store instead of a mock dictionary.

3. **Publish/Subscribe (Pub/Sub)**:
   - Enables asynchronous, event-driven communication between services.
   - Supports message brokers like RabbitMQ, Kafka, and Redis.
   - Example: The Chat Service publishes a “MessageSent” event, and the Analytics Service subscribes to update message counts.

4. **Bindings**:
   - Connects applications to external systems (e.g., HTTP endpoints, databases) via input/output bindings.
   - Example: Trigger a service when a new message arrives in a queue.

5. **Actors**:
   - Implements the actor model for stateful, concurrent processing.
   - Example: Use actors to manage individual user sessions with encapsulated state.

6. **Workflows**:
   - Orchestrates long-running workflows with retries and compensation logic.
   - Example: Coordinate a multi-step process (e.g., user message → analytics update → response).

7. **Secrets**:
   - Securely manages secrets (e.g., API keys, database credentials).
   - Example: Store the OpenAI API key in Dapr’s secret store.

8. **Configuration**:
   - Manages application configuration (e.g., feature flags).
   - Example: Toggle agentic features dynamically.

9. **Observability**:
   - Provides tracing, logging, and metrics for monitoring.
   - Example: Trace requests between the Chat Service and Analytics Service using Zipkin.

In DACA, we’ll primarily use **Service Invocation**, **State Management**, **Pub/Sub**, **Workflows**, and **Observability** to build our agentic AI system.

---

## Step 3: Installing the Dapr CLI
The **Dapr CLI** is the primary tool for interacting with Dapr, allowing you to initialize Dapr, run applications with Dapr sidecars, manage components, and more. Let’s install and set up the Dapr CLI.

### Install the Dapr CLI
#### On macOS/Linux
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

#### On Windows (PowerShell)
```powershell
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

#### Verify Installation
Check the Dapr CLI version:
```bash
dapr --version
```
Output:
```
CLI version: 1.13.1
Runtime version: n/a
```
The runtime version is `n/a` because we haven’t initialized Dapr yet.

### Install the Dapr Runtime
The Dapr CLI requires the Dapr runtime to be installed on your system. This includes the Dapr sidecar and its dependencies (e.g., Redis for default components).

#### Initialize Dapr
Run the following command to initialize Dapr:
```bash
dapr init
```
This command:
- Downloads and installs the Dapr runtime binaries.
- Sets up a default Redis container for state and pub/sub components.
- Configures default component files in `~/.dapr/components/`.

Output:
```
⌚  Making the jump to hyperspace...
ℹ  Installing runtime version 1.13.1
⬇  Downloading binaries and setting up components...
✅  Success! Dapr has been installed to /usr/local/bin. To get started, please visit https://docs.dapr.io/getting-started/
ℹ  Container images for Dapr have been pulled to your local machine
ℹ  Dapr control plane has been initialized in your local environment
ℹ  Note: To verify that Dapr has been installed properly, restart your terminal session
```

#### Verify Dapr Runtime
Check the Dapr runtime version:
```bash
dapr --version
```
Output:
```
CLI version: 1.13.1
Runtime version: 1.13.1
```

Check that the Dapr Redis container is running:
```bash
docker ps
```
You should see a container named `dapr_redis` running on port `6379`.

---

## Step 4: Comprehensive Guide to the Dapr CLI
The Dapr CLI provides a rich set of commands for managing Dapr applications, components, and runtime. Let’s explore the most important commands with practical examples.

### 1. `dapr init`
- **Purpose**: Initializes Dapr on your machine.
- **Usage**:
  ```bash
  dapr init
  ```
- **What It Does**:
  - Installs the Dapr runtime.
  - Pulls Docker images for Dapr’s control plane and default components (e.g., Redis).
  - Creates a `~/.dapr/` directory with default configuration and components.

#### Example: Reinitialize Dapr
If you need to reinitialize Dapr (e.g., after uninstalling):
```bash
dapr init --runtime-version 1.13.1
```
The `--runtime-version` flag specifies the Dapr version to install.

---

### 2. `dapr uninstall`
- **Purpose**: Removes Dapr from your machine.
- **Usage**:
  ```bash
  dapr uninstall
  ```
- **What It Does**:
  - Stops and removes Dapr containers (e.g., Redis).
  - Deletes Dapr binaries and configuration files.

#### Example: Uninstall Dapr
```bash
dapr uninstall --all
```
The `--all` flag also removes Docker images and volumes.

---

### 3. `dapr run`
- **Purpose**: Runs an application with a Dapr sidecar.
- **Usage**:
  ```bash
  dapr run --app-id <app-id> --app-port <port> --dapr-http-port <dapr-port> -- <command>
  ```
- **Options**:
  - `--app-id`: A unique identifier for your application.
  - `--app-port`: The port your app listens on.
  - `--dapr-http-port`: The port for the Dapr sidecar’s HTTP API.
  - `<command>`: The command to run your app (e.g., `uvicorn main:app`).

#### Example: Run a Simple Python App with Dapr
Create a simple FastAPI app in a new directory to test `dapr run`:
```bash
mkdir dapr-test-app
cd dapr-test-app
uv init
uv add fastapi uvicorn
```

Create `main.py`:
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Dapr Test App!"}
```

Run the app with Dapr:
```bash
dapr run --app-id test-app --app-port 8000 --dapr-http-port 3500 -- uv run uvicorn main:app --host 0.0.0.0 --port 8000
```
- `test-app` is the app ID.
- `8000` is the app port.
- `3500` is the Dapr sidecar port (default for Dapr’s HTTP API).

Output:
```
== APP == INFO:     Started server process [12345]
== APP == INFO:     Waiting for application startup.
== APP == INFO:     Application startup complete.
== APP == INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
ℹ  Starting Dapr with id test-app. HTTP Port: 3500  gRPC Port: 50001
✅  You're up and running! Both Dapr and your app logs will appear here.
```

Visit `http://localhost:8000/` to confirm the app is running:
```json
{"message": "Hello from Dapr Test App!"}
```

---

### 4. `dapr dashboard`
- **Purpose**: Opens the Dapr dashboard, a web UI for monitoring Dapr applications.
- **Usage**:
  ```bash
  dapr dashboard
  ```
- **What It Does**:
  - Starts a web server (default port `8080`).
  - Provides a UI to view running Dapr apps, components, and logs.

#### Example: Open the Dapr Dashboard
While the test app is running, open a new terminal and run:
```bash
dapr dashboard
```
Output:
```
ℹ  Starting Dapr Dashboard on http://localhost:8080
```

Visit `http://localhost:8080` in your browser. You’ll see:
- The `test-app` application with its Dapr sidecar.
- Configured components (e.g., Redis for state and pub/sub).
- Logs and health status.

---

### 5. `dapr components`
- **Purpose**: Lists the Dapr components configured in your environment.
- **Usage**:
  ```bash
  dapr components
  ```
- **What It Does**:
  - Displays the components defined in `~/.dapr/components/` (or a custom components directory).

#### Example: List Components
```bash
dapr components
```
Output:
```
  NAME           TYPE           CREATED
  statestore     state.redis    2025-04-06 10:00:00
  pubsub         pubsub.redis   2025-04-06 10:00:00
```
These are the default components created by `dapr init`, using Redis as the backend.

---

### 6. `dapr configurations`
- **Purpose**: Lists the Dapr configurations (e.g., tracing settings).
- **Usage**:
  ```bash
  dapr configurations
  ```
- **What It Does**:
  - Displays the configurations defined in `~/.dapr/config.yaml`.

#### Example: List Configurations
```bash
dapr configurations
```
Output:
```
  NAME        TRACING-ENABLED  TRACING-EXPORTER
  dapr        true             zipkin
```
The default configuration enables tracing with Zipkin.

---

### 7. `dapr stop`
- **Purpose**: Stops a running Dapr application.
- **Usage**:
  ```bash
  dapr stop --app-id <app-id>
  ```
- **What It Does**:
  - Stops the Dapr sidecar and the associated app process.

#### Example: Stop the Test App
Stop the `test-app` we started earlier:
```bash
dapr stop --app-id test-app
```
Output:
```
✅  Stopped app with id: test-app
```

---

### 8. `dapr list`
- **Purpose**: Lists all running Dapr applications.
- **Usage**:
  ```bash
  dapr list
  ```
- **What It Does**:
  - Displays the app ID, app port, Dapr HTTP/gRPC ports, and runtime status of running apps.

#### Example: List Running Apps
First, restart the test app:
```bash
cd dapr-test-app
dapr run --app-id test-app --app-port 8000 --dapr-http-port 3500 -- uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

In a new terminal, run:
```bash
dapr list
```
Output:
```
  APP ID     HTTP PORT  GRPC PORT  APP PORT  COMMAND                          AGE  CREATED              STATUS
  test-app   3500       50001      8000      uv run uvicorn main:app --ho...  10s  2025-04-06 10:05:00  Running
```

---

### 9. `dapr invoke`
- **Purpose**: Invokes a method on a Dapr application (tests service invocation).
- **Usage**:
  ```bash
  dapr invoke --app-id <app-id> --method <method> --data <data>
  ```
- **What It Does**:
  - Sends an HTTP request to the Dapr sidecar, which forwards it to the specified app method.

#### Example: Invoke the Root Endpoint
With the test app running, invoke the `/` endpoint:
```bash
dapr invoke --app-id test-app --method / --data '{}'
```
Output:
```
{"message":"Hello from Dapr Test App!"}
```
The `--method /` corresponds to the `GET /` endpoint in our FastAPI app.

---

### 10. `dapr publish`
- **Purpose**: Publishes a message to a pub/sub topic.
- **Usage**:
  ```bash
  dapr publish --pubsub <pubsub-name> --topic <topic> --data <data>
  ```
- **What It Does**:
  - Publishes a message to the specified topic using the configured pub/sub component.

#### Example: Publish a Message
Publish a message to a topic named `messages` using the default `pubsub` component:
```bash
dapr publish --pubsub pubsub --topic messages --data '{"message": "Hello, Dapr!"}'
```
Output:
```
✅  Published data: {"message": "Hello, Dapr!"}
```
Since no service is subscribed to this topic yet, the message is sent to Redis but not consumed. We’ll explore pub/sub in a later tutorial.

---

### 11. `dapr status`
- **Purpose**: Shows the status of the Dapr control plane.
- **Usage**:
  ```bash
  dapr status
  ```
- **What It Does**:
  - Displays the health of Dapr system services (e.g., daprd, placement).

#### Example: Check Dapr Status
```bash
dapr status
```
Output:
```
  NAME            HEALTHY  VERSION  AGE  CREATED
  daprd           True     1.13.1   1h   2025-04-06 10:00:00
  placement       True     1.13.1   1h   2025-04-06 10:00:00
  sentry          True     1.13.1   1h   2025-04-06 10:00:00
  operator        True     1.13.1   1h   2025-04-06 10:00:00
```

---

## Step 5: Why Dapr CLI for DACA?
The Dapr CLI is essential for DACA because:
- **Local Development**: Commands like `dapr run` and `dapr dashboard` simplify local testing of microservices with Dapr sidecars.
- **Debugging**: `dapr list`, `dapr invoke`, and `dapr publish` help test and debug service interactions.
- **Component Management**: `dapr components` and `dapr configurations` allow us to configure Dapr for different environments (e.g., local Redis, CloudAMQP in production).
- **Production Readiness**: Commands like `dapr status` ensure the Dapr runtime is healthy before deployment.


---

## Step 6: Introduction to the Dapr Scheduler
### What is the Dapr Scheduler?
The **Dapr Scheduler** is a control plane service introduced in Dapr 1.14 (September 2024) to manage scheduled jobs, actor reminders, and workflows. It’s designed to improve the scalability and performance of scheduling tasks in Dapr, addressing limitations of earlier approaches (e.g., using the Placement service for actor reminders). The Scheduler service runs as a separate process in both self-hosted and Kubernetes environments, storing job data in an embedded **etcd** database for persistence and reliability.

#### Key Features of the Dapr Scheduler
- **Job Scheduling**: Supports the **Jobs API**, allowing applications to schedule tasks to run at a specific time or on a recurring schedule (e.g., database backups, email notifications).
- **Actor Reminders**: Since Dapr 1.15 (March 2025), the Scheduler manages actor reminders by default, improving scalability over the previous Placement service approach.
- **Workflow Support**: Enhances the **Workflow API** by managing reminders and timers for long-running processes.
- **High Availability (HA)**: In Kubernetes, the Scheduler always runs in HA mode with multiple replicas for load balancing. In self-hosted mode, HA is optional but recommended for production.
- **Load Balancing**: All Scheduler replicas are peers (no leader), and jobs are distributed across replicas for efficient execution.
- **Persistence**: Jobs and reminders are stored in an embedded etcd database, ensuring they survive restarts (if properly configured).

#### How the Dapr Scheduler Works
1. **Scheduling a Job**:
   - An application uses the Jobs API (via HTTP/gRPC) to schedule a job, specifying details like name, schedule, repeats, and data payload.
   - The Dapr sidecar forwards the job to the Scheduler service, which stores it in etcd.
2. **Triggering a Job**:
   - At the scheduled time, the Scheduler sends the job back to the Dapr sidecar via a streaming connection.
   - The sidecar delivers the job to the application, which executes the associated business logic.
3. **Error Handling**:
   - Client-side errors (e.g., app fails to process the job) trigger retries (default: 3 retries with a 1-second interval).
   - Non-client-side errors (e.g., no available sidecar) place the job in a staging queue until a sidecar is available.

#### Dapr Scheduler in DACA
The Dapr Scheduler is crucial for DACA because:
- **Agentic AI Workflows**: DACA’s agentic AI systems often require scheduled tasks (e.g., periodic data updates, timed agent actions), which the Scheduler handles efficiently.
- **Scalability**: The Scheduler’s HA mode and load balancing align with DACA’s goal of planetary-scale deployment.
- **Reliability**: Persistent storage in etcd ensures that scheduled jobs and reminders aren’t lost during failures, supporting DACA’s resilience requirements.

---

## Step 7: Managing the Dapr Scheduler with the Dapr CLI
The Dapr CLI provides tools to interact with the Scheduler service, especially for monitoring and debugging. Let’s explore how to manage the Scheduler using CLI commands.

### 7.1 Verify the Scheduler Service is Running
The Scheduler service is automatically started as part of `dapr init` (or `dapr init -k` for Kubernetes). Let’s confirm it’s running.

#### Check Running Containers
Since the Scheduler runs as a Docker container in self-hosted mode, use Docker to verify:
```bash
docker ps
```
Output (look for the Scheduler container):
```
CONTAINER ID   IMAGE                        COMMAND                  CREATED        STATUS        PORTS     NAMES
abc123def456   daprio/dapr:1.13.1           "./scheduler"            1 hour ago     Up 1 hour             dapr_scheduler
xyz789ghi012   redis:7                      "docker-entrypoint.s…"   1 hour ago     Up 1 hour     6379/tcp  dapr_redis
```
The `dapr_scheduler` container runs the Scheduler service, and `dapr_redis` supports default components.

#### Check Dapr Status
Use the `dapr status` command to check the health of Dapr control plane services, including the Scheduler:
```bash
dapr status
```
Output:
```
  NAME            HEALTHY  VERSION  AGE  CREATED
  daprd           True     1.13.1   1h   2025-04-06 04:00:00
  placement       True     1.13.1   1h   2025-04-06 04:00:00
  sentry          True     1.13.1   1h   2025-04-06 04:00:00
  operator        True     1.13.1   1h   2025-04-06 04:00:00
  scheduler       True     1.13.1   1h   2025-04-06 04:00:00
```
The `scheduler` service should be listed as `HEALTHY`. Note: The version here is 1.13.1 for illustration, but as of April 2025, you’d likely be using Dapr 1.15 or later, where the Scheduler is enabled by default for actor reminders.

### 7.2 View Scheduler Logs
To debug or monitor the Scheduler, you can view its logs via Docker.

#### Find the Scheduler Container ID
```bash
docker ps
```
Note the `CONTAINER ID` for `dapr_scheduler` (e.g., `abc123def456`).

#### View Logs
```bash
docker logs abc123def456
```
Output (example):
```
time="2025-04-06T04:00:00Z" level=info msg="Dapr Scheduler starting up..."
time="2025-04-06T04:00:01Z" level=info msg="Connected to etcd database"
time="2025-04-06T04:00:02Z" level=info msg="Scheduler service running in non-HA mode"
```
This confirms the Scheduler is running and connected to its etcd database. In a production setup, you’d configure HA mode for better reliability.

### .73 Test the Jobs API with `dapr publish`
The Scheduler manages jobs scheduled via the **Jobs API**. While we can’t directly schedule a job using the CLI (this requires an application using the Jobs API), we can simulate a related interaction by publishing a message to a pub/sub topic, which could trigger a job in a real application. Let’s use the `dapr publish` command to demonstrate this concept.

#### Publish a Message
Publish a message to a topic named `schedule-job`, simulating an event that might trigger a job:
```bash
dapr publish --pubsub pubsub --topic schedule-job --data '{"job_name": "test-job", "schedule": "@every 1m"}'
```
Output:
```
✅  Published data: {"job_name": "test-job", "schedule": "@every 1m"}
```
This message is sent to the default `pubsub` component (Redis). In a real application, a service subscribed to this topic could schedule a job using the Jobs API, which the Scheduler would then manage. We’ll implement this pattern in the next tutorial.

### 7.4 Check Scheduler Configuration in the Dashboard
The Dapr dashboard provides a UI to monitor the Scheduler and other services.

#### Open the Dashboard
```bash
dapr dashboard
```
Visit `http://localhost:8080` in your browser. Navigate to the **Control Plane** section to see the Scheduler service listed alongside other services (e.g., placement, sentry). You can also check logs and health status here.

### 7.5 Simulate a Scheduler Interaction with a Test App
To see the Scheduler in action, let’s create a minimal application that schedules a job using the Jobs API. This will give us a practical example of how the Scheduler works, and we’ll use the CLI to run and monitor it.

#### Create a Simple Go App
The Jobs API is currently best supported in the Go SDK (as of Dapr 1.15). Let’s create a small Go app to schedule a job.

Create a new directory:
```bash
mkdir dapr-scheduler-test
cd dapr-scheduler-test
go mod init dapr-scheduler-test
go get github.com/dapr/go-sdk@v1.10.0
```

Create `main.go`:
```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/dapr/go-sdk/service/common"
	daprd "github.com/dapr/go-sdk/service/http"
)

func main() {
	// Start a Dapr service
	s := daprd.NewService(":8080")

	// Register a job event handler
	if err := s.AddJobEventHandler("test-job", jobHandler); err != nil {
		log.Fatalf("Failed to register job event handler: %v", err)
	}

	// Schedule a job
	job := &common.Job{
		Name:     "test-job",
		DueTime:  "5s", // Run after 5 seconds
		Repeats:  2,    // Repeat twice
		Data:     &common.Any{Value: []byte(`{"message": "Hello from test job!"}`)},
	}
	if err := s.ScheduleJob(context.Background(), job); err != nil {
		log.Fatalf("Failed to schedule job: %v", err)
	}

	fmt.Println("Job scheduled: test-job")

	// Start the server
	if err := s.Start(); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func jobHandler(ctx context.Context, job *common.JobEvent) error {
	var data map[string]string
	if err := json.Unmarshal(job.Data, &data); err != nil {
		return fmt.Errorf("failed to unmarshal job data: %v", err)
	}
	fmt.Printf("Job triggered at %s: %s\n", time.Now().Format(time.RFC3339), data["message"])
	return nil
}
```

#### Run the App with Dapr
Use `dapr run` to start the app with a Dapr sidecar:
```bash
dapr run --app-id scheduler-test --app-port 8080 --dapr-http-port 3500 -- go run main.go
```
Output:
```
== APP == Job scheduled: test-job
ℹ  Starting Dapr with id scheduler-test. HTTP Port: 3500  gRPC Port: 50001
✅  You're up and running! Both Dapr and your app logs will appear here.
== APP == Job triggered at 2025-04-06T05:27:05Z: Hello from test job!
== APP == Job triggered at 2025-04-06T05:27:10Z: Hello from test job!
```
The job runs 5 seconds after scheduling, repeats once, and then stops (as specified by `Repeats: 2`).

#### Monitor with `dapr list`
While the app is running, check the running Dapr apps:
```bash
dapr list
```
Output:
```
  APP ID          HTTP PORT  GRPC PORT  APP PORT  COMMAND         AGE  CREATED              STATUS
  scheduler-test  3500       50001      8080      go run main.go  10s  2025-04-06 05:27:00  Running
```

#### Stop the App
```bash
dapr stop --app-id scheduler-test
```
Output:
```
✅  Stopped app with id: scheduler-test
```

This example demonstrates how the Scheduler manages jobs scheduled via the Jobs API, and how the Dapr CLI helps run and monitor the application.

---

## Step 8: Why Dapr Scheduler for DACA?
The Dapr Scheduler enhances DACA’s architecture by:
- **Efficient Scheduling**: Handles timed tasks for agentic AI (e.g., periodic data syncs, scheduled agent actions).
- **Scalability**: HA mode and load balancing ensure the Scheduler can handle DACA’s planet-scale workloads.
- **Reliability**: Persistent storage in etcd prevents job loss, aligning with DACA’s resilience goals.
- **Integration with Workflows**: Supports DACA’s agentic workflows by managing reminders and timers.

---

### Exercises for Students
1. Create a custom Dapr component (e.g., a state store using a different backend like in-memory) and list it with `dapr components`.
2. Use `dapr invoke` to test a POST endpoint on the test app (hint: add a POST endpoint to `main.py`).
3. Explore Dapr’s tracing by enabling Zipkin and viewing traces in the Dapr dashboard.
4. Modify the Go app to schedule a recurring job (e.g., every 10 seconds) and observe the Scheduler’s behavior.
5. Use `docker logs` to investigate the Scheduler’s behavior when a job fails (e.g., stop the app before the job triggers).
6. Explore the Dapr dashboard’s **Control Plane** section to view Scheduler metrics and logs in more detail.

---

## Conclusion
In this tutorial, we introduced Dapr, explored its building blocks, and provided a comprehensive guide to the Dapr CLI. We then extended the tutorial to cover the Dapr Scheduler, a control plane service for managing scheduled jobs, actor reminders, and workflows. We demonstrated how to verify the Scheduler’s status, view its logs, and interact with it using CLI commands like `dapr status`, `dapr publish`, and `dapr run`. We also created a simple Go app to schedule a job, showcasing the Scheduler in action. You’re now ready to integrate Dapr with our microservices in the next tutorial!

---

