# 02: Authorization Server Discovery

**Objective:** Building on the previous lesson, teach the client how to perform full Authorization Server (AS) discovery.

Once the client knows the `issuer` URL of the AS (from the MCP server's metadata), it must then query the AS to discover all *its* capabilities, such as the endpoints for authorization, token exchange, and client registration.

## Key MCP and OAuth Concepts

-   **OpenID Connect Discovery (`/.well-known/openid-configuration`):** This is the standard endpoint where an Authorization Server publishes its own metadata.
-   **AS Metadata:** This crucial JSON document contains all the URLs a client needs to interact with the AS, including:
    -   `authorization_endpoint`: Where to send the user for login and consent.
    -   `token_endpoint`: Where to exchange an authorization code for an access token.
    -   `registration_endpoint`: Where a new client can dynamically register itself.
    -   `jwks_uri`: Where the public keys are located for verifying token signatures.
-   **Client State:** The client needs to fetch, parse, and store this AS metadata to configure itself for the subsequent steps of the OAuth flow.

## Implementation Plan

This lesson refines and extends the code from the previous step.

-   **`authorization_server_mock.py`:**
    -   The mock AS will already have the `/.well-known/openid-configuration` endpoint from the last lesson. We will ensure it is complete and contains all the necessary URLs for the upcoming lessons (`authorization_endpoint`, `token_endpoint`, etc.).

-   **`mcp_server.py`:**
    -   No changes are needed for the MCP server in this step. It continues to serve its metadata pointing to the AS.

-   **`client.py`:**
    -   The client will perform the discovery process from the previous lesson to get the AS `issuer` URL.
    -   **New Step:** It will then construct the OpenID Connect discovery URL (e.g., `https://my-auth-server.com/.well-known/openid-configuration`).
    -   It will make a `GET` request to this URL on the Authorization Server.
    -   It will parse the resulting JSON and print out the key endpoints it has discovered (e.g., "Discovered Token Endpoint: ..."), demonstrating it has all the information needed to proceed. 