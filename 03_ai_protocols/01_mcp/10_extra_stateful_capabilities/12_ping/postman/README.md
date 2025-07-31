# 📮 Postman Testing Guide for MCP Ping Utility

This directory contains a Postman collection for testing the MCP Ping Utility according to the [MCP 2025-06-18 Ping Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/ping).

## 🎯 What You'll Test

- **🏓 Basic Ping Request/Response**: The standard ping/pong flow.
- **⏰ Response Time Validation**: Ensuring the server responds promptly.
- **🔧 Specification Compliance**: Validating the exact request and response formats.
- **⚡ Performance Testing**: Sending rapid pings to check server health under load.

## 📋 Prerequisites

1.  **Start the MCP Server**:
    ```bash
    # Navigate to the code directory
    cd mcp-decoded/02_server_engineering/09_ping/mcp_code
    
    # Start the server
    uv run server.py
    ```
    The server will run on `http://localhost:8000`.

2.  **Import the Collection**:
    -   Import `MCP_Ping_Tests.postman_collection.json` into Postman.
    -   The collection comes with a pre-configured `mcp_session_id` variable.

## 🔄 How to Test: The Full Lifecycle

Follow these requests in order within the Postman collection.

### 1. Initialize MCP Server
This request starts a new MCP session and automatically saves the `mcp-session-id` for subsequent requests.

-   **Request**: `POST http://localhost:8000/mcp/`
-   **Body**:
    ```json
    {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "clientInfo": {
                "name": "postman-ping-client",
                "version": "1.0.0"
            },
            "capabilities": {}
        },
        "id": 1
    }
    ```
-   **Expected Result**: The test script will confirm a `200 OK` status and extract the session ID.

### 2. Send Initialized Notification
This tells the server we are ready to proceed.

-   **Request**: `POST http://localhost:8000/mcp/`
-   **Headers**: Includes the `mcp-session-id` captured from the previous step.
-   **Expected Result**: A `202 Accepted` status code.

### 3. Basic Ping Test
This sends a standard `ping` and validates the response.

-   **Request**: `POST http://localhost:8000/mcp/`
-   **Body**:
    ```json
    {
        "jsonrpc": "2.0",
        "id": "ping_test_1",
        "method": "ping"
    }
    ```
-   **Expected Result**: A `200 OK` response with an empty `result` object: `{"jsonrpc": "2.0", "id": "ping_test_1", "result": {}}`. The test script validates this structure.

## 📚 Specification Deep Dive

According to the [MCP Ping Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/ping):

-   **Request Format**: A `ping` request **MUST NOT** include a `params` object.
-   **Response Format**: The response **MUST** contain an empty `result` object (`{}`).
-   **Behavior**: The receiver **MUST** respond promptly. Our Postman tests check for this by asserting a reasonable response time.

This simple handshake is the foundation of a stable and reliable MCP connection.

## 🧪 Test Scenarios

### ✅ **Success Cases**
1. **Basic Ping** - Standard specification example
2. **Rapid Pings** - Multiple concurrent ping requests  
3. **Response Time** - Validates prompt response requirement
4. **Format Compliance** - Exact specification format validation

### ❌ **Error Cases**  
1. **Invalid Parameters** - Ping with params object (should be rejected)
2. **Missing Session** - Ping without MCP session
3. **Malformed JSON** - Invalid JSON-RPC format

## 📊 Expected Results

| Test Case | Expected Status | Response Time | Notes |
|-----------|----------------|---------------|-------|
| Basic Ping | 200 OK | < 1000ms | Specification compliance |
| Rapid Pings | 200 OK | < 500ms | Performance validation |
| Invalid Params | 200/400 | Any | Server handles gracefully |
| No Session | 200/400/401 | Any | Server policy dependent |

## 📚 References

- [MCP Ping Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/utilities/ping)
- [MCP Basic Protocol](https://modelcontextprotocol.io/specification/2025-03-26/basic/overview)  
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

---

**🎯 Key Learning:** MCP ping is the foundation of connection health monitoring. Understanding this simple utility prepares you for more complex MCP utilities like logging and progress tracking! 🏓 