# 05: Token Audience and Signature Validation

**Objective:** Secure the MCP server by teaching it how to validate the access tokens (JWTs) it receives from the client.

This is the final and most critical step in protecting the Resource Server. An MCP server **MUST NOT** grant access based on the mere presence of a token; it **MUST** validate the token's signature, expiration, issuer, and, most importantly, its intended audience.

## Key MCP and OAuth Concepts

-   **JSON Web Token (JWT):** A compact, URL-safe standard for representing claims to be transferred between two parties. The access tokens issued by our AS will be JWTs.
-   **Bearer Token:** An access token that can be used by whoever possesses it ("the bearer"). They are sent in the `Authorization` HTTP header: `Authorization: Bearer <token>`.
-   **JWT Validation:** A multi-step process the MCP server must perform:
    1.  **Fetch Public Keys:** Get the AS's public keys from its `jwks_uri` (discovered in lesson 2).
    2.  **Verify Signature:** Use the public key to verify that the JWT was actually signed by the AS and has not been tampered with.
    3.  **Verify Claims:** Check the standard claims within the JWT payload:
        -   `exp`: The token has not expired.
        -   `iss`: The token was issued by the expected Authorization Server.
        -   **`aud` (Audience):** This is the most important claim for MCP. The server **MUST** verify that the `aud` claim contains its own unique identifier. This ensures the token was specifically issued for use with *this* MCP server and not some other service.

## Implementation Plan

-   **`authorization_server_mock.py`:**
    -   The mock AS will now sign the JWTs it issues with a private key.
    -   It will also expose a `/jwks.json` endpoint (its `jwks_uri`) that contains the corresponding public key.

-   **`mcp_server.py`:**
    -   We will enhance the server's security middleware.
    -   When a request with a `Bearer` token arrives, the middleware will:
        1.  Fetch the AS's public keys from its `jwks_uri` (and cache them).
        2.  Decode and validate the JWT using a standard library (like `python-jose`).
        3.  Crucially, it will check that the `aud` claim in the token matches the MCP server's own identifier.
        4.  If validation succeeds, it will allow the request to proceed. Otherwise, it will return a `401` or `403` error.

-   **`client.py`:**
    -   After obtaining the access token (from the previous lesson), the client will now use it.
    -   It will make a request to a protected MCP endpoint (e.g., `tools/list`), including the token in the `Authorization: Bearer <token>` header.
    -   If the token is valid, the client will receive a `200 OK` response from the MCP server. We will also test the negative case by sending a tampered or incorrect token to ensure the server correctly rejects it. 