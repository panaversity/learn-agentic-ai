import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowClient, DaprWorkflowContext, WorkflowActivityContext

# Basic Pydantic model for input
class OrderPayload(BaseModel):
    itemName: str
    quantity: int

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

# --- Workflow and Activity Definitions ---
@wfr.activity(name="process_order_activity")
def process_order_activity(ctx: WorkflowActivityContext, order_data: dict):
    instance_id = ctx.workflow_id # Activity can access workflow instance ID
    logger.info(f"Activity (for WF '{instance_id}'): Processing order for {order_data.get('itemName')}")
    # Simulate some long-running work
    time.sleep(15) # Simulate a 15-second process
    logger.info(f"Activity (for WF '{instance_id}'): Finished processing order for {order_data.get('itemName')}")
    return {"processed": True, "item": order_data.get('itemName'), "message": "Order processed successfully"}

@wfr.workflow(name="AsyncOrderProcessingWorkflow")
def async_order_processing_workflow(ctx: DaprWorkflowContext, order_input: dict):
    instance_id = ctx.instance_id
    logger.info(f"Workflow '{instance_id}': Started processing order: {order_input}")
    
    # Call an activity
    result = yield ctx.call_activity(
        process_order_activity,
        input=order_input
    )
    
    logger.info(f"Workflow '{instance_id}': Order processing activity completed. Result: {result}")
    return result

# --- FastAPI Application Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        wfr.start()
        logger.info("Workflow Runtime started.")
    except Exception as e:
        logger.warning(f"Workflow Runtime might already be started or failed to start: {e}")

    yield # Application runs

    try:
        wfr.shutdown()
        logger.info("Workflow Runtime stopped.")
    except Exception as e:
        logger.warning(f"Workflow Runtime failed to shutdown gracefully: {e}")


app = FastAPI(title="Async HTTP API Demo with Dapr Workflow", lifespan=lifespan)

@app.post("/start-async-order")
async def start_order_workflow_endpoint(order: OrderPayload):
    client = DaprWorkflowClient()
    try:
        # Schedule the workflow
        instance_id = client.schedule_new_workflow(
            workflow=async_order_processing_workflow,
            input=order.model_dump() # Pass Pydantic model as dict
        )
        logger.info(f"Successfully scheduled workflow 'AsyncOrderProcessingWorkflow' with instance ID: {instance_id}")
        return {"instance_id": instance_id}
    except Exception as e:
        logger.error(f"Error scheduling workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/status/{instance_id}")
async def get_workflow_status(instance_id: str):
    client = DaprWorkflowClient()
    status = client.get_workflow_state(instance_id)
    return status.to_json()

