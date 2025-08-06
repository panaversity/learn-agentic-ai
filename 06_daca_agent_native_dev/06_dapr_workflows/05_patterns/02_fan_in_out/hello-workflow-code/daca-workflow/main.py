import time
import logging

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext, when_all

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

# -------- Workflow Definition --------
@wfr.workflow(name="hello_workflow")
def greet_users_workflow(ctx: DaprWorkflowContext, count: int):
    # 1. Create user names
    user_names = yield ctx.call_activity(generate_user_names, input=count)

    # 2. Fan-out: Greet each user
    greetings = []
    for name in user_names:
        greetings.append(ctx.call_activity(say_hello, input=name))

    # 3. Fan-in: Wait for all greetings
    results = yield when_all(greetings)

    # 4. Combine and return
    return {"greetings": results}


# -------- Activities --------
@wfr.activity(name="generate_users")
def generate_user_names(ctx: WorkflowActivityContext, count: int) -> list[str]:
    return [f"User {i + 1}" for i in range(count)]

@wfr.activity(name="say_hello")
def say_hello(ctx: WorkflowActivityContext, name: str) -> str:
    return f"Hello, {name}!"

    # Do some compensating work
@asynccontextmanager
async def lifespan(app: FastAPI):
    wfr.start()
    logger.info("Workflow runtime started")
    yield
    wfr.shutdown()
    logger.info("Workflow runtime shutdown")

app = FastAPI(title="Hello Workflow", lifespan=lifespan)

@app.post("/start-workflow")
async def start_wf_endpoint(number: int):
    client = DaprWorkflowClient()
    try:
        instance_id = client.schedule_new_workflow(workflow=greet_users_workflow, input=number)
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