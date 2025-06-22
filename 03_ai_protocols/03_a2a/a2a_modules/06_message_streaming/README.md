# Step 06: Message Streaming 🌊

**Real-time streaming communication - Server-Sent Events with A2A protocol**

> **Goal**: Implement real-time message streaming using the official A2A SDK for responsive agent communication.

## 🎯 What You'll Learn

- A2A message/stream protocol implementation
- Server-Sent Events (SSE) for real-time streaming
- EventQueue management for streaming responses
- Chunked response handling
- Real-time agent feedback patterns
- Foundation for conversational AI agents

## 📋 Prerequisites

- Completed [Step 05: Hello A2A](../05_hello_a2a/)
- Understanding of A2A messaging protocol
- UV package manager installed
- Basic understanding of streaming concepts

## 🚀 Implementation

### 1. Create UV Project
```bash
cd 06_message_streaming
uv init a2a06_code
cd a2a06_code
uv add httpx a2a-sdk uvicorn
```

### 2. Streaming Agent Implementation

**File**: `streaming_agent.py`

```python
import asyncio
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


class StreamingAgent:
    """Agent that demonstrates streaming responses."""

    async def invoke(self, message: str) -> None:
        """Generate streaming response word by word."""
        response_parts = [
            "Hello!", "I'm", "streaming", "this", "response", 
            "word", "by", "word", "to", "demonstrate", 
            "real-time", "communication", "capabilities."
        ]
        
        for part in response_parts:
            yield part
            await asyncio.sleep(0.5)  # Simulate processing time


class StreamingAgentExecutor(AgentExecutor):
    """Agent Executor that handles streaming responses."""

    def __init__(self):
        self.agent = StreamingAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # Extract message from context
        message_text = "default message"
        if context.message and context.message.parts:
            for part in context.message.parts:
                if part.kind == "text":
                    message_text = part.text
                    break

        # Stream response parts
        async for response_part in self.agent.invoke(message_text):
            await event_queue.enqueue_event(new_agent_text_message(response_part))
            
        # Send final completion message
        await event_queue.enqueue_event(new_agent_text_message("\n\n✅ Streaming complete!"))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        await event_queue.enqueue_event(new_agent_text_message("❌ Streaming cancelled"))
```

### 3. Streaming Server

**File**: `streaming_server.py`

```python
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    AgentProvider,
)
from streaming_agent import StreamingAgentExecutor


if __name__ == '__main__':
    # Define streaming skill
    streaming_skill = AgentSkill(
        id='streaming_response',
        name='Streaming Response Generator',
        description='Generates real-time streaming responses word by word',
        tags=['streaming', 'real-time', 'communication'],
        examples=['Tell me a story', 'Explain something step by step'],
    )

    # Create agent card with streaming capabilities
    public_agent_card = AgentCard(
        name='Streaming Demo Agent',
        description='Demonstrates real-time streaming communication using A2A protocol',
        url='http://localhost:8001/',
        version='1.0.0',
        provider=AgentProvider(
            organization='A2A Streaming Lab',
            url='http://localhost:8001/',
        ),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=AgentCapabilities(
            streaming=True,  # Enable streaming capability
            pushNotifications=False,
            stateTransitionHistory=False,
        ),
        skills=[streaming_skill],
    )
    
    # Setup A2A server with streaming support
    request_handler = DefaultRequestHandler(
        agent_executor=StreamingAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    print("🌊 Starting Streaming Demo Agent...")
    print("📡 Streaming capability enabled!")
    uvicorn.run(server.build(), host='0.0.0.0', port=8001)
```

### 4. Streaming Client

**File**: `streaming_client.py`

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
    SendStreamingMessageRequest,
)


async def test_streaming() -> None:
    """Test streaming message communication."""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = 'http://localhost:8001'

    async with httpx.AsyncClient() as httpx_client:
        # Discover agent
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        
        logger.info(f'Discovering streaming agent at: {base_url}')
        public_agent_card: AgentCard = await resolver.get_agent_card()
        
        # Verify streaming capability
        if public_agent_card.capabilities and public_agent_card.capabilities.streaming:
            logger.info("✅ Agent supports streaming!")
        else:
            logger.warning("⚠️ Agent does not support streaming")

        # Create streaming client
        client = A2AClient(
            httpx_client=httpx_client, 
            agent_card=public_agent_card
        )

        # Prepare streaming message
        message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'Please stream a response to me!'}
                ],
                'messageId': uuid4().hex,
            },
        }

        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()), 
            params=MessageSendParams(**message_payload)
        )

        print("\n🌊 Starting streaming communication...")
        print("📡 Receiving streaming response:")
        print("-" * 50)

        # Process streaming response
        stream_response = client.send_message_streaming(streaming_request)
        
        chunk_count = 0
        async for chunk in stream_response:
            chunk_count += 1
            print(f"Chunk {chunk_count}: {chunk.model_dump(mode='json', exclude_none=True)}")
            
            # Add visual separator between chunks
            if chunk_count % 3 == 0:
                print("...")
                await asyncio.sleep(0.2)

        print("-" * 50)
        print(f"✅ Streaming complete! Received {chunk_count} chunks")


