# Step 06: Message Streaming 🌊

**Real-time streaming with A2A protocol - Official patterns from LangGraph sample**

> **Goal**: Implement A2A message streaming using official patterns from [a2a-samples/langgraph](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/langgraph) with TaskUpdater and proper event handling.

## 🎯 What You'll Learn

- Official A2A streaming patterns from [LangGraph sample](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/langgraph)
- TaskUpdater for streaming status updates
- Server-Sent Events (SSE) with A2A protocol
- Task state management (working → completed)
- Artifact updates and status events
- Real-time agent feedback patterns

## 📋 Prerequisites

- Completed [Step 05: Hello A2A](../05_hello_a2a/)
- Understanding of A2A Agent Executor pattern
- UV package manager installed
- Basic understanding of streaming concepts

## 🚀 Implementation

### 1. Create UV Project

```bash
cd 06_message_streaming
uv init a2a06_code
cd a2a06_code
uv add a2a-sdk uvicorn httpx
```

### 2. Streaming Agent Implementation

**File**: `streaming_agent.py`

```python
import asyncio
import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Part, TextPart, TaskState
from a2a.utils import new_agent_text_message, new_task

logger = logging.getLogger(__name__)


class StreamingAgent:
    """Agent that demonstrates streaming responses following official patterns."""

    async def stream(self, query: str, context_id: str):
        """Generate streaming response with status updates."""

        # Simulate streaming with different types of updates
        steps = [
            {"content": "Starting to process your request...", "is_task_complete": False, "require_user_input": False},
            {"content": "Analyzing your query...", "is_task_complete": False, "require_user_input": False},
            {"content": "Generating response...", "is_task_complete": False, "require_user_input": False},
            {"content": f"Your query '{query}' has been processed successfully!", "is_task_complete": True, "require_user_input": False},
        ]

        for step in steps:
            yield step
            await asyncio.sleep(1.0)  # Simulate processing time


class StreamingAgentExecutor(AgentExecutor):
    """Agent Executor implementing official streaming patterns."""

    def __init__(self):
        self.agent = StreamingAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute agent with streaming following official LangGraph pattern."""

        # Get user input
        query = context.get_user_input()
        task = context.current_task

        # Create new task if needed
        if not task:
            task = new_task(context.message)  # type: ignore
            await event_queue.enqueue_event(task)

        # Create TaskUpdater for streaming
        updater = TaskUpdater(event_queue, task.id, task.contextId)

        try:
            # Stream responses using official pattern
            async for item in self.agent.stream(query, task.contextId):
                is_task_complete = item['is_task_complete']
                require_user_input = item['require_user_input']

                if not is_task_complete and not require_user_input:
                    # Send status update while working
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            item['content'],
                            task.contextId,
                            task.id,
                        ),
                    )

                elif require_user_input:
                    # Request input from user
                    await updater.update_status(
                        TaskState.input_required,
                        new_agent_text_message(
                            item['content'],
                            task.contextId,
                            task.id,
                        ),
                        final=True,
                    )
                    break

                else:
                    # Task complete - add final artifact
                    await updater.add_artifact(
                        [Part(root=TextPart(text=item['content']))],
                        name='streaming_result',
                    )
                    await updater.complete()
                    break

        except Exception as e:
            logger.error(f'An error occurred while streaming: {e}')
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    f"Error occurred: {str(e)}",
                    task.contextId,
                    task.id,
                ),
                final=True,
            )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel streaming operation."""
        task = context.current_task
        if task:
            updater = TaskUpdater(event_queue, task.id, task.contextId)
            await updater.update_status(
                TaskState.cancelled,
                new_agent_text_message(
                    "Streaming operation cancelled",
                    task.contextId,
                    task.id,
                ),
                final=True,
            )
```

### 3. Streaming Server

**File**: `__main__.py`

