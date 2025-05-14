# 07: [Advanced Workflow Configuration & Features](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/)

This section explores advanced topics for building robust, production-ready Dapr Workflows.

## Dapr Workflows Breakdown
Dapr Workflows are functions you write that define a series of tasks to be executed in a particular order. The Dapr Workflow engine takes care of scheduling and execution of the tasks, including managing failures and retries. If the app hosting your workflows is scaled out across multiple machines, the workflow engine may also load balance the execution of workflows and their tasks across multiple machines.

There are several different kinds of tasks that a workflow can schedule, including

- Activities for executing custom logic
- Durable timers for putting the workflow to sleep for arbitrary lengths of time
- Child workflows for breaking larger workflows into smaller pieces
- External event waiters for blocking workflows until they receive external event signals.

1. WorkFlow Identity: Each workflow you define has a type name, and individual executions of a workflow require a unique instance ID. 
2. Workflow replay: Dapr Workflows maintain their execution state by using a technique known as event sourcing. Instead of storing the current state of a workflow as a snapshot, the workflow engine manages an append-only log of history events that describe the various steps that a workflow has taken. 
3. Following two techniques help write workflows that may need to schedule extreme numbers of tasks:
    1. Use the continue-as-new API
    2. Use child workflows
4. Workflow activities: Workflow activities are the basic unit of work in a workflow and are the tasks that get orchestrated in the business process.
5. Retry policies: Workflows support durable retry policies for activities and child workflows. Workflow retry policies are separate and distinct from Dapr resiliency policies.

**Key Topics:**
*   **Observability:**
    *   Configuring and interpreting Dapr metrics for workflows (Prometheus).
    *   Distributed tracing for workflows and activities (Jaeger/OpenTelemetry).
    *   Best practices for logging in workflows.
*   **Error Handling & Resilience:**
    *   Advanced error handling patterns within workflows.
    *   Compensation logic (Sagas).
    *   Configuring retry policies (if available at activity/workflow component level).
*   **Testing Strategies:**
    *   Unit testing workflow and activity logic (mocking).
    *   Integration testing workflows with other Dapr components.
*   **State Management for Workflows:**
    *   Choosing and configuring state stores for workflow persistence.
    *   Understanding potential limitations (e.g., state store specific constraints).
*   **Workflow Versioning:**
    *   Strategies for managing changes and updates to workflow definitions.
*   **Performance & Scalability:**
    *   Considerations for designing high-throughput workflows.
    *   Understanding workflow engine concurrency.
*   **Advanced SDK Features & Nuances.**