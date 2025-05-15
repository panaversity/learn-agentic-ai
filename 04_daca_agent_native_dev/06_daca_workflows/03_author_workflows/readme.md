# 03: [Authoring Dapr Workflows & Activities](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/)

This module provides a hands-on guide to the Dapr Python SDK (`dapr-ext-workflow`) for authoring robust and complex workflow logic. We will start with the basic "Hello, Workflow!" example and incrementally add advanced features to it. You will learn to define workflows and activities, manage data flow, orchestrate tasks, handle time, integrate external events, and more.

This guide assumes you have completed `01_hello_workflow` and have a foundational understanding from `02_architecture_theory`. The official [Dapr - How to: Author workflows documentation](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/) provides excellent general concepts that we will apply specifically to the Python SDK.

## Core Concepts Recap (from `main.py`)

Our starting point, `main.py`, already demonstrates these basics:

*   **Workflow Runtime**: `wfr = WorkflowRuntime()`
*   **Registering Workflows**: `@wfr.workflow` (e.g., `hello_workflow`)
*   **Registering Activities**: `@wfr.activity` (e.g., `hello_activity`)
*   **Calling Activities**: `yield ctx.call_activity(hello_activity, input=name)`
*   **Workflow Context**: `DaprWorkflowContext` (provides `ctx.instance_id`, `ctx.call_activity`, `ctx.current_utc_date_time`, etc.)
*   **Activity Context**: `WorkflowActivityContext` (provides `ctx.workflow_id`, `ctx.task_id`)
*   **FastAPI Integration**: Using `lifespan` to manage `wfr.start()` and `wfr.shutdown()`.
*   **API Endpoints**: For starting (`/start/{user_name}`) and checking status (`/status/{instance_id}`).

## Running the Example

You can take starter code and code as you follow this or this step code. The project is configured to run with Tilt, which handles building the Docker image and deploying to a local Kubernetes Kind cluster.

```bash
tilt up
```

