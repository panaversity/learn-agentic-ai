# Step 07: Multiturn Conversation 💬

**Context-aware conversations with memory - Official patterns from LangGraph sample**

> **Goal**: Implement multiturn conversations using official A2A patterns from [a2a-samples/langgraph](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/langgraph) with contextId management and conversation memory.

## 🎯 What You'll Learn

- Official multiturn conversation patterns from [LangGraph sample](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/langgraph)
- Context management with `contextId` and task continuity  
- Conversation memory and state persistence
- Input-required states for interactive dialogue
- History tracking across message exchanges
- RequestContext usage for multiturn scenarios

## 📋 Prerequisites

- Completed [Step 06: Message Streaming](../06_message_streaming/)
- Understanding of A2A TaskUpdater and streaming
- UV package manager installed
- Basic understanding of conversation state management

## 🚀 Implementation

### 1. Create UV Project
```bash
cd 07_multiturn_conversation
uv init a2a07_code
cd a2a07_code
uv add a2a-sdk uvicorn httpx
```

### 2. Conversational Agent Implementation

**File**: `conversation_agent.py`

```python
import logging
from typing import Dict, List, Any
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Part, TextPart, TaskState
from a2a.utils import new_agent_text_message, new_task

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Simple conversation memory following official patterns."""
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, str]]] = {}
    
    def add_message(self, context_id: str, role: str, content: str):
        """Add message to conversation history."""
        if context_id not in self.conversations:
            self.conversations[context_id] = []
        
        self.conversations[context_id].append({
            "role": role,
            "content": content,
            "timestamp": str(len(self.conversations[context_id]))
        })
    
    def get_conversation(self, context_id: str) -> List[Dict[str, str]]:
        """Get conversation history for context."""
        return self.conversations.get(context_id, [])
    
    def get_conversation_summary(self, context_id: str) -> str:
        """Get formatted conversation summary."""
        messages = self.get_conversation(context_id)
        if not messages:
            return "No conversation history"
        
        summary = "Conversation history:\n"
        for msg in messages[-5:]:  # Last 5 messages
            summary += f"- {msg['role']}: {msg['content']}\n"
        
        return summary


class MultiturnAgent:
    """Agent demonstrating multiturn conversation patterns."""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.waiting_for_info = {}  # Track what info we're waiting for per context
    
    async def stream(self, query: str, context_id: str):
        """Process query with conversation context awareness."""
        
        # Add user message to memory
        self.memory.add_message(context_id, "user", query)
        
        # Get conversation history
        history = self.memory.get_conversation(context_id)
        
        # Check if we're in middle of collecting information
        if context_id in self.waiting_for_info:
            yield await self._handle_pending_request(query, context_id, history)
            return
        
        # Process new request
        async for response in self._process_new_request(query, context_id, history):
            yield response
    
    async def _process_new_request(self, query: str, context_id: str, history: List[Dict[str, str]]):
        """Process a new conversation request."""
        
        query_lower = query.lower()
        
        # Check for different conversation patterns
        if "weather" in query_lower:
            # Need location information
            if not self._has_location_info(history):
                self.waiting_for_info[context_id] = "location"
                yield {
                    "content": "I'd be happy to help you with weather information! What city or location would you like weather for?",
                    "is_task_complete": False,
                    "require_user_input": True
                }
                return
            else:
                location = self._extract_location(history)
                yield {"content": f"Looking up weather for {location}...", "is_task_complete": False, "require_user_input": False}
                yield {"content": f"The weather in {location} is sunny and 72°F. Perfect day!", "is_task_complete": True, "require_user_input": False}
        
        elif "favorite" in query_lower and "color" in query_lower:
            # Personal preference question
            yield {"content": "Analyzing your question...", "is_task_complete": False, "require_user_input": False}
            
            # Check if user has mentioned colors before
            color_mentioned = self._extract_mentioned_color(history)
            if color_mentioned:
                yield {"content": f"Based on our conversation, you seem to like {color_mentioned}! Is that still your favorite?", "is_task_complete": False, "require_user_input": True}
                self.waiting_for_info[context_id] = "color_confirmation"
            else:
                yield {"content": "What's your favorite color? I'd love to know more about your preferences!", "is_task_complete": False, "require_user_input": True}
                self.waiting_for_info[context_id] = "favorite_color"
        
        elif "hello" in query_lower or "hi" in query_lower:
            # Greeting with context awareness
            if len(history) > 1:
                yield {"content": "Nice to chat with you again! How can I help you today?", "is_task_complete": True, "require_user_input": False}
            else:
                yield {"content": "Hello! I'm a conversational agent that remembers our chat. How can I help you?", "is_task_complete": True, "require_user_input": False}
        
        else:
            # General response with context
            conversation_context = f"Based on our conversation: {self.memory.get_conversation_summary(context_id)}"
            yield {"content": "Processing your request...", "is_task_complete": False, "require_user_input": False}
            yield {"content": f"I understand you're asking about: {query}\n\n{conversation_context}", "is_task_complete": True, "require_user_input": False}
    
    async def _handle_pending_request(self, query: str, context_id: str, history: List[Dict[str, str]]):
        """Handle responses when waiting for specific information."""
        
        waiting_for = self.waiting_for_info[context_id]
        
        if waiting_for == "location":
            # User provided location for weather
            self.memory.add_message(context_id, "assistant", f"Got location: {query}")
            del self.waiting_for_info[context_id]
            return {"content": f"Perfect! The weather in {query} is sunny and 75°F with light clouds. Great day to be outside!", "is_task_complete": True, "require_user_input": False}
        
        elif waiting_for == "favorite_color":
            # User provided favorite color
            self.memory.add_message(context_id, "assistant", f"Favorite color: {query}")
            del self.waiting_for_info[context_id]
            return {"content": f"Great choice! {query.title()} is a beautiful color. I'll remember that for our future conversations!", "is_task_complete": True, "require_user_input": False}
        
        elif waiting_for == "color_confirmation":
            # User confirmed/changed color preference
            del self.waiting_for_info[context_id]
            if "yes" in query.lower() or "still" in query.lower():
                return {"content": "Awesome! I'll keep that noted. Colors can say a lot about personality!", "is_task_complete": True, "require_user_input": False}
            else:
                return {"content": f"Thanks for the update! {query.title()} is your new favorite. I've updated my memory!", "is_task_complete": True, "require_user_input": False}
        
        # Default fallback
        del self.waiting_for_info[context_id]
        return {"content": f"Thank you for the information: {query}. How else can I help?", "is_task_complete": True, "require_user_input": False}
    
    def _has_location_info(self, history: List[Dict[str, str]]) -> bool:
        """Check if location was mentioned in conversation."""
        for msg in history:
            if any(city in msg['content'].lower() for city in ['new york', 'london', 'tokyo', 'paris', 'city']):
                return True
        return False
    
    def _extract_location(self, history: List[Dict[str, str]]) -> str:
        """Extract location from conversation history."""
        for msg in history:
            content = msg['content'].lower()
            if 'new york' in content:
                return 'New York'
            elif 'london' in content:
                return 'London'
            elif 'tokyo' in content:
                return 'Tokyo'
            elif 'paris' in content:
                return 'Paris'
        return "your location"
    
    def _extract_mentioned_color(self, history: List[Dict[str, str]]) -> str:
        """Extract any color mentioned in conversation."""
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'black', 'white']
        for msg in history:
            content = msg['content'].lower()
            for color in colors:
                if color in content:
                    return color
        return ""


class MultiturnAgentExecutor(AgentExecutor):
    """Agent Executor implementing official multiturn conversation patterns."""

    def __init__(self):
        self.agent = MultiturnAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute agent with multiturn conversation support."""
        
        # Get user input and context
        query = context.get_user_input()
        task = context.current_task

        # Create new task if needed (new conversation)
        if not task:
            task = new_task(context.message)  # type: ignore
            await event_queue.enqueue_event(task)

        # Create TaskUpdater for managing conversation state
        updater = TaskUpdater(event_queue, task.id, task.contextId)

        try:
            # Process with conversation memory
            async for item in self.agent.stream(query, task.contextId):
                is_task_complete = item['is_task_complete']
                require_user_input = item['require_user_input']

                if not is_task_complete and not require_user_input:
                    # Send interim status update
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            item['content'],
                            task.contextId,
                            task.id,
                        ),
                    )

                elif require_user_input:
                    # Request more input (multiturn conversation)
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
                    # Task complete - add final response
                    await updater.add_artifact(
                        [Part(root=TextPart(text=item['content']))],
                        name='conversation_response',
                    )
                    await updater.complete()
                    break

        except Exception as e:
            logger.error(f'An error occurred in conversation: {e}')
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    f"Sorry, I encountered an error: {str(e)}",
                    task.contextId,
                    task.id,
                ),
                final=True,
            )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel conversation."""
        task = context.current_task
        if task:
            updater = TaskUpdater(event_queue, task.id, task.contextId)
            await updater.update_status(
                TaskState.cancelled,
                new_agent_text_message(
                    "Conversation cancelled",
                    task.contextId,
                    task.id,
                ),
                final=True,
            )
```

