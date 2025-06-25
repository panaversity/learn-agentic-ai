# Step 12: Enterprise Features 🏢

**Learning Objective**: Implement production-ready enterprise capabilities using the official A2A Python SDK, including telemetry, monitoring, scalability patterns, and enterprise-grade operational features.

## 📚 Official A2A Reference

**Primary Documentation**: [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)  
**Enterprise Guide**: [A2A Enterprise-Ready Features](https://google-a2a.github.io/A2A/topics/enterprise-ready/)  
**Telemetry Reference**: [A2A Telemetry Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.utils.telemetry)

## 🎯 What You'll Learn

- A2A SDK telemetry and OpenTelemetry integration
- Enterprise-grade monitoring with A2A tracing
- Production deployment patterns with A2A SDK
- Performance optimization for A2A agent networks
- Health checks and operational monitoring
- Enterprise security and compliance features

## 🏗️ Project Structure

```
12_enterprise_features/
├── README.md
├── pyproject.toml
├── src/
│   ├── enterprise_agent.py      # Production-ready agent with telemetry
│   ├── monitoring_service.py    # A2A telemetry monitoring
│   ├── health_manager.py        # Health checks with A2A SDK
│   └── performance_optimizer.py # Performance monitoring
├── infrastructure/
│   ├── docker-compose.yml       # Container orchestration
│   ├── kubernetes/              # K8s deployment manifests
│   │   ├── agent-deployment.yaml
│   │   └── monitoring-stack.yaml
│   └── observability/
│       ├── jaeger-config.yaml   # Distributed tracing
│       └── prometheus-config.yml # Metrics collection
├── examples/
│   ├── telemetry_demo.py        # A2A telemetry demonstration
│   ├── enterprise_monitoring.py # Complete monitoring setup
│   └── load_testing.py          # Performance testing
├── tests/
│   ├── test_enterprise_features.py
│   └── test_telemetry.py
└── config/
    ├── telemetry.yaml           # OpenTelemetry configuration
    └── enterprise.yaml          # Enterprise settings
```

## 🚀 Quick Start

### 1. Initialize Project

```bash
cd 12_enterprise_features
uv init enterprise_a2a
cd enterprise_a2a
uv add a2a fastapi uvicorn opentelemetry-api opentelemetry-sdk opentelemetry-exporter-jaeger prometheus-client
```

### 2. Start Enterprise Stack

```bash
# Start observability stack
docker-compose up -d jaeger prometheus grafana

# Start enterprise agent with telemetry
uv run python src/enterprise_agent.py

# Start monitoring service
uv run python src/monitoring_service.py
```

### 3. Test Enterprise Features

```bash
# Test telemetry and tracing
uv run python examples/telemetry_demo.py

# Run enterprise monitoring
uv run python examples/enterprise_monitoring.py

# Performance testing
uv run python examples/load_testing.py
```

## 📋 Core Implementation

### Enterprise Agent with A2A Telemetry (src/enterprise_agent.py)

```python
from a2a import Agent, AgentCard, AgentSkill, AgentProvider, AgentCapabilities
from a2a.server import A2AServer
from a2a.utils.telemetry import trace_class, trace_function, SpanKind
import asyncio
import logging
import time
from typing import Dict, Optional
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OpenTelemetry for enterprise tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Create enterprise agent card with advanced capabilities
enterprise_card = AgentCard(
    name="Enterprise Production Agent",
    version="2.0.0",
    description="Production-ready agent with enterprise features and telemetry",
    provider=AgentProvider(
        organization="Enterprise A2A Solutions",
        url="http://localhost:8400"
    ),
    url="http://localhost:8400",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=True,
        extensions=["enterprise", "telemetry", "monitoring"]
    ),
    skills=[
        AgentSkill(
            id="enterprise_process",
            name="Enterprise Data Processing",
            description="High-performance enterprise data processing with full telemetry",
            input_modes=["text", "json"],
            output_modes=["text", "json"],
            tags=["enterprise", "production", "monitored"]
        ),
        AgentSkill(
            id="analytics_task",
            name="Enterprise Analytics",
            description="Advanced analytics with performance monitoring",
            input_modes=["json"],
            output_modes=["json"],
            tags=["analytics", "performance", "enterprise"]
        ),
        AgentSkill(
            id="health_check",
            name="Health Check",
            description="Comprehensive health and status reporting",
            input_modes=["text"],
            output_modes=["json"],
            tags=["health", "monitoring", "ops"]
        )
    ]
)

@trace_class(exclude_list=['_internal_method'])
class EnterpriseAgent:
    """Enterprise-grade agent with full telemetry and monitoring"""
    
    def __init__(self):
        self.agent = Agent(card=enterprise_card)
        self.start_time = time.time()
        self.request_count = 0
        self.performance_metrics = {
            "total_requests": 0,
            "avg_response_time": 0.0,
            "error_count": 0,
            "success_rate": 100.0
        }
        
        # Register skills with telemetry decorators
        self.agent.skill("enterprise_process")(self.enterprise_process)
        self.agent.skill("analytics_task")(self.analytics_task)
        self.agent.skill("health_check")(self.health_check)
    
    @trace_function(
        span_name="enterprise.process.data",
        kind=SpanKind.INTERNAL,
        attributes={"component": "enterprise_processor"}
    )
    async def enterprise_process(self, message, context):
        """Enterprise data processing with comprehensive telemetry"""
        start_time = time.time()
        
        try:
            # Extract processing parameters
            content = message.content
            processing_type = context.get("processing_type", "standard")
            
            # Simulate enterprise processing with telemetry
            with tracer.start_as_current_span("data.validation") as validation_span:
                validation_span.set_attribute("data.size", len(content))
                validation_span.set_attribute("processing.type", processing_type)
                
                # Simulate validation
                await asyncio.sleep(0.1)
                validation_span.set_attribute("validation.status", "passed")
            
            with tracer.start_as_current_span("data.processing") as processing_span:
                processing_span.set_attribute("processor.version", "2.0.0")
                
                # Simulate complex processing
                await asyncio.sleep(0.5)
                
                processed_data = {
                    "original_content": content,
                    "processed_at": time.time(),
                    "processing_type": processing_type,
                    "word_count": len(content.split()) if isinstance(content, str) else 0,
                    "character_count": len(content) if isinstance(content, str) else 0
                }
                
                processing_span.set_attribute("processing.word_count", processed_data["word_count"])
                processing_span.set_attribute("processing.status", "completed")
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, success=True)
            
            return {
                "content": "Enterprise processing completed successfully",
                "type": "json",
                "metadata": {
                    "processed_data": processed_data,
                    "processing_time_ms": round(processing_time * 1000, 2),
                    "agent_version": "2.0.0",
                    "telemetry_enabled": True
                }
            }
        
        except Exception as e:
            # Record error in telemetry
            with tracer.start_as_current_span("error.handling") as error_span:
                error_span.set_attribute("error.type", type(e).__name__)
                error_span.set_attribute("error.message", str(e))
                error_span.record_exception(e)
            
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, success=False)
            
            return {
                "content": f"Enterprise processing failed: {str(e)}",
                "type": "error",
                "metadata": {
                    "error_type": type(e).__name__,
                    "processing_time_ms": round(processing_time * 1000, 2)
                }
            }
    
    @trace_function(
        span_name="enterprise.analytics.execute",
        kind=SpanKind.INTERNAL
    )
    async def analytics_task(self, message, context):
        """Advanced analytics with performance monitoring"""
        start_time = time.time()
        
        try:
            # Parse analytics request
            import json
            analytics_request = json.loads(message.content) if message.content.startswith('{') else {"query": message.content}
            
            query_type = analytics_request.get("type", "basic")
            data_points = analytics_request.get("data_points", 1000)
            
            with tracer.start_as_current_span("analytics.computation") as analytics_span:
                analytics_span.set_attribute("analytics.query_type", query_type)
                analytics_span.set_attribute("analytics.data_points", data_points)
                
                # Simulate analytics computation
                computation_time = min(data_points / 1000, 2.0)  # Scale with data size
                await asyncio.sleep(computation_time)
                
                # Generate analytics results
                results = {
                    "query_type": query_type,
                    "data_points_analyzed": data_points,
                    "computation_time_ms": round(computation_time * 1000, 2),
                    "insights": [
                        "Trend analysis shows positive growth",
                        "Data quality score: 95%",
                        "Anomalies detected: 2"
                    ],
                    "confidence_score": 0.94
                }
                
                analytics_span.set_attribute("analytics.confidence", results["confidence_score"])
                analytics_span.set_attribute("analytics.insights_count", len(results["insights"]))
            
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, success=True)
            
            return {
                "content": "Analytics completed successfully",
                "type": "json",
                "metadata": {
                    "analytics_results": results,
                    "total_processing_time_ms": round(processing_time * 1000, 2)
                }
            }
        
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, success=False)
            
            return {
                "content": f"Analytics failed: {str(e)}",
                "type": "error",
                "metadata": {"error_type": type(e).__name__}
            }
    
    @trace_function(span_name="enterprise.health.check")
    async def health_check(self, message, context):
        """Comprehensive health and status reporting"""
        uptime = time.time() - self.start_time
        
        health_status = {
            "status": "healthy",
            "uptime_seconds": round(uptime, 2),
            "performance_metrics": self.performance_metrics.copy(),
            "system_info": {
                "agent_version": "2.0.0",
                "telemetry_enabled": True,
                "monitoring_active": True
            },
            "capabilities": {
                "streaming": True,
                "push_notifications": True,
                "enterprise_features": True
            },
            "last_check": time.time()
        }
        
        # Health score calculation
        if self.performance_metrics["success_rate"] > 95:
            health_status["health_score"] = "excellent"
        elif self.performance_metrics["success_rate"] > 85:
            health_status["health_score"] = "good"
        else:
            health_status["health_score"] = "needs_attention"
        
        return {
            "content": f"Health check completed - Status: {health_status['health_score']}",
            "type": "json",
            "metadata": {"health_report": health_status}
        }
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update performance metrics with telemetry"""
        self.performance_metrics["total_requests"] += 1
        
        # Update average response time
        current_avg = self.performance_metrics["avg_response_time"]
        total_requests = self.performance_metrics["total_requests"]
        self.performance_metrics["avg_response_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
        
        if not success:
            self.performance_metrics["error_count"] += 1
        
        # Update success rate
        self.performance_metrics["success_rate"] = (
            ((total_requests - self.performance_metrics["error_count"]) / total_requests) * 100
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    
    enterprise_agent = EnterpriseAgent()
    
    print("🏢 Starting Enterprise Production Agent...")
    print("📊 Features: Telemetry, Monitoring, Performance Tracking")
    print("🔍 OpenTelemetry tracing enabled")
    print("📈 Metrics collection active")
    
    # Create A2A server with enterprise configuration
    server = A2AServer(enterprise_agent.agent)
    
    # Start the server
    await server.start(host="0.0.0.0", port=8400)

if __name__ == "__main__":
    asyncio.run(main())
```

### A2A Telemetry Monitoring Service (src/monitoring_service.py)

```python
from a2a.client import A2AClient, A2ACardResolver
from a2a.utils.telemetry import trace_function, SpanKind
import asyncio
import logging
import time
import json
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class AgentHealthStatus:
    agent_name: str
    url: str
    status: str
    last_check: datetime
    response_time_ms: float
    health_score: str
    metrics: Dict

class A2AMonitoringService:
    """Enterprise monitoring service for A2A agent networks"""
    
    def __init__(self):
        self.resolver = A2ACardResolver()
        self.monitored_agents = {}
        self.health_history = []
        self.alert_thresholds = {
            "response_time_ms": 5000,
            "success_rate": 85.0,
            "error_rate": 15.0
        }
    
    @trace_function(span_name="monitoring.agent.register", kind=SpanKind.CLIENT)
    async def register_agent_for_monitoring(self, agent_url: str):
        """Register an agent for continuous monitoring"""
        try:
            agent_card = await self.resolver.get_agent_card(agent_url)
            if agent_card:
                client = A2AClient.get_client_from_agent_card_url(agent_url)
                
                self.monitored_agents[agent_card.name] = {
                    "url": agent_url,
                    "card": agent_card,
                    "client": client,
                    "last_health_check": None,
                    "status": "unknown"
                }
                
                logging.info(f"✅ Registered agent for monitoring: {agent_card.name}")
                return True
        
        except Exception as e:
            logging.error(f"❌ Failed to register agent {agent_url}: {e}")
        
        return False
    
    @trace_function(span_name="monitoring.health.check", kind=SpanKind.CLIENT)
    async def perform_health_check(self, agent_name: str) -> AgentHealthStatus:
        """Perform comprehensive health check on an agent"""
        if agent_name not in self.monitored_agents:
            raise ValueError(f"Agent {agent_name} not registered for monitoring")
        
        agent_info = self.monitored_agents[agent_name]
        client = agent_info["client"]
        
        start_time = time.time()
        
        try:
            # Send health check request
            response = await client.send_message(
                skill_id="health_check",
                message={
                    "content": "comprehensive_health_check",
                    "role": "monitoring_service"
                }
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response and response.get("type") != "error":
                health_data = response.get("metadata", {}).get("health_report", {})
                
                health_status = AgentHealthStatus(
                    agent_name=agent_name,
                    url=agent_info["url"],
                    status="healthy",
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    health_score=health_data.get("health_score", "unknown"),
                    metrics=health_data.get("performance_metrics", {})
                )
                
                # Update agent status
                agent_info["last_health_check"] = health_status
                agent_info["status"] = "healthy"
                
                return health_status
            else:
                # Agent responded with error
                health_status = AgentHealthStatus(
                    agent_name=agent_name,
                    url=agent_info["url"],
                    status="unhealthy",
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    health_score="error",
                    metrics={}
                )
                
                agent_info["status"] = "unhealthy"
                return health_status
        
        except Exception as e:
            # Agent is unreachable or failed
            response_time = (time.time() - start_time) * 1000
            
            health_status = AgentHealthStatus(
                agent_name=agent_name,
                url=agent_info["url"],
                status="unreachable",
                last_check=datetime.now(),
                response_time_ms=response_time,
                health_score="critical",
                metrics={}
            )
            
            agent_info["status"] = "unreachable"
            logging.error(f"Health check failed for {agent_name}: {e}")
            return health_status
    
    @trace_function(span_name="monitoring.check.all", kind=SpanKind.INTERNAL)
    async def check_all_agents(self) -> List[AgentHealthStatus]:
        """Perform health checks on all registered agents"""
        health_results = []
        
        for agent_name in self.monitored_agents.keys():
            try:
                health_status = await self.perform_health_check(agent_name)
                health_results.append(health_status)
                
                # Store in history
                self.health_history.append(health_status)
                
                # Check for alerts
                await self._check_alerts(health_status)
                
            except Exception as e:
                logging.error(f"Failed to check {agent_name}: {e}")
        
        # Trim history (keep last 1000 entries)
        if len(self.health_history) > 1000:
            self.health_history = self.health_history[-1000:]
        
        return health_results
    
    async def _check_alerts(self, health_status: AgentHealthStatus):
        """Check if health status triggers any alerts"""
        alerts = []
        
        # Response time alert
        if health_status.response_time_ms > self.alert_thresholds["response_time_ms"]:
            alerts.append(f"High response time: {health_status.response_time_ms:.2f}ms")
        
        # Success rate alert
        if health_status.metrics:
            success_rate = health_status.metrics.get("success_rate", 100)
            if success_rate < self.alert_thresholds["success_rate"]:
                alerts.append(f"Low success rate: {success_rate:.1f}%")
        
        # Status alerts
        if health_status.status in ["unhealthy", "unreachable"]:
            alerts.append(f"Agent status: {health_status.status}")
        
        if alerts:
            logging.warning(f"🚨 ALERTS for {health_status.agent_name}: {', '.join(alerts)}")
    
    @trace_function(span_name="monitoring.performance.test", kind=SpanKind.CLIENT)
    async def performance_test(self, agent_name: str, test_duration: int = 30) -> Dict:
        """Run performance test on an agent"""
        if agent_name not in self.monitored_agents:
            raise ValueError(f"Agent {agent_name} not registered")
        
        client = self.monitored_agents[agent_name]["client"]
        test_results = {
            "agent_name": agent_name,
            "test_duration": test_duration,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "min_response_time": float('inf'),
            "max_response_time": 0.0,
            "requests_per_second": 0.0
        }
        
        start_time = time.time()
        response_times = []
        
        print(f"🚀 Starting {test_duration}s performance test for {agent_name}...")
        
        while time.time() - start_time < test_duration:
            request_start = time.time()
            
            try:
                response = await client.send_message(
                    skill_id="enterprise_process",
                    message={
                        "content": f"Performance test request {test_results['total_requests']}",
                        "role": "performance_tester"
                    }
                )
                
                response_time = (time.time() - request_start) * 1000
                response_times.append(response_time)
                
                test_results["total_requests"] += 1
                
                if response and response.get("type") != "error":
                    test_results["successful_requests"] += 1
                else:
                    test_results["failed_requests"] += 1
                
                # Update response time stats
                test_results["min_response_time"] = min(test_results["min_response_time"], response_time)
                test_results["max_response_time"] = max(test_results["max_response_time"], response_time)
                
            except Exception as e:
                test_results["total_requests"] += 1
                test_results["failed_requests"] += 1
                logging.debug(f"Request failed: {e}")
            
            # Brief pause between requests
            await asyncio.sleep(0.1)
        
        # Calculate final statistics
        if response_times:
            test_results["avg_response_time"] = sum(response_times) / len(response_times)
        
        actual_duration = time.time() - start_time
        test_results["requests_per_second"] = test_results["total_requests"] / actual_duration
        test_results["success_rate"] = (test_results["successful_requests"] / test_results["total_requests"]) * 100
        
        return test_results
    
    def generate_monitoring_report(self) -> Dict:
        """Generate comprehensive monitoring report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "monitored_agents": len(self.monitored_agents),
            "agents_status": {},
            "overall_health": "unknown",
            "alerts": []
        }
        
        healthy_count = 0
        total_agents = len(self.monitored_agents)
        
        for agent_name, agent_info in self.monitored_agents.items():
            last_check = agent_info.get("last_health_check")
            if last_check:
                report["agents_status"][agent_name] = {
                    "status": last_check.status,
                    "health_score": last_check.health_score,
                    "response_time_ms": last_check.response_time_ms,
                    "last_check": last_check.last_check.isoformat()
                }
                
                if last_check.status == "healthy":
                    healthy_count += 1
            else:
                report["agents_status"][agent_name] = {
                    "status": "not_checked",
                    "health_score": "unknown"
                }
        
        # Overall health assessment
        if total_agents == 0:
            report["overall_health"] = "no_agents"
        elif healthy_count == total_agents:
            report["overall_health"] = "excellent"
        elif healthy_count >= total_agents * 0.8:
            report["overall_health"] = "good"
        elif healthy_count >= total_agents * 0.5:
            report["overall_health"] = "degraded"
        else:
            report["overall_health"] = "critical"
        
        return report

async def main():
    """Run monitoring service demo"""
    logging.basicConfig(level=logging.INFO)
    
    monitoring = A2AMonitoringService()
    
    print("🔍 Starting A2A Enterprise Monitoring Service...")
    
    # Register agents for monitoring
    agents_to_monitor = [
        "http://localhost:8400",  # Enterprise agent
        "http://localhost:8100",  # Coordinator agent (if running)
    ]
    
    for agent_url in agents_to_monitor:
        await monitoring.register_agent_for_monitoring(agent_url)
    
    print(f"📊 Monitoring {len(monitoring.monitored_agents)} agents")
    
    # Continuous monitoring loop
    try:
        while True:
            print("\n🔄 Performing health checks...")
            health_results = await monitoring.check_all_agents()
            
            for health in health_results:
                status_emoji = "✅" if health.status == "healthy" else "❌"
                print(f"{status_emoji} {health.agent_name}: {health.status} ({health.response_time_ms:.1f}ms)")
            
            # Generate and display report
            report = monitoring.generate_monitoring_report()
            print(f"\n📈 Overall Health: {report['overall_health']}")
            print(f"🔢 Healthy Agents: {sum(1 for s in report['agents_status'].values() if s['status'] == 'healthy')}/{report['monitored_agents']}")
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring service stopped")

if __name__ == "__main__":
    asyncio.run(main())
```

### Telemetry Demonstration (examples/telemetry_demo.py)

```python
import asyncio
from a2a.client import A2AClient
from a2a.utils.telemetry import trace_function, SpanKind
import logging
import time

@trace_function(span_name="demo.client.test", kind=SpanKind.CLIENT)
async def test_enterprise_agent_telemetry():
    """Demonstrate A2A SDK telemetry features"""
    print("📊 A2A Telemetry Demonstration")
    print("=" * 35)
    
    # Create client for enterprise agent
    client = A2AClient.get_client_from_agent_card_url("http://localhost:8400")
    
    # Test enterprise processing with telemetry
    print("\n1. Testing enterprise processing with telemetry...")
    
    test_cases = [
        {
            "skill": "enterprise_process",
            "message": "Process this enterprise data with full telemetry tracking",
            "description": "Enterprise data processing"
        },
        {
            "skill": "analytics_task", 
            "message": '{"type": "trend_analysis", "data_points": 5000}',
            "description": "Analytics computation"
        },
        {
            "skill": "health_check",
            "message": "full_health_report",
            "description": "Health check with metrics"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}...")
        
        start_time = time.time()
        
        try:
            response = await client.send_message(
                skill_id=test_case["skill"],
                message={
                    "content": test_case["message"],
                    "role": "telemetry_demo",
                    "metadata": {"demo_request_id": f"demo_{i}"}
                }
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            if response:
                print(f"   ✅ Success ({processing_time:.1f}ms)")
                
                # Display telemetry metadata
                metadata = response.get("metadata", {})
                if "processing_time_ms" in metadata:
                    print(f"   📊 Agent processing time: {metadata['processing_time_ms']}ms")
                
                if "health_report" in metadata:
                    health = metadata["health_report"]
                    print(f"   💚 Health score: {health.get('health_score', 'unknown')}")
                    print(f"   📈 Success rate: {health.get('performance_metrics', {}).get('success_rate', 'N/A')}%")
                
                if "analytics_results" in metadata:
                    analytics = metadata["analytics_results"]
                    print(f"   🔬 Confidence: {analytics.get('confidence_score', 'N/A')}")
                    print(f"   📊 Data points: {analytics.get('data_points_analyzed', 'N/A')}")
            else:
                print(f"   ❌ No response received")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")

@trace_function(span_name="demo.load.test", kind=SpanKind.CLIENT)
async def demonstrate_load_testing():
    """Demonstrate load testing with telemetry"""
    print("\n🚀 Load Testing Demonstration")
    print("=" * 30)
    
    client = A2AClient.get_client_from_agent_card_url("http://localhost:8400")
    
    concurrent_requests = 5
    total_requests = 20
    
    print(f"Running {total_requests} requests with {concurrent_requests} concurrent connections...")
    
    async def send_request(request_id: int):
        start_time = time.time()
        
        try:
            response = await client.send_message(
                skill_id="enterprise_process",
                message={
                    "content": f"Load test request {request_id}",
                    "role": "load_tester",
                    "metadata": {"request_id": request_id}
                }
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "request_id": request_id,
                "success": response is not None and response.get("type") != "error",
                "processing_time_ms": processing_time,
                "response": response
            }
        
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "request_id": request_id,
                "success": False,
                "processing_time_ms": processing_time,
                "error": str(e)
            }
    
    # Execute load test
    semaphore = asyncio.Semaphore(concurrent_requests)
    
    async def limited_request(request_id):
        async with semaphore:
            return await send_request(request_id)
    
    start_time = time.time()
    
    tasks = [limited_request(i) for i in range(total_requests)]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful_requests = sum(1 for r in results if r["success"])
    failed_requests = total_requests - successful_requests
    avg_response_time = sum(r["processing_time_ms"] for r in results) / len(results)
    requests_per_second = total_requests / total_time
    
    print(f"\n📊 Load Test Results:")
    print(f"   Total requests: {total_requests}")
    print(f"   Successful: {successful_requests}")
    print(f"   Failed: {failed_requests}")
    print(f"   Success rate: {(successful_requests/total_requests)*100:.1f}%")
    print(f"   Average response time: {avg_response_time:.1f}ms")
    print(f"   Requests per second: {requests_per_second:.1f}")
    print(f"   Total test time: {total_time:.1f}s")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Run telemetry demonstrations
    await test_enterprise_agent_telemetry()
    await demonstrate_load_testing()
    
    print("\n🎯 Telemetry demonstration complete!")
    print("📈 Check Jaeger UI at http://localhost:16686 for detailed traces")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔍 Key Learning Points

### 1. A2A SDK Telemetry Integration
- Using `@trace_class` and `@trace_function` decorators for automatic tracing
- OpenTelemetry integration with A2A SDK telemetry utilities
- Distributed tracing across agent networks

### 2. Enterprise Monitoring Patterns
- Health check endpoints with comprehensive metrics
- Performance monitoring and alerting
- Agent registry and discovery for monitoring

### 3. Production-Ready Features
- Error handling and recovery mechanisms
- Performance optimization with telemetry insights
- Scalability patterns for enterprise deployments

### 4. Observability Stack
- Integration with Jaeger for distributed tracing
- Prometheus metrics collection
- Custom monitoring dashboards

## 🎯 Success Criteria

- [ ] Enterprise agents running with full telemetry enabled
- [ ] OpenTelemetry traces captured and viewable in Jaeger
- [ ] Health monitoring service tracking multiple agents
- [ ] Performance metrics collected and analyzed
- [ ] Load testing demonstrating scalability
- [ ] Comprehensive monitoring reports generated

## 🚀 Production Deployment

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "6831:6831/udp"
    environment:
      - COLLECTOR_ZIPKIN_HTTP_PORT=9411

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./infrastructure/observability/prometheus-config.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  enterprise-agent:
    build: .
    ports:
      - "8400:8400"
    environment:
      - JAEGER_AGENT_HOST=jaeger
      - JAEGER_AGENT_PORT=6831
    depends_on:
      - jaeger
      - prometheus
```

## 🏢 Next Steps - Production Readiness

After completing the enterprise features implementation:

1. **Kubernetes Deployment**: Deploy agents on Kubernetes for production scale
2. **Service Mesh Integration**: Integrate with Istio or Linkerd for advanced networking
3. **CI/CD Pipeline**: Implement automated testing and deployment
4. **Security Hardening**: Add production security measures
5. **Multi-Region Setup**: Deploy across multiple regions for high availability

## 📚 Additional Resources

- [A2A Python SDK Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/)
- [A2A Enterprise-Ready Features](https://google-a2a.github.io/A2A/topics/enterprise-ready/)
- [A2A Telemetry Documentation](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.utils.telemetry)
- [OpenTelemetry Python Documentation](https://opentelemetry-python.readthedocs.io/)
- [Production Deployment Best Practices](https://google-a2a.github.io/A2A/topics/life-of-a-task/) 