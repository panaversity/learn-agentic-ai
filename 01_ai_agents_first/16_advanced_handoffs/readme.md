# Advanced Handoffs MasterClass

You've learned how to transfer a conversation from one agent to another—the basic "call transfer." Now, it's time to upgrade that to a **VIP transfer**, where the next agent receives a full briefing, knows exactly what to do, and sees only the information relevant to their task.

> **The Big Idea:** Advanced handoffs are not just about routing; they are about orchestrating a clean, intelligent, and context-rich transition between specialists. You're the director, ensuring every actor has the right script and cues.

### What We'll Master in This Step

This guide will equip you with the skills to manage sophisticated, multi-agent workflows. We will answer these key questions:

*   **Customizing the Handoff:** How can I change the handoff's name and description for the LLM, and how do I run code (like logging) the moment a handoff is triggered?
*   **Passing Structured Data:** How can I make the first agent pass a detailed "briefing" (like an escalation reason) to the next agent using structured data?
*   **Controlling the Narrative:** How do I clean up the conversation history before the next agent sees it, so they aren't confused by irrelevant tool calls?
*   **Ensuring Reliability:** What's the best way to prompt an agent so it knows when and how to hand off correctly?
*   **Managing Multi-Turn Conversations:** After a handoff, how do I ensure the user continues talking to the correct specialist agent?

---

## Part 1: The VIP Briefing – Customizing and Passing Data

A basic handoff is a blind transfer. An advanced handoff includes a detailed briefing note. You can customize how the handoff looks to the LLM and pass critical data along with it.

This is all done with the `handoff()` function.

### Customizing the Tool & Adding Callbacks

You can change the `tool_name` and `description` the LLM sees and trigger an `on_handoff` function the moment the transfer is initiated.

*   **Use Case:** Rename `transfer_to_refund_agent` to `escalate_to_refunds` for clarity and log the event for auditing purposes.

```python
from agents import Agent, handoff, RunContextWrapper

def log_handoff_event(ctx: RunContextWrapper):
    print(f"HANDOFF INITIATED: Transferring to the Escalation Agent at {ctx.current_timestamp_ms}")

specialist = Agent(name="Escalation Agent")
custom_handoff = handoff(
    agent=specialist,
    tool_name_override="escalate_to_specialist",
    tool_description_override="Use this for complex issues that require a specialist.",
    on_handoff=log_handoff_event,
)
```

### Passing Structured Data with `input_type`

This is the most powerful feature. You can require the LLM to provide structured data (using a Pydantic model) when it calls the handoff. This is the "briefing note."

*   **Use Case:** When escalating to a refunds agent, force the triage agent to provide a `reason` and `order_id`.

```python
from pydantic import BaseModel

class EscalationData(BaseModel):
    reason: str
    order_id: str

async def on_escalation(ctx: RunContextWrapper, input_data: EscalationData):
    print(f"Escalating order {input_data.order_id} because: {input_data.reason}")

escalation_agent = Agent(name="Escalation agent")
escalation_handoff = handoff(
    agent=escalation_agent,
    on_handoff=on_escalation,
    input_type=EscalationData, # The LLM must provide this data
)
```

---

## Part 2: A Clean Slate – Filtering Conversation History

By default, the new agent sees the *entire* conversation history, including all previous tool calls. This can be noisy. You can use an `input_filter` to clean it up.

The SDK provides pre-built filters in `agents.extensions.handoff_filters`.

*   **Use Case:** A triage agent uses several tools to diagnose a problem. When handing off to an FAQ agent, hide all that technical "noise" so the FAQ agent just sees the user's questions.

```python
from agents.extensions import handoff_filters

faq_agent = Agent(name="FAQ agent")
faq_handoff = handoff(
    agent=faq_agent,
    # This removes all tool call/output history for the next agent.
    input_filter=handoff_filters.remove_all_tools,
)
```

---

## Part 3: Managing the Full Conversation

A handoff isn't the end; it's the middle. You need to prompt the agent to make smart handoff decisions and then ensure the conversation continues with the right specialist.

### Prompting for Success

Make your handoff instructions explicit. The SDK provides a recommended text snippet to add to your prompts to make them more reliable.

```python
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

triage_agent = Agent(
    name="Triage Agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Your primary job is to diagnose the user's problem.
    If it is about billing, handoff to the Billing Agent.
    If it is about refunds, handoff to the Refund Agent."""
)
```

### Continuing the Conversation with the Specialist

