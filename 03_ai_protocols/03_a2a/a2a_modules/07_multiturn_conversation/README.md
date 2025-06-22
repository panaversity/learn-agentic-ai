# Step 07: Multiturn Conversation 💬

**Conversational AI with context - Task management and conversation history**

> **Goal**: Implement multiturn conversations with context retention using A2A task management and conversation history.

## 🎯 What You'll Learn

- Multiturn conversation patterns with A2A
- Task lifecycle management (create, update, complete)
- Conversation context and history retention
- Task-based conversation state management
- Memory patterns for conversational agents
- Foundation for complex conversational AI

## 📋 Prerequisites

- Completed [Step 06: Message Streaming](../06_message_streaming/)
- Understanding of A2A tasks and streaming
- UV package manager installed
- Basic understanding of conversation state management

## 🚀 Implementation

### 1. Create UV Project
```bash
cd 07_multiturn_conversation
uv init a2a07_code
cd a2a07_code
uv add httpx a2a-sdk uvicorn
```

### 2. Conversational Agent Implementation

**File**: `conversation_agent.py`

```python
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message


@dataclass
class ConversationTurn:
    """Represents a single turn in conversation."""
    role: str  # 'user' or 'agent'
    message: str
    timestamp: str
    turn_number: int


class ConversationMemory:
    """Manages conversation history and context."""
    
    def __init__(self):
        self.conversations: Dict[str, List[ConversationTurn]] = {}
        self.turn_counters: Dict[str, int] = {}
    
    def add_turn(self, task_id: str, role: str, message: str) -> None:
        """Add a conversation turn."""
        if task_id not in self.conversations:
            self.conversations[task_id] = []
            self.turn_counters[task_id] = 0
        
        self.turn_counters[task_id] += 1
        turn = ConversationTurn(
            role=role,
            message=message,
            timestamp="now",  # In real app, use proper timestamp
            turn_number=self.turn_counters[task_id]
        )
        self.conversations[task_id].append(turn)
    
    def get_conversation_history(self, task_id: str) -> List[ConversationTurn]:
        """Get full conversation history."""
        return self.conversations.get(task_id, [])
    
    def get_recent_context(self, task_id: str, num_turns: int = 5) -> str:
        """Get recent conversation context as formatted string."""
        history = self.get_conversation_history(task_id)
        recent = history[-num_turns:] if len(history) > num_turns else history
        
        context_lines = []
        for turn in recent:
            context_lines.append(f"{turn.role}: {turn.message}")
        
        return "\n".join(context_lines)


class ConversationalAgent:
    """Agent that maintains conversation context."""

    def __init__(self):
        self.memory = ConversationMemory()
        self.personality = {
            "name": "Alex",
            "traits": ["helpful", "curious", "remembers context"],
            "greeting": "Hi! I'm Alex, your conversational AI assistant."
        }

    async def process_message(self, task_id: str, user_message: str) -> str:
        """Process user message with conversation context."""
        
        # Add user message to conversation history
        self.memory.add_turn(task_id, "user", user_message)
        
        # Get conversation context
        context = self.memory.get_recent_context(task_id, num_turns=10)
        conversation_history = self.memory.get_conversation_history(task_id)
        turn_count = len(conversation_history)
        
        # Generate contextual response
        if turn_count == 1:
            # First message - introduce yourself
            response = f"{self.personality['greeting']} How can I help you today?"
        elif "remember" in user_message.lower():
            # User asking about memory
            if turn_count > 2:
                response = f"Yes, I remember our conversation! We've exchanged {turn_count} messages. Here's our recent context:\n\n{context}"
            else:
                response = "We just started talking, but I'm already keeping track of our conversation!"
        elif "who are you" in user_message.lower() or "what's your name" in user_message.lower():
            # Identity question with context
            response = f"I'm {self.personality['name']}, and we've been chatting for {turn_count} turns now. I'm {', '.join(self.personality['traits'])}."
        elif user_message.lower() in ["bye", "goodbye", "see you"]:
            # Farewell with context
            response = f"Goodbye! It was great chatting with you for {turn_count} turns. Feel free to continue our conversation anytime!"
        else:
            # General response with context awareness
            recent_topics = [turn.message for turn in conversation_history[-3:] if turn.role == "user"]
            response = f"I understand you're saying: '{user_message}'. "
            
            if len(recent_topics) > 1:
                response += f"Following up on our discussion about: {', '.join(recent_topics[-2:-1])}. "
            
            response += "What would you like to explore further?"
        
        # Add agent response to conversation history
        self.memory.add_turn(task_id, "agent", response)
        
        return response


class ConversationalAgentExecutor(AgentExecutor):
    """Agent Executor for multiturn conversations."""

    def __init__(self):
        self.agent = ConversationalAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # Extract user message
        user_message = "Hello"
        if context.message and context.message.parts:
            for part in context.message.parts:
                if part.kind == "text":
                    user_message = part.text
                    break

        # Use task ID for conversation continuity
        task_id = context.task_id or "default-conversation"
        
        # Process message with conversation context
        response = await self.agent.process_message(task_id, user_message)
        
        # Stream response for better UX
        words = response.split()
        for i, word in enumerate(words):
            if i == 0:
                await event_queue.enqueue_event(new_agent_text_message(word))
            else:
                await event_queue.enqueue_event(new_agent_text_message(f" {word}"))
            await asyncio.sleep(0.1)  # Simulate natural typing speed
        
        # Add conversation metadata
        conversation_history = self.agent.memory.get_conversation_history(task_id)
        metadata_msg = f"\n\n💭 [Turn {len(conversation_history)//2} | Context: {len(conversation_history)} messages]"
        await event_queue.enqueue_event(new_agent_text_message(metadata_msg))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        await event_queue.enqueue_event(new_agent_text_message("❌ Conversation cancelled"))
```

