# 06: OAuth Error Handling

**Objective:** Implement robust error handling for the common failure modes in an OAuth 2.1 flow.

A production-ready application must gracefully handle incorrect, expired, or insufficient credentials. This lesson focuses on the client's ability to interpret specific OAuth errors returned by the MCP server and take appropriate action.

## Key OAuth Concepts

-   **`WWW-Authenticate` Header:** This header is key to error communication. A secure Resource Server (our MCP server) uses it to provide details about why a request failed.
-   **`error` and `error_description` Parameters:** The `WWW-Authenticate` header can include standardized error codes (e.g., `invalid_token`, `insufficient_scope`) and a human-readable description.
-   **`invalid_token` (RFC 6750):** A standard error indicating that the provided access token is expired, malformed, or has been revoked. The client's correct response is to discard the token and attempt to acquire a new one (e.g., by re-running the Authorization Code Flow or using a refresh token).
-   **`insufficient_scope` (RFC 6750):** An error indicating that the token is valid, but it does not grant permission for the specific operation the client requested. For example, the user may have only granted "read" access, but the client is attempting to "write".

## Implementation Plan

-   **`authorization_server_mock.py`:**
    -   The mock AS will be updated to optionally issue tokens with limited scopes or short expiry times to facilitate testing these error conditions.

-   **`mcp_server.py`:**
    -   The server's security middleware will be enhanced to detect these specific conditions:
        -   If a token is expired, it will return a `401 Unauthorized` with `error="invalid_token"`.
        -   We will simulate a "scoped" tool and if a token without the required scope is used, the server will return a `403 Forbidden` with `error="insufficient_scope"`.

-   **`client.py`:**
    -   The client's request logic will be wrapped in a `try...except` block or similar structure to handle HTTP errors.
    -   **Scenario 1 (Invalid Token):**
        -   The client will attempt to use an expired token.
        -   It will catch the `401` error, parse the `WWW-Authenticate` header, and identify the `invalid_token` error.
        -   It will then print a message like "Token is invalid, starting re-authentication..." and trigger the full auth flow again.
    -   **Scenario 2 (Insufficient Scope):**
        -   The client will use a valid token with limited scope to call a protected tool.
        -   It will catch the `403` error, identify the `insufficient_scope` error, and print an informative message to the user, such as "You have not granted permission for this action." 