```python
import httpx
import uvicorn
import logging

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, InMemoryPushNotifier
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from streaming_agent import StreamingAgentExecutor

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # Define streaming skill
    streaming_skill = AgentSkill(
        id='streaming_response',
        name='Streaming Response Generator',
        description='Generates real-time streaming responses with status updates',
        tags=['streaming', 'real-time', 'status-updates'],
        examples=['Process my request', 'Stream me a response'],
    )

    # Create agent card with streaming capabilities
    agent_card = AgentCard(
        name='Streaming Demo Agent',
        description='Demonstrates official A2A streaming patterns with TaskUpdater',
        url='http://localhost:10000/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(
            streaming=True,  # Enable streaming capability
            pushNotifications=False,
            stateTransitionHistory=True,
        ),
        skills=[streaming_skill],
    )

    # Setup A2A server with streaming support
    httpx_client = httpx.AsyncClient()
    request_handler = DefaultRequestHandler(
        agent_executor=StreamingAgentExecutor(),
        task_store=InMemoryTaskStore(),
        push_notifier=InMemoryPushNotifier(httpx_client),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    print("🌊 Starting Streaming Demo Agent...")
    print("📡 Streaming capability enabled!")
    print("📋 Agent Discovery: http://localhost:10000/.well-known/agent-card.json")
    print("💬 A2A Endpoint: http://localhost:10000/")
    uvicorn.run(server.build(), host='0.0.0.0', port=10000)
```

### 4. Streaming Test Client

**File**: `test_client.py`

```python
import logging
import asyncio
from typing import Any
from uuid import uuid4
import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)


async def test_streaming() -> None:
    """Test streaming message communication with official patterns."""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = 'http://localhost:10000'

    async with httpx.AsyncClient() as httpx_client:
        # Discover agent capabilities
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        logger.info(f'Discovering streaming agent at: {base_url}')
        agent_card: AgentCard = await resolver.get_agent_card()

        # Verify streaming capability
        if agent_card.capabilities and agent_card.capabilities.streaming:
            logger.info("✅ Agent supports streaming!")
        else:
            logger.warning("⚠️ Agent does not support streaming")

        # Create client
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card
        )

        # Test streaming message
        message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'Please stream a response with status updates!'}
                ],
                'messageId': uuid4().hex,
            },
        }

        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**message_payload)
        )

        print("\n🌊 Starting streaming communication...")
        print("📡 Receiving streaming response chunks:")
        print("-" * 60)

        # Process streaming response
        stream_response = client.send_message_streaming(streaming_request)

        chunk_count = 0
        async for chunk in stream_response:
            chunk_count += 1
            result = chunk.result

            # Parse different types of streaming events
            if hasattr(result, 'kind'):
                if result.kind == 'task':
                    print(f"📦 Chunk {chunk_count} [TASK]: {result.status.state}")
                elif result.kind == 'status-update':
                    status_msg = result.status.message.parts[0].text if result.status.message else "Status update"
                    final = "FINAL" if result.final else "INTERIM"
                    print(f"🔄 Chunk {chunk_count} [STATUS-{final}]: {status_msg}")
                elif result.kind == 'artifact-update':
                    artifact_text = result.artifact.parts[0].text
                    print(f"🎯 Chunk {chunk_count} [ARTIFACT]: {artifact_text}")
            else:
                print(f"📡 Chunk {chunk_count}: {chunk.model_dump(mode='json', exclude_none=True)}")

            await asyncio.sleep(0.1)  # Small delay for readability

        print("-" * 60)
        print(f"✅ Streaming complete! Received {chunk_count} chunks")


async def test_non_streaming_comparison() -> None:
    """Compare with non-streaming for demonstration."""

    print("\n🔄 Testing non-streaming for comparison...")

    base_url = 'http://localhost:10000'

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

        # Send non-streaming message
        message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [{'kind': 'text', 'text': 'Send me a regular response'}],
                'messageId': uuid4().hex,
            },
        }

        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(**message_payload)
        )

        print("📦 Sending non-streaming message...")
        response = await client.send_message(request)
        print("📦 Non-streaming response received:")
        print(f"   Status: {response.result.status.state}")
        if hasattr(response.result, 'artifacts') and response.result.artifacts:
            print(f"   Content: {response.result.artifacts[0].parts[0].text}")


if __name__ == '__main__':
    async def main():
        await test_streaming()
        await test_non_streaming_comparison()

    asyncio.run(main())
```

### 5. Project Configuration

**File**: `pyproject.toml`

