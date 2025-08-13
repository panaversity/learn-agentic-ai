# Host Agent (ADK Framework) 🎭

**The orchestrator - coordinates multi-agent Table Tennis scheduling using A2A protocol**

> **🎯 Learning Objective**: Build the central host agent that discovers, coordinates, and manages multiple specialized agents using Google's Agent Development Kit (ADK) framework.

## 🧠 Learning Sciences Foundation

### **Orchestration Learning Theory**

- **Systems Coordination**: Understanding how to manage complex multi-agent interactions
- **Delegation Patterns**: Learning to assign tasks to appropriate specialized agents
- **Integration Complexity**: Managing the complexity of cross-framework communication

### **Leadership and Coordination Skills**

- **Task Decomposition**: Breaking complex goals into agent-specific tasks
- **Resource Management**: Efficiently utilizing available agent capabilities
- **Conflict Resolution**: Handling competing priorities and resource constraints

## 🎯 What You'll Learn

### **Core Concepts**

- **Host-Coordinator Pattern** - Central orchestration of distributed agents
- **ADK Framework Integration** - Using Google's official agent framework
- **A2A Discovery and Routing** - Finding and communicating with remote agents
- **Task Orchestration** - Coordinating parallel agent execution

### **Practical Skills**

- Build host agent using ADK framework
- Implement agent discovery for multiple remote agents
- Coordinate parallel task execution across frameworks
- Handle agent failures and graceful degradation

### **Strategic Understanding**

- Why host-coordinator patterns work for complex multi-agent scenarios
- How ADK simplifies agent development and A2A integration
- The benefits of framework-agnostic agent coordination

## 📋 Prerequisites

✅ **Completed**: Steps 1-6 - Agent cards through streaming tasks  
✅ **Knowledge**: A2A protocol fundamentals and multi-agent concepts  
✅ **Framework**: Basic understanding of ADK patterns  
✅ **Tools**: UV package manager, Python 3.10+, ADK SDK

## 🎯 Host Agent Responsibilities

### **Primary Functions**

```
🎭 Host Agent Coordination
├── 1. Agent Discovery: Find Carly, Nate, and Caitlyn
├── 2. Task Delegation: Assign specialized tasks to each agent
├── 3. Response Aggregation: Collect and combine agent responses
├── 4. Decision Making: Synthesize information and make recommendations
├── 5. User Interaction: Present final recommendations and handle user decisions
└── 6. Error Handling: Manage agent failures and retry scenarios
```

### **Table Tennis Scheduling Workflow**

```
🏓 Complete Scheduling Process
User: "What time is everyone available tomorrow for Table Tennis?"

Host Agent Workflow:
1. Parse user request and identify required information
2. Discover available agents (Carly, Nate, Caitlyn)
3. Send parallel requests:
   ├── Carly (ADK): "Check calendar availability for tomorrow"
   ├── Nate (CrewAI): "Check team calendar for conflicts"
   └── Caitlyn (LangGraph): "Find optimal scheduling windows"
4. Query court availability using local tools
5. Aggregate responses and find optimal time slot
6. Present recommendation: "Everyone available at 8 PM, Court 1 booked!"
7. Handle user confirmation and finalize booking
```

## 🏗️ ADK Implementation Pattern

### **Host Agent Structure**

```python
from google.adk import Agent, Skill, Context
from a2a import AgentCard, A2AClient
import asyncio
from typing import List, Dict, Any

class Table TennisHostAgent(Agent):
    def __init__(self):
        super().__init__(
            agent_id="Table Tennis-host",
            name="Table Tennis Coordinator"
        )
        self.a2a_client = A2AClient()
        self.discovered_agents = {}

    @Skill(name="coordinate_Table Tennis_scheduling")
    async def coordinate_scheduling(
        self,
        context: Context,
        request: str
    ) -> Dict[str, Any]:
        """Main coordination logic for Table Tennis scheduling"""

        # Step 1: Discover remote agents
        agents = await self._discover_agents()

        # Step 2: Extract scheduling requirements
        requirements = await self._parse_request(request)

        # Step 3: Delegate to specialized agents
        tasks = await self._create_agent_tasks(requirements)
        responses = await self._execute_parallel_tasks(tasks)

        # Step 4: Aggregate and synthesize
        availability = await self._aggregate_responses(responses)

        # Step 5: Check court availability
        courts = await self._check_court_availability(availability)

        # Step 6: Generate recommendation
        recommendation = await self._generate_recommendation(
            availability, courts
        )

        return {
            "recommendation": recommendation,
            "availability": availability,
            "courts": courts,
            "confidence": self._calculate_confidence(responses)
        }

    async def _discover_agents(self) -> Dict[str, str]:
        """Discover A2A agents using agent cards"""
        agent_endpoints = {
            "calendar": "http://localhost:8002",  # Carly (ADK)
            "team": "http://localhost:8003",      # Nate (CrewAI)
            "optimizer": "http://localhost:8004"  # Caitlyn (LangGraph)
        }

        discovered = {}
        for agent_type, endpoint in agent_endpoints.items():
            try:
                agent_card = await self.a2a_client.get_agent_card(endpoint)
                discovered[agent_type] = {
                    "endpoint": endpoint,
                    "card": agent_card,
                    "capabilities": agent_card.get("skills", [])
                }
            except Exception as e:
                print(f"Failed to discover {agent_type} agent: {e}")

        return discovered

    async def _execute_parallel_tasks(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute tasks across multiple agents in parallel"""

        async def send_task(task):
            try:
                response = await self.a2a_client.send_message(
                    endpoint=task["endpoint"],
                    message=task["message"]
                )
                return {
                    "agent": task["agent"],
                    "success": True,
                    "response": response,
                    "latency": response.get("latency", 0)
                }
            except Exception as e:
                return {
                    "agent": task["agent"],
                    "success": False,
                    "error": str(e),
                    "latency": float('inf')
                }

        # Execute all tasks in parallel
        results = await asyncio.gather(*[
            send_task(task) for task in tasks
        ])

        return results
```

