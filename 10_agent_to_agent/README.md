# Step 10: Agent-to-Agent Communication 🤝

**Learning Objective**: Implement direct agent-to-agent communication using the official A2A Python SDK to enable sophisticated multi-agent collaboration and task delegation.

## 📚 Official A2A Reference

**Primary Documentation**: [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)  
**Client API Reference**: [A2AClient Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.client.A2AClient)  
**Streaming Guide**: [A2A Streaming & Asynchronous Operations](https://google-a2a.github.io/A2A/topics/streaming-asynchronous-operations/)

## 🎯 What You'll Learn

- Using `A2AClient` for direct agent communication
- Message sending and receiving with A2A SDK
- Implementing streaming communication patterns
- Task delegation and handoffs between agents
- Error handling and retry mechanisms
- Multi-agent workflow orchestration

## 🏗️ Project Structure

```
10_agent_to_agent/
├── README.md
├── pyproject.toml
├── src/
│   ├── coordinator_agent.py     # Central coordination agent
│   ├── specialist_agents.py     # Specialized worker agents
│   ├── communication_hub.py     # A2A communication utilities
│   └── workflow_manager.py      # Multi-agent workflow coordination
├── examples/
│   ├── basic_communication.py   # Simple A2A messaging
│   ├── task_delegation.py       # Task delegation patterns
│   ├── streaming_chat.py        # Streaming communication
│   └── multi_agent_workflow.py  # Complex workflows
├── tests/
│   ├── test_communication.py
│   └── test_workflows.py
└── agents/
    ├── research_agent.py        # Research specialist
    ├── analysis_agent.py        # Data analysis specialist
    └── summary_agent.py         # Content summarization
```

## 🚀 Quick Start

### 1. Initialize Project

```bash
cd 10_agent_to_agent
uv init a2a_communication
cd a2a_communication
uv add a2a fastapi uvicorn httpx
```

### 2. Start Agent Network

```bash
# Terminal 1: Start coordinator agent
uv run python src/coordinator_agent.py

# Terminal 2: Start specialist agents
uv run python src/specialist_agents.py

# Terminal 3: Test communication
uv run python examples/basic_communication.py
```

### 3. Test Multi-Agent Workflows

```bash
# Test task delegation
uv run python examples/task_delegation.py

# Test streaming communication
uv run python examples/streaming_chat.py

# Test complex workflows
uv run python examples/multi_agent_workflow.py
```

## 📋 Core Implementation

### Coordinator Agent (src/coordinator_agent.py)

```python
from a2a import Agent, AgentCard, AgentSkill, AgentProvider, AgentCapabilities
from a2a.server import A2AServer
from a2a.client import A2AClient, A2ACardResolver
import asyncio
import logging
import json
from typing import Dict, List, Optional

# Create coordinator agent card
coordinator_card = AgentCard(
    name="Multi-Agent Coordinator",
    version="1.0.0",
    description="Coordinates tasks between multiple specialized agents using A2A SDK",
    provider=AgentProvider(
        organization="A2A Learning Network",
        url="http://localhost:8100"
    ),
    url="http://localhost:8100",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        extensions=[]
    ),
    skills=[
        AgentSkill(
            id="delegate_task",
            name="Task Delegation",
            description="Delegate complex tasks to appropriate specialist agents",
            input_modes=["text"],
            output_modes=["text", "json"]
        ),
        AgentSkill(
            id="coordinate_workflow",
            name="Workflow Coordination",
            description="Coordinate multi-step workflows across multiple agents",
            input_modes=["text", "json"],
            output_modes=["text", "json"]
        )
    ]
)

class CoordinatorAgent:
    def __init__(self):
        self.agent = Agent(card=coordinator_card)
        self.resolver = A2ACardResolver()
        self.known_agents = {}  # Cache of available agents
        
        # Register skills
        self.agent.skill("delegate_task")(self.delegate_task)
        self.agent.skill("coordinate_workflow")(self.coordinate_workflow)
    
    async def discover_specialist_agents(self):
        """Discover and cache available specialist agents"""
        specialist_urls = [
            "http://localhost:8200",  # Research agent
            "http://localhost:8201",  # Analysis agent
            "http://localhost:8202"   # Summary agent
        ]
        
        for agent_url in specialist_urls:
            try:
                agent_card = await self.resolver.get_agent_card(agent_url)
                if agent_card:
                    self.known_agents[agent_card.name] = {
                        "url": agent_url,
                        "card": agent_card,
                        "client": A2AClient.get_client_from_agent_card_url(agent_url)
                    }
                    logging.info(f"✅ Discovered specialist: {agent_card.name}")
            except Exception as e:
                logging.warning(f"⚠️ Could not discover agent at {agent_url}: {e}")
    
    async def delegate_task(self, message, context):
        """Delegate a task to the most appropriate specialist agent"""
        try:
            task_description = message.content.strip()
            
            # Simple task routing logic (extend with ML-based routing)
            target_agent = None
            if any(keyword in task_description.lower() for keyword in ["research", "find", "search", "investigate"]):
                target_agent = "Research Specialist"
            elif any(keyword in task_description.lower() for keyword in ["analyze", "analysis", "calculate", "compute"]):
                target_agent = "Analysis Specialist"
            elif any(keyword in task_description.lower() for keyword in ["summarize", "summary", "brief", "overview"]):
                target_agent = "Summary Specialist"
            
            if target_agent and target_agent in self.known_agents:
                agent_info = self.known_agents[target_agent]
                client = agent_info["client"]
                
                # Find appropriate skill for the task
                skills = agent_info["card"].skills
                target_skill = skills[0].id if skills else "process"
                
                # Send task to specialist agent
                response = await client.send_message(
                    skill_id=target_skill,
                    message={
                        "content": task_description,
                        "role": "user",
                        "metadata": {"delegated_by": "coordinator"}
                    }
                )
                
                return {
                    "content": f"Task delegated to {target_agent}. Response: {response.get('content', 'No response')}",
                    "type": "text",
                    "metadata": {
                        "delegated_to": target_agent,
                        "specialist_response": response
                    }
                }
            else:
                return {
                    "content": f"No suitable specialist found for task: {task_description}",
                    "type": "text",
                    "metadata": {"available_agents": list(self.known_agents.keys())}
                }
        
        except Exception as e:
            return {
                "content": f"Error during task delegation: {str(e)}",
                "type": "error"
            }
    
    async def coordinate_workflow(self, message, context):
        """Coordinate a multi-step workflow across multiple agents"""
        try:
            workflow_request = json.loads(message.content) if message.content.startswith('{') else {"steps": [message.content]}
            steps = workflow_request.get("steps", [])
            
            results = []
            for i, step in enumerate(steps):
                step_result = await self.delegate_task(
                    type("Message", (), {"content": step})(),
                    context
                )
                results.append({
                    "step": i + 1,
                    "description": step,
                    "result": step_result
                })
                
                # Brief delay between steps
                await asyncio.sleep(0.5)
            
            return {
                "content": "Multi-step workflow completed",
                "type": "json",
                "metadata": {
                    "workflow_results": results,
                    "total_steps": len(steps)
                }
            }
        
        except Exception as e:
            return {
                "content": f"Error coordinating workflow: {str(e)}",
                "type": "error"
            }

async def main():
    logging.basicConfig(level=logging.INFO)
    
    coordinator = CoordinatorAgent()
    
    print("🎯 Starting Multi-Agent Coordinator...")
    print("🔗 Skills: delegate_task, coordinate_workflow")
    
    # Discover specialist agents
    await coordinator.discover_specialist_agents()
    print(f"📡 Discovered {len(coordinator.known_agents)} specialist agents")
    
    # Create A2A server
    server = A2AServer(coordinator.agent)
    
    # Start the server
    await server.start(host="0.0.0.0", port=8100)

if __name__ == "__main__":
    asyncio.run(main())
```

### Specialist Agents (src/specialist_agents.py)

```python
from a2a import Agent, AgentCard, AgentSkill, AgentProvider, AgentCapabilities
from a2a.server import A2AServer
import asyncio
import logging

# Research Specialist Agent
research_card = AgentCard(
    name="Research Specialist",
    version="1.0.0",
    description="Specialized agent for research and information gathering",
    provider=AgentProvider(
        organization="A2A Specialist Network",
        url="http://localhost:8200"
    ),
    url="http://localhost:8200",
    capabilities=AgentCapabilities(
        streaming=False,
        push_notifications=False,
        extensions=[]
    ),
    skills=[
        AgentSkill(
            id="research",
            name="Research Information",
            description="Research and gather information on specified topics",
            input_modes=["text"],
            output_modes=["text"]
        )
    ]
)

research_agent = Agent(card=research_card)

@research_agent.skill("research")
async def research_task(message, context):
    """Handle research tasks"""
    topic = message.content.strip()
    
    # Simulate research (in production, integrate with real research APIs)
    await asyncio.sleep(1)  # Simulate processing time
    
    research_results = f"""
Research Report on: {topic}

Key Findings:
- This is a comprehensive topic that requires detailed investigation
- Multiple perspectives and sources should be considered
- Current trends and developments are evolving rapidly
- Recommended for further analysis by specialist teams

Confidence Level: High
Sources: Simulated research database
    """.strip()
    
    return {
        "content": research_results,
        "type": "text",
        "metadata": {
            "research_topic": topic,
            "agent_type": "research_specialist",
            "processing_time": "1.0s"
        }
    }

# Analysis Specialist Agent
analysis_card = AgentCard(
    name="Analysis Specialist",
    version="1.0.0",
    description="Specialized agent for data analysis and computation",
    provider=AgentProvider(
        organization="A2A Specialist Network",
        url="http://localhost:8201"
    ),
    url="http://localhost:8201",
    capabilities=AgentCapabilities(
        streaming=False,
        push_notifications=False,
        extensions=[]
    ),
    skills=[
        AgentSkill(
            id="analyze",
            name="Data Analysis",
            description="Analyze data and provide computational insights",
            input_modes=["text"],
            output_modes=["text"]
        )
    ]
)

analysis_agent = Agent(card=analysis_card)

@analysis_agent.skill("analyze")
async def analyze_task(message, context):
    """Handle analysis tasks"""
    data_description = message.content.strip()
    
    # Simulate analysis (in production, integrate with real analysis tools)
    await asyncio.sleep(1.5)  # Simulate processing time
    
    analysis_results = f"""
Analysis Report for: {data_description}

Statistical Overview:
- Data pattern recognition: Identified significant trends
- Correlation analysis: Strong positive correlations detected
- Anomaly detection: 3 outliers identified and flagged
- Predictive modeling: 87% confidence in future projections

Recommendations:
1. Further data collection recommended
2. Consider additional variables for analysis
3. Implement monitoring for detected anomalies

Processing Method: Advanced Analytics Engine
    """.strip()
    
    return {
        "content": analysis_results,
        "type": "text",
        "metadata": {
            "analysis_subject": data_description,
            "agent_type": "analysis_specialist",
            "confidence_score": 0.87
        }
    }

# Summary Specialist Agent
summary_card = AgentCard(
    name="Summary Specialist",
    version="1.0.0",
    description="Specialized agent for content summarization and synthesis",
    provider=AgentProvider(
        organization="A2A Specialist Network",
        url="http://localhost:8202"
    ),
    url="http://localhost:8202",
    capabilities=AgentCapabilities(
        streaming=False,
        push_notifications=False,
        extensions=[]
    ),
    skills=[
        AgentSkill(
            id="summarize",
            name="Content Summarization",
            description="Summarize and synthesize content into key insights",
            input_modes=["text"],
            output_modes=["text"]
        )
    ]
)

summary_agent = Agent(card=summary_card)

@summary_agent.skill("summarize")
async def summarize_task(message, context):
    """Handle summarization tasks"""
    content = message.content.strip()
    
    # Simulate summarization (in production, use NLP models)
    await asyncio.sleep(0.8)  # Simulate processing time
    
    # Extract key points (simple simulation)
    sentences = content.split('.')[:3]  # Take first 3 sentences
    key_points = [sentence.strip() + "." for sentence in sentences if sentence.strip()]
    
    summary_result = f"""
Executive Summary

Key Points:
{chr(10).join(f"• {point}" for point in key_points)}

Overall Assessment:
The content covers important aspects that require stakeholder attention. 
Main themes focus on actionable insights and strategic considerations.

Word Count: Original ({len(content.split())} words) → Summary ({len(summary_result.split())} words)
Compression Ratio: {len(summary_result)/len(content):.2%}
    """.strip()
    
    return {
        "content": summary_result,
        "type": "text",
        "metadata": {
            "original_length": len(content),
            "summary_length": len(summary_result),
            "agent_type": "summary_specialist"
        }
    }

async def start_specialist_agent(agent, port, name):
    """Start a specialist agent on specified port"""
    logging.basicConfig(level=logging.INFO)
    
    print(f"🤖 Starting {name}...")
    print(f"🔧 Skills: {[skill.name for skill in agent.card.skills]}")
    print(f"📡 Listening on port: {port}")
    
    server = A2AServer(agent)
    await server.start(host="0.0.0.0", port=port)

async def main():
    """Start all specialist agents concurrently"""
    print("🚀 Starting A2A Specialist Agent Network...")
    
    # Start all agents concurrently
    await asyncio.gather(
        start_specialist_agent(research_agent, 8200, "Research Specialist"),
        start_specialist_agent(analysis_agent, 8201, "Analysis Specialist"),
        start_specialist_agent(summary_agent, 8202, "Summary Specialist")
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Communication Hub Utilities (src/communication_hub.py)

```python
from a2a.client import A2AClient, A2ACardResolver
import asyncio
import logging
from typing import Dict, List, Optional, Any

class A2ACommunicationHub:
    """Utility class for managing A2A communications between agents"""
    
    def __init__(self):
        self.resolver = A2ACardResolver()
        self.clients: Dict[str, A2AClient] = {}
        self.agent_cards: Dict[str, Any] = {}
    
    async def register_agent(self, agent_name: str, agent_url: str):
        """Register an agent for communication"""
        try:
            agent_card = await self.resolver.get_agent_card(agent_url)
            if agent_card:
                client = A2AClient.get_client_from_agent_card_url(agent_url)
                self.clients[agent_name] = client
                self.agent_cards[agent_name] = agent_card
                logging.info(f"✅ Registered agent: {agent_name}")
                return True
        except Exception as e:
            logging.error(f"❌ Failed to register {agent_name}: {e}")
        return False
    
    async def send_message_to_agent(
        self, 
        agent_name: str, 
        skill_id: str, 
        message_content: str,
        metadata: Optional[Dict] = None
    ):
        """Send a message to a specific agent"""
        if agent_name not in self.clients:
            raise ValueError(f"Agent {agent_name} not registered")
        
        client = self.clients[agent_name]
        
        message = {
            "content": message_content,
            "role": "user"
        }
        
        if metadata:
            message["metadata"] = metadata
        
        try:
            response = await client.send_message(skill_id=skill_id, message=message)
            return response
        except Exception as e:
            logging.error(f"❌ Failed to send message to {agent_name}: {e}")
            raise
    
    async def broadcast_message(
        self, 
        skill_id: str, 
        message_content: str,
        exclude_agents: Optional[List[str]] = None
    ):
        """Broadcast a message to all registered agents"""
        exclude_agents = exclude_agents or []
        results = {}
        
        for agent_name, client in self.clients.items():
            if agent_name in exclude_agents:
                continue
            
            try:
                response = await self.send_message_to_agent(
                    agent_name, skill_id, message_content
                )
                results[agent_name] = {"success": True, "response": response}
            except Exception as e:
                results[agent_name] = {"success": False, "error": str(e)}
        
        return results
    
    async def send_message_with_streaming(
        self, 
        agent_name: str, 
        skill_id: str, 
        message_content: str
    ):
        """Send a message with streaming response"""
        if agent_name not in self.clients:
            raise ValueError(f"Agent {agent_name} not registered")
        
        client = self.clients[agent_name]
        
        # Check if agent supports streaming
        agent_card = self.agent_cards[agent_name]
        if not agent_card.capabilities.streaming:
            logging.warning(f"Agent {agent_name} does not support streaming")
            return await self.send_message_to_agent(agent_name, skill_id, message_content)
        
        try:
            # Use streaming send_message method
            response_stream = await client.send_message_streaming(
                skill_id=skill_id,
                message={
                    "content": message_content,
                    "role": "user"
                }
            )
            return response_stream
        except Exception as e:
            logging.error(f"❌ Streaming failed for {agent_name}: {e}")
            raise
    
    async def get_agent_capabilities(self, agent_name: str) -> Optional[Dict]:
        """Get capabilities of a registered agent"""
        if agent_name in self.agent_cards:
            card = self.agent_cards[agent_name]
            return {
                "name": card.name,
                "skills": [{"id": skill.id, "name": skill.name} for skill in card.skills],
                "capabilities": {
                    "streaming": card.capabilities.streaming,
                    "push_notifications": card.capabilities.push_notifications
                }
            }
        return None
    
    def list_registered_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self.clients.keys())

