# Step 09: Configuration - Production Optimization (Theory)

Master Graphiti configuration for production systems with security, performance, and scalability in mind.

## 📚 Official Documentation

- [LLM Configuration](https://help.getzep.com/graphiti/configuration/llm-configuration) - LLM provider setup and optimization
- [GraphDB Configuration](https://help.getzep.com/graphiti/configuration/graph-db-configuration) - Neo4j optimization for production

## 📚 Production Configuration Fundamentals

### Why Configuration Matters for Educational AI

**AI systems have unique requirements:**
- **Scale**: Handle thousands of students, courses, and interactions
- **Privacy**: FERPA compliance and student data protection
- **Performance**: Real-time responses for interactive learning
- **Cost**: Balance LLM API costs with budgets
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

**What's Coming**: Understand how all these Graphiti concepts come together in real-world production systems!

---

**Key Takeaway**: Production configuration is where educational AI meets operational reality. Balance learning effectiveness with security, performance, and cost constraints for sustainable educational AI systems! ⚙️

*"The best educational AI configuration optimizes for learning outcomes while respecting budget constraints and compliance requirements."*