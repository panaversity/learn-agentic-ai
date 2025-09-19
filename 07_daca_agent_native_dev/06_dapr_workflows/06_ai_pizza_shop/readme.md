# AI Pizza Shop - Dapr Workflow Challenge

## 🎯 Learning Objectives

By completing this challenge, you will be able to:

- Design and implement a multi-step, stateful business process using Dapr Workflows.
- Define and orchestrate workflow activities, including error handling and retries.
- Utilize child workflows for modular process decomposition.
- Incorporate durable timers for scheduled delays.
- Apply concepts like (mocked) AI integration and simulated payment processing within a workflow.
- (Bonus) Implement advanced patterns like compensation, parallel execution (fan-out/fan-in), and human-in-the-loop interactions.

## 🚀 Goal

Welcome to the Dapr Workflows capstone challenge! In this project, you will build a simplified AI-enhanced pizza ordering and preparation system using Dapr Workflows. This will allow you to apply the various concepts and patterns learned throughout the "Dapr Workflows" modules.

## 🍕 Scenario Overview

Imagine an "AI Pizza Shop" where customers can place orders for pizzas. The system, powered by Dapr Workflows, will handle order validation, suggest toppings with a touch of (mocked) AI, process payments, manage kitchen preparation steps, and notify the customer.

In this challenge, Dapr Workflows act as the central orchestrator for this business process. Each activity defined within the workflow (e.g., validating an order, processing a payment, suggesting a topping) can be thought of as a distinct unit of work that, in a larger distributed system, might represent a call to an independent microservice. This challenge focuses on mastering the workflow orchestration itself.

## ✅ Core Requirements (Minimum Viable Product - MVP)

Your primary task is to implement the main order processing workflow and its associated activities.

1.  **Order Placement Endpoint:**

    - Create a FastAPI endpoint (e.g., `/order_pizza`) that accepts a JSON payload like:
      ```json
      {
        "customer_name": "Ada Lovelace",
        "pizza_type": "Margherita",
        "quantity": 1
      }
      ```
    - This endpoint should trigger a new `OrderProcessingWorkflow`.

2.  **`OrderProcessingWorkflow`:** This is your main parent workflow.

    - **Input:** Customer name, pizza type, quantity.
    - **Steps:**
      1.  **Call `ValidateOrderActivity`**:
          - **Input:** Order details.
          - **Logic:** Basic validation (e.g., `pizza_type` is known, `quantity` > 0).
          - **Output:** Boolean indicating validity, or raise an error if invalid.
      2.  **Call `AIToppingSuggestionActivity` (Mocked AI):**
          - **Input:** `pizza_type`.
          - **Logic:** Simulate an AI suggestion. For example, if `pizza_type` is "Pepperoni", return "Extra Cheese"; if "Veggie", return "Olives".
          - **Output:** A string with the suggested topping.
      3.  **Call `ProcessPaymentActivity` (Simulated with Retry):**
          - **Input:** Order total (can be a fixed amount for simplicity).
          - **Logic:** Simulate payment processing. This activity should be designed to fail a couple of times before succeeding to demonstrate retry policies.
          - **Retry Policy:** Implement a `RetryPolicy` (e.g., 3 attempts, 1-second initial interval).
          - **Output:** Payment confirmation status.
      4.  **Call `KitchenPreparationWorkflow` (as a Child Workflow):**
          - **Input:** `pizza_type`, `quantity`, suggested topping.
          - **Output:** Confirmation that preparation is complete.
      5.  **Call `NotifyCustomerActivity`:**
          - **Input:** `customer_name`, order details, preparation status.
          - **Logic:** Log a message like "Dear Ada Lovelace, your Margherita pizza with Extra Cheese is ready!"
          - **Output:** Notification status.
    - **Output:** A summary of the order processing (e.g., "Order for Ada Lovelace processed successfully. Enjoy your Margherita!").

3.  **`KitchenPreparationWorkflow` (Child Workflow):**

    - **Input:** `pizza_type`, `quantity`, suggested topping from parent.
    - **Steps (for each pizza in the quantity):**
      1.  **Call `MakeDoughActivity`:**
          - **Logic:** Log "Making dough for Margherita."
      2.  **Call `AddToppingsActivity`:**
          - **Input:** `pizza_type`, suggested topping.
          - **Logic:** Log "Adding toppings (including Extra Cheese) to Margherita."
      3.  **Call `BakePizzaActivity` (with Timer):**
          - **Logic:** Log "Baking Margherita..." and then use `ctx.create_timer()` to simulate a 5-10 second baking time. After the timer, log "Margherita is baked!"
    - **Output:** "Kitchen preparation complete for [quantity] [pizza_type]."

4.  **Activities:**
    - `ValidateOrderActivity`
    - `AIToppingSuggestionActivity`
    - `ProcessPaymentActivity`
    - `MakeDdoughActivity`
    - `AddToppingsActivity`
    - `BakePizzaActivity`
    - `NotifyCustomerActivity`

