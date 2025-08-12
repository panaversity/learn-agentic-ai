# Step 7: Multi-Turn Conversations & Context Persistence

**What We'll Actually Build**: A2A agents that maintain conversation context across multiple interactions using `contextId` and `referenceTaskIds`.

## 🎯 What You'll Learn by Building

Building on Step 4's streaming foundation, we'll create **conversation-aware agents**:

1. **Context Persistence Agent**: Maintains conversation history across task interactions
2. **Task Referencing Agent**: Links new tasks to previous work using `referenceTaskIds`
3. **Input-Required State Agent**: Handles clarifying questions with user input prompts

**Learning Method**: Build, run, test - conversational A2A agents!

## 🔍 Understanding Multi-Turn Conversations

### Why Context Persistence?

In Step 4, you learned streaming for individual tasks. But real conversations need:

- **Memory**: "Remember what I said about the red sailboat"
- **Context**: "Make it bigger" (referring to previous task result)
- **Clarification**: "What style do you prefer?" (agent asking follow-up questions)

**Solution**: A2A's `contextId` persists across tasks, enabling true conversational agents!

### A2A Multi-Turn Flow

```
1. User: "Generate image of sailboat" 
   → Task 1 (contextId: "conv-123")
2. User: "Make the sailboat red" 
   → Task 2 (contextId: "conv-123", referenceTaskIds: ["task-1"])
3. Agent: "What shade of red?" 
   → Task 2 enters input-required state
4. User: "Bright red" 
   → Task 2 continues with user input
5. User: "Add clouds too"
   → Task 3 (contextId: "conv-123", referenceTaskIds: ["task-1", "task-2"])
```

## 🛠️ Build 1: Context Persistence Agent

Let's build an agent that remembers conversation history:

### Create `conversation_agent.py`

