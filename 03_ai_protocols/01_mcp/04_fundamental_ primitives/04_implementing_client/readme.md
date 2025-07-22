# 04: Implementing a Client


The MCP client abstracts away the complexity of server communication, letting you focus on your application logic while still getting access to powerful external tools and data sources.

![mcp-interaction.png](mcp-interaction.png)

Understanding this flow is crucial because you'll see all these pieces when building your own MCP clients and servers in the upcoming sections.

> This step is for students following the Antropic Introduction to MCP course. In class our focus is on learning core premitives

In this step, we build the client side of our CLI MCP application. 


## Understanding the MCP Client Lifecycle

A robust client-server application must manage its connection lifecycle carefully. The MCP Lifecycle, as described in the [MCP Lifecycle Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle), includes the following phases:

- **Initialization:** The client and server negotiate the protocol version and capabilities. The client sends an `initialize` request and then notifies with an `initialized` message once ready.

- **Operation:** Regular communication happens during this phase; the client sends requests (such as listing tools or calling a tool) and receives responses from the server.

- **Shutdown:** When the session is complete, the connection is closed gracefully. Resource management during this phase is critical to avoid hanging connections.

Incorporating these phases into your client's design helps ensure that your application is robust and can handle errors or unexpected interruptions gracefully.

## Our Client Architecture

The MCP client is made up of two main parts:

1. **MCP Client Class:** A custom class we create to simplify working with the server session. It makes using the MCP server easier by wrapping the session in methods that handle common tasks.

2. **Client Session:** This is the actual connection to the MCP server provided by the MCP Python SDK. The session manages sending and receiving messages, so you don’t have to worry about the low-level details.

Our custom client class ensures that resources are properly managed, cleaning up the connection when it’s no longer needed.

## Core Client Functions

There are two essential functions in the MCP client that you have to update:

### List Tools Function

This function retrieves a list of all available tools from the MCP server. It calls the built-in method provided by the session and returns the list of tools.

implementation:

```python
async def list_tools(self) -> list[types.Tool]:
    result = await self.session().list_tools()
    return result.tools
```

### Call Tool Function

This function is used to execute a specific tool on the server. You provide the tool name and the necessary input parameters, and it calls the tool on the server, returning the result.

Example implementation:

```python
async def call_tool(self, tool_name: str, tool_input: dict) -> types.CallToolResult | None:
    return await self.session().call_tool(tool_name, tool_input)
```

## Testing the Client

Once you've completed your client implementation start the mcp_server, it's time to test it:

1. **Test the Client Standalone:**
   - Run the client test harness with the following command:
     ```bash
     uv run mcp_client.py
     ```
   - This command connects to your MCP server and prints out the available tools, allowing you to verify that the client is retrieving the correct data.

2. **Test Through the Chat Application:**
   - Run the main application with:
     ```bash
     uv run main.py
     ```
   - Try asking a question such as "What is the contents of the report.pdf document?". Your application will use the client to call the appropriate tool and return the result.


## Conclusion

In this step, you've learned how to implement the MCP client and its core functions—`list_tools()` and `call_tool()`—which allow your application to interact with the MCP server efficiently. You also learned how to test the client using simple command-line commands and received an introduction to the important concept of the MCP lifecycle.

Take your time to review the code, experiment with it, and refer to the [MCP Lifecycle Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle) for further details. This is an essential step in building a robust, interactive application. Happy coding!

## Next Steps

1. **Reflect on the MCP Lifecycle:** As you work on your client, think about the MCP Lifecycle described in the [MCP Lifecycle Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle). Consider how the phases of Initialization, Operation, and Shutdown help manage connections and resources. This reflection will deepen your understanding of building robust, long-running applications.

2. **Discussion Points:**
   - How does handling the client lifecycle improve your application's resilience?
   - What challenges might you face in managing resources during shutdown?
   - How can you use the insights from the MCP Lifecycle to further improve your client design?

Keep experimenting and don't hesitate to review the concepts as many times as needed. Happy coding!
