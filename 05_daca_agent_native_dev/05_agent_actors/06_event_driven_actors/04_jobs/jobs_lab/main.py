import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
import datetime
import httpx
import os
import json
from typing import Optional

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

APP_ID = "task-executor-app"  # Dapr app-id
app = FastAPI(title="TaskExecutorService")

# DAPR_SIDECAR_HOST = os.getenv("DAPR_HOST", "http://localhost")
# Port of this app's Dapr sidecar
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
BASE_DAPR_JOBS_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs"


@app.post("/executeScheduledTask")
async def execute_scheduled_task(request: Request):
    timestamp = datetime.datetime.now().isoformat()
    logger.info(
        f"[{timestamp}] Received call to /executeScheduledTask by Dapr Job.")

    data_received = None
    try:
        # Dapr jobs usually send data with 'application/json' or 'text/plain'
        # Check content-type to decide how to parse
        content_type = request.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            data_received = await request.json()
            logger.info(f"Received JSON data: {data_received}")
        elif "text/plain" in content_type:
            data_received = await request.body()
            data_received = data_received.decode('utf-8')
            logger.info(f"Received text data: {data_received}")
        else:
            # Fallback for other types or if no specific type is matched
            raw_body = await request.body()
            if raw_body:
                logger.info(
                    f"Received raw data (Content-Type: {content_type}): {raw_body.decode(errors='replace')}")
            else:
                logger.info(
                    "No data payload received or unknown content type.")

    except Exception as e:
        logger.error(f"Error processing request data: {e}")
        # Optionally, re-raise or return an error response if critical
        # For now, we log and let Dapr see a 2xx from the return below.

    return {"status": "success", "message": "Task triggered by Dapr Job", "received_at": timestamp, "data_echo": data_received}

# A simple health check endpoint Dapr can use


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "OK"

# New endpoint that Dapr seems to be calling by convention


@app.post("/job/{job_name_from_path}")
async def handle_dapr_job_trigger(job_name_from_path: str, request: Request):
    timestamp = datetime.datetime.now().isoformat()
    logger.info(
        f"[{timestamp}] DAPR JOB TRIGGER: Endpoint /job/{job_name_from_path} was called.")

    data_received = None
    try:
        content_type = request.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            data_received = await request.json()
            logger.info(
                f"DAPR JOB TRIGGER (for {job_name_from_path}): Received JSON data: {data_received}")
        elif "text/plain" in content_type:
            data_received = await request.body()
            data_received = data_received.decode('utf-8')
            logger.info(
                f"DAPR JOB TRIGGER (for {job_name_from_path}): Received text data: {data_received}")
        else:
            raw_body = await request.body()
            if raw_body:
                logger.info(
                    f"DAPR JOB TRIGGER (for {job_name_from_path}): Received raw data (Content-Type: {content_type}): {raw_body.decode(errors='replace')}")
            else:
                logger.info(
                    f"DAPR JOB TRIGGER (for {job_name_from_path}): No data payload received.")
    except Exception as e:
        logger.error(
            f"DAPR JOB TRIGGER (for {job_name_from_path}): Error processing data: {e}")

    # This endpoint now successfully receives the call Dapr makes.
    # The actual "data" field from the original job_payload (e.g., {"message": "WORKING OR NOT"})
    # should be in data_received here.
    return {"status": "success", "message": f"Dapr job {job_name_from_path} triggered custom /job endpoint", "received_at": timestamp, "data_echo": data_received}

# --- Programmatic Job Management Endpoints ---


@app.post("/programmatic/schedule-task")
async def schedule_new_task(job_name: str, schedule: str = "@every 1m", repeats: int = 0, task_data: Optional[dict] = None):
    """
    Schedules a new Dapr job targeting the /executeScheduledTask endpoint of this service.
    - job_name: Unique name for the job.
    - schedule: CRON string (e.g., "@every 30s", "0 0 * * *") or RFC3339/Go Duration for dueTime.
    - repeats: Number of times to repeat. 0 or undefined for indefinite (based on schedule).
    - task_data: JSON serializable data to send to the /executeScheduledTask endpoint.
    """
    target_job_name = job_name or f"prog-task-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    logger.info(
        f"Attempting to schedule job: {target_job_name} with schedule: {schedule}")

    job_payload = {
        "schedule": schedule,
        # "dueTime": "5s", # Alternative to schedule for one-shot or initial delay
        "target": {
            "appId": APP_ID,  # Target this same application
            "method": "executeScheduledTask"
        },
        "data": task_data or {"message": "Programmatically scheduled!", "source": target_job_name},
        "contentType": "application/json"
    }
    if repeats > 0:
        job_payload["repeats"] = repeats

    url = f"{BASE_DAPR_JOBS_URL}/{target_job_name}"
    logger.info(
        f"Sending Dapr job payload to {url}: {json.dumps(job_payload)}")

    try:
        async with httpx.AsyncClient() as client:
            # Dapr job API expects JSON body for the spec
            response = await client.post(url, json=job_payload)
            response.raise_for_status()
            logger.info(
                f"Successfully scheduled job {target_job_name}. Status: {response.status_code}")
            # Dapr returns 204 No Content on successful creation/update
            return {"status": "Job scheduled/updated", "job_name": target_job_name, "response_status": response.status_code, "response_text": response.text}
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error scheduling job {target_job_name}: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"Failed to schedule job: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error scheduling job {target_job_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/programmatic/task-status/{job_name}")
async def get_task_status(job_name: str):
    logger.info(f"Fetching status for job: {job_name}")
    url = f"{BASE_DAPR_JOBS_URL}/{job_name}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"Successfully fetched status for job {job_name}.")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error fetching job status {job_name}: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"Failed to get job status: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error fetching job status {job_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/programmatic/delete-task/{job_name}")
async def delete_scheduled_task(job_name: str):
    logger.info(f"Attempting to delete job: {job_name}")
    url = f"{BASE_DAPR_JOBS_URL}/{job_name}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(url)
            response.raise_for_status()
            logger.info(
                f"Successfully deleted job {job_name}. Status: {response.status_code}")
            # Dapr returns 204 No Content on successful deletion
            return {"status": "Job deleted", "job_name": job_name, "response_status": response.status_code, "response_text": response.text}
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error deleting job {job_name}: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"Failed to delete job: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error deleting job {job_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")
