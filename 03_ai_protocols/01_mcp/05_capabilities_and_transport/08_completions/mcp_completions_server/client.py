#!/usr/bin/env python3
"""
Simple MCP Completions HTTP Client

Demonstrates basic completion requests via streamable HTTP.
Focus on key concepts rather than comprehensive testing.
"""

import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import PromptReference, ResourceTemplateReference


async def test_completions():
    """Test basic MCP completions functionality via HTTP."""

    print("🚀 Starting MCP Completions HTTP Test")
    print("=" * 50)

    server_url = "http://localhost:8000/mcp/"

    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize session
                print("🔌 Connecting to HTTP server...")
                await session.initialize()
                print("✅ Connected!\n")

                # Test 1: Basic language completion
                print("📝 Test 1: Language Completion")
                print("-" * 30)
                result = await session.complete(
                    ref=PromptReference(type="ref/prompt", name="review_code"),
                    argument={"name": "language", "value": "py"}
                )
                print(f"Input: 'py' → Output: {result.completion.values}")

                # Test 2: Focus completion
                print("\n📝 Test 2: Focus Completion")
                print("-" * 30)
                result = await session.complete(
                    ref=PromptReference(type="ref/prompt", name="review_code"),
                    argument={"name": "focus", "value": "sec"}
                )
                print(f"Input: 'sec' → Output: {result.completion.values}")

                # Test 3: Context-aware framework completion
                print("\n📝 Test 3: Context-Aware Framework Completion")
                print("-" * 30)
                result = await session.complete(
                    ref=PromptReference(type="ref/prompt",
                                        name="setup_project"),
                    argument={"name": "framework", "value": "fast"},
                    context_arguments={"language": "python"}
                )
                print(
                    f"Input: 'fast' (language=python) → Output: {result.completion.values}")

                # Test 4: GitHub owner completion
                print("\n📝 Test 4: GitHub Owner Completion")
                print("-" * 30)
                result = await session.complete(
                    ref=ResourceTemplateReference(
                        type="ref/resource",
                        uri="github://repos/{owner}/{repo}"
                    ),
                    argument={"name": "owner", "value": "micro"}
                )
                print(f"Input: 'micro' → Output: {result.completion.values}")

                # Test 5: Context-aware repo completion
                print("\n📝 Test 5: Context-Aware Repo Completion")
                print("-" * 30)
                result = await session.complete(
                    ref=ResourceTemplateReference(
                        type="ref/resource",
                        uri="github://repos/{owner}/{repo}"
                    ),
                    argument={"name": "repo", "value": "type"},
                    context_arguments={"owner": "microsoft"}
                )
                print(
                    f"Input: 'type' (owner=microsoft) → Output: {result.completion.values}")

                print("\n🎉 All tests completed!")
                print("\n💡 Also try the Postman collection for manual HTTP testing")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("💡 Make sure the server is running.")


if __name__ == "__main__":
    asyncio.run(test_completions())
