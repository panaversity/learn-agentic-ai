# 🤝Advanced Handoff

Go beyond “just route”: 

1. **Rename the handoff tool**
2. **Attach callbacks**
3. **Pass structured input** to the target agent
4. **Filter/clean history** for the receiving agent
5. **Prime prompts** so LLMs route confidently

## 🎨 1. Customizing handoffs (name, description, callback)

You can refine how the handoff appears to the LLM and run side effects at the moment of transfer:

```python
from agents import Agent, handoff, RunContextWrapper

def on_handoff(ctx: RunContextWrapper[None]):
    print("About to hand off — prefetch user profile, start timers, etc.")

specialist = Agent(name="Escalation agent", instructions="Take over complex cases.")
to_escalation = handoff(
    agent=specialist,
    tool_name_override="route_to_escalations",
    tool_description_override="Transfer this user to the Escalations agent.",
    on_handoff=on_handoff,
)
triage = Agent(name="Triage", instructions="Escalate only when needed.", handoffs=[to_escalation])

```

- 🏷`tool_name_override` lets you control the tool name text.
- 📢`on_handoff` fires right when the LLM invokes the handoff—handy for logging or prefetch.
- 📦 You can also accept structured input with `input_type` (next section).

---

## 📦 2. Pass structured data with `input_type`

Sometimes you want the LLM to also pass **structured info** to the receiving agent (e.g., “escalation reason”). Use `input_type`:

```python
from pydantic import BaseModel
from agents import Agent, handoff, RunContextWrapper

class EscalationData(BaseModel):
    reason: str

async def on_escalation(ctx: RunContextWrapper[None], input_data: EscalationData):
    print(f"Escalating because: {input_data.reason}")

escalation_agent = Agent(name="Escalation agent", instructions="Explain next steps and resolve.")
escalation_handoff = handoff(agent=escalation_agent, on_handoff=on_escalation, input_type=EscalationData)

triage = Agent(
    name="Triage",
    instructions="If the user is upset or blocked, call the escalation handoff with a reason.",
    handoffs=[escalation_handoff],
)

```

The model can now **provide a JSON object** that conforms to `EscalationData` when it invokes the handoff.

---

## 🧹 3. Controlling what history the new agent sees (input filters)

By default, the new agent sees **the entire prior conversation**. You can edit that input with an `input_filter`—for example, 🗑 **remove all tool calls** so the next agent sees a cleaner history:

```python
from agents import Agent, handoff
from agents.extensions import handoff_filters

faq_agent = Agent(name="FAQ agent", instructions="Answer concisely from known FAQs.")
faq_handoff = handoff(agent=faq_agent, input_filter=handoff_filters.remove_all_tools)

router = Agent(
    name="Router",
    instructions="If a FAQ matches, handoff to the FAQ agent.",
    handoffs=[faq_handoff],
)

```

🌐 There’s also a **global** `handoff_input_filter` you can set for the whole run via `RunConfig`.

---

## 🧪 Interactive Lab 2 — add a reason and sanitize history

1. 📝 Add `input_type=EscalationData` with a reason like “angry customer; shipment lost.”
2. 🧹 Apply `handoff_filters.remove_all_tools` and confirm the receiving agent doesn’t see tool noise.
3. 🕵 Print `result.last_agent` to verify who ended the turn; store it for your next user turn if you want to continue with the same agent.

> ✅ Checkpoint: You should see your on_handoff log fire, and the receiving agent respond based only on the cleaned conversation.
> 

---

## 🧠 4. Prompting best practices (make handoffs obvious)

📌 Include explicit handoff instructions in your prompts so the LLM **knows** when to transfer. 

🛠 The SDK ships a ready-made prompt prefix and a helper:

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