After a handoff, who handles the user's next message? You have two patterns.

1.  **Resume with the Triage Agent (Simple & Safe):** Pass the entire history back to your main entry agent. It will see the previous handoff and can decide to route to the same specialist again.
2.  **Resume with the Specialist (Efficient):** Get the agent that replied last (`result.last_agent`) and start the next turn directly with them. This avoids going through triage again.

```python
# Turn 1: Triage hands off to the Refunds specialist
result1 = await Runner.run(triage_agent, "I need a refund for order #123.")
print(f"Reply from: {result1.last_agent.name}")
print(f"Message: {result1.final_output}")

# The user replies: "Thanks, how long will it take?"
follow_up_message = {"role": "user", "content": "Thanks, how long will it take?"}

# --- PATTERN 2: CONTINUE WITH THE SPECIALIST ---
# Get the agent that answered last (e.g., the Refunds Agent)
specialist = result1.last_agent
# Create the input for the next turn, including all prior history
follow_up_input = result1.to_input_list() + [follow_up_message]

# Run the next turn starting directly with the specialist
result2 = await Runner.run(specialist, follow_up_input)
print(f"Reply from: {result2.last_agent.name}")
print(f"Message: {result2.final_output}")
```

---

## 🆚 When to prefer handoffs vs agents-as-tools (cheat sheet)

- **🤝 Handoffs**: long, specialized dialogs where a different agent should **own the conversation** (e.g., a “Refunds Agent” continues asking for order ID, initiates refund).
- **🛠 Agents-as-tools**: quick, scoped skill borrow (translate/parse) while the main agent **keeps the mic**.

---

## ⚠ Gotchas & guardrails

- 📢 Make routing explicit in prompts.
- 🧹 Sanitize history between agents if needed.
- 🔄 Keep `result.last_agent` if continuing with the same specialist.

---

## Your Turn: A Mini-Lab

Let's build an advanced customer support handoff system.

```python
from agents import Agent, Runner, handoff, RunContextWrapper
from agents.extensions import handoff_filters
from pydantic import BaseModel
import asyncio

# --- Define the data for our "briefing note" ---
class HandoffData(BaseModel):
    summary: str

# --- Define our specialist agents ---
billing_agent = Agent(name="Billing Agent", instructions="Handle billing questions.")
technical_agent = Agent(name="Technical Support Agent", instructions="Troubleshoot technical issues.")

# --- Define our on_handoff callback ---
def log_the_handoff(ctx: RunContextWrapper, input_data: HandoffData):
    print(f"\n[SYSTEM: Handoff initiated. Briefing: '{input_data.summary}']\n")

# --- TODO 1: Create the advanced handoffs ---

# Create a handoff to `billing_agent`.
# - Override the tool name to be "transfer_to_billing".
# - Use the `log_the_handoff` callback.
# - Require `HandoffData` as input.
to_billing_handoff = handoff(
    # Your code here
)

# Create a handoff to `technical_agent`.
# - Use the `log_the_handoff` callback.
# - Require `HandoffData` as input.
# - Add an input filter: `handoff_filters.remove_all_tools`.
to_technical_handoff = handoff(
    # Your code here
)

# --- Triage Agent uses the handoffs ---
triage_agent = Agent(
    name="Triage Agent",
    instructions="First, use the 'diagnose' tool. Then, based on the issue, handoff to the correct specialist with a summary.",
    tools=[
        # A dummy tool for the triage agent to use
        function_tool(lambda: "The user's payment failed.")("diagnose")
    ],
    handoffs=[to_billing_handoff, to_technical_handoff],
)


async def main():
    print("--- Running Scenario: Billing Issue ---")
    result = await Runner.run(triage_agent, "My payment won't go through.")
    print(f"Final Reply From: {result.last_agent.name}")
    print(f"Final Message: {result.final_output}")

# asyncio.run(main())
```

#### ✅ Expected Outcome

When you complete the `TODO`s and run the lab, your output should show:
1.  A system message logging the handoff with a summary like "User's payment failed."
2.  The final reply coming from the "Billing Agent."

---

## 🏁 Wrap-Up

*   **What it is:** A set of powerful controls to manage the transfer of a conversation between agents.
*   **When to use it:** When building multi-agent systems that require clear roles, context passing, and clean conversation flows.
*   **How to do it:** Use the `handoff()` function to customize the `tool_name`, trigger `on_handoff` callbacks, pass structured data with `input_type`, and clean the conversation with `input_filter`. Always give clear handoff instructions in your prompts.