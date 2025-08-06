# Step 7: Agentic Integration - Building an MCP Server for RAG

## Learning Objectives
By the end of this module, you will be able to:
- Understand the Model Context Protocol (MCP) specification
- Build an MCP server that exposes RAG functionality to AI agents
- Design tool interfaces for different retrieval patterns
- Implement proper error handling and response formatting
- Enable AI agents to use your RAG system effectively

## Theoretical Foundation

### What is the Model Context Protocol (MCP)?

**MCP Overview:**
- **Purpose**: Standardized protocol for AI agents to access external tools and data
- **Architecture**: Client-server model with JSON-RPC communication
- **Benefits**: Interoperability, security, and structured tool access
- **Adoption**: Supported by major AI frameworks and platforms

**Why MCP for RAG:**
- **Agent Integration**: AI agents can seamlessly use your RAG system
- **Tool Abstraction**: Hide complexity behind simple function calls
- **Scalability**: Multiple agents can use the same RAG server
- **Maintenance**: Centralized RAG logic, distributed access

### MCP Architecture Components

**1. MCP Server (Your RAG System)**
```python
# Your RAG system exposed as MCP tools
class RAGMCPServer:
    def __init__(self):
        self.rag_system = AdvancedRAG()
        self.tools = self.register_tools()
    
    def register_tools(self):
        return {
            "search_documents": self.search_documents,
            "search_multimodal": self.search_multimodal,
            "hierarchical_search": self.hierarchical_search,
            "graph_search": self.graph_search
        }
```

**2. MCP Client (AI Agent)**
```python
# AI agent using your RAG tools
agent = PydanticAIAgent(
    model="gpt-4",
    tools=[
        mcp_client.get_tool("search_documents"),
        mcp_client.get_tool("search_multimodal")
    ]
)
```

**3. Communication Protocol**
```json
// Agent calls RAG tool
{
    "method": "tools/call",
    "params": {
        "name": "search_documents",
        "arguments": {
            "query": "How to implement authentication in Node.js?",
            "k": 5,
            "filters": {"domain": "backend"}
        }
    }
}

// RAG server responds
{
    "result": {
        "documents": [...],
        "metadata": {
            "total_found": 127,
            "search_time_ms": 45
        }
    }
}
```

## MCP Server Implementation

### Basic MCP Server Structure

**1. Server Setup**
```python
import asyncio
from mcp import Server
from mcp.types import Tool, TextContent, ImageContent
from typing import Any, Dict, List, Optional, Union

class RAGMCPServer:
    def __init__(self):
        self.server = Server("rag-server")
        self.rag_system = self.initialize_rag_system()
        self.register_tools()
    
    def initialize_rag_system(self) -> AdvancedRAG:
        """Initialize your RAG system with all components"""
        return AdvancedRAG(
            vector_db=MilvusDB(),
            embedder=GoogleEmbedder(),
            reranker=CrossEncoderReranker(),
            multimodal=True
        )
    
    def register_tools(self):
        """Register all RAG tools with the MCP server"""
        
        # Basic search tool
        @self.server.tool("search_documents")
        async def search_documents(
            query: str,
            k: int = 10,
            filters: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
            """Search for relevant documents using semantic similarity"""
            return await self._search_documents(query, k, filters)
        
        # Multimodal search tool
        @self.server.tool("search_multimodal")
        async def search_multimodal(
            query: str,
            content_types: List[str] = ["text", "image"],
            k: int = 10
        ) -> List[Dict[str, Any]]:
            """Search across multiple content types (text, images, audio)"""
            return await self._search_multimodal(query, content_types, k)
        
        # Hierarchical search tool
        @self.server.tool("hierarchical_search")
        async def hierarchical_search(
            query: str,
            max_depth: int = 3,
            k: int = 10
        ) -> Dict[str, Any]:
            """Perform hierarchical search from general to specific"""
            return await self._hierarchical_search(query, max_depth, k)
        
        # Graph-based search tool
        @self.server.tool("graph_search")
        async def graph_search(
            query: str,
            entities: Optional[List[str]] = None,
            max_hops: int = 2,
            k: int = 10
        ) -> Dict[str, Any]:
            """Search using knowledge graph relationships"""
            return await self._graph_search(query, entities, max_hops, k)
```

