# 🎭 Dynamic Instructions Learning Module

## 🚀 Quick Start

1. **Navigate to the module:**
   ```bash
   cd 01_ai_agents_first/09_dynamic_instructions/hello_agent
   ```

2. **Install dependencies:**
   ```bash
   uv add openai-agents python-dotenv
   ```

3. **Set up your environment:**
   ```bash
   # Copy the backup file
   cp .env_backup .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Run the learning examples:**
   ```bash
   python main.py
   ```

## 📚 What You'll Learn

This module teaches you how to make your AI agents **adapt their behavior** using **Dynamic Instructions**:

- **Basic Dynamic**: Simple function-based instructions
- **Context-Aware**: Adapt based on conversation history
- **Time-Based**: Change behavior based on time of day
- **Stateful**: Remember interactions and adapt accordingly

## 🎯 Learning Progression

1. **Start Simple**: Basic dynamic instructions
2. **Add Context**: Use conversation history
3. **Add Time**: Time-based adaptations
4. **Add State**: Remember interactions

## 🧪 Examples Included

- **Basic Dynamic**: Simple function that changes instructions
- **Context-Aware**: Adapts based on message count
- **Time-Based**: Different responses at different times
- **Stateful**: Remembers interaction count

## 💡 Key Concepts

### Dynamic Instructions (The Chameleon Teacher)
- **Static**: Same instructions every time
- **Dynamic**: Instructions change based on context
- **Context-Aware**: Adapts to conversation history
- **Stateful**: Remembers previous interactions

### When to Use Dynamic Instructions
- **Personalization**: Adapt to user preferences
- **Context Awareness**: Change based on conversation
- **Time Sensitivity**: Different responses at different times
- **Learning Progression**: Adapt as user becomes experienced

## 🔗 Related Modules

- **Previous**: [Model Settings](../07_model_settings/) - Control agent behavior
- **Next**: [Context Management](../10_context_management/) - Manage conversation state

## 🎓 Tips for Success

1. **Start simple**: Begin with basic functions
2. **Test thoroughly**: Dynamic instructions can be unpredictable
3. **Document behavior**: Write down what each function does
4. **Handle errors**: Always have fallback instructions
5. **Consider performance**: Async functions add complexity

---

*Ready to make your agents adapt? Let's start with the examples!* 🎭✨
