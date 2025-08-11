# Step 02: Agent Skills 🛠️

**Define agent capabilities using A2A Skills specification - the foundation of agent discovery**

> **🎯 Learning Objective**: Master how A2A agents advertise their capabilities through structured skill definitions, enabling intelligent agent-to-agent discovery and task delegation.

## 🧠 Learning Sciences Foundation

### **Cognitive Load Theory Applied**

- **Intrinsic Load**: Focus on core concept of agent skills and capability description
- **Extraneous Load**: Minimize by building directly on Step 1's agent card foundation
- **Germane Load**: Connect skills to real-world agent capabilities and business value

### **Constructivist Learning**

- **Prior Knowledge**: Agent Cards from Step 1 + JSON structure understanding
- **New Knowledge**: Skills definition, capability metadata, discoverability patterns
- **Knowledge Construction**: Skills as building blocks for agent ecosystems

## 🎯 What You'll Learn

### **Core Concepts**

- **Agent Skills Structure** - How to define what an agent can do
- **Capability Metadata** - Input parameters, output formats, descriptions
- **Skill Discovery** - How other agents find and evaluate capabilities
- **SDK Integration** - Using official A2A SDK for skill definitions

### **Practical Skills**

- Define skills using `AgentSkill` objects from A2A SDK
- Structure skill metadata for optimal discoverability
- Test skill definitions visually in browser
- Prepare foundation for agent executor patterns

### **Strategic Understanding**

- Why skills are the foundation of multi-agent systems
- How skill definitions enable autonomous agent collaboration
- The relationship between skills and actual implementation

## 📋 Prerequisites

✅ **Completed**: [Step 01: Agent Card](../01_agent_card/) - Agent discovery foundation  
✅ **Knowledge**: Basic JSON structure and HTTP servers  
✅ **Tools**: UV package manager, Python 3.10+, web browser

## 🎯 Success Criteria

By the end of this step, you'll have:

### **Technical Deliverables**

- [ ] Agent card with 2-3 well-defined skills
- [ ] Skills using official A2A SDK `AgentSkill` objects
- [ ] Browser-testable endpoint at `/.well-known/agent-card.json`
- [ ] Proper skill metadata (parameters, outputs, descriptions)

### **Conceptual Mastery**

- [ ] Understand the role of skills in agent ecosystems
- [ ] Can explain skill discoverability patterns
- [ ] Ready to implement actual skill execution in Step 4

### **Learning Validation Questions**

1. **Analysis**: How do skills enable agent-to-agent collaboration?
2. **Application**: What skills would a calendar agent need to define?
3. **Synthesis**: How might agents use skill metadata to plan complex tasks?

## 🏗️ Learning Architecture

### **Phase 1: Conceptual Foundation (10 min)**

```
🧭 Mental Model Building
├── What are agent skills vs. agent capabilities?
├── How do skills relate to agent cards?
├── Why is skill metadata important for discovery?
└── Connection to multi-agent orchestration patterns
```

### **Phase 2: Hands-On Implementation (15 min)**

```
⚡ Active Construction
├── Install A2A SDK and import AgentSkill
├── Define 2-3 example skills with parameters
├── Add skills array to existing agent card
└── Test in browser for immediate feedback
```

### **Phase 3: Integration & Reflection (5 min)**

```
🔄 Knowledge Integration
├── Compare with Step 1's simple agent card
├── Predict how these skills will execute in Step 4
├── Consider multi-agent scenarios for Step 7
└── Document learning insights
```

## 💡 Pedagogical Scaffolding

### **Guided Discovery Questions**

- 🤔 **Before coding**: "What information would you need to use someone else's agent?"
- 🤔 **During coding**: "How specific should skill descriptions be?"
- 🤔 **After coding**: "How might agents automatically discover compatible skills?"

### **Metacognitive Prompts**

- **Self-Assessment**: "Can I explain what each skill does without looking at code?"
- **Transfer Planning**: "How would I add skills to a different type of agent?"
- **Connection Making**: "How do these skills prepare me for agent execution?"

## 🔄 Spaced Repetition Schedule

### **Immediate Review** (End of session)

- Review skill definitions and metadata structure
- Test agent card endpoint with skills included
- Verify understanding with success criteria checklist

### **Distributed Practice** (Next day)

- Modify skills and observe changes in agent card
- Add a new skill type and test discoverability
- Connect to Step 3's multiple agent patterns

### **Interleaved Review** (Before Step 4)

- Compare skills across different agent types
- Analyze how skills prepare for executor patterns
- Preview connection to multi-agent scenarios

## 🌟 Motivation & Relevance

### **Real-World Connection**

```
💼 Business Value
"Enterprise AI agents need to advertise their capabilities
for autonomous discovery and task delegation - skills are
the standardized way to enable AI-to-AI collaboration."
```

### **Personal Relevance**

```
🚀 Career Impact
"Understanding agent skill definition is foundational to
building agent ecosystems - this pattern applies across
all major AI frameworks and platforms."
```

### **Immediate Reward**

```
⚡ Quick Win
"See your agent's skills displayed in browser within 15 minutes -
visual feedback makes abstract concepts concrete."
```

## 🎮 Engagement Strategies

### **Gamification Elements**

- **Progress**: Visual skill definitions in browser
- **Achievement**: Complete skill metadata checklist
- **Mastery**: Predict how skills will execute in Step 4

### **Social Learning**

- **Peer Review**: Compare skill definitions with others
- **Teaching**: Explain skill structure to someone else
- **Collaboration**: Design skills for multi-agent scenarios

## 📊 Assessment Strategy

### **Formative Assessment** (During learning)

- Browser testing provides immediate feedback
- Self-check against technical deliverables
- Peer discussion of skill design choices

### **Summative Assessment** (End of step)

- Complete working agent card with skills
- Successful response to validation questions
- Ready to proceed to Step 3 multiple agents

### **Authentic Assessment** (Real-world application)

- Design skills for actual business use case
- Evaluate skill discoverability and usability
- Plan skill evolution for agent ecosystem

## 📖 Learning Resources

### **Primary Resources**

- [A2A Skills Specification](https://google-a2a.github.io/A2A/latest/specification/#agentskill-object-structure)
- [A2A Python SDK AgentSkill](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.types.AgentSkill)
- Step 1 Agent Card foundation

### **Extension Resources**

- [Agent Discovery Patterns](https://google-a2a.github.io/A2A/latest/topics/discovery/)
- Multi-agent coordination examples
- Enterprise skill taxonomy patterns

---

## 🚀 Ready to Begin?

**Next Action**: Create your first agent skill definition and see it working in your browser within 15 minutes!

```bash
cd 02_agent_skills/
# Follow the implementation guide to add skills to your agent card
```

**Remember**: Skills are the foundation that makes multi-agent systems possible. Every minute spent here pays dividends in Step 7's multi-agent demo! 🎯
