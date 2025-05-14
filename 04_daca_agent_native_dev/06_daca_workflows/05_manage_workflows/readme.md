# 05: [Managing Dapr Workflow Instances](https://docs.dapr.io/developing-applications/building-blocks/workflow/howto-manage-workflow/)

Once workflows are authored and running, you need ways to manage their lifecycle. This section covers using the Dapr Workflow Management API (typically HTTP).

**Key Topics:**
*   Starting a new workflow instance (with optional instance ID and input).
*   Querying the status and metadata of a workflow instance.
*   Pausing a running workflow.
*   Resuming a paused workflow.
*   Terminating a workflow instance.
*   Raising external events to a waiting workflow.
*   Purging workflow instance history from the state store.
*   Tools for interacting with the Workflow API (e.g., `curl`, Postman, Dapr Dashboard if applicable).