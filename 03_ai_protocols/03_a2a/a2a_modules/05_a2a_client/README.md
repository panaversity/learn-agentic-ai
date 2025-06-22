# Step 05: A2A Client 🤝

**Master agent-to-agent communication using the official A2A SDK**

> **🎯 Official Tutorial**: [Interact with Server - A2A Python Tutorial](https://google-a2a.github.io/A2A/latest/tutorials/python/6-interact-with-server/)

> **Goal**: Learn how to build A2A clients that can discover, connect to, and communicate with A2A agents using the official SDK patterns.

## 📊 Current Status

| Component | Status | Description |
|-----------|--------|-------------|
| ✅ **Agent Server** | Ready | Uses corrected message extraction from Step 04 |
| ✅ **Client Discovery** | Working | A2ACardResolver and agent card fetching |
| ✅ **Non-Streaming** | Working | `message/send` with proper message format |
| ✅ **Streaming** | Working | `message/stream` with real-time responses |
| ✅ **Error Handling** | Implemented | Connection errors and graceful failures |

## 🎯 What You'll Learn

- **A2A Client SDK** - Using `A2AClient` and `A2ACardResolver`
- **Agent Discovery** - Fetching and parsing Agent Cards  
- **Message Protocols** - `message/send` vs `message/stream`
- **Request/Response Flow** - Complete A2A communication lifecycle
- **Streaming Communication** - Real-time agent interactions
- **Error Handling** - Robust client implementations
- **Agent-to-Agent Foundation** - Building blocks for multi-agent systems

## 📋 Prerequisites

- Completed [Step 04: Agent Executor](../04_agent_executor/) - **Essential!**
- Understanding of Agent Cards and Agent Skills
- UV package manager installed
- Basic understanding of async/await in Python

## 🚀 Implementation

### 1. Project Overview

This step includes a complete A2A client-server setup:

```
05_a2a_client/
├── greet_agent.py      # Agent with corrected message extraction
├── agent_card.py       # A2A server setup
├── client.py           # Comprehensive A2A client demo
├── pyproject.toml      # UV project configuration
└── README.md           # This guide
```

### 2. Agent Server (For Testing)

**File**: `greet_agent.py` - **Uses corrected patterns from Step 04**

```python
import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)


class GreetingAgent:
    """A greeting agent that responds to user messages contextually."""

    async def invoke(self, message: str = "") -> str:
        """Process user input and return appropriate greeting."""
        if not message or message == "No message found":
            return 'Hello! How can I help you today?'
        
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return f'Hello there! You said: "{message}"'
        elif "goodbye" in message_lower or "bye" in message_lower:
            return f'Goodbye! Thanks for chatting: "{message}"'
        elif "how are you" in message_lower:
            return "I'm doing great! Thanks for asking. How can I assist you?"
        else:
            return f'I heard you say: "{message}". How can I assist you?'


class GreetingAgentExecutor(AgentExecutor):
    """Agent Executor using corrected message extraction from Step 04."""

    def __init__(self):
        self.agent = GreetingAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Extract user message using CORRECTED pattern from Step 04
        user_message = self._extract_message_from_context(context)
        
        # Process with greeting agent
        result = await self.agent.invoke(user_message)
        
        # Send response via event queue
        await event_queue.enqueue_event(new_agent_text_message(result))

    def _extract_message_from_context(self, context: RequestContext) -> str:
        """
        Extract user message using corrected pattern from Step 04.
        
        Key fix: A2A SDK structure is Part(root=TextPart(text='hello'))
        """
        if not context.message:
            return "No message found"
            
        if context.message.parts:
            for part in context.message.parts:
                # Method 1: A2A SDK structure: Part(root=TextPart(text='hello'))
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    return part.root.text
                # Method 2: Direct text attribute fallback
                elif hasattr(part, 'text'):
                    return part.text
        
        return "No message found"
```

### 3. A2A Client Implementation

**File**: `client.py` - **Comprehensive client demonstration**

```python
import asyncio
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2AClientDemo:
    """Complete A2A Client demonstration showing the full workflow."""
    
    def __init__(self, agent_url: str):
        self.agent_url = agent_url
        self.agent_card: AgentCard = None
        self.client: A2AClient = None
    
    async def discover_agent(self, httpx_client: httpx.AsyncClient) -> None:
        """Step 1: Agent Discovery - Fetch agent capabilities."""
        logger.info("🔍 === AGENT DISCOVERY ===")
        
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=self.agent_url,
        )
        
        # Fetch Agent Card from /.well-known/agent.json
        self.agent_card = await resolver.get_agent_card()
        logger.info(f"✅ Discovered Agent: {self.agent_card.name}")
        logger.info(f"🎯 Skills: {[skill.name for skill in self.agent_card.skills]}")
    
    async def setup_client(self, httpx_client: httpx.AsyncClient) -> None:
        """Step 2: Initialize A2A Client."""
        logger.info("🔧 === CLIENT SETUP ===")
        
        self.client = A2AClient(
            httpx_client=httpx_client,
            agent_card=self.agent_card
        )
        logger.info("✅ A2A Client ready to communicate")
    
    async def send_message(self, message_text: str) -> dict:
        """Step 3a: Non-Streaming Message (message/send)."""
        logger.info(f"📤 Sending: '{message_text}'")
        
        # Create A2A message payload
        message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'text': message_text}  # Simplified format
                ],
                'messageId': uuid4().hex,
            },
        }
        
        request = SendMessageRequest(
            id=str(uuid4()), 
            params=MessageSendParams(**message_payload)
        )
        
        response = await self.client.send_message(request)
        
        # Extract and display response
        response_data = response.model_dump(mode='json', exclude_none=True)
        if 'result' in response_data and 'parts' in response_data['result']:
            for part in response_data['result']['parts']:
                if 'text' in part:
                    print(f"🤖 Agent: {part['text']}")
        
        return response_data
    
    async def send_streaming_message(self, message_text: str) -> None:
        """Step 3b: Streaming Message (message/stream)."""
        logger.info(f"🌊 Streaming: '{message_text}'")
        
        message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [{'text': message_text}],
                'messageId': uuid4().hex,
            },
        }
        
        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()), 
            params=MessageSendParams(**message_payload)
        )
        
        stream_response = self.client.send_message_streaming(streaming_request)
        
        print("🌊 Streaming Response:")
        chunk_count = 0
        
        async for chunk in stream_response:
            chunk_count += 1
            chunk_data = chunk.model_dump(mode='json', exclude_none=True)
            
            # Extract text from streaming chunk
            if 'result' in chunk_data and 'parts' in chunk_data['result']:
                for part in chunk_data['result']['parts']:
                    if 'text' in part:
                        print(f"Chunk #{chunk_count}: {part['text']}")
        
        logger.info(f"✅ Streaming completed: {chunk_count} chunks")


async def main():
    """Main demo showing complete A2A client workflow."""
    agent_url = 'http://localhost:8000'
    
    print("🚀 A2A Client Demo Starting...")
    
    async with httpx.AsyncClient() as httpx_client:
        demo = A2AClientDemo(agent_url)
        
        try:
            # Step 1: Discover the agent
            await demo.discover_agent(httpx_client)
            
            # Step 2: Setup client  
            await demo.setup_client(httpx_client)
            
            # Step 3a: Non-streaming messages
            await demo.send_message("Hello there!")
            await demo.send_message("How are you doing?")
            
            # Step 3b: Streaming messages  
            await demo.send_streaming_message("Say goodbye nicely")
            
            print("🎉 Demo completed successfully!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
```

## 🧪 Testing the Complete Flow

### 1. Start the Agent Server

```bash
cd 05_a2a_client

# Start the A2A greeting agent server
uv run agent_card.py
```

**Expected Output:**
```
🤖 Starting A2A Greeting Agent Server...
📋 Agent Discovery: http://localhost:8000/.well-known/agent.json
💬 Agent Name: A2A Greeting Agent
🎯 Skills: ['Greeting Agent']
🔗 Ready for A2A client connections...

INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test Agent Discovery

```bash
# In another terminal
curl http://localhost:8000/.well-known/agent.json | jq '.'
```

**Expected Response:**
```json
{
  "capabilities": {
    "streaming": true
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "description": "A friendly A2A agent for testing client-server communication patterns",
  "name": "A2A Greeting Agent",
  "skills": [
    {
      "description": "A friendly agent that responds to greetings and processes user messages",
      "examples": ["hello", "hi there", "how are you?", "goodbye", "tell me about yourself"],
      "id": "greeting_agent",
      "name": "Greeting Agent",
      "tags": ["greeting", "chat", "friendly", "test"]
    }
  ],
  "url": "http://localhost:8000/",
  "version": "1.0.0"
}
```

### 3. Run the A2A Client

```bash
# In another terminal (keep server running)
cd 05_a2a_client
uv run client.py
```

**Expected Output:**
```
🚀 A2A Client Demo Starting...

INFO:client:🔍 === AGENT DISCOVERY ===
INFO:client:Fetching Agent Card from: http://localhost:8000/.well-known/agent.json
INFO:client:✅ Discovered Agent: A2A Greeting Agent
INFO:client:🎯 Skills: ['Greeting Agent']

INFO:client:🔧 === CLIENT SETUP ===
INFO:client:✅ A2A Client ready to communicate

==================================================
INFO:client:📤 Sending: 'Hello there!'
🤖 Agent: Hello there! You said: "Hello there!"

INFO:client:📤 Sending: 'How are you doing?'
🤖 Agent: I'm doing great! Thanks for asking. How can I assist you?

INFO:client:📤 Sending: 'Tell me about yourself'
🤖 Agent: I heard you say: "Tell me about yourself". How can I assist you?

==================================================
INFO:client:🌊 Streaming: 'Say goodbye nicely'
🌊 Streaming Response:
Chunk #1: Goodbye! Thanks for chatting: "Say goodbye nicely"
INFO:client:✅ Streaming completed: 1 chunks

🎉 Demo completed successfully!
```

## 🔍 Key Learning Points

### Message Format Evolution

**❌ Old (Incorrect):**
```python
# This was causing 'Part' object has no attribute 'kind' error
if part.kind == "text":
    return part.text
```

**✅ New (Corrected from Step 04):**
```python
# Correct A2A SDK structure: Part(root=TextPart(text='hello'))
if hasattr(part, 'root') and hasattr(part.root, 'text'):
    return part.root.text
elif hasattr(part, 'text'):
    return part.text
```

### Client Message Format

**A2A Client sends this format:**
```python
message_payload = {
    'message': {
        'role': 'user',
        'parts': [
            {'text': 'hello world'}  # No 'kind' needed
        ],
        'messageId': uuid4().hex,
    },
}
```

**A2A Server receives this structure:**
```python
# context.message.parts = [Part(root=TextPart(text='hello world'))]
# Access via: part.root.text
```

### Communication Patterns

1. **Discovery**: `/.well-known/agent.json` → Agent Card
2. **Setup**: `A2ACardResolver` + `A2AClient` 
3. **Non-Streaming**: `send_message()` → Complete response
4. **Streaming**: `send_message_streaming()` → Real-time chunks

## ✅ Success Criteria

- ✅ **Agent Discovery**: Fetch and parse Agent Cards
- ✅ **Client Setup**: Initialize A2A client with discovered agent
- ✅ **Non-Streaming**: Send messages and receive complete responses
- ✅ **Streaming**: Handle real-time streaming responses
- ✅ **Message Extraction**: Server correctly processes client messages
- ✅ **Error Handling**: Graceful connection and processing failures

## 🎯 Next Steps

**Ready for Multi-Agent Communication?** → Continue to advanced A2A patterns:
- Agent-to-Agent delegation
- Multi-step workflows
- Orchestration patterns
- Error propagation across agents

---

## 💡 Key Insights

1. **Discovery First**: Always start with Agent Card discovery to understand capabilities
2. **Message Structure**: Client sends simplified format, server receives Part(root=TextPart) structure
3. **Streaming vs Non-Streaming**: Choose based on response length and real-time requirements
4. **Error Handling**: Essential for robust agent-to-agent communication
5. **Foundation for Multi-Agent**: This pattern scales to complex agent orchestration

## 📖 Official References

- [A2A Python Tutorial - Interact with Server](https://google-a2a.github.io/A2A/latest/tutorials/python/6-interact-with-server/)
- [A2A SDK Documentation](https://google-a2a.github.io/A2A/latest/)
- [Step 04: Agent Executor](../04_agent_executor/) - **Required foundation**

**🎉 You've mastered A2A client-server communication - the foundation of agent networks!**