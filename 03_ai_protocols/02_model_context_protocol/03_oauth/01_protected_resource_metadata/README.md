# 01: Protected Resource Metadata

## What You Will Learn in This Step

This first step focuses on **Protected Resource Metadata Discovery** as defined in [RFC 9728](https://datatracker.ietf.org/doc/rfc9728/).

You are implementing the **first half** of the two-stage OAuth discovery process. The goal is to understand how an MCP server, acting as a "Protected Resource," advertises its security requirements and tells clients where to find the Authorization Server.

By the end of this lesson, you will understand and have implemented the following flow:
1. A client makes a request to a protected tool without a token
2. The MCP server rejects it with a `401 Unauthorized` error
3. The client inspects the `WWW-Authenticate` header in the error response
4. The client fetches the server's metadata file (`/.well-known/oauth-protected-resource`)
5. From this file, the client learns the **URL** of the Authorization Server (`http://localhost:9000`)

**Note:** This step only discovers the Authorization Server's location. Step 02 will query that server to learn its specific endpoints.

---

## Learning Objectives

After completing this module, you will be able to:
1. Implement Protected Resource Metadata according to MCP specification
2. Understand the first stage of the OAuth 2.1 discovery process
3. See how a client discovers an Authorization Server's location

## Standards Compliance

This implementation follows these specifications:
- [MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OAuth 2.1](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)
- [OAuth 2.0 Protected Resource Metadata (RFC 9728)](https://datatracker.ietf.org/doc/rfc9728/)

## Prerequisites

- Basic understanding of HTTP and REST APIs
- Experience with Python

## Core Concepts

### 1. Protected Resource Metadata (RFC 9728)
- **Purpose**: Standardizes how clients discover OAuth configuration from Resource Servers
- **Requirements**:
  - MCP servers MUST expose `/.well-known/oauth-protected-resource`
  - Document MUST include `authorization_servers` field
  - Servers MUST use `WWW-Authenticate` header for 401 responses
  - Clients MUST parse `WWW-Authenticate` headers

### 2. First Stage of Discovery Flow
- **What happens**:
  1. Client makes unauthenticated JSON-RPC request to MCP server
  2. Server responds with 401 + `WWW-Authenticate` header
  3. Client fetches `/.well-known/oauth-protected-resource` from MCP server
  4. Client extracts Authorization Server URL from metadata

### 3. Resource Parameter Implementation
- **Requirements**:
  - Clients MUST include `resource` parameter in future token requests
  - Parameter MUST identify target MCP server
  - Must use canonical URI format
  ```
  &resource=https%3A%2F%2Fmcp.example.com
  ```

### 4. Token Requirements (For Later Steps)
- **Bearer Token Usage**:
  ```http
  POST /mcp HTTP/1.1
  Host: mcp.example.com
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
  ```
- Tokens MUST NOT be in URI query string
- Authorization required for every request

## Implementation Guide

### Running the Demo
1. **Start the MCP Server:** In one terminal, from the `mcp_code` directory, run:
   ```bash
   uv run uvicorn serve:mcp_app --reload
   ```
2. **Run the Client:** In a second terminal, from the `mcp_code` directory, run:
   ```bash
   uv run client.py
   ```

The client's output will show:
1. The `401 Unauthorized` response from the unauthenticated request
2. The metadata document it fetched from `/.well-known/oauth-protected-resource`
3. The discovered Authorization Server URL: `http://localhost:9000`

## Next Steps

With the Authorization Server URL discovered, step 02 will:
1. **Create a simple Authorization Server** at `http://localhost:9000`
2. **Query its metadata endpoint** (`/.well-known/oauth-authorization-server`) to discover specific endpoints
3. **Complete the two-stage discovery process** required by the MCP specification

This two-stage approach allows Authorization Servers to serve multiple MCP servers while maintaining clear separation of concerns.

## Resources

- [MCP Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- [OAuth 2.1 Specification](https://oauth.net/2.1/)
- [RFC 9728 - Protected Resource Metadata](https://datatracker.ietf.org/doc/rfc9728/)