```toml
[project]
name = "a2a06-code"
version = "0.1.0"
description = "A2A Streaming with Official Patterns"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "a2a-sdk>=0.2.8",
    "uvicorn>=0.32.1",
    "httpx>=0.28.1",
]

[tool.uv]
dev-dependencies = []
```

## 🧪 Testing

### 1. Start the Streaming Server

```bash
cd a2a06_code
uv run __main__.py
```

You should see:

```
🌊 Starting Streaming Demo Agent...
📡 Streaming capability enabled!
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### 2. Test Agent Discovery

```bash
# Check streaming capability
curl http://localhost:10000/.well-known/agent-card.json | jq '.capabilities.streaming'
```

### 3. Run Streaming Client

```bash
cd a2a06_code
uv run test_client.py
```

### 4. Test Streaming with curl

```bash
# Test streaming endpoint
curl -X POST http://localhost:10000/ \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/stream",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Stream me a response!"}],
        "messageId": "stream-test-123"
      }
    },
    "id": "stream-req-456"
  }'
```

## 📊 Expected Output

### Agent Card with Streaming

```json
{
  "name": "Streaming Demo Agent",
  "description": "Demonstrates official A2A streaming patterns with TaskUpdater",
  "url": "http://localhost:10000/",
  "capabilities": {
    "streaming": true,
    "stateTransitionHistory": true
  },
  "skills": [
    {
      "id": "streaming_response",
      "name": "Streaming Response Generator",
      "tags": ["streaming", "real-time", "status-updates"]
    }
  ]
}
```

### Streaming Client Output

```
🌊 Starting streaming communication...
📡 Receiving streaming response chunks:
------------------------------------------------------------
📦 Chunk 1 [TASK]: submitted
🔄 Chunk 2 [STATUS-INTERIM]: Starting to process your request...
🔄 Chunk 3 [STATUS-INTERIM]: Analyzing your query...
🔄 Chunk 4 [STATUS-INTERIM]: Generating response...
🎯 Chunk 5 [ARTIFACT]: Your query 'Please stream a response with status updates!' has been processed successfully!
🔄 Chunk 6 [STATUS-FINAL]: completed
------------------------------------------------------------
✅ Streaming complete! Received 6 chunks

🔄 Testing non-streaming for comparison...
📦 Sending non-streaming message...
📦 Non-streaming response received:
   Status: completed
   Content: Your query 'Send me a regular response' has been processed successfully!
```

## 🔍 Key A2A Streaming Concepts

### Official Streaming Architecture

- **TaskUpdater**: Official class for managing streaming updates
- **update_status()**: Send status updates with TaskState (working, completed, etc.)
- **add_artifact()**: Send final results as artifacts
- **complete()**: Mark task as completed
- **Server-Sent Events**: HTTP streaming using `text/event-stream`

### Task State Progression

```python
# Official task state flow
TaskState.submitted → TaskState.working → TaskState.completed
```

### Event Types

- **Task Events**: Initial task creation
- **Status Update Events**: Interim progress updates (working state)
- **Artifact Events**: Final results and outputs
- **Final Status Events**: Task completion or failure

### TaskUpdater Usage

```python
# Create updater for task
updater = TaskUpdater(event_queue, task.id, task.contextId)

# Send interim status update
await updater.update_status(
    TaskState.working,
    new_agent_text_message("Processing..."),
)

# Add final artifact
await updater.add_artifact(
    [Part(root=TextPart(text="Final result"))],
    name='result',
)

# Complete task
await updater.complete()
```

## ✅ Success Criteria

- ✅ UV project created with correct A2A SDK dependencies
- ✅ Agent card shows `streaming: true` capability
- ✅ TaskUpdater properly manages streaming events
- ✅ Server handles `message/stream` method correctly
- ✅ Client receives real-time streaming chunks
- ✅ Task state progression works (submitted → working → completed)
- ✅ Artifacts and status updates are properly separated
- ✅ SSE protocol compliance maintained

## 🎯 Next Step

Ready for [Step 07: Multiturn Conversation](../07_multiturn_conversation/) - Learn about conversation context and memory!

## 📖 Official Reference

This step implements patterns from: [A2A LangGraph Sample](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/langgraph)

**🎉 Congratulations! You've mastered official A2A streaming patterns with TaskUpdater!**
