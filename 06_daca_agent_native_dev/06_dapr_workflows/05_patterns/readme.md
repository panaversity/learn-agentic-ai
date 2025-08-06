# 04: [Common Dapr Workflow Patterns](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns/)

Dapr Workflows can implement various standard orchestration patterns. This section explores common patterns and provides examples of how to realize them using Dapr Workflows.

For practical implementation, the code from the `01_hello_workflow` module can serve as a starting point for building out these patterns.

**[Key Workflow Design Patterns](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-patterns):**

- **Sequential Execution (Task Chaining):**

  - Activities are executed one after another in a defined sequence. The output of one activity can be the input to the next. This is the most fundamental pattern.
  - _Example:_ Processing an order: 1. Validate order -> 2. Process payment -> 3. Update inventory -> 4. Notify user.

- **Parallel Execution (Fan-out/Fan-in):**

  - Multiple activities are executed concurrently (fan-out), and the workflow waits for all (or some) of them to complete before proceeding (fan-in).
  - _Example:_ Fetching product details from multiple suppliers simultaneously, then aggregating the results.

- **Async HTTP APIs with Workflows:**

  - A long-running operation is initiated via an HTTP request. The workflow starts, returns a pending status and an instance ID. The client can then poll for completion or be notified via a callback. Dapr Workflow manages the state of the long-running operation.
  - _Example:_ Triggering a video processing job that might take several minutes or hours.

- **Saga Pattern:**

  - Manages distributed transactions by orchestrating a sequence of local transactions. If any step fails, the Saga executes compensating transactions to undo preceding operations, ensuring data consistency.
  - _Example:_ A trip booking workflow involving booking a flight, a hotel, and a car rental. If the hotel booking fails, the flight and car rental (if already booked) must be canceled.

- **Monitor Pattern:**
  - A workflow that periodically checks the status of a resource or process. This often involves timers and can run for extended periods. For very long-running or indefinite monitors, the `continue_as_new` feature is essential to prevent excessively long workflow histories.
  - _Example:_ Monitoring an external service's health by pinging it every 5 minutes. If it's down, send an alert.

**[Challenge: Advanced Techniques](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/):**

- **Workflow Replay and Determinism:**

  - Dapr Workflows ensure reliability by event sourcing. The workflow engine replays the history of activity executions to reconstruct the state when a workflow instance resumes (e.g., after a host crashes or during `continue_as_new`).
  - **Crucially, this means workflow code (the orchestrator logic) and activity code must be deterministic.** Given the same input, they must produce the same output and call the same sequence of activities. Avoid using non-deterministic functions (like `Math.random()` or `DateTime.Now` directly in orchestrator logic without passing them as activity results) within the workflow definition itself.
  - _Reading:_ Understand why determinism is critical for reliable replay.

- **Scheduling Many Tasks (`continue_as_new` and Child Workflows):**
  - **`continue_as_new`**: Allows a workflow instance to effectively restart itself with a new input, optionally carrying over some state, without growing its history indefinitely. This is vital for infinite loops or very long-running workflows (like Monitors).
  - **Child Workflows**: A workflow can start other workflows as children. This helps in modularizing complex logic, managing lifecycle independently (to some extent), and can also be a strategy for handling a large number of parallel tasks by breaking them into smaller, manageable child workflows.
  - _Reading:_ Explore scenarios where `continue_as_new` is preferred over a simple loop, and when to use child workflows for better organization or scale.

- **Human-in-the-Loop / External Event Pattern:**

  - The workflow pauses and waits for an external event, often a human action (e.g., an approval) or a message from another system, before proceeding. This typically uses `wait_for_external_event` in the Dapr Workflow SDK.
  - _Example:_ An expense report workflow waits for a manager's approval, which is submitted via a separate UI that then raises an event to the workflow instance.
  - _Challenge:_ Implement a simple workflow that waits for an "approval" event before completing.


We have covered the key patterns and as a challenge you will follow this guide to implement Advanced Techniques.