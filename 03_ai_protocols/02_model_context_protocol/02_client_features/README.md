# 03: Client Features - Advanced MCP Capabilities

## 🎯 Module Learning Objectives  
By completing this module, you will be able to:
1. **Master** all three advanced MCP client capabilities (sampling, elicitation, roots)
2. **Design** intelligent tools that combine AI reasoning, user interaction, and context awareness
3. **Implement** both stateful and stateless HTTP MCP servers appropriately
4. **Evaluate** when and how to use each capability for maximum effectiveness
5. **Build** production-ready MCP applications with proper architecture patterns

## 🧠 Core Philosophy: From Static to Intelligent Tools

**Traditional MCP Tools:** 
- Take parameters → Process → Return results
- Limited, predictable behavior
- No adaptation or learning

**Advanced MCP Tools:**
- **🧠 Can Think** (via sampling) - Delegate complex reasoning to AI
- **🤝 Can Interact** (via elicitation) - Have conversations with users  
- **📁 Can Adapt** (via roots) - Understand and work within user's context

This represents the evolution from simple automation to intelligent, adaptive AI assistants.

## 🎓 Active Learning Path

### 📚 Progressive Skill Building

Each lesson builds on the previous, with hands-on exercises and real-world applications:

### **Stage 1: [01_sampling](./01_sampling/) - AI-Powered Reasoning**

**🎯 Core Question:** *"When should tools think vs. follow predefined logic?"*

**What You'll Learn:**
- How to delegate complex reasoning to client LLMs
- When AI delegation improves tool capabilities
- Building tools that adapt their behavior intelligently
- **Architecture:** Stateful HTTP for server-to-client requests

**🛠️ Hands-On Exercises:**
- Build a sentiment analysis tool using sampling
- Experiment with prompt engineering for different outputs
- Create multi-step AI reasoning workflows

**🏆 Success Criteria:** You can explain when and why to use AI delegation in tool design.

---

### **Stage 2: [02_elicitation](./02_elicitation/) - Interactive Experiences**

**🎯 Core Question:** *"How can tools become conversational and user-friendly?"*

**What You'll Learn:**
- Designing interactive, multi-step tool workflows  
- Various input types (text, select, boolean, etc.)
- Building user-friendly interfaces for complex operations
- **Architecture:** Stateful HTTP for multi-round-trip interactions

**🛠️ Hands-On Exercises:**  
- Design an interactive project setup wizard
- Build error handling for interrupted workflows
- Create conditional logic based on user responses

**🏆 Success Criteria:** You can design tools that feel like natural conversations.

---

### **Stage 3: [03_roots](./03_roots/) - Context Awareness**

**🎯 Core Question:** *"How can tools understand and work within project boundaries?"*

**What You'll Learn:**
- Building project-aware tools that discover context
- Working with file system boundaries securely
- Creating tools that adapt to different project structures
- **Architecture:** Flexible HTTP (stateful or stateless based on complexity)

**🛠️ Hands-On Exercises:**
- Build a project analysis tool using roots
- Design security controls for file system access
- Create tools that work across multiple project types

**🏆 Success Criteria:** You can build tools that "understand" user workspaces.

## 🏗️ Architecture Deep Dive

### **HTTP Configuration Decision Tree**

```
Does your tool need to send requests TO the client?
├─ Yes: Sampling or Elicitation
│  └─ Use: stateless_http=False (Stateful Required)
└─ No: Only client sends requests to server  
   ├─ Simple operations
   │  └─ Use: stateless_http=True (Better performance)
   └─ Complex operations with roots
      └─ Use: stateless_http=False (Better for multiple requests)
```

### **Streamable HTTP Implementation**

All servers use the modern streamable HTTP pattern:

```python
# Consistent pattern across all lessons
mcp = FastMCP(
    name="my-server",
    stateless_http=False,  # or True based on needs
)

@mcp.tool()
async def my_tool(ctx: Context) -> str:
    # Tool implementation
    pass

# Modern streamable HTTP app
mcp_app = mcp.streamable_http_app()

if __name__ == "__main__":
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)
```