# Example usage functions
async def demo_communication_hub():
    """Demonstrate the communication hub functionality"""
    hub = A2ACommunicationHub()
    
    # Register agents
    agents = [
        ("Coordinator", "http://localhost:8100"),
        ("Research", "http://localhost:8200"),
        ("Analysis", "http://localhost:8201"),
        ("Summary", "http://localhost:8202")
    ]
    
    print("🔗 A2A Communication Hub Demo")
    print("=" * 40)
    
    # Register all agents
    for name, url in agents:
        success = await hub.register_agent(name, url)
        if success:
            print(f"✅ Registered: {name}")
        else:
            print(f"❌ Failed to register: {name}")
    
    # Test direct communication
    print("\n📡 Testing direct communication...")
    try:
        response = await hub.send_message_to_agent(
            "Research", 
            "research", 
            "Research the latest trends in artificial intelligence"
        )
        print(f"✅ Research response: {response.get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Communication failed: {e}")
    
    # Test broadcast
    print("\n📢 Testing broadcast communication...")
    results = await hub.broadcast_message(
        "process",  # Generic skill name
        "Process this broadcast message",
        exclude_agents=["Coordinator"]  # Exclude coordinator from broadcast
    )
    
    for agent_name, result in results.items():
        if result["success"]:
            print(f"✅ {agent_name}: Responded successfully")
        else:
            print(f"❌ {agent_name}: {result['error']}")

