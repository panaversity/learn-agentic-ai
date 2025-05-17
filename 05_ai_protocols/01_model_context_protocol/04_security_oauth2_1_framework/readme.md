# Module 04: MCP Security & OAuth 2.1 Framework

Authorization is OPTIONAL for MCP implementations. When supported Implementations using an HTTP-based transport SHOULD conform to this specification.

**Objective:** To understand and learn how to apply the OAuth 2.1 authorization framework to secure Model Context Protocol (MCP) interactions, by studying the official MCP specifications and the `simple-auth` example from the Python SDK.

## 🔗 Relevant MCP Specifications & Examples

- **Main Specification (Security Section):** [MCP Specification 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26) (Refer to "Security and Trust & Safety")
- **Authorization Specifics:** [MCP Authorization Spec (2025-03-26)](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization)
- **Python SDK `simple-auth` Example:** [GitHub Link](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-auth)
- **`simple-auth` Server Code:** [server.py](https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/servers/simple-auth/mcp_simple_auth/server.py)
- **MCP Auth Provider (SDK):** [provider.py](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/auth/provider.py)

## Introduction

As MCP enables powerful capabilities through data access and tool execution, securing these interactions is paramount. The MCP specification details the use of OAuth 2.1 for authorization. This module will guide you through understanding and applying these principles by dissecting the MCP documentation and the official `simple-auth` Python SDK example.

Our primary goal is to learn how MCP expects OAuth 2.1 to be implemented, rather than learning OAuth 2.1 from first principles in isolation.

## Core MCP Authorization Concepts (OAuth 2.1)

Based on the MCP specifications ([Authorization Spec](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization)), understanding these concepts is crucial:

1.  **Key Security Principles (MCP Spec):**

    - User Consent and Control
    - Data Privacy
    - Tool Safety
    - LLM Sampling Controls

2.  **OAuth 2.1 Roles in MCP:**

    - MCP Client (OAuth 2.1 Client)
    - MCP Server (OAuth 2.1 Resource Server)
    - Authorization Server (Can be part of the MCP server or separate)

3.  **Authorization Flow Highlights (as per MCP Spec):**

    - **Supported Grant Types:** MCP recommends Authorization Code (for user-facing clients) and Client Credentials (for machine-to-machine).
    - **Discovery (RFC8414):**
      - MCP Servers SHOULD support OAuth 2.0 Authorization Server Metadata.
      - MCP Clients MUST support it.
      - Fallbacks to default URI paths are specified if metadata discovery is not supported by the server.
      - Authorization Base URL derived from MCP server URL (e.g. `https://api.example.com` if MCP server is `https://api.example.com/v1/mcp`)
    - **Dynamic Client Registration (DCR - RFC7591):** SHOULD be supported by clients and servers.
    - **Access Tokens:** Bearer tokens in `Authorization` header.
    - **PKCE (Proof Key for Code Exchange):** REQUIRED for all clients using flows like Authorization Code.

4.  **MCP Specific Headers:**

    - `MCP-Protocol-Version`: For compatibility checks during discovery and requests.

5.  **Critical Security Considerations (MUST be implemented):**
    - HTTPS for all authorization endpoints.
    - Secure token storage by clients.
    - Server-side redirect URI validation.
    - Token expiration and rotation SHOULD be enforced by servers.

## Learning Path

This module focuses on dissecting the MCP's OAuth 2.1 implementation using its official specifications and the `simple-auth` example. The initial step involves running the example, which will also serve as our entry point for analyzing the architecture in a practical context. Each subsequent step will guide you through understanding different parts of this existing framework.

