# What MCP is
MCP standardizes how an AI app (the host) connects to one or more “MCP servers” that expose tools, resources, and prompts. The wire format is JSON-RPC 2.0. It is stateful, with an initialization handshake that negotiates capabilities, then long-lived messaging for requests, responses, and notifications. 

## Two layers

### 1. Data layer. 
Defines lifecycle management, the primitives (tools, resources, prompts), client-side primitives the server can call back into (sampling, elicitation, logging), and notifications. All over JSON-RPC 2.0. 
### 2. Transport layer. 
Defines how messages move. Today the spec highlights two standard transports: stdio for local processes, and Streamable HTTP for remote, with optional SSE for server-to-client streaming. Auth is via normal HTTP methods like bearer tokens or custom headers. 

### Core primitives to emphasize
#### Server exposes:
• **Tools**. Executable functions callable by the client. Discover with tools/list, call with tools/call.

• **Resources**. Read-only context like files, schemas, API responses. Discover with resources/list, fetch with resources/read.

• **Prompts**. Server-provided templates that can be parameterized via prompts/list and prompts/get.
Client exposes:

• **Sampling**. Server can ask the client to get an LLM completion via sampling/complete.

• **Elicitation**. Server can request extra user input.

• **Logging**. Server streams logs to the client.
These are negotiated at init so both sides know what’s available. 


1. initialize. Client sends protocolVersion and its capabilities, gets serverInfo and server capabilities back.
2. notifications/initialized. Client signals it is ready.
3. Discovery. tools/list, resources/list, prompts/list as needed.
4. Execution. tools/call, resources/read, prompts/get, with progress and notifications as supported.
5. Notifications. e.g., notifications/tools/list_changed when tool inventory changes. 

### Transports, when to use what
#### Stdio
• Best for local development, CLIs, and editors spawning a child process.
• Lowest latency, no network.
• Typical in Claude Desktop or VS Code launching a local server. 

#### Streamable HTTP
• Best for remote servers or when you want normal HTTP auth and routing.
• Client-to-server over POST, with optional streaming back using SSE semantics; widely used for hosted servers and cloud platforms. 

#### What about SSE and WebSockets
• The spec’s current emphasis is stdio and Streamable HTTP, with optional SSE streaming semantics on HTTP. Some community SDKs/frameworks note SSE as deprecated in favor of Streamable HTTP

#### Hosted MCP tool (model calls the server directly, no Python callback round-trip)
• Use HostedMCPTool. You pass a server label or connector config.
• Good for minimizing latency and infrastructure on your side. ([OpenAI GitHub][3])
