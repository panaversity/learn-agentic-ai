# Step 9: Latency Routing 🚀

**Implement intelligent agent selection and performance optimization for responsive multi-agent systems**

> **🎯 Learning Objective**: Master latency-aware routing patterns that automatically select the fastest available agents and optimize multi-agent coordination for real-time performance requirements.

## 🧠 Learning Sciences Foundation

### **Performance Optimization Learning**
- **Systems Performance Mindset**: Understanding bottlenecks and optimization opportunities
- **Data-Driven Decision Making**: Using metrics to guide agent selection and routing
- **Real-Time Constraints**: Balancing accuracy with speed in agent coordination

### **Cognitive Load Optimization**
- **Automated Decision Making**: Reducing cognitive load through intelligent routing
- **Performance Feedback Loops**: Learning from latency patterns to improve routing
- **Predictive Modeling**: Anticipating performance based on historical data

## 🎯 What You'll Learn

### **Core Concepts**
- **Health Check Systems** - Monitoring agent availability and response times
- **Latency-Aware Routing** - Selecting agents based on performance metrics
- **Load Balancing** - Distributing requests across agent instances
- **Circuit Breaker Patterns** - Protecting against cascading failures

### **Practical Skills**
- Implement health check endpoints for all agents
- Create latency monitoring and metrics collection
- Build intelligent routing algorithms for agent selection
- Configure circuit breakers and failover mechanisms

### **Strategic Understanding**
- How performance optimization enables real-time multi-agent systems
- Trade-offs between speed, accuracy, and reliability in agent routing
- Scaling patterns for enterprise multi-agent deployments

## 📋 Prerequisites

✅ **Completed**: [Step 8: Security Hardening](../08_security_hardening/) - Production security foundation  
✅ **Knowledge**: Multi-agent systems with comprehensive security controls  
✅ **Performance Awareness**: Understanding of latency and throughput concepts  
✅ **Tools**: UV package manager, Python 3.10+, monitoring tools (Prometheus)  

## 🎯 Success Criteria

By the end of this step, you'll have:

### **Technical Deliverables**
- [ ] Health check endpoints for all agents with latency metrics
- [ ] Intelligent routing system that selects fastest available agents
- [ ] Load balancing across multiple instances of the same agent type
- [ ] Circuit breaker protection against failing agents

### **Performance Architecture**
- [ ] Real-time latency monitoring and alerting
- [ ] Automated failover and recovery mechanisms
- [ ] Performance-based agent selection algorithms
- [ ] Capacity planning and scaling recommendations

### **Operational Excellence**
- [ ] Performance dashboards and monitoring
- [ ] SLA monitoring and breach alerting
- [ ] Performance tuning and optimization procedures
- [ ] Capacity planning for growth scenarios

### **Learning Validation Questions**
1. **Performance Analysis**: What factors affect agent response times?
2. **Routing Strategy**: How do you balance speed vs. accuracy in agent selection?
3. **Scalability**: How does latency routing enable horizontal scaling?

## 🏗️ Learning Architecture

### **Phase 1: Performance Monitoring Foundation (20 min)**
```
📊 Performance Infrastructure
├── Implement health check endpoints for all agents
├── Configure latency monitoring and metrics collection
├── Set up performance dashboards and alerting
└── Establish performance baselines and SLA targets
```

### **Phase 2: Intelligent Routing Implementation (40 min)**
```
🚀 Smart Agent Selection
├── Build latency-aware routing algorithms
├── Implement circuit breaker patterns for reliability
├── Add load balancing across agent instances
├── Configure failover and recovery mechanisms
└── Test routing under various load conditions
```

### **Phase 3: Performance Optimization (20 min)**
```
⚡ System Tuning
├── Analyze performance bottlenecks and optimization opportunities
├── Tune routing algorithms based on real performance data
├── Implement predictive routing based on historical patterns
└── Validate performance improvements with load testing
```