if __name__ == "__main__":
    asyncio.run(demo_communication_hub())
```

## 🧪 Testing Examples

### Basic Communication Test (examples/basic_communication.py)

```python
import asyncio
from src.communication_hub import A2ACommunicationHub

async def main():
    print("🤝 A2A Basic Communication Test")
    print("=" * 35)
    
    hub = A2ACommunicationHub()
    
    # Register coordinator and one specialist
    await hub.register_agent("Coordinator", "http://localhost:8100")
    await hub.register_agent("Research", "http://localhost:8200")
    
    print(f"📋 Registered agents: {hub.list_registered_agents()}")
    
    # Test delegation through coordinator
    print("\n1. Testing task delegation...")
    try:
        response = await hub.send_message_to_agent(
            "Coordinator",
            "delegate_task",
            "Research the benefits of agent-to-agent communication"
        )
        print(f"✅ Delegation response: {response.get('content', 'No response')}")
    except Exception as e:
        print(f"❌ Delegation failed: {e}")
    
    # Test direct communication
    print("\n2. Testing direct communication...")
    try:
        response = await hub.send_message_to_agent(
            "Research",
            "research",
            "Latest developments in multi-agent systems"
        )
        print(f"✅ Direct response: {response.get('content', 'No response')[:150]}...")
    except Exception as e:
        print(f"❌ Direct communication failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Task Delegation Example (examples/task_delegation.py)

```python
import asyncio
from src.communication_hub import A2ACommunicationHub

async def main():
    print("🎯 A2A Task Delegation Demo")
    print("=" * 30)
    
    hub = A2ACommunicationHub()
    
    # Register all agents
    agents = [
        ("Coordinator", "http://localhost:8100"),
        ("Research", "http://localhost:8200"),
        ("Analysis", "http://localhost:8201"),
        ("Summary", "http://localhost:8202")
    ]
    
    for name, url in agents:
        await hub.register_agent(name, url)
    
    # Test different types of task delegation
    test_tasks = [
        "Research the impact of climate change on agriculture",
        "Analyze the sales data from the last quarter",
        "Summarize the key findings from the market research report"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. Delegating task: {task}")
        
        try:
            response = await hub.send_message_to_agent(
                "Coordinator",
                "delegate_task",
                task
            )
            
            print(f"✅ Task completed successfully")
            print(f"📄 Response: {response.get('content', 'No response')[:200]}...")
            
            # Check metadata for delegation info
            metadata = response.get('metadata', {})
            if 'delegated_to' in metadata:
                print(f"🎯 Delegated to: {metadata['delegated_to']}")
        
        except Exception as e:
            print(f"❌ Task delegation failed: {e}")
        
        await asyncio.sleep(1)  # Brief pause between tasks

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔍 Key Learning Points

### 1. A2A SDK Client Management
- Using `A2AClient.get_client_from_agent_card_url()` for automatic client creation
- Proper client lifecycle management
- Error handling for communication failures

### 2. Message Structure and Metadata
- Standard A2A message format with content, role, and metadata
- Passing context between agents through metadata
- Response handling and error propagation

### 3. Agent Discovery Integration
- Combining `A2ACardResolver` with communication patterns
- Dynamic agent discovery and client creation
- Capability-based communication routing

### 4. Streaming and Async Patterns
- Using `send_message_streaming()` for real-time communication
- Handling async agent responses
- Managing concurrent agent interactions

## 🎯 Success Criteria

- [ ] Coordinator agent successfully delegating tasks to specialists
- [ ] Direct agent-to-agent communication working via A2A SDK
- [ ] Task delegation based on content analysis
- [ ] Multi-step workflows coordinated across agents
- [ ] Error handling and retry mechanisms implemented
- [ ] Streaming communication patterns demonstrated

## 🔗 Next Steps

After mastering agent-to-agent communication, proceed to **[Step 11: Authentication](../11_authentication/README.md)** to implement secure authentication mechanisms for agent networks.

## 📚 Additional Resources

- [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)
- [A2AClient API Reference](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.client.A2AClient)
- [A2A Streaming Guide](https://google-a2a.github.io/A2A/topics/streaming-asynchronous-operations/)
- [Multi-Agent Workflow Patterns](https://google-a2a.github.io/A2A/topics/life-of-a-task/) 