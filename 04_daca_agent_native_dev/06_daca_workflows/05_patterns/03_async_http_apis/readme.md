# [Pattern 3: Async HTTP APIs](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/#async-http-apis)

This section explores how Dapr Workflows inherently support the **Asynchronous HTTP API** pattern (also known as the Asynchronous Request-Reply pattern). This is crucial for long-running operations initiated via an HTTP request, where the client cannot wait synchronously for the full process to complete.

## The Challenge of Async HTTP APIs

Traditionally, implementing this pattern involves several components and complexities:

1.  **Start API**: An initial HTTP endpoint that receives the request.
2.  **Backend Queue**: The Start API often writes a message to a queue to trigger the long-running operation.
3.  **Immediate Response (HTTP 202)**: The Start API immediately returns an HTTP `202 Accepted` response, usually with a unique identifier (e.g., a URL or an ID) that the client can use to poll for status.
4.  **Status API**: A separate endpoint that clients poll to check the status of the long-running operation.
5.  **State Store**: A database or cache to store the status of the operation.
6.  **Client Polling Logic**: The client needs to implement logic to repeatedly poll the Status API.

This is illustrated by the Dapr documentation:

> *(Diagram showing how the async request response pattern works - Reference from Dapr Docs)*

## How Dapr Workflows Simplify This

Dapr Workflows provide out-of-the-box support for the asynchronous request-reply pattern via their standard HTTP management APIs, significantly reducing the amount of custom code and infrastructure you need to manage.

When you start a Dapr workflow (whether through the Dapr HTTP API directly or via the Dapr Workflow SDK which calls these APIs):

1.  **Initiation**: The call to start the workflow (e.g., via `DaprWorkflowClient.schedule_new_workflow()` in Python, or a direct POST to `http://localhost:3500/v1.0/workflows/dapr/<WORKFLOW_NAME>/start`) is an instruction to the Dapr sidecar.
2.  **Instance ID**: Dapr returns an `instanceID` for the newly scheduled workflow. This `instanceID` is the key to tracking its progress.
3.  **Status Polling**: Clients can then use this `instanceID` to poll a generic Dapr workflow status endpoint: `http://localhost:3500/v1.0/workflows/dapr/<INSTANCE_ID>`.
4.  **Standardized Status**: This endpoint provides a consistent JSON response including the `runtimeStatus` (e.g., `RUNNING`, `COMPLETED`, `FAILED`, `TERMINATED`), input, and output (once completed).

Our application's `main.py` will define the workflow and an endpoint to start it. The async HTTP API pattern is then leveraged by how a client interacts with our endpoint and subsequently with Dapr's generic status endpoint.

## Workflow

## Conceptual `main.py` Code for Async HTTP API Demo

To demonstrate this pattern, our `main.py` will define a simple workflow and an endpoint to start it. The key is that once our application's endpoint schedules the workflow via the Dapr SDK, the subsequent status polling leverages Dapr's built-in HTTP APIs.

Here's what the relevant parts of `main.py` would look like:

