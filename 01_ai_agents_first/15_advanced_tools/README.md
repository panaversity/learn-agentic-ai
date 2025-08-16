# Advanced Tools MasterClass

Welcome to the next level of tool calling. If basic tools are about giving your agent *abilities*, advanced tools are about giving you *control*. This guide will teach you how to manage your agent's workflow, handle errors gracefully, and build robust, real-world applications.

> **The Big Idea:** You are a manager, and your tools are your team. Advanced features are your management playbook for telling them *when* to work, *if* they can work, and *what to do* when they run into trouble.

### What We'll Master in This Step?

To give you a roadmap, here are the key questions we will answer. By the end of this guide, you'll be able to confidently control your agent's behavior in complex, real-world scenarios:

*   **Controlling Execution Flow:** How can I force my agent to stop after its first action (`stop_on_first_tool`), or only after a specific "finalizing" tool is used (`stop_tool_names`)?
*   **Preventing Runaway Agents:** What is the ultimate safety net (`max_turns`) to prevent agents from getting stuck in loops, and how does it interact with other settings?
*   **Creating Context-Aware Tools:** How do I make certain tools available *only* under specific conditions, like creating an "admin-only" tool using the dynamic `is_enabled` flag?
*   **Building Resilient Agents:** How can my agent handle tool failures gracefully so it can recover and try a different approach instead of crashing?
*   **Managing Stateful Tools:** For the rare cases where a tool needs to remember information between calls, how do we build one using a class (`FunctionTool`), and why is this advanced pattern used sparingly?

## 🤔 Why Do We Need Advanced Tools MasterClass?

Without advanced controls, agents can get stuck in loops, crash on a simple error, or try to use tools they shouldn't have access to. This costs time and money.

Advanced tools solve these critical problems:
*   **Control:** Stop your agent from running forever or calling tools unnecessarily.
*   **Context:** Enable or disable tools based on the user's permissions or the situation.
*   **Resilience:** Handle failures without crashing the entire process.
*   **Precision:** Build sophisticated, multi-step workflows that execute predictably.

---

## Part 1: Controlling the Flow – How to Stop Your Agent

Your first job as a manager is to prevent your team from working endlessly. These controls stop your agent at the right moment.

### The "One and Done" Rule: `stop_on_first_tool`

This tells your agent to stop immediately after it successfully uses **any** tool. It's perfect for simple, single-action tasks.

*   **Use Case:** An agent whose only job is to send an email. Once the email is sent, its work is done.

```python
agent = Agent(
    name="Email Sender",
    instructions="Send an email and then stop.",
    tools=[send_email],
    tool_use_behavior="stop_on_first_tool", # Formerly stop_at_first_tool
)
```

### The "Final Action" Rule: `stop_tool_names`

This tells the agent to stop only after using a *specific* tool. This is essential for workflows that have a clear finishing move.

*   **Use Case:** A research agent that first searches for information (`web_search`) and then saves the result (`save_to_file`). You want it to stop only after it saves.

```python
agent = Agent(
    name="Researcher",
    tools=[web_search, save_to_file],
    stop_tool_names=["save_to_file"], # Stop after this tool is called
)
```

### The "Hard Limit" Rule: `Runner.max_turns`

This is your ultimate safety net. It sets the maximum number of back-and-forth cycles (LLM calls) the agent can perform. It prevents infinite loops and contains costs.

*   **Use Case:** A complex research task where you want to allow up to 5 web searches before stopping, no matter what.

```python
result = await Runner.run(agent, "Find articles about AI agents. You can think and act a maximum of 5 times.", max_turns=6)
```

> **🧠 Think About It:** What happens if `max_turns` is 1 and the agent needs to call a tool (search)? The runner will stop it after the first tool call, before taking tool response to llm. Always set `max_turns` high enough for the expected workflow.

---

## Part 2: Context is King – Making Tools Appear & Disappear

A good manager doesn't give every tool to every team member. The `is_enabled` flag lets you make tools available only when the conditions are right.

### The Static On/Off Switch

The simplest way is with a `True`/`False` value. This is great for turning off a tool for maintenance.

```python
@function_tool(is_enabled=False)
def under_maintenance_tool():
    """This tool is temporarily disabled."""
    return "Sorry, this feature is offline for maintenance."
```

### The Dynamic On/Off Switch (with a function)

This is where it gets powerful. You can pass a function to `is_enabled` that checks the current context. The tool will only be available if the function returns `True`.

