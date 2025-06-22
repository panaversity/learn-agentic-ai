# Step 04: Agent Executor 🎯

**Implement the Agent Executor pattern - the core of A2A agents**

> **Goal**: Learn the official A2A Agent Executor pattern for handling agent execution logic.

## 🎯 What You'll Learn

- Agent Executor pattern from [official A2A tutorial](https://google-a2a.github.io/A2A/latest/tutorials/python/4-agent-executor/)
- RequestContext and EventQueue usage
- Proper agent execution lifecycle
- Official A2A SDK integration

## 📋 Prerequisites

- Completed Steps 01-03 (Agent Card, Skills, Multiple Cards)
- Understanding of async Python
- UV package manager installed

## 🚀 Implementation

### 1. Create UV Project
```bash
cd 04_agent_executor
uv init a2a04_code
cd a2a04_code
uv add a2a-server
```

### 2. Agent Executor Implementation

**File**: `agent_executor.py`

```python
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


# --8<-- [start:HelloWorldAgent]
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        # This is where Agent is invoked - whatever OpenAI Agents SDK, LangGraph, Google ADK...
        return 'Hello from Agent Executor!'


# --8<-- [end:HelloWorldAgent]


# --8<-- [start:HelloWorldAgentExecutor_init]
class HelloWorldAgentExecutor(AgentExecutor):
    """Agent Executor Implementation following official A2A pattern."""

    def __init__(self):
        self.agent = HelloWorldAgent()

    # --8<-- [end:HelloWorldAgentExecutor_init]
    # --8<-- [start:HelloWorldAgentExecutor_execute]
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute the agent and enqueue the result."""
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    # --8<-- [end:HelloWorldAgentExecutor_execute]

    # --8<-- [start:HelloWorldAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel agent execution (not supported in this basic example)."""
        raise Exception('cancel not supported')

    # --8<-- [end:HelloWorldAgentExecutor_cancel]
```

### 3. Agent Card with Executor

**File**: `agent_card_server.py`

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
from agent_executor import (
    HelloWorldAgentExecutor,  # type: ignore[import-untyped]
)


if __name__ == '__main__':
    # --8<-- [start:AgentSkill]
    skill = AgentSkill(
        id='hello_world',
        name='Returns hello world',
        description='just returns hello world',
        tags=['hello world'],
        examples=['hi', 'hello world'],
    )
    # --8<-- [end:AgentSkill]

    # --8<-- [start:AgentCard]
    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name='Hello World Agent with Executor',
        description='Agent using the official Agent Executor pattern',
        url='http://localhost:8000/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    # --8<-- [end:AgentCard]

    request_handler = DefaultRequestHandler(
        agent_executor=HelloWorldAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    print("🎯 Starting Agent Executor Server...")
    print("📋 Agent Discovery: http://localhost:8000/.well-known/agent.json")
    print("💬 A2A Endpoint: http://localhost:8000/a2a")
    uvicorn.run(server.build(), host='0.0.0.0', port=8000)
```

### 4. Test Client

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
)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = 'http://localhost:8000'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        # Fetch agent card
        logger.info(f'Fetching agent card from: {base_url}/.well-known/agent.json')
        public_agent_card: AgentCard = await resolver.get_agent_card()
        logger.info(public_agent_card.model_dump_json(indent=2, exclude_none=True))

        # Initialize client
        client = A2AClient(
            httpx_client=httpx_client, agent_card=public_agent_card
        )
        logger.info('A2AClient initialized.')

        # Send message
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'Hello Agent Executor!'}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)
        print("📤 Agent Response:")
        print(response.model_dump(mode='json', exclude_none=True))


if __name__ == '__main__':
    asyncio.run(main())
```

## 🧪 Testing

### 1. Start the Agent Server
```bash
cd a2a04_code
python agent_card_server.py
```

### 2. Test Agent Discovery
```bash
# In another terminal
curl http://localhost:8000/.well-known/agent.json | jq '.'
```

### 3. Test with Client
```bash
# In another terminal
cd a2a04_code
python test_client.py
```

### 4. Manual A2A Test
```bash
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "Test the executor!"
          }
        ],
        "messageId": "test-123"
      }
    },
    "id": "req-456"
  }' | jq '.'
```

## 📊 Expected Output

**Agent Response Structure:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": "task-abc123",
    "status": {
      "state": "completed",
      "timestamp": "2024-01-01T12:00:00"
    },
    "artifacts": [
      {
        "artifactId": "artifact-def456",
        "parts": [
          {
            "kind": "text",
            "text": "Hello from Agent Executor!"
          }
        ]
      }
    ],
    "kind": "task"
  },
  "id": "req-456"
}
```

## 🔍 Key A2A Concepts

### Agent Executor Pattern
- **AgentExecutor**: Abstract base class for agent execution logic
- **execute()**: Main method that processes requests and generates responses
- **cancel()**: Method to cancel ongoing execution
- **RequestContext**: Contains request metadata and context
- **EventQueue**: Queue for sending events/responses back to client

### Official A2A Architecture
- **A2AStarletteApplication**: Main server application
- **DefaultRequestHandler**: Handles incoming A2A requests
- **InMemoryTaskStore**: Stores task state in memory
- **AgentCard**: Describes agent capabilities
- **AgentSkill**: Defines specific agent skills

### Integration Points
- Your agent logic goes in the `HelloWorldAgent.invoke()` method
- The executor handles A2A protocol details
- EventQueue manages response streaming
- Task store handles state persistence

## ✅ Success Criteria

- ✅ UV project created with a2a-server dependency
- ✅ Agent Executor implements required methods
- ✅ Server starts and serves agent card
- ✅ Client can discover and communicate with agent
- ✅ A2A protocol compliance maintained
- ✅ Official A2A SDK patterns followed

## 🎯 Next Step

**Ready for Step 05?** → [05_hello_a2a](../05_hello_a2a/) - Interact with the server using A2A client

---

## 💡 Key Insights

1. **Agent Executor is the core pattern** - All A2A agents should implement this
2. **Separation of concerns** - Agent logic separate from A2A protocol handling
3. **Official SDK integration** - Use A2A SDK for protocol compliance
4. **Event-driven architecture** - EventQueue enables streaming and async responses
5. **Task-based responses** - All A2A responses are wrapped in task objects

## 📖 Official Reference

This step directly implements: [Agent Executor Tutorial](https://google-a2a.github.io/A2A/latest/tutorials/python/4-agent-executor/)

**🎉 Congratulations! You've implemented the official A2A Agent Executor pattern!** 