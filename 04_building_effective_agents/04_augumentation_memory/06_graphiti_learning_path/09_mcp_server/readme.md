# Step 09: [MCP Server Integration](https://help.getzep.com/graphiti/getting-started/mcp-server) - AI Assistant Integration

Welcome to Step 09! Master Graphiti's Model Context Protocol server for AI assistant integration. In this step we will breakdown the MCP server covered before and rework on it.

## 🎯 Learning Objectives

- Set up and configure Graphiti's MCP server
- Integrate with AI assistants (Cursor, etc.)  
- Design MCP tools for educational workflows
- Implement memory-powered AI tutoring systems
- Apply MCP patterns for TutorsGPT architecture

## 📚 Core Concepts

### What is the Model Context Protocol (MCP)?

**MCP** provides standardized interfaces for AI assistants to access external data sources and tools. Graphiti's MCP server exposes temporal knowledge graph capabilities to AI assistants.

**Educational Power:**
- **AI Tutors**: Access student learning history and progress
- **Content Recommendations**: Query educational knowledge graphs
- **Learning Analytics**: Retrieve insights about learning patterns
- **Personalization**: Adapt content based on student memory

### Graphiti MCP Tools

The Graphiti MCP server provides these core tools:

```python
# Available MCP tools:
- add_episode: Ingest new learning experiences
- search_facts: Query educational relationships  
- search_nodes: Find specific educational entities
- get_episodes: Retrieve learning history
- build_communities: Discover knowledge clusters
```

## 🚀 Worked Examples

### Setting Up Educational MCP Server

```bash
# Install Graphiti MCP server
pip install graphiti-core[mcp]

# Configure for educational use
export NEO4J_URI="your_neo4j_uri"
export OPENAI_API_KEY="your_openai_key"
export MCP_SERVER_NAME="tutorsgpt_memory"
```

### MCP Server Configuration

```json
// Claude Desktop configuration
{
  "mcpServers": {
    "tutorsgpt-memory": {
      "command": "python",
      "args": ["-m", "graphiti.mcp_server"],
      "env": {
        "NEO4J_URI": "your_neo4j_uri",
        "NEO4J_USER": "neo4j", 
        "NEO4J_PASSWORD": "your_password",
        "OPENAI_API_KEY": "your_openai_key"
      }
    }
  }
}
```

### AI Tutor Integration Example

```python
# Example AI assistant interaction with educational memory

# Assistant Query: "What programming concepts has Alice struggled with?"

# MCP Tool: search_facts
{
  "query": "Alice programming difficulties struggles challenges",
  "group_id": "cs101_fall2024",
  "limit": 10
}

# Response: Relationships showing Alice's learning challenges
# - Alice STRUGGLED_WITH Variables (2 weeks ago)
# - Alice NEEDED_HELP_WITH Loops (1 week ago)  
# - Alice MASTERED Functions (3 days ago)

# Assistant can now provide targeted help based on Alice's history
```

## 📚 Practice Problems

### Problem 1: Personalized Tutor Setup
**Task**: Configure MCP server for a personalized AI tutor that remembers each student's learning journey and adapts explanations accordingly.

### Problem 2: Curriculum Assistant  
**Challenge**: Create an AI assistant that helps instructors by querying course knowledge graphs to identify learning gaps and suggest content improvements.

### Problem 3: Learning Analytics Dashboard
**Scenario**: Build an AI-powered dashboard that uses MCP to query educational knowledge graphs and generate insights about class performance.

## 🔧 Advanced Techniques

### Custom Educational MCP Tools

```python
# Custom MCP tools for educational workflows
@mcp.tool()
async def get_student_progress(student_id: str, course_id: str):
    """Retrieve comprehensive student learning progress"""
    return await graphiti_client.search(
        query=f"student {student_id} progress mastery completion",
        group_id=course_id,
        limit=20
    )

@mcp.tool()  
async def recommend_learning_path(student_id: str, target_skill: str):
    """Generate personalized learning recommendations"""
    # Query student's current knowledge
    current_knowledge = await get_student_progress(student_id, course_id)
    
    # Find prerequisite chain for target skill
    prerequisites = await graphiti_client.search(
        query=f"prerequisites for {target_skill}",
        scope='edges',
        limit=15
    )
    
    # Generate personalized path
    return create_learning_path(current_knowledge, prerequisites)
```

### Memory-Powered Conversations

```python
# AI Assistant with Educational Memory
class EducationalAssistant:
    def __init__(self, mcp_client):
        self.memory = mcp_client
    
    async def tutor_student(self, student_id: str, question: str):
        """Provide tutoring with memory of student's history"""
        
        # Retrieve student's learning context
        context = await self.memory.search_facts(
            query=f"student {student_id} learning history progress",
            group_id=f"student_{student_id}",
            limit=15
        )
        
        # Adapt response based on student's past struggles and successes
        if self.has_struggled_with_concept(context, extract_concept(question)):
            return self.generate_gentle_explanation(question, context)
        else:
            return self.generate_standard_explanation(question, context)
```

## 🎯 Next Steps

Continue to **[10_configuration](../10_configuration/)** to optimize Graphiti for production educational systems.

**Master's Tip**: MCP integration transforms Graphiti from a knowledge storage system into an intelligent memory partner for AI assistants. This is where temporal knowledge graphs become truly powerful for educational AI! 🤖