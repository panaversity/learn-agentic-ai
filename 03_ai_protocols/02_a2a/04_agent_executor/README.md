# Step 4: Agent Executor

**Master the Agent Executor pattern - the bridge between A2A and your agent logic**

## 🎯 Goal

Implement the Agent Executor pattern that wraps your agent to handle A2A protocol requests with standardized `execute()` and `cancel()` methods.

## 🔍 What You'll Learn

- Agent Executor interface and lifecycle
- RequestContext and event queue patterns
- A2A-compliant request/response handling
- Task management and status updates

## 🚀 Quick Start

```bash
# Install A2A Python SDK
uv add a2a-python

# Start the A2A server
python server.py

# Test with message/send
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "id": 1,
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Hello!"}]
      }
    }
  }'
```

## 🔧 Agent Executor Implementation

```python
from a2a import AgentExecutor, AgentTextMessage

class GreetingAgentExecutor(AgentExecutor):
    def __init__(self, agent):
        self.agent = agent
    
    async def execute(self, context, event_queue):
        # Process the incoming message
        result = await self.agent.invoke()
        
        # Create standardized response
        response_message = AgentTextMessage(
            text="Hello! I'm working with the A2A protocol!"
        )
        
        # Add to event queue
        await event_queue.put(response_message)
    
    async def cancel(self, context):
        # Handle cancellation requests
        return {"cancelled": True}
```

## 🎯 Success Criteria

- ✅ Agent executor handles execute() and cancel() 
- ✅ JSON-RPC 2.0 requests work correctly
- ✅ Response includes proper A2A message format
- ✅ Task state management works

**Next**: [Step 5: A2A Messaging](../05_a2a_messaging/) - Full client/server communication
