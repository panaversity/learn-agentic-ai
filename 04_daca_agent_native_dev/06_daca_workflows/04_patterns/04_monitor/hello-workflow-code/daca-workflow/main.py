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