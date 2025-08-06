import time
import logging

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

@wfr.activity(name="hello_activity")
def hello_activity(ctx: WorkflowActivityContext, name: str):
    logger.info(f"Activity (for WF '{ctx.workflow_id}' and Task '{ctx.task_id}'): Greeting '{name}'")
    time.sleep(10) # Simulate work - EXPERIMENT BY INCREASING THIS TIME
    return f"Hello, {name}!"

@wfr.workflow(name="hello_workflow")
def hello_workflow(ctx: DaprWorkflowContext, name: str):
    logger.info(f"WF '{ctx.instance_id}': Starting with '{name}'")
    greeting = yield ctx.call_activity(hello_activity, input=name)
    logger.info(f"WF '{ctx.instance_id}': Activity said '{greeting}'")
    return {"final_greeting": greeting}

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