# Module 03: [OpenAI Agents SDK with Model Context Protocol (MCP)](https://openai.github.io/openai-agents-python/mcp/)

**Overall Objective:** To understand and demonstrate how to integrate MCP servers (specifically those using the `streamable-http` transport) with agents created using the OpenAI Agents SDK. This will involve connecting agents to MCP servers, enabling tool discovery and invocation, managing tool list caching, and observing MCP interactions through tracing.

## Introduction

The OpenAI Agents SDK provides robust support for the Model Context Protocol (MCP). This integration allows agents to seamlessly connect to and utilize tools and resources exposed by any MCP-compliant server. By leveraging MCP, developers can create a standardized way for agents to access a wide array of external capabilities, enhancing their functionality and modularity.

This module will focus on using the `MCPServerStreamableHttp` client class provided by the SDK, which allows agents to communicate with MCP servers that use the `streamable-http` transport. This transport is suitable for scenarios requiring bidirectional streaming and efficient, long-lived connections.

We will explore:

- How to configure an agent to connect to one or more MCP servers.
- How tools from these servers are discovered and made available to the agent's underlying Language Model (LLM).
- The process of tool invocation and result handling when an MCP tool is selected by the LLM.
- Performance optimization techniques like caching the list of tools from an MCP server.
- The SDK's built-in tracing capabilities for monitoring MCP interactions.

## Sub-modules

This module is broken down into the following sub-modules, each focusing on a specific aspect of using MCP with the OpenAI Agents SDK:

1.  **`01_intro_agent_and_mcp_streamable_http`**: Covers the basics of establishing a connection from an agent to a `streamable-http` MCP server using `MCPServerStreamableHttp`.
2.  **`02_caching_mcp_tool_lists`**: Explains and shows how to use the tool list caching feature for performance optimization.
3.  **`03_tracing_mcp_interactions_in_sdk`**: Highlights how to observe MCP operations (like `list_tools` and `call_tool`) using the SDK's tracing features.
4.  **`04_agent_with_multiple_mcp_servers`**: Illustrates configuring a single agent to connect to and utilize tools from multiple MCP servers.

By the end of this module, you will have a practical understanding of how to extend your OpenAI Agents with powerful tools and resources made available through the Model Context Protocol.
