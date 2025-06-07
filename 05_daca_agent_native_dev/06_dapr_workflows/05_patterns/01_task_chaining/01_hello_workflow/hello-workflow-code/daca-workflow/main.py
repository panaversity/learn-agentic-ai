import time
import logging

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

@wfr.workflow(name='random_workflow')
def task_chain_workflow(ctx: DaprWorkflowContext, wf_input: int):
    try:
        result1 = yield ctx.call_activity(step1, input=wf_input)
        result2 = yield ctx.call_activity(step2, input=result1)
        result3 = yield ctx.call_activity(step3, input=result2)
    except Exception as e:
        yield ctx.call_activity(error_handler, input=str(e))
        raise
    # TODO update to set custom status
    return [result1, result2, result3]


@wfr.activity(name='step10')
def step1(ctx, activity_input):
    print(f'Step 1: Received input: {activity_input}.')
    # Do some work
    return activity_input + 1


@wfr.activity
def step2(ctx, activity_input):
    print(f'Step 2: Received input: {activity_input}.')
    # Do some work
    return activity_input * 2


@wfr.activity
def step3(ctx, activity_input):
    print(f'Step 3: Received input: {activity_input}.')
    # Do some work
    return activity_input - 2


@wfr.activity
def error_handler(ctx, error):
    print(f'Executing error handler: {error}.')
    # Do some compensating work
@asynccontextmanager
async def lifespan(app: FastAPI):
    wfr.start()
    logger.info("Workflow runtime started")
    yield
    wfr.shutdown()
    logger.info("Workflow runtime shutdown")

app = FastAPI(title="Hello Workflow", lifespan=lifespan)

@app.post("/start-chaining-workflow")
async def start_wf_endpoint(number: int):
    client = DaprWorkflowClient()
    try:
        instance_id = client.schedule_new_workflow(workflow=task_chain_workflow, input=number)
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