```python
import asyncio
import json
from datetime import datetime
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.types import (
    AgentCard, AgentCapabilities, Part, TextPart, TaskState,
    Message, Task, UserInputPrompt
)

class ConversationMemory:
    """Store conversation history by contextId."""
    def __init__(self):
        self.contexts = {}  # contextId -> list of messages
        self.task_results = {}  # taskId -> result summary
    
    def add_message(self, context_id: str, role: str, text: str, task_id: str = None):
        if context_id not in self.contexts:
            self.contexts[context_id] = []
        
        message = {
            "role": role,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "taskId": task_id
        }
        
        self.contexts[context_id].append(message)
        return message
    
    def add_task_result(self, task_id: str, result: str):
        """Store task results for reference in future conversations."""
        self.task_results[task_id] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_history(self, context_id: str):
        return self.contexts.get(context_id, [])
    
    def get_task_result(self, task_id: str):
        return self.task_results.get(task_id)
    
    def get_referenced_results(self, reference_task_ids: list):
        """Get results from referenced tasks."""
        results = {}
        for task_id in reference_task_ids:
            if task_id in self.task_results:
                results[task_id] = self.task_results[task_id]
        return results

class ConversationExecutor(AgentExecutor):
    """Demonstrates multi-turn conversations with context persistence."""
    
    def __init__(self):
        self.memory = ConversationMemory()
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        
        try:
            # Initialize task
            if not context.current_task:
                await updater.submit()
            await updater.start_work()
            
            user_input = context.get_user_input()
            context_id = context.context_id
            task_id = context.task_id
            
            # Store user message in conversation history
            self.memory.add_message(context_id, "user", user_input, task_id)
            
            # Get conversation history
            history = self.memory.get_history(context_id)
            turn_number = len([msg for msg in history if msg["role"] == "user"])
            
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"💭 Processing turn {turn_number} in conversation..."))
                ])
            )
            
            # Get referenced task results if provided
            reference_task_ids = getattr(context, 'reference_task_ids', [])
            referenced_results = self.memory.get_referenced_results(reference_task_ids)
            
            # Handle different conversation scenarios
            if turn_number == 1:
                response = await self._handle_first_turn(user_input, updater)
            elif "remember" in user_input.lower() or "recall" in user_input.lower():
                response = await self._handle_memory_request(history, updater)
            elif reference_task_ids:
                response = await self._handle_task_reference(user_input, referenced_results, updater)
            elif "?" in user_input and turn_number > 1:
                response = await self._handle_clarifying_question(user_input, history, updater)
            elif any(word in user_input.lower() for word in ["what", "how", "why", "explain"]):
                response = await self._handle_question_with_input_required(user_input, updater, context)
            else:
                response = await self._handle_contextual_turn(user_input, history, updater)
            
            # Store agent response and task result
            self.memory.add_message(context_id, "assistant", response, task_id)
            self.memory.add_task_result(task_id, response)
            
            # Stream final response
            await updater.add_artifact(
                [Part(root=TextPart(text=response))],
                name=f"conversation_turn_{turn_number}"
            )
            
            await updater.complete()
            
        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"❌ Conversation failed: {str(e)}"))
                ])
            )
    
    async def _handle_first_turn(self, user_input: str, updater: TaskUpdater):
        """Handle the first message in a conversation."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="👋 Starting new conversation..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        return f"Hello! I'm your conversation agent. You said: '{user_input}'\n\n" \
               f"I'll remember our conversation context. Try:\n" \
               f"• Ask me to remember what you said\n" \
               f"• Reference this response in your next message\n" \
               f"• Ask clarifying questions\n\n" \
               f"Started at: {datetime.now().isoformat()}"
    
    async def _handle_memory_request(self, history: list, updater: TaskUpdater):
        """Handle requests to recall conversation history."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="🧠 Recalling conversation history..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        user_messages = [msg for msg in history if msg["role"] == "user"]
        if len(user_messages) <= 1:
            return "This is our first exchange! Nothing to remember yet."
        
        recap = "📝 CONVERSATION HISTORY:\n\n"
        for i, msg in enumerate(user_messages[:-1], 1):  # Exclude current message
            timestamp = msg.get('timestamp', 'Unknown')
            recap += f"{i}. You said: \"{msg['text']}\"\n"
            recap += f"   Time: {timestamp}\n"
            recap += f"   Task: {msg.get('taskId', 'N/A')[:8]}...\n\n"
        
        recap += f"Total conversation turns: {len(user_messages)}"
        return recap
    
    async def _handle_task_reference(self, user_input: str, referenced_results: dict, updater: TaskUpdater):
        """Handle requests that reference previous tasks."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="🔗 Processing request with task references..."))
            ])
        )
        
        await asyncio.sleep(1.5)
        
        if not referenced_results:
            return f"I understand you want: '{user_input}'\n\n" \
                   f"However, I couldn't find the referenced previous tasks. " \
                   f"This might be a new conversation thread."
        
        response = f"🔗 BUILDING ON PREVIOUS WORK:\n\n"
        response += f"Your request: '{user_input}'\n\n"
        response += f"Referenced previous results:\n"
        
        for task_id, result_data in referenced_results.items():
            preview = result_data['result'][:100] + "..." if len(result_data['result']) > 100 else result_data['result']
            response += f"• Task {task_id[:8]}...: {preview}\n"
            response += f"  Completed: {result_data['timestamp']}\n\n"
        
        response += f"✅ I've incorporated the context from {len(referenced_results)} previous task(s) " \
                   f"to understand your request better!"
        
        return response
    
    async def _handle_clarifying_question(self, user_input: str, history: list, updater: TaskUpdater):
        """Handle clarifying questions based on conversation context."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="❓ Analyzing your question with conversation context..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        recent_context = history[-3:] if len(history) >= 3 else history
        context_summary = " → ".join([f"{msg['role']}: {msg['text'][:50]}..." for msg in recent_context])
        
        return f"❓ CLARIFYING QUESTION ANSWERED:\n\n" \
               f"Your question: '{user_input}'\n\n" \
               f"Based on our recent conversation:\n{context_summary}\n\n" \
               f"My answer: I understand you're asking about our previous discussion. " \
               f"Given the context of our {len(history)} message conversation, " \
               f"I can provide a more informed response that builds on what we've discussed."
    
    async def _handle_question_with_input_required(self, user_input: str, updater: TaskUpdater, context: RequestContext):
        """Demonstrate input-required state for follow-up questions."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="🤔 I need more information to answer properly..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        # Transition to input-required state
        await updater.update_status(
            TaskState.input_required,
            message=updater.new_agent_message([
                Part(root=TextPart(text="To give you the best answer, could you be more specific?"))
            ]),
            input_prompt=UserInputPrompt(
                prompt_text="What specific aspect would you like me to focus on?",
                input_types=["text/plain"]
            )
        )
        
        # In a real implementation, this would wait for UserInputEvent
        # For this demo, we'll simulate getting clarification
        await asyncio.sleep(2)
        
        return f"🤔 CLARIFICATION REQUESTED:\n\n" \
               f"Your question: '{user_input}'\n\n" \
               f"I transitioned to 'input-required' state to ask for clarification.\n" \
               f"In a real implementation, I would:\n" \
               f"1. Wait for your UserInputEvent response\n" \
               f"2. Continue processing with your additional context\n" \
               f"3. Provide a more targeted answer\n\n" \
               f"This demonstrates A2A's multi-turn conversation flow!"
    
    async def _handle_contextual_turn(self, user_input: str, history: list, updater: TaskUpdater):
        """Handle regular turns with conversation context."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="🎯 Using full conversation context..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        conversation_summary = f"We've had {len(history)} exchanges in this conversation."
        recent_topics = [msg['text'] for msg in history[-3:] if msg['role'] == 'user']
        
        return f"🎯 CONTEXTUAL RESPONSE:\n\n" \
               f"Your message: '{user_input}'\n\n" \
               f"Conversation context: {conversation_summary}\n" \
               f"Recent topics: {recent_topics}\n\n" \
               f"This response demonstrates how A2A agents can maintain context " \
               f"across multiple interactions using persistent contextId!\n\n" \
               f"Processed with full conversation awareness at: {datetime.now().isoformat()}"

# Agent Card with multi-turn conversation support
agent_card = AgentCard(
    name="Conversation Agent",
    description="Demonstrates A2A multi-turn conversations with context persistence",
    url="http://localhost:8001/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        state_transition_history=True  # Enable state tracking for conversations
    ),
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)

if __name__ == "__main__":
    request_handler = DefaultRequestHandler(
        agent_executor=ConversationExecutor(),
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )
    
    server = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )
    
    print("🚀 Starting Conversation Agent on port 8001...")
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8001")
    print("💭 Context Persistence: Enabled")
    print("🔗 Task References: Supported")
    
    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8001)
```