Once `tilt up` is running, you can access:
*   **Tilt UI**: [http://localhost:10350](http://localhost:10350) (Shows the status of your services)
*   **Application API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs)
*   **Jaeger UI (for tracing, if configured)**: [http://localhost:16686/](http://localhost:16686/)

## Advanced Workflow Authoring Features

Let's explore the key features provided by adding examples for each of the following Dapr Workflow authoring features. After each modification, we will test and play to master it.

### 1. Workflow and Activity Inputs & Outputs

Workflows and activities robustly handle typed inputs and can return structured outputs.
*   **Workflow Input**: Defined as an argument in your workflow function. The Dapr SDK handles serialization and deserialization. Important the input type is `input: Optional[TInput] = None`
*   **Workflow Output**: The return value of the workflow function. This is serialized and stored as the workflow's output.

Our current `main.py` already effectively demonstrates this:
*   `hello_workflow(ctx: DaprWorkflowContext, name: str)` takes a string input.
*   `hello_activity(ctx: WorkflowActivityContext, name: str)` also takes a string input.
*   The activity returns a formatted string.
*   The workflow returns a dictionary: `{"final_greeting": greeting}`.

### 2. Calling Activities with Retry Policies

To make workflows resilient, Dapr allows automatic retries for failed activities.

*   **Concept**: If an activity raises an exception, the Dapr workflow engine can retry its execution based on a defined policy.
*   **SDK Usage**: The `ctx.call_activity` method accepts a `retry_policy` argument. A `WorkflowRetryPolicy` object defines parameters like `max_number_of_attempts`, `first_retry_interval` (as `timedelta`), `backoff_coefficient`, etc.

*   **Hands-on: Adding Retry Policy to `enhanced-hello-workflow/main.py`**
    1.  Add the following import:
        ```python
        from dapr.ext.workflow import RetryPolicy
        from datetime import timedelta
        import random # For simulating failure

        retry_policy = RetryPolicy(
            first_retry_interval=timedelta(seconds=1),
            max_number_of_attempts=3,
            backoff_coefficient=2,
            max_retry_interval=timedelta(seconds=10),
            retry_timeout=timedelta(seconds=100),
        )
        ```
    2.  Define a new, potentially flaky activity:
        ```python
        @wfr.activity(name="flaky_activity")
        def flaky_activity(ctx: WorkflowActivityContext, data: str):
            logger.info(f"Flaky Activity (for WF '{ctx.workflow_id}'): Attempting with '{data}'")
            # Simulate a 50% chance of failure
            if random.random() < 0.5:
                logger.warning(f"Flaky Activity (for WF '{ctx.workflow_id}'): Simulating failure!")
                raise ValueError("Simulated random failure in flaky_activity")
            result = f"Successfully processed by flaky_activity: {data}"
            logger.info(f"Flaky Activity (for WF '{ctx.workflow_id}'): {result}")
            return result
        ```
    3.  Modify `hello_workflow` to call this `flaky_activity` with a retry policy:
        ```python
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

        ```
    4.  **To test**: Start the workflow multiple times. You should observe logs indicating retries and sometimes permanent failure.

*   For more on conceptual retry strategies, see [Dapr Workflow Features - Retry Policies](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#retry-policies).


### 3. Child Workflows (`ctx.call_child_workflow`)

Workflows can orchestrate other workflows for modularity.

*   **Concept**: A parent workflow starts a child workflow, can wait for its completion, and get its output. The child has its own independent instance, history, and status.
*   **SDK Usage**: Use `yield ctx.call_child_workflow()`.

*   **Hands-on: Adding a Child Workflow to `enhanced-hello-workflow/main.py`**
    1.  Define a new simple child activity and child workflow:
        ```python
        @wfr.activity(name="child_task_activity")
        def child_task_activity(ctx: WorkflowActivityContext, item_to_process: str):
            logger.info(f"Child Activity (for WF '{ctx.workflow_id}'): Processing item '{item_to_process}'")
            return f"Item '{item_to_process}' processed by child activity."

        @wfr.workflow(name="child_orchestration_workflow")
        def child_orchestration_workflow(ctx: DaprWorkflowContext, data_for_child: str):
            logger.info(f"Child WF '{ctx.instance_id}': Starting with '{data_for_child}'")
            activity_result = yield ctx.call_activity(child_task_activity, input=data_for_child)
            logger.info(f"Child WF '{ctx.instance_id}': Child activity said '{activity_result}'")
            return f"Child WF '{ctx.instance_id}' completed. Result: {activity_result}"
        ```
    2.  Modify `hello_workflow` (or create a new "parent" workflow) to call this child:
        ```python
        # Modify or add to hello_workflow, or create a new parent workflow.
        # For this example, let's assume we modify hello_workflow:
        @wfr.workflow(name="hello_workflow") 
        def hello_workflow(ctx: DaprWorkflowContext, name: str):
            logger.info(f"Parent WF '{ctx.instance_id}': Starting, will call child workflow for '{name}'")
            
            child_input = f"Data for child from {name}"
            # Optional: define a deterministic child ID
            child_instance_id = f"{ctx.instance_id}-child-{name.replace(' ', '_')}" 
            
            logger.info(f"Parent WF '{ctx.instance_id}': Calling child_orchestration_workflow with ID '{child_instance_id}'.")
            child_output = yield ctx.call_child_workflow(
                child_orchestration_workflow,
                input=child_input,
                instance_id=child_instance_id 
            )
            logger.info(f"Parent WF '{ctx.instance_id}': Child workflow output: '{child_output}'")
            
            return {"parent_result": f"Processed '{name}'", "child_result": child_output}
        ```
    3.  **To test**: Start the `hello_workflow`. You should see logs from both parent and child workflows/activities. You can also query the status of the child workflow instance using its specific ID.

*   Reference: [Dapr How to: Author Workflows - Child Workflows](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/#child-workflows).


### 4. Timers / Durable Delays (`ctx.create_timer`)

Workflows can pause durably for a specified duration.

*   **Concept**: Ensures the workflow resumes after the delay, even if the application restarts.
*   **SDK Usage**: Use `yield ctx.create_timer(timedelta_object)`. (Ensure `from datetime import timedelta` is present).

*   **Hands-on: Adding a Timer to `enhanced-hello-workflow/main.py`**
    1.  Modify `hello_workflow`:
        ```python
        @wfr.workfl`ow(name="hello_workflow")
        def hello_workflow(ctx: DaprWorkflowContext, name: str):
            logger.info(f"WF '{ctx.instance_id}': Starting at")
            
            # Call an activity (e.g., the original hello_activity or child_task_activity)
            initial_greeting = yield ctx.call_activity(hello_activity, input=name)
            logger.info(f"WF '{ctx.instance_id}': Initial activity said '{initial_greeting}'")

            delay_seconds = 15
            logger.info(f"WF '{ctx.instance_id}': Waiting for {delay_seconds} seconds...")
            yield ctx.create_timer(timedelta(seconds=delay_seconds)) # Workflow pauses here durably

            logger.info(f"WF '{ctx.instance_id}': Resumed after {delay_seconds}s performing next step.")
            final_message = f"Workflow for '{name}' completed after timed delay."
            
            return {"greeting": initial_greeting, "final_message_after_timer": final_messa`ge}
        ```
    2.  **To test**: Start the workflow. Observe the logs showing the start time, the "Waiting" message, and then the "Resumed" message after the specified delay.

*   Reference: [Dapr How to: Author Workflows - Timers](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/#timers-durable-delays).

### 5. Basic Error Handling in Workflows

Using `try...except` to manage activity failures within a workflow.

*   **Concept**: Allows for compensation logic or controlled failure of the workflow.
*   **SDK Usage**: Standard Python `try...except Exception as e:` around `yield ctx.call_activity(...)`.

*   **Hands-on: Adding Error Handling to `enhanced-hello-workflow/main.py`**
    1.  Define an activity that is designed to fail, or reuse the `flaky_activity` from the retry policy example. Let's define a new one for clarity:
        ```python
        @wfr.activity(name="always_fail_activity")
        def always_fail_activity(ctx: WorkflowActivityContext, data: str):
            logger.error(f"Always Fail Activity (WF '{ctx.workflow_id}'): Raising exception for input '{data}'")
            raise ValueError(f"This activity always fails with input: {data}")

        @wfr.activity(name="compensation_activity")
        def compensation_activity(ctx: WorkflowActivityContext, error_info: dict):
            logger.info(f"Compensation Activity (WF '{ctx.workflow_id}'): Compensating for error: {error_info.get('error_message')}")
            return f"Compensation logic executed for: {error_info.get('failed_activity')}"
        ```
    2.  Create or modify a workflow to call this and handle the error:
        ```python
        @wfr.workflow(name="error_handling_workflow")
        def error_handling_workflow(ctx: DaprWorkflowContext, task_data: str):
            logger.info(f"ErrorHandling WF '{ctx.instance_id}': Starting with '{task_data}'")
            ctx.set_custom_status("Attempting risky operation.")
            activity_result = None
            compensation_result = None
            try:
                activity_result = yield ctx.call_activity(always_fail_activity, input=task_data)
                ctx.set_custom_status("Risky operation succeeded (unexpectedly!).")
            except Exception as e: # Catching a general exception; be more specific if possible
                logger.error(f"ErrorHandling WF '{ctx.instance_id}': Activity 'always_fail_activity' failed: {e}")
                ctx.set_custom_status(f"Caught error: {e}. Performing compensation.")
                
                # Call a compensating activity
                compensation_input = {"failed_activity": "always_fail_activity", "error_message": str(e)}
                compensation_result = yield ctx.call_activity(compensation_activity, input=compensation_input)
                
                ctx.set_custom_status(f"Compensation done: {compensation_result}. Workflow will now fail.")
                # Option: Re-raise the exception if the workflow itself should be marked as FAILED
                # raise WorkflowFailureError(f"Workflow failed after compensation due to: {e}") from e
                # Or, if compensation means success, return a success status.
                # For this example, let's consider compensation as handling, but the overall operation failed.
                # To mark workflow as FAILED, you'd typically re-raise or raise a specific workflow error.
                # If not re-raised, the workflow will complete successfully from its perspective.
                # For true failure propagation, re-raising is common.
                # raise # This will mark the workflow as FAILED

            if activity_result:
                 return {"status": "SUCCESS_UNEXPECTED", "result": activity_result}
            else:
                 return {"status": "HANDLED_FAILURE", "compensation": compensation_result, "original_input": task_data}

        ```
    3.  **To test**: Start `error_handling_workflow`. It should attempt `always_fail_activity`, catch the exception, run `compensation_activity`, and then complete (its status will be COMPLETED unless you re-raise the exception). Check the workflow's output and custom status.

## Hands-on Practice

The best way to understand these authoring features is to use them:
1.  **Extend `01_hello_workflow`**: Try adding a timer, a custom status update, or make the activity simulate a failure to test retry policies.
2.  **Create Small, Focused Examples**: For each feature (child workflows, external events), create a new minimal workflow application to see it in action.
3.  **Experiment**: Change inputs, add logging, and observe the workflow's behavior and state via the `/status` endpoint or Dapr dashboard/logs.
4.  Observe logs from Tilt and the application.

## Next Steps

With a solid grasp of authoring individual workflow features by implementing them hands-on, you are now ready to see how these are combined to create sophisticated orchestrations. Proceed to **`04_patterns`** to explore common and powerful workflow patterns and their implementations.

#### More Configs
- Waiting for External Events [Dapr How to: Author Workflows - External Events](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/#external-events).

- Setting Custom Workflow Status (`ctx.set_custom_status`) [Dapr How to: Author Workflows - Custom Status](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/#custom-status).

-  Continue As New (`ctx.continue_as_new`) [Dapr How to: Author Workflows - Continue As New](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-author-workflow/#continue-as-new).

- Deterministic Logic Utilities (`ctx.current_utc_date_time`, `ctx.new_guid`) [Dapr Workflow Features - Workflow determinism](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#workflow-determinism-and-code-restraints).