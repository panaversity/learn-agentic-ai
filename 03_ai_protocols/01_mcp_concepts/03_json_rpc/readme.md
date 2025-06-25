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

