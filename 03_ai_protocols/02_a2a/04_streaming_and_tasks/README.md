# Step 4: [Streaming & Tasks](https://a2a-protocol.org/latest/topics/streaming-and-async/)

**What We'll Actually Build**: Real A2A streaming agents with Server-Sent Events (SSE), task management - following the official A2A specification. The Push Notifications for async tasks will be covered in step 06_push_notifications.

## 🎯 What You'll Learn by Building

We'll build **3 progressively complex agents** to understand A2A streaming:

1. **Basic Streaming Agent**: SSE with `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent`

**Learning Method**: Build, run, test - just like Step 3!

## 🔍 Understanding A2A Streaming with Real Examples

### What is Server-Sent Events (SSE) in A2A?

When you use `message/stream`, the A2A server opens a persistent HTTP connection and streams events in real-time.

**Key A2A Event Types:**

- **`Task`**: Initial task creation with `id` and `contextId`
- **`TaskStatusUpdateEvent`**: Progress updates ("working", "completed", etc.)
- **`TaskArtifactUpdateEvent`**: Actual results/files being streamed
- **`final: true`**: Signals end of this interaction stream

## 🛠️ Build: Basic Streaming Agent

Let's start with a simple agent that demonstrates real A2A streaming:

### Create `basic_streaming_agent.py`

```python
import asyncio
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.types import AgentCard, AgentCapabilities, Part, TextPart, TaskState

class BasicStreamingExecutor(AgentExecutor):
    """Demonstrates A2A streaming with TaskStatusUpdateEvent and TaskArtifactUpdateEvent."""

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Step 1: Set up TaskUpdater for streaming
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        # Step 2: Start the task (creates initial Task event)
        if not context.current_task:
            await updater.submit()  # Streams: {"kind": "task", "id": "task-123"}
        await updater.start_work()  # Changes state to "working"

        user_input = context.get_user_input()
        print(f"🎯 Processing: {user_input}")

        # Step 3: Stream progress updates (TaskStatusUpdateEvent)
        progress_steps = [
            "🚀 Initializing...",
            "📊 Processing your request...",
            "🔍 Analyzing data...",
            "📝 Generating response..."
        ]

        for i, step in enumerate(progress_steps):
            # This streams a TaskStatusUpdateEvent
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"{step} ({i+1}/{len(progress_steps)})"))
                ])
            )
            await asyncio.sleep(1)  # Simulate work

        # Step 4: Create and stream the final result (TaskArtifactUpdateEvent)
        result_text = f"✅ Completed processing: '{user_input}'\n\nProcessed at: {asyncio.get_event_loop().time()}"

        await updater.add_artifact(
            [Part(root=TextPart(text=result_text))],
            name="processing_result"
        )

        # Step 5: Complete the task (final TaskStatusUpdateEvent with final=true)
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(
            TaskState.canceled,
            message=updater.new_agent_message([
                Part(root=TextPart(text="❌ Task was cancelled"))
            ])
        )

# Agent Card with streaming enabled
agent_card = AgentCard(
    name="Basic Streaming Agent",
    description="Demonstrates A2A streaming with real-time updates",
    url="http://localhost:8001/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,  # REQUIRED for A2A streaming
        push_notifications=False,
        state_transition_history=False
    ),
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)

if __name__ == "__main__":
    # Create the A2A server with streaming support
    request_handler = DefaultRequestHandler(
        agent_executor=BasicStreamingExecutor(),
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )

    server = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    print("🚀 Starting Basic Streaming Agent on port 8001...")
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8001")

    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8001)
```

### Test the Streaming Agent with Python Httpx Client

Create `test_basic_streaming.py` for raw python client:

```python
import asyncio
import httpx
import json

async def test_basic_streaming():
    """Test the basic streaming agent with real SSE."""

    print("🧪 Testing Basic A2A Streaming Agent\n")

    async with httpx.AsyncClient() as client:
        # Send streaming request using async context manager
        async with client.stream(
            "POST",
            "http://localhost:8001",
            json={
                "jsonrpc": "2.0",
                "method": "message/stream",  # Use streaming method
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": "Process my data"}],
                        "messageId": "test-msg-1",
                        "kind": "message"
                    }
                },
                "id": "stream-test-1"
            },
            headers={"Accept": "text/event-stream"}
        ) as response:
            
            print("📥 Streaming events:")
            async for chunk in response.aiter_text():
                if chunk.startswith("data: "):
                    try:
                        event_data = json.loads(chunk[6:])  # Remove "data: " prefix
                        result = event_data.get("result", {})
                        kind = result.get("kind")

                        if kind == "task":
                            task_id = result.get("id")
                            context_id = result.get("contextId")
                            print(f"📋 Task Created: {task_id[:8]}... (context: {context_id[:8]}...)")

                        elif kind == "status-update":
                            status = result.get("status", {})
                            state = status.get("state")
                            message = status.get("message", {})

                            if message.get("parts"):
                                text = message["parts"][0].get("text", "")
                                print(f"📊 Status [{state}]: {text}")

                            if result.get("final"):
                                print(f"🏁 Stream ended (final status: {state})")
                                break

                        elif kind == "artifact-update":
                            artifact = result.get("artifact", {})
                            name = artifact.get("name")
                            last_chunk = result.get("lastChunk", False)

                            if artifact.get("parts"):
                                content = artifact["parts"][0].get("text", "")
                                preview = content[:100] + "..." if len(content) > 100 else content
                                print(f"📄 Artifact '{name}': {preview}")
                                if last_chunk:
                                    print(f"✅ Artifact '{name}' completed")

                    except json.JSONDecodeError:
                        continue

    print("\n🎯 Test completed! The agent streamed real A2A events.")

if __name__ == "__main__":
    asyncio.run(test_basic_streaming())
```

