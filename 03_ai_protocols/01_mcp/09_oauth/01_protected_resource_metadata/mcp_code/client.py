"""Client demonstrating Protected Resource Metadata discovery."""

import asyncio
import json
import logging
import httpx

from typing import Any

logger = logging.getLogger(__name__)

async def discover_auth_server() -> dict[str, Any]:
    """
    Discover the Authorization Server from MCP server metadata.

    This demonstrates the RFC 9728 Protected Resource Metadata flow:
    1. Make an unauthenticated JSON-RPC request to the MCP server.
    2. Expect a 401 response with a WWW-Authenticate header.
    3. Fetch the /.well-known/oauth-protected-resource metadata.
    4. Parse the metadata to find the Authorization Server URL.
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Make an unauthenticated JSON-RPC request
        mcp_endpoint = "http://localhost:8000/mcp/"
        logger.info(f"Making unauthenticated JSON-RPC request to {mcp_endpoint}")

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "1",
        }

        response = await client.post(mcp_endpoint, json=payload)
        print(response.json())

        # Step 2: Check for 401 with WWW-Authenticate header
        if response.status_code != 401:
            raise Exception(
                f"Expected 401 response, but got {response.status_code}: {response.text}"
            )

        auth_header = response.headers.get("WWW-Authenticate", "")
        if not auth_header.startswith("Bearer"):
            raise Exception("Expected Bearer challenge in WWW-Authenticate header")
        logger.info("✅ Received 401 with correct WWW-Authenticate header.")

        # Step 3: Fetch metadata
        metadata_url = "http://localhost:8000/.well-known/oauth-protected-resource"
        logger.info(f"Fetching Protected Resource metadata from {metadata_url}")

        response = await client.get(metadata_url)
        response.raise_for_status()

        metadata = response.json()
        logger.info("✅ Found Protected Resource metadata:")
        logger.info(json.dumps(metadata, indent=2))

        return metadata


async def run_discovery():
    """Run the discovery flow."""
    try:
        # Step 1: Discover auth server
        metadata = await discover_auth_server()
        auth_server_url = metadata["authorization_servers"][0]

        logger.info("-" * 40)
        logger.info(
            f"🎉 Success! Discovered Authorization Server: {auth_server_url}")
        logger.info("-" * 40)

    except Exception as e:
        logger.error(f"An error occurred: {e}")


def main():
    """Run the OAuth client discovery demo."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_discovery())


if __name__ == "__main__":
    main()
