# Step 05: Hello A2A 💬

**First real A2A messaging - agent-to-agent communication using official SDK**

> **Goal**: Implement complete A2A messaging between a client and agent using the official A2A SDK and protocol.

## 🎯 What You'll Learn

- A2A message/send protocol implementation
- Official A2A client-server communication
- RequestContext and EventQueue usage
- Message streaming capabilities
- Complete A2A workflow from discovery to messaging
- Foundation for agent-to-agent communication

## 📋 Prerequisites

- Completed [Step 04: Agent Executor](../04_agent_executor/)
- Understanding of AgentCard, AgentSkill, and AgentExecutor
- UV package manager installed
- Basic understanding of async/await in Python

## 🚀 Implementation

### 1. Create UV Project
```bash
cd 05_hello_a2a
uv init 01_hello_a2a
cd 01_hello_a2a
uv add httpx a2a-sdk uvicorn
```

### 2. Agent Implementation

**File**: `greet_agent.py`

```python
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        # This is where Agent is invoked - whatever OpenAI Agents SDK, LangGraph, Google ADK...
        return 'Hello from Greet Agent'


class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = HelloWorldAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')
```

### 3. Agent Server

**File**: `agent_card.py`

```python
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from greet_agent import HelloWorldAgentExecutor


if __name__ == '__main__':
    # Define agent skill
    skill = AgentSkill(
        id='greet_agent',
        name='Returns a greeting',
        description='just returns a greeting',
        tags=['greeting'],
        examples=['hi', 'hello'],
    )

    # Create public agent card
    public_agent_card = AgentCard(
        name='Greet Agent',
        description='Just a greet agent',
        url='http://localhost:8000/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    
    # Setup A2A server
    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=8000)
```

### 4. A2A Client

**File**: `client.py`

```python
import logging
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


async def main() -> None:
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'

    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = 'http://localhost:8000'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        
        # Fetch Public Agent Card and Initialize Client
        logger.info(
            f'Attempting to fetch public agent card from: {base_url}{PUBLIC_AGENT_CARD_PATH}'
        )
        public_agent_card: AgentCard = await resolver.get_agent_card()
        logger.info(
            public_agent_card.model_dump_json(indent=2, exclude_none=True)
        )

        # Create A2A Client
        client = A2AClient(
            httpx_client=httpx_client, agent_card=public_agent_card
        )
        logger.info('A2AClient initialized.')

        # Send Message
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'how are you?'}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)
        print(response.model_dump(mode='json', exclude_none=True))

        # Send Streaming Message
        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        stream_response = client.send_message_streaming(streaming_request)

        async for chunk in stream_response:
            print(chunk.model_dump(mode='json', exclude_none=True))


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

## 🧪 Testing

### 1. Start the Agent Server
```bash
cd 01_hello_a2a
uv run agent_card.py
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test Agent Discovery
In another terminal:
```bash
# Test agent card discovery
curl http://localhost:8000/.well-known/agent.json | jq '.'
```

### 3. Run A2A Client
In another terminal:
```bash
cd 01_hello_a2a
uv run client.py
```

You should see the complete A2A communication flow!

### 4. Test A2A Protocol Directly
```bash
# Test message/send endpoint
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Hello A2A Agent!"}],
        "messageId": "test-123"
      }
    },
    "id": "req-456"
  }' | jq '.'
```

## 📊 Expected Output

### Agent Card Discovery
```json
{
  "name": "Greet Agent",
  "description": "Just a greet agent",
  "url": "http://localhost:8000/",
  "version": "1.0.0",
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "greet_agent",
      "name": "Returns a greeting",
      "description": "just returns a greeting",
      "tags": ["greeting"],
      "examples": ["hi", "hello"]
    }
  ]
}
```

### Client Output
```
INFO:root:Attempting to fetch public agent card from: http://localhost:8000/.well-known/agent.json
INFO:root:A2AClient initialized.
{
  "jsonrpc": "2.0",
  "result": {
    "task": {
      "taskId": "task-abc123",
      "status": "completed",
      "artifacts": [
        {
          "kind": "text",
          "text": "Hello from Greet Agent"
        }
      ]
    }
  },
  "id": "req-456"
}
```

## 🔍 Key A2A Concepts

### A2A Message Flow
1. **Agent Discovery**: Client fetches agent card via `/.well-known/agent.json`
2. **Client Initialization**: A2AClient created with agent card
3. **Message Creation**: SendMessageRequest with user message
4. **Protocol Communication**: JSON-RPC 2.0 over HTTP
5. **Task Execution**: Agent processes message and returns task result

### Official A2A Components
- **A2ACardResolver**: Handles agent discovery
- **A2AClient**: Official client for A2A communication
- **AgentExecutor**: Server-side agent execution
- **RequestContext**: Contains request metadata
- **EventQueue**: Manages response events and streaming

### Message Structure
- **role**: 'user' or 'agent'
- **parts**: Array of message parts (text, data, file)
- **messageId**: Unique identifier for message
- **taskId**: Unique identifier for execution task

### JSON-RPC 2.0 Protocol
- **method**: A2A protocol method (message/send, message/stream)
- **params**: Method-specific parameters
- **id**: Request identifier for response matching
- **jsonrpc**: Protocol version ("2.0")

## ✅ Success Criteria

- ✅ UV project created with a2a-sdk and httpx dependencies
- ✅ Agent server starts using official A2A SDK
- ✅ Agent card accessible at `/.well-known/agent.json`
- ✅ A2A client successfully discovers agent
- ✅ Message/send protocol works correctly
- ✅ Streaming message protocol works
- ✅ Task-based responses returned properly
- ✅ JSON-RPC 2.0 compliance verified

## 🎯 Next Step

Ready for [Step 06: Message Streaming](../06_message_streaming/) - Learn about real-time streaming communication!

## 📖 Official Reference

This step implements the official A2A tutorial: [Hello A2A](https://google-a2a.github.io/A2A/latest/tutorials/python/1-hello-a2a/)

**🎉 Congratulations! You've successfully implemented complete A2A agent-to-agent communication using the official SDK!**