### Test Multi-Turn Conversations

Create `test_conversation.py`:

```python
import asyncio
import httpx
import json
from uuid import uuid4

class A2AConversationTester:
    """Test multi-turn conversations with persistent contextId."""
    
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.context_id = str(uuid4())  # Persistent conversation context
        self.task_history = []  # Track task IDs for referencing
        
    async def send_message(self, text: str, reference_task_ids=None):
        """Send a message in the ongoing conversation."""
        
        payload = {
            "jsonrpc": "2.0",
            "method": "message/stream",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": text}],
                    "messageId": str(uuid4()),
                    "kind": "message"
                },
                "contextId": self.context_id  # This maintains conversation context!
            },
            "id": str(uuid4())
        }
        
        # Add task references for follow-ups
        if reference_task_ids:
            payload["params"]["referenceTaskIds"] = reference_task_ids
        
        print(f"\n💬 User: {text}")
        print(f"🔗 Context: {self.context_id[:8]}...")
        if reference_task_ids:
            print(f"📋 References: {[tid[:8] + '...' for tid in reference_task_ids]}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.stream(
                "POST",
                self.base_url,
                json=payload,
                headers={"Accept": "text/event-stream"}
            )
            
            task_id = None
            async for chunk in response.aiter_text():
                if chunk.startswith("data: "):
                    try:
                        event_data = json.loads(chunk[6:])
                        result = event_data.get("result", {})
                        kind = result.get("kind")
                        
                        if kind == "task":
                            task_id = result.get("id")
                            print(f"📋 Created task: {task_id[:8]}...")
                            
                        elif kind == "status-update":
                            status = result.get("status", {})
                            state = status.get("state")
                            message = status.get("message", {})
                            
                            if message.get("parts"):
                                text = message["parts"][0].get("text", "")
                                print(f"  📊 [{state.upper()}]: {text}")
                            
                            if result.get("final"):
                                break
                                
                        elif kind == "artifact-update":
                            artifact = result.get("artifact", {})
                            if artifact.get("parts"):
                                content = artifact["parts"][0].get("text", "")
                                # Show preview of response
                                lines = content.split('\n')
                                preview = lines[0] if lines else content[:100]
                                print(f"🤖 Agent: {preview}")
                                if len(lines) > 1:
                                    print(f"         (+ {len(lines)-1} more lines)")
                                
                    except json.JSONDecodeError:
                        continue
            
            if task_id:
                self.task_history.append(task_id)
            return task_id

async def test_conversation_scenarios():
    """Test different multi-turn conversation scenarios."""
    
    print("🧪 Testing Multi-Turn A2A Conversations")
    print("=" * 50)
    
    tester = A2AConversationTester()
    
    # Scenario 1: Basic conversation flow
    print("\n🎯 Scenario 1: Basic Conversation Flow")
    task1 = await tester.send_message("Hello, I'm planning a project")
    await asyncio.sleep(1)
    
    task2 = await tester.send_message("What programming languages should I consider?")
    await asyncio.sleep(1)
    
    # Scenario 2: Memory recall
    print("\n🎯 Scenario 2: Memory Recall")
    task3 = await tester.send_message("Can you remember what I said earlier?")
    await asyncio.sleep(1)
    
    # Scenario 3: Task referencing
    print("\n🎯 Scenario 3: Task References")
    task4 = await tester.send_message("Build on my project idea", 
                                    reference_task_ids=[task1, task2])
    await asyncio.sleep(1)
    
    # Scenario 4: Clarifying question
    print("\n🎯 Scenario 4: Clarifying Questions")
    task5 = await tester.send_message("What's the best approach for this?")
    await asyncio.sleep(1)
    
    # Scenario 5: Input-required demonstration
    print("\n🎯 Scenario 5: Input-Required State")
    task6 = await tester.send_message("How should I implement the database layer?")
    await asyncio.sleep(1)
    
    # Scenario 6: Contextual follow-up
    print("\n🎯 Scenario 6: Contextual Follow-up")
    task7 = await tester.send_message("Thanks for all the help!")
    
    print(f"\n✅ Conversation completed with {len(tester.task_history)} tasks!")
    print(f"📋 Task IDs: {[t[:8] + '...' for t in tester.task_history]}")
    print(f"🔗 Persistent contextId: {tester.context_id[:8]}...")
    
    print("\n🎯 Key Features Demonstrated:")
    print("  • Persistent contextId across all interactions")
    print("  • Conversation memory and recall")
    print("  • Task referencing with referenceTaskIds")
    print("  • Input-required state transitions")
    print("  • Contextual response generation")

async def test_multiple_conversations():
    """Test multiple separate conversations."""
    
    print("\n\n🧪 Testing Multiple Separate Conversations")
    print("=" * 50)
    
    # Start two separate conversations
    conv1 = A2AConversationTester()
    conv2 = A2AConversationTester()
    
    print(f"🔗 Conversation 1 context: {conv1.context_id[:8]}...")
    print(f"🔗 Conversation 2 context: {conv2.context_id[:8]}...")
    
    # Conversation 1: Technical discussion
    print("\n💬 Conversation 1: Technical Discussion")
    await conv1.send_message("I need help with Python async programming")
    await conv1.send_message("What are the main concepts I should understand?")
    
    # Conversation 2: Project planning
    print("\n💬 Conversation 2: Project Planning")
    await conv2.send_message("I'm starting a new web application")
    await conv2.send_message("What technology stack would you recommend?")
    
    # Cross-reference test (should not have access to other conversation)
    print("\n🧪 Cross-Reference Test")
    await conv1.send_message("Remember what we discussed about web applications", 
                            reference_task_ids=conv2.task_history[-1:])
    
    print("\n✅ Multiple conversation test completed!")
    print("🎯 Key Learning: Each conversation maintains separate context!")

if __name__ == "__main__":
    asyncio.run(test_conversation_scenarios())
    
    user_input = input("\n🤔 Test multiple conversations? (y/n): ")
    if user_input.lower() == 'y':
        asyncio.run(test_multiple_conversations())
```

