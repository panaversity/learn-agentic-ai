import asyncio
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CreateMessageRequestParams, CreateMessageResult, ErrorData, TextContent
from mcp.shared.context import RequestContext


async def mock_sampler(context: RequestContext["ClientSession", Any], params: CreateMessageRequestParams) -> CreateMessageResult | ErrorData:
    """A mock LLM handler that gets called by the ClientSession when the server sends a 'sampling/create' request."""

    print("<- Client: Received 'sampling/create' request from server.")

    print(f"<- Client Parameters '{params}'.")
    print(f"<- Client Context '{context}'.")
    print(f"<- Client Message '{params.messages}'.")

    # Mock a response from an LLM
    mock_llm_response = (
        f"In a world of shimmering code, a brave little function set out to find the legendary Golden Bug. "
        f"It traversed treacherous loops and navigated complex conditionals. "
        f"Finally, it found not a bug, but a feature, more valuable than any treasure."
    )

    print("-> Client: Sending mock story back to the server.")

    # Respond with a dictionary that matches the expected structure
    return CreateMessageResult(
        role="assistant",
        content=TextContent(text=mock_llm_response, type="text"),
        model="openai/gpt-4o-mini",
    )

async def main():
    """A simple client to demonstrate receiving MCP logging notifications."""
    server_url = "http://localhost:8000/mcp/"
    print(f"🚀 Connecting to MCP server at {server_url}")

    try:
        async with streamablehttp_client(server_url) as (read_stream, write_stream, get_session_id):
            async with ClientSession(read_stream, write_stream, sampling_callback=mock_sampler) as session:
                print("✅ Connected. Initializing session...")
                await session.initialize()
                print("🛠️ Session initialized.")

                # Call the sampling tool
                story_topic = "a function's adventure"
                print(f"-> Client: Calling 'create_story' tool with topic: '{story_topic}'")

                tool_result = await session.call_tool("create_story", {"topic": story_topic})

                print("-" * 50)
                print(f"🎉 Final Story Received from Server: {tool_result}")
                if tool_result:
                    print(f"'{tool_result.content[0].text}'")
                else:
                    print("No content received from server.")

                print("\n✅ Demo complete!")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("💡 Make sure the server is running.")

    print("\n🎉 Demo finished.")

if __name__ == "__main__":
    asyncio.run(main())