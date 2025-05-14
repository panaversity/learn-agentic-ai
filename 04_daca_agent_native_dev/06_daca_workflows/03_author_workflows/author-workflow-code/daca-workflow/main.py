import time
import logging

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

@wfr.activity(name="always_fail_activity")
def always_fail_activity(ctx: WorkflowActivityContext, data: str):
    logger.error(f"Always Fail Activity (WF '{ctx.workflow_id}'): Raising exception for input '{data}'")
    raise ValueError(f"This activity always fails with input: {data}")

@wfr.activity(name="compensation_activity")
def compensation_activity(ctx: WorkflowActivityContext, error_info: dict):
    logger.info(f"Compensation Activity (WF '{ctx.workflow_id}'): Compensating for error: {error_info.get('error_message')}")
    return f"Compensation logic executed for: {error_info.get('failed_activity')}"

@wfr.workflow(name="error_handling_workflow")
def error_handling_workflow(ctx: DaprWorkflowContext, task_data: str):
    logger.info(f"ErrorHandling WF '{ctx.instance_id}': Starting with '{task_data}'")
    ctx.set_custom_status("Attempting risky operation.")
    activity_result = None
    compensation_result = None
    try:
        activity_result = yield ctx.call_activity(always_fail_activity, input=task_data)
        ctx.set_custom_status("Risky operation succeeded (unexpectedly!).")
    except Exception as e: # Catching a general exception; be more specific if possible
        logger.error(f"ErrorHandling WF '{ctx.instance_id}': Activity 'always_fail_activity' failed: {e}")
        ctx.set_custom_status(f"Caught error: {e}. Performing compensation.")
        
        # Call a compensating activity
        compensation_input = {"failed_activity": "always_fail_activity", "error_message": str(e)}
        compensation_result = yield ctx.call_activity(compensation_activity, input=compensation_input)
        
        ctx.set_custom_status(f"Compensation done: {compensation_result}. Workflow will now fail.")
        # Option: Re-raise the exception if the workflow itself should be marked as FAILED
        # raise WorkflowFailureError(f"Workflow failed after compensation due to: {e}") from e
        # Or, if compensation means success, return a success status.
        # For this example, let's consider compensation as handling, but the overall operation failed.
        # To mark workflow as FAILED, you'd typically re-raise or raise a specific workflow error.
        # If not re-raised, the workflow will complete successfully from its perspective.
        # For true failure propagation, re-raising is common.
        # raise # This will mark the workflow as FAILED

    if activity_result:
            return {"status": "SUCCESS_UNEXPECTED", "result": activity_result}
    else:
            return {"status": "HANDLED_FAILURE", "compensation": compensation_result, "original_input": task_data}

@asynccontextmanager
async def lifespan(app: FastAPI):
    wfr.start()
    logger.info("Workflow runtime started")
    yield
    wfr.shutdown()
    logger.info("Workflow runtime shutdown")

app = FastAPI(title="Hello Workflow", lifespan=lifespan)

@app.post("/start/{user_name}")
async def start_wf_endpoint(user_name: str):
    client = DaprWorkflowClient()
    try:
        instance_id = client.schedule_new_workflow(workflow=error_handling_workflow, input=user_name)
        return {"instance_id": instance_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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