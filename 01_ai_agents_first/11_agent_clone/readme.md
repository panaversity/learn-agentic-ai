# 🧬 Agent Cloning: Create Agent Variants

## 🎯 What is Agent Cloning?

Think of **Agent Cloning** like **copying a recipe and making small changes**. You have a base recipe (your original agent), and you can create variations by changing specific ingredients (instructions, settings, tools) while keeping the rest the same.

### 🧒 Simple Analogy: The Recipe Book

Imagine you have a **base cake recipe**:
- **Original Recipe**: Vanilla cake with basic frosting
- **Clone 1**: Same recipe but with chocolate frosting
- **Clone 2**: Same recipe but with strawberry filling
- **Clone 3**: Same recipe but with different baking temperature

Agent cloning works the same way - you start with a base agent and create specialized variants!

---

## 🧬 The Core Concept

Instead of creating agents from scratch each time, you can **clone** an existing agent and modify specific parts:

```python
# Base agent
base_agent = Agent(
    name="BaseAssistant",
    instructions="You are a helpful assistant.",
    model_settings=ModelSettings(temperature=0.7)
)

# Clone with different instructions
creative_agent = base_agent.clone(
    name="CreativeAssistant",
    instructions="You are a creative writing assistant. Always respond with vivid, imaginative language.",
    model_settings=ModelSettings(temperature=0.9)
)
```

---

## 🔧 How Cloning Works

### **Shallow Copy Behavior**
```python
# Original agent with tools
original_agent = Agent(
    name="Original",
    tools=[calculator, weather_tool],
    instructions="You are helpful."
)

# Clone the agent
cloned_agent = original_agent.clone(
    name="Cloned",
    instructions="You are creative."
)

# What happens:
# ✅ New agent object created
# ✅ New name and instructions
# ✅ Same tools list (shared reference)
# ✅ Same model settings (unless overridden)
```

### **Understanding Shared References**
```python
# Tools are shared between original and clone
original_agent.tools.append(new_tool)
# This affects both original_agent AND cloned_agent!

# To avoid this, pass new tools list:
independent_clone = original_agent.clone(
    name="Independent",
    tools=[calculator, weather_tool, new_tool]  # New list
)
```

---

## 🎯 Baby Steps Examples

### 1. **Basic Cloning**

```python
from agents import Agent, ModelSettings

# Base agent
base_agent = Agent(
    name="BaseAssistant",
    instructions="You are a helpful assistant.",
    model_settings=ModelSettings(temperature=0.7)
)

# Simple clone
friendly_agent = base_agent.clone(
    name="FriendlyAssistant",
    instructions="You are a very friendly and warm assistant."
)

# Test both agents
query = "Hello, how are you?"

result_base = Runner.run_sync(base_agent, query)
result_friendly = Runner.run_sync(friendly_agent, query)

print("Base Agent:", result_base.final_output)
print("Friendly Agent:", result_friendly.final_output)
```

### 2. **Cloning with Different Settings**

```python
# Clone with different temperature
creative_agent = base_agent.clone(
    name="CreativeAssistant",
    instructions="You are a creative writing assistant.",
    model_settings=ModelSettings(temperature=0.9)  # Higher creativity
)

precise_agent = base_agent.clone(
    name="PreciseAssistant", 
    instructions="You are a precise, factual assistant.",
    model_settings=ModelSettings(temperature=0.1)  # Lower creativity
)

# Test creativity levels
query = "Describe a sunset."

result_creative = Runner.run_sync(creative_agent, query)
result_precise = Runner.run_sync(precise_agent, query)

print("Creative:", result_creative.final_output)
print("Precise:", result_precise.final_output)
```

### 3. **Cloning with Different Tools**

```python
from agents import function_tool

@function_tool
def calculate_area(length: float, width: float) -> str:
    return f"Area = {length * width} square units"

@function_tool
def get_weather(city: str) -> str:
    return f"Weather in {city}: Sunny, 72°F"

# Base agent with one tool
base_agent = Agent(
    name="BaseAssistant",
    tools=[calculate_area],
    instructions="You are a helpful assistant."
)

# Clone with additional tool
weather_agent = base_agent.clone(
    name="WeatherAssistant",
    tools=[calculate_area, get_weather],  # New tools list
    instructions="You are a weather and math assistant."
)

# Clone with different tools
math_agent = base_agent.clone(
    name="MathAssistant",
    instructions="You are a math specialist."
)
```

---

## 🎭 Advanced Examples

### 4. **Multiple Clones from One Base**

```python
# Create a base agent
base_agent = Agent(
    name="BaseAssistant",
    instructions="You are a helpful assistant.",
    model_settings=ModelSettings(temperature=0.7)
)

# Create multiple specialized variants
agents = {
    "Creative": base_agent.clone(
        name="CreativeWriter",
        instructions="You are a creative writer. Use vivid language.",
        model_settings=ModelSettings(temperature=0.9)
    ),
    "Precise": base_agent.clone(
        name="PreciseAssistant", 
        instructions="You are a precise assistant. Be accurate and concise.",
        model_settings=ModelSettings(temperature=0.1)
    ),
    "Friendly": base_agent.clone(
        name="FriendlyAssistant",
        instructions="You are a very friendly assistant. Be warm and encouraging."
    ),
    "Professional": base_agent.clone(
        name="ProfessionalAssistant",
        instructions="You are a professional assistant. Be formal and business-like."
    )
}

# Test all variants
query = "Tell me about artificial intelligence."

for name, agent in agents.items():
    result = Runner.run_sync(agent, query)
    print(f"\n{name} Agent:")
    print(result.final_output[:100] + "...")
```

