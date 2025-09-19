import time
import logging

from datetime import timedelta
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext
from dapr.ext.workflow import RetryPolicy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

retry_policy = RetryPolicy(
    first_retry_interval=timedelta(seconds=1),
    max_number_of_attempts=3,
    backoff_coefficient=2,
    max_retry_interval=timedelta(seconds=10),
    retry_timeout=timedelta(seconds=100),
)

flaky_activity_call_count = 0

@wfr.activity(name="flaky_activity")
def flaky_activity(ctx: WorkflowActivityContext, data: str):
    logger.info(f"Flaky Activity (for WF '{ctx.workflow_id}'): Attempting with '{data}'")
    # a global variable to track the number of times the activity has been called
    global flaky_activity_call_count
    # Simulate a 50% chance of failure
    if flaky_activity_call_count < 3:
        flaky_activity_call_count += 1
        logger.warning(f"\n\n[STIMULATING FAILURE]:\n\n Flaky Activity (for WF '{ctx.workflow_id}'): Simulating failure!")
        raise ValueError("Simulated random failure in flaky_activity")
    flaky_activity_call_count = 0
    result = f"Successfully processed by flaky_activity: {data}"
    logger.info(f"Flaky Activity (for WF '{ctx.workflow_id}'): {result}")
    return result

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
    flaky_result = yield ctx.call_activity(
        flaky_activity,
        input=name,
        retry_policy=retry_policy
    )
    logger.info(f"WF '{ctx.instance_id}': Flaky activity succeeded: '{flaky_result}'")
    return {"final_greeting": greeting, "flaky_result": flaky_result}

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