### Run Multi-Turn Conversation Tests

1. **Start conversation agent**: `python conversation_agent.py` (port 8001)
2. **Run conversation tests**: `python test_conversation.py`
3. **Try different conversation flows** to see context persistence in action!

**🎯 Key Learning**: The `contextId` enables true conversational AI - agents remember what you've discussed and can reference previous work!

## 🛠️ Build 2: Advanced Conversation Features

Now let's implement more sophisticated conversation patterns:

### Create `advanced_conversation_agent.py`

```python
import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.types import (
    AgentCard, AgentCapabilities, Part, TextPart, TaskState,
    UserInputPrompt
)

class AdvancedConversationMemory:
    """Enhanced conversation memory with topic tracking and sentiment."""
    
    def __init__(self):
        self.contexts = {}  # contextId -> conversation data
        self.task_artifacts = {}  # taskId -> artifacts
        self.conversation_metadata = {}  # contextId -> metadata
    
    def start_conversation(self, context_id: str):
        """Initialize a new conversation context."""
        self.contexts[context_id] = {
            "messages": [],
            "topics": [],
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        self.conversation_metadata[context_id] = {
            "total_turns": 0,
            "user_questions": 0,
            "agent_clarifications": 0,
            "task_references": 0
        }
    
    def add_interaction(self, context_id: str, user_message: str, agent_response: str, 
                       task_id: str, reference_task_ids: list = None):
        """Add a complete interaction to conversation history."""
        
        if context_id not in self.contexts:
            self.start_conversation(context_id)
        
        interaction = {
            "taskId": task_id,
            "userMessage": user_message,
            "agentResponse": agent_response,
            "timestamp": datetime.now().isoformat(),
            "referenceTaskIds": reference_task_ids or []
        }
        
        self.contexts[context_id]["messages"].append(interaction)
        self.contexts[context_id]["last_activity"] = datetime.now().isoformat()
        
        # Update metadata
        metadata = self.conversation_metadata[context_id]
        metadata["total_turns"] += 1
        if "?" in user_message:
            metadata["user_questions"] += 1
        if reference_task_ids:
            metadata["task_references"] += 1
    
    def get_conversation_summary(self, context_id: str):
        """Get a summary of the conversation."""
        if context_id not in self.contexts:
            return "No conversation found."
        
        conv = self.contexts[context_id]
        metadata = self.conversation_metadata[context_id]
        
        duration = datetime.now() - datetime.fromisoformat(conv["start_time"])
        
        return {
            "totalTurns": metadata["total_turns"],
            "duration": str(duration),
            "userQuestions": metadata["user_questions"],
            "taskReferences": metadata["task_references"],
            "lastActivity": conv["last_activity"],
            "messageHistory": conv["messages"][-5:]  # Last 5 interactions
        }
    
    def detect_conversation_patterns(self, context_id: str):
        """Analyze conversation for patterns and insights."""
        if context_id not in self.contexts:
            return []
        
        messages = self.contexts[context_id]["messages"]
        patterns = []
        
        # Pattern: Rapid fire questions
        recent_questions = sum(1 for msg in messages[-3:] if "?" in msg["userMessage"])
        if recent_questions >= 2:
            patterns.append("rapid_questions")
        
        # Pattern: Task chaining
        task_refs = sum(1 for msg in messages if msg["referenceTaskIds"])
        if task_refs >= 2:
            patterns.append("task_chaining")
        
        # Pattern: Long conversation
        if len(messages) >= 5:
            patterns.append("extended_conversation")
        
        return patterns

class AdvancedConversationExecutor(AgentExecutor):
    """Advanced conversation agent with pattern recognition and smart responses."""
    
    def __init__(self):
        self.memory = AdvancedConversationMemory()
        self.active_input_prompts = {}  # Track input-required states
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        
        try:
            # Initialize task
            if not context.current_task:
                await updater.submit()
            await updater.start_work()
            
            user_input = context.get_user_input()
            context_id = context.context_id
            task_id = context.task_id
            reference_task_ids = getattr(context, 'reference_task_ids', [])
            
            # Analyze conversation context
            conversation_summary = self.memory.get_conversation_summary(context_id)
            patterns = self.memory.detect_conversation_patterns(context_id)
            
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"🧠 Analyzing conversation context (Turn {conversation_summary.get('totalTurns', 0) + 1})..."))
                ])
            )
            
            # Handle different conversation scenarios with pattern awareness
            if "summary" in user_input.lower() or "recap" in user_input.lower():
                response = await self._provide_conversation_summary(conversation_summary, patterns, updater)
            elif "clarify" in user_input.lower() or ("what" in user_input.lower() and "mean" in user_input.lower()):
                response = await self._handle_clarification_request(user_input, conversation_summary, updater)
            elif reference_task_ids:
                response = await self._handle_advanced_task_reference(user_input, reference_task_ids, updater)
            elif "rapid_questions" in patterns:
                response = await self._handle_rapid_questions(user_input, conversation_summary, updater)
            elif len(user_input.split()) < 3:  # Short input
                response = await self._handle_brief_input(user_input, conversation_summary, updater, context)
            else:
                response = await self._handle_standard_conversation(user_input, conversation_summary, patterns, updater)
            
            # Store the complete interaction
            self.memory.add_interaction(context_id, user_input, response, task_id, reference_task_ids)
            
            # Create artifact
            await updater.add_artifact(
                [Part(root=TextPart(text=response))],
                name=f"conversation_response_{len(conversation_summary.get('messageHistory', []))}"
            )
            
            await updater.complete()
            
        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"❌ Advanced conversation failed: {str(e)}"))
                ])
            )
    
    async def _provide_conversation_summary(self, summary: dict, patterns: list, updater: TaskUpdater):
        """Provide an intelligent conversation summary."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="📊 Generating conversation summary..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        response = "📊 CONVERSATION SUMMARY:\n\n"
        response += f"• Total turns: {summary.get('totalTurns', 0)}\n"
        response += f"• Duration: {summary.get('duration', 'Unknown')}\n"
        response += f"• Questions asked: {summary.get('userQuestions', 0)}\n"
        response += f"• Task references: {summary.get('taskReferences', 0)}\n\n"
        
        if patterns:
            response += f"🔍 CONVERSATION PATTERNS:\n"
            pattern_descriptions = {
                "rapid_questions": "You're asking many questions quickly - I'm ready to help!",
                "task_chaining": "You're building on previous work - great conversation flow!",
                "extended_conversation": "We're having a deep conversation - I'm tracking everything!"
            }
            for pattern in patterns:
                response += f"• {pattern_descriptions.get(pattern, pattern)}\n"
            response += "\n"
        
        recent_messages = summary.get('messageHistory', [])
        if recent_messages:
            response += f"💭 RECENT CONTEXT ({len(recent_messages)} latest):\n"
            for i, msg in enumerate(recent_messages, 1):
                user_preview = msg['userMessage'][:50] + "..." if len(msg['userMessage']) > 50 else msg['userMessage']
                response += f"{i}. You: {user_preview}\n"
            
        return response
    
    async def _handle_clarification_request(self, user_input: str, summary: dict, updater: TaskUpdater):
        """Handle requests for clarification of previous responses."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="🔍 Reviewing conversation for clarification..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        recent_messages = summary.get('messageHistory', [])
        if not recent_messages:
            return "I don't have previous context to clarify. Could you be more specific?"
        
        last_interaction = recent_messages[-1]
        
        return f"🔍 CLARIFICATION:\n\n" \
               f"Your question: '{user_input}'\n\n" \
               f"Looking at our last exchange:\n" \
               f"You said: \"{last_interaction['userMessage']}\"\n" \
               f"I responded with a message about: {last_interaction['agentResponse'][:100]}...\n\n" \
               f"What specific part would you like me to explain further? " \
               f"I can provide more detail on any aspect of my previous response."
    
    async def _handle_advanced_task_reference(self, user_input: str, reference_task_ids: list, updater: TaskUpdater):
        """Handle complex task references with multiple dependencies."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text=f"🔗 Processing request with {len(reference_task_ids)} task references..."))
            ])
        )
        
        await asyncio.sleep(1.5)
        
        return f"🔗 ADVANCED TASK REFERENCING:\n\n" \
               f"Your request: '{user_input}'\n\n" \
               f"I'm building on {len(reference_task_ids)} previous tasks:\n" \
               f"Referenced tasks: {[tid[:8] + '...' for tid in reference_task_ids]}\n\n" \
               f"This demonstrates A2A's powerful task chaining capability:\n" \
               f"• Each task can reference multiple previous tasks\n" \
               f"• Context flows seamlessly between related work\n" \
               f"• Complex workflows can be built incrementally\n\n" \
               f"✅ Processing complete with full task reference context!"
    
    async def _handle_rapid_questions(self, user_input: str, summary: dict, updater: TaskUpdater):
        """Handle users asking many questions quickly."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="⚡ Detected rapid questions - optimizing response..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        return f"⚡ RAPID Q&A MODE:\n\n" \
               f"I notice you're asking several questions quickly - that's great!\n\n" \
               f"Your current question: '{user_input}'\n" \
               f"Recent questions: {summary.get('userQuestions', 0)} in this conversation\n\n" \
               f"💡 Pro tip: I can handle complex, multi-part questions too. " \
               f"Feel free to ask everything at once, or continue with individual questions - " \
               f"I'm tracking the full context either way!\n\n" \
               f"✅ Ready for your next question!"
    
    async def _handle_brief_input(self, user_input: str, summary: dict, updater: TaskUpdater, context: RequestContext):
        """Handle very brief inputs that might need clarification."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="🤔 Brief input detected - checking if clarification needed..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        # Common brief inputs that are clear
        clear_brief_inputs = ["yes", "no", "ok", "thanks", "hello", "hi", "bye"]
        if user_input.lower() in clear_brief_inputs:
            return f"👍 Got it: '{user_input}'\n\n" \
                   f"Brief and clear! Sometimes the best communication is concise. " \
                   f"I understand what you mean in the context of our conversation."
        
        # For unclear brief inputs, transition to input-required
        await updater.update_status(
            TaskState.input_required,
            message=updater.new_agent_message([
                Part(root=TextPart(text="Could you provide a bit more detail?"))
            ]),
            input_prompt=UserInputPrompt(
                prompt_text=f"You said '{user_input}' - could you elaborate on what you'd like me to help with?",
                input_types=["text/plain"]
            )
        )
        
        await asyncio.sleep(1)  # Simulate waiting for input
        
        return f"🤔 BRIEF INPUT HANDLING:\n\n" \
               f"You said: '{user_input}'\n\n" \
               f"I transitioned to 'input-required' state because your input was brief " \
               f"and I wanted to make sure I understand what you need.\n\n" \
               f"In a real implementation, I would wait for your UserInputEvent with more details, " \
               f"then continue processing with the additional context."
    
    async def _handle_standard_conversation(self, user_input: str, summary: dict, patterns: list, updater: TaskUpdater):
        """Handle standard conversational inputs with pattern awareness."""
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="💬 Processing with full conversation intelligence..."))
            ])
        )
        
        await asyncio.sleep(1)
        
        pattern_insights = ""
        if patterns:
            pattern_insights = f"\n🔍 I notice we're in an {patterns[0].replace('_', ' ')} pattern. "
        
        return f"💬 INTELLIGENT CONVERSATION:\n\n" \
               f"Your message: '{user_input}'\n\n" \
               f"Conversation context:\n" \
               f"• Turn {summary.get('totalTurns', 0) + 1} of our discussion\n" \
               f"• Duration: {summary.get('duration', 'Just started')}\n" \
               f"• Questions you've asked: {summary.get('userQuestions', 0)}\n" \
               f"• Task references: {summary.get('taskReferences', 0)}{pattern_insights}\n\n" \
               f"This response is generated with full awareness of our conversation history, " \
               f"demonstrating A2A's powerful context persistence capabilities!\n\n" \
               f"✅ Response generated at: {datetime.now().isoformat()}"

# Advanced agent card
agent_card = AgentCard(
    name="Advanced Conversation Agent",
    description="Sophisticated A2A agent with pattern recognition and conversation intelligence",
    url="http://localhost:8002/",
    version="2.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        state_transition_history=True,
        multi_turn_conversations=True
    ),
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)

if __name__ == "__main__":
    request_handler = DefaultRequestHandler(
        agent_executor=AdvancedConversationExecutor(),
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )
    
    server = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )
    
    print("🚀 Starting Advanced Conversation Agent on port 8002...")
    print("🔗 Agent Card: http://localhost:8002/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8002")
    print("🧠 Pattern Recognition: Enabled")
    print("📊 Conversation Analytics: Active")
    print("🔍 Smart Clarification: Ready")
    
    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8002)
```

