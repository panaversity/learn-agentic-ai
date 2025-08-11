# Step 04: Agent Executor 🎯

**Master the Agent Executor pattern - the core engine of A2A agents**

> **🎯 Official Tutorial**: [Agent Executor - A2A Python Tutorial](https://google-a2a.github.io/A2A/latest/tutorials/python/4-agent-executor/)

> **Goal**: Deep dive into the Agent Executor pattern to understand how it processes requests, manages EventQueue, and handles the core execution logic.

## 📊 Current Status

| Component                 | Status  | Description                             |
| ------------------------- | ------- | --------------------------------------- |
| ✅ **Agent Discovery**    | Working | `/.well-known/agent-card.json` endpoint |
| ✅ **Server Setup**       | Working | A2A server starts successfully          |
| ✅ **Official Pattern**   | Working | HelloWorld executor matches tutorial    |
| ✅ **Enhanced Pattern**   | Ready   | Educational version with logging        |
| ✅ **Message Testing**    | Fixed   | Message extraction working correctly    |
| ✅ **Postman Collection** | Working | Comprehensive test scenarios            |

**✅ Fixed**: Message extraction now works correctly by accessing `part.root.text` from A2A SDK Part structure.

## 🎯 What You'll Learn

- **AgentExecutor pattern** - The heart of every A2A agent
- **EventQueue mechanics** - Understanding `enqueue` and `dequeue` operations
- **RequestContext** - How agent receives and processes requests
- **Official A2A patterns** - Following the exact tutorial examples
- **Enhanced implementations** - Building on the foundation
- **Raw A2A requests** - Manual testing without client SDK
- **Execution lifecycle** - From request to response

## 📋 Prerequisites

- Completed [Step 03: Multiple Cards](../03_multiple_cards/)
- Understanding of async Python
- UV package manager installed

## 🚀 Implementation

### 1. Create UV Project

```bash
cd 04_agent_executor
uv init a2a04_code
cd a2a04_code
uv add a2a-sdk uvicorn
```

### Enhanced Agent Executor (Learning Version)

**File**: `agent_executor.py`

```python
import asyncio
import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)


class EnhancedAgent:
    """Enhanced agent that processes actual user messages."""

    async def invoke(self, message: str) -> str:
        """Process a message and return response."""
        logger.info(f"Agent processing message: {message}")

        # Simulate some processing time
        await asyncio.sleep(0.5)

        # Different responses based on input
        if "hello" in message.lower():
            return "Hello! Nice to meet you through the A2A protocol!"
        elif "time" in message.lower():
            return "I don't have access to real time, but I can process your requests!"
        elif "error" in message.lower():
            raise Exception("Simulated error for testing error handling")
        else:
            return f"I received your message: '{message}'. How can I help you?"


class EnhancedAgentExecutor(AgentExecutor):
    """
    Enhanced Agent Executor that processes actual user input.

    Key improvements over official example:
    1. Extracts user message from RequestContext
    2. Processes the actual message content
    3. Detailed logging for learning
    4. Error handling
    """

    def __init__(self):
        self.agent = EnhancedAgent()
        logger.info("Enhanced AgentExecutor initialized")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Enhanced execution with message processing.
        """
        logger.info("=== Enhanced AgentExecutor.execute() called ===")

        # Extract message from RequestContext
        user_message = self._extract_message_from_context(context)
        logger.info(f"Extracted user message: {user_message}")

        # Log context details for learning
        self._log_context_details(context)

        try:
            # Process with enhanced agent
            logger.info("Calling enhanced agent.invoke()...")
            result = await self.agent.invoke(user_message)
            logger.info(f"Agent returned: {result}")

            # Enqueue the response
            logger.info("Enqueueing response to EventQueue...")
            await event_queue.enqueue_event(new_agent_text_message(result))
            logger.info("✅ Response successfully enqueued!")

        except Exception as e:
            # Handle errors gracefully
            error_msg = f"Agent execution failed: {str(e)}"
            logger.error(error_msg)
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        """Enhanced cancel with proper response."""
        logger.info("=== Enhanced AgentExecutor.cancel() called ===")
        cancel_msg = "Agent execution was cancelled"
        await event_queue.enqueue_event(new_agent_text_message(cancel_msg))

    def _extract_message_from_context(self, context: RequestContext) -> str:
        """Extract user message from RequestContext."""
        if not context.message:
            return "No message found"

        if context.message.parts:
            for part in context.message.parts:
                # A2A SDK structure: Part(root=TextPart(text='hello'))
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    return part.root.text
                elif hasattr(part, 'text'):
                    return part.text
        return "No message found"

    def _log_context_details(self, context: RequestContext):
        """Log RequestContext details for learning purposes."""
        logger.info("--- RequestContext Details ---")
        logger.info(f"Message ID: {context.message.messageId if context.message else 'None'}")
        logger.info(f"Message Role: {context.message.role if context.message else 'None'}")
        logger.info(f"Message Parts Count: {len(context.message.parts) if context.message and context.message.parts else 0}")
        logger.info(f"Task ID: {context.task_id}")
        logger.info("-----------------------------")
```

### 4. Server Implementation

**File**: `main.py`

```python
import uvicorn
import logging
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# Choose which executor to use
from agent_executor import EnhancedAgentExecutor  # Official example
# from enhanced_agent_executor import EnhancedAgentExecutor  # Enhanced version

# Enable detailed logging to see EventQueue operations
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # Agent skill definition
    skill = AgentSkill(
        id='hello_world',
        name='Returns hello world',
        description='Official A2A HelloWorld example - just returns hello world',
        tags=['hello world', 'tutorial', 'official'],
        examples=['hi', 'hello world', 'test'],
    )

    # Agent card matching official tutorial
    agent_card = AgentCard(
        name='Hello World Agent Executor',
        description='Official A2A Agent Executor tutorial implementation',
        url='http://localhost:9999/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    # Setup A2A server with official components
    request_handler = DefaultRequestHandler(
        agent_executor=EnhancedAgentExecutor(),  # Use official executor
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    print("🎯 Starting Official Agent Executor Server...")
    print("📋 Agent Discovery: http://localhost:9999/.well-known/agent-card.json")
    print("💬 Test with curl or Postman (see collection below)...")
    uvicorn.run(server.build(), host='0.0.0.0', port=9999)
```

## 🧪 Testing & Learning

### 1. Start the Demo Server

```bash
cd a2a04_code
uv run main.py
```

**Expected Output:**

```
🎯 Starting Official Agent Executor Server...
📋 Agent Discovery: http://localhost:9999/.well-known/agent-card.json
💬 Test with curl or Postman (see collection below)...
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9999 (Press CTRL+C to quit)
```

### 2. Agent Discovery Test

```bash
curl http://localhost:9999/.well-known/agent-card.json | jq '.'
```

**Expected Response:**

```json
{
  "capabilities": {
    "streaming": false
  },
  "defaultInputModes": ["text"],
  "defaultOutputModes": ["text"],
  "description": "Official A2A Agent Executor tutorial implementation",
  "name": "Hello World Agent Executor",
  "skills": [
    {
      "description": "Official A2A HelloWorld example - just returns hello world",
      "examples": ["hi", "hello world", "test"],
      "id": "hello_world",
      "name": "Returns hello world",
      "tags": ["hello world", "tutorial", "official"]
    }
  ],
  "url": "http://localhost:9999/",
  "version": "1.0.0"
}
```

You can also try sending a message:

```bash
 curl -X POST http://localhost:9999/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "hello"}],
        "messageId": "test-001"
      }
    },
    "id": "req-001"
  }' | jq '.'
```

### 3. Testing with Enhanced Executor

## 🔧 Postman Collection Testing

A comprehensive Postman collection is included for thorough testing:

**File**: `A2A_Agent_Executor_Tests.postman_collection.json`

### Import and Setup

1. **Import the Collection**:

   - Open Postman
   - Click "Import" → "Upload Files"
   - Select `A2A_Agent_Executor_Tests.postman_collection.json`

2. **Set Environment Variables**:

   - Create a new Environment called "A2A Local"
   - Add variable: `base_url` = `http://localhost:9999`

3. **Start Your Server**:
   ```bash
   cd a2a04_code
   uv run main.py
   ```

### Test Scenarios

The collection includes:

1. **01 - Agent Discovery**: Tests `/.well-known/agent-card.json` endpoint
2. **02 - Basic Hello Message**: Sends simple message via `message/send`
3. **03 - Different Message Content**: Tests that official agent always returns "Hello World"
4. **04 - Invalid JSON-RPC Method**: Tests error handling

### Running Tests

**Option 1: Individual Tests**

- Click any request and hit "Send"
- Check the "Test Results" tab for validations

**Option 2: Collection Runner**

- Click "..." next to collection name
- Select "Run collection"
- Choose environment and run all tests

### Expected Test Results

✅ **All tests should pass when using the official HelloWorldAgentExecutor**

- Agent Discovery: Validates agent card structure
- Basic Message: Confirms "Hello World" response
- Different Content: Still returns "Hello World" (official behavior)
- Invalid Method: Proper JSON-RPC error handling

### Testing Enhanced Executor

To test the enhanced version:

1. Update `main.py` to use `EnhancedAgentExecutor`
2. Re-run tests
3. Test #03 should show different behavior (processes actual message content)

## 🔍 Deep Dive: EventQueue Mechanics

### What is EventQueue?

The `EventQueue` is the core communication channel between your agent and the A2A client:

```python
# ENQUEUE: Your agent puts responses into the queue
await event_queue.enqueue_event(new_agent_text_message("Hello!"))

# DEQUEUE: A2A system takes responses from queue and sends to client
# (This happens automatically in the A2A framework)
```

### EventQueue Operations

1. **Enqueue** (`await event_queue.enqueue_event()`):

   - Your agent puts messages/artifacts into the queue
   - These get converted to proper A2A protocol format
   - Sent to the client as JSON-RPC responses

2. **Dequeue** (automatic):
   - A2A system pulls events from queue
   - Converts to HTTP responses
   - Delivers to client

### Key EventQueue Methods

```python
# Send text message
await event_queue.enqueue_event(new_agent_text_message("Hello"))

# Send custom event (advanced)
from a2a.types import Event
await event_queue.enqueue_event(Event(...))
```

## 🔧 RequestContext Deep Dive

The `RequestContext` contains everything about the incoming request:

```python
def analyze_context(context: RequestContext):
    """Understand what's in RequestContext"""

    # The actual message from user
    message = context.message
    print(f"User said: {message.parts[0].text}")
    print(f"Message ID: {message.messageId}")
    print(f"Role: {message.role}")  # Usually "user"

    # Task information
    print(f"Task ID: {context.task_id}")

    # Authentication info (if any)
    print(f"Auth info: {context.auth_context}")
```

## ✅ Success Criteria

- ✅ **Understand AgentExecutor**: Know how `execute()` and `cancel()` work
- ✅ **Master EventQueue**: Understand enqueue operations and why they matter
- ✅ **Parse RequestContext**: Extract user messages and context data
- ✅ **Handle Raw Requests**: Test with curl commands
- ✅ **See the Logs**: Watch the execution flow in real-time
- ✅ **Error Handling**: Understand how exceptions are managed

## 🎯 Next Step

**Ready for A2A Client?** → [05_a2a_client](../05_a2a_client/) - Learn agent-to-agent communication

**Why Skip "Start Server"?**
Server startup is the same everywhere: `uvicorn.run(server.build(), ...)`. The real learning is in **client interaction** and **messaging patterns**.

---

## 💡 Key Insights

1. **AgentExecutor is the Engine**: Every A2A agent centers around this pattern
2. **EventQueue is the Highway**: All responses travel through `enqueue_event()`
3. **RequestContext is the Package**: Contains everything about the incoming request
4. **Logging is Learning**: Watch the execution flow to understand the pattern
5. **Raw Testing First**: Understand the protocol before using helper SDKs

## 📖 Official Reference

Agent Executor pattern from: [A2A HelloWorld Sample](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/helloworld)

**🎉 You've mastered the core Agent Executor pattern - the foundation of all A2A agents!**
