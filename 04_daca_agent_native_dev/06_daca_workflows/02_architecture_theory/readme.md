# 02: [Dapr Workflow Architecture](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/) Theory

This section delves into the internal architecture of Dapr Workflows. Understanding how Dapr Workflows operate "under the hood" is crucial for designing robust applications, effective troubleshooting, and leveraging advanced features. 

The primary reference for this section is the official [Dapr Workflow Architecture documentation](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/).

# 02: Dapr Workflow Architecture Deep Dive

This section delves into the internal architecture of Dapr Workflows. Understanding how Dapr Workflows operate "under the hood" is crucial for designing robust applications, effective troubleshooting, and leveraging advanced features. The primary reference for this section is the official [Dapr Workflow Architecture documentation](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/).

See Dapr Workflow architecture in Kubernetes mode:

![Dapr Workflow architecture in Kubernetes mode](./k8-workflow-engine.png)

## Core Architectural Principles

By default, Dapr Workflows are implemented using a system of **Dapr Actors**. This actor-based model is fundamental to how workflows achieve statefulness, reliability, and scalability. The Dapr sidecar (`daprd`) hosts the workflow engine. Your application code, written using a Dapr Workflow SDK (e.g., `dapr-ext-workflow` for Python), defines workflows and activities. The SDK communicates with the workflow engine in the sidecar, typically via gRPC.

## Key Architectural Components (Actor-Based Backend)

