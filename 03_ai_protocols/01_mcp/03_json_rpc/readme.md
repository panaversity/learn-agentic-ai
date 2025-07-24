# Introduction to JSON-RPC 2.0

[Specification](https://www.jsonrpc.org/specification)

JSON-RPC 2.0 is a lightweight and stateless remote procedure call (RPC) protocol that allows for notifications and remote procedure calls in a simple, standardized way. It uses JSON (JavaScript Object Notation) as its data format, making it easy to use with a wide variety of programming languages and platforms. The protocol is transport-agnostic, meaning it can be used over HTTP, WebSockets, or any other message-passing environment.

At its core, JSON-RPC 2.0 defines a set of data structures and the rules for their processing. It's designed for simplicity and is a popular choice for building APIs and distributed systems.

### Key Concepts

#### 1\. Request Object

A remote procedure call is initiated by sending a `Request` object to a server. This object has the following members:

  * **`jsonrpc`**: A string that specifies the version of the JSON-RPC protocol. For version 2.0, this **MUST** be exactly `"2.0"`.
  * **`method`**: A string containing the name of the method to be invoked on the server.
  * **`params`**: A structured value (either an `Array` or `Object`) that holds the parameters for the method. This member can be omitted if the method doesn't require any parameters.
  * **`id`**: An identifier established by the client. It can be a string, a number, or `null`. If it's not included, the request is considered a "notification."

#### 2\. Notification

A notification is a special type of `Request` object that does not include the `id` member. When a client sends a notification, it's signaling that it's not interested in a response from the server. The server **MUST NOT** reply to a notification.

Notifications are useful for one-way communication, like sending events or logging information. However, because they don't have a corresponding response, the client won't be aware of any errors that might occur.

#### 3\. Parameter Structures

When calling a method with parameters, the `params` member can be structured in two ways:

  * **By-position**: The `params` member is an `Array` of values, where each value corresponds to a parameter in the order the server expects.
  * **By-name**: The `params` member is an `Object`, where each key-value pair represents a named parameter.

#### 4\. Response Object

When a client makes a standard RPC call (not a notification), the server **MUST** reply with a `Response` object. This object contains the following members:

  * **`jsonrpc`**: The JSON-RPC protocol version, which **MUST** be `"2.0"`.
  * **`result`**: This member is **REQUIRED** on success. Its value is determined by the method that was invoked on the server. If there was an error, this member **MUST NOT** be included.
  * **`error`**: This member is **REQUIRED** on error. If there was no error, this member **MUST NOT** be included. The value of this member is an `Error` object.
  * **`id`**: This member is **REQUIRED** and **MUST** be the same as the `id` from the `Request` object.

A `Response` object **MUST** contain either the `result` or the `error` member, but not both.

#### 5\. Error Object

If an error occurs during an RPC call, the `Response` object will contain an `error` member with the following structure:

  * **`code`**: An integer that indicates the type of error.
  * **`message`**: A short, single-sentence description of the error.
  * **`data`**: A primitive or structured value with additional information about the error. This is optional and its format is defined by the server.

Here are some predefined error codes:

| Code | Message | Meaning |
| :--- | :--- | :--- |
| -32700 | Parse error | Invalid JSON was received by the server. |
| -32600 | Invalid Request | The JSON sent is not a valid Request object. |
| -32601 | Method not found | The method does not exist or is not available. |
| -32602 | Invalid params | Invalid method parameter(s). |
| -32603 | Internal error | Internal JSON-RPC error. |
| -32000 to -32099 | Server error | Reserved for implementation-defined server errors. |

#### 6\. Batch Requests

To send multiple `Request` objects at once, a client can send an `Array` of `Request` objects. The server will process all the requests and respond with an `Array` of the corresponding `Response` objects. The server can process a batch of requests in any order, and the responses can also be in any order. The client should use the `id` of each request to match it with its response.

### Examples

Here are some examples of JSON-RPC 2.0 in action:

**RPC call with positional parameters:**

*Client sends:*

```json
{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
```

*Server responds:*

```json
{"jsonrpc": "2.0", "result": 19, "id": 1}
```

**RPC call with named parameters:**

*Client sends:*

```json
{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}
```

*Server responds:*

```json
{"jsonrpc": "2.0", "result": 19, "id": 3}
```

**A notification:**

*Client sends:*

```json
{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}
```

*(No response from the server)*

**RPC call to a non-existent method:**

*Client sends:*

```json
{"jsonrpc": "2.0", "method": "foobar", "id": "1"}
```

*Server responds:*

```json
{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "1"}
```

### Extensions

Method names that start with `rpc.` are reserved for system extensions and should not be used for anything else.


---

## **Why JSON-RPC for Model Context Protocol (MCP), not REST?**

**Model Context Protocol (MCP)** chooses **JSON-RPC** over REST for several technical and strategic reasons. Understanding this will also give you an edge in designing or integrating agent frameworks!

---

### **1. Agent/Model Operations Need More Than REST’s CRUD**

REST is built around CRUD (Create, Read, Update, Delete), mapping HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`) to resources. But LLM/Agent orchestration protocols like MCP need something different:

* **Procedural/Command-like Interactions:**
  MCP sessions involve rich operations—start, cancel, resume, stream, call tool, manage prompt state, etc.—that don’t map neatly to CRUD.

**JSON-RPC** is designed for *remote procedure calls* (Calling a function on another computer, as if it was a local function in your code.) — “Do this specific thing for me and return the result”—making it a natural fit.

---

### **2. Multiplexing & Streaming Support**

* **Multiple calls on the same connection:**
  JSON-RPC is naturally suited to protocols that need to keep an open channel (e.g., WebSocket, HTTP/2, SSE) and send multiple commands and responses in real-time. REST (over HTTP 1.1) usually opens a new connection/request per action.
* **Streaming & Notifications:**
  With agents, you might want progress updates, partial results, or server-initiated messages (notifications).
  JSON-RPC supports *notifications* (one-way messages), which is not idiomatic in REST.

---

### **3. Explicit Method Names and Structured Requests**

* **In REST, the endpoint and verb define the operation.**
  In JSON-RPC, you get `{"method": "tools/call", ...}`—the action is explicit and discoverable, not hidden in URL/HTTP verb combos.
* **Easy to extend:**
  Adding new capabilities (new methods) doesn’t require inventing new URLs or overloading HTTP semantics.

---

### **4. Stateless vs. Stateful Workflows**

* **MCP can run stateful workflows** (sessions, resumption, tool resources, etc.), which benefit from a protocol that can express both state changes and direct procedure invocations.
* REST is best for stateless, resource-centric operations.

  ##### How can MCP do stateful things if JSON-RPC is stateless?
  * The “state” is maintained by the server (or agent), not the protocol.

  * MCP uses things like session_id, context_id, or other tokens/IDs to let the server keep track of ongoing workflows or conversations.

  * Each JSON-RPC call includes the necessary information (like the session/context) so the server knows which workflow or conversation it’s handling.

---

### **5. Strong Error Handling**

* **JSON-RPC defines a standard, structured error response** (`error` with code, message, data) for every request.
* REST error handling is less standardized and can be messy (status codes + arbitrary payloads).

---

### **6. Ecosystem and Alignment with IDE Protocols**

* **LLM agents and tools are inspired by language servers, debuggers, IDE plugins, etc.—many of which use JSON-RPC.**
* Examples: LSP (Language Server Protocol), Debug Adapter Protocol—both JSON-RPC-based!

---

### **Summary Table**

| Feature        | REST                     | JSON-RPC (used by MCP)        |
| -------------- | ------------------------ | ----------------------------- |
| Paradigm       | Resource/CRUD            | Remote Procedure Call (RPC)   |
| Operations     | Limited to HTTP verbs    | Arbitrary named methods       |
| Streaming      | Tricky, non-standard     | Native via WebSocket/SSE      |
| Multiplexing   | New HTTP req for each op | Multiple in single connection |
| Notifications  | Not idiomatic            | Built-in                      |
| Error Handling | Varies, not standardized | Structured, part of protocol  |
| Statefulness   | Stateless best practice  | Can support sessions/state    |
| Extensibility  | Needs URL/method changes | Just add new methods          |

---

### **Forward-Looking Take:**

Protocols like MCP are designed for the **future of AI orchestration**, not just simple CRUD APIs. They need:

* Fine-grained control over model context and tools,
* Real-time interactivity and notifications,
* Consistency and extensibility.

**JSON-RPC is purpose-built for these requirements**, making it a far better fit than REST for advanced agent/model protocols. If you're planning to design LLM-based systems or integrate AI agents at scale, understanding and leveraging these design choices puts you way ahead!
