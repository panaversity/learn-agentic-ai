# Step 09: Agent Discovery 🔍

**Goal**: Implement agent discovery mechanisms and registry patterns for multi-agent systems.

## 🎯 What You'll Learn

- Agent discovery via `.well-known/agent-card.json` endpoints
- Agent registry patterns for centralized discovery
- Dynamic agent capability detection
- Service mesh patterns for A2A agents
- Real-world multi-agent orchestration

## 🔍 Agent Discovery Mechanisms

### 1. Standard Discovery Pattern

```
GET https://agent-host/.well-known/agent-card.json
→ Returns AgentCard with capabilities and endpoints
```

### 2. Registry-Based Discovery

```
Registry Server: Maintains list of all available agents
Agents: Register themselves with capabilities
Clients: Query registry to discover agents by skill/capability
```

## 📁 Project Structure

```
09_agent_discovery/
├── README.md                    # This guide
├── pyproject.toml              # UV project configuration
├── registry_server.py          # Central agent registry
├── discoverable_agent.py       # Agent that registers itself
├── math_agent.py              # Specialized math agent
├── language_agent.py          # Language processing agent
├── discovery_client.py        # Client that discovers agents
├── test_discovery.py          # Test multi-agent discovery
└── requirements.txt           # Dependencies
```

## 🚀 Implementation

### 1. Setup Project

```bash
cd 09_agent_discovery
uv sync
```

### 2. Start the Registry Server

```bash
uv run python registry_server.py
# Runs on http://localhost:8000
```

### 3. Register Agents (New Terminals)

```bash
# Terminal 2: Math Agent
uv run python math_agent.py
# Registers with registry and runs on port 8001

# Terminal 3: Language Agent
uv run python language_agent.py
# Registers with registry and runs on port 8002
```

### 4. Test Discovery

```bash
# Terminal 4: Discovery Client
uv run python discovery_client.py

# Or run automated tests
uv run python test_discovery.py
```

## 🔧 Key Concepts

### Agent Registry Pattern

- **Centralized Discovery**: Single registry tracks all agents
- **Capability Indexing**: Find agents by skills/capabilities
- **Health Monitoring**: Track agent availability
- **Load Balancing**: Route requests to available agents

### Direct Discovery Pattern

- **Well-Known Endpoints**: Standard `.well-known/agent-card.json`
- **Peer Discovery**: Agents discover each other directly
- **Service Mesh**: Network of interconnected agents
- **Capability Broadcasting**: Agents announce their capabilities

### Discovery Protocols

- **Registration**: Agents register capabilities with registry
- **Query**: Clients query registry for agents with specific skills
- **Resolution**: Registry returns agent endpoints and capabilities
- **Health Check**: Periodic agent availability verification

## 📊 Example Discovery Flow

```
1. Math Agent starts → Registers with Registry
2. Language Agent starts → Registers with Registry
3. Client needs "math" skill → Queries Registry
4. Registry returns Math Agent endpoint
5. Client connects directly to Math Agent
6. Math Agent processes calculation request
```

## 🎯 Testing

### Manual Testing

```bash
# Check registry
curl http://localhost:8000/registry

# Check specific agent discovery
curl http://localhost:8001/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json

# Query registry for specific capabilities
curl "http://localhost:8000/discover?capability=mathematics"
curl "http://localhost:8000/discover?capability=language_processing"
```

### Automated Testing

```bash
uv run python test_discovery.py
```

## 🔍 Expected Results

### Registry Response

```json
{
  "agents": [
    {
      "id": "math_agent_001",
      "endpoint": "http://localhost:8001",
      "capabilities": ["mathematics", "calculations"],
      "status": "healthy",
      "last_seen": "2024-01-15T10:30:00Z"
    },
    {
      "id": "language_agent_001",
      "endpoint": "http://localhost:8002",
      "capabilities": ["language_processing", "translation"],
      "status": "healthy",
      "last_seen": "2024-01-15T10:30:01Z"
    }
  ]
}
```

### Discovery Query Response

```json
{
  "capability": "mathematics",
  "agents": [
    {
      "id": "math_agent_001",
      "endpoint": "http://localhost:8001",
      "confidence": 1.0,
      "load": "low"
    }
  ]
}
```

## 🌟 Real-World Applications

- **Microservices Discovery**: Find services by capability
- **Agent Marketplace**: Browse available AI agents
- **Load Balancing**: Distribute requests across agent instances
- **Fault Tolerance**: Automatically failover to healthy agents
- **Capability Matching**: Route requests to most suitable agents

## 📖 Next Steps

- **Step 10**: [Agent-to-Agent Communication](../10_agent_to_agent/) - Direct agent communication patterns
- **Step 11**: [Authentication](../11_authentication/) - Secure agent communication

## 📚 References

- [A2A Agent Discovery Specification](https://google-a2a.github.io/A2A/specification/#agent-discovery)
- [Service Discovery Patterns](https://microservices.io/patterns/service-discovery/)
- [Agent Ecosystem Design](https://google-a2a.wiki/technical-documentation/#agent-collaboration)