*   **Use Case:** An "admin" tool that should only be visible to users with admin privileges.

```python
# This function checks the context provided during the run.
def is_user_admin(context: RunContextWrapper, agent: Agent) -> bool:
    return context.get("user_role") == "admin"

@function_tool(is_enabled=is_user_admin)
def delete_user_database():
    """[ADMIN ONLY] Deletes the entire user database."""
    # ... dangerous logic here ...
    return "Database has been deleted."
```

---

## Part 3: When Things Go Wrong – Graceful Error Handling

Tools can fail—APIs go down, files are missing, math is impossible. A resilient agent doesn't crash; it handles the error.

### The Easy Way: `try/except` in the Tool

For most cases, a simple `try/except` block inside your tool is enough. You catch the error and return a helpful message to the agent, so it knows what went wrong and can try something else.

```python
@function_tool
def divide(a: int, b: int) -> str:
    """Divides two numbers."""
    try:
        result = a / b
        return str(result)
    except ZeroDivisionError:
        return "Error: You cannot divide by zero. Please ask the user for a different number."
```

### The Advanced Way: Custom Error Functions

For more complex scenarios, like custom logging or routing, you can provide a `failure_error_function`. This is less common but offers maximum control.

---

## Part 4: The Specialist – Stateful Tools (Use with Caution)

Sometimes you need a tool that *remembers* things between calls. While the `@function_tool` decorator is best for 99% of cases, you can build a tool from a class to manage internal state.

*   **Use Case:** A counter tool that increments a number each time it's called.

> **⚠️ Recommendation:** This pattern is complex and can make your agent's behavior harder to predict. Always prefer a simple `@function_tool` if possible.

```python
from agents import FunctionTool

class CounterTool(FunctionTool):
    name = "incrementing_counter"
    description = "Counts up by one each time it is called."
    # No parameters needed for this simple case.
    params_json_schema = {"type": "object", "properties": {}}

    def __init__(self):
        super().__init__()
        self._count = 0

    async def on_invoke_tool(self, context, args_json_str) -> str:
        self._count += 1
        return f"The current count is: {self._count}"

# You would then add an instance of this class to your agent's tool list.
# agent_tools = [CounterTool()]
```

---

## Your Turn: A Mini-Lab

Let's put it all together. Here is a starter template. Your task is to modify it based on the comments.

```python
from agents import Agent, Runner, function_tool, RunContextWrapper
import asyncio

# A tool that can sometimes fail.
@function_tool
def get_user_data(user_id: str) -> str:
    """Looks up user data. Fails if the user ID is 'error'."""
    try:
        if user_id == "error":
            raise ConnectionError("Could not connect to the database.")
        return f"Data for {user_id}: Name - Alex, Role - user"
    except ConnectionError as e:
        return f"Error: {e}. I cannot proceed."

# TODO 1: Make this an admin-only tool.
# Add an `is_enabled` check that looks for `context.get("role") == "admin"`.
@function_tool
def delete_user(user_id: str) -> str:
    """Deletes a user. This is a final action."""
    return f"User {user_id} has been deleted."

admin_agent = Agent(
    name="Admin Agent",
    instructions="Help manage users. First get data, then delete if asked.",
    tools=[get_user_data, delete_user],
    # TODO 2: Make the agent stop after a user is deleted.
    # Add the correct `stop_tool_names` configuration here.
)

async def main():
    print("--- Running as a regular user ---")
    # This run should fail because the delete_user tool is not enabled.
    result_user = await Runner.run(
        admin_agent,
        "Please delete user client_456.",
        # The context provides the user's role.
        context={"role": "user"}
    )
    print(result_user.final_output)

    print("\n--- Running as an admin ---")
    # TODO 3: Set max_turns to 3 for this run as a safety limit.
    result_admin = await Runner.run(
        admin_agent,
        "Get data for user_123 and then delete them.",
        context={"role": "admin"}
    )
    print(result_admin.final_output)

# asyncio.run(main())
```

---

## 🏁 Wrap-Up

*   **What it is:** A set of controls to make your agent's tool use precise, safe, and context-aware.
*   **When to use it:** For any real-world application where you need reliability and control over costs and actions.
*   **How to do it:** Start with `stop` rules and `max_turns`. Add `is_enabled` for context and `try/except` for resilience. Use the `FunctionTool` class only when absolutely necessary.