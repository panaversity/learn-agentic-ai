# 01_base: Foundational Communication Protocols - A Learning Path

This directory organizes fundamental communication protocols in a suggested learning order. Each protocol builds upon concepts from the previous ones or introduces new paradigms in a progressive manner, essential for understanding how agentic systems and modern distributed applications communicate.

## The Learning Curve:

1.  **[`01_Http/`](01_Http/)**: Hypertext Transfer Protocol
2.  **[`02_REST/`](02_REST/)**: Representational State Transfer
3.  **[`03_Streamable_HTTP/`](03_Streamable_HTTP/)**: Streamable HTTP
4.  **[`04_SSE/`](04_SSE/)**: Server-Sent Events
5.  **[`05_JSON_RPC/`](05_JSON_RPC/)**: JSON Remote Procedure Call
6.  **[`06_GRPC/`](06_GRPC/)**: Google Remote Procedure Call

---

### 1. `01_Http/`: Hypertext Transfer Protocol

- **Summary**: HTTP is the bedrock of data communication for the World Wide Web. It's a client-server protocol where requests are initiated by the recipient (usually a web browser or an agent). Understanding HTTP methods (GET, POST, PUT, DELETE, etc.), headers, status codes, and the request/response cycle is the first crucial step.
- **Learning Context**: Start here. HTTP concepts are fundamental to almost all web-based communication, including many of the protocols that follow. It provides the basic vocabulary for web interactions.

### 2. `02_REST/`: Representational State Transfer

- **Summary**: REST is an architectural style, not a specific protocol, that leverages HTTP's standards. It's used for designing networked applications, emphasizing stateless communication, resource-based interactions (identified by URLs), and the use of standard HTTP methods to perform operations on these resources.
- **Learning Context**: After understanding HTTP, REST is the next logical step. It shows how to apply HTTP principles to build scalable and maintainable APIs, which are vital for agents interacting with services or each other.

### 3. `03_Streamable_HTTP/`: Streamable HTTP

- **Summary**: This covers techniques and patterns for streaming data over HTTP. Instead of sending entire payloads at once, data is sent in chunks. This is essential for handling large files, real-time data feeds, or long-lived connections where data arrives incrementally.
- **Learning Context**: Building on HTTP/REST, streamable HTTP addresses scenarios where batch processing of requests/responses is inefficient or impractical. It's important for agents dealing with large datasets or continuous information flows.

### 4. `04_SSE/` (Server-Sent Events)

- **Summary**: SSE is a simple, HTTP-based standard that allows a server to push real-time updates to a client (e.g., an agent or a web browser) over a single, long-lived HTTP connection. It's unidirectional (server to client).
- **Learning Context**: Once HTTP is clear, SSE provides a straightforward way to implement real-time notifications without the complexity of bidirectional protocols. It's useful for agents that need to react to asynchronous events pushed by a server.

### 5. `05_JSON_RPC/`: JSON Remote Procedure Call

- **Summary**: JSON-RPC is a lightweight remote procedure call (RPC) protocol. It uses JSON for its data format and typically HTTP as a transport mechanism. It allows a client to call methods on a remote server as if they were local procedures.
- **Learning Context**: This introduces the RPC paradigm, which is different from the resource-oriented style of REST. JSON-RPC is simpler than gRPC and serves as a good entry point to understanding how agents or services can invoke specific functions on each other directly.

### 6. `06_GRPC/` (Google Remote Procedure Call)

- **Summary**: gRPC is a modern, high-performance, open-source universal RPC framework developed by Google. It uses Protocol Buffers by default as its interface definition language and data serialization format, and typically operates over HTTP/2 for efficiency. It supports various communication patterns like unary, server streaming, client streaming, and bidirectional streaming.
- **Learning Context**: As the final step in this base protocol learning path, gRPC introduces more advanced RPC concepts, performance optimizations, and a stricter contract-first approach to API design using Protocol Buffers. It's ideal for high-throughput internal microservice or agent-to-agent communication where performance and type safety are critical.

By progressing through these protocols, developers can build a strong foundation in the diverse ways software components and AI agents communicate in distributed environments, preparing them for the more specialized AI protocols like MCP and A2A.