The Dapr Workflow engine is built upon the [Durable Task Framework for Go](https://github.com/microsoft/durabletask-go), with Dapr Actors serving as the default backend for managing workflow state and execution.

### [1. Workflow Actors](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#workflow-actors)

Workflow Actors are the heart of the orchestration for each workflow instance.

*   **Role**: Each instance of a workflow you define is managed by a dedicated Workflow Actor. This actor is responsible for:
    *   Orchestrating the execution of your workflow logic.
    *   Managing the state of the workflow instance.
    *   Determining the placement of the workflow execution via the Dapr actor placement service.
*   **Actor ID**: The ID of the Workflow Actor is the same as the `instance_id` of the workflow it manages.
*   **State Storage**: Workflow Actors persist their state in the Dapr-configured state store. This state is meticulously structured using several key patterns:
    *   `inbox-NNNNNN`: A FIFO queue of messages that drive the workflow's execution. Messages can include workflow creation requests, activity task completion notifications, timer expirations, or external events. Each message is stored as a separate key in the state store.
    *   `history-NNNNNN`: An append-only log of all significant events that have occurred during the workflow's execution (e.g., workflow started, activity scheduled, activity completed, timer created). Each event is also a separate key. This history is crucial for replay and durability.
    *   `customStatus`: Stores any custom status payload set by the workflow code.
    *   `metadata`: Contains meta-information about the workflow, such as the length of the inbox and history logs, and a generation counter for instance ID reuse scenarios.
*   **Lifecycle**:
    1.  A Workflow Actor is activated upon receiving a new message in its inbox (e.g., a request to start a new workflow instance).
    2.  The message triggers the execution (or resumption) of your workflow code within your application.
    3.  Your workflow code (the orchestrator function) yields an execution result (e.g., tasks to schedule, state changes).
    4.  The actor schedules any specified tasks (like activities or timers) by sending messages, potentially to other actors (Activity Actors).
    5.  The actor updates its own state (inbox, history, metadata) in the state store to reflect the progression.
    6.  The actor may then go idle, potentially being unloaded from memory by the Dapr sidecar, until another message (like an activity completion or timer event) arrives in its inbox.

*(Reference: [Dapr Workflow Architecture - Workflow Actors](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#workflow-actors))*

### [2. Activity Actors](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#activity-actors)

Activity Actors manage the execution of individual activity tasks scheduled by a Workflow Actor.

*   **Role**: A new Activity Actor instance is activated for *every* activity task scheduled by a workflow. It manages the invocation of your activity code.
*   **Actor ID**: The ID is a combination of the parent Workflow Actor's ID and a sequence number (e.g., `[WorkflowInstanceID]::[SequenceNumber]`), ensuring uniqueness for each activity invocation within a workflow instance.
*   **State Storage**: Each Activity Actor stores a single key during its brief lifetime:
    *   `activityState`: Contains the activity invocation payload, including the serialized input data. This key is automatically deleted after the activity completes and its result is sent back to the parent Workflow Actor.
*   **Lifecycle**: Activity Actors are typically short-lived:
    1.  Activated when a Workflow Actor schedules an activity (by sending it a message).
    2.  Immediately calls into your application to invoke the corresponding activity code with the provided input.
    3.  Once the activity code returns a result, the Activity Actor sends this result as a message to its parent Workflow Actor.
    4.  The parent Workflow Actor consumes this result (via its inbox) and proceeds with its execution.

*(Reference: [Dapr Workflow Architecture - Activity Actors](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#activity-actors))*

## Durability, Fault Tolerance, and Execution Guarantees

### The "Replay" Mechanism and `yield`

The `yield` keyword in your Python workflow orchestrator function is the hook into Dapr's durability mechanism:
1.  When the Dapr workflow engine encounters an action like `yield ctx.call_activity(...)`, it records the intent to perform that action.
2.  The current state of the workflow orchestrator (local variables, current point in code) is snapshotted and appended to its `history-NNNNNN` log in the state store.
3.  The workflow can then be "dehydrated" (removed from memory if idle).
4.  When the awaited action completes (e.g., an activity finishes), the workflow is "rehydrated":
    *   Its Workflow Actor is activated.
    *   The workflow orchestrator code is **re-executed from the beginning**.
    *   During this replay, the engine consults the persisted history. If an action (like a specific activity call) is found in the history as already completed, that code block is **not re-executed**. Instead, its recorded result from history is used.
    *   Local variables are restored to their persisted state as the code replays up to the point of interruption or the next `yield`.
    *   This replay continues until the workflow either reaches a `yield` for an action not yet in history, or it completes.

This replay technique is fundamental to how Dapr Workflows achieve fault tolerance.

### [Reminder Usage for Fault Tolerance](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#reminder-usage-and-execution-guarantees)

Dapr Workflows leverage Dapr Actor reminders to recover from transient system failures, such as a sidecar or application node crashing:
*   Before the workflow engine invokes your application's workflow or activity code, the corresponding Workflow or Activity Actor creates a Dapr reminder.
*   If your code executes successfully and returns its result, this reminder is deleted by the actor.
*   If a crash occurs *before* the reminder is deleted, the reminder will eventually fire (as per Dapr's reminder mechanism).
*   This reminder reactivation will trigger the actor again, leading to a retry of the workflow/activity execution, often involving the replay mechanism described above to ensure it resumes from a consistent state.
*   **Note**: A very high number of active reminders in a Dapr cluster can potentially impact performance.

*(Reference: [Dapr Workflow Architecture - Reminder usage and execution guarantees](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#reminder-usage-and-execution-guarantees))*

## [State Store Interaction Details](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#state-store-usage)

*   The internal workflow and activity actors use the Dapr-configured state store (the same one used for any other Dapr Actors in your application). This means any state store component that supports Dapr Actors implicitly supports Dapr Workflow.
*   Workflows save their state incrementally by appending to the history log, which is distributed across multiple state store keys. This makes each "checkpoint" (usually at a `yield` point) efficient, as it doesn't require updating a single large document.
*   **State Store Limitations Impact Workflows**:
    *   **Item Size Limits**: If your state store has a limit on the size of a single item (e.g., Azure Cosmos DB's 2MB limit per document), this can constrain the maximum size of inputs/outputs for your activities and child workflows, as these are stored as individual history events.
    *   **Batch Transaction Limits**: If a state store limits the size or number of operations in a batch transaction, it might restrict how many parallel actions a workflow can effectively checkpoint simultaneously. This is more relevant for complex fan-out/fan-in patterns where many activities complete around the same time.
*   **Purging**: As workflow history can accumulate, Dapr SDKs provide APIs for purging workflow data for instances that have reached a terminal state (`COMPLETED`, `FAILED`, `TERMINATED`).

*(Reference: [Dapr Workflow Architecture - State store usage](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#state-store-usage))*

## Workflow Determinism: A Critical Requirement

For the replay mechanism to work reliably, **workflow orchestrator code must be deterministic**. This means that given the same history of events, the workflow code must always make the same decisions and schedule the same sequence of tasks with the same inputs.

*   **Why?** During replay, the engine doesn't re-execute already completed activities; it uses their historical results. If the orchestrator code behaves differently on replay (e.g., tries to call a different activity or the same activity with different input than what's in the history), the workflow's integrity breaks.
*   **Key Rules for Deterministic Workflow Orchestrators**:
    1.  **No non-deterministic APIs**: Avoid direct calls to functions that produce different results on each call (e.g., `random.random()`, `datetime.now()`, `uuid.uuid4()`).
        *   **Solution**: Perform such operations in *activities* (which are executed once and their results recorded), or use SDK-provided deterministic equivalents (e.g., `ctx.current_utc_date_time`, `ctx.new_guid`).
    2.  **Only indirect interaction with external state**: The orchestrator shouldn't directly read environment variables, access file systems, or make arbitrary network calls.
        *   **Solution**: Pass external data as workflow input, or have activities interact with external systems and return results.
    3.  **Single-threaded execution logic**: Workflow orchestrator logic must operate on the single dispatch thread provided by the SDK. Do not manually create threads or use asynchronous callbacks that execute on different threads from within the orchestrator code.
        *   **Solution**: Delegate concurrent or background work to activities, which can be scheduled to run in parallel by the workflow engine.
*   **Updating Workflow Code**: Modifying existing workflow definitions (e.g., changing activity call sequences, altering conditional logic based on new inputs not available in old histories) can break determinism for in-flight instances. It's generally recommended to version workflows by creating new definitions for significant changes, allowing old instances to complete on the old code.

*(Reference: [Dapr Workflow Features and Concepts - Workflow determinism and code restraints](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#workflow-determinism-and-code-restraints))*

## Scalability Characteristics

Dapr Workflow scalability is inherently linked to Dapr Actor scalability:
*   The Dapr actor placement service distributes Workflow Actors (and thus workflow instances) across available application instances (pods/nodes).
*   **Factors Influencing Scalability**:
    *   Number of application host machines/pods.
    *   CPU/memory resources available on these hosts.
    *   Performance and scalability of the underlying state store.
    *   Efficiency of the actor placement service and reminder subsystem under load.
*   **Parallelism**: While a single workflow instance's orchestrator logic executes on a single node at any given time, it can achieve high degrees of parallelism by scheduling many activities or child workflows, which can then be distributed across the entire cluster by the placement service.
*   **Important Considerations**:
    *   **Concurrency Control**: Currently, Dapr doesn't impose global limits on the number of concurrent activities or child workflows a single workflow instance can schedule. Developers should design workflows carefully to avoid overwhelming the cluster (a "runaway workflow").
    *   **Uniform Registration**: All instances of a specific workflow application (e.g., all pods for your `daca-workflow-app`) must register the exact same set of workflow and activity definitions. It's not possible to scale certain types of workflows or activities independently of the application they are defined in.

*(Reference: [Dapr Workflow Architecture - Workflow scalability](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#workflow-scalability))*

## Latency Considerations

Due to the necessary state store interactions for durability and the reliance on actor reminders, Dapr Workflows are generally not suited for extremely low-latency (sub-millisecond) operations.
*   **Potential Sources of Latency**:
    *   Network latency to/from the state store when persisting or rehydrating workflow state.
    *   Time taken to rehydrate workflows with very long histories.
    *   Processing overhead from a high number of active reminders in the cluster.
    *   General CPU load on the nodes or within the Dapr sidecar.

*(Reference: [Dapr Workflow Architecture - Workflow latency](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#workflow-latency))*

## Workflow Backend Configuration

*   The "workflow backend" is the Dapr component responsible for orchestrating and persisting workflow state.
*   The **actor-based backend is the default** and is automatically used by Dapr Workflow without requiring an explicit component YAML file.
*   The architecture is designed to potentially support other backend implementations in the future, which would then be configured as named Dapr components.


*(Reference: [Dapr Workflow Architecture - Workflow backend](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/#workflow-backend))*

By understanding these architectural foundations, you are better equipped to design, implement, and troubleshoot complex, resilient, and scalable applications using Dapr Workflows within the DACA framework.