### Tool Implementation Details

**1. Document Search Tool**
```python
async def _search_documents(
    self,
    query: str,
    k: int,
    filters: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Implement document search with proper error handling"""
    
    try:
        # Validate inputs
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        if k <= 0 or k > 100:
            raise ValueError("k must be between 1 and 100")
        
        # Perform search
        search_results = await asyncio.get_event_loop().run_in_executor(
            None,
            self.rag_system.search,
            query,
            k,
            filters
        )
        
        # Format results for MCP
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "content": result.content,
                "score": float(result.score),
                "metadata": {
                    "source": result.source,
                    "title": result.title,
                    "page": result.page,
                    "chunk_id": result.chunk_id
                }
            })
        
        return formatted_results
        
    except Exception as e:
        # Log error and return structured error response
        logger.error(f"Search error: {str(e)}")
        return [{
            "error": True,
            "message": f"Search failed: {str(e)}",
            "type": type(e).__name__
        }]
```

**2. Multimodal Search Tool**
```python
async def _search_multimodal(
    self,
    query: str,
    content_types: List[str],
    k: int
) -> List[Dict[str, Any]]:
    """Search across multiple modalities"""
    
    try:
        # Validate content types
        valid_types = {"text", "image", "audio", "video"}
        invalid_types = set(content_types) - valid_types
        if invalid_types:
            raise ValueError(f"Invalid content types: {invalid_types}")
        
        # Perform multimodal search
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            self.rag_system.multimodal_search,
            query,
            content_types,
            k
        )
        
        # Format results with modality information
        formatted_results = []
        for result in results:
            formatted_result = {
                "content": result.content,
                "score": float(result.score),
                "modality": result.modality,
                "metadata": result.metadata
            }
            
            # Add modality-specific fields
            if result.modality == "image":
                formatted_result["image_url"] = result.image_url
                formatted_result["alt_text"] = result.alt_text
            elif result.modality == "audio":
                formatted_result["transcript"] = result.transcript
                formatted_result["duration"] = result.duration
            
            formatted_results.append(formatted_result)
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Multimodal search error: {str(e)}")
        return [{"error": True, "message": str(e)}]
```

**3. Hierarchical Search Tool**
```python
async def _hierarchical_search(
    self,
    query: str,
    max_depth: int,
    k: int
) -> Dict[str, Any]:
    """Hierarchical search with structured navigation"""
    
    try:
        # Perform hierarchical search
        hierarchy_results = await asyncio.get_event_loop().run_in_executor(
            None,
            self.rag_system.hierarchical_search,
            query,
            max_depth,
            k
        )
        
        # Structure results hierarchically
        structured_results = {
            "query": query,
            "hierarchy": [],
            "total_results": len(hierarchy_results.all_results),
            "search_path": hierarchy_results.search_path
        }
        
        # Group results by hierarchy level
        for level in range(max_depth):
            level_results = hierarchy_results.get_level_results(level)
            structured_results["hierarchy"].append({
                "level": level,
                "description": hierarchy_results.get_level_description(level),
                "results": [
                    {
                        "content": r.content,
                        "score": float(r.score),
                        "heading": r.heading,
                        "parent_context": r.parent_context,
                        "metadata": r.metadata
                    }
                    for r in level_results
                ]
            })
        
        return structured_results
        
    except Exception as e:
        logger.error(f"Hierarchical search error: {str(e)}")
        return {"error": True, "message": str(e)}
```

### Advanced Tool Features

**1. Conversation-Aware Search**
```python
@self.server.tool("conversational_search")
async def conversational_search(
    query: str,
    conversation_history: List[Dict[str, str]],
    k: int = 10
) -> Dict[str, Any]:
    """Search with conversation context awareness"""
    
    try:
        # Build conversation context
        context = ConversationContext(
            current_query=query,
            history=conversation_history
        )
        
        # Perform context-aware search
        results = await asyncio.get_event_loop().run_in_executor(
            None,
            self.rag_system.conversational_search,
            context,
            k
        )
        
        return {
            "results": [self._format_result(r) for r in results],
            "context_used": results.context_summary,
            "resolved_query": results.resolved_query,
            "metadata": {
                "conversation_turns": len(conversation_history),
                "context_entities": results.context_entities
            }
        }
        
    except Exception as e:
        logger.error(f"Conversational search error: {str(e)}")
        return {"error": True, "message": str(e)}
```

