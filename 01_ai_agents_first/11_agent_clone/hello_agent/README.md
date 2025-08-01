# 🧬 Agent Cloning Learning Module

## 🚀 Quick Start

1. **Navigate to the module:**
   ```bash
   cd 01_ai_agents_first/11_agent_clone/hello_agent
   ```

2. **Install dependencies:**
   ```bash
   uv add openai-agents python-dotenv
   ```

3. **Set up your environment:**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Run the learning examples:**
   ```bash
   python main.py
   ```

## 📚 What You'll Learn

This module teaches you how to **create agent variants efficiently** using **Agent Cloning**:

- **Basic Cloning**: Create variants with different names/instructions
- **Settings Cloning**: Clone with different model settings
- **Tools Cloning**: Clone with different tool sets
- **Shared References**: Understand how cloning affects original agents
- **Agent Families**: Create multiple specialized variants

## 🎯 Learning Progression

1. **Start Simple**: Basic cloning with different names/instructions
2. **Add Settings**: Clone with different model settings
3. **Add Tools**: Clone with different tool sets
4. **Understand References**: Learn about shared vs independent
5. **Master Patterns**: Create agent families and templates

## 🧪 Examples Included

- **Basic Cloning**: Simple agent variants
- **Settings Cloning**: Different temperature and creativity levels
- **Tools Cloning**: Adding/removing tools from clones
- **Multiple Clones**: Creating agent families from one base
- **Shared References**: Understanding shallow copy behavior
- **Practical Families**: Writing style variants (Poet, Scientist, Chef)

## 💡 Key Concepts

### Agent Cloning (The Recipe Book)
- **Base Agent**: Your original agent template
- **Clone**: Copy with specific changes
- **Shared References**: Tools and handoffs are shared by default
- **Independent Clones**: Pass new lists for independent tools

### When to Use Cloning
- **Create Variants**: Different personalities from same base
- **A/B Testing**: Test different settings quickly
- **Specialization**: Create domain-specific agents
- **Templates**: Use base agent as template
- **Experimentation**: Try different configurations

## 🔗 Related Modules

- **Previous**: [Dynamic Instructions](../09_dynamic_instructions/) - Adapt agent behavior
- **Next**: [Agent Families](../12_agent_families/) - Create agent hierarchies

## 🎓 Tips for Success

1. **Use cloning for variants**: Don't recreate agents from scratch
2. **Be careful with shared references**: Pass new lists for tools/handoffs
3. **Document your base agents**: Keep track of what you're cloning
4. **Test your clones**: Make sure they behave as expected
5. **Consider templates**: Create base agents for common patterns

---

*Ready to create agent variants? Let's start with the examples!* 🧬✨ 