1.  **`01_running_the_mcp_simple_auth_example`**:

    - **Objective:** Set up, run, and observe the behavior of the official MCP `simple-auth` example. Analyze the OAuth 2.1 architecture within the MCP context by studying the example's structure alongside the MCP authorization specification.
    - **Contents:** Step-by-step guide to configure and run the `simple-auth` server. Map the MCP Authorization Spec's roles (Client, Resource Server, Auth Server) to components in the `simple-auth` example. Instructions on how to simulate an MCP client interaction to trigger the OAuth flow (e.g., using `curl` or a basic script) and observe the HTTP 401, redirection, and token exchange.
    - **Activities:** Clone the `python-sdk` repo (or just the example), install dependencies, run the `simple-auth` server. Make requests to its MCP endpoints to see the auth flow in action. Document the mapping between the spec and the example.

2.  **`02_deep_dive_simple_auth_server`**:

    - **Objective:** Understand the server-side implementation of OAuth 2.1 in the `simple-auth` example, referencing `server.py` and `provider.py`.
    - **Contents:** Code walk-through focusing on:
      - How `mcp_simple_auth.server.SimpleAuthMCP` protects tools.
      - The role of `mcp.server.auth.AuthProvider` and its concrete implementation in the example.
      - Handling of `/authorize` and `/token` endpoints (even if simplified).
      - PKCE validation, token issuance, and token validation logic.
      - Implementation of metadata discovery (e.g., `/.well-known/oauth-authorization-server`).
    - **Activities:** Debug and trace the execution path within the `simple-auth` server code during an OAuth flow.

3.  **`03_mcp_client_integration_with_simple_auth`**:

    - **Objective:** Understand how an MCP client should interact with an MCP server secured like the `simple-auth` example.
    - **Contents:** Client-side responsibilities:
      - Initiating the Authorization Code Grant with PKCE.
      - Handling redirects from the Authorization Server.
      - Exchanging the authorization code for an access token at the token endpoint.
      - Using the access token (as a Bearer token) in subsequent requests to the MCP server.
      - Server metadata discovery by the client.
    - **Activities:** Write a Python script that acts as a basic MCP client, performing the full OAuth 2.1 Authorization Code flow with PKCE against your running `simple-auth` example server.

4.  **`04_exploring_advanced_mcp_oauth_features`**:

    - **Objective:** Study how more advanced OAuth features, recommended by MCP, would apply.
    - **Contents:** Discussion on:
      - **Scopes:** How to define and use OAuth scopes for fine-grained access control to different MCP tools/resources within the `simple-auth` context.
      - **Dynamic Client Registration (DCR):** Review MCP's recommendation for DCR and conceptualize its integration with the `simple-auth` example.
      - **Client Credentials Grant:** How to implement and use the client credentials grant for M2M authentication with an MCP server.
    - **Activities:** Outline code modifications to the `simple-auth` example to support a basic scope. Draft a sequence diagram for DCR in the MCP context.

Review the implementation against MCP and OAuth 2.1 security best practices:
- Use the security considerations from the MCP Authorization spec ([2.7 Security Considerations](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization#27-security-considerations) and [3. Best Practices](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization#3-best-practices)) as a checklist.
- Evaluate the `simple-auth` example and your client script against these best practices. Identify any gaps or areas for improvement.

## 🔗 Key Resources

- **MCP Authorization Spec (2025-03-26):** [Link](https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization)
- **Python SDK `simple-auth` Example Directory (Original):** [GitHub Link](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/servers/simple-auth)
- **`simple-auth` Server Code (`server.py` in this module is based on this):** [GitHub Link](https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/servers/simple-auth/mcp_simple_auth/server.py)
- **`simple-auth` Provider Code (Original):** [GitHub Link](https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/servers/simple-auth/mcp_simple_auth/provider.py)
- **General MCP Auth Provider (SDK Base):** [provider.py in SDK](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/auth/provider.py)
- https://auth0.com/blog/an-introduction-to-mcp-and-authorization/
- https://github.com/modelcontextprotocol/modelcontextprotocol/issues/205
- https://github.com/modelcontextprotocol/python-sdk/issues/702
- https://stytch.com/blog/mcp-authentication-and-authorization-servers/