async def test_non_streaming_comparison() -> None:
    """Compare with non-streaming message for demonstration."""
    
    print("\n🔄 Comparing with non-streaming message...")
    
    base_url = 'http://localhost:8001'

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        public_agent_card = await resolver.get_agent_card()
        client = A2AClient(httpx_client=httpx_client, agent_card=public_agent_card)

        # Send regular (non-streaming) message
        from a2a.types import SendMessageRequest
        
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
        print("📦 Non-streaming response:")
        print(response.model_dump(mode='json', exclude_none=True))


if __name__ == '__main__':
    async def main():
        await test_streaming()
        await test_non_streaming_comparison()
    
    asyncio.run(main())
```

## 🧪 Testing

### 1. Start the Streaming Server
```bash
cd a2a06_code
uv run streaming_server.py
```

You should see:
```
🌊 Starting Streaming Demo Agent...
📡 Streaming capability enabled!
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 2. Test Agent Discovery
```bash
# Check streaming capability in agent card
curl http://localhost:8001/.well-known/agent.json | jq '.capabilities.streaming'
```

### 3. Run Streaming Client
```bash
cd a2a06_code
uv run streaming_client.py
```

### 4. Test Streaming with curl
```bash
# Test streaming endpoint
curl -X POST http://localhost:8001/a2a \
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
  "description": "Demonstrates real-time streaming communication using A2A protocol",
  "url": "http://localhost:8001/",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "skills": [
    {
      "id": "streaming_response",
      "name": "Streaming Response Generator",
      "tags": ["streaming", "real-time", "communication"]
    }
  ]
}
```

### Streaming Client Output
```
🌊 Starting streaming communication...
📡 Receiving streaming response:
--------------------------------------------------
Chunk 1: {"jsonrpc": "2.0", "result": {"task": {"taskId": "task-123", "status": "running", "artifacts": [{"kind": "text", "text": "Hello!"}]}}}
Chunk 2: {"jsonrpc": "2.0", "result": {"task": {"taskId": "task-123", "status": "running", "artifacts": [{"kind": "text", "text": "I'm"}]}}}
Chunk 3: {"jsonrpc": "2.0", "result": {"task": {"taskId": "task-123", "status": "running", "artifacts": [{"kind": "text", "text": "streaming"}]}}}
...
Chunk 14: {"jsonrpc": "2.0", "result": {"task": {"taskId": "task-123", "status": "completed", "artifacts": [{"kind": "text", "text": "✅ Streaming complete!"}]}}}
--------------------------------------------------
✅ Streaming complete! Received 14 chunks
```

## 🔍 Key A2A Streaming Concepts

### Streaming Protocol
- **method**: `message/stream` (vs `message/send`)
- **Accept header**: `text/event-stream` for Server-Sent Events
- **Response format**: Multiple JSON-RPC responses over SSE
- **Task status**: `running` → `completed` progression

### EventQueue Management
- **enqueue_event()**: Sends individual chunks to client
- **new_agent_text_message()**: Creates properly formatted text artifacts
- **Async iteration**: Agent yields response parts over time
- **Completion signaling**: Final message with `completed` status

### Streaming vs Non-Streaming
- **Streaming**: Real-time chunks, immediate feedback, better UX
- **Non-streaming**: Single response, wait for completion, simpler
- **Use cases**: Long responses, step-by-step processes, interactive experiences

### Server-Sent Events (SSE)
- **Protocol**: HTTP-based streaming over persistent connection
- **Format**: `data: {json}\n\n` for each event
- **Browser support**: Native EventSource API
- **Reliability**: Automatic reconnection, error handling

## ✅ Success Criteria

- ✅ UV project created with streaming dependencies
- ✅ Agent card shows `streaming: true` capability
- ✅ Streaming server handles `message/stream` method
- ✅ EventQueue properly manages streaming events
- ✅ Client receives real-time streaming chunks
- ✅ SSE protocol works correctly
- ✅ Task status progression (running → completed)
- ✅ Comparison with non-streaming messaging works

## 🎯 Next Step

Ready for [Step 07: Multiturn Conversation](../07_multiturn_conversation/) - Learn about maintaining conversation context!

## 📖 Official Reference

This step builds on: [A2A Streaming Documentation](https://google-a2a.github.io/A2A/latest/specification/#message-streaming)

**🎉 Congratulations! You've mastered real-time streaming communication with the A2A protocol!** 