### 3. Multiturn Server

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
from conversation_agent import MultiturnAgentExecutor

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # Define conversation skills
    conversation_skill = AgentSkill(
        id='multiturn_conversation',
        name='Multiturn Conversation Handler',
        description='Maintains context and memory across conversation turns',
        tags=['conversation', 'memory', 'context', 'multiturn'],
        examples=[
            'What is the weather?',
            'What is your favorite color?', 
            'Hello, how are you?',
            'Tell me about yourself'
        ],
    )

    # Create agent card with conversation capabilities
    agent_card = AgentCard(
        name='Multiturn Conversation Agent',
        description='Demonstrates A2A multiturn conversations with memory and context management',
        url='http://localhost:11000/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=True,
            conversationMemory=True,  # Conversation memory capability
        ),
        skills=[conversation_skill],
    )
    
    # Setup A2A server with conversation support
    httpx_client = httpx.AsyncClient()
    request_handler = DefaultRequestHandler(
        agent_executor=MultiturnAgentExecutor(),
        task_store=InMemoryTaskStore(),
        push_notifier=InMemoryPushNotifier(httpx_client),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    print("💬 Starting Multiturn Conversation Agent...")
    print("🧠 Memory and context management enabled!")
    print("📋 Agent Discovery: http://localhost:11000/.well-known/agent.json")
    print("💬 A2A Endpoint: http://localhost:11000/")
    uvicorn.run(server.build(), host='0.0.0.0', port=11000)
```

### 4. Multiturn Test Client

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


async def test_multiturn_conversation() -> None:
    """Test complete multiturn conversation flow."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = 'http://localhost:11000'

    async with httpx.AsyncClient() as httpx_client:
        # Connect to conversation agent
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )
        
        logger.info(f'Connecting to conversation agent at: {base_url}')
        agent_card: AgentCard = await resolver.get_agent_card()
        
        # Create client
        client = A2AClient(
            httpx_client=httpx_client, 
            agent_card=agent_card
        )

        print("\n💬 Starting multiturn conversation...")
        print("=" * 70)

        # Conversation flow demonstration
        conversation_messages = [
            "Hello! How are you?",
            "What's the weather like?",
            "New York",  # Response to weather location request
            "What's your favorite color?",
            "Blue",  # Response to color question
            "Yes, blue is still my favorite",  # Response to confirmation
            "Tell me something about our conversation",
        ]

        context_id = None
        task_id = None

        for i, message_text in enumerate(conversation_messages):
            print(f"\n👤 User (Turn {i+1}): {message_text}")
            
            # Build message payload
            message_payload: dict[str, Any] = {
                'message': {
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': message_text}],
                    'messageId': uuid4().hex,
                },
            }
            
            # Add context for continuing conversation
            if context_id and task_id:
                message_payload['message']['contextId'] = context_id
                message_payload['message']['taskId'] = task_id

            request = SendMessageRequest(
                id=str(uuid4()), 
                params=MessageSendParams(**message_payload)
            )

            # Send message and get response
            response = await client.send_message(request)
            result = response.result

            # Extract context for next message
            if hasattr(result, 'contextId'):
                context_id = result.contextId
            if hasattr(result, 'id'):
                task_id = result.id

            # Display response
            status = result.status.state
            print(f"🤖 Agent (Status: {status}):")

            # Show agent response content
            if status == "input-required" and hasattr(result.status, 'message'):
                # Agent is asking for more input
                agent_msg = result.status.message.parts[0].text
                print(f"   {agent_msg}")
                print(f"   [Waiting for user input...]")
                
            elif hasattr(result, 'artifacts') and result.artifacts:
                # Agent provided final response
                agent_response = result.artifacts[0].parts[0].text
                print(f"   {agent_response}")
                
            elif hasattr(result, 'history') and result.history:
                # Check history for agent messages
                for hist_msg in result.history:
                    if hist_msg.role == 'agent':
                        print(f"   {hist_msg.parts[0].text}")

            # Small delay between turns
            await asyncio.sleep(1.0)

        print("\n" + "=" * 70)
        print("✅ Multiturn conversation complete!")
        
        # Show final conversation history
        if hasattr(result, 'history') and result.history:
            print(f"\n📜 Final conversation history ({len(result.history)} messages):")
            for i, hist_msg in enumerate(result.history[-6:], 1):  # Last 6 messages
                role_icon = "👤" if hist_msg.role == "user" else "🤖"
                print(f"   {i}. {role_icon} {hist_msg.parts[0].text[:60]}...")


async def test_context_persistence() -> None:
    """Test that context persists across separate requests."""
    
    print("\n🔄 Testing context persistence...")
    
    base_url = 'http://localhost:11000'

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

        # First interaction
        message1 = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(message={
                'role': 'user',
                'parts': [{'kind': 'text', 'text': 'Hi, I like red cars'}],
                'messageId': uuid4().hex,
            })
        )

        response1 = await client.send_message(message1)
        context_id = response1.result.contextId
        
        print(f"🔗 Established context: {context_id[:8]}...")

        # Second interaction using same context
        message2 = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(message={
                'role': 'user',
                'parts': [{'kind': 'text', 'text': 'What did I just tell you?'}],
                'messageId': uuid4().hex,
                'contextId': context_id,
                'taskId': response1.result.id,
            })
        )

        response2 = await client.send_message(message2)
        
        # Check if agent remembers
        if hasattr(response2.result, 'artifacts') and response2.result.artifacts:
            agent_response = response2.result.artifacts[0].parts[0].text
            if 'red' in agent_response.lower() or 'car' in agent_response.lower():
                print("✅ Context persistence working! Agent remembered previous message.")
            else:
                print("❌ Context not persisted properly.")
            print(f"   Agent response: {agent_response}")


if __name__ == '__main__':
    async def main():
        await test_multiturn_conversation()
        await test_context_persistence()
    
    asyncio.run(main())
```

### 5. Project Configuration

**File**: `pyproject.toml`

```toml
[project]
name = "a2a07-code"
version = "0.1.0"
description = "A2A Multiturn Conversations with Memory"
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

### 1. Start the Conversation Server
```bash
cd a2a07_code
uv run __main__.py
```

### 2. Test Agent Discovery
```bash
# Check conversation capabilities
curl http://localhost:11000/.well-known/agent.json | jq '.capabilities'
```

### 3. Run Multiturn Test
```bash
cd a2a07_code
uv run test_client.py
```

### 4. Manual Conversation Test
```bash
# Start conversation
curl -X POST http://localhost:11000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "What is the weather?"}],
        "messageId": "msg1"
      }
    },
    "id": "req1"
  }' | jq '.result.contextId'

