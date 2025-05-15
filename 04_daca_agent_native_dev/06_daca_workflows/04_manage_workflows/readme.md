# 05: [Managing Dapr Workflow Instances Theory + Hands On](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-manage-workflow/)

Once workflows are authored and running, you need ways to manage their lifecycle. This section covers using the Dapr Workflow Management API, accessible via the Dapr client SDKs and its HTTP API. Understanding these operations is crucial for building robust and controllable agentic systems. Here we will understand how to 

1. Start a Workflow
2. Get Status
3. Pause it
4. Resume it
5. Terminal/Cancel it.
6. Raise External Event.

Below, we'll first explore the theory behind each key management operation with real-world scenarios and SDK/HTTP examples, and then dive into a complete hands-on example.

---

## Theory

### 1. Starting a New Workflow Instance

- **Concept**: This is the action of initiating a new execution of a predefined workflow. You can optionally assign a unique instance ID for tracking and provide an initial input payload that the workflow can use.
- **Real-World Example**: Imagine an e-commerce platform. When a customer successfully places an order, an "OrderProcessingWorkflow" is started. The instance ID could be the order number (e.g., `order-12345`), and the input would be the order details (customer info, items, shipping address).
  ```json
  {
    "customer_id": "cust-789",
    "items": [{ "id": "item-abc", "quantity": 2 }],
    "shipping_address": "123 Main St"
  }
  ```
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient, DaprWorkflowContext

  # Define your workflow function (this would be defined elsewhere in your actual code,
  # and registered with a WorkflowRuntime instance in a Dapr worker process)
  def OrderProcessingWorkflow(ctx: DaprWorkflowContext, order_details: dict):
      print(f"Order processing workflow started for instance {ctx.instance_id} with data: {order_details}")
      # Example activity call (if you have activities defined and registered):
      # yield ctx.call_activity(process_payment_activity, input=order_details)
      # ... more workflow logic ...
      return {"status": "OrderProcessed", "order_id": order_details.get("customer_id")} # Example output

  dwc = DaprWorkflowClient() # Assumes Dapr sidecar is running on default gRPC port
  instance_id = "order-12345"
  input_payload = {"customer_id": "cust-789", "items": [{"id": "item-abc", "quantity": 2}]}

  # Start the workflow (scheduling it).
  # The 'workflow' parameter is the actual workflow function object.
  # The Dapr runtime will find a worker where this workflow type (its name) is registered.
  started_instance_id = dwc.schedule_new_workflow(
      workflow=OrderProcessingWorkflow, # Pass the function object (its name is used for registration)
      instance_id=instance_id,
      input=input_payload
  )
  print(f"Scheduled workflow, instance ID: {started_instance_id}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  The Dapr sidecar typically listens on HTTP port `3500`.
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '''{"input": {"customer_id": "cust-789", "items": [{"id": "item-abc", "quantity": 2}]}}''' \
    http://localhost:3500/v1.0-alpha1/workflows/dapr/OrderProcessingWorkflow/start?instanceID=order-12345
  ```

---

### 2. Querying Workflow Status and Metadata

- **Concept**: Allows you to retrieve the current status (e.g., `RUNNING`, `COMPLETED`, `FAILED`, `TERMINATED`, `PAUSED`), start time, end time (if completed), last updated time, and any custom status information for a specific workflow instance.
- **Real-World Example**: A user wants to check the status of their "VacationApprovalWorkflow" (instance ID: `vacation-request-jane-doe-001`). They can query its status to see if it's still pending, approved, or rejected.
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient

  dwc = DaprWorkflowClient()
  instance_id = "vacation-request-jane-doe-001"

  # Get the state of the workflow instance
  # The returned object (WorkflowState) has attributes like:
  # instance_id, workflow_name, created_at, last_updated_at, runtime_status, properties
  metadata = dwc.get_workflow_state(instance_id=instance_id)

  print(f"Workflow Instance ID: {metadata.instance_id}")
  print(f"Workflow Name: {metadata.workflow_name}")
  print(f"Runtime Status: {metadata.runtime_status}")
  print(f"Created At: {metadata.created_at}")
  print(f"Last Updated At: {metadata.last_updated_at}")
  # print(f"Input: {metadata.properties.get('dapr.workflow.input')}")
  # print(f"Output: {metadata.properties.get('dapr.workflow.output')}")
  # print(f"Custom Status: {metadata.properties.get('dapr.workflow.custom_status')}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  ```bash
  curl http://localhost:3500/v1.0-alpha1/workflows/dapr/vacation-request-jane-doe-001
  ```
  This will return a JSON response with detailed metadata.

---

### 3. Pausing a Running Workflow

- **Concept**: Temporarily suspends the execution of an ongoing workflow. The workflow's current state is persisted, and it will not proceed with further activities until resumed.
- **Real-World Example**: A "MonthlyFinancialReportWorkflow" (instance ID: `report-oct-2023`) is running, but a critical upstream data source (e.g., a transaction database) needs emergency maintenance. The workflow can be paused to prevent errors or incomplete report generation.
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient

  dwc = DaprWorkflowClient()
  instance_id = "report-oct-2023"

  dwc.pause_workflow(instance_id=instance_id)
  print(f"Paused workflow: {instance_id}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  ```bash
  curl -X POST http://localhost:3500/v1.0-alpha1/workflows/dapr/report-oct-2023/pause
  ```

---

### 4. Resuming a Paused Workflow

- **Concept**: Continues the execution of a previously paused workflow from the exact point where it was suspended.
- **Real-World Example**: After the emergency maintenance on the transaction database is complete, the "MonthlyFinancialReportWorkflow" (instance ID: `report-oct-2023`) can be resumed to continue generating the report.
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient

  dwc = DaprWorkflowClient()
  instance_id = "report-oct-2023"

  dwc.resume_workflow(instance_id=instance_id)
  print(f"Resumed workflow: {instance_id}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  ```bash
  curl -X POST http://localhost:3500/v1.0-alpha1/workflows/dapr/report-oct-2023/resume
  ```

---

### 5. Terminating a Workflow Instance

- **Concept**: Forcibly stops a workflow instance immediately. The workflow is marked as `TERMINATED` and will not complete its defined logic or execute any further activities. This is a non-graceful stop.
- **Real-World Example**: An "AutomatedMarketingCampaignWorkflow" (instance ID: `campaign-fall-sale-002`) was started with an incorrect configuration (e.g., wrong target audience or budget). To prevent further issues or unwanted spending, it can be terminated immediately.
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient

  dwc = DaprWorkflowClient()
  instance_id = "campaign-fall-sale-002"

  dwc.terminate_workflow(instance_id=instance_id)
  print(f"Terminated workflow: {instance_id}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  ```bash
  curl -X POST http://localhost:3500/v1.0-alpha1/workflows/dapr/campaign-fall-sale-002/terminate
  ```

---

### 6. Raising External Events to a Waiting Workflow

- **Concept**: Sends an event with an optional payload to a specific workflow instance that is actively waiting for such an event (typically using `ctx.wait_for_external_event("eventName")` within the workflow definition). This is a key mechanism for human-in-the-loop scenarios or interactions with external systems.
- **Real-World Example**: A "DocumentApprovalWorkflow" (instance ID: `doc-approval-projX-rev2`) is paused, waiting for a manager's decision. The manager reviews the document in a separate UI and clicks an "Approve" or "Reject" button. This action triggers an external system to raise an event (e.g., `DocumentReviewedEvent`) to the workflow instance with the decision.
  Event payload example:
  ```json
  { "approved": true, "comments": "Looks good!", "approver_id": "manager_jane" }
  ```
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient

  dwc = DaprWorkflowClient()
  instance_id = "doc-approval-projX-rev2"
  event_name = "DocumentReviewedEvent"
  event_data = {"approved": True, "comments": "Looks good!", "approver_id": "manager_jane"}

  dwc.raise_workflow_event(
      instance_id=instance_id,
      event_name=event_name,
      event_data=event_data # Use event_data (or 'data' if that's the exact param name for DaprWorkflowClient)
  )
  print(f"Raised event '{event_name}' for workflow: {instance_id}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '''{"approved": true, "comments": "Looks good!", "approver_id": "manager_jane"}''' \
    http://localhost:3500/v1.0-alpha1/workflows/dapr/doc-approval-projX-rev2/raiseEvent/DocumentReviewedEvent
  ```

---

### 7. Purging Workflow Instance History

- **Concept**: Permanently deletes the history and state of a workflow instance from the underlying state store. This is typically done for completed, failed, or terminated workflows to manage storage space and keep the state store lean. Once purged, the workflow instance cannot be queried anymore.
- **Real-World Example**: A system runs a "DailyDataIngestionWorkflow" many times a day. To manage storage costs and performance, workflow instances older than 7 days that are in a `COMPLETED` or `FAILED` state are regularly purged. For instance, purging `ingestion-20231001-run005`.
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient

  dwc = DaprWorkflowClient()
  instance_id = "ingestion-20231001-run005" # A completed or failed instance

  dwc.purge_workflow(instance_id=instance_id)
  print(f"Purged workflow: {instance_id}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  ```bash
  curl -X POST http://localhost:3500/v1.0-alpha1/workflows/dapr/ingestion-20231001-run005/purge
  ```

---

### 8. Waiting for Workflow Completion

- **Concept**: Allows a client to block and wait until a specific workflow instance reaches a terminal state (e.g., `COMPLETED`, `FAILED`, `TERMINATED`). This is useful for synchronous operations that depend on the workflow's outcome. You can specify a timeout.
- **Real-World Example**: A data processing pipeline is triggered as a workflow. A subsequent batch job needs to wait for this pipeline (instance ID: `dataproc-batch-007`) to complete successfully before it can start processing the results. The batch job can use this operation to wait.
- **Using the Dapr Workflow SDK (Python)**:

  ```python
  from dapr.ext.workflow import DaprWorkflowClient
  from dapr.ext.workflow.errors import WorkflowTimeoutException, WorkflowNotFoundException, WorkflowInteractionException # More specific exceptions

  dwc = DaprWorkflowClient()
  instance_id = "dataproc-batch-007"
  timeout_seconds = 60 # Optional timeout

  try:
      # The wait_for_workflow_completion method returns a WorkflowState object
      workflow_state = dwc.wait_for_workflow_completion(
          instance_id=instance_id,
          timeout_in_seconds=timeout_seconds
      )
      print(f"Instance ID: {workflow_state.instance_id}")
      print(f"Runtime Status: {workflow_state.runtime_status}")
      output = workflow_state.properties.get('dapr.workflow.output')
      if output:
          print(f"Output: {output}")
  except WorkflowTimeoutException: # Specifically for timeouts
      print(f"Timeout waiting for workflow {instance_id} to complete after {timeout_seconds} seconds.")
  except WorkflowNotFoundException:
      print(f"Workflow instance {instance_id} not found.")
  except WorkflowInteractionException as e: # General interaction errors
      print(f"Error waiting for workflow {instance_id}: {e}")
  ```

- **Using the Dapr HTTP API (`curl`)**:
  The Dapr HTTP API for workflows does not have a direct equivalent to `wait_for_workflow_completion` that blocks the HTTP call itself until completion. You would typically achieve this by polling the workflow status endpoint:

  1. Start the workflow.
  2. Periodically call `GET http://localhost:3500/v1.0-alpha1/workflows/{workflow_component}/{instance_id}`.
  3. Check the `runtimeStatus`

---

## Hands-On Example: Interactive Workflow Management App

This section provides a complete, runnable FastAPI application that demonstrates all the core workflow management operations. You can use this to experiment with starting, querying, pausing, resuming, terminating, raising events to, and purging workflow instances.

The application defines a simple workflow (`interactive_hello_workflow`) that includes an activity and waits for an external event, making it suitable for testing various management scenarios. Take the lab starter code and test it

### Application Code (`main.py`)

```python
# main.py
import time
import logging

from fastapi import FastAPI, HTTPException, Body, Path, Query
from contextlib import asynccontextmanager
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Workflow Runtime
wfr = WorkflowRuntime()

# --- Workflow and Activity Definitions ---
@wfr.activity(name="interactive_hello_activity")
def interactive_hello_activity(ctx: WorkflowActivityContext, name: str):
    instance_id = ctx.workflow_id # Activity context has workflow_id
    task_id = ctx.task_id
    logger.info(f"Activity (for WF '{instance_id}', Task '{task_id}'): Greeting '{name}'")
    # Simulate work that can be interrupted or take time
    for i in range(10): # Duration of 20s, pausable
        logger.info(f"Activity (WF '{instance_id}'): Working... {i+1}/10")
        time.sleep(2) # Simulate 2 seconds of work per iteration
    return f"Hello, {name}!"

@wfr.workflow(name="interactive_hello_workflow")
def interactive_hello_workflow(ctx: DaprWorkflowContext, user_name: str):
    instance_id = ctx.instance_id
    logger.info(f"WF '{instance_id}': Starting with user '{user_name}'")

    greeting = yield ctx.call_activity(interactive_hello_activity, input=user_name)
    logger.info(f"WF '{instance_id}': Activity said: '{greeting}'")

    logger.info(f"WF '{instance_id}': Now waiting for an 'approvalEvent'")
    try:
        # Wait for an external event with a payload
        event_payload = yield ctx.wait_for_external_event(name="approvalEvent")
        logger.info(f"WF '{instance_id}': Received 'approvalEvent' with payload: {event_payload}")
        final_result = {"initial_greeting": greeting, "event_data": event_payload, "status": "Approved"}
    except TimeoutError:
        logger.warning(f"WF '{instance_id}': Timed out waiting for 'approvalEvent'.")
        final_result = {"initial_greeting": greeting, "event_data": None, "status": "TimedOut"}
    except Exception as e:
        logger.error(f"WF '{instance_id}': Error waiting for event: {e}")
        final_result = {"initial_greeting": greeting, "event_data": None, "status": f"EventError: {str(e)}"}

    logger.info(f"WF '{instance_id}': Workflow completed.")
    return final_result

# --- FastAPI Application Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    wfr.start()
    logger.info("Workflow Runtime (wfr) started successfully.")
    yield
    logger.info("Shutting down Workflow Runtime (wfr)...")
    wfr.shutdown()
    logger.info("Workflow Runtime (wfr) shutdown complete.")

app = FastAPI(
    title="Interactive Workflow Management API",
    description="An API to manage Dapr workflows for hands-on learning.",
    lifespan=lifespan
)

# --- API Endpoints for Workflow Management ---

# 1. Start Workflow Endpoint
@app.post("/workflows/start/{instance_id_suffix}")
async def start_workflow_endpoint(
    instance_id_suffix: str = Path(..., description="Suffix for the workflow instance ID (e.g., 'test1')"),
    user_name: str = Query("User", description="Name to be used as input for the workflow")
):
    client = DaprWorkflowClient()
    instance_id = f"iwf-{instance_id_suffix}" # Construct a unique instance ID
    try:
        logger.info(f"Attempting to schedule workflow '{interactive_hello_workflow.__name__}' with ID '{instance_id}' and input '{user_name}'")
        actual_instance_id = client.schedule_new_workflow(
            workflow=interactive_hello_workflow,
            instance_id=instance_id,
            input=user_name
        )
        logger.info(f"Successfully scheduled workflow with instance ID: {actual_instance_id}")
        return {"message": "Workflow scheduled successfully", "instance_id": actual_instance_id}
    except Exception as e:
        logger.error(f"Error starting workflow {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

# 2. Get Workflow Status Endpoint
@app.get("/workflows/{instance_id}/status")
async def get_workflow_status_endpoint(instance_id: str = Path(..., description="The ID of the workflow instance")):
    client = DaprWorkflowClient()
    try:
        logger.info(f"Fetching status for workflow instance ID: {instance_id}")
        state = client.get_workflow_state(instance_id, fetch_payloads=True)
        if not state:
            logger.warning(f"Workflow instance not found: {instance_id}")
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        logger.info(f"Status for {instance_id}: {state.runtime_status}")
        return state.to_json()
    except Exception as e:
        logger.error(f"Error getting status for workflow {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get workflow status: {str(e)}")

# 3. Pause Workflow Endpoint
@app.post("/workflows/{instance_id}/pause")
async def pause_workflow_endpoint(instance_id: str = Path(..., description="The ID of the workflow instance to pause")):
    client = DaprWorkflowClient()
    try:
        logger.info(f"Attempting to pause workflow: {instance_id}")
        client.pause_workflow(instance_id=instance_id)
        logger.info(f"Successfully requested pause for workflow: {instance_id}")
        return {"message": f"Pause requested for workflow instance {instance_id}"}
    except Exception as e:
        logger.error(f"Error pausing workflow {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to pause workflow: {str(e)}")

# 4. Resume Workflow Endpoint
@app.post("/workflows/{instance_id}/resume")
async def resume_workflow_endpoint(instance_id: str = Path(..., description="The ID of the workflow instance to resume")):
    client = DaprWorkflowClient()
    try:
        logger.info(f"Attempting to resume workflow: {instance_id}")
        client.resume_workflow(instance_id=instance_id)
        logger.info(f"Successfully requested resume for workflow: {instance_id}")
        return {"message": f"Resume requested for workflow instance {instance_id}"}
    except Exception as e:
        logger.error(f"Error resuming workflow {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to resume workflow: {str(e)}")

# 5. Terminate Workflow Endpoint
@app.post("/workflows/{instance_id}/terminate")
async def terminate_workflow_endpoint(instance_id: str = Path(..., description="The ID of the workflow instance to terminate")):
    client = DaprWorkflowClient()
    try:
        logger.info(f"Attempting to terminate workflow: {instance_id}")
        client.terminate_workflow(instance_id=instance_id)
        logger.info(f"Successfully requested termination for workflow: {instance_id}")
        return {"message": f"Termination requested for workflow instance {instance_id}"}
    except Exception as e:
        logger.error(f"Error terminating workflow {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to terminate workflow: {str(e)}")

# 6. Raise Event to Workflow Endpoint
@app.post("/workflows/{instance_id}/raise_event/{event_name}")
async def raise_event_workflow_endpoint(
    instance_id: str = Path(..., description="The ID of the workflow instance"),
    event_name: str = Path(..., description="The name of the event to raise (e.g., 'approvalEvent')"),
    event_data: dict = Body(None, description="JSON payload for the event.")
):
    client = DaprWorkflowClient()
    try:
        logger.info(f"Attempting to raise event '{event_name}' with data '{event_data}' for workflow: {instance_id}")
        client.raise_workflow_event(
            instance_id=instance_id,
            event_name=event_name,
            data=event_data
        )
        logger.info(f"Successfully raised event '{event_name}' for workflow: {instance_id}")
        return {"message": f"Event '{event_name}' raised for workflow instance {instance_id}"}
    except Exception as e:
        logger.error(f"Error raising event for workflow {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to raise event: {str(e)}")

# 7. Purge Workflow Endpoint
@app.post("/workflows/{instance_id}/purge")
async def purge_workflow_endpoint(instance_id: str = Path(..., description="The ID of the workflow instance to purge")):
    client = DaprWorkflowClient()
    try:
        logger.info(f"Attempting to purge workflow: {instance_id}")
        client.purge_workflow(instance_id=instance_id)
        logger.info(f"Successfully requested purge for workflow: {instance_id}")
        return {"message": f"Purge requested for workflow instance {instance_id}"}
    except Exception as e:
        logger.error(f"Error purging workflow {instance_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to purge workflow: {str(e)}")


```

Try the code and test all APIs. You can
1. Start a Workflow
2. Get Status
3. Pause it
4. Resume it
5. Terminal/Cancel it.
6. Raise Event.

ImportantL The line event_payload = yield ctx.wait_for_external_event(name="approvalEvent") will cause the workflow to pause indefinitely, waiting for an external event named "approvalEvent" to be raised for this specific workflow instance.
If this event is never raised, the workflow will remain in a running (suspended) state and will not proceed to the logger.info(f"WF {instance_id}': Workflow completed.") line or the final return statement.

This hands-on example allows you to see each management API in action and observe the workflow's behavior through logs and status checks.
