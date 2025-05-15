# [Pattern 6: Workflows with Transactional Outbox](https://docs.dapr.io/developing-applications/building-blocks/state-management/howto-outbox/)

This pattern ensures that state changes and the events/messages notifying other services about those changes are committed atomically. This is crucial for maintaining data consistency across distributed services. Dapr's state management and pub/sub building blocks, when used with its transactional capabilities, make this robustly achievable, and Dapr Workflows can orchestrate processes that leverage this.

## Understanding the Transactional Outbox Pattern

**The Problem:** In a distributed system, you often need to perform two actions as part of a single logical operation:
1.  Save/update data in your primary database (state store).
2.  Publish an event/message to a message broker to notify other services of this change.

If these are done as two separate operations, failures can lead to inconsistencies:
*   State saved, but event not published (other services miss the update).
*   Event published, but state save failed (other services react to a change that didn't actually persist).

**The Solution:** The Transactional Outbox pattern ensures these two actions occur within a single atomic transaction. Both succeed, or both fail (and are rolled back), preventing data divergence.

## Dapr's Approach to Transactional Outbox

Dapr implements the outbox pattern by enabling a Dapr **state store component** to also publish a message to a Dapr **pub/sub component** as part of the same underlying transaction.

*   **Configuration**: You configure specific metadata fields on your Dapr state store component YAML:
    *   `outboxPublishPubsub`: (Required) The name of the Dapr pub/sub component to use for delivering notifications.
    *   `outboxPublishTopic`: (Required) The topic on the specified pub/sub component where state change notifications will be sent.
*   **Operation**: When your application uses Dapr's transactional state APIs (e.g., `execute_state_transaction`) with such a configured state store, Dapr ensures that the operations against the state store and the publishing of the corresponding event happen atomically.

## Integrating Outbox with Dapr Workflows

The Dapr Workflow itself doesn't directly perform the outbox transaction. Instead:
1.  A **Workflow Activity** is designed to interact with the Dapr state store using Dapr's transactional state APIs.
2.  The Workflow orchestrates the business logic, calling this activity at the appropriate step.

For example, a workflow might:
*   Call an activity to validate input.
*   Call an activity named `process_and_notify_transactionally` which saves data and implicitly publishes an event via the outbox mechanism.
*   Call further activities based on the success of the previous steps.

## Conceptual Code and Configuration Examples

Here's how the pieces fit together:

**1. Dapr State Store Component (e.g., `components/transactional-statestore.yaml`)**

This component is configured for outbox. For this example, we'll assume a Redis state store.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: orderstatestore # Name of this state store component
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.default.svc.cluster.local:6379 # Adjust if your Redis is elsewhere
  - name: redisPassword
    value: ""
  # --- Outbox Configuration ---
  - name: outboxPublishPubsub # Required: Name of the Dapr pub/sub component
    value: orderpubsub
  - name: outboxPublishTopic # Required: Topic to publish to on state change
    value: newOrderEvents
  # Optional:
  # - name: outboxPubsub 
  #   value: "myOutboxCoordinatorPubsub" # If you want a separate pub/sub for Dapr's internal coordination
  # - name: outboxDiscardWhenMissingState
  #   value: "false" 
```

**2. Dapr Pub/Sub Component (e.g., `components/order-pubsub.yaml`)**

This is the pub/sub broker that `orderstatestore` will publish to.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: orderpubsub # Must match outboxPublishPubsub above
spec:
  type: pubsub.redis # Or rabbitmq, kafka, etc.
  version: v1
  metadata:
  - name: redisHost
    value: redis-master.default.svc.cluster.local:6379 # Adjust if your Redis is elsewhere
  - name: redisPassword
    value: ""
```

**3. Workflow Activity in `main.py` (Performs the Transaction)**

```python
# --- (Inside your main.py, add to other imports) ---
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem, StateOptions # For execute_state_transaction
import json

# --- Activity Definition ---
# @wfr.activity(name="save_order_and_publish_event_activity") # Registered via decorator
async def save_order_and_publish_event_activity_func(ctx: WorkflowActivityContext, order_details: dict):
    order_id = order_details.get("orderId")
    logger.info(f"Activity '{ctx.task_name}' (WF '{ctx.workflow_id}'): Saving order {order_id} and publishing event transactionally.")
    
    dapr_client = DaprClient()
    store_name = "orderstatestore" # Must match the name of your transactional state store component

    # Operation to save the order state
    save_order_operation = {
        'operation': 'upsert',
        'request': {
            'key': str(order_id), # Ensure key is a string
            'value': json.dumps(order_details) # Store the full order details as JSON string
            # Optional: Add metadata for custom CloudEvent fields if needed
            # 'metadata': {
            #     'cloudevent.id': f'order-{order_id}',
            #     'cloudevent.source': 'OrderWorkflow',
            #     'cloudevent.type': 'OrderCreated',
            #     'cloudevent.subject': str(order_id)
            # }
        }
    }

    # If you want to shape the message published by the outbox (message shaping)
    # otherwise, Dapr publishes the saved state item by default.
    # shaped_message_payload = {"custom_event_field": f"Order {order_id} processed", "data": order_details}
    # shape_message_operation = {
    #     'operation': 'upsert', # Must be upsert for projection
    #     'request': {
    #         'key': str(order_id), # Key MUST match the actual state operation key
    #         'value': json.dumps(shaped_message_payload),
    #         'options': { # Dapr SDK uses StateOptions for this
    #             'metadata': {'outbox.projection': 'true'}
    #         }
    #     }
    # }
    # operations = [save_order_operation, shape_message_operation]
    
    operations = [save_order_operation]

    try:
        await dapr_client.execute_state_transaction(store_name=store_name, operations=operations)
        logger.info(f"Activity '{ctx.task_name}': Order {order_id} saved and event queued via outbox successfully.")
        return {"status": "SUCCESS", "order_id": order_id}
    except Exception as e:
        logger.error(f"Activity '{ctx.task_name}': Transaction failed for order {order_id}: {e}")
        # Optionally, re-raise to fail the workflow, or handle compensation
        raise
    finally:
        await dapr_client.close() # Important to close the client
```

**4. Workflow Definition in `main.py` (Calls the Activity)**

```python
# --- (Inside your main.py) ---
# @wfr.workflow(name="OrderProcessingWithOutboxWorkflow") # Registered via decorator
def order_processing_with_outbox_workflow(ctx: DaprWorkflowContext, order_input: dict):
    order_id = order_input.get("orderId", "unknown_order")
    if not ctx.is_replaying:
        logger.info(f"Workflow '{ctx.instance_id}': Starting order processing with outbox for order: {order_id}")

    # Step 1: (Optional) Validate order, etc.
    # yield ctx.call_activity(validate_order_activity, input=order_input)

    # Step 2: Save order and publish notification transactionally
    transaction_result = yield ctx.call_activity(
        "save_order_and_publish_event_activity", # Name of the activity
        input=order_input
    )

    if transaction_result and transaction_result.get("status") == "SUCCESS":
        if not ctx.is_replaying:
            logger.info(f"Workflow '{ctx.instance_id}': Successfully processed and notified for order {order_id}.")
        return {"workflow_status": "COMPLETED", "order_id": order_id, "transaction_result": transaction_result}
    else:
        if not ctx.is_replaying:
            logger.error(f"Workflow '{ctx.instance_id}': Failed to process and notify for order {order_id}.")
        # Handle failure, perhaps by raising an error to fail the workflow
        # or calling compensation activities.
        return {"workflow_status": "FAILED", "order_id": order_id, "transaction_result": transaction_result}
```

**5. Conceptual Subscriber (Separate Service or `main.py` if simple)**

This service would listen to the `newOrderEvents` topic on the `orderpubsub`.

```python
# --- Conceptual Subscriber (could be in a different service or a separate part of main.py for demo) ---
# from fastapi import FastAPI
# from cloudevents.http import from_http # To parse CloudEvents

# subscriber_app = FastAPI(title="Order Event Subscriber")

# @subscriber_app.post("/newOrderEvents") # Matches the Dapr subscription path for the topic
# async def order_event_subscriber(event: dict): # Dapr delivers event as JSON
#     try:
#         # If Dapr sends CloudEvents, you might parse it:
#         # cloudevent = from_http(event.headers, event.body)
#         # logger.info(f"Subscriber: Received CloudEvent: ID: {cloudevent['id']}, Source: {cloudevent['source']}, Data: {cloudevent.data}")
        
#         # For raw JSON payload (especially if shaped with outbox.projection):
#         logger.info(f"Subscriber: Received event on 'newOrderEvents': {event}")
        
#         # Add business logic here to process the event (e.g., update another system, send notifications)
#         # Example: order_data = event.get("data") or event itself if shaped.
        
#         return {"status": "Event received"}, 200
#     except Exception as e:
#         logger.error(f"Subscriber: Error processing event: {e}")
#         return {"status": "Error processing event"}, 500

# Dapr Subscription YAML for the subscriber app (e.g., components/order-subscription.yaml)
# apiVersion: dapr.io/v1alpha1
# kind: Subscription
# metadata:
#   name: new-order-event-subscription # Name of the Dapr subscription
# spec:
#   topic: newOrderEvents             # Topic to subscribe to
#   route: /newOrderEvents            # Endpoint in your subscriber service to deliver messages to
#   pubsubname: orderpubsub           # Name of the Dapr pub/sub component
# scopes:                             # Optional: Scopes the subscription to specific app IDs
# - order-processor-app               # App ID of the workflow service
# - order-subscriber-app              # App ID of this subscriber service (if different)
```

## Setup

1.  **Starter Code**: Copy `00_starter-code/daca-workflow/` to `06_transactional_outbox_pattern/hello-workflow-code/daca-workflow/`.
2.  **Dapr Components**:
    *   Create `components/transactional-statestore.yaml` with the content provided above (adjust Redis host if needed).
    *   Create `components/order-pubsub.yaml` with the content provided above (adjust Redis host if needed).
    *   (Optional, for full demo) Create `components/order-subscription.yaml` if you implement a subscriber.
3.  **Tiltfile / Kubernetes**: Ensure your Dapr environment (e.g., via `Tiltfile` `k8s_yaml` directives or `kubectl apply -f components/`) applies these new Dapr component configurations. Your Redis instance must be running and accessible.
4.  **Run**: `tilt up`

## Access Points

*   **Tilt UI**: [http://localhost:10350](http://localhost:10350)
*   **App API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs) (for the endpoint that starts the `OrderProcessingWithOutboxWorkflow`).
*   **Dapr Dashboard**: [http://localhost:8080](http://localhost:8080) (Check component status, pub/sub messages if observable).
*   **Redis CLI (or other state store/pub-sub inspection tool)**: To verify state persistence and message publication.

## Implementing and Running the Example

1.  **Modify `main.py`**:
    *   Implement the `order_processing_with_outbox_workflow` and the `save_order_and_publish_event_activity_func`.
    *   Register the workflow and activity with the `WorkflowRuntime`.
    *   Create a FastAPI endpoint (e.g., `/process-order-with-outbox`) that takes order details and schedules the workflow.
    *   (Optional for full demo) If you want to see the event received, you'll need a simple subscriber. This could be another FastAPI app, or even a simple route within the same `main.py` if you configure Dapr Pub/Sub to deliver to it and give your app a Dapr ID. For simplicity in a single file, you might skip the full subscriber and just verify message in Redis pub/sub if your tool allows.

2.  **Start the Workflow**:
    *   Use Swagger UI or `curl` to POST to your `/process-order-with-outbox` endpoint with some order data (e.g., `{"orderId": "order001", "item": "DaprBook", "quantity": 1}`).
    *   Note the `instance_id`.

3.  **Observe Behavior**:
    *   **Logs**: Check Tilt UI logs. You should see:
        *   Workflow starting.
        *   `save_order_and_publish_event_activity_func` logs indicating it's attempting the transaction.
        *   Confirmation of transaction success.
        *   Workflow completion.
    *   **State Store**: Use a Redis client (or your state store's tool) to check that the order data (e.g., key `order001`) has been saved in the `orderstatestore`.
    *   **Pub/Sub Topic**: This is trickier to observe directly without a subscriber.
        *   If you implemented a subscriber, check its logs for the received event on the `newOrderEvents` topic.
        *   Some pub/sub systems (like Redis) might allow you to monitor messages on topics via their CLI (`MONITOR` command in `redis-cli` then `PUBLISH system:newOrderEvents test` might show Dapr's internal messages, or directly `SUBSCRIBE newOrderEvents`).
        *   Dapr Dashboard might offer some pub/sub observability depending on the broker.

4.  **Test Failure (Conceptual)**: If the state save *or* the event publish were to fail (hard to simulate reliably without specific broker/DB errors), Dapr's transactional mechanism should ensure that *neither* operation is committed.

## Key Considerations

*   **Message Shaping (`outbox.projection`)**: As shown in the Dapr docs and commented in the conceptual code, you can publish a different message payload than what's saved to the state store using the `outbox.projection: "true"` metadata on a secondary transactional operation with the same key.
*   **Idempotency**: Subscribers should generally be designed to be idempotent, as message brokers can sometimes deliver a message more than once (though the outbox helps ensure the event is *based* on a successful state change).
*   **Error Handling**: The transactional activity should handle exceptions robustly. If the transaction fails, the activity should likely raise an error to notify the workflow, which can then decide on compensation or retry logic.

## Next Steps

After updating this `readme.md`, the next steps are:
1.  Create the Dapr component YAML files (`transactional-statestore.yaml`, `order-pubsub.yaml`).
2.  Update your `Tiltfile` (or apply manually) to include these components.
3.  Implement the workflow and activity logic in your `main.py` for this pattern.