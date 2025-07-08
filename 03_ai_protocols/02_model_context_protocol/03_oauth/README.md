# OAuth 2.1 and Security for MCP

**Objective:** Implement the complete, end-to-end OAuth 2.1 Authorization Code Flow as specified by the MCP `2025-06-18` standard.

This section is the cornerstone of building secure, production-ready MCP applications. We will create a secure MCP Resource Server and a compliant MCP Client that knows how to acquire and use access tokens to interact with protected resources.

This is a deep, multi-step journey that covers the full lifecycle of modern API security.

## Key MCP and OAuth Concepts

-   **MCP as an OAuth Resource Server:** An MCP server is not just a tool provider; it's a protected resource. We will configure our MCP server to require a valid access token for all its operations.
-   **Authorization Server (AS):** A separate, third-party service responsible for authenticating users and issuing access tokens. We will create a simple OAuth AS for demonstration.
-   **Two-Stage Discovery Process:** 
    1. **Protected Resource Metadata** (`/.well-known/oauth-protected-resource` on MCP server) - tells clients where to find the Authorization Server
    2. **Authorization Server Metadata** (`/.well-known/oauth-authorization-server` on AS) - tells clients the specific endpoints for registration, authorization, and tokens
-   **Dynamic Client Registration:** How a client can programmatically register itself with an Authorization Server.
-   **Authorization Code Flow:** The secure, browser-based flow where a user grants consent, and the client receives an authorization code, which it then exchanges for an access token.
-   **Resource Indicators (RFC 8707):** A critical security feature where the client specifies the intended audience (the MCP server) for the requested token, preventing token leakage and misuse.
-   **Token Validation (JWT):** The MCP server's responsibility to receive an access token (as a JWT), validate its signature, issuer, and audience, and extract user claims before granting access.

## Learning Path

We build the entire flow from the ground up, piece by piece:

1.  **`01_protected_resource_metadata`:** MCP server advertises its security requirements and Authorization Server location via `/.well-known/oauth-protected-resource` - implements the first stage of OAuth discovery
2.  **`02_authorization_server_metadata`:** Create a simple OAuth Authorization Server that provides its endpoint information via `/.well-known/oauth-authorization-server` - completes the two-stage discovery process
3.  **`03_dynamic_client_registration`:** Programmatically register our client with the Authorization Server using the `/register` endpoint - enables automatic client onboarding
4.  **`04_oauth2_authorization_code_flow`:** Implement the full, user-facing login flow to get an access token - the primary OAuth flow for user authentication
5.  **`05_token_audience_validation`:** Implement JWT validation on the MCP server - ensures tokens are properly validated and scoped
6.  **`06_error_handling`:** Handle common OAuth errors like invalid tokens or insufficient scope - builds robust error handling
7.  **`07_security_best_practices`:** Review and implement key security considerations from the spec - hardens the implementation
8.  **`08_client_credentials_flow`:** System-to-system authentication without user interaction - enables machine-to-machine communication for DACA agents

## Current Step Breakdown

**Steps 1-3: Discovery & Registration (Foundation)**
- **01**: Find where the Auth Server is (`http://localhost:9000`)
- **02**: Query Auth Server to learn its endpoints (`/authorize`, `/token`, `/register`)  
- **03**: Register client to get `client_id` and `client_secret`

**Steps 4-7: Full OAuth Flow (User Interactive)**
- **04**: Complete authorization code flow (user login, get access token)
- **05**: MCP server validates tokens (JWT signature, audience, etc.)
- **06**: Handle OAuth errors (expired tokens, insufficient scope)
- **07**: Security best practices review

**Step 8: Alternative Flow (System-to-System)**
- **08**: Client credentials flow (no user interaction needed)

## The Logic Flow

For **human users** (interactive):
```
Steps 1→2→3→4→5 = Complete user-interactive OAuth flow
```

For **system-to-system** (automated):
```
Steps 1→2→3→8→5 = Complete machine-to-machine flow
```

Steps 6-7 apply to both scenarios.

## What Happens in Later Steps?

After completing all OAuth steps, you'd typically move to:

1. **Build Real MCP Applications** - Use the secured MCP server for actual tools
2. **Deploy to Production** - Take the OAuth-secured setup to cloud platforms
3. **Scale with DACA** - Apply the Dapr Agentic Cloud Ascent patterns we discussed
4. **Agent-to-Agent Communication** - Use the OAuth foundation for secure A2A protocols

## The Value of This Progression

Each step teaches a specific piece:
- **01-03**: How clients discover and register with auth systems
- **04**: How users authenticate and authorize
- **05**: How servers validate security
- **06-07**: How to handle real-world issues
- **08**: How systems authenticate without humans

This gives you the complete toolkit for both user-facing and automated secure MCP applications.

## Two-Server Architecture

Step 01 and 02 implementation follows the MCP specification's two-server model:

- **MCP Server** (localhost:8000) - The Resource Server protecting tools/resources
- **Authorization Server** (localhost:9000) - The OAuth server handling authentication and token issuance

Each server has its own discovery endpoint:
- MCP Server: `GET /.well-known/oauth-protected-resource` 
- Authorization Server: `GET /.well-known/oauth-authorization-server`

This separation allows for flexible deployment where the Authorization Server can serve multiple MCP servers. 