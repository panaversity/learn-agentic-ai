# 02: Authorization Server Metadata

**Objective:** Create a simple OAuth Authorization Server and demonstrate how clients discover its capabilities through the `/.well-known/oauth-authorization-server` endpoint.

Building on step 01 where we discovered the Authorization Server's URL (`http://localhost:9000`), this step implements the second half of the discovery process: querying the Authorization Server itself to learn about its specific endpoints and capabilities.

## What You Will Learn in This Step

This step focuses on **Authorization Server Metadata Discovery** as defined in [RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414).

By the end of this lesson, you will understand and have implemented:
1. A simple OAuth Authorization Server that serves metadata at `/.well-known/oauth-authorization-server`
2. A client that queries this endpoint to discover the server's capabilities
3. The two-stage discovery process required by the MCP specification

## Key OAuth Concepts

-   **Authorization Server Metadata (RFC 8414):** A standardized JSON document that tells clients about the Authorization Server's endpoints and capabilities
-   **`/.well-known/oauth-authorization-server`:** The standard endpoint where this metadata is served
-   **Endpoint Discovery:** How clients learn the specific URLs for:
    -   `authorization_endpoint`: Where to send users for login and consent
    -   `token_endpoint`: Where to exchange authorization codes for access tokens
    -   `registration_endpoint`: Where clients can register themselves dynamically
    -   `jwks_uri`: Where to find public keys for token verification

## Two-Server Discovery Flow

This step completes the two-stage discovery process:

1. **Step 01 (✅ Completed):** Client queries MCP server at `/.well-known/oauth-protected-resource` and learns the Authorization Server is at `http://localhost:9000`
2. **Step 02 (This step):** Client queries Authorization Server at `/.well-known/oauth-authorization-server` and learns the specific endpoints for registration, authorization, and token exchange

## Implementation Plan

This lesson builds two components:

-   **`authorization_server.py`:** A minimal OAuth Authorization Server that:
    -   Runs on `http://localhost:9000` 
    -   Serves the `/.well-known/oauth-authorization-server` metadata endpoint
    -   Provides mock endpoints for future lessons (registration, authorization, token)

-   **`client.py`:** An enhanced client that:
    1.  Performs the step 01 discovery flow (finds Authorization Server URL)
    2.  **New:** Queries the Authorization Server's metadata endpoint
    3.  **New:** Parses and displays the discovered endpoint information

## Running the Demo

1. **Start the MCP Server** (from step 01):
   ```bash
   cd ../01_protected_resource_metadata/mcp_code
   mcp-oauth-rs
   ```

2. **Start the Authorization Server** (new):
   ```bash
   cd mcp_code
   python authorization_server.py
   ```

3. **Run the Enhanced Client** (new):
   ```bash
   python client.py
   ```

The client will demonstrate the complete two-stage discovery flow, showing both the MCP server's protected resource metadata and the Authorization Server's endpoint metadata.

## Next Steps

With both discovery stages complete, the next lessons will use these discovered endpoints to:
1. **Register the client** with the Authorization Server using the `registration_endpoint`
2. **Implement the authorization flow** using the `authorization_endpoint` and `token_endpoint`
3. **Validate tokens** using the `jwks_uri` 