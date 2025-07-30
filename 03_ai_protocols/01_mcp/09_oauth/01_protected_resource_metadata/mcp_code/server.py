"""MCP server demonstrating Protected Resource Metadata."""

import datetime
import logging
from typing import Any

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp.server import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier

logger = logging.getLogger(__name__)

class DemoTokenVerifier(TokenVerifier):
    """
    Demo token verifier that always rejects tokens.

    This verifier is used to demonstrate the Protected Resource Metadata flow
    where the client first discovers the authorization server before attempting
    to authenticate.
    """

    async def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify the token.

        This implementation always returns None to demonstrate the 401 flow
        that triggers Protected Resource Metadata discovery.
        """
        logger.info(
            "Demo verifier rejecting token to demonstrate discovery flow")
        return None


class ServerSettings(BaseSettings):
    """Settings for the Protected Resource Metadata demo server."""

    # Server settings
    host: str = "localhost"
    port: int = 8001
    server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    # Authorization Server settings
    auth_server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:9000")

    # OAuth settings
    required_scope: str = "mcp:read"


# Create token verifier (always rejects to demonstrate discovery)
token_verifier = DemoTokenVerifier()

settings = ServerSettings()

# Create FastMCP server as a Resource Server
app = FastMCP(
    name="Protected Resource MCP Server",
    instructions="Demonstrates Protected Resource Metadata for AS discovery",
    host=settings.host,
    port=settings.port,
    debug=True,
    # Configure auth settings
    token_verifier=token_verifier,
    auth=AuthSettings(
        issuer_url=settings.auth_server_url,  # Points to our mock AS
        required_scopes=[settings.required_scope],
        resource_server_url=settings.server_url,  # Required for RFC 9728
    ),
    stateless_http=True,
)

@app.tool()
async def get_time() -> dict[str, Any]:
    """
    Get the current server time.

    This protected tool requires authentication to demonstrate
    the OAuth discovery and authentication flow.
    """
    now = datetime.datetime.now()
    return {
        "current_time": now.isoformat(),
        "timezone": "UTC",
        "timestamp": now.timestamp(),
    }
    
mcp_app = app.streamable_http_app()