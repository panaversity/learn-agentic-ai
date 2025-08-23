# 🎛️ Model Settings: Control Your AI Agent Brain

## 🎯 What are Model Settings?

Think of **Model Settings** like the **knobs and dials** on a professional camera. Just as a photographer adjusts focus, exposure, and shutter speed to get the perfect shot, you can adjust your AI agent's brain behavior to get exactly the response you want.

### 🧒 Simple Analogy: Cooking with Precision

Imagine you're cooking:
- **Temperature** = How creative vs. focused your agent is
- **Tool Choice** = Whether your agent can use calculators, weather apps, etc.
- **Max Tokens** = How long the response can be
- **Parallel Tools** = Whether your agent can use multiple tools at once

---

## 🎛️ The Most Important Settings (Baby Steps)

### 1. **Temperature** - The Creativity Knob

```python
# Low temperature (0.1) = Very focused, consistent answers
agent_focused = Agent(
    name="Math Tutor",
    instructions="You are a precise math tutor.",
    model_settings=ModelSettings(temperature=0.1)
)

# High temperature (0.9) = More creative, varied responses
agent_creative = Agent(
    name="Story Writer",
    instructions="You are a creative storyteller.",
    model_settings=ModelSettings(temperature=0.9)
)
```

**When to use:**
- **Low (0.1-0.3)**: Math, facts, precise instructions
- **Medium (0.4-0.6)**: General conversation, explanations
- **High (0.7-0.9)**: Creative writing, brainstorming

Note: For Gemini temperature range extends to 2.

### 2. **Tool Choice** - The "Can I Use Tools?" Switch

```python
# Agent can decide when to use tools (default)
agent_auto = Agent(
    name="Smart Assistant",
    tools=[calculator, weather_tool],
    model_settings=ModelSettings(tool_choice="auto")
)

# Agent MUST use a tool (even if not needed)
agent_required = Agent(
    name="Tool User",
    tools=[calculator, weather_tool],
    model_settings=ModelSettings(tool_choice="required")
)

# Agent CANNOT use tools (chat only)
agent_no_tools = Agent(
    name="Chat Only",
    tools=[calculator, weather_tool],
    model_settings=ModelSettings(tool_choice="none")
)
```

### 3. **Max Tokens** - The Response Length Limit

```python
# Short, concise responses
agent_brief = Agent(
    name="Brief Assistant",
    model_settings=ModelSettings(max_tokens=100)
)

# Longer, detailed responses
agent_detailed = Agent(
    name="Detailed Assistant", 
    model_settings=ModelSettings(max_tokens=1000)
)
```

---

## 🧪 Hands-On Examples

### Example 1: Math Tutor with Low Temperature

```python
from agents import Agent, ModelSettings, Runner

# Create a precise math tutor
math_tutor = Agent(
    name="Math Tutor",
    instructions="You are a precise math tutor. Always show your work step by step.",
    model_settings=ModelSettings(
        temperature=0.1,  # Very focused
        max_tokens=500    # Enough for detailed steps
    )
)

result = Runner.run_sync(math_tutor, "Solve: 2x + 5 = 13")
print(result.final_output)
```

### Example 2: Creative Writer with High Temperature

```python
creative_writer = Agent(
    name="Creative Writer",
    instructions="You are a creative storyteller. Write engaging, imaginative stories.",
    model_settings=ModelSettings(
        temperature=0.8,  # Very creative
        max_tokens=300    # Short but creative
    )
)

result = Runner.run_sync(creative_writer, "Write a short story about a robot learning to paint")
print(result.final_output)
```

### Example 3: Tool-Using Assistant

```python
from agents import function_tool

@function_tool
def calculate_area(length: float, width: float) -> str:
    """Calculate the area of a rectangle."""
    area = length * width
    return f"Area = {length} × {width} = {area} square units"

# Agent that MUST use tools
tool_user = Agent(
    name="Tool User",
    instructions="You are a helpful assistant. Always use tools when available.",
    tools=[calculate_area],
    model_settings=ModelSettings(tool_choice="required")
)

result = Runner.run_sync(tool_user, "What's the area of a 5x3 rectangle?")
print(result.final_output)
```

---

## 🎛️ Advanced Settings (For Later)

### Parallel Tool Calls

```python
# Agent can use multiple tools at once
parallel_agent = Agent(
    name="Multi-Tasker",
    tools=[weather_tool, calculator, translator],
    model_settings=ModelSettings(
        tool_choice="auto",
        parallel_tool_calls=True  # Use multiple tools simultaneously
    )
)

# Agent uses tools one at a time
sequential_agent = Agent(
    name="One-at-a-Time",
    tools=[weather_tool, calculator, translator],
    model_settings=ModelSettings(
        tool_choice="auto",
        parallel_tool_calls=False  # Use tools one by one
    )
)
```

### Top-P and Penalties

```python
# More focused vocabulary
focused_agent = Agent(
    name="Focused",
    model_settings=ModelSettings(
        top_p=0.3,              # Use only top 30% of vocabulary
        frequency_penalty=0.5,   # Avoid repeating words
        presence_penalty=0.3     # Encourage new topics
    )
)
```

---

## 🎯 When to Use Each Setting

| Setting | Use When | Example |
|---------|----------|---------|
| **Low Temperature** | Need precise, consistent answers | Math problems, fact-checking |
| **High Temperature** | Want creative, varied responses | Story writing, brainstorming |
| **Tool Choice: Required** | Want to force tool usage | Data analysis, calculations |
| **Tool Choice: None** | Want chat-only responses | Casual conversation |
| **Low Max Tokens** | Need brief responses | Quick answers, summaries |
| **High Max Tokens** | Need detailed explanations | Tutorials, documentation |

---

## 🎓 Learning Progression

1. **Start Simple**: Just use `temperature` and `max_tokens`
2. **Add Tools**: Experiment with `tool_choice`
3. **Go Advanced**: Try `parallel_tool_calls` and penalties
4. **Master It**: Combine multiple settings for perfect results

---

## 💡 Pro Tips

- **Start with defaults**: Don't change settings unless you need to
- **Test small changes**: Adjust one setting at a time
- **Document your settings**: Keep notes on what works for different tasks
- **Consider the task**: Different tasks need different settings

---

## 🔗 Next Steps

- Try the examples in the `hello_agent/` folder
- Experiment with your own settings

---

*Remember: Model settings are like seasoning in cooking - a little goes a long way, and the right combination makes all the difference!* 🎛️✨