## 💡 Pedagogical Scaffolding

### **Guided Discovery Questions**
- 🤔 **Before coding**: "What happens when an agent becomes slow or unavailable?"
- 🤔 **During coding**: "How do you balance speed with agent capability?"
- 🤔 **After coding**: "How would routing change under different load patterns?"

### **Metacognitive Prompts**
- **Performance Thinking**: "What are the bottlenecks in multi-agent coordination?"
- **Trade-off Analysis**: "When should you sacrifice speed for accuracy?"
- **System Design**: "How does intelligent routing improve user experience?"

## 🚀 Latency-Aware Routing Implementation

### **Health Check and Metrics Collection**
```python
import time
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
import httpx

@dataclass
class AgentHealth:
    agent_id: str
    endpoint: str
    latency_ms: float
    success_rate: float
    last_check: float
    is_healthy: bool
    error_count: int

class AgentHealthMonitor:
    def __init__(self):
        self.agent_health: Dict[str, AgentHealth] = {}
        self.check_interval = 30  # seconds
        self.timeout = 5  # seconds
        
    async def start_monitoring(self, agents: List[str]):
        """Start continuous health monitoring for all agents"""
        tasks = []
        for agent_endpoint in agents:
            task = asyncio.create_task(
                self._monitor_agent_health(agent_endpoint)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def _monitor_agent_health(self, agent_endpoint: str):
        """Monitor individual agent health continuously"""
        agent_id = agent_endpoint.split('//')[1]  # Extract from URL
        
        while True:
            try:
                start_time = time.time()
                
                # Health check request
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(f"{agent_endpoint}/health")
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Update health metrics
                if agent_id in self.agent_health:
                    health = self.agent_health[agent_id]
                    # Exponential moving average for latency
                    health.latency_ms = 0.7 * health.latency_ms + 0.3 * latency_ms
                    health.success_rate = min(1.0, health.success_rate + 0.1)
                    health.error_count = max(0, health.error_count - 1)
                else:
                    health = AgentHealth(
                        agent_id=agent_id,
                        endpoint=agent_endpoint,
                        latency_ms=latency_ms,
                        success_rate=1.0,
                        last_check=time.time(),
                        is_healthy=True,
                        error_count=0
                    )
                
                health.last_check = time.time()
                health.is_healthy = (
                    response.status_code == 200 and 
                    latency_ms < 1000 and  # 1 second threshold
                    health.error_count < 3
                )
                
                self.agent_health[agent_id] = health
                
            except Exception as e:
                # Handle health check failure
                if agent_id in self.agent_health:
                    health = self.agent_health[agent_id]
                    health.error_count += 1
                    health.success_rate = max(0.0, health.success_rate - 0.2)
                    health.is_healthy = health.error_count < 5
                    health.last_check = time.time()
                
                print(f"Health check failed for {agent_id}: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    def get_fastest_agent(self, agent_type: str) -> Optional[str]:
        """Select the fastest healthy agent of given type"""
        candidates = [
            health for health in self.agent_health.values()
            if health.is_healthy and agent_type in health.agent_id
        ]
        
        if not candidates:
            return None
        
        # Sort by latency, then by success rate
        candidates.sort(key=lambda h: (h.latency_ms, -h.success_rate))
        return candidates[0].endpoint
```

