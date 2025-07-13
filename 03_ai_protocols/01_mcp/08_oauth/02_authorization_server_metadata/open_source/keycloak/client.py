#!/usr/bin/env python3
"""
OAuth Discovery Client for Keycloak - Production Implementation.

This client demonstrates OAuth discovery against a real Keycloak server,
showing the production-ready approach to MCP OAuth integration.
"""

import asyncio
import logging
import httpx
import json
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KeycloakDiscoveryClient:
    """Client that performs OAuth discovery with Keycloak."""

    def __init__(self, realm: str = "mcp-oauth"):
        self.mcp_server_url = "http://localhost:8000"
        self.keycloak_base_url = "http://localhost:9000"
        self.realm = realm
        self.auth_server_url = f"{self.keycloak_base_url}/realms/{realm}"
        self.auth_metadata = None
        self.mcp_metadata = None

    async def check_keycloak_health(self) -> bool:
        """Check if Keycloak is running and healthy."""
        try:
            async with httpx.AsyncClient() as client:
                # Test if realm endpoint is accessible instead of health endpoint
                response = await client.get(f"{self.auth_server_url}", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ Keycloak realm is accessible")
                    return True
                else:
                    logger.warning(
                        f"⚠️ Keycloak realm check failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Keycloak not reachable: {e}")
            return False

    async def discover_mcp_metadata(self) -> Optional[Dict[str, Any]]:
        """Discover MCP server's protected resource metadata."""
        logger.info("🔍 Stage 1: Discovering MCP Protected Resource Metadata")

        async with httpx.AsyncClient() as client:
            # First, try unauthenticated request to see the 401 response
            try:
                logger.info(
                    f"📡 Making unauthenticated request to MCP server: {self.mcp_server_url}/mcp")
                response = await client.post(
                    f"{self.mcp_server_url}/mcp",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": "1"
                    },
                    timeout=5.0
                )

                if response.status_code == 401:
                    logger.info(
                        "✅ Received expected 401 Unauthorized response")
                    www_auth = response.headers.get('WWW-Authenticate', '')
                    logger.info(f"🔐 WWW-Authenticate header: {www_auth}")
            except Exception as e:
                logger.info(f"📡 MCP request failed (expected): {e}")

            # Fetch protected resource metadata
            metadata_url = f"{self.mcp_server_url}/.well-known/oauth-protected-resource"
            logger.info(f"📋 Fetching MCP metadata: {metadata_url}")

            response = await client.get(metadata_url)
            if response.status_code == 200:
                self.mcp_metadata = response.json()
                logger.info("✅ Successfully retrieved MCP server metadata")
                return self.mcp_metadata
            else:
                raise Exception(
                    f"Failed to fetch MCP metadata: {response.status_code}")

    async def discover_keycloak_metadata(self) -> Optional[Dict[str, Any]]:
        """Discover Keycloak's authorization server metadata."""
        logger.info(
            "🔍 Stage 2: Discovering Keycloak Authorization Server Metadata")

        async with httpx.AsyncClient() as client:
            # Keycloak's OAuth 2.1 authorization server metadata endpoint
            metadata_url = f"{self.auth_server_url}/.well-known/oauth-authorization-server"
            logger.info(f"📋 Fetching Keycloak metadata: {metadata_url}")

            response = await client.get(metadata_url)
            if response.status_code == 200:
                self.auth_metadata = response.json()
                logger.info("✅ Successfully retrieved Keycloak metadata")
                return self.auth_metadata
            else:
                raise Exception(
                    f"Failed to fetch Keycloak metadata: {response.status_code}")

    async def test_dynamic_registration(self) -> Optional[Dict[str, Any]]:
        """Test dynamic client registration with Keycloak."""
        if not self.auth_metadata:
            raise Exception("Must discover auth server metadata first")

        registration_endpoint = self.auth_metadata.get('registration_endpoint')
        if not registration_endpoint:
            logger.warning(
                "⚠️ Dynamic registration not supported by this Keycloak configuration")
            return None

        logger.info("🔍 Testing Dynamic Client Registration")

        # Client registration request per RFC 7591
        registration_data = {
            "client_name": "MCP Dynamic Client",
            "client_uri": "http://localhost:8888",
            "redirect_uris": ["http://localhost:8888/callback"],
            "grant_types": ["authorization_code", "client_credentials"],
            "response_types": ["code"],
            "scope": "openid mcp:read mcp:write",
            "token_endpoint_auth_method": "client_secret_post"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    registration_endpoint,
                    json=registration_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 201:
                    registration_response = response.json()
                    logger.info("✅ Dynamic client registration successful")
                    return registration_response
                else:
                    logger.warning(
                        f"⚠️ Dynamic registration failed: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                logger.warning(f"⚠️ Dynamic registration error: {e}")
                return None

    def display_discovery_results(self, registration_data: Optional[Dict[str, Any]] = None):
        """Display comprehensive discovery results."""
        print("\n" + "="*80)
        print("🎉 KEYCLOAK OAUTH DISCOVERY COMPLETE")
        print("="*80)

        # MCP Server Results
        print("\n📋 STAGE 1: MCP Server Protected Resource Metadata")
        print("-" * 60)
        if self.mcp_metadata:
            print(f"🌐 MCP Server: {self.mcp_server_url}")
            auth_servers = self.mcp_metadata.get('authorization_servers', [])
            print(f"🔐 Authorization Servers: {auth_servers}")
            if 'resource_server' in self.mcp_metadata:
                print(
                    f"📝 Resource Server: {self.mcp_metadata['resource_server']}")

        # Keycloak Results
        print(f"\n📋 STAGE 2: Keycloak Authorization Server Metadata")
        print("-" * 60)
        if self.auth_metadata:
            print(f"🏢 Issuer: {self.auth_metadata.get('issuer')}")
            print(
                f"🔐 Authorization Endpoint: {self.auth_metadata.get('authorization_endpoint')}")
            print(
                f"🎫 Token Endpoint: {self.auth_metadata.get('token_endpoint')}")
            print(
                f"📝 Registration Endpoint: {self.auth_metadata.get('registration_endpoint', 'Not available')}")
            print(f"🔑 JWKS URI: {self.auth_metadata.get('jwks_uri')}")
            print(
                f"👤 UserInfo Endpoint: {self.auth_metadata.get('userinfo_endpoint')}")
            print(
                f"🚪 End Session Endpoint: {self.auth_metadata.get('end_session_endpoint')}")

            # Supported features
            scopes = self.auth_metadata.get('scopes_supported', [])
            grant_types = self.auth_metadata.get('grant_types_supported', [])
            response_types = self.auth_metadata.get(
                'response_types_supported', [])

            print(f"\n🛠️ KEYCLOAK CAPABILITIES:")
            print(
                f"   Scopes: {', '.join(scopes[:10])}{'...' if len(scopes) > 10 else ''}")
            print(f"   Grant Types: {', '.join(grant_types)}")
            print(f"   Response Types: {', '.join(response_types)}")

            # Token endpoint auth methods
            auth_methods = self.auth_metadata.get(
                'token_endpoint_auth_methods_supported', [])
            if auth_methods:
                print(f"   Token Auth Methods: {', '.join(auth_methods)}")

        # Registration Results
        if registration_data:
            print(f"\n📝 STAGE 3: Dynamic Client Registration")
            print("-" * 60)
            print(f"✅ Registration successful!")
            print(f"🆔 Client ID: {registration_data.get('client_id')}")
            print(f"🔐 Client Secret: {'*' * 20} (hidden)")
            print(
                f"📅 Issued At: {registration_data.get('client_id_issued_at', 'N/A')}")
            print(
                f"⏰ Expires At: {registration_data.get('client_secret_expires_at', 'Never')}")

        # Next steps
        print(f"\n🚀 PRODUCTION FEATURES AVAILABLE:")
        print("   ✅ Real user authentication (username: mcpuser, password: password123)")
        print("   ✅ Proper JWT token signing and validation")
        print("   ✅ PKCE support for public clients")
        print("   ✅ Refresh tokens for long-lived sessions")
        print("   ✅ Admin console at http://localhost:9000/admin")
        print("   ✅ Built-in security: brute force protection, session management")
        print("   ✅ Production ready: clustering, database persistence, HTTPS")

        print(f"\n🔧 KEYCLOAK ADMIN ACCESS:")
        print("   URL: http://localhost:9000/admin")
        print("   Username: admin")
        print("   Password: admin123")
        print("="*80)

    async def run_full_discovery(self):
        """Run the complete discovery process with Keycloak."""
        try:
            # Check Keycloak health first
            if not await self.check_keycloak_health():
                print("\n💥 Keycloak Error: Server not running or unhealthy")
                print("\n🔧 To start Keycloak:")
                print("   cd open_source/keycloak")
                print("   docker-compose up -d")
                print("   docker-compose logs -f keycloak  # to monitor startup")
                return

            # Stage 1: MCP metadata discovery
            await self.discover_mcp_metadata()

            # Stage 2: Keycloak metadata discovery
            await self.discover_keycloak_metadata()

            # Stage 3: Test dynamic registration (optional)
            registration_data = await self.test_dynamic_registration()

            # Display comprehensive results
            self.display_discovery_results(registration_data)

        except Exception as e:
            logger.error(f"❌ Discovery failed: {e}")
            print(f"\n💥 Discovery Error: {e}")
            print("\n🔧 Troubleshooting:")
            print("   1. Start Keycloak: docker-compose up -d")
            print("   2. Wait for startup: docker-compose logs -f keycloak")
            print("   3. Ensure MCP server is running on http://localhost:8000")
            print("   4. Check Keycloak admin console: http://localhost:9000/admin")


async def main():
    """Main function to run the Keycloak discovery demo."""
    print("🚀 OAuth 2.0 Discovery with Keycloak (Production)")
    print("=" * 80)
    print("This demo shows OAuth discovery using a real Keycloak server:")
    print("• RFC 9728 - Protected Resource Metadata Discovery")
    print("• RFC 8414 - Authorization Server Metadata Discovery")
    print("• RFC 7591 - Dynamic Client Registration (optional)")
    print("• OIDC Discovery with full production features")
    print("=" * 80)

    client = KeycloakDiscoveryClient()
    await client.run_full_discovery()


if __name__ == "__main__":
    asyncio.run(main())
