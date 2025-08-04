# Step 10: Configuration - Production Optimization

Master Graphiti configuration for production educational systems with security, performance, and scalability in mind.

## 📚 Official Documentation

- [LLM Configuration](https://help.getzep.com/graphiti/configuration/llm-configuration) - LLM provider setup and optimization
- [GraphDB Configuration](https://help.getzep.com/graphiti/configuration/graph-db-configuration) - Neo4j optimization for production

## 🎯 What You'll Learn

By the end of this step, you will:
- Optimize LLM configurations for educational content processing
- Configure Neo4j for educational workloads and large student populations
- Implement production security and FERPA compliance settings
- Design scalable multi-institutional configuration strategies
- Apply monitoring and observability for educational AI platforms

## 📋 Prerequisites

- Completed Steps 01-09
- Understanding of production deployment concepts
- Basic knowledge of database optimization
- Familiarity with security and compliance requirements

## 📚 Production Configuration Fundamentals

### Why Configuration Matters for Educational AI

**Educational AI systems have unique requirements:**
- **Scale**: Handle thousands of students, courses, and interactions
- **Privacy**: FERPA compliance and student data protection
- **Performance**: Real-time responses for interactive learning
- **Cost**: Balance LLM API costs with educational budgets
- **Reliability**: 24/7 availability for global student populations

### Key Configuration Areas

1. **LLM Configuration**: Model selection, API limits, cost optimization
2. **Database Configuration**: Memory, indexing, backup strategies
3. **Security Configuration**: Authentication, encryption, compliance
4. **Performance Configuration**: Caching, connection pooling, scaling
5. **Monitoring Configuration**: Logging, metrics, alerting

## 🚀 Complete Configuration Examples

### Production-Ready LLM Configuration

```python
# production_graphiti_config.py
import os
from typing import Optional
from graphiti_core import Graphiti
from graphiti_core.llm_client.openai_client import OpenAIClient, LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient

class EducationalGraphitiConfig:
    """Production configuration for educational Graphiti systems"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.config = self._get_environment_config()
    
    def _get_environment_config(self) -> dict:
        """Get configuration based on environment"""
        
        base_config = {
            # Neo4j configuration
            "neo4j_uri": os.getenv("NEO4J_URI"),
            "neo4j_user": os.getenv("NEO4J_USER", "neo4j"),
            "neo4j_password": os.getenv("NEO4J_PASSWORD"),
            
            # Security
            "use_ssl": True,
            "verify_ssl": True,
            
            # Performance
            "max_connections": 100,
            "connection_timeout": 30,
            "read_timeout": 60,
        }
        
        if self.environment == "production":
            return {
                **base_config,
                # Production LLM settings
                "llm_config": LLMConfig(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="gpt-4-turbo-preview",  # Better for educational content
                    max_tokens=4000,
                    temperature=0.1,  # Lower temperature for consistency
                    top_p=0.9,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    request_timeout=30,
                    max_retries=3,
                    # Educational domain optimization
                    system_prompt="""You are analyzing educational content and student interactions.
                    Focus on identifying:
                    - Students, instructors, courses, academic concepts
                    - Learning relationships and skill progressions  
                    - Assessment outcomes and performance patterns
                    - Temporal learning sequences and prerequisites
                    - Academic achievements and challenges
                    
                    Maintain high accuracy for educational terminology and relationships."""
                ),
                
                # Production embeddings
                "embedder_config": OpenAIEmbedderConfig(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="text-embedding-3-large",  # Higher quality embeddings
                    batch_size=100,
                    request_timeout=30,
                    max_retries=3
                ),
                
                # Production reranker
                "reranker_config": LLMConfig(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="gpt-4-turbo-preview",
                    max_tokens=1000,
                    temperature=0.0,  # Deterministic reranking
                ),
                
                # Caching for cost optimization
                "enable_caching": True,
                "cache_ttl": 3600,  # 1 hour cache
                
                # Rate limiting
                "requests_per_minute": 500,
                "concurrent_requests": 20,
                
                # Monitoring
                "enable_metrics": True,
                "log_level": "INFO"
            }
            
        elif self.environment == "staging":
            return {
                **base_config,
                "llm_config": LLMConfig(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="gpt-3.5-turbo",  # Cost-effective for testing
                    max_tokens=2000,
                    temperature=0.2,
                    request_timeout=20,
                    max_retries=2
                ),
                "embedder_config": OpenAIEmbedderConfig(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="text-embedding-ada-002",  # Cheaper embeddings
                    batch_size=50
                ),
                "enable_caching": True,
                "cache_ttl": 1800,  # 30 minutes
                "requests_per_minute": 100,
                "concurrent_requests": 10,
                "log_level": "DEBUG"
            }
            
        else:  # development
            return {
                **base_config,
                "llm_config": LLMConfig(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="gpt-3.5-turbo",
                    max_tokens=1000,
                    temperature=0.3,
                    request_timeout=15,
                    max_retries=1
                ),
                "embedder_config": OpenAIEmbedderConfig(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    model="text-embedding-ada-002",
                    batch_size=10
                ),
                "enable_caching": False,  # Fresh data for development
                "requests_per_minute": 50,
                "concurrent_requests": 5,
                "log_level": "DEBUG"
            }
    
    def create_graphiti_client(self) -> Graphiti:
        """Create configured Graphiti client"""
        
        config = self.config
        
        return Graphiti(
            uri=config["neo4j_uri"],
            user=config["neo4j_user"], 
            password=config["neo4j_password"],
            
            llm_client=OpenAIClient(config=config["llm_config"]),
            embedder=OpenAIEmbedder(config=config["embedder_config"]),
            cross_encoder=OpenAIRerankerClient(config=config["reranker_config"]),
            
            # Performance settings
            max_concurrent_operations=config["concurrent_requests"],
            operation_timeout=config.get("read_timeout", 60),
            
            # Caching
            enable_cache=config.get("enable_caching", False),
            cache_ttl_seconds=config.get("cache_ttl", 3600),
        )

# Usage examples
def get_production_client():
    """Get production-ready Graphiti client"""
    config = EducationalGraphitiConfig("production")
    return config.create_graphiti_client()

def get_development_client():
    """Get development Graphiti client"""
    config = EducationalGraphitiConfig("development")
    return config.create_graphiti_client()
```

### Neo4j Production Configuration

```bash
# neo4j.conf - Optimized for educational workloads

# =========================================
# MEMORY CONFIGURATION
# =========================================

# Heap memory - for graph operations and query processing
server.memory.heap.initial_size=4G
server.memory.heap.max_size=8G

# Page cache - for storing graph data in memory
# Set to ~50% of available RAM minus heap
server.memory.pagecache.size=6G

# Transaction state memory
db.memory.transaction.total.max=1G

# =========================================
# PERFORMANCE TUNING
# =========================================

# Query optimization
cypher.min_replan_interval=10m
cypher.statistics_divergence_threshold=0.75
cypher.planner=COST

# Connection pooling for educational workloads
server.bolt.thread_pool_min_size=5
server.bolt.thread_pool_max_size=400
server.bolt.connection_keep_alive=60s

# I/O performance
dbms.memory.pagecache.warmup.enabled=true
dbms.memory.pagecache.warmup.preload=true

# =========================================
# EDUCATIONAL DATA OPTIMIZATION
# =========================================

# Index configuration for educational queries
db.index.default_schema_provider=native-btree-1.0
db.index.fulltext.default_provider=lucene

# Relationship indexing for learning paths
db.relationship_property_index.enabled=true

# =========================================
# SECURITY (FERPA Compliance)
# =========================================

# Authentication required
dbms.security.auth_enabled=true
dbms.security.auth_providers=native

# SSL/TLS encryption
dbms.ssl.policy.bolt.enabled=true
dbms.ssl.policy.bolt.base_directory=certificates/bolt
dbms.ssl.policy.bolt.client_auth=REQUIRE

# Audit logging for compliance
dbms.security.audit.enabled=true
dbms.security.audit.log_query=true
dbms.security.audit.log_query_allocation=true

# =========================================
# BACKUP AND RECOVERY
# =========================================

# Automated backups for student data protection
server.backup.enabled=true
server.backup.listen_address=0.0.0.0:6362

# Transaction logging
db.tx_log.rotation.retention_policy=7 days
db.tx_log.rotation.size=250M

# =========================================
# MONITORING AND OBSERVABILITY
# =========================================

# Metrics collection
server.metrics.enabled=true
server.metrics.prometheus.enabled=true
server.metrics.prometheus.endpoint=localhost:2004

# Query logging for performance analysis
dbms.logs.query.enabled=true
dbms.logs.query.threshold=1s
dbms.logs.query.parameter_logging_enabled=true

# =========================================
# CLUSTERING (Multi-Institution Setup)
# =========================================

# Causal clustering for high availability
causal_clustering.minimum_core_cluster_size_at_formation=3
causal_clustering.initial_discovery_members=neo4j-core-1:5000,neo4j-core-2:5000,neo4j-core-3:5000

# Read replica configuration for global access
causal_clustering.read_replica_join_catchup_timeout=10m
```

### Environment-Specific Configuration

```python
# config_manager.py
import os
import json
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    name: str
    llm_model: str
    embedding_model: str
    max_concurrent: int
    cache_enabled: bool
    cache_ttl: int
    log_level: str
    monitoring_enabled: bool
    cost_optimization: bool

class ConfigManager:
    """Manage configurations across environments"""
    
    ENVIRONMENTS = {
        "development": EnvironmentConfig(
            name="development",
            llm_model="gpt-3.5-turbo",
            embedding_model="text-embedding-ada-002", 
            max_concurrent=5,
            cache_enabled=False,
            cache_ttl=0,
            log_level="DEBUG",
            monitoring_enabled=False,
            cost_optimization=True
        ),
        
        "staging": EnvironmentConfig(
            name="staging",
            llm_model="gpt-3.5-turbo",
            embedding_model="text-embedding-ada-002",
            max_concurrent=15,
            cache_enabled=True,
            cache_ttl=1800,
            log_level="INFO", 
            monitoring_enabled=True,
            cost_optimization=True
        ),
        
        "production": EnvironmentConfig(
            name="production",
            llm_model="gpt-4-turbo-preview",
            embedding_model="text-embedding-3-large",
            max_concurrent=50,
            cache_enabled=True,
            cache_ttl=3600,
            log_level="WARNING",
            monitoring_enabled=True,
            cost_optimization=False  # Prioritize quality over cost
        )
    }
    
    @classmethod
    def get_config(cls, environment: str = None) -> EnvironmentConfig:
        """Get configuration for environment"""
        env = environment or os.getenv("ENVIRONMENT", "development")
        return cls.ENVIRONMENTS.get(env, cls.ENVIRONMENTS["development"])
    
    @classmethod
    def validate_config(cls, config: EnvironmentConfig) -> bool:
        """Validate configuration settings"""
        required_env_vars = [
            "OPENAI_API_KEY",
            "NEO4J_URI", 
            "NEO4J_PASSWORD"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
            
        return True

# Usage
config = ConfigManager.get_config("production")
ConfigManager.validate_config(config)
```

### Monitoring and Observability

```python
# monitoring.py
import logging
import time
from typing import Dict, Any
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Educational AI metrics
STUDENT_QUERIES = Counter('tutorsgpt_student_queries_total', 'Total student queries', ['course', 'topic'])
LEARNING_INSIGHTS = Counter('tutorsgpt_learning_insights_generated', 'Learning insights generated')
RESPONSE_TIME = Histogram('tutorsgpt_response_time_seconds', 'Response time for queries')
ACTIVE_STUDENTS = Gauge('tutorsgpt_active_students', 'Currently active students')
LLM_API_CALLS = Counter('tutorsgpt_llm_api_calls_total', 'LLM API calls', ['model', 'type'])
KNOWLEDGE_GRAPH_SIZE = Gauge('tutorsgpt_knowledge_graph_nodes', 'Nodes in knowledge graph')

class EducationalObservability:
    """Monitoring and observability for educational AI systems"""
    
    def __init__(self, graphiti_client, log_level: str = "INFO"):
        self.client = graphiti_client
        self.setup_logging(log_level)
        self.setup_metrics()
    
    def setup_logging(self, log_level: str):
        """Configure structured logging for educational AI"""
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tutorsgpt.log'),
                logging.StreamHandler()
            ]
        )
        
        # Create specialized loggers
        self.query_logger = logging.getLogger('tutorsgpt.queries')
        self.learning_logger = logging.getLogger('tutorsgpt.learning')
        self.performance_logger = logging.getLogger('tutorsgpt.performance')
    
    def setup_metrics(self):
        """Start Prometheus metrics server"""
        start_http_server(8000)  # Metrics available at :8000/metrics
    
    @asynccontextmanager
    async def track_query(self, student_id: str, course: str, topic: str):
        """Track student query with metrics and logging"""
        
        start_time = time.time()
        
        try:
            # Log query start
            self.query_logger.info(
                f"Student query started - Student: {student_id}, Course: {course}, Topic: {topic}"
            )
            
            # Update metrics
            STUDENT_QUERIES.labels(course=course, topic=topic).inc()
            ACTIVE_STUDENTS.inc()
            
            yield
            
        except Exception as e:
            # Log errors
            self.query_logger.error(
                f"Query failed - Student: {student_id}, Error: {str(e)}"
            )
            raise
            
        finally:
            # Track completion
            duration = time.time() - start_time
            RESPONSE_TIME.observe(duration)
            ACTIVE_STUDENTS.dec()
            
            self.performance_logger.info(
                f"Query completed - Duration: {duration:.2f}s, Student: {student_id}"
            )
    
    async def track_learning_insight(self, insight_type: str, student_id: str, details: Dict[str, Any]):
        """Track generated learning insights"""
        
        LEARNING_INSIGHTS.inc()
        
        self.learning_logger.info(
            f"Learning insight generated - Type: {insight_type}, "
            f"Student: {student_id}, Details: {details}"
        )
    
    async def track_llm_usage(self, model: str, operation_type: str, tokens_used: int):
        """Track LLM API usage for cost monitoring"""
        
        LLM_API_CALLS.labels(model=model, type=operation_type).inc()
        
        self.performance_logger.info(
            f"LLM API call - Model: {model}, Type: {operation_type}, Tokens: {tokens_used}"
        )
    
    async def update_knowledge_graph_metrics(self):
        """Update knowledge graph size metrics"""
        
        try:
            # Get graph statistics (simplified example)
            results = await self.client.search("", num_results=1)  # This would need actual graph size query
            # KNOWLEDGE_GRAPH_SIZE.set(node_count)  # Would set actual count
            
        except Exception as e:
            self.performance_logger.error(f"Failed to update graph metrics: {e}")

# Usage example
async def example_monitored_query():
    """Example of using monitoring in educational queries"""
    
    config = EducationalGraphitiConfig("production")
    client = config.create_graphiti_client()
    observability = EducationalObservability(client, "INFO")
    
    async with observability.track_query("alice_001", "CS101", "Python Loops"):
        # Perform student query
        results = await client.search("Alice learning progress Python loops")
        
        # Track insights generated
        await observability.track_learning_insight(
            "progress_analysis",
            "alice_001", 
            {"concepts_mastered": 3, "areas_for_improvement": 1}
        )
        
        # Track LLM usage
        await observability.track_llm_usage("gpt-4-turbo", "entity_extraction", 250)
        
        return results
```

## 🧪 Configuration Examples for Different Scenarios

### Multi-Institutional Setup

```python
# multi_institution_config.py
class MultiInstitutionConfig:
    """Configuration for multiple educational institutions"""
    
    INSTITUTION_CONFIGS = {
        "stanford": {
            "namespace": "stanford_university",
            "llm_budget_tier": "premium",  # Higher quality models
            "max_students": 50000,
            "compliance_level": "high",
            "cache_strategy": "aggressive"
        },
        "community_college": {
            "namespace": "community_college_network", 
            "llm_budget_tier": "standard",  # Cost-optimized models
            "max_students": 5000,
            "compliance_level": "standard",
            "cache_strategy": "moderate"
        }
    }
    
    def get_institution_client(self, institution_id: str) -> Graphiti:
        """Get configured client for specific institution"""
        
        inst_config = self.INSTITUTION_CONFIGS.get(institution_id)
        if not inst_config:
            raise ValueError(f"Unknown institution: {institution_id}")
        
        # Adjust configuration based on institution needs
        if inst_config["llm_budget_tier"] == "premium":
            model = "gpt-4-turbo-preview"
            embedding_model = "text-embedding-3-large"
            max_concurrent = 50
        else:
            model = "gpt-3.5-turbo"
            embedding_model = "text-embedding-ada-002"
            max_concurrent = 20
        
        return Graphiti(
            uri=os.getenv(f"NEO4J_URI_{institution_id.upper()}"),
            user=os.getenv("NEO4J_USER"),
            password=os.getenv(f"NEO4J_PASSWORD_{institution_id.upper()}"),
            # ... configured based on institution needs
        )
```

### Cost Optimization Configuration

```python
# cost_optimization.py
class CostOptimizedConfig:
    """Configuration focused on minimizing LLM costs"""
    
    def __init__(self):
        self.cost_tracking = {
            "daily_budget": float(os.getenv("DAILY_LLM_BUDGET", "100.0")),
            "current_spend": 0.0,
            "alert_threshold": 0.8
        }
    
    def get_budget_aware_config(self) -> dict:
        """Get configuration that adapts based on budget usage"""
        
        budget_usage = self.cost_tracking["current_spend"] / self.cost_tracking["daily_budget"]
        
        if budget_usage < 0.5:
            # Low usage - can use premium models
            return {
                "llm_model": "gpt-4-turbo-preview",
                "embedding_model": "text-embedding-3-large",
                "cache_ttl": 1800,  # 30 minutes
                "batch_size": 50
            }
        elif budget_usage < 0.8:
            # Medium usage - balance cost and quality
            return {
                "llm_model": "gpt-3.5-turbo",
                "embedding_model": "text-embedding-ada-002", 
                "cache_ttl": 3600,  # 1 hour
                "batch_size": 100
            }
        else:
            # High usage - aggressive cost optimization
            return {
                "llm_model": "gpt-3.5-turbo",
                "embedding_model": "text-embedding-ada-002",
                "cache_ttl": 7200,  # 2 hours
                "batch_size": 200,
                "reduce_quality": True
            }
```

## ✅ Configuration Checklist

### Security & Compliance
- [ ] SSL/TLS encryption enabled
- [ ] Authentication configured
- [ ] Audit logging enabled for FERPA compliance
- [ ] Data encryption at rest
- [ ] Access controls properly configured

### Performance & Scalability  
- [ ] Appropriate memory allocation for student load
- [ ] Connection pooling configured
- [ ] Caching strategy implemented
- [ ] Index optimization for educational queries
- [ ] Backup and recovery tested

### Cost Management
- [ ] Budget-aware LLM model selection
- [ ] Aggressive caching for cost reduction
- [ ] Batch processing optimization
- [ ] Usage monitoring and alerting
- [ ] Cost allocation by institution/course

### Monitoring & Observability
- [ ] Structured logging configured
- [ ] Prometheus metrics collection
- [ ] Educational-specific metrics tracked
- [ ] Alerting for system issues
- [ ] Performance dashboards

## 🎯 Next Steps

**Excellent work!** You now understand how to configure Graphiti for production educational systems with security, performance, and cost considerations.

**Ready to understand the bigger picture?** Continue to **[11_zep_memory](../11_zep_memory/)** to see how Graphiti powers Zep's production memory architecture and fits into the broader agentic AI ecosystem.

**What's Coming**: Understand how all these Graphiti concepts come together in real-world production systems!

---

**Key Takeaway**: Production configuration is where educational AI meets operational reality. Balance learning effectiveness with security, performance, and cost constraints for sustainable educational AI systems! ⚙️

*"The best educational AI configuration optimizes for learning outcomes while respecting budget constraints and compliance requirements."*