```python
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext

# Basic Pydantic model for input
class OrderPayload(BaseModel):
    itemName: str
    quantity: int

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

# --- Workflow and Activity Definitions ---
@wfr.activity(name="process_order_activity")
def process_order_activity(ctx: WorkflowActivityContext, order_data: dict):
    instance_id = ctx.workflow_id # Activity can access workflow instance ID
    logger.info(f"Activity (for WF '{instance_id}'): Processing order for {order_data.get('itemName')}")
    # Simulate some long-running work
    time.sleep(15) # Simulate a 15-second process
    logger.info(f"Activity (for WF '{instance_id}'): Finished processing order for {order_data.get('itemName')}")
    return {"processed": True, "item": order_data.get('itemName'), "message": "Order processed successfully"}

@wfr.workflow(name="AsyncOrderProcessingWorkflow")
def async_order_processing_workflow(ctx: DaprWorkflowContext, order_input: dict):
    instance_id = ctx.instance_id
    logger.info(f"Workflow '{instance_id}': Started processing order: {order_input}")
    
    # Call an activity
    result = yield ctx.call_activity(
        process_order_activity,
        input=order_input
    )
    
    logger.info(f"Workflow '{instance_id}': Order processing activity completed. Result: {result}")
    return result

# --- FastAPI Application Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        wfr.start()
        logger.info("Workflow Runtime started.")
    except Exception as e:
        logger.warning(f"Workflow Runtime might already be started or failed to start: {e}")

    yield # Application runs

    try:
        wfr.shutdown()
        logger.info("Workflow Runtime stopped.")
    except Exception as e:
        logger.warning(f"Workflow Runtime failed to shutdown gracefully: {e}")


app = FastAPI(title="Async HTTP API Demo with Dapr Workflow", lifespan=lifespan)

@app.post("/start-async-order")
async def start_order_workflow_endpoint(order: OrderPayload):
    client = DaprWorkflowClient()
    try:
        # Schedule the workflow
        instance_id = client.schedule_new_workflow(
            workflow=async_order_processing_workflow,
            input=order.model_dump() # Pass Pydantic model as dict
        )
        logger.info(f"Successfully scheduled workflow 'AsyncOrderProcessingWorkflow' with instance ID: {instance_id}")
        return {"instance_id": instance_id}
    except Exception as e:
        logger.error(f"Error scheduling workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/status/{instance_id}")
async def get_workflow_status(instance_id: str):
    client = DaprWorkflowClient()
    status = client.get_workflow_state(instance_id)
    return status.to_json()
```

This snippet shows:
*   A simple `AsyncOrderProcessingWorkflow` and its `process_order_activity`.
*   The `process_order_activity` includes a `time.sleep(15)` to simulate a long-running task.
*   A FastAPI endpoint `/start-async-order` that takes an `OrderPayload`, schedules the workflow, and returns the `instance_id`.
*   Basic logging and error handling.
*   The `lifespan` manager for starting/stopping the workflow runtime and registering components.

## Setup

1.  **Starter Code**: Copy the contents of the `00_starter-code/daca-workflow/` directory into `03_async_http_apis/hello-workflow-code/daca-workflow/`.
    We will modify its `main.py` to include a simple workflow (e.g., one that takes some input and has a short delay, similar to `01_hello_workflow`).

2.  **Run the Environment**:
    ```bash
    tilt up
    ```

## Access Points

*   **Tilt UI**: [http://localhost:10350](http://localhost:10350)
*   **Application API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs) (To use our application's endpoint that starts the workflow).
*   **Dapr Sidecar Workflow Endpoints**: Directly accessible via `curl` or Postman on `http://localhost:3500` (for status polling).
*   **Jaeger UI**: [http://localhost:16686/](http://localhost:16686/)

## Implementing and Running the Async HTTP API Example

1.  **Modify `main.py`**:
    *   Define a simple workflow (e.g., `AsyncDemoWorkflow`) that perhaps takes an input, performs an activity with a `time.sleep()`, and returns a result.
    *   Register this workflow and its activity.
    *   Create a FastAPI endpoint in your application (e.g., `/start-async-demo`) that takes input data, schedules `AsyncDemoWorkflow` using `DaprWorkflowClient`, and returns the `instance_id`.

2.  **Start the Workflow via Your App's Endpoint**:
    *   Use Swagger UI or `curl` to POST to your app's `/start-async-demo` endpoint with some JSON payload.
    *   Your app should return a JSON response like: `{"instance_id": "your-workflow-instance-id"}`.

3.  **Poll for Status using Dapr's Generic Endpoint**:
    *   Using `curl` or Postman, make GET requests to `http://localhost:3500/v1.0/workflows/dapr/your-workflow-instance-id`.
    *   Observe the `runtimeStatus` field. Initially, it should be `RUNNING`.
    *   Continue polling every few seconds. Eventually, it should change to `COMPLETED` (or `FAILED` if there was an issue).

4.  **Observe Output**: Once `COMPLETED`, the response from the Dapr status endpoint will also contain the `dapr.workflow.output` property with your workflow's result.

## Next Steps

After understanding this `readme.md`, proceed to implement the described workflow and endpoint in the `main.py` file within `03_async_http_apis/hello-workflow-code/daca-workflow/`.