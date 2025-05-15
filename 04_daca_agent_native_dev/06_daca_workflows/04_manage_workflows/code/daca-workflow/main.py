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