### 3. Conversation Server

**File**: `conversation_server.py`

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
from conversation_agent import ConversationalAgentExecutor


if __name__ == '__main__':
    # Define conversation skills
    conversation_skill = AgentSkill(
        id='multiturn_conversation',
        name='Multiturn Conversation',
        description='Engage in contextual conversations with memory of previous exchanges',
        tags=['conversation', 'context', 'memory', 'multiturn'],
        examples=[
            'Tell me about yourself',
            'Do you remember what we talked about?',
            'Let\'s continue our conversation'
        ],
    )
    
    memory_skill = AgentSkill(
        id='conversation_memory',
        name='Conversation Memory',
        description='Remember and reference previous parts of our conversation',
        tags=['memory', 'context', 'history'],
        examples=[
            'What did I just say?',
            'Summarize our conversation',
            'Remember this for later'
        ],
    )

    # Create conversational agent card
    public_agent_card = AgentCard(
        name='Conversational AI Agent',
        description='AI agent that maintains conversation context and memory across multiple turns',
        url='http://localhost:8002/',
        version='1.0.0',
        provider=AgentProvider(
            organization='A2A Conversation Lab',
            url='http://localhost:8002/',
        ),
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False,
            stateTransitionHistory=True,  # Enable state transition history
        ),
        skills=[conversation_skill, memory_skill],
    )
    
    # Setup A2A server with task management
    request_handler = DefaultRequestHandler(
        agent_executor=ConversationalAgentExecutor(),
        task_store=InMemoryTaskStore(),  # Stores conversation tasks
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler
    )

    print("💬 Starting Conversational AI Agent...")
    print("🧠 Memory and context enabled!")
    print("📝 Task-based conversation management active!")
    uvicorn.run(server.build(), host='0.0.0.0', port=8002)
```

## 🧪 Testing

### 1. Start the Conversation Server
```bash
cd a2a07_code
uv run conversation_server.py
```

### 2. Test Conversation Continuity
```bash
# Start a conversation
TASK_ID="conv-$(date +%s)"