**2. Batch Search Tool**
```python
@self.server.tool("batch_search")
async def batch_search(
    queries: List[str],
    k_per_query: int = 5
) -> Dict[str, Any]:
    """Process multiple queries efficiently"""
    
    try:
        if len(queries) > 50:
            raise ValueError("Maximum 50 queries per batch")
        
        # Process queries in parallel
        tasks = [
            asyncio.get_event_loop().run_in_executor(
                None,
                self.rag_system.search,
                query,
                k_per_query
            )
            for query in queries
        ]
        
        batch_results = await asyncio.gather(*tasks)
        
        # Format batch response
        formatted_batch = {
            "total_queries": len(queries),
            "results": []
        }
        
        for i, (query, results) in enumerate(zip(queries, batch_results)):
            formatted_batch["results"].append({
                "query_index": i,
                "query": query,
                "results": [self._format_result(r) for r in results],
                "result_count": len(results)
            })
        
        return formatted_batch
        
    except Exception as e:
        logger.error(f"Batch search error: {str(e)}")
        return {"error": True, "message": str(e)}
```

### Resource Management Tools

**1. Index Management**
```python
@self.server.tool("manage_index")
async def manage_index(
    action: str,
    document_path: Optional[str] = None,
    document_id: Optional[str] = None
) -> Dict[str, Any]:
    """Manage document index (add, remove, update documents)"""
    
    try:
        if action == "add" and document_path:
            result = await self._add_document(document_path)
        elif action == "remove" and document_id:
            result = await self._remove_document(document_id)
        elif action == "update" and document_path and document_id:
            result = await self._update_document(document_id, document_path)
        elif action == "status":
            result = await self._get_index_status()
        else:
            raise ValueError(f"Invalid action or missing parameters: {action}")
        
        return {"success": True, "result": result}
        
    except Exception as e:
        logger.error(f"Index management error: {str(e)}")
        return {"error": True, "message": str(e)}

async def _add_document(self, document_path: str) -> Dict[str, Any]:
    """Add a new document to the index"""
    
    # Process document
    chunks = await asyncio.get_event_loop().run_in_executor(
        None,
        self.rag_system.process_document,
        document_path
    )
    
    # Add to index
    document_id = await asyncio.get_event_loop().run_in_executor(
        None,
        self.rag_system.add_chunks,
        chunks
    )
    
    return {
        "document_id": document_id,
        "chunks_added": len(chunks),
        "document_path": document_path
    }
```

**2. Search Analytics Tool**
```python
@self.server.tool("search_analytics")
async def search_analytics(
    time_range_hours: int = 24
) -> Dict[str, Any]:
    """Get search analytics and performance metrics"""
    
    try:
        analytics = await asyncio.get_event_loop().run_in_executor(
            None,
            self.rag_system.get_analytics,
            time_range_hours
        )
        
        return {
            "time_range_hours": time_range_hours,
            "total_searches": analytics.total_searches,
            "average_response_time_ms": analytics.avg_response_time,
            "most_common_queries": analytics.top_queries,
            "search_patterns": analytics.search_patterns,
            "error_rate": analytics.error_rate,
            "index_stats": {
                "total_documents": analytics.total_documents,
                "total_chunks": analytics.total_chunks,
                "index_size_mb": analytics.index_size_mb
            }
        }
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return {"error": True, "message": str(e)}
```

## Agent Integration Patterns

