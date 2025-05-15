# [Pattern 5: External System Interaction (and Human Interaction)](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/#external-system-interaction)

This pattern addresses scenarios where a workflow needs to pause its execution and wait for a signal or data from an external system, which could be another microservice, a third-party API, or often, a human user.

## Understanding External System Interaction

Common use cases include:

*   **Human Approvals**: Purchase order approvals, leave requests, content moderation where a human decision is needed.
*   **Payment Gateways**: Waiting for confirmation that a payment has been processed successfully.
*   **Callback Mechanisms**: Interacting with systems that operate asynchronously and provide results via a callback.
*   **Long-running external tasks**: Triggering a task in another system and waiting for its completion signal.

The typical flow involves:
1.  The workflow initiates a request or sends a notification to an external entity.
2.  The workflow pauses, waiting for a specific external event (e.g., "approval_received", "payment_confirmed").
3.  Often, a timeout is also associated with this wait period.
4.  The workflow resumes based on whichever occurs first: the external event or the timeout.
5.  An external component (another service, an API endpoint responding to a user action, an event subscriber) uses Dapr's capabilities to send the named event to the specific workflow instance.

## External Interaction with Dapr Workflows

Dapr Workflows provide robust support for this pattern through:

*   **`ctx.wait_for_external_event(event_name: str)`**: The workflow calls this and yields, effectively pausing its execution until an event with the specified `event_name` is raised against its instance.
*   **`ctx.create_timer(timedelta(...))`**: Used to create a timer. This is often used in conjunction with `wait_for_external_event` to implement timeouts.
*   **`wf.when_any([task1, task2, ...])`**: This powerful construct allows the workflow to wait for any one of a list of pending tasks (like an external event or a timer) to complete. The workflow then proceeds based on which task completed first.
*   **`DaprClient().raise_workflow_event(instance_id: str, workflow_component: str, event_name: str, event_data: any)`**: This method, used *outside* the workflow code itself (e.g., in a separate FastAPI endpoint or an event handler), is how the external signal is delivered to the waiting workflow instance.

## Conceptual Code Example (Adapted from Dapr Docs for `main.py`)

The following Python code illustrates the pattern for a purchase order approval.

