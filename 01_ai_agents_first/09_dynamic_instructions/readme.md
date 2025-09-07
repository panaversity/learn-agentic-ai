# 🎭 Dynamic Instructions: Make Your Agent Adapt

## 🎯 What are Dynamic Instructions?

Think of **Dynamic Instructions** like a **smart assistant that changes its personality** based on who it's talking to. Instead of giving your agent the same instructions every time, you can make it adapt its behavior based on the situation.

### 🧒 Simple Analogy: The Chameleon Teacher

Imagine a teacher who:
- **Greets new students** warmly and introduces themselves
- **Gets more detailed** with students who ask follow-up questions  
- **Becomes more efficient** with students they've helped many times

Dynamic instructions let your AI agent do the same thing!

---

## 🎭 The Core Idea

Instead of static instructions like:
```python
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant."  # ❌ Always the same
)
```

You can use a **function** that changes the instructions:
```python
from agents import RunContextWrapper, Agent

def dynamic_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. Adapt to the user's needs."

agent = Agent(
    name="Smart Assistant",
    instructions=dynamic_instructions  # ✅ Changes based on context
)
```

---

## 🔧 Function Signature

Dynamic instruction functions receive two parameters:

```python
from agents import RunContextWrapper, Agent

def dynamic_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    return f"The user's name is {ctx.context.name}. Help them with their questions."
```

### 📋 Parameters Explained

| Parameter | Type | What It Contains |
|-----------|------|------------------|
| **`ctx`** | `RunContextWrapper` | The ctx object with context, usage |
| **`agent`** | `Agent` | The agent object with name, tools, settings |
| **Returns** | `str` | The instructions string for the agent |

---

## 🎯 Baby Steps Examples

### 1. **Simple Dynamic Instructions**

```python
from agents import RunContextWrapper, Agent

def basic_dynamic(ctx: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. Be helpful and friendly."

agent = Agent(
    name="Dynamic Agent",
    instructions=basic_dynamic
)
```

### 2. **Context-Aware Instructions**

```python
def context_aware(ctx: RunContextWrapper, agent: Agent) -> str:
    # Check how many messages in the conversation
    message_count = len(getattr(ctx.context, 'messages', []))
    
    if message_count == 0:
        return "You are a welcoming assistant. Introduce yourself!"
    elif message_count < 3:
        return "You are a helpful assistant. Be encouraging and detailed."
    else:
        return "You are an experienced assistant. Be concise but thorough."

agent = Agent(
    name="Context Aware Agent", 
    instructions=context_aware
)
```

### 3. **Time-Based Instructions**

```python
import datetime

def time_based(ctx: RunContextWrapper, agent: Agent) -> str:
    current_hour = datetime.datetime.now().hour
    
    if 6 <= current_hour < 12:
        return f"You are {agent.name}. Good morning! Be energetic and positive."
    elif 12 <= current_hour < 17:
        return f"You are {agent.name}. Good afternoon! Be focused and productive."
    else:
        return f"You are {agent.name}. Good evening! Be calm and helpful."

agent = Agent(
    name="Time Aware Agent",
    instructions=time_based
)
```

---

## 🎭 Advanced Examples

### 4. **Stateful Instructions (Remembers Interactions)**

```python
class StatefulInstructions:
    def __init__(self):
        self.interaction_count = 0
    
    def __call__(self, ctx: RunContextWrapper, agent: Agent) -> str:
        self.interaction_count += 1
        
        if self.interaction_count == 1:
            return "You are a learning assistant. This is our first interaction - be welcoming!"
        elif self.interaction_count <= 3:
            return f"You are a learning assistant. This is interaction #{self.interaction_count} - build on our conversation."
        else:
            return f"You are an experienced assistant. We've had {self.interaction_count} interactions - be efficient."

instruction_gen = StatefulInstructions()

agent = Agent(
    name="Stateful Agent",
    instructions=instruction_gen
)
```

### 5. **Async Dynamic Instructions**

