"""
Enhanced OAuth client demonstrating two-stage metadata discovery.

This client demonstrates both:
1. Step 01: Protected Resource Metadata discovery (RFC 9728)
2. Step 02: Authorization Server Metadata discovery (RFC 8414)

The complete flow shows how an MCP client discovers OAuth endpoints
in the two-stage process required by the MCP specification.
"""

import asyncio
import json
import logging
import httpx

from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


async def discover_auth_server() -> dict[str, Any]:
    """
    Step 01: Discover the Authorization Server from MCP server metadata.

    This demonstrates the RFC 9728 Protected Resource Metadata flow:
    1. Make an unauthenticated JSON-RPC request to the MCP server.
    2. Expect a 401 response with a WWW-Authenticate header.
    3. Fetch the /.well-known/oauth-protected-resource metadata.
    4. Parse the metadata to find the Authorization Server URL.
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Make an unauthenticated JSON-RPC request
        mcp_endpoint = "http://localhost:8000/mcp/"
        logger.info(
            f"🔍 Step 01: Making unauthenticated JSON-RPC request to {mcp_endpoint}")

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "1",
        }

        response = await client.post(mcp_endpoint, json=payload)

        # Step 2: Check for 401 with WWW-Authenticate header
        if response.status_code != 401:
            logger.error(
                f"Expected 401 response, but got {response.status_code}: {response.text}")
            raise Exception(
                f"Expected 401 response, but got {response.status_code}: {response.text}"
            )

        auth_header = response.headers.get("WWW-Authenticate", "")
        if not auth_header.startswith("Bearer"):
            raise Exception(
                "Expected Bearer challenge in WWW-Authenticate header")
        logger.info("✅ Received 401 with correct WWW-Authenticate header")

        # Step 3: Fetch Protected Resource metadata
        metadata_url = "http://localhost:8000/.well-known/oauth-protected-resource"
        logger.info(
            f"📋 Fetching Protected Resource metadata from {metadata_url}")

        response = await client.get(metadata_url)
        response.raise_for_status()

        metadata = response.json()
        logger.info("✅ Step 01 Complete: Found Protected Resource metadata")
        logger.info(json.dumps(metadata, indent=2))

        return metadata


async def discover_auth_server_endpoints(auth_server_url: str) -> dict[str, Any]:
    """
    Step 02: Discover Authorization Server endpoints and capabilities.

    This demonstrates the RFC 8414 Authorization Server Metadata flow:
    1. Take the Authorization Server URL from Step 01
    2. Fetch the /.well-known/oauth-authorization-server metadata
    3. Parse the metadata to discover specific OAuth endpoints
    4. Extract endpoint URLs for future OAuth operations
    """
    async with httpx.AsyncClient() as client:
        # Construct metadata URL from Authorization Server URL
        metadata_url = f"{auth_server_url}.well-known/oauth-authorization-server"
        logger.info(
            f"🔍 Step 02: Fetching Authorization Server metadata from {metadata_url}")

        response = await client.get(metadata_url)
        response.raise_for_status()

        metadata = response.json()
        logger.info("✅ Step 02 Complete: Found Authorization Server metadata")
        logger.info(json.dumps(metadata, indent=2))

        return metadata


async def run_complete_discovery():
    """Run the complete two-stage OAuth discovery flow."""
    try:
        print("🚀 Starting OAuth Discovery Flow")
        print("=" * 60)

        # Stage 1: Discover WHERE the Authorization Server is
        print("\n📍 STAGE 1: Protected Resource Metadata Discovery")
        print("Goal: Find the Authorization Server URL")
        print("-" * 40)

        protected_resource_metadata = await discover_auth_server()
        auth_server_url = protected_resource_metadata["authorization_servers"][0]

        print(
            f"\n🎯 Stage 1 Result: Authorization Server located at {auth_server_url}")

        # Stage 2: Discover WHAT the Authorization Server can do
        print("\n📍 STAGE 2: Authorization Server Metadata Discovery")
        print("Goal: Find the specific OAuth endpoints")
        print("-" * 40)

        auth_server_metadata = await discover_auth_server_endpoints(auth_server_url)

        # Extract key endpoints
        authorization_endpoint = auth_server_metadata.get(
            "authorization_endpoint")
        token_endpoint = auth_server_metadata.get("token_endpoint")
        registration_endpoint = auth_server_metadata.get(
            "registration_endpoint")
        jwks_uri = auth_server_metadata.get("jwks_uri")

        print(f"\n🎯 Stage 2 Results: OAuth endpoints discovered")

        # Summary
        print("\n" + "=" * 60)
        print("🎉 SUCCESS: Complete OAuth Discovery Flow")
        print("=" * 60)
        print("Now you know:")
        print(f"  🏠 MCP Resource Server: http://localhost:8000")
        print(f"  🔐 Authorization Server: {auth_server_url}")
        print(f"  📝 Authorization Endpoint: {authorization_endpoint}")
        print(f"  🎫 Token Endpoint: {token_endpoint}")
        print(f"  📋 Registration Endpoint: {registration_endpoint}")
        print(f"  🔑 JWKS Endpoint: {jwks_uri}")
        print("\nNext steps:")
        print("  1. Register a client (if using dynamic registration)")
        print("  2. Redirect user to authorization endpoint")
        print("  3. Exchange authorization code for access token")
        print("  4. Make authenticated requests to MCP server")
        print("=" * 60)

    except Exception as e:
        logger.error(f"❌ Discovery failed: {e}")
        raise


def main():
    """Run the OAuth client discovery demo."""
    asyncio.run(run_complete_discovery())


if __name__ == "__main__":
    main()
