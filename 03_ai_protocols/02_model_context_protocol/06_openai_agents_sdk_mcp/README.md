# 06: Integrating with OpenAI's Agents SDK

**Objective:** To understand and demonstrate how to integrate MCP servers (specifically those using the `streamable-http` transport) with agents created using the OpenAI Agents SDK. This will involve connecting agents to MCP servers, enabling tool discovery and invocation, managing tool list caching, and observing MCP interactions through tracing.


This final section bridges the gap between the open, interoperable world of MCP and a popular, production-grade agent framework. It shows how MCP is not a competing standard, but a powerful **complement** that makes agentic frameworks more modular, testable, and extensible.

## Why This Architecture is Powerful (DACA-Aligned)

-   **Decoupling:** The agent's core logic (the OpenAI Assistant) is completely decoupled from the tool's implementation (the MCP Server).
-   **Interoperability:** The same MCP server that we built and tested throughout this course can be used by an OpenAI agent, a LangChain agent, or any other framework, without changing a single line of server code.
-   **Scalability & Maintainability:** You can develop, test, and scale your tools (the MCP server) independently from your agent. Different teams can own different tool servers.
-   **Open Core:** This aligns with the DACA principle of using open standards (MCP) to connect to managed services or closed frameworks (OpenAI API) at the edges.

## Sub-modules
We will explore:

- How to configure an agent to connect to one or more MCP servers.
- How tools from these servers are discovered and made available to the agent's underlying Language Model (LLM).
- The process of tool invocation and result handling when an MCP tool is selected by the LLM.
- Performance optimization techniques like caching the list of tools from an MCP server.
- The SDK's built-in tracing capabilities for monitoring MCP interactions.

This module is broken down into the following sub-modules, each focusing on a specific aspect of using MCP with the OpenAI Agents SDK:

1.  **`01_intro_agent_and_mcp_streamable_http`**: Covers the basics of establishing a connection from an agent to a `streamable-http` MCP server using `MCPServerStreamableHttp`.
2.  **`02_caching_mcp_tool_lists`**: Explains and shows how to use the tool list caching feature for performance optimization.
3.  **`03_tracing_mcp_interactions_in_sdk`**: Highlights how to observe MCP operations (like `list_tools` and `call_tool`) using the SDK's tracing features.
4.  **`04_agent_with_multiple_mcp_servers`**: Illustrates configuring a single agent to connect to and utilize tools from multiple MCP servers.

By the end of this module, you will have a practical understanding of how to extend your OpenAI Agents with powerful tools and resources made available through the Model Context Protocol.
