# Step 12: MCP-A2A Bridge - Protocol Convergence 🌉

**Build unified agents that expose both MCP and A2A protocols, bridging agent-to-context and agent-to-agent communication**

> **🎯 Learning Objective**: Master the integration of Model Context Protocol (MCP) and Agent-to-Agent (A2A) protocols in a single agent architecture, enabling seamless context management and agent collaboration.

## 🧠 Learning Sciences Foundation

### **Protocol Integration Learning**
- **Unified Interface Design**: Creating consistent APIs across different protocol paradigms
- **Context-Agent Bridge Patterns**: Connecting agent-to-context with agent-to-agent workflows
- **Architectural Convergence**: Understanding when and how to combine complementary protocols

### **Cognitive Load Management**
- **Single Agent, Dual Protocols**: Reducing complexity through unified implementation
- **Protocol Translation**: Converting between MCP context operations and A2A agent messages
- **Seamless User Experience**: Hiding protocol complexity behind intuitive interfaces

## 🎯 What You'll Learn

### **Core Concepts**
- **MCPAgent Pattern** - Agents that implement both MCP and A2A protocols
- **Protocol Bridging** - Translating between agent-context and agent-agent communication
- **Unified API Design** - Single endpoint serving multiple protocol standards
- **Context-Aware Agent Networks** - Agents that share context and collaborate simultaneously

### **Practical Skills**
- Implement dual-protocol agents (MCP + A2A)
- Bridge MCP context operations with A2A agent messaging
- Design unified APIs that serve both protocols efficiently
- Create context-sharing patterns across agent networks

### **Strategic Understanding**
- When to use MCP vs A2A vs unified approaches
- Architecture patterns for protocol convergence
- Performance implications of dual-protocol implementations

## 📋 Prerequisites

✅ **Knowledge**: MCP protocol fundamentals and A2A agent implementation  
✅ **Understanding**: Context management vs agent collaboration patterns  
✅ **Tools**: UV package manager, Python 3.10+, MCP SDK, A2A libraries  

## 🎯 Success Criteria

By the end of this step, you'll have:

### **Technical Deliverables**
- [ ] MCPAgent that implements both MCP and A2A protocols
- [ ] Protocol bridge that translates MCP context to A2A messages
- [ ] Unified API endpoints serving both protocol types
- [ ] Context-sharing patterns across multi-agent networks

### **Integration Architecture**
- [ ] Single server exposing both `/.well-known/agent-card.json` and MCP endpoints
- [ ] A2A messages that trigger MCP context operations
- [ ] MCP tools that invoke A2A agent collaboration
- [ ] Seamless protocol switching based on request type

### **Performance Optimization**
- [ ] Efficient protocol detection and routing
- [ ] Shared context caching across protocols
- [ ] Optimized message translation pipelines
- [ ] Protocol-specific performance monitoring

### **Learning Validation Questions**
1. **Protocol Design**: When should you use MCP vs A2A vs unified approaches?
2. **Bridge Architecture**: How do you efficiently translate between protocol paradigms?
3. **Context Management**: How does shared context enhance agent collaboration?

## 🏗️ Learning Architecture

### **Phase 1: Protocol Analysis and Planning (15 min)**
```
🔍 Protocol Convergence Analysis
├── Compare MCP agent-context vs A2A agent-agent patterns
├── Identify bridging opportunities and translation points
├── Design unified API architecture for dual protocols
└── Plan context-sharing strategies across agent networks
```

### **Phase 2: MCPAgent Implementation (45 min)**
```
🌉 Dual-Protocol Agent Development
├── Implement base MCPAgent class with both protocol supports
├── Create protocol detection and routing mechanisms
├── Build MCP-to-A2A and A2A-to-MCP translation layers
├── Add unified endpoint handlers for both protocols
└── Test protocol switching and message translation
```

### **Phase 3: Context-Aware Agent Networks (20 min)**
```
🔗 Network Integration Patterns
├── Implement context-sharing patterns across A2A networks
├── Create MCP tools that invoke A2A agent collaboration
├── Add A2A messages that trigger MCP context operations
└── Validate end-to-end context-agent-agent workflows
```

## 💡 Pedagogical Scaffolding

### **Guided Discovery Questions**
- 🤔 **Before coding**: "What happens when agents need both context and collaboration?"
- 🤔 **During coding**: "How do you translate between different protocol paradigms?"
- 🤔 **After coding**: "When would you choose unified vs separate protocol implementations?"

### **Metacognitive Prompts**
- **Protocol Thinking**: "What are the strengths and limitations of each protocol?"
- **Integration Analysis**: "How does protocol bridging affect performance and complexity?"
- **System Design**: "How does unified protocol support enhance agent capabilities?"