# First message
curl -X POST http://localhost:8002/a2a \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"message/send\",
    \"params\": {
      \"message\": {
        \"role\": \"user\",
        \"parts\": [{\"kind\": \"text\", \"text\": \"Hello, who are you?\"}],
        \"messageId\": \"msg-1\"
      }
    },
    \"id\": \"$TASK_ID\"
  }" | jq '.result.task.artifacts[].text'

# Continue conversation with same task ID
curl -X POST http://localhost:8002/a2a \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"message/send\",
    \"params\": {
      \"message\": {
        \"role\": \"user\",
        \"parts\": [{\"kind\": \"text\", \"text\": \"Do you remember what I just asked?\"}],
        \"messageId\": \"msg-2\"
      }
    },
    \"id\": \"$TASK_ID\"
  }" | jq '.result.task.artifacts[].text'
```

### 3. Test Memory Features
```bash
# Test memory recall
curl -X POST http://localhost:8002/a2a \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"message/send\",
    \"params\": {
      \"message\": {
        \"role\": \"user\",
        \"parts\": [{\"kind\": \"text\", \"text\": \"What do you remember about our conversation?\"}],
        \"messageId\": \"msg-3\"
      }
    },
    \"id\": \"$TASK_ID\"
  }" | jq '.result.task.artifacts[].text'
```

## 📊 Expected Output

### Conversation Flow Example
```
First Message:
👤 "Hello, who are you?"
🤖 "Hi! I'm Alex, your conversational AI assistant. How can I help you today?"
💭 [Turn 1 | Context: 2 messages]

Second Message:
👤 "Do you remember what I just asked?"
🤖 "Yes, I remember our conversation! We've exchanged 4 messages. Here's our recent context:

user: Hello, who are you?
agent: Hi! I'm Alex, your conversational AI assistant. How can I help you today?
user: Do you remember what I just asked?"
💭 [Turn 2 | Context: 4 messages]

Third Message:
👤 "What's your personality like?"
🤖 "I understand you're saying: 'What's your personality like?'. Following up on our discussion about: Do you remember what I just asked?. What would you like to explore further?"
💭 [Turn 3 | Context: 6 messages]
```

## 🔍 Key A2A Conversation Concepts

### Task-Based Conversation Management
- **Task ID continuity**: Same task ID maintains conversation context
- **Task lifecycle**: Create → Update → Complete for each conversation
- **State persistence**: InMemoryTaskStore maintains conversation state
- **Context retention**: Conversation history tied to task ID

### Conversation Memory Patterns
- **Turn tracking**: Number and sequence of conversation exchanges
- **Context windowing**: Recent N turns for immediate context
- **History management**: Full conversation history for reference
- **Metadata tracking**: Timestamps, roles, turn numbers

### A2A Multiturn Features
- **stateTransitionHistory**: Capability flag for conversation tracking
- **Streaming responses**: Real-time conversation feel
- **Message parts**: Structured message format for rich content
- **Role-based messaging**: Clear user/agent distinction

## ✅ Success Criteria

- ✅ UV project created with conversation dependencies
- ✅ Agent maintains conversation context across multiple turns
- ✅ Task ID provides conversation continuity
- ✅ Memory system tracks conversation history
- ✅ Streaming responses create natural conversation flow
- ✅ Agent demonstrates context awareness in responses
- ✅ Conversation metadata properly tracked
- ✅ Multiple conversation threads can be managed

## 🎯 Next Step

Ready for [Step 08: Push Notifications](../08_push_notifications/) - Learn about disconnected agent communication!

## 📖 Official Reference

This step extends: [A2A Task Management](https://google-a2a.github.io/A2A/latest/specification/#task-management)

**🎉 Congratulations! You've built a conversational AI agent with memory and context using A2A!** 