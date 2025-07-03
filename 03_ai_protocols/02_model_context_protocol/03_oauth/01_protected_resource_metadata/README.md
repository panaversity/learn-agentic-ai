# 01: Protected Resource Metadata

**Objective:** Configure an MCP server to advertise itself as an OAuth 2.1 protected resource, as required by the MCP specification.

This is the very first step in making a secure MCP server. Before a client can even attempt to authenticate, it needs a standardized way to discover the server's security requirements and the location of the Authorization Server (AS) that governs it.

## Key MCP and OAuth Concepts

-   **OAuth Resource Server:** An MCP server acts as a Resource Server in the OAuth 2.1 model. Its API (tools, resources, etc.) is the protected resource.
-   **Authorization Server (AS):** The entity that issues access tokens for the Resource Server.
-   **Resource Metadata (`/.well-known/oauth-authorization-server`):** An MCP server **MUST** expose a document at this well-known URI. This document tells clients the `issuer` URL of the Authorization Server responsible for this MCP server.
-   **`WWW-Authenticate` Header:** When a client makes an unauthenticated request, the MCP server should respond with a `401 Unauthorized` status and this header, pointing to the location of its AS metadata. This provides a discovery mechanism for clients.

## Implementation Plan

-   **`authorization_server_mock.py`:**
    -   We will create a very simple, mock Authorization Server using FastAPI.
    -   It will expose an endpoint at `/.well-known/openid-configuration` which contains its own metadata, including its `issuer` and `token_endpoint`.

-   **`mcp_server.py`:**
    -   We will configure our `FastMCP` server to be "protected."
    -   It will automatically host a `/.well-known/oauth-authorization-server` endpoint. This endpoint will contain a JSON object pointing to our mock AS's issuer URL.
    -   We will add middleware to the MCP server that rejects any request without a valid token and replies with a `401 Unauthorized` and the correct `WWW-Authenticate` header.

-   **`client.py`:**
    -   The client will first make an unauthenticated request to the MCP server.
    -   It will receive a `401` error. It will then parse the `WWW-Authenticate` header to find the metadata URL (`/.well-known/oauth-authorization-server`).
    -   The client will then fetch this metadata URL from the MCP server to discover the URL of the Authorization Server, printing it to confirm success. 