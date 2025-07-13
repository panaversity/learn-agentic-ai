# 07: Security Best Practices

**Objective:** Review and consolidate the security best practices learned throughout the OAuth section, cross-referencing them with the official MCP specification.

This final lesson in the OAuth module is less about writing new code and more about understanding the "why" behind the code we've written. We will create a checklist of security measures and ensure our implementation adheres to them.

## Key Security Concepts (from MCP Spec)

This lesson directly reinforces the requirements in the [`authorization.mdx`](https://github.com/modelcontextprotocol/specification/blob/main/specification/2025-06-18/basic/authorization.mdx) and [`security_best_practices.mdx`](https://github.com/modelcontextprotocol/specification/blob/main/specification/2025-06-18/basic/security_best_practices.mdx) documents.

-   **Confidential Clients:** Clients capable of storing a secret (like our native Python client) **SHOULD** be treated as confidential and use their `client_secret` when interacting with the token endpoint.
-   **PKCE (Proof Key for Code Exchange):** While not explicitly built in our mock flow for simplicity, we will discuss why PKCE is **REQUIRED** for public clients (like browser-based JS apps) and **RECOMMENDED** for all clients to prevent authorization code interception attacks.
-   **HTTPS:** All communication with the Authorization Server and MCP Server **MUST** use TLS (HTTPS) in a production environment.
-   **Secure Credential Storage:** The client **MUST** store its `client_secret` and any received refresh tokens securely (e.g., using the system keychain, not in a plain text file).
-   **State Parameter:** The `state` parameter **MUST** be used in authorization requests to mitigate CSRF attacks.
-   **Resource Indicators (RFC 8707):** As implemented, clients **MUST** use the `resource` parameter to specify the token's audience, preventing token misdirection.
-   **Token Validation:** The MCP server **MUST** perform full token validation, including signature, expiry, issuer, and audience checks.

## Implementation Plan

This lesson is primarily a code review and documentation exercise.

-   **`checklist.md`:**
    -   We will create a new markdown file containing a security checklist based on the points above.

-   **Code Review:**
    -   We will go through the code written in the previous lessons (`client.py`, `mcp_server.py`, `authorization_server_mock.py`).
    -   For each item on our checklist, we will identify the exact line(s) of code that implement the security measure.
    -   For items we simplified for the tutorial (like PKCE or secure storage), we will add comments to the code explaining what a production-ready implementation would need to do differently.

-   **Final Test:**
    -   Run the complete end-to-end flow one last time to ensure all components are working together correctly and securely. 