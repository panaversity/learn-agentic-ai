# 07: [Advanced Workflow Configuration & Features](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/)

This section explores advanced topics for building robust, production-ready Dapr Workflows.

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