## 🎮 Testing Scenarios

### **Scenario 1: Complete Table Tennis Scheduling**

```bash
# Start host agent
cd host_agent/
python3 Table Tennis_host.py

# Test complete scheduling workflow
curl -X POST http://localhost:8001/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "content": "What time is everyone available tomorrow for Table Tennis?"
      }
    },
    "id": "Table Tennis-123"
  }'
```

### **Scenario 2: Agent Failure Handling**

```bash
# Stop one remote agent to test failure handling
pkill -f nate_crewai.py

# Test graceful degradation
curl -X POST http://localhost:8001/coordinate \
  -H "Content-Type: application/json" \
  -d '{"request": "Schedule Table Tennis with partial agent availability"}'
```

## 🌟 Motivation & Relevance

### **Real-World Connection**

```
🏢 Enterprise Orchestration
"This host agent pattern is how enterprise AI systems
coordinate specialized services - one agent for calendar,
another for resources, another for optimization."
```

### **Personal Relevance**

```
🚀 Architecture Skills
"Learning to build orchestration systems is a senior-level
skill. This pattern applies to microservices, serverless
functions, and any distributed system architecture."
```

### **Immediate Reward**

```
⚡ Multi-Agent Magic
"See your host agent coordinate 3 different AI frameworks
in real-time to solve a complex scheduling problem!"
```

## 📊 Success Metrics

### **Technical Validation**

- [ ] Host agent successfully discovers all remote agents
- [ ] Parallel task execution works across all frameworks
- [ ] Graceful handling of individual agent failures
- [ ] Complete Table Tennis scheduling workflow end-to-end

### **Performance Targets**

- [ ] Agent discovery: < 500ms for all 3 agents
- [ ] Parallel coordination: < 2s for complex scheduling
- [ ] Error recovery: < 1s to detect and handle failures
- [ ] User response: Complete workflow in < 5s

### **Integration Success**

- [ ] ADK framework properly integrated with A2A protocol
- [ ] Cross-framework communication working seamlessly
- [ ] Complex coordination patterns working reliably
- [ ] Ready for production deployment patterns

## 🎯 Advanced Coordination Patterns

### **Intelligent Task Distribution**

```python
async def _optimize_task_distribution(
    self,
    requirements: Dict[str, Any],
    agent_capabilities: Dict[str, List[str]]
) -> List[Dict[str, Any]]:
    """Optimally distribute tasks based on agent capabilities and load"""

    # Analyze agent capabilities and current load
    agent_scores = {}
    for agent_id, capabilities in agent_capabilities.items():
        # Score based on capability match and current load
        capability_score = self._calculate_capability_match(
            requirements, capabilities
        )
        load_score = await self._get_agent_load_score(agent_id)

        agent_scores[agent_id] = {
            "capability": capability_score,
            "load": load_score,
            "combined": capability_score * (1 - load_score)
        }

    # Create optimal task distribution
    return self._create_task_assignments(requirements, agent_scores)
```

### **Adaptive Timeout Management**

```python
class AdaptiveTimeoutManager:
    def __init__(self):
        self.agent_performance_history = {}
        self.base_timeout = 5.0  # seconds

    def get_timeout_for_agent(self, agent_id: str, task_complexity: str) -> float:
        """Calculate adaptive timeout based on agent performance history"""

        if agent_id not in self.agent_performance_history:
            return self.base_timeout

        history = self.agent_performance_history[agent_id]
        avg_response_time = sum(history) / len(history)

        # Add buffer based on task complexity
        complexity_multiplier = {
            "simple": 1.0,
            "medium": 1.5,
            "complex": 2.0
        }.get(task_complexity, 1.0)

        return min(
            avg_response_time * complexity_multiplier * 1.5,  # 50% buffer
            30.0  # Maximum timeout
        )
```

## 📖 Learning Resources

### **Primary Resources**

- [ADK Framework Documentation](https://google-adk.github.io/docs/)
- [A2A Multi-Agent Patterns](https://google-a2a.github.io/A2A/latest/topics/multi-agent/)
- [Host-Coordinator Pattern Guide](https://google-a2a.github.io/A2A/latest/patterns/host-coordinator/)

### **Extension Resources**

- Enterprise orchestration patterns and best practices
- ADK advanced features and integration guides
- Multi-agent system design principles

---

## 🚀 Ready to Build the Orchestrator?

**Next Action**: Implement the host agent and coordinate your first multi-agent system!

```bash
# Install ADK framework
pip install google-adk

# Start building the coordinator
python3 setup_host_agent.py
```

**Remember**: This host agent is the conductor of your multi-agent orchestra. The coordination patterns you build here are the foundation for enterprise-scale AI agent systems! 🎭
