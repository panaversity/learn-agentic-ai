# [Pattern 2: Fan-out/Fan-in](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/#fan-outfan-in)

This section demonstrates the **Fan-out/Fan-in** pattern using Dapr Workflows. In this pattern, a workflow executes multiple activities in parallel (fan-out), waits for all of them to complete, and then aggregates their results (fan-in).

## Why Use Fan-out/Fan-in?

This pattern is highly useful for:

*   **Parallel Processing**: Efficiently processing batches of work items simultaneously (e.g., image processing, data transformation on multiple records).
*   **Data Aggregation**: Fetching data from multiple sources concurrently and then combining it.
*   **Improving Performance**: Reducing overall execution time by parallelizing independent tasks.

As the Dapr documentation highlights, implementing this manually can be complex, especially when considering:

*   Controlling the degree of parallelism.
*   Knowing when all parallel tasks have completed to trigger aggregation.
*   Handling a dynamic number of parallel steps.

Dapr Workflows simplify this significantly by allowing you to express the pattern with clear programming constructs, primarily using `wf.when_all()` (in Python) to wait for a list of parallel tasks.

## Conceptual Code Example (from Dapr Docs)

The following Python code illustrates the Fan-out/Fan-in pattern. We will implement a similar structure in our `main.py`.

```python
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
```

**Key Takeaways from the Dapr Docs Example:**

*   The pattern is expressed clearly using standard programming constructs.
*   The number of parallel tasks can be dynamic (based on `work_batch`).
*   The workflow itself handles the aggregation.
*   Dapr ensures durability. If the workflow crashes mid-way, it resumes and only schedules remaining tasks.

## Setup

1.  **Starter Code**: Copy the contents of the `00_starter-code/daca-workflow/` directory into a new directory named `02_fan_in_out/hello-workflow-code/daca-workflow/` (or adapt your existing `01_task_chaining` code if you prefer, ensuring you have a clean base for this pattern).
    The `main.py` in this new directory will be modified.

2.  **Run the Environment**:
    ```bash
    tilt up
    ```

## Access Points

Once `tilt up` is running:

*   **Tilt UI**: [http://localhost:10350](http://localhost:10350) (Service status and logs)
*   **Application API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs) (To start workflows and check status)
*   **Jaeger UI (for tracing, if configured)**: [http://localhost:16686/](http://localhost:16686/) (Visualize workflow execution)

## Next Steps

After understanding this `readme.md`, the next step is to implement the Fan-out/Fan-in logic in the `main.py` file located within your `02_fan_in_out/hello-workflow-code/daca-workflow/` directory.