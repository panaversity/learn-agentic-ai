# [Pattern 1: Task Chaining](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/)

This section demonstrates the **Task Chaining** pattern using Dapr Workflows. Task chaining is a fundamental workflow pattern where a sequence of activities (tasks) are executed one after another. The output of one activity often becomes the input for the next, forming a chain of operations.

This pattern is useful for scenarios like:

- Processing data through multiple sequential steps.
- Implementing a business process with ordered stages.
- Any scenario where one operation must complete before the next can begin.

We will adapt the code from the `01_hello_workflow` example to illustrate task chaining. Instead of a single `hello_activity`, we will create a sequence of activities, for example:

1.  `activity_capitalize_name`: Takes a name and capitalizes it.
2.  `activity_generate_greeting`: Takes the capitalized name and generates a greeting string.
3.  `activity_print_greeting`: Takes the greeting string and prints it (simulating a final action).

The workflow will orchestrate these activities in a chain.

## Setup

`01_hello_workflow` is our starter code. Run the server:

```bash
tilt up
```

Once `tilt up` is running, you can access:

- **Tilt UI**: [http://localhost:10350](http://localhost:10350) (Shows the status of your services and logs)
- **Application API Docs (Swagger UI)**: [http://localhost:30080/docs](http://localhost:30080/docs) (To start workflows and check their status)
- **Jaeger UI (for tracing, if configured)**: [http://localhost:16686/](http://localhost:16686/) (To visualize the workflow execution and activity calls)

## Code

Update main.py Workflow
```python
@wfr.workflow(name='random_workflow')
def task_chain_workflow(ctx: wf.DaprWorkflowContext, wf_input: int):
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
```

## Running the Task Chaining Example

1.  **Start the Workflow**:

    - Navigate to the Swagger UI: [http://localhost:30080/docs](http://localhost:30080/docs).
    - Use the `/start` endpoint. Provide a number (e.g., 2).
    - Note the `instance_id` returned.

2.  **Observe Logs**:

    - Check the Tilt UI or your terminal logs for output from the `daca-workflow-container`.
    - You should see log messages indicating the start of the workflow and the execution of each activity in sequence.

3.  **Check Workflow Status**:

    - Use the `/status/{instance_id}` endpoint in the Swagger UI with the `instance_id` you received.
    - Observe the `runtime_status` (e.g., `RUNNING`, `COMPLETED`).
    - When completed, the `serialized_output` should reflect the result of the final activity in the chain.

4.  **Inspect Traces (Optional)**:
    - If Jaeger is configured, open its UI: [http://localhost:16686/](http://localhost:16686/).
    - Find traces for the `daca-workflow` service. You should see a trace for your workflow instance, showing the parent workflow span and child spans for each chained activity.

## Next Steps

After understanding this `readme.md`, the next step is to modify the `main.py` file in the `01_hello_workflow/hello-workflow-code/daca-workflow/` directory (within this `01_task_chaining` folder) to implement the described task chaining logic.

For more details on this and other workflow patterns, refer to the official Dapr documentation:

- [Dapr Workflow Patterns](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/)
- [Task Chaining Specifics](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/#task-chaining)
