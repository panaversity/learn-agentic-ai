# Step 7: [Multi-Turn Interactions](https://a2a-protocol.org/latest/specification/#94-multi-turn-interaction-input-required)

In Step 4, you learned streaming for individual tasks. But real conversations need:

- **Memory**: "Remember what I said about the red sailboat"
- **Context**: "Make it bigger" (referring to previous task result)
- **Clarification**: "What style do you prefer?" (agent asking follow-up questions)

**Solution**: A2A agents that maintain conversation context across multiple interactions using `contextId` and `referenceTaskIds`. 

## 🔍 Understanding A2A Multi-Turn Flow

```
1. User: "Generate image of sailboat" 
   → Task 1 (contextId: "conv-123")
2. User: "Make the sailboat red" 
   → Task 2 (contextId: "conv-123", referenceTaskIds: ["task-1"])
3. Agent: "What shade of red?" 
   → Task 2 enters input-required state
4. User: "Bright red" 
   → Task 2 continues with user input
5. User: "Add clouds too"
   → Task 3 (contextId: "conv-123", referenceTaskIds: ["task-1", "task-2"])
```

## How It Works (Mental Model First)
1. JSON-RPC message/stream

    - Client sends method: "message/stream" with a user message, optional contextId, optional referenceTaskIds, and (for a continuation) an existing taskId.
    - Response is an HTTP streaming (SSE-style) stream: each line starting with data:  is a JSON envelope containing a single incremental result.

2. Events emitted by the server (via TaskUpdater)

    - status-update (TaskStatusUpdateEvent): interim progress (final=False).
    - artifact-update (TaskArtifactUpdateEvent): output chunks (lastChunk=True on final chunk).
    - Final status-update with state=completed and final=True ends the stream.

3. Task + context persistence

    - InMemoryTaskStore keeps tasks so they can be continued or queried.
    - contextId groups a conversational thread (logical conversation).
    - referenceTaskIds explicitly say “use outputs of these previous tasks.”

4. Multi‑turn clarification

    - Agent cannot proceed? Emit status with state=input_required, final=True.
    - Client sends another message/stream reusing the same contextId and the taskId with added user input.
    - Execution resumes; final completion state ends that turn’s stream.

5. Minimal memory pattern here

    - We don’t persist a full conversation DB
    — just show how to emit streaming updates and (optionally) ask for clarification.

6. Client responsibilities

    - Read each data: line, parse JSON.
    - Capture the task object’s id when it appears.
    - Stop reading when a status-update has final=True.
    - For clarifications: send follow-up including same taskId & contextId.

That’s all you truly need. Everything else is layering and polish.


## 🛠️ Build

1. Setup
```bash
uv init hello_interactions
cd hello_interactions
uv add "a2a-sdk[http-server]" openai-agents
```

2. Agent and A2A server setup

Review main.py code. It's the same agent we just shared context_id from client to OpenAI Agent Sessions.

3. Client

When making request we just context_id in message.


## The Three Core Ideas (Condensed)
1. Task State Management

    - DefaultRequestHandler + InMemoryTaskStore = persisted task lifecycle.
    - First turn: new task; continuation: existing task passed in RequestContext.

2. Streaming Mechanics
    - Use TaskUpdater.submit(), start_work(), update_status(), add_artifact(), complete().
    - Client sees a sequence: task intro (kind task) → multiple status/artifact updates → final status (final=True).

3. Multi‑Turn via input_required

    - Emit a status with TaskState.input_required when you need user info.
    - Client replays with same taskId (continuation) plus clarifying input.