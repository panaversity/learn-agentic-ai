# S1: Hello, Dapr Workflow! - A DACA AgentCore Introduction

**Workflows aren’t just fancy—they **save you from losing users** when things go wrong (e.g., network drops) and **cut dev time** when you scale up.**

This guide introduces the foundational concepts of Dapr Workflow by implementing a simple "Hello, Workflow!" example. It demonstrates how to define, run, and interact with workflows and activities using the Dapr Python SDK and FastAPI. This serves as an initial step in understanding how DACA utilizes Dapr Workflows for building resilient agentic patterns.

Refer to the official [Dapr Workflow overview](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/) for comprehensive documentation.

## Prerequisites

*   [Dapr (Distributed Application Runtime)](https://dapr.io/) installed.
*   Python 3.x installed.
*   [Tilt](https://tilt.dev/) for running the example (as configured in this project).
*   Basic understanding of FastAPI.

## Running the Example

You can take starter code and code as you follow this or this step code. The project is configured to run with Tilt, which handles building the Docker image and deploying to a local Kubernetes Kind cluster.

```bash
tilt up
```

Once `tilt up` is running, you can access:

*   **Tilt UI**: [http://localhost:10350](http://localhost:10350) (Shows the status of your services)
*   **Application API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs)
*   **Jaeger UI (for tracing, if configured)**: [http://localhost:16686/](http://localhost:16686/)

## Understanding the Code (`main.py`)

The core logic is in `daca-workflow/main.py`. Let's break it down:

### 1. Imports
```python
import time
import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext
```
*   Standard libraries like `time` and `logging`.
*   `FastAPI` and `HTTPException` for building the web API.
*   `asynccontextmanager` for managing the lifespan of the Dapr Workflow Runtime with FastAPI.
*   Key components from `dapr.ext.workflow`:
    *   `WorkflowRuntime`: The engine that executes workflows and activities.
    *   `DaprWorkflowClient`: Used to interact with the workflow runtime (e.g., start workflows, get status).
    *   `DaprWorkflowContext`: Provides context and methods within a workflow definition (e.g., `ctx.instance_id`, `ctx.call_activity`).
    *   `WorkflowActivityContext`: Provides context within an activity definition (e.g., `ctx.workflow_id`, `ctx.task_id`).

### 2. Workflow Runtime Initialization
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()
```
*   Basic logging is configured.
*   `wfr = WorkflowRuntime()`: An instance of the `WorkflowRuntime` is created. This runtime is responsible for discovering and executing registered workflows and activities. Dapr offers this built-in runtime to drive workflow execution.

### 3. Activity Definition (`hello_activity`)

As the [Dapr documentation states](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features/#workflows-and-activities), workflow activities are the basic units of work in a workflow. They are used for performing individual tasks, which can include calling other services (potentially using Dapr service invocation), interacting with state stores, or publishing messages via pub/sub brokers.

```python
@wfr.activity(name="hello_activity")
def hello_activity(ctx: WorkflowActivityContext, name: str):
    logger.info(f"Activity (for WF '{ctx.workflow_id}' and Task '{ctx.task_id}'): Greeting '{name}'")
    time.sleep(10) # Simulate work
    return f"Hello, {name}!"
```

*   `@wfr.activity(name="hello_activity")`: This decorator registers the `hello_activity` function with the Dapr workflow runtime as an "activity." An activity represents a single, discrete step or task.
*   `ctx: WorkflowActivityContext`: The activity function receives a `WorkflowActivityContext` object. This context provides information about the specific task execution, such as the `workflow_id` of the parent workflow that invoked it and the unique `task_id` for this activity execution.
*   `name: str`: This is an input parameter passed to the activity when it's called by a workflow.
*   The body of the activity performs the actual work. In this simple example, it logs a message, simulates a delay using `time.sleep(10)`, and then returns a greeting string. In real-world scenarios, an activity might make a network call, perform a database operation, or execute a complex calculation.
*   Activities are designed to be **idempotent** where possible, meaning calling them multiple times with the same input should ideally produce the same result without unintended side effects. This helps with reliability and retries.

### 4. Workflow Definition (`hello_workflow`)

Dapr Workflows make it easy to write stateful orchestrations, often involving multiple steps or services. They are designed to be **long-running, fault-tolerant, and stateful**. A workflow defines the order and conditions under which activities (or even other child workflows) are executed.

```python
@wfr.workflow(name="hello_workflow")
def hello_workflow(ctx: DaprWorkflowContext, name: str):
    logger.info(f"WF '{ctx.instance_id}': Starting with '{name}'")
    greeting = yield ctx.call_activity(hello_activity, input=name)
    logger.info(f"WF '{ctx.instance_id}': Activity said '{greeting}'")
    return {"final_greeting": greeting}
```

*   `@wfr.workflow(name="hello_workflow")`: This decorator registers the `hello_workflow` function with the Dapr workflow runtime as a "workflow definition."
*   `ctx: DaprWorkflowContext`: The workflow function receives a `DaprWorkflowContext` object. This context is crucial for orchestrating the workflow. It provides:
    *   `ctx.instance_id`: A unique identifier for this particular execution (instance) of the workflow.
    *   Methods to call activities (like `ctx.call_activity()`), schedule timers, wait for external events, and manage child workflows.
*   `name: str`: This is an input parameter for this specific workflow instance, passed when the workflow is started.
*   `greeting = yield ctx.call_activity(hello_activity, input=name)`: This line is the core of the workflow's orchestration logic.
    *   `ctx.call_activity()` is used to invoke the previously defined `hello_activity`.
    *   The `input=name` argument passes the workflow's input (`name`) to the activity.
    *   The `yield` keyword is fundamental to how Dapr Workflows (and the underlying Durable Task Framework) achieve durability. When `yield ctx.call_activity()` is encountered:
        1.  The workflow engine schedules the `hello_activity` for execution.
        2.  The state of the `hello_workflow` (including its current position and local variables) is persisted by Dapr (typically in a configured state store).
        3.  The workflow effectively "pauses" or "goes to sleep."
        4.  When the `hello_activity` completes, the workflow engine reactivates the `hello_workflow` from its last persisted state, and the result of the activity is returned from the `yield` expression and assigned to the `greeting` variable.
    *   This durable persistence and replay mechanism ensures that the workflow can resume correctly even if the application crashes or restarts.
*   The workflow then logs the result from the activity and returns a final dictionary. This return value becomes the output of the workflow instance.

### 5. FastAPI Lifespan Management
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    wfr.start()
    logger.info("Workflow runtime started")
    yield
    wfr.shutdown()
    logger.info("Workflow runtime shutdown")

app = FastAPI(title="Hello Workflow", lifespan=lifespan)
```
*   FastAPI's `lifespan` context manager is used to manage resources during the application's lifecycle.
*   `wfr.start()`: Starts the Dapr Workflow Runtime when the FastAPI application starts. The runtime begins listening for workflow invocations and activity tasks.
*   `yield`: The application runs while the runtime is active.
*   `wfr.shutdown()`: Gracefully shuts down the Dapr Workflow Runtime when the FastAPI application stops.

### 6. FastAPI Endpoints

#### Start Workflow Endpoint
```python
@app.post("/start/{user_name}")
async def start_wf_endpoint(user_name: str):
    client = DaprWorkflowClient()
    try:
        instance_id = client.schedule_new_workflow(workflow=hello_workflow, input=user_name)
        return {"instance_id": instance_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
*   Defines a POST endpoint at `/start/{user_name}`.
*   `client = DaprWorkflowClient()`: Creates a client to interact with the Dapr sidecar's workflow engine. This client uses gRPC to send commands directly to the workflow engine.
*   `instance_id = client.schedule_new_workflow(workflow=hello_workflow, input=user_name)`:
    *   Schedules a new instance of the `hello_workflow`.
    *   The `workflow` parameter takes the workflow function itself.
    *   The `input` parameter passes the `user_name` to the workflow.
    *   It returns a unique `instance_id` for this workflow execution.
*   Learn more about [managing workflows via API](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features/#workflow-http-calls-to-manage-a-workflow).

#### Get Status Endpoint
```python
@app.get("/status/{instance_id}")
async def get_status_endpoint(instance_id: str):
    client = DaprWorkflowClient()
    try:
        state = client.get_workflow_state(instance_id, fetch_payloads=True)
        if not state: raise HTTPException(status_code=404, detail="Not found")
        return state.to_json()
    except Exception as e:
        if "not found" in str(e).lower(): raise HTTPException(status_code=404, detail="Not found")
        raise HTTPException(status_code=500, detail=str(e))
```
*   Defines a GET endpoint at `/status/{instance_id}`.
*   `state = client.get_workflow_state(instance_id, fetch_payloads=True)`:
    *   Retrieves the current state of the specified workflow instance.
    *   `fetch_payloads=True` ensures that the input and output of the workflow are included in the state.
*   `state.to_json()`: Converts the `WorkflowState` object to a JSON string for the HTTP response.

## Interacting with the Workflow

1.  **Start a new workflow:**

    Replace `YOUR_NAME` with any name.

    ```bash
    curl -X POST http://localhost:30080/start/YOUR_NAME
    ```

    This will return a JSON response with the `instance_id`, for example:
    `{"instance_id":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}`

2.  **Check the status of the workflow:**

    Replace `WORKFLOW_INSTANCE_ID` with the ID you received from the previous step.

    ```bash
    curl http://localhost:30080/status/WORKFLOW_INSTANCE_ID
    ```

    This will return a JSON object with the workflow's current status, including `runtime_status` (e.g., "RUNNING", "COMPLETED", "FAILED"), input, output (once completed), and timestamps. Since our activity has a 10-second delay, you might see "RUNNING" initially and then "COMPLETED" if you query after ~10 seconds.

## Key Dapr Workflow Concepts Illustrated

This example demonstrates several fundamental Dapr Workflow concepts:

*   **Workflow Definition**: Orchestrating a sequence of tasks (`hello_workflow`).
*   **Activity Definition**: Implementing individual units of work (`hello_activity`).
*   **Durable Execution**: Workflows are long-running and stateful. The `yield ctx.call_activity` ensures the workflow can pause and resume.
*   **Workflow Runtime**: The engine that executes the defined workflows and activities.
*   **Workflow Client**: The interface for managing workflow instances (starting, querying).
*   **Integration with Application Frameworks**: Using Dapr Workflows within a FastAPI application.

This "Hello, Workflow!" serves as a starting point. Dapr Workflows offer many more advanced features like child workflows, timers, event handling, and error management, which are crucial for building complex, resilient applications in the DACA framework.

## Learning Resources:
- **Primary Quickstart:** [Dapr Workflow Quickstart](https://docs.dapr.io/getting-started/quickstarts/workflow-quickstart/)
- **Python SDK Workflow Examples:** [GitHub - dapr/python-sdk/examples/demo_workflow](https://github.com/dapr/python-sdk/tree/main/examples/demo_workflow)
- **Python SDK Workflow Extension:** [GitHub - dapr/python-sdk/ext/dapr-ext-workflow](https://github.com/dapr/python-sdk/tree/main/ext/dapr-ext-workflow)
- **Dapr Workflow Overview:** [docs.dapr.io - Workflow Overview](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)
- **Dapr Workflow API Reference:** [docs.dapr.io - Workflow API reference](https://docs.dapr.io/reference/api/workflow_api/)
- **How to Author Workflows:** [docs.dapr.io - How-To: Author Workflows](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/)