## 🚀 MCPAgent Bridge Implementation

### **Core MCPAgent Class**
```python
import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

# MCP and A2A imports
from mcp.server import MCPServer
from mcp.types import Tool, Resource
from a2a_sdk import A2AAgent, AgentCard, Message, Task

@dataclass
class ProtocolRequest:
    protocol: str  # "mcp" or "a2a"
    method: str
    data: Dict[str, Any]
    request_id: str

class MCPAgent(A2AAgent):
    """Unified agent implementing both MCP and A2A protocols"""
    
    def __init__(
        self,
        name: str,
        description: str,
        port: int = 8000,
        enable_mcp: bool = True,
        enable_a2a: bool = True
    ):
        # Initialize A2A base
        super().__init__(name, description, port)
        
        self.enable_mcp = enable_mcp
        self.enable_a2a = enable_a2a
        
        # MCP server setup
        if enable_mcp:
            self.mcp_server = MCPServer(name)
            self._setup_mcp_tools()
            self._setup_mcp_resources()
        
        # Shared context store
        self.context_store: Dict[str, Any] = {}
        self.agent_network: Dict[str, str] = {}  # agent_id -> endpoint
    
    async def start_server(self):
        """Start unified server handling both protocols"""
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse
        
        app = FastAPI(title=f"{self.name} - MCP+A2A Bridge")
        
        # A2A Protocol Endpoints
        if self.enable_a2a:
            self._setup_a2a_endpoints(app)
        
        # MCP Protocol Endpoints  
        if self.enable_mcp:
            self._setup_mcp_endpoints(app)
        
        # Unified Protocol Detection
        @app.middleware("http")
        async def protocol_detection(request: Request, call_next):
            # Detect protocol based on headers, path, or content
            protocol = self._detect_protocol(request)
            request.state.protocol = protocol
            return await call_next(request)
        
        # Health endpoint for both protocols
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "protocols": {
                    "mcp": self.enable_mcp,
                    "a2a": self.enable_a2a
                },
                "context_items": len(self.context_store),
                "agent_network_size": len(self.agent_network)
            }
        
        import uvicorn
        await uvicorn.run(app, host="0.0.0.0", port=self.port)
    
    def _detect_protocol(self, request: Request) -> str:
        """Detect which protocol is being used"""
        
        # Check Content-Type header
        content_type = request.headers.get("content-type", "")
        
        # Check URL patterns
        path = str(request.url.path)
        
        # MCP patterns
        if "/mcp/" in path or "jsonrpc" in content_type:
            return "mcp"
        
        # A2A patterns  
        if "/message/" in path or "/task/" in path or "/.well-known/agent-card" in path:
            return "a2a"
        
        # Default based on method
        if request.method == "POST" and content_type == "application/json":
            return "a2a"  # Default to A2A for JSON posts
        
        return "mcp"  # Default to MCP
    
    def _setup_a2a_endpoints(self, app: FastAPI):
        """Setup A2A protocol endpoints"""
        
        @app.get("/.well-known/agent-card.json")
        async def get_agent_card():
            return self.get_agent_card()
        
        @app.post("/message/send")
        async def send_message(message: Dict[str, Any]):
            # A2A message may trigger MCP operations
            result = await self._handle_a2a_message(message)
            return result
        
        @app.post("/message/stream")
        async def stream_message(message: Dict[str, Any]):
            # Streaming A2A with MCP context integration
            return await self._handle_a2a_stream(message)
        
        @app.post("/task/create")
        async def create_task(task_data: Dict[str, Any]):
            # A2A task that may use MCP context
            return await self._handle_a2a_task(task_data)
    
    def _setup_mcp_endpoints(self, app: FastAPI):
        """Setup MCP protocol endpoints"""
        
        @app.post("/mcp/jsonrpc")
        async def mcp_jsonrpc(request: Dict[str, Any]):
            # MCP calls that may trigger A2A collaboration
            return await self._handle_mcp_request(request)
        
        @app.get("/mcp/tools")
        async def list_mcp_tools():
            return {"tools": self._get_mcp_tools()}
        
        @app.get("/mcp/resources")
        async def list_mcp_resources():
            return {"resources": self._get_mcp_resources()}
    
    async def _handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A message with potential MCP context integration"""
        
        content = message.get("content", "")
        
        # Check if message requests context operations
        if "context:" in content.lower():
            # Extract context operation
            context_query = content.split("context:")[1].strip()
            
            # Use MCP to get context
            if self.enable_mcp:
                context_result = await self._query_mcp_context(context_query)
                
                # Enhance message with context
                enhanced_content = f"{content}\n\nContext: {context_result}"
                message["content"] = enhanced_content
        
        # Check if message needs agent collaboration
        if "collaborate:" in content.lower():
            # Extract collaboration request
            collab_request = content.split("collaborate:")[1].strip()
            
            # Use A2A to collaborate with other agents
            collab_result = await self._collaborate_with_agents(collab_request)
            
            # Enhance message with collaboration results
            enhanced_content = f"{content}\n\nCollaboration: {collab_result}"
            message["content"] = enhanced_content
        
        # Process the enhanced message
        return await super().handle_message(message)
    
    async def _query_mcp_context(self, query: str) -> str:
        """Query MCP context and return relevant information"""
        
        # Search context store
        relevant_context = []
        for key, value in self.context_store.items():
            if query.lower() in str(value).lower():
                relevant_context.append(f"{key}: {value}")
        
        if relevant_context:
            return "\n".join(relevant_context)
        
        # If no direct context, try MCP tools
        if self.enable_mcp:
            try:
                # Simulate MCP tool call
                tool_result = await self._call_mcp_tool("search_context", {"query": query})
                return str(tool_result)
            except Exception as e:
                return f"Context query failed: {e}"
        
        return "No relevant context found"
    
    async def _collaborate_with_agents(self, request: str) -> str:
        """Collaborate with other agents in the network"""
        
        collaboration_results = []
        
        for agent_id, endpoint in self.agent_network.items():
            try:
                # Send A2A message to collaborating agent
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{endpoint}/message/send",
                        json={
                            "content": request,
                            "from_agent": self.name,
                            "collaboration": True
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        collaboration_results.append(f"{agent_id}: {result.get('content', 'No response')}")
            
            except Exception as e:
                collaboration_results.append(f"{agent_id}: Error - {e}")
        
        return "\n".join(collaboration_results) if collaboration_results else "No collaboration responses"
    
    async def _handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request with potential A2A integration"""
        
        method = request.get("method", "")
        params = request.get("params", {})
        
        # Check if MCP operation needs agent collaboration
        if method == "tools/call":
            tool_name = params.get("name", "")
            
            if tool_name == "collaborate_with_agents":
                # MCP tool that triggers A2A collaboration
                agent_request = params.get("arguments", {}).get("request", "")
                collab_result = await self._collaborate_with_agents(agent_request)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": collab_result,
                        "type": "text"
                    }
                }
        
        # Handle regular MCP operations
        return await self._process_mcp_request(request)
    
    def _setup_mcp_tools(self):
        """Setup MCP tools that can trigger A2A operations"""
        
        self.mcp_tools = [
            Tool(
                name="collaborate_with_agents",
                description="Collaborate with other agents in the A2A network",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "string",
                            "description": "The collaboration request to send to other agents"
                        }
                    },
                    "required": ["request"]
                }
            ),
            Tool(
                name="share_context",
                description="Share context with agents in the network",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "context_key": {"type": "string"},
                        "context_value": {"type": "string"},
                        "target_agents": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["context_key", "context_value"]
                }
            )
        ]
    
    def _setup_mcp_resources(self):
        """Setup MCP resources that bridge to A2A data"""
        
        self.mcp_resources = [
            Resource(
                uri="context://shared",
                name="Shared Context Store",
                description="Context shared across agent network",
                mimeType="application/json"
            ),
            Resource(
                uri="agents://network",
                name="Agent Network",
                description="Connected agents in A2A network",
                mimeType="application/json"
            )
        ]
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Enhanced agent card showing both protocol support"""
        
        base_card = super().get_agent_card()
        
        # Add MCP capability information
        if self.enable_mcp:
            base_card["protocols"] = base_card.get("protocols", [])
            base_card["protocols"].append("mcp")
            
            base_card["mcp_endpoints"] = {
                "jsonrpc": f"http://localhost:{self.port}/mcp/jsonrpc",
                "tools": f"http://localhost:{self.port}/mcp/tools",
                "resources": f"http://localhost:{self.port}/mcp/resources"
            }
        
        # Add context capabilities
        base_card["capabilities"] = base_card.get("capabilities", [])
        base_card["capabilities"].extend([
            "context_management",
            "agent_collaboration",
            "protocol_bridging"
        ])
        
        return base_card

# Example implementations
class ContextAwareCalendarAgent(MCPAgent):
    """Calendar agent with MCP context and A2A collaboration"""
    
    def __init__(self):
        super().__init__(
            name="Context-Aware Calendar Agent",
            description="Calendar management with context sharing and agent collaboration",
            port=8001
        )
        
        # Initialize with calendar context
        self.context_store["user_preferences"] = {
            "timezone": "UTC",
            "work_hours": "9-17",
            "meeting_buffer": 15
        }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle calendar requests with context awareness"""
        
        content = message.get("content", "")
        
        if "schedule" in content.lower():
            # Use context to enhance scheduling
            prefs = self.context_store.get("user_preferences", {})
            
            # Collaborate with other agents for complex scheduling
            if "team meeting" in content.lower():
                collab_result = await self._collaborate_with_agents(
                    f"Find availability for team meeting: {content}"
                )
                
                return {
                    "content": f"Scheduled meeting considering team availability and preferences: {prefs}\nCollaboration results: {collab_result}",
                    "context_used": True,
                    "collaboration": True
                }
        
        return await super().handle_message(message)

class WeatherContextAgent(MCPAgent):
    """Weather agent that shares context across agent network"""
    
    def __init__(self):
        super().__init__(
            name="Weather Context Agent", 
            description="Weather information with context sharing",
            port=8002
        )
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather requests and share context"""
        
        content = message.get("content", "")
        
        if "weather" in content.lower():
            # Get weather data (simulated)
            weather_data = {
                "temperature": 22,
                "condition": "sunny",
                "humidity": 45,
                "timestamp": "2024-01-15T10:00:00Z"
            }
            
            # Store in context for other agents
            self.context_store["current_weather"] = weather_data
            
            # Share context with network if collaborative weather request
            if "outdoor" in content.lower() or "event" in content.lower():
                await self._share_context_with_network("current_weather", weather_data)
            
            return {
                "content": f"Current weather: {weather_data['condition']}, {weather_data['temperature']}°C",
                "weather_data": weather_data,
                "context_shared": True
            }
        
        return await super().handle_message(message)
    
    async def _share_context_with_network(self, key: str, value: Any):
        """Share context with all agents in network"""
        
        for agent_id, endpoint in self.agent_network.items():
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{endpoint}/context/update",
                        json={
                            "key": key,
                            "value": value,
                            "from_agent": self.name
                        }
                    )
            except Exception as e:
                print(f"Failed to share context with {agent_id}: {e}")
```

