# 04: OAuth 2.1 and Security

**Objective:** Implement the complete, end-to-end OAuth 2.1 Authorization Code Flow as specified by the MCP `2025-06-18` standard.

This section is the cornerstone of building secure, production-ready MCP applications. We will create a secure MCP Resource Server and a compliant MCP Client that knows how to acquire and use access tokens to interact with protected resources.

This is a deep, multi-step journey that covers the full lifecycle of modern API security.

## Key MCP and OAuth Concepts

-   **MCP as an OAuth Resource Server:** An MCP server is not just a tool provider; it's a protected resource. We will configure our FastMCP server to require a valid access token for all its operations.
-   **Authorization Server (AS):** A separate, third-party service responsible for authenticating users and issuing access tokens. For this lesson, we will simulate a simple AS.
-   **Protected Resource Metadata:** The mechanism by which an MCP server advertises the location and requirements of its Authorization Server (`/.well-known/oauth-authorization-server`).
-   **Dynamic Client Registration:** How a client can programmatically register itself with an Authorization Server.
-   **Authorization Code Flow:** The secure, browser-based flow where a user grants consent, and the client receives an authorization code, which it then exchanges for an access token.
-   **Resource Indicators (RFC 8707):** A critical security feature where the client specifies the intended audience (the MCP server) for the requested token, preventing token leakage and misuse.
-   **Token Validation (JWT):** The MCP server's responsibility to receive an access token (as a JWT), validate its signature, issuer, and audience, and extract user claims before granting access.

## Learning Path

We will build the entire flow from the ground up, piece by piece:

1.  **`01_protected_resource_metadata`:** Make the MCP server advertise its security requirements.
2.  **`02_authorization_server_discovery`:** Teach the client how to find the AS from the MCP server's metadata.
3.  **`03_dynamic_client_registration`:** Programmatically register our client with the AS.
4.  **`04_oauth2_authorization_code_flow`:** Implement the full, user-facing login flow to get an access token.
5.  **`05_token_audience_validation`:** Implement JWT validation on the MCP server.
6.  **`06_error_handling`:** Handle common OAuth errors like invalid tokens or insufficient scope.
7.  **`07_security_best_practices`:** Review and implement key security considerations from the spec. 