### 1. Simple Q&A Agent
```python
# Agent using basic search
@agent.system_prompt
async def rag_qa_agent(ctx: RunContext[None]) -> str:
    return """
    You are a helpful assistant with access to a document search system.
    Use the search_documents tool to find relevant information before answering questions.
    Always cite your sources and indicate the confidence level of your answers.
    """

@agent.tool
async def search_documents(
    query: str,
    k: int = 5
) -> List[Dict[str, Any]]:
    """Search for relevant documents"""
    # This connects to your MCP server
    return await mcp_client.call_tool("search_documents", {
        "query": query,
        "k": k
    })

# Usage
response = await agent.run("How do I implement OAuth2 in Python?")
```

### 2. Research Synthesis Agent
```python
@agent.system_prompt
async def research_agent(ctx: RunContext[None]) -> str:
    return """
    You are a research assistant that synthesizes information from multiple sources.
    Use hierarchical_search for complex topics and graph_search for entity relationships.
    Provide comprehensive answers with proper citations and cross-references.
    """

@agent.tool
async def comprehensive_search(
    query: str,
    search_depth: str = "medium"
) -> Dict[str, Any]:
    """Perform comprehensive multi-stage search"""
    
    # Start with hierarchical search
    hierarchy_results = await mcp_client.call_tool("hierarchical_search", {
        "query": query,
        "max_depth": 3 if search_depth == "deep" else 2
    })
    
    # Follow up with graph search if entities found
    if hierarchy_results.get("context_entities"):
        graph_results = await mcp_client.call_tool("graph_search", {
            "query": query,
            "entities": hierarchy_results["context_entities"]
        })
    else:
        graph_results = None
    
    return {
        "hierarchy": hierarchy_results,
        "graph": graph_results,
        "synthesis_required": True
    }
```

### 3. Multimodal Content Agent
```python
@agent.system_prompt
async def multimodal_agent(ctx: RunContext[None]) -> str:
    return """
    You can search and analyze both text and visual content.
    Use search_multimodal for questions about images, diagrams, or visual content.
    Describe visual content when relevant and explain relationships between text and images.
    """

@agent.tool
async def analyze_visual_content(
    query: str,
    include_images: bool = True
) -> Dict[str, Any]:
    """Search for visual content and provide analysis"""
    
    content_types = ["text"]
    if include_images:
        content_types.append("image")
    
    results = await mcp_client.call_tool("search_multimodal", {
        "query": query,
        "content_types": content_types,
        "k": 10
    })
    
    # Separate text and image results
    text_results = [r for r in results if r["modality"] == "text"]
    image_results = [r for r in results if r["modality"] == "image"]
    
    return {
        "text_content": text_results,
        "visual_content": image_results,
        "has_visual_answers": len(image_results) > 0
    }
```

## Error Handling and Monitoring

### Robust Error Handling
```python
class RAGErrorHandler:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.last_errors = []
    
    async def handle_tool_error(self, tool_name: str, error: Exception) -> Dict[str, Any]:
        """Standardized error handling for all tools"""
        
        error_type = type(error).__name__
        error_message = str(error)
        
        # Log error
        logger.error(f"Tool {tool_name} error: {error_type}: {error_message}")
        
        # Track error statistics
        self.error_counts[f"{tool_name}:{error_type}"] += 1
        self.last_errors.append({
            "tool": tool_name,
            "error_type": error_type,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 errors
        if len(self.last_errors) > 100:
            self.last_errors = self.last_errors[-100:]
        
        # Return structured error response
        return {
            "error": True,
            "error_type": error_type,
            "message": error_message,
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "suggestions": self._get_error_suggestions(error_type, error_message)
        }
    
    def _get_error_suggestions(self, error_type: str, message: str) -> List[str]:
        """Provide helpful suggestions based on error type"""
        
        suggestions = []
        
        if error_type == "ValueError":
            if "empty" in message.lower():
                suggestions.append("Ensure your query is not empty")
            if "range" in message.lower():
                suggestions.append("Check parameter values are within valid ranges")
        
        elif error_type == "TimeoutError":
            suggestions.append("Try a simpler query or reduce the number of results")
            suggestions.append("Check if the search index is available")
        
        elif error_type == "ConnectionError":
            suggestions.append("Check database connectivity")
            suggestions.append("Verify the search service is running")
        
        return suggestions
```