### **Protocol Bridge Router**
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProtocolHandler(Protocol):
    """Protocol interface for handling different communication standards"""
    
    async def handle_request(self, request: ProtocolRequest) -> Dict[str, Any]:
        ...
    
    def get_protocol_name(self) -> str:
        ...

class ProtocolBridge:
    """Central router for handling multiple protocols"""
    
    def __init__(self):
        self.handlers: Dict[str, ProtocolHandler] = {}
        self.translation_cache: Dict[str, Any] = {}
    
    def register_handler(self, protocol: str, handler: ProtocolHandler):
        """Register a protocol handler"""
        self.handlers[protocol] = handler
    
    async def route_request(self, request: ProtocolRequest) -> Dict[str, Any]:
        """Route request to appropriate protocol handler"""
        
        if request.protocol not in self.handlers:
            raise ValueError(f"Unsupported protocol: {request.protocol}")
        
        handler = self.handlers[request.protocol]
        
        # Check translation cache
        cache_key = f"{request.protocol}:{request.method}:{hash(str(request.data))}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Handle request
        result = await handler.handle_request(request)
        
        # Cache result
        self.translation_cache[cache_key] = result
        
        return result
    
    async def translate_between_protocols(
        self, 
        source_protocol: str,
        target_protocol: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Translate data between protocols"""
        
        if source_protocol == "mcp" and target_protocol == "a2a":
            return self._mcp_to_a2a(data)
        elif source_protocol == "a2a" and target_protocol == "mcp":
            return self._a2a_to_mcp(data)
        else:
            return data  # No translation needed
    
    def _mcp_to_a2a(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate MCP request to A2A message"""
        
        if mcp_data.get("method") == "tools/call":
            # Convert MCP tool call to A2A message
            params = mcp_data.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            return {
                "content": f"Execute {tool_name}: {arguments}",
                "type": "tool_execution",
                "mcp_origin": True,
                "original_request": mcp_data
            }
        
        # Default translation
        return {
            "content": str(mcp_data),
            "type": "mcp_passthrough",
            "mcp_origin": True
        }
    
    def _a2a_to_mcp(self, a2a_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate A2A message to MCP request"""
        
        content = a2a_data.get("content", "")
        
        # Convert A2A message to MCP tool call
        return {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "process_agent_message",
                "arguments": {
                    "message": content,
                    "a2a_data": a2a_data
                }
            },
            "id": f"a2a_bridge_{hash(content)}"
        }
```

## 🎮 Testing Scenarios

### **Scenario 1: Dual Protocol Agent Discovery**
```bash
# Test A2A discovery
curl http://localhost:8001/.well-known/agent-card.json | jq .

# Test MCP capabilities  
curl -X POST http://localhost:8001/mcp/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### **Scenario 2: Context-Enhanced Agent Collaboration**
```bash
# Send A2A message that triggers MCP context
curl -X POST http://localhost:8001/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Schedule team meeting context: check user preferences",
    "requires_context": true
  }'

# MCP tool that triggers A2A collaboration
curl -X POST http://localhost:8001/mcp/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "collaborate_with_agents",
      "arguments": {"request": "Find best meeting time"}
    },
    "id": 2
  }'
```

### **Scenario 3: Cross-Protocol Context Sharing**
```bash
# Start context-aware agents
python3 context_calendar_agent.py &
python3 weather_context_agent.py &

# Weather agent shares context
curl -X POST http://localhost:8002/message/send \
  -d '{"content": "outdoor event weather check"}'

# Calendar agent uses shared weather context
curl -X POST http://localhost:8001/message/send \
  -d '{"content": "schedule outdoor team meeting context: weather"}'
```

## 🌟 Motivation & Relevance

### **Real-World Connection**
```
🌉 Protocol Convergence
"Modern AI systems need both context and collaboration.
OpenAI's GPTs use context, but enterprise AI needs
agent-to-agent communication. Bridge protocols create
the best of both worlds."
```

### **Personal Relevance**
```
🔗 Integration Architecture Skills
"Building protocol bridges is a senior architecture skill.
These patterns apply to API gateways, service meshes,
and any system integrating multiple standards."
```

### **Immediate Reward**
```
🚀 Unified Agent Power
"See your agents seamlessly switch between context
operations and agent collaboration, creating intelligent
systems that think AND collaborate!"
```

## 📊 Assessment Strategy

### **Formative Assessment** (During learning)
- Protocol detection and routing working correctly
- Context sharing visible across agent networks
- MCP-A2A translations happening seamlessly

### **Summative Assessment** (End of step)
- Complete MCPAgent with dual protocol support
- Context-enhanced agent collaboration workflows
- Unified API serving both MCP and A2A efficiently

### **Authentic Assessment** (Real-world application)
- Design protocol convergence strategies for enterprise systems
- Implement context-aware agent networks for real applications
- Plan migration strategies from single to dual protocol architectures

## 🔄 Spaced Repetition Schedule

### **Immediate Review** (End of session)
- Test all protocol translation scenarios
- Validate context sharing across agent networks
- Review performance implications of dual protocols

### **Distributed Practice** (Next day)
- Implement advanced protocol bridging patterns
- Add protocol-specific optimizations and caching
- Connect to production deployment scenarios

### **Interleaved Review** (Before next module)
- Compare unified vs separate protocol architectures
- Analyze when to use MCP vs A2A vs bridge patterns
- Prepare for advanced enterprise integration patterns

## 🎯 Protocol Performance Metrics

### **Bridging Efficiency**
```
🌉 Translation Performance
├── Protocol Detection: < 1ms
├── MCP-to-A2A Translation: < 5ms  
├── A2A-to-MCP Translation: < 5ms
├── Context Sharing Latency: < 50ms
├── Unified Endpoint Overhead: < 2%
└── Cache Hit Rate: > 80%
```

### **Integration Success Metrics**
```
🔗 Bridge Success Rates
├── Protocol Auto-Detection: > 99%
├── Translation Accuracy: > 95%
├── Context Sync Success: > 98%
├── Cross-Protocol Workflows: > 90%
├── Unified API Uptime: 99.9%
└── Bridge Latency Impact: < 10%
```

## 📖 Learning Resources

### **Primary Resources**
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [A2A Protocol Bridge Patterns](https://google-a2a.github.io/A2A/latest/topics/integration/)
- [Protocol Translation Best Practices](https://example.com/protocol-bridges)

### **Extension Resources**
- Enterprise protocol gateway patterns
- Service mesh integration for multi-protocol systems
- Performance optimization for protocol translation layers

---

## 🚀 Ready to Bridge the Protocol Gap?

**Next Action**: Build unified agents that seamlessly combine context and collaboration!

```bash
cd 12_mcp_a2a_bridge/
# Create the future of unified agent protocols
```

**Remember**: The bridge you build here represents the evolution of AI agent architecture - where context management and agent collaboration converge into powerful, unified systems! 🌉
