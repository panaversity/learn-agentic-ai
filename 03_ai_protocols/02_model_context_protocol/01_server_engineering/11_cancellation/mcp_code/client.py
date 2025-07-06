#!/usr/bin/env python3
"""
A simple client to demonstrate cancelling a long-running MCP tool call.
"""

import asyncio
import anyio
import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.exceptions import McpError


async def main():
    """
    Connects to the server, starts a long-running task, and then cancels it.
    """
    print("🚀 Starting cancellable task demonstration...")

    try:
        async with streamablehttp_client("http://localhost:8000/mcp/") as (read, write, _):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server.")

                await session.initialize()
                print("✅ Session initialized.")

                async with anyio.create_task_group() as tg:
                    # This function will run the long-running tool call.
                    async def run_cancellable_task(request_id_to_cancel: int):
                        print("📁 Starting long-running task 'process_large_file'...")
                        print(
                            f"   (Task with request ID {request_id_to_cancel} will be cancelled in 3 seconds)")
                        try:
                            # We use the lower-level send_request to have more control
                            # than the simple session.call_tool().
                            await session.send_request(
                                types.ClientRequest(
                                    root=types.CallToolRequest(
                                        method="tools/call",
                                        params=types.CallToolRequestParams(
                                            name="process_large_file",
                                            arguments={
                                                "filename": "large_dataset.csv"},
                                        ),
                                    )
                                ),
                                result_type=types.CallToolResult,
                            )
                        except McpError as e:
                            # The server will respond with a RequestCancelled error.
                            if e.error.code == -32800:
                                print(
                                    f"✅ Task {request_id_to_cancel} was successfully cancelled by the server!")
                            else:
                                print(
                                    f"❌ Task failed with an unexpected error: {e}")

                    # The proper way to get the request ID is to inspect the session's
                    # internal counter *before* making the request.
                    request_id_to_cancel = session._request_id

                    # Start the long-running task in the background.
                    tg.start_soon(run_cancellable_task, request_id_to_cancel)

                    # Wait for 3 seconds before sending the cancellation.
                    await asyncio.sleep(3)

                    print(
                        f"⏹️ Waited 3 seconds. Sending cancellation for request {request_id_to_cancel}...")

                    await session.send_notification(
                        types.ClientNotification(
                            root=types.CancelledNotification(
                                method="notifications/cancelled",
                                params=types.CancelledNotificationParams(
                                    requestId=request_id_to_cancel),
                            )
                        )
                    )
                    # The task running in the background will now be cancelled by the server.

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n💡 Make sure the server is running.")

    print("\n🎉 Demo finished.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Demo stopped by user.")
