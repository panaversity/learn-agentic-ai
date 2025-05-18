# MCP Communication Transports

The Model Context Protocol (MCP) is designed to be transport-agnostic at its core, primarily defining the message structures (based on JSON-RPC 2.0) and the logical flow of interactions (lifecycle, capabilities). However, to ensure practical interoperability, MCP also specifies standard transport bindings.

These transports define how MCP messages are exchanged over different underlying communication channels. Key considerations for MCP transports include:

- **Reliability:** Ensuring messages are delivered.
- **Efficiency:** Minimizing overhead.
- **Bidirectional Communication:** Supporting messages from Client-to-Server and Server-to-Client (especially for notifications).
- **Compatibility:** Working well with existing infrastructure (e.g., HTTP proxies, load balancers).
- **Security:** Allowing for secure communication channels.

Currently, the primary transport mechanisms are:

1.  **Stdio (Standard Input/Output):**

    - Used for **local servers** that run as subprocesses managed by the MCP Host.
    - Communication occurs over the server process's standard input and standard output streams.
    - Offers simplicity and is well-suited for scenarios requiring high privacy or direct access to local system resources.

2.  **Streamable HTTP Transport:**

    - The **current standard** for **remote servers** accessible over a network, as defined in the 2025-03-26 MCP specification.
    - It supersedes the earlier HTTP+SSE mechanism, offering enhanced flexibility, robustness, and efficiency.
    - Its design, particularly its support for operationally stateless server implementations and improved connection management, makes it highly suitable for scalable and resilient architectures like DACA.
    - Detailed in [Streamable HTTP](./01_streamable_http.md)

3.  **HTTP with Server-Sent Events (HTTP+SSE) - Earlier Remote Transport:**

    - The **primary mechanism for remote servers prior to the 2025-03-26 specification**.
    - Utilized a main HTTP endpoint for client-to-server requests and a separate `/sse` endpoint for server-to-client event streams.
    - While it enabled basic remote MCP communication, the Streamable HTTP transport was introduced to address its limitations in areas like connection resumability, server operational flexibility (statelessness), and overall efficiency.

Understanding these transports is crucial for implementing and deploying MCP clients and servers effectively.