billing_agent = Agent(
    name="Billing agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
Use the billing policies below to resolve issues..."""
)

```

Alternatively, use `prompt_with_handoff_instructions(...)` to inject the recommended blurb automatically.

## 📝5. Continue the Conversation with the Same Specialist:

### 📃Pattern A — keep Triage in front, pass the whole thread forward:

Use `result.to_input_list()` (it bundles your original input + all items generated during the run) and then append the user’s next message. Run again with the **same entry agent** (e.g., Triage).

```python
# turn 1: user asks about a refund → Triage hands off to Refunds
result1 = await Runner.run(triage, "I was double charged. Can I get a refund?")
print("Reply:", result1.final_output)

# turn 2: user follows up → keep Triage as the entry, pass prior thread + new msg
followup_input = result1.to_input_list() + [
    {"role": "user", "content": "Thanks. Also, how long will it take?"}
]
result2 = await Runner.run(triage, followup_input)
print("Reply:", result2.final_output)

```

Why this works: the SDK explicitly supports turning a result into inputs for the next turn with `to_input_list()`, so you can keep all prior context intact. 

### 📃Pattern B — resume directly with the **same specialist:**

If your UI shows you’re already “with Refunds,” you can **start the next turn from that specialist** by reusing `result.last_agent` (the actual agent that produced the final reply). This avoids bouncing back to Triage unnecessarily.

```python
# turn 1: triage → refunds
result1 = await Runner.run(triage, "I was double charged. Can I get a refund?")
specialist = result1.last_agent            # ← who actually answered last time
# e.g., "Refunds agent"

# turn 2: continue with the same specialist
followup_input = result1.to_input_list() + [
    {"role": "user", "content": "Great. What info do you need from me?"}
]
result2 = await Runner.run(specialist, followup_input)  # start at Refunds
print("Reply:", result2.final_output)
```

Why this works: the SDK exposes `last_agent` *specifically* so you can carry the baton to the same specialist on the next user turn (super common after a handoff). 

> Quick tip: Both patterns rely on `to_input_list()` to maintain the entire prior conversation state before appending the new user message.
> 

---

## ⚙ Under the hood: runner loop (what actually happens)

The runner:

1. 🔄 Calls the current agent
2. 📦 If the model **returns a handoff**, it **switches the current agent** and re-runs the loop with the updated input
3. 🛠 If the model uses tools, it runs them, appends results, and loops again
4. ✅ Ends when a final output is produced (or `max_turns` is exceeded)

> Debugging tip: Inspect new_items to see a HandoffCallItem followed by HandoffOutputItem; that’s the tell-tale sign.
> 

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

## 📚 Step-by-step mini-lesson

1. **Build three agents**: `Triage`, `Billing`, `Refunds`. Add both specialists to `Triage.handoffs`.
2. **Run three queries**: billing-ish, refunds-ish, and random. Confirm only relevant ones hand off.
3. **Add `on_handoff`** to log transitions; simulate prefetch.
4. **Add `input_type`** to pass `EscalationData(reason=...)`.
5. **Apply `input_filter`** to remove tool noise.
6. **Use the prompt prefix** so the LLM routes confidently.
7. **Inspect `new_items`** for `Handoff*` entries; celebrate.

---

## Starter template you can copy

```python
from agents import Agent, Runner, handoff
from agents.extensions import handoff_filters
from pydantic import BaseModel

# Specialists
billing = Agent(name="Billing agent", instructions="Resolve billing issues.")
refunds = Agent(name="Refunds agent", instructions="Process and explain refunds.")

# Optional: typed input and on_handoff callback
class EscalationData(BaseModel):
    reason: str

def log_handoff(ctx, input_data: EscalationData | None = None):
    print("HANDOFF:", getattr(input_data, "reason", "<no reason>"))

# Customized handoff (rename tool, accept typed input, log on handoff)
to_refunds = handoff(
    agent=refunds,
    tool_name_override="transfer_to_refunds",
    tool_description_override="Send this to the refunds specialist.",
    on_handoff=log_handoff,
    input_type=EscalationData,
)

# Optional: sanitize history for the receiving agent
to_billing = handoff(agent=billing, input_filter=handoff_filters.remove_all_tools)

# Orchestrator / Triage
triage = Agent(
    name="Triage",
    instructions=("Decide whether the user needs Billing or Refunds. "
                  "If escalating, include a short reason."),
    handoffs=[to_billing, to_refunds],
)

# Run
# result = await Runner.run(triage, "I was double charged last month.")
# print(result.final_output)

```

This template pulls together: **handoff list**, **custom tool naming**, **typed inputs**, **input filters**, and a **triage** pattern.

---

## 🏁 Wrap-up

- **📌 What a handoff is:** a **control transfer** to another agent (exposed to the LLM as `transfer_to_<agent>`).
- **🎯 When to use it:** when a specialist should **own** the conversation from this point onward (e.g., refunds, billing).
- **🛠 How to do it:** list handoffs on the agent, optionally customize with `handoff(...)` (name, description, `on_handoff`, `input_type`, `input_filter`).
- **🔄 How it runs:** the loop **switches current agent** and continues until a final output.