### Test Advanced Conversation Features

Create `test_advanced_conversation.py`:

```python
import asyncio
import httpx
import json
from uuid import uuid4

class AdvancedConversationTester:
    """Test advanced conversation features."""
    
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.context_id = str(uuid4())
        self.task_history = []
    
    async def send_message(self, text: str, reference_task_ids=None):
        """Send message to advanced conversation agent."""
        
        payload = {
            "jsonrpc": "2.0",
            "method": "message/stream",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": text}],
                    "messageId": str(uuid4()),
                    "kind": "message"
                },
                "contextId": self.context_id
            },
            "id": str(uuid4())
        }
        
        if reference_task_ids:
            payload["params"]["referenceTaskIds"] = reference_task_ids
        
        print(f"\n💬 User: {text}")
        if reference_task_ids:
            print(f"🔗 References: {[tid[:8] + '...' for tid in reference_task_ids]}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.stream(
                "POST",
                self.base_url,
                json=payload,
                headers={"Accept": "text/event-stream"}
            )
            
            task_id = None
            async for chunk in response.aiter_text():
                if chunk.startswith("data: "):
                    try:
                        event_data = json.loads(chunk[6:])
                        result = event_data.get("result", {})
                        kind = result.get("kind")
                        
                        if kind == "task":
                            task_id = result.get("id")
                            print(f"📋 Task: {task_id[:8]}...")
                            
                        elif kind == "status-update":
                            status = result.get("status", {})
                            state = status.get("state")
                            message = status.get("message", {})
                            
                            if message.get("parts"):
                                text = message["parts"][0].get("text", "")
                                print(f"  📊 [{state.upper()}]: {text}")
                            
                            if result.get("final"):
                                break
                                
                        elif kind == "artifact-update":
                            artifact = result.get("artifact", {})
                            if artifact.get("parts"):
                                content = artifact["parts"][0].get("text", "")
                                lines = content.split('\n')
                                print(f"🤖 Agent: {lines[0]}")
                                if len(lines) > 1:
                                    print(f"         (+ {len(lines)-1} more lines)")
                                
                    except json.JSONDecodeError:
                        continue
            
            if task_id:
                self.task_history.append(task_id)
            return task_id

async def test_advanced_patterns():
    """Test advanced conversation patterns."""
    
    print("🧪 Testing Advanced Conversation Patterns")
    print("=" * 50)
    
    tester = AdvancedConversationTester()
    
    # Pattern 1: Rapid questions
    print("\n🎯 Pattern 1: Rapid Questions")
    await tester.send_message("What is machine learning?")
    await asyncio.sleep(0.5)
    await tester.send_message("How does it work?")
    await asyncio.sleep(0.5)
    await tester.send_message("What are the types?")
    
    # Pattern 2: Task chaining
    print("\n🎯 Pattern 2: Complex Task Chaining")
    await tester.send_message("Let me build on all our previous discussion", 
                            reference_task_ids=tester.task_history)
    
    # Pattern 3: Brief inputs
    print("\n🎯 Pattern 3: Brief Input Handling")
    await tester.send_message("ok")
    await asyncio.sleep(0.5)
    await tester.send_message("help")
    
    # Pattern 4: Conversation summary
    print("\n🎯 Pattern 4: Conversation Summary")
    await tester.send_message("Can you give me a summary of our conversation?")
    
    # Pattern 5: Clarification request
    print("\n🎯 Pattern 5: Clarification Request")
    await tester.send_message("What did you mean by that last response?")
    
    print(f"\n✅ Advanced pattern testing completed!")
    print(f"📊 Total interactions: {len(tester.task_history)}")
    print(f"🧠 Context ID: {tester.context_id[:8]}...")

if __name__ == "__main__":
    asyncio.run(test_advanced_patterns())
```

