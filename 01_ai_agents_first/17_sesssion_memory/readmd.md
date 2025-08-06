# 🧠 [Sessions](https://openai.github.io/openai-agents-python/sessions/): Making Agents Remember Conversations

## 🎯 What is Session Memory?

Think of **Session Memory** like **giving your agent a notebook** where it writes down everything you talk about. Without session memory, it's like talking to someone with severe amnesia - they forget everything you just said! With session memory, your agent remembers the entire conversation.

### 🧒 Simple Analogy: The Conversation Notebook

Imagine talking to a friend:

- **Without Memory**: "Hi, what's your name?" → "I'm Alice" → "What's your name?" → "I'm Alice" (forgets immediately!)
- **With Memory**: "Hi, what's your name?" → "I'm Alice" → "What state do you live in?" → "I live in California" (remembers I'm Alice!)

Session memory is like giving your agent a perfect memory of your conversation!

## Sessions in OpenAI Agents SDK

The Agents SDK provides built-in session memory to automatically maintain conversation history across multiple agent runs, eliminating the need to manually handle .to_input_list() between turns.

Sessions stores conversation history for a specific session, allowing agents to maintain context without requiring explicit manual memory management. This is particularly useful for building chat applications or multi-turn conversations where you want the agent to remember previous interactions.


---

## 🧠 The Core Concept

**Without Session Memory (Default)**:

```python
# Each conversation is independent - agent forgets everything!
result1 = Runner.run_sync(agent, "What city is the Golden Gate Bridge in?")
# Agent: "San Francisco"

result2 = Runner.run_sync(agent, "What state is it in?")
# Agent: "What are you referring to?" (forgot about San Francisco!)
```

**With Session Memory**:

```python
# Agent remembers the conversation!
session = SQLiteSession("conversation_123")

result1 = Runner.run_sync(agent, "What city is the Golden Gate Bridge in?", session=session)
# Agent: "San Francisco"

result2 = Runner.run_sync(agent, "What state is it in?", session=session)
# Agent: "California" (remembers we were talking about San Francisco!)
```

---

## 🔧 How Session Memory Works

### **The Magic Behind the Scenes**

When you use session memory, the agent automatically:

1. **Before each run**: Retrieves all previous conversation history
2. **During the run**: Processes your new message with full context
3. **After the run**: Saves the new message and response to memory

```python
# What happens automatically:
session = SQLiteSession("user_123")

# Turn 1
result1 = Runner.run_sync(agent, "Hello", session=session)
# Memory now: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}]

# Turn 2
result2 = Runner.run_sync(agent, "How are you?", session=session)
# Memory loads previous history + adds new messages
# Memory now: [previous messages + new user message + new assistant response]
```

### **Session Storage Options**

| Storage Type          | Code                                     | When to Use                    |
| --------------------- | ---------------------------------------- | ------------------------------ |
| **No Memory**         | `Runner.run_sync(agent, query)`          | Quick tests, one-off questions |
| **Temporary Memory**  | `SQLiteSession("session_id")`            | Current session only           |
| **Persistent Memory** | `SQLiteSession("session_id", "<db...>")` | Save conversations forever     |

---

## 🎯 Baby Steps Examples

### 1. **Your First Session Memory**

```python
import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, AsyncOpenAI

# 🌿 Load environment variables
load_dotenv(find_dotenv())

# 🔐 Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

# Create agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant. Be friendly and remember our conversation.",
    model=model
)

# Create session memory
session = SQLiteSession("my_first_conversation")

print("=== First Conversation with Memory ===")

# Turn 1
result1 = Runner.run_sync(
    agent,
    "Hi! My name is Alex and I love pizza.",
    session=session
)
print("Agent:", result1.final_output)

# Turn 2 - Agent should remember your name!
result2 = Runner.run_sync(
    agent,
    "What's my name?",
    session=session
)
print("Agent:", result2.final_output)  # Should say "Alex"!

# Turn 3 - Agent should remember you love pizza!
result3 = Runner.run_sync(
    agent,
    "What food do I like?",
    session=session
)
print("Agent:", result3.final_output)  # Should mention pizza!
```

### 2. **Persistent vs Temporary Memory**

```python
import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, AsyncOpenAI

# 🌿 Load environment variables
load_dotenv(find_dotenv())

# 🔐 Setup Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

external_client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model = OpenAIChatCompletionsModel(model="gemini-2.5-flash", openai_client=external_client)

# Temporary memory (lost when program ends)
temp_session = SQLiteSession("temp_conversation")

# Persistent memory (saved to file)
persistent_session = SQLiteSession("user_123", "conversations.db")

agent = Agent(name="Assistant", instructions="You are helpful.", model=model)

# Use temporary session
result1 = Runner.run_sync(
    agent,
    "Remember: my favorite color is blue",
    session=temp_session
)

# Use persistent session
result2 = Runner.run_sync(
    agent,
    "Remember: my favorite color is blue",
    session=persistent_session
)

print("Both sessions now remember your favorite color!")
print("But only the persistent session will remember after restarting the program.")
```

### 3. **Memory Operations - Adding, Viewing, and Removing**

```python
import asyncio
from agents import SQLiteSession

async def memory_operations_demo():
    session = SQLiteSession("memory_ops", "test.db")

    # Add some conversation items manually
    conversation_items = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you?"},
        {"role": "user", "content": "What's the weather like?"},
        {"role": "assistant", "content": "I don't have access to weather data."}
    ]

    await session.add_items(conversation_items)
    print("Added conversation to memory!")

    # View all items in memory
    items = await session.get_items()
    print(f"\nMemory contains {len(items)} items:")
    for item in items:
        print(f"  {item['role']}: {item['content']}")

    # Remove the last item (undo)
    last_item = await session.pop_item()
    print(f"\nRemoved last item: {last_item}")

    # View memory again
    items = await session.get_items()
    print(f"\nMemory now contains {len(items)} items:")
    for item in items:
        print(f"  {item['role']}: {item['content']}")

    # Clear all memory
    await session.clear_session()
    print("\nCleared all memory!")

    # Verify memory is empty
    items = await session.get_items()
    print(f"Memory now contains {len(items)} items")

# Run the async demo
asyncio.run(memory_operations_demo())
```

## Custom memory implementations

Remember you can implement your own session memory by creating a class that follows the Session protocol:

## 🏗️ Real-World Applications

### Self Challenge Project **Customer Support ChatAgent**

```python
from agents import Agent, Runner, SQLiteSession
import datetime

class CustomerSupportBot:
    def __init__(self):
        self.agent = Agent(
            name="SupportBot",
            instructions="""You are a helpful customer support agent.
            Remember the customer's information and previous issues throughout the conversation.
            Be friendly and professional."""
        )

    def get_customer_session(self, customer_id: str):
        """Get or create a session for a specific customer"""
        return SQLiteSession(f"customer_{customer_id}", "support_conversations.db")

    def chat_with_customer(self, customer_id: str, message: str):
        """Handle a customer message"""
        session = self.get_customer_session(customer_id)

        result = Runner.run_sync(
            self.agent,
            message,
            session=session
        )

        return result.final_output

# Example usage
support_bot = CustomerSupportBot()

# Customer 123's conversation
print("=== Customer 123 Support Session ===")
print("Customer: Hi, I'm having trouble with my order #12345")
response1 = support_bot.chat_with_customer("123", "Hi, I'm having trouble with my order #12345")
print(f"Support: {response1}")

print("\nCustomer: The item was damaged when it arrived")
response2 = support_bot.chat_with_customer("123", "The item was damaged when it arrived")
print(f"Support: {response2}")

print("\nCustomer: What was my order number again?")
response3 = support_bot.chat_with_customer("123", "What was my order number again?")
print(f"Support: {response3}")  # Should remember order #12345!

# Different customer's conversation
print("\n=== Customer 456 Support Session ===")
print("Customer: Hello, I need help with billing")
response4 = support_bot.chat_with_customer("456", "Hello, I need help with billing")
print(f"Support: {response4}")  # Fresh conversation, no memory of customer 123
```

---

## ⚠️ Important Tips and Best Practices

### **Session ID Naming Conventions**

| Pattern           | Example                      | Use Case               |
| ----------------- | ---------------------------- | ---------------------- |
| **User-based**    | `"user_12345"`               | Personal conversations |
| **Thread-based**  | `"thread_abc123"`            | Forum/chat threads     |
| **Context-based** | `"support_ticket_456"`       | Specific purposes      |
| **Timestamped**   | `"session_2024_01_15_14_30"` | Time-based tracking    |

### **Memory Management**

```python
# ✅ Good: Use meaningful session IDs
session = SQLiteSession("customer_support_user_123", "production.db")

# ✅ Good: Different contexts get different sessions
work_session = SQLiteSession("work_chat_user_456")
personal_session = SQLiteSession("personal_chat_user_456")

# ✅ Good: Clear session when starting fresh
await session.clear_session()  # Start over

# ❌ Avoid: Generic session IDs
session = SQLiteSession("session1")  # Not descriptive

# ❌ Avoid: Mixing different contexts in same session
# Don't put work and personal conversations in same session
```

### **Performance Considerations**

```python
# For long conversations, limit memory retrieval
session = SQLiteSession("long_conversation")

# Get only recent items for performance
recent_items = await session.get_items(limit=50)  # Last 50 messages only

# For very active sessions, consider periodic cleanup
conversation_length = len(await session.get_items())
if conversation_length > 1000:
    print("Consider archiving old messages for performance")
```

---

## 🎓 Learning Progression

1. **Start Simple**: Basic session memory with one conversation
2. **Multiple Sessions**: Different conversations for different contexts
3. **Memory Operations**: Adding, viewing, removing items
4. **Corrections**: Using pop_item() to fix mistakes
5. **Real Applications**: Customer support, tutoring, personal assistants
6. **Custom Memory**: Build your own storage backend
7. **Production Patterns**: Performance optimization and best practices

---

_Remember: Session memory transforms your agent from having amnesia to having perfect recall of your conversations!_ 🧠✨