### Performance Monitoring
```python
class RAGPerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "search_times": [],
            "result_counts": [],
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def monitor_search(self, tool_name: str, func, *args, **kwargs):
        """Monitor performance of search operations"""
        
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            # Record success metrics
            execution_time = (time.time() - start_time) * 1000  # ms
            self.metrics["search_times"].append(execution_time)
            
            if isinstance(result, list):
                self.metrics["result_counts"].append(len(result))
            
            # Add performance metadata to result
            if isinstance(result, dict) and not result.get("error"):
                result["performance"] = {
                    "execution_time_ms": round(execution_time, 2),
                    "cache_status": "hit" if execution_time < 50 else "miss"
                }
            
            return result
            
        except Exception as e:
            # Record failure metrics
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Performance monitoring error in {tool_name}: {str(e)}")
            raise
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        
        if not self.metrics["search_times"]:
            return {"message": "No search data available"}
        
        search_times = self.metrics["search_times"]
        
        return {
            "average_search_time_ms": statistics.mean(search_times),
            "median_search_time_ms": statistics.median(search_times),
            "95th_percentile_ms": np.percentile(search_times, 95),
            "total_searches": len(search_times),
            "average_results_per_search": statistics.mean(self.metrics["result_counts"]),
            "cache_hit_rate": self.metrics["cache_hits"] / (
                self.metrics["cache_hits"] + self.metrics["cache_misses"]
            ) if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
        }
```

## Server Deployment and Configuration

### Production Server Setup
```python
async def run_rag_mcp_server():
    """Run the RAG MCP server in production"""
    
    # Initialize server with configuration
    server = RAGMCPServer()
    
    # Add middleware for logging, monitoring, etc.
    server.add_middleware(LoggingMiddleware())
    server.add_middleware(PerformanceMiddleware())
    server.add_middleware(AuthenticationMiddleware())
    
    # Configure server settings
    server.configure({
        "max_concurrent_requests": 100,
        "request_timeout_seconds": 30,
        "enable_caching": True,
        "cache_ttl_seconds": 300
    })
    
    # Start server
    await server.run(host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(run_rag_mcp_server())
```

### Configuration Management
```python
# config.yaml
rag_server:
  vector_db:
    type: "milvus"
    host: "localhost"
    port: 19530
    collection_name: "documents"
  
  embeddings:
    model: "text-embedding-ada-002"
    batch_size: 100
    cache_enabled: true
  
  search:
    default_k: 10
    max_k: 100
    timeout_seconds: 30
  
  multimodal:
    enabled: true
    clip_model: "ViT-B/32"
    image_processing: true
  
  performance:
    enable_monitoring: true
    log_slow_queries: true
    slow_query_threshold_ms: 1000
```

## What We'll Build

### Complete MCP RAG Server
```python
class ProductionRAGMCPServer:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.server = Server("production-rag-server")
        self.rag_system = self.initialize_rag_system()
        self.error_handler = RAGErrorHandler()
        self.performance_monitor = RAGPerformanceMonitor()
        
        self.register_all_tools()
    
    def register_all_tools(self):
        """Register comprehensive set of RAG tools"""
        
        # Core search tools
        self.register_search_tools()
        
        # Advanced search tools
        self.register_advanced_search_tools()
        
        # Management tools
        self.register_management_tools()
        
        # Analytics tools
        self.register_analytics_tools()
    
    async def start_server(self):
        """Start the production MCP server"""
        logger.info("Starting RAG MCP Server...")
        await self.server.run()
```

### Features to Implement
1. **Complete tool suite**: All RAG functionality exposed via MCP
2. **Error handling**: Robust error management and reporting
3. **Performance monitoring**: Real-time metrics and optimization
4. **Agent integration**: Multiple agent patterns and examples
5. **Production deployment**: Scalable server configuration

## Success Criteria
- Build working MCP server that exposes RAG functionality
- Demonstrate AI agent successfully using RAG tools
- Implement proper error handling and monitoring
- Show performance improvements from caching and optimization
- Deploy server that can handle multiple concurrent agent requests

---

**Next Step**: In Step 8, we'll implement comprehensive evaluation metrics to measure and improve the quality of our RAG system.