**Workflow and Activity Definitions (in `main.py`):**
```python
import time # For activity simulation
import logging

from dataclasses import dataclass, asdict
from datetime import timedelta

from dapr.ext.workflow import DaprWorkflowContext, WorkflowActivityContext, WorkflowRuntime, DaprWorkflowClient, when_any
from fastapi import FastAPI, HTTPException

from contextlib import asynccontextmanager
from pydantic import BaseModel # For request/response models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wfr = WorkflowRuntime()

# --- Dataclasses ---
@dataclass
class Order:
    order_id: str # Added for clarity
    cost: float
    product: str
    quantity: int

    def __str__(self):
        return f'Order {self.order_id}: {self.quantity} of {self.product} at ${self.cost} each.'

@dataclass
class Approval:
    approver_name: str
    approved: bool # True if approved, False if explicitly rejected

# --- Workflow Definition ---
@wfr.workflow(name="PurchaseOrderApprovalWorkflow")
def purchase_order_workflow(ctx: DaprWorkflowContext, order_input_dict: dict):
    current_order = Order(**order_input_dict)
    timeout_seconds = 30 # Short timeout for demo purposes; Dapr example uses 24 hours

    if not ctx.is_replaying:
        logger.info(f"Workflow '{ctx.instance_id}': Starting purchase order workflow for {current_order}")

    # Orders under $1000 are auto-approved
    if current_order.cost * current_order.quantity < 1000:
        if not ctx.is_replaying:
            logger.info(f"Workflow '{ctx.instance_id}': Order {current_order.order_id} auto-approved.")
        return {"status": "Auto-Approved", "order_id": current_order.order_id}

    # Orders of $1000 or more require manager approval
    if not ctx.is_replaying:
        logger.info(f"Workflow '{ctx.instance_id}': Order {current_order.order_id} requires approval. Sending request...")
    yield ctx.call_activity(
        send_approval_request_activity, # Activity name as string
        input=asdict(current_order)
    )

    # Wait for either an approval event or a timeout
    if not ctx.is_replaying:
        logger.info(f"Workflow '{ctx.instance_id}': Order {current_order.order_id} waiting for 'approval_event' or timeout of {timeout_seconds}s.")
    
    approval_event_task = ctx.wait_for_external_event("approval_event")
    timeout_event_task = ctx.create_timer(timedelta(seconds=timeout_seconds))

    winner = yield when_any([approval_event_task, timeout_event_task])

    if winner == approval_event_task:
        approval_data_dict = approval_event_task.get_result() # This is the event_data sent by raise_workflow_event
        approval_decision = Approval(**approval_data_dict)
        if approval_decision.approved:
            if not ctx.is_replaying:
                logger.info(f"Workflow '{ctx.instance_id}': Order {current_order.order_id} approved by {approval_decision.approver_name}. Placing order...")
            yield ctx.call_activity(place_order_activity, input=asdict(current_order))
            return {"status": f"Approved by {approval_decision.approver_name}", "order_id": current_order.order_id}
        else:
            if not ctx.is_replaying:
                logger.info(f"Workflow '{ctx.instance_id}': Order {current_order.order_id} rejected by {approval_decision.approver_name}.")
            return {"status": f"Rejected by {approval_decision.approver_name}", "order_id": current_order.order_id}
    else: # Timeout occurred
        if not ctx.is_replaying:
            logger.warning(f"Workflow '{ctx.instance_id}': Order {current_order.order_id} approval timed out. Cancelling...")
        # Optionally call a cancellation activity
        # yield ctx.call_activity("cancel_order_activity", input=asdict(current_order))
        return {"status": "Cancelled due to timeout", "order_id": current_order.order_id}

# --- Activity Definitions ---
@wfr.activity(name="send_approval_request_activity")
def send_approval_request_activity(ctx: WorkflowActivityContext, order_dict: dict):
    order = Order(**order_dict)
    logger.info(f"Activity (WF '{ctx.workflow_id}'): Sending approval request for {order}. Instance ID to approve/reject: {ctx.workflow_id}")
    # Simulate sending an email or notification. Crucially, include ctx.workflow_id in the notification.
    time.sleep(1)
    return {"notification_sent": True, "for_order_id": order.order_id}

@wfr.activity(name="place_order_activity")
def place_order_activity(ctx: WorkflowActivityContext, order_dict: dict):
    order = Order(**order_dict)
    logger.info(f"Activity (WF '{ctx.workflow_id}'): Placing {order}.")
    time.sleep(1)
    return {"order_placed": True, "order_id": order.order_id}

# --- FastAPI Endpoints ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Activities and workflow are registered with decorators
    wfr.start()
    logger.info("External System Interaction Workflow Runtime started.")
    yield
    wfr.shutdown()
    logger.info("External System Interaction Workflow Runtime stopped.")

app = FastAPI(title="External System Interaction Demo", lifespan=lifespan)

class StartOrderRequest(BaseModel):
    order_id: str
    cost: float
    product: str
    quantity: int

@app.post("/start-purchase-order")
async def start_po_workflow_endpoint(request: StartOrderRequest):
    # Use the global DaprWorkflowClient from dapr.ext.workflow
    # This client is typically for scheduling, getting status, etc.
    workflow_client = DaprWorkflowClient() # Correct client for scheduling
    order_data = Order(order_id=request.order_id, cost=request.cost, product=request.product, quantity=request.quantity)
    try:
        instance_id = workflow_client.schedule_new_workflow(
            workflow=purchase_order_workflow, # Pass the workflow function
            input=asdict(order_data),
            # Optionally use a deterministic instance ID: workflow_id=f"po_{request.order_id}"
        )
        return {"instance_id": instance_id, "message": f"Purchase order workflow started for {request.order_id}. If approval needed, use /signal-approval endpoint."}
    except Exception as e:
        logger.error(f"Error scheduling workflow for order {request.order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class SignalApprovalRequest(BaseModel):
    approver_name: str
    approved: bool

@app.post("/signal-approval/{instance_id}")
async def signal_approval_endpoint(instance_id: str, approval_signal: SignalApprovalRequest):
    # Use the general DaprClient for raising events
    dapr_client = DaprWorkflowClient()
    event_name = "approval_event"
    event_payload = asdict(Approval(approver_name=approval_signal.approver_name, approved=approval_signal.approved))
    try:
        # For raising event, workflow_component="dapr" is usually correct if using default Dapr workflow engine
        dapr_client.raise_workflow_event(
            instance_id=instance_id,
            event_name=event_name,
            data=event_payload
        )
        return {"message": f"Event '{event_name}' raised for instance '{instance_id}'"}
    except Exception as e:
        logger.error(f"Error raising event for instance '{instance_id}': {e}")
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

## Setup

1.  **Starter Code**: Copy contents of `00_starter-code/daca-workflow/` to `05_external_system_interaction/hello-workflow-code/daca-workflow/`.
2.  **Run**: `tilt up`

## Access Points

*   **Tilt UI**: [http://localhost:10350](http://localhost:10350)
*   **App API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs) (for `/start-purchase-order` and `/signal-approval`)
*   **Jaeger/Dapr Dashboard**: As usual.

## Implementing and Running the Example

1.  **Modify `main.py`**: Implement the dataclasses, workflow, activities, and the two FastAPI endpoints (`/start-purchase-order` and `/signal-approval/{instance_id}`) based on the conceptual code.
2.  **Test Scenario 1 (Approval)**:
    a.  Call `/start-purchase-order` with an order where `cost * quantity >= 1000` (e.g., `{"order_id": "order123", "cost": 500, "product": "Widget", "quantity": 2}`). Note the `instance_id`.
    b.  Observe logs: `send_approval_request_activity` runs. Workflow pauses.
    c.  **Before the timeout (30s in demo)**, call `/signal-approval/{instance_id}` with `{"approver_name": "ManagerX", "approved": true}`.
    d.  Observe logs: Workflow receives event, `place_order_activity` runs, workflow completes with "Approved" status.
3.  **Test Scenario 2 (Rejection)**:
    a.  Start another order: `/start-purchase-order` (e.g., `{"order_id": "order456", "cost": 600, "product": "Gadget", "quantity": 2}`). Note `instance_id`.
    b.  Call `/signal-approval/{instance_id_of_order456}` with `{"approver_name": "ManagerY", "approved": false}`.
    d.  Observe logs: Workflow receives event, completes with "Rejected" status.
4.  **Test Scenario 3 (Timeout)**:
    a.  Start another order: `/start-purchase-order` (e.g., `{"order_id": "order789", "cost": 700, "product": "Gizmo", "quantity": 2}`). Note `instance_id`.
    b.  **Do not** call `/signal-approval`.
    c.  Observe logs: After the timeout (30s), workflow resumes, completes with "Cancelled due to timeout" status.

## Next Steps

Implement the full logic in your `main.py` for this pattern. This one is more involved due to the external interaction simulation but demonstrates a very powerful Dapr Workflow capability.