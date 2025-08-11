# Step 7: Multi-Agent System ⭐

**The main event - build a complete multi-agent system with framework diversity**

## 🎯 Goal

Build a **complete multi-agent system** where a host agent (ADK) coordinates with 3 remote agents built using different frameworks (ADK, CrewAI, LangGraph) to schedule a pickleball game.

**This step demonstrates A2A's core value proposition: framework-agnostic agent communication.**

## 🏓 Scenario: Pickleball Scheduling

**User**: "What time is everyone available tomorrow for pickleball?"

**System Architecture**:

```
┌─────────────────┐    A2A     ┌──────────────────┐
│   Host Agent    │◄────────────►│   Carly (ADK)    │
│     (ADK)       │             │  Calendar Agent  │
│  Orchestrator   │             └──────────────────┘
│                 │    A2A     ┌──────────────────┐
│ - Discovery     │◄────────────►│  Nate (CrewAI)   │
│ - Scheduling    │             │  Calendar Agent  │
│ - Court Booking │             └──────────────────┘
│                 │    A2A     ┌──────────────────┐
│                 │◄────────────►│Caitlyn(LangGraph)│
└─────────────────┘             │  Calendar Agent  │
                                └──────────────────┘
```

## 🚀 Quick Demo

### Terminal Setup

```bash
# Terminal 1: Start Carly (ADK agent)
cd carly_adk
uv run main.py
# → Runs on http://localhost:8001

# Terminal 2: Start Nate (CrewAI agent)
cd nate_crewai
uv run main.py
# → Runs on http://localhost:8002

# Terminal 3: Start Caitlyn (LangGraph agent)
cd caitlyn_langgraph
uv run main.py
# → Runs on http://localhost:8003

# Terminal 4: Start Host Orchestrator
cd host_agent
adk web
# → Runs on http://localhost:8000
```

### Test the System

```bash
# Option 1: Use the ADK web interface
# Visit http://localhost:8000
# Ask: "What time is everyone available tomorrow for pickleball?"

# Option 2: Direct API call
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is everyone available tomorrow for pickleball?"}'
```

## 🔍 How It Works

### 1. **Agent Discovery**

Host agent fetches agent cards from each remote agent:

```bash
curl http://localhost:8001/.well-known/agent-card.json  # Carly
curl http://localhost:8002/.well-known/agent-card.json  # Nate
curl http://localhost:8003/.well-known/agent-card.json  # Caitlyn
```

### 2. **Parallel Coordination**

Host sends A2A messages to all agents simultaneously:

```python
# Pseudo-code for host agent
responses = await asyncio.gather(
    send_a2a_message("Carly", "Are you free tomorrow 8-10 PM?"),
    send_a2a_message("Nate", "Are you free tomorrow 8-10 PM?"),
    send_a2a_message("Caitlyn", "Are you free tomorrow 8-10 PM?")
)
```

### 3. **Response Aggregation**

Host collects all responses and finds optimal time slot:

```python
# Analyze responses
available_times = find_common_availability(responses)
court_availability = check_court_availability(available_times)
optimal_time = select_best_time(available_times, court_availability)
```

### 4. **Booking Execution**

Host books the court and confirms with everyone:

```python
booking_result = book_court(optimal_time)
notify_all_agents(f"Booked court for {optimal_time}")
```

## 📁 Directory Structure

```
07_multi_agent_system/
├── README.md                    # This file
├── demo-script.sh              # Automated demo runner
├── test-all.sh                 # Test script for the system
├── docker-compose.yml          # Run entire system with Docker
│
├── host_agent/                 # ADK orchestrator
│   ├── main.py                 # ADK app entry point
│   ├── agent.py                # Host agent logic
│   ├── tools.py                # Court booking tools + A2A messaging
│   └── .well-known/
│       └── agent.json          # Host agent card
│
├── carly_adk/                  # ADK calendar agent
│   ├── main.py                 # Server entry point
│   ├── agent.py                # Carly's agent logic
│   ├── executor.py             # A2A executor wrapper
│   ├── tools.py                # Calendar tools
│   └── .well-known/
│       └── agent.json          # Carly's agent card
│
├── nate_crewai/                # CrewAI calendar agent
│   ├── main.py                 # Server entry point
│   ├── agent.py                # Nate's CrewAI agent
│   ├── executor.py             # A2A executor wrapper
│   ├── tools.py                # Availability tools
│   └── .well-known/
│       └── agent.json          # Nate's agent card
│
└── caitlyn_langgraph/          # LangGraph calendar agent
    ├── main.py                 # Server entry point
    ├── agent.py                # Caitlyn's LangGraph agent
    ├── executor.py             # A2A executor wrapper
    ├── tools.py                # Scheduling tools
    └── .well-known/
        └── agent.json          # Caitlyn's agent card
```

