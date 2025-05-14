import time
import logging

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

@wfr.activity(name="child_task_activity")
def child_task_activity(ctx: WorkflowActivityContext, item_to_process: str):
    logger.info(f"Child Activity (for WF '{ctx.workflow_id}'): Processing item '{item_to_process}'")
    return f"Item '{item_to_process}' processed by child activity."

@wfr.workflow(name="child_orchestration_workflow")
def child_orchestration_workflow(ctx: DaprWorkflowContext, data_for_child: str):
    logger.info(f"Child WF '{ctx.instance_id}': Starting with '{data_for_child}'")
    activity_result = yield ctx.call_activity(child_task_activity, input=data_for_child)
    logger.info(f"Child WF '{ctx.instance_id}': Child activity said '{activity_result}'")
    return f"Child WF '{ctx.instance_id}' completed. Result: {activity_result}"


@wfr.workflow(name="hello_workflow") 
def hello_workflow(ctx: DaprWorkflowContext, name: str):
    logger.info(f"Parent WF '{ctx.instance_id}': Starting, will call child workflow for '{name}'")
    
    child_input = f"Data for child from {name}"
    # Optional: define a deterministic child ID
    child_instance_id = f"{ctx.instance_id}-child-{name.replace(' ', '_')}" 
    
    logger.info(f"Parent WF '{ctx.instance_id}': Calling child_orchestration_workflow with ID '{child_instance_id}'.")
    child_output = yield ctx.call_child_workflow(
        child_orchestration_workflow,
        input=child_input,
        instance_id=child_instance_id 
    )
    logger.info(f"Parent WF '{ctx.instance_id}': Child workflow output: '{child_output}'")
    
    return {"parent_result": f"Processed '{name}'", "child_result": child_output}

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
        instance_id = client.schedule_new_workflow(workflow=hello_workflow, input=user_name)
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