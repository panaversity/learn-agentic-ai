# Human In The Loop - Multi-Turn Interactions with Input Required 🤝

**Build a simple agent that can pause and ask the user for more info during a task. This uses A2A rules to handle talks that go back and forth, like clarifying details in a conversation.**

> **🎯 Learning Goal**: Learn how to make agents handle multi-turn chats in A2A. This includes pausing for user input, restarting tasks, and keeping track of state so humans and agents can work together smoothly. Handle clarification requests, resume interrupted tasks, and manage state across interactions for collaborative agent-human systems.

## 🧠 Why This Matters for Learning

### **How Protocols Work Together**
- **Task Life Cycle**: Know the full path of a task – from start to pause (like needing input) to end (done or failed).
- **Back-and-Forth Patterns**: Create chats where agents stop for human help and pick up again using IDs for context and tasks.
- **Human-Agent Teamwork**: Add human checks into agent work to fix unclear parts, making things more reliable.

### **Keeping It Easy to Understand**
- **Chats with Memory**: Use contextId to link related tasks, so you don't repeat info.
- **Asking for Help**: Use "input-needed" state to break down confusing questions, making chats feel natural.
- **Easy Restart**: Clients reply with the same taskId, which keeps things simple without complex saving.

## 🚀 How to Build Human In The Loop

This is a full, standalone example. It shows the full task life cycle in A2A: A task starts when a message comes in. The agent can reply with a simple message or a task. Tasks have states like working, needing input, done, or failed. Use contextId to group chats and taskId to continue a specific task.

### Task Life Cycle Explained Simply
1. **Client Sends Message**: Using "message/send" with user input.
2. **Agent Decides**:
   - Simple reply: Just a message (no long work).
   - Complex work: Make a task with taskId and contextId.
3. **Task States**:
   - **Working**: Agent is doing the job.
   - **Input-Needed**: Pause and ask user for more info (e.g., if details are missing).
   - **Done**: Task finishes successfully.
   - **Failed/Canceled**: Something went wrong or stopped.
4. **Continuing**:
   - Client sends again with same contextId and taskId to add input.
   - Agent restarts the task from where it paused.
5. **Follow-Ups**: For new related asks, use same contextId but new taskId. Reference old tasks if needed.
6. **End**: Once done or failed, task can't restart – make a new one for changes.

This example uses a Currency Agent. User asks for an exchange rate. If currencies are missing, agent pauses and asks. User replies, agent finishes.

### Key Files
1. **currency_agent.py**: Defines the Currency Agent responsible for fetching exchange rates. It includes logic to check for required details (e.g., source and target currencies) and emit input-required if incomplete.
2. **agent_executor.py**: Custom AgentExecutor that bridges A2A to OpenAI Agents SDK. It handles task persistence, checks for user input completeness, and uses TaskUpdater to set states like input-required or completed.
3. **server.py**: The main A2A FastAPI server using DefaultRequestHandler and InMemoryTaskStore for task persistence. It mounts the agent endpoint and supports streaming updates.
4. **client.py**: A simple client script to simulate interactions: initial query, receiving input-required, and sending follow-up with same taskId/contextId.
5. **conversations.db**: SQLite database for persisting agent sessions across turns (managed by SQLiteSession).

### How to Demo
- User asks: "What's the exchange rate?" (no details).
- Agent makes task, sets to input-needed: "Which currencies? Like USD to EUR."
- User replies with same IDs: "USD to EUR."
- Agent continues, gets rate, adds result as artifact, sets to done.

### Setup and Running:
1. Install dependencies: `uv sync` (includes a2a-sdk[http-server], openai-agents, etc.).
2. Run the server: `uv run server.py` (exposes endpoint at http://localhost:8001).
3. Simulate client interactions: `uv run client.py --query "What's the exchange rate?"` (observe input-required), then follow up with `--task-id <taskId> --context-id <contextId> --input "USD to EUR"`.
4. Monitor logs and responses to see the task state transitions and artifact updates.

### Code Highlights:
In `agent_executor.py`, add logic for input-required:

```python
async def execute(self, context: RequestContext, event_queue: EventQueue):
    updater = TaskUpdater(event_queue, context.task_id, context.context_id)
    await updater.start_work()
    
    user_input = context.get_user_input()
    if not self.has_required_details(user_input):  # Custom check for ambiguity
        await updater.update_status(
            TaskState.input_required,
            message=updater.new_agent_message([
                Part(root=TextPart(text="Between which currencies? (e.g., USD to EUR)"))
            ])
        )
        return  # Pause task
    
    # Proceed if input is complete (or after resumption)
    result = await Runner.run(self.agent, user_input, session=self.memory_session)
    await updater.add_artifact([Part(root=TextPart(text=result.final_output))], name="exchange_rate")
    await updater.complete()
```

In `client.py`, handle resumption:

```python
# Pseudocode for follow-up
response = send_message(
    message="USD to EUR",
    context_id=previous_context_id,
    task_id=previous_task_id
)
```

This setup allows the agent to dynamically involve humans, bridging autonomous execution with supervised clarification.

---

## 📖 Key Takeaway

**Remember**: Human-in-the-loop isn't just a fallback—it's the bridge to trustworthy AI, where agents and users collaborate to turn ambiguity into precision! 🤝

### Concepts Demonstrated:
- **Task Lifecycle**: Tasks start in working state, can interrupt to input-required for human input, and resume to completion without creating new tasks.
- **State Persistence**: Using InMemoryTaskStore (or SQLite) to maintain task state across turns, ensuring immutability once terminal.
- **Human-In-The-Loop**: Agent pauses execution to involve the user, enabling clarification without failure.
- **Refinements & Follow-Ups**: Optional referenceTaskIds for linking new tasks to prior ones in the same contextId, supporting parallel or sequential workflows.

### Ideas Shown
- Task path: Start → Pause for input → Continue → Finish.
- Saving state: Keep tasks so they can restart.
- Human help: Agent stops to ask user, avoids errors.
- Extra chats: Link new tasks with contextId for follow-ups.

### **Resources to Learn More**
- [A2A Rules: Task Life](https://a2a-protocol.org/latest/topics/life-of-a-task/)
- [A2A Multi-Turn (Input Needed)](https://a2a-protocol.org/latest/specification/#94-multi-turn-interaction-input-required)
- [A2A Kit Docs](https://a2a-protocol.org/latest/sdk/)


