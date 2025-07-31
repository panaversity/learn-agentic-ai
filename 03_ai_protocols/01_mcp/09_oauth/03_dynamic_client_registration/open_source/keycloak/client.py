#!/usr/bin/env python3
"""
Step 03: OAuth 2.1 Dynamic Client Registration Demo

This client demonstrates the complete OAuth 2.1 discovery and registration process:
1. Discover MCP server's protected resource metadata
2. Discover Keycloak's authorization server metadata  
3. Register a new OAuth client dynamically using Initial Access Token
4. Receive and store client credentials for future use

Usage:
    # With Initial Access Token from environment
    INITIAL_ACCESS_TOKEN="your-token-here" uv run client.py
    
    # Interactive mode (will prompt for token)
    uv run client.py
"""

import asyncio
import logging
import httpx
import os
import sys
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DynamicClientRegistrationDemo:
    """Client that performs complete OAuth 2.1 discovery and registration with Keycloak."""

    def __init__(self, realm: str = "mcp-oauth"):
        self.mcp_server_url = "http://localhost:8000"
        self.keycloak_base_url = "http://localhost:9000"
        self.realm = realm
        self.auth_server_url = f"{self.keycloak_base_url}/realms/{realm}"
        self.auth_metadata = None
        self.mcp_metadata = None

        # Client credentials (populated during registration)
        self.client_id = None
        self.client_secret = None
        self.registration_access_token = None
        self.registration_client_uri = None
        self.registration_data = None

    async def discover_mcp_metadata(self) -> Optional[Dict[str, Any]]:
        """Discover MCP server's protected resource metadata."""
        logger.info("🔍 Stage 1: Discovering MCP Protected Resource Metadata")

        async with httpx.AsyncClient() as client:
            # First, try unauthenticated request to see the 401 response
            try:
                logger.info(f"📡 Making unauthenticated request to MCP server: {self.mcp_server_url}/mcp")
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
                    logger.info("✅ Received expected 401 Unauthorized response")
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
                raise Exception(f"Failed to fetch MCP metadata: {response.status_code}")

    async def discover_keycloak_metadata(self) -> Optional[Dict[str, Any]]:
        """Discover Keycloak's authorization server metadata."""
        logger.info("🔍 Stage 2: Discovering Keycloak Authorization Server Metadata")

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
                raise Exception(f"Failed to fetch Keycloak metadata: {response.status_code}")

    async def register_dynamic_client(self, initial_access_token: str) -> Optional[Dict[str, Any]]:
        """
        Perform Dynamic Client Registration with Keycloak per RFC 7591.

        Args:
            initial_access_token: Token created in Keycloak admin console for authorization
        """
        if not self.auth_metadata:
            raise Exception("Must discover auth server metadata first")

        registration_endpoint = self.auth_metadata.get('registration_endpoint')
        if not registration_endpoint:
            logger.warning("⚠️ Dynamic registration not supported by this Keycloak configuration")
            return None

        logger.info("🔍 Stage 3: Dynamic Client Registration")
        logger.info(f"📝 Registration endpoint: {registration_endpoint}")

        # Client metadata per RFC 7591
        registration_data = {
            "client_name": "MCP OAuth Demo Client - Step 03",
            "client_uri": "http://localhost:8888",
            "redirect_uris": [
                "http://localhost:8888/callback",
                "http://127.0.0.1:8888/callback"
            ],
            "grant_types": ["authorization_code", "client_credentials"],
            "response_types": ["code"],
            "scope": "openid mcp:read mcp:write offline_access",
            "token_endpoint_auth_method": "client_secret_post",
            "application_type": "web",
            "contacts": ["admin@localhost"]
        }

        async with httpx.AsyncClient() as client:
            try:
                logger.info("📤 Sending registration request...")
                logger.info(f"🔑 Using Initial Access Token: {initial_access_token[:20]}...")

                response = await client.post(
                    registration_endpoint,
                    json=registration_data,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {initial_access_token}"
                    },
                    timeout=10.0
                )

                logger.info(f"📥 Registration response: {response.status_code}")

                if response.status_code == 201:
                    registration_response = response.json()
                    logger.info("✅ Dynamic client registration successful!")

                    # Store credentials
                    self.client_id = registration_response.get('client_id')
                    self.client_secret = registration_response.get(
                        'client_secret')
                    self.registration_access_token = registration_response.get(
                        'registration_access_token')
                    self.registration_client_uri = registration_response.get(
                        'registration_client_uri')
                    self.registration_data = registration_response

                    return registration_response

                elif response.status_code == 401:
                    logger.error("❌ Registration failed - Unauthorized (401)")
                    logger.info(
                        "💡 Initial Access Token is missing, expired, or invalid")
                    logger.info(
                        "🔧 Create a new token in Keycloak admin console")
                    return None

                elif response.status_code == 403:
                    logger.error("❌ Registration failed - Forbidden (403)")
                    logger.info(
                        "💡 Client Registration Policies are blocking the request")
                    logger.info(
                        "🔧 Use Initial Access Token or check Keycloak policies")
                    return None

                else:
                    logger.error(f"❌ Registration failed with status: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None

            except Exception as e:
                logger.error(f"❌ Registration request failed: {e}")
                return None

    def display_results(self, registration_data: Optional[Dict[str, Any]] = None):
        """Display comprehensive results of the discovery and registration process."""
        print("\n" + "="*80)
        print("🎉 OAUTH 2.1 DISCOVERY AND REGISTRATION COMPLETE!")
        print("="*80)

        # Stage 1: MCP Server Discovery
        print("\n📋 STAGE 1: MCP Server Discovery")
        print("-" * 40)
        if self.mcp_metadata:
            auth_servers = self.mcp_metadata.get('authorization_servers', [])
            print(f"✅ MCP Server: {self.mcp_server_url}")
            print(
                f"📍 Authorization Server: {auth_servers[0] if auth_servers else 'None'}")
            print(f"🔒 Resource Parameter: {self.mcp_server_url}")
        else:
            print("❌ MCP server discovery failed")

        # Stage 2: Authorization Server Discovery
        print("\n📋 STAGE 2: Authorization Server Discovery")
        print("-" * 40)
        if self.auth_metadata:
            print(f"✅ Authorization Server: {self.auth_server_url}")
            print(
                f"🔐 Authorization Endpoint: {self.auth_metadata.get('authorization_endpoint', 'N/A')}")
            print(
                f"🎫 Token Endpoint: {self.auth_metadata.get('token_endpoint', 'N/A')}")
            print(
                f"📝 Registration Endpoint: {self.auth_metadata.get('registration_endpoint', 'N/A')}")
        else:
            print("❌ Authorization server discovery failed")

        # Stage 3: Dynamic Client Registration
        print("\n📋 STAGE 3: Dynamic Client Registration")
        print("-" * 40)
        if registration_data:
            print(f"✅ Registration Status: SUCCESS")
            print(f"🆔 Client ID: {self.client_id}")
            print(f"🔐 Client Secret: {'*' * 20} (hidden for security)")
            print(
                f"📍 Redirect URIs: {', '.join(registration_data.get('redirect_uris', []))}")
            print(f"🎭 Scopes: {registration_data.get('scope', 'N/A')}")
        else:
            print("❌ Dynamic client registration failed")

        # Next Steps
        print("\n📋 NEXT STEPS")
        print("-" * 40)
        if registration_data:
            print("✅ You can now use these credentials for OAuth 2.1 flows:")
            print("   • Authorization Code Flow")
            print("   • Client Credentials Flow")
            print("   • Token Exchange")
            print("   • Access protected MCP resources")
        else:
            print("❌ Registration failed. Check the guidance above.")

        print("\n" + "="*80)

    def get_initial_access_token(self) -> str:
        """Get Initial Access Token from environment or user input."""
        # Check environment variable first
        token = os.getenv('INITIAL_ACCESS_TOKEN')
        if token:
            logger.info("✅ Using Initial Access Token from environment")
            return token

        # Interactive mode
        print("\n🔧 Initial Access Token Required")
        print("=" * 50)
        print("1. Open Keycloak Admin Console: http://localhost:9000/admin")
        print("2. Login with: admin / admin123")
        print("3. Select realm: mcp-oauth")
        print("4. Go to: Clients → Client registration → Initial access tokens")
        print("5. Click 'Create', set expiration (3600s) and count (10)")
        print("6. Copy the token immediately!")
        print()

        token = input("📝 Paste your Initial Access Token: ").strip()
        if not token:
            print("❌ No token provided!")
            sys.exit(1)

        return token

    async def run_full_demo(self):
        """Run the complete OAuth 2.1 discovery and registration demo."""
        try:

            # Get Initial Access Token
            initial_access_token = self.get_initial_access_token()

            # Stage 1: Discover MCP server metadata
            await self.discover_mcp_metadata()

            # Stage 2: Discover Keycloak authorization server metadata
            await self.discover_keycloak_metadata()

            # Stage 3: Register dynamic client
            registration_data = await self.register_dynamic_client(initial_access_token)

            # Display results
            self.display_results(registration_data)

        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise


async def main():
    """Main function to run the OAuth discovery and registration demo."""
    client = DynamicClientRegistrationDemo()
    await client.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
