# 03: Exposing Resources with Enhanced Metadata (2025-06-18)

**Objective:** Learn how to expose data as **MCP Resources** with features: **title fields**, **rich metadata**, **multiple URI schemes**, and **structured content responses** using the 2025-06-18 specification.

**Building on Previous Lessons**: You've learned about Tools (Lesson 02) - functions AI can call. Now let's explore Resources - **data that AI can read** to enhance its knowledge and context.

### 🤔 What Are MCP Resources? (Simple Explanation)

**Simple Definition**: MCP Resources are **documents, data, and information that AI can access** to provide better, more informed responses.

**Real-World Analogy**: If Tools are like giving AI a toolbox, Resources are like giving AI a **library or knowledge base**. The AI can:
- 📖 Read documentation and guides
- 📊 Access real-time data and reports  
- 🗂️ Browse file systems and databases
- 🔍 Search through knowledge collections

### 🏗️ MCP Resources vs. What You Know

| **If you're familiar with...** | **MCP Resources are like...** | **Key advantage** |
|-------------------------------|--------------------------------|-------------------|
| **File Systems** | Files the AI can browse and read | Discoverable and structured for AI |
| **REST API GET endpoints** | Read-only API endpoints | Built-in metadata and categorization |
| **RAG (Retrieval Augmented Generation)** | Knowledge base for AI context | Standardized across all AI platforms |
| **Documentation Sites** | Docs the AI can navigate | Self-describing with rich metadata |
| **Database Views** | Queryable data collections | AI-friendly formatting and discovery |

### 🎯 Why Resources Matter for AI

**The Problem**: AI models have training cutoffs and can't access:
- Your company's latest documents
- Real-time data and reports
- User-specific information
- Dynamic content that changes frequently

**The MCP Resources Solution**:
- ✅ **Rich Context**: AI gets access to relevant, up-to-date information
- ✅ **Organized Data**: Resources are categorized and searchable
- ✅ **Dynamic Content**: Information that updates automatically
- ✅ **Metadata Rich**: Resources include descriptions, types, and relationships

### 🔗 How Resources Work With Tools

**Powerful Combination**: Resources and Tools work together:
- 📚 **Resources provide context**: AI reads documentation about how to use an API
- 🔧 **Tools take action**: AI calls the API using knowledge from resources
- 📊 **Resources show results**: AI reads updated data after tool execution

This lesson builds on our foundation by creating a server that demonstrates resource capabilities including virtual file systems, dynamic templates, analytics dashboards, and cross-scheme resource discovery.

## Key MCP Concepts (2025-06-18)

### 🎯 **Core Resource Features**
-   **Resources:** Data items with unique URIs (e.g., `file:///project/README.md`, `users://123/profile`)
-   **Resource Providers (`@mcp.resource_provider`)**: Functions that list available resources for specific URI schemes
-   **Resource Getters (`@mcp.resource_getter`)**: Functions that fetch content for specific resource URIs
-   **URI Schemes**: Categorization system (`file://`, `app://`, `users://`, `db://`, custom schemes)

### 📊 **Enhanced Metadata System (NEW in 2025-06-18)**
-   **Title Fields**: Human-friendly titles alongside programmatic names
-   **Rich Descriptions**: Detailed resource descriptions with context and usage
-   **MIME Type Detection**: Accurate content type identification for proper handling
-   **Resource Metadata**: Size, modification dates, authors, tags, and custom properties
-   **Cross-References**: Links between related resources and dependencies

### 🔧 **Advanced Resource Patterns**
-   **Static Resources**: Fixed content like documentation and configuration
-   **Dynamic Resources**: Generated content based on parameters and state
-   **Template Resources**: URI templates with parameters (e.g., `users://{user_id}/profile`)
-   **Multiple Schemes**: Different URI schemes for different data types
-   **Structured Content**: Rich formatting with markdown, JSON, and custom formats


## 🔧 Resource Implementation Guide

### **Resource Definition Patterns**

**Basic Resource (Static Content):**
```python
@mcp.resource(
    uri="app:///messages/welcome",
    name="Welcome Message",
    title="Server Welcome Message",  # NEW in 2025-06-18
    description="Comprehensive welcome message with server information",
    mime_type="text/markdown"
)
async def get_welcome_message() -> str:
    return "# Welcome to MCP Resources!"
```

