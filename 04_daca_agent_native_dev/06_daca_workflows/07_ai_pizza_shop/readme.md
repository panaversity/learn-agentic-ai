# 06: Challenge: [AI Pizza Shop - A DACA Workflow Example](https://github.com/diagrid-labs/dapr-workshop)

This section brings together many of the concepts learned in previous sections to build a practical, AI-driven application: "The AI Pizza Shop." This example will demonstrate how Dapr Workflows can orchestrate a more complex process within a DACA context.

**Key Features to Implement:**
*   Order intake via an API.
*   Workflow to process a pizza order:
    *   Activity: Validate order (AI-based suggestion for toppings?).
    *   Activity: Process payment (mocked).
    *   Activity: Send to kitchen (AI agent to optimize baking queue?).
    *   Activity: Notify customer on progress.
*   Potential use of child workflows for sub-processes (e.g., inventory check).
*   Integration with other Dapr building blocks (e.g., state, pub/sub for notifications).