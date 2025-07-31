"""
Simple OAuth Authorization Server for educational purposes.

This server implements RFC 8414 Authorization Server Metadata 
and provides mock endpoints for OAuth flows.
"""

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class AuthServerSettings(BaseSettings):
    """Settings for the Authorization Server."""

    host: str = "localhost"
    port: int = 9000
    base_url: AnyHttpUrl = AnyHttpUrl("http://localhost:9000")


settings = AuthServerSettings()

# Create FastAPI app for Authorization Server
app = FastAPI(
    title="Demo Authorization Server",
    description="OAuth 2.1 Authorization Server for MCP OAuth demonstration",
    version="1.0.0"
)


@app.get("/.well-known/oauth-authorization-server")
async def authorization_server_metadata():
    """
    OAuth 2.0 Authorization Server Metadata (RFC 8414).

    This endpoint provides clients with the Authorization Server's configuration,
    including all available endpoints for OAuth flows.
    """
    base_url = str(settings.base_url)

    metadata = {
        # Required fields (RFC 8414)
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",

        # Optional but recommended fields
        "jwks_uri": f"{base_url}/.well-known/jwks.json",
        "registration_endpoint": f"{base_url}/oauth/register",
        "scopes_supported": ["mcp:read", "mcp:write", "mcp:tools"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],

        # Security-related metadata
        "code_challenge_methods_supported": ["S256"],
        "introspection_endpoint": f"{base_url}/oauth/introspect",
        "revocation_endpoint": f"{base_url}/oauth/revoke",

        # Additional metadata for this demo
        "service_documentation": "https://modelcontextprotocol.io/specification/basic/authorization",
        "ui_locales_supported": ["en-US"],
    }

    logger.info("📋 Serving Authorization Server metadata")
    return JSONResponse(
        content=metadata,
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
        }
    )


@app.get("/oauth/authorize")
async def authorize():
    """
    OAuth 2.0 Authorization Endpoint (mock implementation).

    In a real implementation, this would handle user authentication
    and consent, then redirect back to the client with an authorization code.
    """
    logger.info("🔐 Authorization endpoint accessed")
    return {
        "message": "Mock authorization endpoint - not yet implemented",
        "note": "This would normally redirect to a login page or return an authorization code"
    }


@app.post("/oauth/token")
async def token():
    """
    OAuth 2.0 Token Endpoint (mock implementation).

    In a real implementation, this would exchange authorization codes
    or client credentials for access tokens.
    """
    logger.info("🎫 Token endpoint accessed")
    return {
        "message": "Mock token endpoint - not yet implemented",
        "note": "This would normally return access tokens, refresh tokens, etc."
    }


@app.post("/oauth/register")
async def register():
    """
    OAuth 2.0 Dynamic Client Registration (mock implementation).

    In a real implementation, this would allow clients to dynamically
    register themselves with the Authorization Server.
    """
    logger.info("📝 Registration endpoint accessed")
    return {
        "message": "Mock registration endpoint - not yet implemented",
        "note": "This would normally handle dynamic client registration"
    }


@app.get("/.well-known/jwks.json")
async def jwks():
    """
    JSON Web Key Set endpoint (mock implementation).

    In a real implementation, this would provide the public keys
    used to verify JWT access tokens.
    """
    logger.info("🔑 JWKS endpoint accessed")
    return {
        "keys": [],
        "message": "Mock JWKS endpoint - not yet implemented",
        "note": "This would normally contain public keys for token verification"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "OAuth Authorization Server (Demo)",
        "base_url": str(settings.base_url)
    }