### **Intelligent Agent Router**
```python
from enum import Enum
from typing import Any, Dict, List

class RoutingStrategy(Enum):
    FASTEST = "fastest"
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"

class AgentRouter:
    def __init__(self, health_monitor: AgentHealthMonitor):
        self.health_monitor = health_monitor
        self.round_robin_counters: Dict[str, int] = {}
        self.request_counts: Dict[str, int] = {}
    
    async def route_request(
        self, 
        agent_type: str, 
        request: Dict[str, Any],
        strategy: RoutingStrategy = RoutingStrategy.FASTEST
    ) -> Optional[str]:
        """Route request to optimal agent based on strategy"""
        
        healthy_agents = self._get_healthy_agents(agent_type)
        if not healthy_agents:
            raise NoHealthyAgentsError(f"No healthy agents available for type: {agent_type}")
        
        if strategy == RoutingStrategy.FASTEST:
            return self._route_fastest(healthy_agents)
        elif strategy == RoutingStrategy.ROUND_ROBIN:
            return self._route_round_robin(agent_type, healthy_agents)
        elif strategy == RoutingStrategy.LEAST_LOADED:
            return self._route_least_loaded(healthy_agents)
        elif strategy == RoutingStrategy.WEIGHTED:
            return self._route_weighted(healthy_agents)
    
    def _get_healthy_agents(self, agent_type: str) -> List[AgentHealth]:
        """Get all healthy agents of specified type"""
        return [
            health for health in self.health_monitor.agent_health.values()
            if health.is_healthy and agent_type in health.agent_id
        ]
    
    def _route_fastest(self, agents: List[AgentHealth]) -> str:
        """Route to agent with lowest latency"""
        fastest = min(agents, key=lambda a: a.latency_ms)
        return fastest.endpoint
    
    def _route_round_robin(self, agent_type: str, agents: List[AgentHealth]) -> str:
        """Route using round-robin strategy"""
        if agent_type not in self.round_robin_counters:
            self.round_robin_counters[agent_type] = 0
        
        index = self.round_robin_counters[agent_type] % len(agents)
        self.round_robin_counters[agent_type] += 1
        
        return agents[index].endpoint
    
    def _route_least_loaded(self, agents: List[AgentHealth]) -> str:
        """Route to agent with least current load"""
        least_loaded = min(
            agents, 
            key=lambda a: self.request_counts.get(a.agent_id, 0)
        )
        
        # Track request count
        self.request_counts[least_loaded.agent_id] = (
            self.request_counts.get(least_loaded.agent_id, 0) + 1
        )
        
        return least_loaded.endpoint
    
    def _route_weighted(self, agents: List[AgentHealth]) -> str:
        """Route based on weighted performance metrics"""
        # Calculate weights based on latency and success rate
        weights = []
        for agent in agents:
            # Lower latency and higher success rate = higher weight
            weight = agent.success_rate / (agent.latency_ms / 100)
            weights.append(weight)
        
        # Weighted random selection
        import random
        total_weight = sum(weights)
        random_value = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return agents[i].endpoint
        
        return agents[0].endpoint  # Fallback
```

### **Circuit Breaker Implementation**
```python
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, requests rejected
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: Exception = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.timeout
        )
    
    def _on_success(self):
        """Handle successful request"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage in agent routing
class ResilientAgentRouter(AgentRouter):
    def __init__(self, health_monitor: AgentHealthMonitor):
        super().__init__(health_monitor)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    async def send_message_with_circuit_breaker(
        self, 
        agent_endpoint: str, 
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send message with circuit breaker protection"""
        
        agent_id = agent_endpoint.split('//')[1]
        
        if agent_id not in self.circuit_breakers:
            self.circuit_breakers[agent_id] = CircuitBreaker(
                failure_threshold=3,
                timeout=30
            )
        
        circuit_breaker = self.circuit_breakers[agent_id]
        
        async def send_request():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{agent_endpoint}/message/send",
                    json=message,
                    timeout=5.0
                )
                return response.json()
        
        return await circuit_breaker.call(send_request)
```

## 🎮 Performance Testing Scenarios

### **Scenario 1: Latency Comparison Testing**
```bash
# Test all agents and compare response times
for port in 8001 8002 8003 8004; do
    echo "Testing agent on port $port:"
    time curl -s http://localhost:$port/health | jq .
    echo "---"
done

# Automated performance test
python3 test_agent_latency.py --agents http://localhost:8001,http://localhost:8002,http://localhost:8003
```

