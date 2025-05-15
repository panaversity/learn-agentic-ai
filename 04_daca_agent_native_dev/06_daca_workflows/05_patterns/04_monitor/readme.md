# [Pattern 4: Monitor](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/#monitor)

This section details the **Monitor** pattern, a common design for processes that need to periodically check a status, perform an action based on that status, wait for a defined interval, and then repeat the cycle. Dapr Workflows provide an elegant way to implement such recurring, potentially long-lived processes.

## Understanding the Monitor Pattern

The core loop of a monitor is:
1.  **Check Status**: Query the state of a system, entity, or resource.
2.  **Take Action**: Based on the status, perform a specific action (e.g., send an alert, scale a resource, log data).
3.  **Sleep/Wait**: Pause execution for a predetermined or dynamically calculated period.
4.  **Repeat**: Go back to step 1.

This pattern is useful for:
*   Health checks of services or infrastructure.
*   Polling for changes in data (e.g., inventory levels, stock prices).
*   Scheduled maintenance or cleanup tasks.

Traditional cron-based schedulers can be limiting when the sleep interval needs to be dynamic or when many individual monitors (e.g., one per device in an IoT scenario) are required.

## Monitor Pattern with Dapr Workflows

Dapr Workflows facilitate this pattern primarily through two features:

*   **`ctx.create_timer(fire_at)`**: This allows the workflow to pause its execution until a specific future time. It's the mechanism for the "sleep/wait" phase.
*   **`ctx.continue_as_new(input)`**: This is the cornerstone for creating robust, long-running (or "eternal") monitoring workflows. Instead of an actual infinite loop within a single workflow execution (which is an anti-pattern and can lead to an infinitely growing history), `continue_as_new` effectively stops the current workflow instance and immediately starts a new instance of the same workflow, passing along new input. This keeps the history of each individual run manageable and ensures the workflow can run indefinitely.

A monitor workflow can gracefully terminate by simply choosing not to call `continue_as_new` based on some condition.

## Conceptual Code Example (Adapted from Dapr Docs for `main.py`)

The following Python code illustrates the Monitor pattern. We will implement a similar structure in our `main.py`.

```python
import random
import logging
from dataclasses import dataclass, asdict
from datetime import timedelta
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowContext, WorkflowActivityContext, DaprWorkflowClient
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("monitor")

# --- Data Model ---
@dataclass
class JobStatus:
    job_id: str
    is_healthy: bool = True  # Assume healthy by default

# --- Workflow Runtime ---
wfr = WorkflowRuntime()

# --- Activities ---
@wfr.activity()
def check_status(ctx: WorkflowActivityContext, job_id: str) -> str:
    """Simulate status check - replace with real system probe in production."""
    result = random.choice(["healthy", "unhealthy", "healthy"])  # Biased for demo
    logger.info(f"[{job_id}] Checked status: {result}")
    return result

@wfr.activity()
def send_alert(ctx: WorkflowActivityContext, message: str):
    """Simulate sending an alert (e.g., email, SMS)."""
    logger.warning(f"🚨 {message}")
    return {"sent": True, "message": message}

# --- Workflow ---
@wfr.workflow()
def monitor_workflow(ctx: DaprWorkflowContext, job: dict):
    """Main workflow logic: check -> alert -> sleep -> repeat"""
    job_status = JobStatus(**job)

    current_status = yield ctx.call_activity(check_status, input=job_status.job_id)
    if not ctx.is_replaying:
        logger.info(f"[{job_status.job_id}] Current status: {current_status}")

    # Decide action and interval
    if current_status == "healthy":
        job_status.is_healthy = True
        sleep_seconds = 60  # Check less frequently
    else:
        if job_status.is_healthy:  # Was healthy, now unhealthy
            yield ctx.call_activity(send_alert, input=f"Job {job_status.job_id} is UNHEALTHY!")
        job_status.is_healthy = False
        sleep_seconds = 10  # Check more frequently

    # Sleep before continuing
    yield ctx.create_timer(ctx.current_utc_datetime + timedelta(seconds=sleep_seconds))

    # Restart workflow with updated state
    ctx.continue_as_new(asdict(job_status))

# --- FastAPI with Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    wfr.start()
    yield
    wfr.shutdown()

app = FastAPI(lifespan=lifespan)

# --- Endpoint to Start Monitor ---
@app.post("/monitor/{job_id}")
async def start_monitor(job_id: str):
    client = DaprWorkflowClient()
    instance_id = f"monitor_{job_id}"
    job = JobStatus(job_id=job_id)
    try:
        client.schedule_new_workflow(monitor_workflow, input=asdict(job), instance_id=instance_id)
        return {"message": f"Started monitor for job '{job_id}'", "instance_id": instance_id}
    except Exception as e:
        return {"error": str(e)}

# --- Endpoint to Terminate Monitor ---
@app.post("/monitor/terminate/{instance_id}")
async def terminate_monitor(instance_id: str):
    client = DaprWorkflowClient()
    try:
        client.terminate_workflow(instance_id)
        return {"message": f"Terminated workflow '{instance_id}'"}
    except Exception as e:
        return {"error": str(e)}

```

**Note on Actors and Reminders**: As the Dapr documentation mentions, this pattern can also be expressed using Dapr Actors and Reminders. The choice depends on the specific needs:
*   **Workflows**: Good for expressing a sequence of actions with potentially stronger reliability guarantees, and the logic is often contained within a single function or a set of clearly defined activities. State management is explicit via `continue_as_new` inputs.
*   **Actors + Reminders**: Excellent for scenarios where you have many independent entities (actors) that each need their own recurring schedule (reminders). State is managed by the actor itself.

## Setup

1.  **Starter Code**: Copy the contents of the `00_starter-code/daca-workflow/` directory into `04_monitor/hello-workflow-code/daca-workflow/`.
    The `main.py` in this new directory will be modified to implement the monitor pattern as shown in the conceptual code above.

2.  **Run the Environment**:
    ```bash
    tilt up
    ```

## Access Points

*   **Tilt UI**: [http://localhost:10350](http://localhost:10350) (Service status and logs).
*   **Application API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs) (To start and terminate monitor workflows).
*   **Jaeger UI**: [http://localhost:16686/](http://localhost:16686/) (Each `continue_as_new` cycle effectively starts a new logical instance from Dapr's perspective, though they chain together).
*   **Dapr Dashboard**: [http://localhost:8080](http://localhost:8080) (Observe workflow instances).

## Next Steps

After updating this `readme.md` with the content above, proceed to implement the Monitor pattern in the `main.py` file within your `04_monitor/hello-workflow-code/daca-workflow/` directory, using the provided conceptual code as a strong guide.