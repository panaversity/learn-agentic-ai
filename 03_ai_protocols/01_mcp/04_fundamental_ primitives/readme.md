# Module 4: MCP Fundamental Primitives

> **Master the core building blocks of Model Context Protocol through hands-on coding**  
> Based on [Anthropic's Introduction to Model Context Protocol Course](https://anthropic.skilljar.com/introduction-to-model-context-protocol)

> **First Read** [Introduction MCP Course Lessons](https://docs.google.com/document/d/1W7Ex0rAK2kMtqTHHHEGwTFu2Wrf-zmQJosifppqF-vQ/)


MCP is not just about enhancing desktop applications with agentic functionality. It's about exposing reusable tools and resources to build agentic microservices. Watch:

- [Model Context Protocol (MCP) Explained for Beginners: AI Flight Booking Demo!](https://www.youtube.com/watch?v=E2DEHOEbzks)
- [Why MCP really is a big deal | Model Context Protocol with Tim Berglund](https://www.youtube.com/watch?v=FLpS7OfD5-s)

Model Context Protocol (MCP) is a communication layer for Agents context and tools so you don't have to write a bunch of tedious integration code for each project. Use it to shift the burden of tool definitions and execution away from your server to MCP servers.

- If Github have MCP server and my agent have to manage some GitHub Actions why write them again?
- Like companies providing APIs now they will likely create MCP implementation.
- It's Transport agnostic with some caveats- the client and server can communicate over different protocols.

## Overview

This module introduces the three fundamental primitives of MCP: **Tools**, **Resources**, and **Prompts**. You'll learn to build MCP servers and clients using the Python SDK, focusing on practical, code-driven examples that demonstrate real-world applications.

## 📚 Learning Objectives

By the end of this module, you will be able to:

### Core Competencies
- ✅ **Build MCP servers** using the Python SDK with decorator-based tool definitions
- ✅ **Implement all three MCP primitives**: Tools (model-controlled), Resources (app-controlled), Prompts (user-controlled)
- ✅ **Create MCP clients** that connect to and interact with servers
- ✅ **Use the MCP Server Inspector** for testing and debugging server functionality

### Technical Skills
- ✅ **Define tools with decorators** instead of writing JSON schemas manually
- ✅ **Implement file management functionality** with tools for reading, writing, and managing files
- ✅ **Create resources** for exposing read-only data with proper MIME type handling
- ✅ **Build prompts** that provide pre-crafted instructions for common workflows
- ✅ **Handle errors gracefully** with proper exception handling and user feedback

### Understanding
- ✅ **Distinguish between MCP primitives**: Know when to use tools vs. resources vs. prompts
- ✅ **Understand control models**: Model-controlled (tools), app-controlled (resources), user-controlled (prompts)
- ✅ **Apply best practices** for security, performance, and maintainability

## Prerequisites

- Working knowledge of Python programming
- Basic understanding of JSON and HTTP request-response patterns
- Familiarity with decorators and type hints in Python

## Learning Structure

### 1. Project Setup and First Server
**Goal**: Establish development environment and create your first working MCP server

- [01_hello_mcp_server](./01_hello_mcp_server/read.md) - Setting up your development environment with `uv` using base_project
- [02_project_setup](./02_project_setup/readme.md) - Set your Base Project for this learning module

### 2. Building Tools and Resources
**Goal**: Master the three fundamental MCP primitives through practical examples

- [03_defining_tools](./03_defining_tools/readme.md) - Creating tools with decorators and type hints
- [04_implementing_client](./04_implementing_client/readme.md) - For mcp tools create a simple client.
- [05_defining_resources.md](05_defining_resources/readme.md) - Creating read-only data resources
- [06. Working with Prompts](06_working_with_prompts/readme.md) - Building pre-crafted prompts for common workflows

## MCP Core Primitives

### 1. Tools (Model-Controlled)
Tools are functions that AI models can call to perform actions. They are:
- **Model-controlled**: The AI decides when and how to use them
- **Action-oriented**: Perform specific tasks like reading files, making API calls
- **Decorator-based**: Defined using Python decorators with type hints

### 2. Resources (App-Controlled)
Resources provide read-only access to data. They are:
- **App-controlled**: The application decides when to expose them
- **Data-focused**: Provide access to documents, databases, APIs
- **URI-based**: Accessed through specific URIs with optional parameters

### 3. Prompts (User-Controlled)
Prompts are pre-crafted instructions for common workflows. They are:
- **User-controlled**: Users decide when to apply them
- **Instruction-focused**: Provide high-quality, reusable prompts
- **Context-aware**: Can include dynamic content and formatting

## Quick Start

1. **Setup Environment**: Follow the [project setup guide](01_project_setup.md)
2. **Create First Server**: Build a simple MCP server with tools
3. **Test with Inspector**: Use the built-in server inspector for debugging
4. **Add Resources**: Implement read-only data access
5. **Build Client**: Create an MCP client to connect with your server
6. **Create Prompts**: Build reusable prompt templates

### Knowledge Check
- [ ] Can explain the difference between tools, resources, and prompts
- [ ] Understand when to use each MCP primitive
- [ ] Can implement proper error handling in MCP servers
- [ ] Know how to use the MCP Server Inspector effectively
- [ ] Can create both static and templated resources
- [ ] Understand MIME type handling for different content types

## 🛠️ Development Tools

### Essential Tools
- **`uv`**: Fast Python package manager for dependency management
- **MCP Python SDK**: Core library for building MCP servers and clients
- **MCP Server Inspector**: Web-based tool for testing and debugging servers
- **Postman**: Test APIs

### Recommended Tools
- **Cursor or VS Code**: IDE with Python and MCP extensions
- **Git**: Version control for your MCP projects

## 🔗 Resources and References

### Official Documentation
- [MCP Specification (2025-06-18)](https://modelcontextprotocol.io/specification/2025-06-18)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)

### Learning Resources
- [Anthropic's MCP Course](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [MCP Server Inspector](https://github.com/modelcontextprotocol/server-inspector)
- [JSON Schema Documentation](https://json-schema.org/learn/getting-started-step-by-step)

### Community and Support
- [MCP GitHub Discussions](https://github.com/modelcontextprotocol/python-sdk/discussions)
- [MCP Discord Community](https://discord.gg/modelcontextprotocol)

## 🚀 Next Steps

After completing this module, you'll be ready to explore:

### Module 2: Core Capabilities & Transport Communication
- Sampling and AI delegation
- Logging and progress notifications
- Roots and context discovery
- JSON-RPC message types and transport protocols

### Advanced Modules (Future)
- **Server Engineering**: Advanced server patterns and optimization
- **Client Features**: Advanced client capabilities and integrations
- **OAuth Integration**: Security and authentication patterns
- **OpenAI Agents SDK**: Integration with OpenAI's agent framework

## 💡 Tips for Success

1. **Code Along**: Don't just read—implement every example
2. **Experiment**: Modify examples to explore different scenarios
3. **Use the Inspector**: Test your servers thoroughly with the MCP Server Inspector
4. **Build Incrementally**: Start simple and add complexity gradually
5. **Document Your Learning**: Keep notes on patterns and best practices you discover