# Continue conversation (use contextId from above)
curl -X POST http://localhost:11000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "London"}],
        "messageId": "msg2",
        "contextId": "CONTEXT_ID_FROM_ABOVE",
        "taskId": "TASK_ID_FROM_ABOVE"
      }
    },
    "id": "req2"
  }'
```

## 📊 Expected Output

### Multiturn Conversation Flow
```
💬 Starting multiturn conversation...
======================================================================

👤 User (Turn 1): Hello! How are you?
🤖 Agent (Status: completed):
   Hello! I'm a conversational agent that remembers our chat. How can I help you?

👤 User (Turn 2): What's the weather like?
🤖 Agent (Status: input-required):
   I'd be happy to help you with weather information! What city or location would you like weather for?
   [Waiting for user input...]

👤 User (Turn 3): New York
🤖 Agent (Status: completed):
   Perfect! The weather in New York is sunny and 75°F with light clouds. Great day to be outside!

👤 User (Turn 4): What's your favorite color?
🤖 Agent (Status: input-required):
   What's your favorite color? I'd love to know more about your preferences!
   [Waiting for user input...]

👤 User (Turn 5): Blue
🤖 Agent (Status: completed):
   Great choice! Blue is a beautiful color. I'll remember that for our future conversations!

👤 User (Turn 6): Yes, blue is still my favorite
🤖 Agent (Status: completed):
   Awesome! I'll keep that noted. Colors can say a lot about personality!