### **Scenario 2: Load Testing with Routing**
```bash
# Install load testing tool
pip install locust

# Run load test with intelligent routing
locust -f load_test_routing.py --host=http://localhost:8000 --users=50 --spawn-rate=5
```

### **Scenario 3: Circuit Breaker Testing**
```bash
# Start agents
python3 agent_calendar.py &
python3 agent_weather.py &

# Simulate agent failure
kill $(pgrep -f agent_weather.py)

# Test circuit breaker behavior
curl -X POST http://localhost:8000/route/weather \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather?"}'
```

## 🌟 Motivation & Relevance

### **Real-World Connection**
```
⚡ Enterprise Performance
"Production AI systems must respond within milliseconds.
Google's search responds in <200ms, ChatGPT streams in
real-time. Your agents need the same performance standards."
```

### **Personal Relevance**
```
🚀 Performance Engineering Skills  
"Latency optimization and intelligent routing are core
skills for senior engineers. These patterns apply across
all distributed systems, not just AI agents."
```

### **Immediate Reward**
```
📊 Performance Insights
"See your routing algorithms selecting the fastest agents
in real-time, with visual dashboards showing performance
improvements within 60 minutes!"
```

## 📊 Assessment Strategy

### **Formative Assessment** (During learning)
- Health check endpoints provide immediate latency feedback
- Routing algorithms show selection decisions in real-time
- Load testing validates performance improvements

### **Summative Assessment** (End of step)
- Intelligent routing system selecting optimal agents
- Circuit breaker protection preventing cascading failures
- Ready for production deployment with gRPC optimization

### **Authentic Assessment** (Real-world application)
- Design routing strategies for specific business requirements
- Implement performance monitoring for production deployments
- Plan scaling strategies for growing agent ecosystems

## 🔄 Spaced Repetition Schedule

### **Immediate Review** (End of session)
- Test routing algorithms under various load conditions
- Validate circuit breaker behavior with simulated failures
- Review performance metrics and optimization opportunities

### **Distributed Practice** (Next day)
- Implement advanced routing strategies (geographic, capability-based)
- Add predictive routing based on historical patterns
- Connect to production deployment planning

### **Interleaved Review** (Before Step 10)
- Compare HTTP routing performance with gRPC alternatives
- Analyze routing optimization for production deployment
- Prepare for comprehensive monitoring and observability

## 🎯 Performance Metrics and SLAs

### **Agent Performance SLAs**
```
📊 Performance Targets
├── Health Check Response: < 100ms (99th percentile)
├── Agent Discovery: < 200ms (95th percentile)
├── Message Processing: < 500ms (90th percentile)
├── Multi-Agent Coordination: < 2s (95th percentile)
├── Availability: 99.9% uptime
└── Error Rate: < 0.1% of requests
```

### **Routing Algorithm Performance**
```
🚀 Routing Efficiency Metrics
├── Agent Selection Time: < 10ms
├── Route Calculation: < 5ms
├── Health Check Overhead: < 2% of total latency
├── Circuit Breaker Accuracy: > 95%
├── Load Distribution Variance: < 20%
└── Failover Time: < 1s
```

## 📖 Learning Resources

### **Primary Resources**
- [A2A Performance Best Practices](https://google-a2a.github.io/A2A/latest/topics/performance/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Load Balancing Algorithms](https://nginx.org/en/docs/http/load_balancing.html)

### **Extension Resources**
- Enterprise performance monitoring strategies
- Microservices routing and service mesh patterns
- AI system latency optimization techniques

---

## 🚀 Ready to Optimize Agent Performance?

**Next Action**: Implement intelligent routing and watch your agents automatically select the fastest paths!

```bash
cd 09_latency_routing/
# Build high-performance routing for your multi-agent system
```

**Remember**: Performance isn't just about speed - it's about delivering consistent, reliable experiences that enable real-time AI collaboration. The routing intelligence you build here makes Step 10's production deployment truly enterprise-ready! 🚀