### Run Advanced Conversation Tests

1. **Start advanced conversation agent**: `python advanced_conversation_agent.py` (port 8002)
2. **Run advanced tests**: `python test_advanced_conversation.py`
3. **Observe pattern recognition** and intelligent conversation handling!

**🎯 Key Learning**: Advanced A2A conversation agents can recognize patterns, provide intelligent summaries, and adapt their responses based on conversation context!

## 🎯 What You've Mastered

Congratulations! You've built sophisticated conversational A2A agents with:

### 📊 Complete Multi-Turn Capabilities

| Feature | Basic | Advanced |
|---------|-------|----------|
| **Context Persistence** | ✅ contextId | ✅ Rich conversation memory |
| **Task References** | ✅ referenceTaskIds | ✅ Multi-task chaining |
| **State Management** | ✅ input-required | ✅ Smart state transitions |
| **Pattern Recognition** | ❌ | ✅ Conversation analytics |
| **Response Intelligence** | ✅ Basic context | ✅ Adaptive responses |

### 🚀 Ready for Production Conversations

You now understand:
- **Persistent Context**: How `contextId` maintains conversation state
- **Task Relationships**: Using `referenceTaskIds` to build on previous work
- **Interactive States**: `input-required` for clarifying questions
- **Pattern Recognition**: Detecting and responding to conversation patterns
- **Memory Management**: Storing and retrieving conversation history

**🎯 Next**: Push notifications for long-running conversational tasks!