👤 User (Turn 7): Tell me something about our conversation
🤖 Agent (Status: completed):
   I understand you're asking about: Tell me something about our conversation
   
   Based on our conversation: Conversation history:
   - user: Hello! How are you?
   - user: What's the weather like?
   - user: New York
   - user: What's your favorite color?
   - user: Blue

======================================================================
✅ Multiturn conversation complete!

🔄 Testing context persistence...
🔗 Established context: 12ab34cd...
✅ Context persistence working! Agent remembered previous message.
   Agent response: Based on our conversation, you mentioned that you like red cars!
```

## 🔍 Key A2A Multiturn Concepts

### Official Multiturn Pattern
- **contextId**: Unique identifier that links messages in same conversation
- **taskId**: Links messages within same task/conversation turn
- **input-required state**: Pauses conversation to collect more input
- **Conversation memory**: Agent maintains state across turns
- **History tracking**: Full conversation preserved in response

### Context Management
```python
# Check for existing task/context
task = context.current_task

# Create new context if none exists
if not task:
    task = new_task(context.message)
    await event_queue.enqueue_event(task)

# Use TaskUpdater with same contextId
updater = TaskUpdater(event_queue, task.id, task.contextId)
```

### State Flow for Multiturn
```python
# Request more input
await updater.update_status(
    TaskState.input_required,
    new_agent_text_message("Please provide more details..."),
    final=True,  # Pause here for user input
)

# Continue in next message with same contextId
```

### Memory Implementation
- **Session-based**: Memory tied to contextId
- **Structured storage**: Role, content, timestamp tracking
- **History access**: Previous messages inform current response
- **State persistence**: Agent remembers what it's waiting for

## ✅ Success Criteria

- ✅ UV project created with A2A SDK dependencies
- ✅ Agent maintains conversation memory across turns
- ✅ contextId properly links related messages
- ✅ input-required state works for interactive dialogues
- ✅ Conversation history persists and influences responses
- ✅ Multiple conversation threads can run simultaneously
- ✅ Context awareness improves response quality
- ✅ Official A2A multiturn patterns implemented correctly

## 🎯 Next Step

Ready for [Step 08: Production Ready](../08_production_ready/) - Prepare for deployment!

## 📖 Official Reference

This step implements patterns from: [A2A LangGraph Multiturn Example](https://github.com/google-a2a/a2a-samples/tree/main/samples/python/agents/langgraph)

**🎉 Congratulations! You've mastered A2A multiturn conversations with memory and context management!** 