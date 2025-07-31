# Module 4: Core Capabilities & Transport Communication

A hands-on, curiosity-driven journey through advanced MCP features and StreamableHTTP patterns.

> **Master advanced MCP features and communication protocols for production-ready applications**  
> Based on [Anthropic's Advanced MCP Topics Course](https://anthropic.skilljar.com/model-context-protocol-advanced-topics)

> **First Read** [Advanced MCP Course Lessons](https://docs.google.com/document/d/1mvWO9NzzomRea_uJuKHEoiyswGVJTpkuQqjUBGalptE/)

> See [MCP 2025-06-18 Specification Schema](./mcp_schema_2025-06-18/schema.ts)

## 🎯 Module Overview

This module covers the advanced capabilities that make MCP powerful for production applications: **Sampling**, **Logging & Progress Notifications**, **Roots**, and **Transport Protocols**. You'll learn how to build MCP servers that can delegate reasoning to clients, provide real-time feedback, discover context, and communicate efficiently.

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

#### [05. STDIO and StreamableHTTP Transport](05_transport/README.md)
- **Duration**: 45-60 minutes
- **Focus**: HTTP-based transport for production deployments and Standard input/output transport for local development
- **Deliverable**: StreamableHTTP server with and without state management as well as STDIO-based MCP server and client
- **Key Concepts**:
  - STDIO transport implementation
  - Message framing and parsing
  - Process lifecycle management
  - Error handling and recovery
  - Development and debugging workflows
  - StreamableHTTP protocol specification
  - Stateful vs stateless connections
  - Connection management and persistence
  - Authentication and security
  - Production deployment considerations
  
## 🔧 Prerequisites

### Technical Requirements
- **Completed Module 4**: Understanding of MCP fundamentals
- **Python 3.8+** with async/await experience
- **HTTP and SSE knowledge**: Basic understanding of web protocols
- **JSON-RPC familiarity**: Understanding of RPC patterns (will be covered)


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

- MCP Specification
- OAuth Integration
- OpenAI Agents SDK Integration

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