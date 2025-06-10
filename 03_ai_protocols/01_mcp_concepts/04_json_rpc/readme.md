# JSON-RPC: A Lightweight Remote Procedure Call Protocol

> **JSON-RPC is a stateless, light-weight remote procedure call (RPC) protocol. It is transport agnostic and uses JSON as its data format. It is designed to be simple!**  
> — [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

JSON-RPC is a stateless, light-weight remote procedure call (RPC) protocol. It allows for notifications (data sent to the server that does not require a response) and for multiple calls to be sent to the server which may be answered out of order. The protocol uses JSON (JavaScript Object Notation) for its data format, making it human-readable and easy to work with across many programming languages.

This guide covers the widely adopted JSON-RPC 2.0 specification, highlighting its structure, and providing hands-on Python examples using FastAPI and Pydantic.

## Why JSON-RPC for Agents?

**Key Benefits:**
- **Type Safety**: Structured requests/responses with clear contracts
- **Error Handling**: Standardized error codes and messages
- **Interoperability**: Works across different agent frameworks
- **Debugging**: Clear request/response correlation with IDs
- **Batching**: Multiple agent calls in single network round-trip

### Concept:

Regardless of the version, JSON-RPC revolves around a few core ideas:

- **Request Object**: A message sent from a client to a server to invoke a specific method with certain parameters.
- **Response Object**: A message sent from the server back to the client, containing the result of a successful method execution or an error object if the execution failed.
- **Notification**: A special type of request that does not require a response from the server.
- **Method**: A string representing the name of the procedure/function to be invoked on the server.
- **Params**: A structured value (Array or Object) holding the arguments for the method.
- **ID**: A unique identifier established by the client for a request. It's used to correlate a response with its corresponding request.

- 

## Strengths of JSON-RPC

- **Simplicity & Readability**: JSON is human-readable and easy to parse, aiding debugging and development.
- **Lightweight**: Minimal overhead compared to more verbose formats like XML (used in SOAP).
- **Interoperability**: Widely supported across programming languages and platforms due to JSON's ubiquity.
- **Clear Structure for RPC**: Provides a well-defined way to express method calls, parameters, results, and errors, especially in version 2.0.
- **Supports Notifications**: Allows for fire-and-forget messages (clear in 2.0, ambiguous in 1.0).
- **Transport Agnostic**: JSON-RPC itself only defines the payload format. It can be transported over various protocols like HTTP, WebSockets, TCP, stdio, etc.
- **Batching (2.0)**: Allows multiple calls to be sent in a single request, reducing network latency.

## Weaknesses/Considerations

- **Schema and Typing**: JSON itself is schema-less. While the JSON-RPC structure defines field names like `method`, `params`, `result`, `error`, the types and structure of `params` and `result` are application-defined. Robust systems often use an additional schema definition language (like JSON Schema, OpenAPI, or Protocol Buffers for gRPC which is an alternative to JSON-RPC) to define service interfaces.
- **No Built-in Security Features**: JSON-RPC does not define security mechanisms like authentication or authorization. These must be handled by the transport layer (e.g., HTTPS, OAuth over HTTP) or the application layer.
- **Error Handling Specificity (Beyond Codes)**: While JSON-RPC 2.0 standardizes error codes, detailed application-specific error information needs to be structured within the `error.data` field or by using the reserved server error code range.
- **Stateless**: Each request is independent. For stateful interactions, session management needs to be handled by the application or transport.
- **Discovery**: JSON-RPC does not specify a standard way for clients to discover available methods or their signatures (unlike, e.g., WSDL for SOAP or gRPC reflection). Systems often provide separate documentation or a meta-method for this.

## General Use Cases

- **Web APIs**: As an alternative to REST, especially when the interaction model is more about actions (procedures) than resources.
- **Microservices Communication**: For lightweight, synchronous inter-service calls.
- **Blockchain Interaction**: Many blockchain nodes (like Ethereum with its Geth client) expose a JSON-RPC API for interacting with the blockchain (e.g., sending transactions, querying state).
- **Desktop and Mobile Application Backends**: For client-server communication where a simple RPC mechanism is needed.
- **System Integration**: For simple machine-to-machine communication.
- **IoT (Internet of Things)**: For device-to-server or device-to-device communication where bandwidth and processing power might be limited.
- **Language Server Protocol (LSP)**: Used by IDEs and code editors to communicate with language servers for features like autocompletion, linting, etc. LSP messages are based on JSON-RPC.
  
---
## Core Protocol (JSON-RPC 2.0)

JSON-RPC 2.0 is the current, more robust version of the protocol. It clarifies many ambiguities of 1.0, introduces named parameters, a standardized error object, and explicit support for batch requests.

### JSON-RPC 2.0 Request Object

A 2.0 request **MUST** include:

- `jsonrpc: "2.0"`: A string specifying the version of the JSON-RPC protocol.
- `method`: A string containing the name of the method to be invoked.

It **MAY** include:

- `params`: A structured value that holds the parameter values to be used during the invocation of the method. This can be an Array (for positional parameters) or an Object (for named parameters).
- `id`: An identifier established by the client if a response is expected. The value can be a string, a number, or `null` (though `null` as an ID for a request expecting a response is discouraged due to potential confusion with 1.0 notifications). If the `id` member is omitted entirely, the request is treated as a notification.

**Example 2.0 Request (Positional Params):**

```json
{
  "jsonrpc": "2.0",
  "method": "add",
  "params": [5, 3],
  "id": "req-20-add-pos"
}
```

**Example 2.0 Request (Named Params):**

```json
{
  "jsonrpc": "2.0",
  "method": "subtract",
  "params": { "minuend": 42, "subtrahend": 23 },
  "id": "req-20-sub-named"
}
```

### JSON-RPC 2.0 Notification Object

A notification is a request object without an `id` member.

- It **MUST** include `jsonrpc: "2.0"` and `method`.
- It **MAY** include `params`.
- It **MUST NOT** include an `id` member (i.e., the "id" key itself should be absent).

The server **MUST NOT** reply to a notification (e.g., an HTTP 204 No Content is appropriate).

**Example 2.0 Notification:**

```json
{
  "jsonrpc": "2.0",
  "method": "log_event",
  "params": { "level": "info", "message": "User action performed" }
}
```

### JSON-RPC 2.0 Response Object (Success)

When a method call is successful, the server **MUST** reply with a Response object containing:

- `jsonrpc: "2.0"`: Version string.
- `result`: The value returned by the invoked method. Its type is defined by the method.
- `id`: Must match the `id` of the request.

It **MUST NOT** contain an `error` member.

**Example 2.0 Response (Success):**

```json
{
  "jsonrpc": "2.0",
  "result": 19,
  "id": "req-20-sub-named"
}
```

### JSON-RPC 2.0 Response Object (Error)

When a method call results in an error, the server **MUST** reply with a Response object containing:

- `jsonrpc: "2.0"`: Version string.
- `error`: An Error object (see below).
- `id`: Must match the `id` of the request. If detecting the `id` in the request is impossible (e.g., Parse error), it must be `null`.

It **MUST NOT** contain a `result` member.

#### Error Object (JSON-RPC 2.0)

The `error` object **MUST** contain:

- `code`: An integer indicating the error type.
- `message`: A string providing a short description of the error.

It **MAY** contain:

- `data`: A primitive or structured value containing additional information about the error.

**Pre-defined Error Codes (JSON-RPC 2.0):**

- `-32700 Parse error`: Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text.
- `-32600 Invalid Request`: The JSON sent is not a valid Request object.
- `-32601 Method not found`: The method does not exist / is not available.
- `-32602 Invalid params`: Invalid method parameter(s).
- `-32603 Internal error`: Internal JSON-RPC error.
- `-32000 to -32099 Server error`: Reserved for implementation-defined server-errors.

**Example 2.0 Response (Error):**

```json
{
  "jsonrpc": "2.0",
  "error": { "code": -32601, "message": "Method not found" },
  "id": "req-20-nonexistent"
}
```

### JSON-RPC 2.0 Batch Calls

To send multiple requests or notifications, the client can send an array of Request objects. The server processes each request in the batch and **SHOULD** return an array of corresponding Response objects.

- The server MAY process batch requests in parallel and respond out of order. The order of responses in the batch array does not need to match the order of requests.
- If all requests in a batch are notifications, the server **MUST NOT** return anything (an empty response or HTTP 204 No Content is appropriate).
- If the batch array itself is malformed (e.g., not an array, or an empty array), the server returns a single Response object error.

**Example 2.0 Batch Request:**

```json
[
  { "jsonrpc": "2.0", "method": "sum", "params": [1, 2, 4], "id": "1" },
  { "jsonrpc": "2.0", "method": "notify_hello", "params": [7] },
  { "jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": "2" }
]
```

**Example 2.0 Batch Response (order may vary):**

```json
[
  { "jsonrpc": "2.0", "result": 7, "id": "1" },
  { "jsonrpc": "2.0", "result": 19, "id": "2" }
]
```

(No response object for the `notify_hello` notification is included in the batch response array.)

## Relevance to DACA / Agent-to-Agent (A2A)

JSON-RPC's principles and structure are highly relevant for agentic systems like those envisioned by DACA, particularly for Agent-to-Agent (A2A) communication:

- **Structured Agent Commands**: JSON-RPC 2.0 provides a clean, standardized way to define "methods" (agent capabilities or actions) and "params" (arguments for those actions). This allows one agent to clearly instruct another.
- **Clear Outcomes & Error Handling**: The `result` and `error` objects (especially the well-defined V2 error object) offer a standardized mechanism for an agent to report the outcome of processing a command, including detailed error information if necessary.
- **Payload Format**: For A2A communication within frameworks like DACA, JSON-RPC can serve as the payload format over various transports. Whether agents communicate via direct HTTP calls (potentially managed by Dapr service invocation), messages over a Dapr pub/sub system, or other event-driven mechanisms, JSON-RPC provides a consistent message structure.
- **Interoperability**: If different agents are developed by different teams or even in different languages, a shared understanding of JSON-RPC as the communication contract simplifies integration.
- **Notifications for Asynchronous Tasks**: Agents can use JSON-RPC notifications to send fire-and-forget signals or trigger asynchronous tasks in other agents without needing an immediate response, fitting well with event-driven architectures.
- **Batching for Efficiency**: When an agent needs to make multiple requests to another agent (or a group of agents via a proxy), batching can reduce network overhead and latency.

Adopting JSON-RPC (preferably 2.0) for A2A payloads can promote consistency, simplify development, and improve debugging in complex multi-agent systems by providing a shared, well-understood protocol for interaction.

---

## Further Reading

- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification) (Official 2.0 Specification)
- [JSON-RPC 1.0 Specification (historical)](https://www.jsonrpc.org/specification_v1)
- [Differences between 1.0 and 2.0 (simple-is-better.org)](https://www.simple-is-better.org/rpc/#differences-between-1-0-and-2-0)
- Python Libraries:
  - [`json` module (built-in)](https://docs.python.org/3/library/json.html)
  - For building servers/clients with manual JSON-RPC handling: `FastAPI`, `Flask`, `aiohttp` (server-side) and `requests`, `httpx` (client-side).
  - Dedicated JSON-RPC libraries:
    - Server: [`jsonrpcserver`](https://jsonrpcserver.readthedocs.io/en/latest/), [`python-jsonrpc-server`](https://pypi.org/project/python-jsonrpc-server/)
    - Client: [`jsonrpcclient`](https://jsonrpcclient.readthedocs.io/en/latest/)
- [Wallarm: What is JSON-RPC?](https://www.wallarm.com/what/what-is-json-rpc) (Provides general context and use cases)
- [Language Server Protocol (LSP) Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/) (Example of JSON-RPC in a widely used protocol)
