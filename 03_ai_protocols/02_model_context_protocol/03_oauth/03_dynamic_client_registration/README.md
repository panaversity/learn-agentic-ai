# 03: Dynamic Client Registration

**Objective:** Implement the Dynamic Client Registration flow, allowing our MCP client to programmatically register itself with the Authorization Server (AS).

Building on the previous steps where we:
1. **Step 01:** Discovered the Authorization Server URL (`http://localhost:9000`) from the MCP server
2. **Step 02:** Queried the Authorization Server and discovered its `registration_endpoint`

Now we implement the registration process itself. Before a client can ask for an access token, the Authorization Server needs to know who the client is. While some clients have pre-configured credentials, a truly dynamic system allows for on-the-fly registration.

## Key OAuth Concepts

-   **Dynamic Client Registration (RFC 7591):** A protocol that allows an OAuth client to register with an Authorization Server.
-   **Registration Endpoint:** The URL on the AS (discovered in step 02) where clients can `POST` their metadata to register.
-   **Client Metadata:** Information the client provides about itself, such as its name, logo, and—most importantly—its `redirect_uris`.
-   **`redirect_uris`:** A critical security feature. This is a list of URLs where the AS is allowed to send the user back after they log in. The AS will reject any request that uses a redirect URI not on this list.
-   **Client Credentials (`client_id`, `client_secret`):** Upon successful registration, the AS issues a unique `client_id` and an optional `client_secret` to the client. The client **MUST** store these securely and use them to identify itself in future requests to the AS.

## Implementation Plan

-   **`authorization_server.py`:**
    -   The Authorization Server from step 02 will be enhanced to include a `/register` endpoint (the `registration_endpoint`).
    -   This endpoint will accept a `POST` request with client metadata.
    -   It will generate a new `client_id` and `client_secret`, store the client's details (especially its `redirect_uris`), and return the new credentials to the client.

-   **`client.py`:**
    -   The client will perform the two-stage discovery process (from steps 01 and 02) to find the `registration_endpoint`.
    -   **New Step:** It will then craft a JSON payload with its own metadata, including a `redirect_uris` array (e.g., `["http://localhost:8888/callback"]`).
    -   It will `POST` this payload to the `registration_endpoint`.
    -   It will receive the `client_id` and `client_secret` from the AS and store them securely (for this example, in memory).
    -   The client will print a success message confirming that it has been registered and has received its credentials. 

## Prerequisites

Before running this step, you need:
1. The MCP server from step 01 running on `http://localhost:8000`
2. The Authorization Server from step 02 running on `http://localhost:9000`

## Next Steps

With client registration complete, step 04 will use the obtained `client_id` and `client_secret` to implement the full OAuth 2.1 Authorization Code Flow to acquire access tokens. 