```python
import asyncio

async def async_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    # Simulate fetching data from database
    await asyncio.sleep(0.1)
    current_time = datetime.datetime.now()
    
    return f"""You are {agent.name}, an AI assistant with real-time capabilities.
    Current time: {current_time.strftime('%H:%M')}
    Provide helpful and timely responses."""

agent = Agent(
    name="Async Agent",
    instructions=async_instructions
)
```

---

## 🔍 Understanding Ctx and Agent

### **Ctx Parameter**
The `ctx` contains context and usage:
1. **Context** can contain any data you provide:
    - **Messages**: Conversation history
    - **User data**: Custom user information
    - **Run state**: Current execution state
    - **Metadata**: Additional information
2. **Usage** contains model usage:
    - **requests**: Total requests made to the LLM API
    - **input_tokens**: Total input tokens sent, across all requests
    - **input_tokens_details**: Details about the input tokens
    - **output_tokens**: Total output tokens received
    - **more**: output_tokens_details, total_tokens, add method
```python
def explore_context(ctx: RunContextWrapper, agent: Agent) -> str:
    # Access conversation messages
    messages = getattr(ctx.context, 'messages', [])
    message_count = len(messages)
    
    # Access user context (if available)
    user_name = getattr(ctx.context, 'name', 'User')
    
    return f"You are {agent.name}. Talking to {user_name}. Message #{message_count}."
```

### **Agent Parameter**
The `agent` contains:
- **name**: Agent's identity
- **tools**: Available tools
- **model_settings**: Model settings
- **handoffs**: Agent handoffs
- **many more**: hooks, input_guardrails, output_type etc...

```python
def explore_agent(ctx: RunContextWrapper, agent: Agent) -> str:
    # Access agent properties
    agent_name = agent.name
    tool_count = len(agent.tools)
    
    return f"You are {agent_name} with {tool_count} tools. Be helpful!"
```

---

## 🎯 When to Use Dynamic Instructions

| Use Case | Example |
|----------|---------|
| **Personalization** | Adapt based on user preferences |
| **Context Awareness** | Change behavior based on conversation history |
| **Time Sensitivity** | Different responses at different times |
| **Learning Progression** | Adapt as user becomes more experienced |
| **Multi-Modal** | Different instructions for different input types |

---

## 🧪 Try It Yourself!

### Exercise 1: Simple Dynamic Instructions

```python
from agents import RunContextWrapper, Agent

def my_dynamic_instructions(ctx: RunContextWrapper, agent: Agent) -> str:
    return f"You are {agent.name}. You love helping people learn Python!"

agent = Agent(
    name="Python Helper",
    instructions=my_dynamic_instructions
)

result = Runner.run_sync(agent, "What is a function?")
print(result.final_output)
```

### Exercise 2: Message Count Aware

```python
def message_count_aware(ctx: RunContextWrapper, agent: Agent) -> str:
    message_count = len(getattr(ctx.context, 'messages', []))
    
    if message_count == 0:
        return "You are a welcoming assistant. Say hello!"
    else:
        return f"You are an assistant. This is message #{message_count}. Be helpful!"

agent = Agent(
    name="Message Counter",
    instructions=message_count_aware
)
```

---

## 🎓 Learning Progression

1. **Start Simple**: Basic dynamic instructions
2. **Add Context**: Use conversation history
3. **Add Time**: Time-based adaptations
4. **Add State**: Remember interactions
5. **Go Async**: Handle async operations

---

## 💡 Pro Tips

- **Keep it simple**: Start with basic functions
- **Test thoroughly**: Dynamic instructions can be unpredictable
- **Document behavior**: Write down what each function does
- **Handle errors**: Always have fallback instructions
- **Consider performance**: Async functions add complexity

---

## 🔗 Next Steps

- Try the examples in the `hello_agent/` folder
- Experiment with your own dynamic instructions
- Learn about [Context Management](../08_local_context/readme.md)
- Explore [Context Engineering](../28_context_engineering/readme.md)

---

*Remember: Dynamic instructions make your agents smarter and more adaptable!* 🎭✨