We highly encourage you to dive in and build your solution to this challenge from scratch – that's where the deepest learning happens! However, if you get stuck, need a little inspiration, or want to compare your approach after you're done, a [reference implementation is available here](https://github.com/mjunaidca/ai-pizza-challenge-dapr-workflows). Use it to spark ideas and enhance your own unique version!

## 🌟 Bonus Challenges / Advanced Features

Once the MVP is working, try to extend it with these features:

1.  **Advanced Error Handling & Compensation:**
    - If `BakePizzaActivity` fails (e.g., simulate an oven malfunction by raising an exception), the `KitchenPreparationWorkflow` should catch this.
    - Implement a `NotifyKitchenStaffActivity` as a compensation if baking fails.
2.  **Parallel Pizza Preparation:**
    - Modify `OrderProcessingWorkflow` and `KitchenPreparationWorkflow` to handle an order with `quantity` > 1 by preparing each pizza in parallel (hint: fan-out/fan-in with multiple child `KitchenPreparationWorkflow` instances or by parallelizing activity calls within a single kitchen workflow for multiple pizzas if child workflow per pizza is too much).
3.  **Human-in-the-Loop (HITL) for Quality Check:**
    - After `BakePizzaActivity`, have the `KitchenPreparationWorkflow` pause and wait for an external event named `pizza_quality_approved` (using `ctx.wait_for_external_event`).
    - You'll need an additional FastAPI endpoint to raise this event for a given workflow instance.
4.  **Basic Inventory Check (Saga-like element):**
    - Before `ProcessPaymentActivity`, call a new `CheckInventoryActivity`.
    - If inventory is insufficient (simulated), the workflow should not proceed to payment and should end with an appropriate message.
    - If payment then fails, consider if a `ReleaseInventoryHoldActivity` compensation is needed.
5.  **Persistent Order Status:**
    - Use `ctx.set_custom_status()` at various stages of the `OrderProcessingWorkflow` (e.g., "Validating Order", "Processing Payment", "In Kitchen", "Ready").
    - Ensure your `/status/{instance_id}` endpoint reflects these custom statuses.

## Considerations for a Full DACA Application (Beyond this Workflow Challenge)

While this challenge focuses on Dapr Workflows, a production-grade AI Pizza Shop within the DACA framework would likely integrate other Dapr building blocks for enhanced capabilities:

- **Dapr Pub/Sub:** For truly decoupled, event-driven notifications. Instead of `NotifyCustomerActivity` directly logging, it could publish an `OrderReadyEvent` to a message broker. Other services (e.g., a dedicated Notification Service, a Customer Dashboard Service) could subscribe to these events.
- **Dapr State Management:** For managing durable, queryable order state accessible across different services, beyond the workflow instance's internal state. For example, storing the canonical order details and its evolving status in a shared state store like Redis or CosmosDB.
- **Dapr Service Invocation:** If activities like `ProcessPaymentActivity` or `AIToppingSuggestionActivity` were implemented as separate microservices, the workflow activities would use Dapr Service Invocation to call them reliably.
- **Dapr Bindings:** For integrating with external systems, such as sending an SMS notification via Twilio when the pizza is out for delivery, or receiving orders from an external ordering platform.

These considerations provide a roadmap for how the concepts learned in this workflow challenge can be expanded into a more comprehensive microservices-based application using the full suite of Dapr's capabilities, aligning with the DACA vision.

## 🛠️ Key Dapr Workflow Concepts to Apply

- Workflow Definition (`@wfr.workflow`)
- Activity Definition (`@wfr.activity`)
- Starting Workflows (`DaprWorkflowClient().schedule_new_workflow()`)
- Calling Activities (`ctx.call_activity()`)
- Child Workflows (`ctx.call_child_workflow()`)
- Timers (`ctx.create_timer()`)
- Retry Policies (`dapr.ext.workflow.RetryPolicy`)
- Error Handling (try/except blocks in workflows)
- External Events (`ctx.wait_for_external_event()`, `client.raise_workflow_event()`) (Bonus)
- Setting Custom Status (`ctx.set_custom_status()`) (Bonus)

## 🏁 Getting Started

1.  **Prerequisites:**
    - Dapr CLI installed and initialized.
    - Python 3.x installed.
    - `dapr` and `dapr-ext-workflow` Python packages installed.
    - A code editor (e.g., VS Code).
    - Familiarity with FastAPI (for creating API endpoints).
2.  **Base Code:** You can use the `00_starter-code` from this module or adapt code from `01_hello_workflow` or `03_author_workflows`.
3.  **Structure:** Create a `main.py` (or similar) in the `06_ai_pizza_shop` directory.
4.  **Iterate:** Start with the `OrderProcessingWorkflow` and one or two activities. Test, then add more complexity step-by-step.
5.  **Simulate:** For external systems (AI, Payment), simple logging or random failures are sufficient. The focus is on workflow orchestration.

## 🤔 Self-Assessment Pointers

- Can you successfully place an order and see it through all MVP steps?
- Does the `AIToppingSuggestionActivity` provide a suggestion?
- Does the `ProcessPaymentActivity` demonstrate retries upon simulated failures?
- Is the `KitchenPreparationWorkflow` correctly invoked as a child workflow?
- Does the `BakePizzaActivity` use a timer effectively?
- Are customer notifications logged?
- (For Bonus) Do your advanced features work as expected? Can you demonstrate compensation, parallel processing, HITL, or inventory logic?

Good luck, and have fun building your AI Pizza Shop with Dapr Workflows!
