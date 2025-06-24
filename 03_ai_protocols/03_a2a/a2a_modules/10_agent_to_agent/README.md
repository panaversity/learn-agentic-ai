# Step 10: Agent-to-Agent Communication 🤝

**Goal**: Implement direct agent-to-agent communication patterns for collaborative multi-agent systems.

## 🎯 What You'll Learn

- Direct A2A protocol messaging between agents
- Agent orchestration and delegation patterns
- Collaborative task execution across agents
- Agent coordination protocols
- Multi-agent workflow patterns

## 🔄 Agent-to-Agent Communication Patterns

### 1. Direct Messaging
```
Agent A → message/send → Agent B
Agent B → processes → responds with result
```

### 2. Task Delegation
```
Orchestrator Agent → creates task → Specialist Agent
Specialist Agent → executes → reports back to Orchestrator
```

### 3. Collaborative Processing
```
Agent A → partial result → Agent B → enriches → Agent C → finalizes
```

### 4. Agent Chains
```
Input → Agent 1 → intermediate → Agent 2 → intermediate → Agent 3 → Output
```

## 📁 Project Structure

```
10_agent_to_agent/
├── README.md                    # This guide
├── pyproject.toml              # UV project configuration
├── orchestrator_agent.py       # Main coordination agent
├── math_specialist.py          # Math processing agent
├── language_specialist.py      # Language processing agent
├── data_analyst.py             # Data analysis agent
├── workflow_coordinator.py     # Multi-agent workflow manager
├── test_collaboration.py       # Test agent collaboration
└── requirements.txt           # Dependencies
```

## 🚀 Implementation

### 1. Setup Project
```bash
cd 10_agent_to_agent
uv sync
```

### 2. Start Specialist Agents (Multiple Terminals)
```bash
# Terminal 1: Math Specialist
uv run python math_specialist.py
# Runs on http://localhost:8001

# Terminal 2: Language Specialist  
uv run python language_specialist.py
# Runs on http://localhost:8002

# Terminal 3: Data Analyst
uv run python data_analyst.py
# Runs on http://localhost:8003
```

### 3. Start Orchestrator
```bash
# Terminal 4: Orchestrator Agent
uv run python orchestrator_agent.py
# Runs on http://localhost:8000
```

### 4. Test Agent Collaboration
```bash
# Terminal 5: Test Client
uv run python test_collaboration.py

# Or manual testing
curl -X POST http://localhost:8000/a2a/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"text": "Analyze sales data: [100, 150, 200] and create a summary report"}]
      }
    }
  }'
```

## 🔧 Key Communication Patterns

### Direct Agent Messaging
- **Peer-to-Peer**: Agents communicate directly using A2A protocol
- **Request-Response**: Synchronous communication for immediate results
- **Fire-and-Forget**: Asynchronous messaging for background tasks
- **Streaming**: Real-time data flow between agents

### Agent Orchestration
- **Coordinator Pattern**: Central agent manages workflow
- **Pipeline Pattern**: Sequential processing through agent chain
- **Scatter-Gather**: Distribute work, collect results
- **Conditional Routing**: Route to agents based on content/capability

### Collaboration Protocols
- **Task Handoff**: Transfer task context between agents
- **Result Aggregation**: Combine outputs from multiple agents
- **Error Handling**: Fallback chains and error recovery
- **State Synchronization**: Maintain consistency across agents

## 📊 Example Collaboration Flow

### Complex Analysis Workflow
```
1. User Request → Orchestrator Agent
2. Orchestrator → analyzes request type
3. Orchestrator → delegates to Data Analyst (extract insights)
4. Data Analyst → processes data → returns insights  
5. Orchestrator → delegates to Math Specialist (calculations)
6. Math Specialist → performs calculations → returns results
7. Orchestrator → delegates to Language Specialist (generate report)
8. Language Specialist → creates summary → returns formatted report
9. Orchestrator → combines all results → responds to user
```

### Multi-Step Processing Chain
```
Input: "Calculate average of [10,20,30] and explain in French"

Flow:
User → Orchestrator → Math Specialist → Language Specialist → User
     ↓              ↓                  ↓
  "Calculate     "Average is 20"   "La moyenne est 20. 
   average..."                      Cela signifie..."
```

## 🎯 Testing Scenarios

### Manual Testing
```bash
# Test direct agent communication
curl -X POST http://localhost:8001/a2a/message/send \
  -H "Content-Type: application/json" \
  -d '{"method": "message/send", "params": {"message": {"role": "user", "parts": [{"text": "Calculate 15 + 25"}]}}}'

# Test orchestrated workflow
curl -X POST http://localhost:8000/a2a/message/send \
  -H "Content-Type: application/json" \
  -d '{"method": "message/send", "params": {"message": {"role": "user", "parts": [{"text": "Analyze data [1,2,3,4,5] and create a French summary"}]}}}'
```

### Automated Testing
```bash
uv run python test_collaboration.py
```

## 🔍 Expected Results

### Simple Math Delegation
```json
{
  "id": "req_001",
  "result": {
    "message": {
      "role": "agent", 
      "parts": [{"text": "The calculation 15 + 25 equals 40."}]
    }
  }
}
```

### Complex Multi-Agent Workflow
```json
{
  "id": "req_002",
  "result": {
    "message": {
      "role": "agent",
      "parts": [{
        "text": "Analysis Complete:\n\nData Insights: Mean=3, Trend=Increasing\nCalculations: Sum=15, Average=3.0\nSummary (French): Les données montrent une tendance croissante avec une moyenne de 3.0. La somme totale est 15."
      }]
    },
    "workflow": {
      "steps": ["data_analysis", "calculations", "language_processing"],
      "agents_used": ["data_analyst", "math_specialist", "language_specialist"],
      "total_time": "1.2s"
    }
  }
}
```

## 🌟 Real-World Applications

- **Content Processing Pipeline**: Text → Analysis → Translation → Publishing
- **Financial Analysis**: Data → Calculations → Risk Assessment → Report
- **Customer Service**: Query → Intent → Knowledge Base → Response Generation
- **Research Workflow**: Data Collection → Analysis → Synthesis → Documentation
- **Manufacturing Control**: Sensor Data → Analysis → Decision → Action

## 📈 Collaboration Benefits

- **Specialization**: Each agent focuses on specific capabilities
- **Scalability**: Add agents without changing existing ones
- **Reliability**: Fault tolerance through agent redundancy
- **Flexibility**: Dynamic workflow routing based on requirements
- **Efficiency**: Parallel processing across multiple agents

## 🔧 Advanced Patterns

### Agent Mesh Network
- Agents discover and communicate with any other agent
- Dynamic routing based on agent availability and load
- Self-healing network with automatic failover

### Hierarchical Coordination
- Multi-level agent hierarchies (Team → Department → Company)
- Escalation patterns for complex tasks
- Authority delegation and permission management

### Event-Driven Collaboration
- Agents react to events from other agents
- Publish-subscribe patterns for loose coupling
- Event sourcing for audit trails and replay

## 📖 Next Steps

- **Step 11**: [Authentication](../11_authentication/) - Secure agent communication
- **Step 12**: [Enterprise Features](../12_enterprise_features/) - Production deployment

## 📚 References

- [A2A Multi-Agent Communication](https://google-a2a.wiki/technical-documentation/#agent-collaboration)
- [Agent Coordination Patterns](https://google-a2a.github.io/A2A/specification/#multi-agent-systems)
- [Distributed Systems Patterns](https://microservices.io/patterns/) 