**Dynamic Resource (Generated Content):**
```python
@mcp.resource(
    uri="app:///system/info",
    name="System Information", 
    title="Live Server System Information",  # NEW in 2025-06-18
    description="Real-time system metrics and performance data",
    mime_type="application/json"
)
async def get_system_info() -> str:
    system_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "server_name": "my-resources-server",
        "uptime": 3600,
        "requests_served": 1247
    }
    return json.dumps(system_data, indent=2)
```

**Template Resource (Parameterized):**
```python
@mcp.resource(
    uri="users://{user_id}/profile",
    name="User Profile",
    title="Dynamic User Profile Information",  # NEW in 2025-06-18
    description="User profile with activity data and preferences",
    mime_type="text/markdown"
)
def get_user_profile(user_id: str) -> str:
    return f"""# User Profile: {user_id}
    
**User ID:** {user_id}
**Status:** Active
**Generated:** {datetime.datetime.now().isoformat()}
"""
```

## Implementation Plan

Inside the `my_resources_server/` subdirectory:

### **Server (`server.py`)**
-   **Virtual File System**: Rich metadata structure with file types, sizes, authors, tags
-   **Multiple URI Schemes**: `file://`, `app://`, `users://` with scheme-specific providers
-   **Dynamic Content**: Real-time system information, analytics dashboards, user profiles
-   **Template Resources**: Parameterized URIs for dynamic content generation
-   **Metadata**: Title fields, detailed descriptions, content classification

### **Client (`client.py`)**
-   **Multi-Scheme Discovery**: Lists resources across all supported URI schemes
-   **Content Parsing**: Handles different MIME types and structured responses
-   **Template Testing**: Tests parameterized resources with various inputs
-   **Metadata Display**: Shows enhanced resource information and titles

### **Postman Collection**
-   **Scheme-Specific Testing**: Tests for each URI scheme independently
-   **Template Validation**: Tests parameterized resources with different values
-   **Metadata Verification**: Validates title fields and enhanced descriptions
-   **Error Handling**: Tests edge cases and invalid resource requests

## Project Structure

## 1. Server Code (`server.py`)

Server demonstrates comprehensive resource capabilities:
1. Call `resources/list` to discover available resources
2. Use `resources/read` to fetch specific content
3. Explore template resources with dynamic parameters

## How to Run: Complete Testing Guide

### **Terminal 1: Start the Enhanced Server**

1. **Navigate to the directory:**
   ```bash
   cd my_resources_server
   ```

2. **Install libraries:**
   ```bash
   uv add mcp uvicorn httpx
   ```

3. **Run the server:**
   ```bash
   uvicorn server:mcp_app --host 0.0.0.0 --port 8000 --reload
   ```

### **Terminal 2: Test with Enhanced Client**

1. **Run the comprehensive client:**
   ```bash
   uv run python client.py
   ```

### **Postman Testing (Recommended)**

1. **Import the enhanced collection:** `postman/MCP_Exposing_Resources.postman_collection.json`
2. **Run requests in sequence:**
   - `01. Initialize Session` - Protocol negotiation
   - `02. Send Initialized Notification` - Complete initialization
   - `03-05. List Resources by Scheme` - Test each URI scheme
   - `06-10. Get Specific Resources` - Fetch various content types
   - `11-13. Test Template Resources` - Dynamic content generation
   - `14. Test Error Handling` - Invalid resource requests

## 4. Key Learning Outcomes

After completing this lesson, you will understand:

### **✅ Enhanced Resource Implementation**
- Creating resources with title fields and rich metadata
- Implementing multiple URI schemes for different data types
- Building template resources with dynamic parameters
- Structuring virtual file systems with comprehensive metadata

### **✅ Advanced Resource Patterns**
- Static vs dynamic vs template resource patterns
- Cross-scheme resource discovery and navigation
- Content generation with real-time data
- Analytics and monitoring resource integration

### **✅ 2025-06-18 Specification Features**
- Title fields for human-friendly resource identification
- Enhanced descriptions with context and usage information
- Proper MIME type handling for different content formats
- Structured metadata for resource classification and search

### **✅ Production Considerations**
- Resource organization and categorization strategies
- Performance optimization for large resource collections
- Caching and content generation best practices
- Error handling and graceful degradation patterns

## 6. Next Steps and Advanced Patterns

- **Lesson 04**: Create prompt templates that reference these resources

This lesson provides the foundation for building rich, discoverable resource collections that enhance the context and capabilities available to MCP clients and AI agents.