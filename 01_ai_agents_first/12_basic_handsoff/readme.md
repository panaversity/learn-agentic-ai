# Handoff

https://openai.github.io/openai-agents-python/handoffs/

In the OpenAI Agents SDK, **handoffs** enable an agent to delegate tasks to another agent, facilitating specialized handling of different tasks within a multi-agent system. This mechanism is particularly useful when different agents possess expertise in distinct domains. citeturn0search2

**Table of Contents:**

1. [Understanding Handoffs](#understanding-handoffs)
2. [Creating Agents](#creating-agents)
3. [Implementing Handoffs](#implementing-handoffs)
4. [Running the Agent Orchestration](#running-the-agent-orchestration)
5. [Advanced Handoff Customization](#advanced-handoff-customization)
6. [Conclusion](#conclusion)

---

## 1. Understanding Handoffs

Handoffs allow an agent to delegate tasks to another agent. This is particularly useful in scenarios where different agents specialize in distinct areas. For example, a customer support application might have agents that each specifically handle tasks like order status, refunds, or frequently asked questions.



## 2. Creating Agents

Define agents with specific roles and instructions.

**Example:**


```python
from agents import Agent

# Agent specializing in billing inquiries
billing_agent = Agent(
    name="Billing Agent",
    instructions="You handle all billing-related inquiries. Provide clear and concise information regarding billing issues."
)

# Agent specializing in refund processes
refund_agent = Agent(
    name="Refund Agent",
    instructions="You handle all refund-related processes. Assist users in processing refunds efficiently."
)
```


## 3. Implementing Handoffs

To enable an agent to delegate tasks to another agent, define handoffs during the agent's creation.

**Example:**


```python
from agents import Agent

# Triage agent that decides which specialist agent to hand off tasks to
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent should handle the user's request based on the nature of the inquiry.",
    handoffs=[billing_agent, refund_agent]
)
```


In this setup, the `triage_agent` can delegate tasks to either the `billing_agent` or the `refund_agent` based on the user's request.

## 4. Running the Agent Orchestration

Use the `Runner` to execute the agent workflow.

**Example:**


```python
from agents import Runner

async def main():
    user_input = "I need a refund for my recent purchase."
    result = await Runner.run(triage_agent, user_input)
    print(result.final_output)

# Execute the main function
import asyncio
asyncio.run(main())
```


In this example, the `triage_agent` assesses the user's input and delegates the task to the appropriate specialist agent.

Note:

Triage AI agents are artificial intelligence systems designed to assess, categorize, and prioritize tasks, ensuring that the most critical issues receive immediate attention. By automating the initial evaluation process, these agents enhance efficiency and accuracy across various sectors.
How to pronounce:

https://www.google.com/search?q=pronounce+triage

## 5. Advanced Handoff Customization

For more control over handoffs, utilize the `handoff()` function to customize behavior.

**Example:**


```python
from agents import Agent, handoff

# Define the refund agent
refund_agent = Agent(
    name="Refund Agent",
    instructions="You handle all refund-related processes."
)

# Customize the handoff to the refund agent
custom_handoff = handoff(
    agent=refund_agent,
    tool_name_override="custom_refund_handoff",
    tool_description_override="Handles refund processes with customized parameters."
)

# Triage agent with customized handoff
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent should handle the user's request.",
    handoffs=[custom_handoff]
)
```


In this scenario, the `triage_agent` uses a customized handoff to the `refund_agent`, allowing for specific configurations during the delegation process.

## 6. Conclusion

Implementing handoffs in the OpenAI Agents SDK enhances the modularity and specialization of your AI agents, enabling them to delegate tasks efficiently. By following this tutorial, you can create a multi-agent system where each agent operates within its domain expertise, leading to more efficient and effective task management.

For more detailed information, refer to the [OpenAI Agents SDK Handoffs Documentation](https://openai.github.io/openai-agents-python/handoffs/). 