## 🧪 Integrated Learning Experiments

### **Cross-Capability Integration Challenges**

After completing individual lessons, try these integration exercises:

**🔬 Experiment 1: Smart Code Assistant**
Combine all three capabilities:
1. **Roots** discover project structure
2. **Sampling** analyze code patterns and suggest improvements
3. **Elicitation** gather user preferences for recommendations

**🔬 Experiment 2: Interactive Project Onboarding**
Build a tool that:
1. **Elicitation** asks about project goals and constraints
2. **Roots** analyzes existing project structure (if any)
3. **Sampling** generates personalized setup recommendations

**🔬 Experiment 3: Context-Aware Documentation Generator**
Create a system that:
1. **Roots** scans entire codebase
2. **Sampling** generates documentation for each component
3. **Elicitation** asks for user preferences on documentation style

## 🎯 Assessment and Mastery

### **Progressive Assessment Framework**

**🥉 Bronze Level: Basic Implementation**
- [ ] Can implement each capability independently
- [ ] Understands when to use stateful vs. stateless HTTP
- [ ] Can follow provided code examples successfully

**🥈 Silver Level: Applied Understanding**  
- [ ] Can design appropriate tools for given scenarios
- [ ] Understands trade-offs between different approaches
- [ ] Can combine capabilities effectively

**🥇 Gold Level: Expert Application**
- [ ] Can architect complex, multi-capability systems
- [ ] Understands security and performance implications
- [ ] Can teach others and explain design decisions

### **Portfolio Projects**

Build these to demonstrate mastery:

1. **Personal Productivity Assistant** - Uses all three capabilities for task management
2. **Development Workflow Optimizer** - Analyzes and improves team coding practices  
3. **Interactive Learning Platform** - Adapts content based on user progress and context

## 🌟 Real-World Impact

### **What You Can Build After This Module**

**🛠️ Development Tools:**
- Code analysis tools that understand entire projects
- Interactive debugging assistants that ask smart questions
- AI-powered refactoring tools with user guidance

**📊 Business Applications:**
- Intelligent form builders that adapt to user responses
- Context-aware reporting tools for different business units
- Interactive onboarding systems for complex software

**🎓 Educational Systems:**
- Adaptive learning platforms that understand student context
- Interactive coding tutors that adjust to skill level
- Project-based learning assistants

### **Career Advancement**

**Skills You'll Develop:**
- **System Architecture:** Understanding when to use different HTTP patterns
- **User Experience Design:** Creating intuitive, conversational tool interfaces
- **AI Integration:** Effectively combining human and AI intelligence
- **Security Thinking:** Managing file access and user data responsibly

## 🚀 Getting Started

### **Recommended Learning Path**

1. **🔰 Start Here:** Read this overview to understand the big picture
2. **📖 Begin with Sampling:** Master AI delegation patterns first
3. **🤝 Move to Elicitation:** Learn interactive design principles
4. **📁 Complete with Roots:** Add context awareness to your toolkit
5. **🔄 Integrate Everything:** Build comprehensive tools using all capabilities

### **Study Tips for Success**

- **✋ Hands-On First:** Run every example before reading the theory
- **🤔 Question Everything:** Ask "why" and "when" for each pattern you see
- **🧪 Experiment Actively:** Modify examples to test your understanding
- **🏗️ Build Your Own:** Create tools for problems you actually face
- **👥 Teach Others:** Explaining concepts reinforces your learning

### **Prerequisites Check**

Before starting, ensure you have:
- [ ] Completed MCP basics (01_mcp_concepts and 01_server_engineering)
- [ ] Understanding of async/await in Python
- [ ] Basic familiarity with HTTP concepts
- [ ] Development environment with Python 3.11+ and uv

---

**🎓 Ready to Transform Your Tool-Building Skills?**

Start your journey with [01_sampling](./01_sampling/) and discover how to give your tools the power of AI reasoning.

**The future of development tools is intelligent, interactive, and context-aware. You're about to build it.** 