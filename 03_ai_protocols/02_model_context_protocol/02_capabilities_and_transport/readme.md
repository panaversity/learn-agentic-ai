# Module 2: Core Capabilities & Transport Communication

> **Master advanced MCP features and communication protocols for production-ready applications**  
> Based on [Anthropic's Advanced MCP Topics Course](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)

## 🎯 Module Overview

This module covers the advanced capabilities that make MCP powerful for production applications: **Sampling**, **Logging & Progress Notifications**, **Roots**, and **Transport Protocols**. You'll learn how to build sophisticated MCP servers that can delegate reasoning to clients, provide real-time feedback, discover context, and communicate efficiently.

### Pedagogical Approach

This module follows a **capability-driven approach**:
- **Feature-First**: Each lesson focuses on a specific MCP capability
- **Production-Ready**: Examples demonstrate real-world usage patterns
- **Protocol Deep-Dive**: Understand the underlying communication mechanisms
- **Integration Patterns**: Learn how capabilities work together

## 📚 Learning Objectives

By the end of this module, you will be able to:

### Core Capabilities
- ✅ **Implement Sampling**: Build servers that delegate AI reasoning to clients
- ✅ **Use Logging & Progress**: Provide real-time feedback during long-running operations
- ✅ **Implement Roots**: Discover and access user context and project information
- ✅ **Master Transport Protocols**: Understand JSON-RPC, STDIO, and StreamableHTTP

### Advanced Skills
- ✅ **Design Stateful vs Stateless**: Choose appropriate server architectures
- ✅ **Handle Bidirectional Communication**: Implement server-to-client requests
- ✅ **Manage Context Discovery**: Build servers that understand user environment
- ✅ **Optimize Performance**: Use appropriate transport protocols for different use cases

### Production Readiness
- ✅ **Error Handling**: Implement robust error handling for all capabilities
- ✅ **Security**: Apply security best practices for MCP communications
- ✅ **Monitoring**: Use logging and progress notifications for observability
- ✅ **Scalability**: Design servers that can handle production workloads

## 🏗️ Course Structure

### Phase 1: Core Capabilities (Lessons 01-03)
**Goal**: Master the three core MCP capabilities that enable sophisticated AI interactions

#### [01. Sampling - Giving Tools a Brain](01_sampling/README.md)
- **Duration**: 75-90 minutes
- **Focus**: AI delegation and reasoning capabilities
- **Deliverable**: Sampling-enabled MCP server with AI-powered tools
- **Key Concepts**:
  - Understanding when servers need to delegate reasoning to clients
  - Implementing `sampling/create` requests and responses
  - Stateful vs stateless HTTP connections
  - Capability negotiation and model preferences
  - Error handling for sampling failures

#### [02. Logging & Progress Notifications](02_logging_progress/README.md)
- **Duration**: 60-75 minutes
- **Focus**: Real-time feedback and observability
- **Deliverable**: Server with comprehensive logging and progress tracking
- **Key Concepts**:
  - Log notification types and levels
  - Progress tracking for long-running operations
  - Structured logging with metadata
  - Client-side notification handling
  - Performance monitoring and debugging

#### [03. Roots - Context Discovery](03_roots/README.md)
- **Duration**: 60-75 minutes
- **Focus**: Discovering user context and project information
- **Deliverable**: Server that can discover and access user environment
- **Key Concepts**:
  - Root discovery and enumeration
  - File system context and project structure
  - Environment variables and configuration
  - Workspace and editor integration
  - Context-aware tool behavior

### Phase 2: Transport & Communication (Lessons 04-06)
**Goal**: Master MCP transport protocols and communication patterns

#### [04. JSON-RPC Message Types](04_jsonrpc_messages/README.md)
- **Duration**: 45-60 minutes
- **Focus**: Understanding MCP's JSON-RPC 2.0 foundation
- **Deliverable**: Deep understanding of MCP message structure
- **Key Concepts**:
  - JSON-RPC 2.0 specification and MCP extensions
  - Request/response message formats
  - Error handling and status codes
  - Message validation and parsing
  - Protocol compliance and debugging

#### [05. STDIO Transport](05_stdio_transport/README.md)
- **Duration**: 45-60 minutes
- **Focus**: Standard input/output transport for local development
- **Deliverable**: STDIO-based MCP server and client
- **Key Concepts**:
  - STDIO transport implementation
  - Message framing and parsing
  - Process lifecycle management
  - Error handling and recovery
  - Development and debugging workflows

#### [06. StreamableHTTP Transport](06_streamable_http/README.md)
- **Duration**: 60-75 minutes
- **Focus**: HTTP-based transport for production deployments
- **Deliverable**: StreamableHTTP server with state management
- **Key Concepts**:
  - StreamableHTTP protocol specification
  - Stateful vs stateless connections
  - Connection management and persistence
  - Authentication and security
  - Production deployment considerations

## 🔧 Prerequisites

### Technical Requirements
- **Completed Module 1**: Understanding of MCP fundamentals
- **Python 3.8+** with async/await experience
- **HTTP and WebSocket knowledge**: Basic understanding of web protocols
- **JSON-RPC familiarity**: Understanding of RPC patterns (will be covered)

## 🧠 Core Capabilities Deep Dive

### 1. Sampling - AI Delegation
**Definition**: Allows servers to request LLM sampling from clients

**Key Concepts**:
- **Server-to-Client Requests**: Servers can ask clients to perform AI reasoning
- **Stateful Connections**: Required for bidirectional communication
- **Model Preferences**: Servers can specify preferred models and parameters
- **Error Handling**: Graceful handling of sampling failures

**Use Cases**:
- Content generation (stories, code, documentation)
- Data analysis and interpretation
- Creative tasks (design, writing, brainstorming)
- Complex reasoning and problem-solving

### 2. Logging & Progress Notifications
**Definition**: Real-time feedback and observability for MCP operations

**Key Concepts**:
- **Log Levels**: Debug, info, warning, error notifications
- **Progress Tracking**: Percentage-based progress for long operations
- **Structured Data**: Rich metadata for debugging and monitoring
- **Client Handling**: How clients process and display notifications

**Use Cases**:
- Long-running data processing
- File operations and transfers
- API integrations with external services
- System monitoring and health checks

### 3. Roots - Context Discovery
**Definition**: Discovering and accessing user context and environment

**Key Concepts**:
- **Root Enumeration**: Discovering available context sources
- **File System Access**: Reading workspace and project files
- **Environment Integration**: Accessing configuration and settings
- **Context-Aware Tools**: Tools that adapt based on discovered context

**Use Cases**:
- Code analysis and understanding
- Project-specific tool behavior
- Configuration management
- Workspace-aware applications

## 🌐 Transport Protocols Deep Dive

### 1. JSON-RPC 2.0 Foundation
**Definition**: The underlying RPC protocol that MCP extends

**Key Concepts**:
- **Request/Response Pattern**: Standard RPC message flow
- **Error Handling**: Structured error responses
- **Message Format**: JSON-based message structure
- **Protocol Extensions**: MCP-specific message types

### 2. STDIO Transport
**Definition**: Standard input/output transport for local development

**Key Concepts**:
- **Process Communication**: Parent-child process communication
- **Message Framing**: Delimiting messages in byte streams
- **Lifecycle Management**: Starting and stopping MCP processes
- **Development Workflow**: Local development and debugging

### 3. StreamableHTTP Transport
**Definition**: HTTP-based transport for production deployments

**Key Concepts**:
- **HTTP/HTTPS Support**: Web-standard transport protocol
- **Stateful Connections**: Persistent connections for bidirectional communication
- **Authentication**: OAuth 2.1 and other security mechanisms
- **Production Deployment**: Scalable, load-balanced deployments

## 📖 Assessment and Progress Tracking

### Module Completion Checklist
- [ ] **Sampling Implementation**: Built server that delegates AI reasoning to clients
- [ ] **Progress Notifications**: Implemented comprehensive logging and progress tracking
- [ ] **Roots Discovery**: Created server that discovers and accesses user context
- [ ] **JSON-RPC Understanding**: Deep understanding of MCP message structure
- [ ] **STDIO Transport**: Built and tested STDIO-based server
- [ ] **StreamableHTTP Transport**: Implemented HTTP-based server with state management
- [ ] **Error Handling**: Robust error handling for all capabilities
- [ ] **Security**: Applied security best practices for transport protocols

### Knowledge Check
- [ ] Can explain when to use sampling vs. direct tool implementation
- [ ] Understand the difference between stateful and stateless connections
- [ ] Can implement proper progress notifications for long-running operations
- [ ] Know how to discover and access user context through roots
- [ ] Can choose appropriate transport protocols for different use cases
- [ ] Understand JSON-RPC message structure and MCP extensions
- [ ] Can implement secure authentication for HTTP transport
- [ ] Know how to handle errors and failures in all capabilities

## 🔗 Resources and References

### Official Documentation
- [MCP Specification - Sampling](https://modelcontextprotocol.io/specification/2025-06-18/client/sampling)
- [MCP Specification - Logging](https://modelcontextprotocol.io/specification/2025-06-18/client/logging)
- [MCP Specification - Roots](https://modelcontextprotocol.io/specification/2025-06-18/client/roots)
- [MCP Specification - Transport](https://modelcontextprotocol.io/specification/2025-06-18/transport)

### Learning Resources
- [Anthropic's Advanced MCP Course](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [HTTP/2 Specification](https://tools.ietf.org/html/rfc7540)
- [OAuth 2.1 Security](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1)

### Community and Support
- [MCP GitHub Discussions](https://github.com/modelcontextprotocol/python-sdk/discussions)
- [MCP Discord Community](https://discord.gg/modelcontextprotocol)
- [Transport Protocol Discussions](https://github.com/modelcontextprotocol/specification/discussions)

## 🚀 Next Steps

After completing this module, you'll be ready to explore:

### Module 3: Advanced Engineering
- Lifecycle management and server optimization
- Pagination and large data handling
- Cancellation and timeout management
- Advanced error handling and recovery

### Module 4: Advanced Client Features
- Advanced client capabilities and integrations
- Multi-server coordination and load balancing
- Client-side caching and optimization
- Advanced debugging and monitoring

### Module 5: OAuth Integration
- Security and authentication patterns
- OAuth 2.1 implementation and best practices
- Protected resource metadata discovery
- Authorization server integration

### Module 6: OpenAI Agents SDK Integration
- Integration with OpenAI's agent framework
- MCP server integration with OpenAI Agents
- Advanced agent capabilities and patterns
- Production deployment and scaling

## 💡 Tips for Success

1. **Start with Sampling**: It's the most transformative capability—master it first
2. **Test Transport Protocols**: Experiment with different transports to understand trade-offs
3. **Monitor Performance**: Use logging and progress notifications to understand your server's behavior
4. **Security First**: Always consider security implications when implementing transport protocols
5. **Production Thinking**: Design for scalability and reliability from the beginning

## 🔧 Common Challenges and Solutions

### Sampling Challenges
- **Challenge**: Understanding when to use sampling vs. direct implementation
- **Solution**: Use sampling for creative tasks, direct implementation for deterministic operations

### Transport Challenges
- **Challenge**: Choosing between STDIO and HTTP transport
- **Solution**: Use STDIO for development, HTTP for production deployments

### State Management Challenges
- **Challenge**: Managing state in stateless vs. stateful connections
- **Solution**: Use stateful connections when you need bidirectional communication

---

**Ready to begin?** Start with [Lesson 01: Sampling - Giving Tools a Brain](01_sampling/README.md) to learn how to build AI-powered MCP servers! 