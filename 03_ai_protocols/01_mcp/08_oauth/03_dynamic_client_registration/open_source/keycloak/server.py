"""
MCP server configured for Keycloak OAuth integration.

This server demonstrates Protected Resource Metadata discovery
pointing to a real Keycloak Authorization Server.
"""

import datetime
import logging
from typing import Any

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp.server import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger(__name__)


class KeycloakTokenVerifier(TokenVerifier):
    """
    Token verifier for Keycloak integration.

    In this demo, it rejects all tokens to demonstrate the discovery flow.
    In a real implementation, this would validate JWT tokens using Keycloak's JWKS endpoint.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify the token against Keycloak.

        This demo implementation always returns None to trigger OAuth discovery.
        In production, this would:
        1. Fetch Keycloak's JWKS from the discovered jwks_uri
        2. Validate the JWT signature and claims
        3. Return AccessToken with user info and scopes
        """
        logger.info(
            "Demo verifier rejecting token to demonstrate Keycloak discovery flow")
        return None


class KeycloakServerSettings(BaseSettings):
    """Settings for MCP server with Keycloak integration."""

    # MCP Server settings
    host: str = "localhost"
    port: int = 8000
    server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000/")

    # Keycloak settings (matching docker-compose configuration)
    keycloak_base_url: AnyHttpUrl = AnyHttpUrl("http://localhost:9000/")
    keycloak_realm: str = "mcp-oauth"

    @property
    def keycloak_issuer_url(self) -> str:
        """Keycloak issuer URL for the configured realm."""
        return f"{self.keycloak_base_url}realms/{self.keycloak_realm}"

    # OAuth settings
    required_scopes: list[str] = ["mcp:read"]


# Create settings
settings = KeycloakServerSettings()

# Create token verifier
token_verifier = KeycloakTokenVerifier()

# Create FastMCP server configured for Keycloak
app = FastMCP(
    name="MCP Server with Keycloak OAuth",
    instructions="Demonstrates OAuth discovery and authentication with production Keycloak server",
    host=settings.host,
    port=settings.port,
    debug=True,
    # Configure auth settings for Keycloak
    token_verifier=token_verifier,
    auth=AuthSettings(
        # Points to Keycloak realm
        issuer_url=AnyHttpUrl(settings.keycloak_issuer_url),
        required_scopes=settings.required_scopes,
        resource_server_url=settings.server_url,  # Required for RFC 9728
    ),
    stateless_http=True,
)


@app.tool()
async def get_time() -> dict[str, Any]:
    """
    Get the current server time.

    This protected tool requires authentication via Keycloak OAuth.
    """
    now = datetime.datetime.now()
    return {
        "current_time": now.isoformat(),
        "timezone": "UTC",
        "timestamp": now.timestamp(),
        "message": "Successfully accessed protected MCP tool via Keycloak OAuth!"
    }


# Export the ASGI application
mcp_app = app.streamable_http_app()

if __name__ == "__main__":
    print("🚀 Starting MCP Server with Keycloak OAuth Integration Run Keycloak Docker Compose first")
    print("=" * 60)
    print(f"📍 MCP Server: {settings.server_url}")
    print(f"🔐 Keycloak Issuer: {settings.keycloak_issuer_url}")
    print(f"🌐 Keycloak Admin: {settings.keycloak_base_url}admin")
    print(f"📋 Protected Resource Metadata: {settings.server_url}.well-known/oauth-protected-resource")
    print(
        f"🔍 Authorization Server Metadata: {settings.keycloak_issuer_url}.well-known/openid_configuration")
    print("=" * 60)
    print("Use: uv run uvicorn server:mcp_app --reload")
    print("=" * 60)