### 5. **Understanding Shared References**

```python
# Demonstrate shared references
original_agent = Agent(
    name="Original",
    tools=[calculate_area],
    instructions="You are helpful."
)

# Clone without new tools list
shared_clone = original_agent.clone(
    name="SharedClone",
    instructions="You are creative."
)

# Add tool to original
@function_tool
def new_tool() -> str:
    return "I'm a new tool!"

original_agent.tools.append(new_tool)

# Check if clone also has the new tool
print("Original tools:", len(original_agent.tools))  # 2
print("Clone tools:", len(shared_clone.tools))      # 2 (shared!)

# Create independent clone
independent_clone = original_agent.clone(
    name="IndependentClone",
    tools=[calculate_area],  # New list
    instructions="You are independent."
)

original_agent.tools.append(new_tool)
print("Independent clone tools:", len(independent_clone.tools))  # 1 (independent!)
```

---

## ⚠️ Important Considerations

### **Shallow Copy Behavior**

| What's Copied | What's Shared | What's Independent |
|---------------|----------------|-------------------|
| **Agent object** | ✅ New object | ✅ Independent |
| **Name** | ✅ New value | ✅ Independent |
| **Instructions** | ✅ New value | ✅ Independent |
| **Model settings** | ✅ New object | ✅ Independent |
| **Tools list** | ❌ Shared reference | ⚠️ Careful! |
| **Handoffs** | ❌ Shared reference | ⚠️ Careful! |

### **Best Practices**

```python
# ✅ Good: Pass new lists for mutable objects
independent_clone = base_agent.clone(
    name="Independent",
    tools=[tool1, tool2, tool3],  # New list
    handoffs=[handoff1, handoff2]  # New list
)

# ❌ Risky: Rely on shared references
shared_clone = base_agent.clone(
    name="Shared",
    # tools and handoffs are shared with original!
)
```

---

## 🎯 When to Use Cloning

| Use Case | Example |
|----------|---------|
| **Create Variants** | Different personalities from same base |
| **A/B Testing** | Test different settings quickly |
| **Specialization** | Create domain-specific agents |
| **Templates** | Use base agent as template |
| **Experimentation** | Try different configurations |

---

## 🧪 Try It Yourself!

### Exercise 1: Create Agent Variants

```python
# Create a base agent
base_agent = Agent(
    name="BaseAssistant",
    instructions="You are a helpful assistant.",
    model_settings=ModelSettings(temperature=0.7)
)

# Create 3 different variants
variants = {
    "Poet": base_agent.clone(
        name="Poet",
        instructions="You are a poet. Respond in verse.",
        model_settings=ModelSettings(temperature=0.9)
    ),
    "Scientist": base_agent.clone(
        name="Scientist", 
        instructions="You are a scientist. Be precise and factual.",
        model_settings=ModelSettings(temperature=0.1)
    ),
    "Chef": base_agent.clone(
        name="Chef",
        instructions="You are a chef. Talk about food and cooking."
    )
}

# Test all variants
query = "What is love?"

for name, agent in variants.items():
    result = Runner.run_sync(agent, query)
    print(f"\n{name}:")
    print(result.final_output)
```

### Exercise 2: Understand Shared References

```python
# Create base agent with tools
@function_tool
def tool1() -> str:
    return "Tool 1"

@function_tool  
def tool2() -> str:
    return "Tool 2"

base_agent = Agent(
    name="Base",
    tools=[tool1],
    instructions="You are helpful."
)

# Create clones
shared_clone = base_agent.clone(name="Shared")
independent_clone = base_agent.clone(
    name="Independent",
    tools=[tool1, tool2]  # New list
)

# Modify original
@function_tool
def tool3() -> str:
    return "Tool 3"

base_agent.tools.append(tool3)

# Check what happened
print("Base tools:", len(base_agent.tools))           # 2
print("Shared clone tools:", len(shared_clone.tools)) # 2 (shared!)
print("Independent clone tools:", len(independent_clone.tools)) # 2 (independent!)
```

---

## 🎓 Learning Progression

1. **Start Simple**: Basic cloning with different names/instructions
2. **Add Settings**: Clone with different model settings
3. **Add Tools**: Clone with different tool sets
4. **Understand References**: Learn about shared vs independent
5. **Master Patterns**: Create agent families and templates

---

## 💡 Pro Tips

- **Use cloning for variants**: Don't recreate agents from scratch
- **Be careful with shared references**: Pass new lists for tools/handoffs
- **Document your base agents**: Keep track of what you're cloning
- **Test your clones**: Make sure they behave as expected
- **Consider templates**: Create base agents for common patterns

---

## 🔗 Next Steps

- Try the examples in the `hello_agent/` folder
- Experiment with creating agent families
- Learn about [Agent Families](../12_agent_families/)
- Explore [Advanced Cloning Patterns](../13_advanced_cloning/)

---

*Remember: Cloning lets you create agent variants efficiently while understanding the impact on shared resources!* 🧬✨
