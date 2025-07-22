# 03: Defining Tools with MCP

## Introduction
In this step, you'll learn how to create and use MCP tools with the FastMCP Python SDK. This guide will show you how to turn your Python functions into easy-to-use tools with minimal hassle.

## How Tools Work: Discovery and Execution
Here’s a simple overview of the process:
1. **Finding Tools:** The MCP client sends a `tools/list` request to get a list of available tools.
2. **Using Tools:** When you want to run a tool, the client sends a `tools/call` request with the tool name and the necessary parameters.
3. **Handling Errors:** If something goes wrong (for example, if a document is missing), the tool raises a Python error that is automatically converted into an MCP error response.

Below is a simple diagram illustrating the process:

```mermaid
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: Request to list available tools (tools/list)
    Server-->>Client: List of tools
    Client->>Server: Call a tool with parameters (tools/call)
    Server-->>Client: Tool result (formatted as text, image, audio, or resource link)
    Note over Client,Server: If tools change, server notifies client (tools/list_changed)
```

### 1. Defining Tools with `@mcp.tool`
Using the `@mcp.tool` decorator, you can convert a regular Python function into an MCP tool. The decorator uses Python’s type hints and Pydantic’s `Field` to automatically create a clear, friendly interface. This means you don’t have to write complex JSON schemas by hand.

*Learn More:* [MCP Tools Documentation](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)

### 2. Listing Tools

To discover available tools, clients send a tools/list request. This operation supports pagination.

**Request**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {
    "cursor": "optional-cursor-value"
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "title": "Weather Information Provider",
        "description": "Get current weather info",
        "inputSchema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "City name or zip code"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "nextCursor": "next-page-cursor"
  }
}
```

### 3. Calling Tools
To invoke a tool, clients send a tools/call request:

**Request:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "location": "New York"
    }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Current weather in New York:\nTemperature: 72°F\nConditions: Partly cloudy"
      }
    ],
    "isError": false
  }
}
```

> Run the code in hello_mcp for hands-on.

## Todo Exercise: Simple Document Tools

Open mcp_server.py file from base project and complete the first 2 TODOs.

Below are two simple tools that help you manage documents stored in an in-memory dictionary:

### Document Reader Tool
This tool lets you read a document’s content by its ID.

```python
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_document(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]
```

*What You Learn:*
- **Automatic Setup:** Your function’s parameters are used to automatically create a clear schema.
- **Friendly Errors:** If the document isn’t found, a clear error message is provided.

### Document Editor Tool
This tool allows you to update a document by replacing a specific text string with a new one.

```python
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the document's content with new text."
)
def edit_document(
    doc_id: str = Field(description="Id of the document to be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly."),
    new_str: str = Field(description="The new text to insert.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Successfully updated document {doc_id}"
```

*What You Learn:*
- **Handling Multiple Inputs:** The tool uses three parameters to show how to manage more than one input.
- **Real-World Use:** It demonstrates a practical find-and-replace operation.
- **Clear Error Messages:** Just like in the reader tool, you get helpful errors if something is wrong.

## Testing Your Tools

1. Start MCP Server:
```bash
uv run uvicorn mcp_server:mcp_app --reload
```

1. Now you can test your tools us using:
- **MCP Inspector:** Use this tool to interactively view and try out your tools.
- **Postman Collection:** Follow the provided Postman collection (`MCP_Defining_Tools.postman_collection.json`) to send requests and see the responses.

## Testing with MCP Inspector and Postman

Testing your MCP tools is simple. You can use two main methods:

### MCP Inspector

The MCP Inspector is a browser-based tool for quickly testing your MCP server without needing to integrate it into a full application. Follow these steps to use it:

1. **Activate Your Python Environment:** Ensure your project’s Python environment is active.

2. **Start the Inspector:** Instead of running the server with the Python command, start the MCP Inspector using the following command:
   
   ```bash
   npx @modelcontextprotocol/inspector
   ```

   This command uses a streamable HTTP transport to connect to your MCP server.

3. **Open in Browser:** Once the command runs, it will provide a local URL (for example, `http://127.0.0.1:6274`). Open this URL in your browser.

4. **Connect to Your Server:** In the inspector interface, click the **Connect** button. This will change the connection status from "Disconnected" to "Connected".

5. **List and Test Tools:** Navigate to the Tools section. Click "List Tools" to see all available tools, select a tool (e.g., `read_doc_contents`), enter the required parameters, and click "Run Tool". The inspector shows both the status and the returned data, making it easy to verify that your tool is working as expected.

### Postman

You can also test your MCP tools using Postman. Follow these steps:

1. **Import the Collection:** Import the provided Postman collection file (`MCP_Defining_Tools.postman_collection.json`) into Postman.

2. **Send Requests:** Choose the request corresponding to a tool you want to test. Fill in the necessary parameters in the request body.

3. **Review the Response:** Send the request and review the JSON response. This helps you confirm that your tool returns the expected result, including proper error handling.

These testing methods provide a practical and interactive way to debug and refine your MCP tools. For more details, refer to the [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools.md).


## Recap: What You Did
1. **Defined Tools:** Used the `@mcp.tool` decorator to convert normal Python functions into MCP tools.
2. **Registered Tools:** When the server starts, your tools are automatically listed and ready to use.
3. **Called Tools:** You learned how tools can be invoked with the right parameters using `tools/call`.
4. **Handled Errors:** You saw how simple Python errors can help diagnose issues when something goes wrong.

## More Resources
- [MCP Tools Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [MCP Tools Concepts](https://modelcontextprotocol.io/docs/concepts/tools)
- [FastMCP Python SDK on GitHub](https://github.com/modelcontextprotocol/python-sdk)

Thank you for taking this step! Remember, it's completely normal to feel challenged when learning something new. Take your time, review the examples, and experiment with tweaking the tools to really understand how they work.
