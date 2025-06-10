# AI Protocols for Agentic Systems

This module outlines the various communication protocols foundational to building robust, scalable, and interoperable agentic AI systems, particularly within the Dapr Agentic Cloud Ascent (DACA) design pattern.

The protocols are organized in a layered approach, starting from fundamental communication mechanisms and moving towards more specialized AI-centric protocols.

## Directory Structure and Protocols

### `01_mcp_concepts/`: Foundational Communication Protocols

This directory contains the underlying communication technologies that serve as the transport layer for more complex interactions, organized in a suggested learning path. Understanding these is crucial for designing efficient and reliable data exchange in distributed agent systems. See the `01_base/readme.md` for the detailed learning progression.

- **[`01_Http/`] Defines standards and best practices for using Hypertext Transfer Protocol.
- **[`02_REST/`]**: Focuses on the architectural principles of REST for building scalable web services.
- **[`03_Streamable_HTTP/`]**: Covers protocols and techniques for streaming data over HTTP.
- **[`03_JSON_RPC/`]**: Outlines the use of JSON Remote Procedure Call for simple and efficient inter-service communication.

### `02_model_context_protocol/` (MCP)

This section details the Model Context Protocol (MCP). MCP is designed to standardize how Large Language Models (LLMs) and other AI models access and interact with external tools, services, and data sources. It provides a structured way to manage context, capabilities, and function calling, enabling more effective and reliable tool integration for agents.

### `03_a2a/` (Agent2Agent Protocol)

The Agent2Agent (A2A) Protocol defines a standardized framework for secure and interoperable communication directly between autonomous AI agents. This is fundamental for enabling complex collaboration, task delegation, and emergent behaviors in multi-agent systems, paving the way for the "Agentia World" vision. A2A often leverages one or more of the base protocols (e.g., HTTP/REST) for its transport.

### `04_llms_txt/`

This directory focuses on `llms.txt` (and `llms-full.txt`), a proposed standard for website owners to declare permissions and guidelines for how LLMs and other AI agents should interact with their content. It's akin to `robots.txt` but specifically for AI crawlers and agents, promoting responsible AI interactions with web content.

## Alignment with DACA Principles

This structured approach to protocols directly supports the core DACA principles:

- **Simplicity**: By clearly defining and separating protocol layers, the complexity of the overall system is managed, making it easier to understand and develop.
- **Scalability & Resilience**: Choosing the right base protocols (e.g., gRPC for internal high-throughput, HTTP/REST for interoperable A2A) and layering specialized protocols on top allows for optimized performance and robustness, which Dapr further enhances.
- **Open Core**: The use of well-established open standards and the definition of new open protocols like MCP and A2A foster interoperability and prevent vendor lock-in.

This organization provides a clear roadmap for developers to understand and implement the communication backbone of sophisticated agentic AI systems.