## 🧪 Testing & Validation

### Individual Agent Tests

```bash
# Test each agent independently
./test-individual-agents.sh

# Or manually:
curl -X POST http://localhost:8001/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Are you free at 8 PM tomorrow?"}'
```

### Multi-Agent Flow Test

```bash
# Test complete orchestration
./test-multi-agent-flow.sh

# Validates:
# 1. Agent discovery works
# 2. Parallel messaging succeeds
# 3. Response aggregation works
# 4. Court booking completes
```

### A2A Protocol Validation

```bash
# Verify A2A compliance
python validate-a2a-compliance.py

# Checks:
# - Agent cards are valid JSON
# - All required A2A endpoints exist
# - Message format compliance
# - Error handling
```

## 🎯 Learning Objectives

After completing this step, you'll understand:

### **Technical Skills**

- ✅ **Multi-agent orchestration** patterns
- ✅ **Framework integration** via A2A (ADK + CrewAI + LangGraph)
- ✅ **Parallel agent communication**
- ✅ **Response aggregation** and decision making
- ✅ **A2A compliance** across different frameworks

### **Architectural Patterns**

- ✅ **Host-coordinator** pattern for multi-agent systems
- ✅ **Framework abstraction** through A2A protocol
- ✅ **Service discovery** and capability matching
- ✅ **Async coordination** with parallel execution

### **Real-World Application**

- ✅ **Scheduling optimization** across multiple agents
- ✅ **Resource booking** with availability checking
- ✅ **User experience** with natural language interaction
- ✅ **Error handling** in distributed agent systems

## 🚧 Implementation Notes

### **Agent Executor Pattern**

Each remote agent implements the same A2A interface:

```python
class AgentExecutor:
    async def execute(self, context, event_queue):
        # 1. Extract user query from A2A message
        # 2. Run framework-specific agent logic
        # 3. Convert response to A2A format
        # 4. Update task with artifacts
```

### **Framework Abstraction**

The host doesn't need to know framework details:

```python
# Host sees all agents the same way through A2A
async def send_message(agent_name: str, message: str) -> str:
    # A2A handles framework differences
    return await a2a_client.send_message(agent_name, message)
```

### **Capability-Based Routing**

Host selects agents based on advertised skills:

```python
# Find agents with calendar skills
calendar_agents = [agent for agent in agents
                  if "check_availability" in agent.skills]
```

## 🔥 Key Innovations

### **1. Framework Independence**

- Same A2A protocol works across ADK, CrewAI, LangGraph
- Add new frameworks without changing existing code
- Vendor-neutral multi-agent systems

### **2. Black Box Communication**

- Agents don't need to know each other's internals
- Framework-specific details hidden behind A2A
- Clean separation of concerns

### **3. Real-World Complexity**

- Not a toy example - handles real scheduling constraints
- Multiple agents with different specializations
- Parallel execution with aggregation

### **4. Production Patterns**

- Proper error handling and timeouts
- Health checks and service discovery
- Logging and monitoring integration

## 📈 Next Steps

After mastering this multi-agent system:

1. **Step 8: Push Notifications** - Add async webhook support
2. **Step 9: Authentication** - Secure the agent network
3. **Step 10: Security Hardening** - Add TLS, signed cards
4. **Step 11: Latency Routing** - Optimize for performance
5. **Step 12: gRPC & Production** - Deploy at scale

## 🎉 Success Criteria

You've completed this step when:

- ✅ All 4 agents start successfully on different ports
- ✅ Host agent discovers all remote agent capabilities
- ✅ Multi-agent scheduling request completes end-to-end
- ✅ System handles agent failures gracefully
- ✅ You understand how to add agents with different frameworks

---

**🚀 Ready to build your multi-agent system? Start with [Host Agent Setup](./host_agent/) or run `./demo-script.sh` for a guided experience!**

_This is where A2A really shines - enabling agents built with different frameworks to collaborate seamlessly._ ⭐