### Test Streaming Agent with A2A Client:

```python
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig, Client
from a2a.types import Message, TextPart

async def main():
    # Discover your calendar agent
    try:
        async with httpx.AsyncClient() as httpx_client:
            
            resolver = A2ACardResolver(base_url="http://localhost:8001", httpx_client=httpx_client)
            agent_card = await resolver.get_agent_card()
            print(f"Found agent: {agent_card}")

            # Create A2A client with discovered agent cards
            client: Client = ClientFactory(config=ClientConfig(httpx_client=httpx_client, streaming=True)).create(card=agent_card)

            # Create message with proper structure
            message = Message(
                role="user",
                message_id="123",
                parts=[TextPart(text="Schedule a team meeting for tomorrow at 2 PM")]
            )

            response = client.send_message(message)
            async for chunk in response:
                print("\n[CHUNK]", chunk)

    except Exception as e:
        print(f"Error fetching agent cards: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Run and Observe

1. **Start the agent**: `python basic_streaming_agent.py`
2. **In another terminal**: `python test_basic_streaming.py`
3. **Watch the real-time events stream!**

You'll see:

```
📋 Task Created: 1a2b3c4d... (context: 5e6f7g8h...)
📊 Status [working]: 🚀 Initializing... (1/4)
📊 Status [working]: 📊 Processing your request... (2/4)
📊 Status [working]: 🔍 Analyzing data... (3/4)
📊 Status [working]: 📝 Generating response... (4/4)
📄 Artifact 'processing_result': ✅ Completed processing: 'Process my data'...
✅ Artifact 'processing_result' completed
🏁 Stream ended (final status: completed)
```

**🎯 Key Learning**: This is **real A2A streaming** - each progress update is sent immediately as a separate SSE event!

## 📚 A2A SDK Components You have Learned

### AgentExecutor Pattern

```python
class MyAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Your agent logic here - SDK handles all A2A protocol details

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        # Handle task cancellation
```

### TaskUpdater for State Management

```python
updater = TaskUpdater(event_queue, context.task_id, context.context_id)

await updater.submit()      # Task created (submitted state)
await updater.start_work()  # Begin processing (working state)

# Send progress updates
await updater.update_status(TaskState.working, message=progress_message)

# Create outputs
await updater.add_artifact(content, name="My Report")

await updater.complete()    # Finish successfully (completed state)
```

### A2A Task States (Managed Automatically)

- **`submitted`**: Task created, waiting to start
- **`working`**: Agent actively processing
- **`completed`**: Successfully finished
- **`failed`**: Error occurred
- **`canceled`**: User stopped the task

## 🏗️ A2A SDK Architecture

The A2A SDK provides these key components:

- **`A2AFastAPIApplication`**: Ready-to-use FastAPI server with A2A compliance
- **`AgentExecutor`**: Base class for your agent logic with streaming support
- **`TaskUpdater`**: Manages task state transitions and progress updates automatically
- **`EventQueue`**: Handles real-time event streaming to clients
- **`RequestContext`**: Provides access to user input and task context

## � A2A Task States (From Specification)

The A2A spec defines these exact task states:

- **`submitted`**: Task created, waiting to start
- **`working`**: Agent actively processing
- **`input-required`**: Waiting for user input
- **`completed`**: Successfully finished
- **`failed`**: Error occurred
- **`canceled`**: User stopped the task
- **`rejected`**: Agent refused the task
- **`auth-required`**: Need authentication

### ✅ A2A SDK Benefits

- **No Protocol Implementation**: SDK handles SSE, JSON-RPC, task states automatically
- **Focus on Logic**: You only implement `execute()` and `cancel()` methods
- **Production Ready**: Built-in error handling, persistence, scaling support
- **Developer Friendly**: Clear patterns and abstractions

### 🚫 Common Mistakes to Avoid

- ❌ Trying to manually implement streaming (use SDK instead)
- ❌ Forgetting to call `submit()` and `start_work()`
- ❌ Not sending progress updates for long operations
- ❌ Missing the `cancel()` method implementation

### 🏗️ Best Practices

- ✅ Use meaningful progress messages that inform users
- ✅ Break long operations into steps with updates
- ✅ Handle exceptions gracefully with appropriate task states
- ✅ Test both quick queries and long operations
- ✅ Always implement cancellation support

**💡 Remember**: The A2A SDK handles all the complex protocol details - you focus on building great agent experiences!