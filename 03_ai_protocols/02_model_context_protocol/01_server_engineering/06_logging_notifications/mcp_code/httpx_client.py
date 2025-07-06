"""
MCP Logging Client - Educational Implementation (2025-06-18)

This client demonstrates how to:
- Connect to a stateful MCP server that provides logging.
- Use a logging handler to process notifications in real-time.
- Set the server's logging level to control message verbosity.
- Call a tool and observe the log messages it generates.
"""

import asyncio
import json
import httpx
from typing import Dict, Any
from httpx_sse import EventSource, aconnect_sse
from mcp.types import JSONRPCMessage, JSONRPCRequest, JSONRPCNotification, ClientCapabilities, Implementation


class MCPLoggingHTTPXClient:
    """MCP-compliant httpx client for logging notifications"""

    def __init__(self, url: str):
        self.url = url
        self.session_id: str | None = None
        self.request_headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        self.get_stream_task: asyncio.Task[Any] | None = None
        self.emoji_map = {
            "debug": "🔍",
            "info": "📰",
            "notice": "📢",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🆘",
            "alert": "🚒",
            "emergency": "💥"
        }

    def _update_headers_with_session(self, base_headers: dict[str, str]) -> dict[str, str]:
        """Update headers with session ID if available"""
        headers = base_headers.copy()
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        return headers

    def _format_log_message(self, level: str, logger_name: str | None, data: str):
        """Format log message like the official client"""
        emoji = self.emoji_map.get(level.lower(), "📝")
        logger_info = f" [{logger_name}]" if logger_name else ""
        print(f"    {emoji} [{level.upper()}]{logger_info} {data}")

    async def start_get_stream(self, client: httpx.AsyncClient):
        """Start GET stream for server-initiated messages (logging notifications)"""
        if not self.session_id:
            return

        print("    🔄 Starting GET stream for server logging...")

        try:
            headers = self._update_headers_with_session(self.request_headers)

            async with aconnect_sse(
                client,
                "GET",
                self.url,
                headers=headers,
                timeout=httpx.Timeout(30.0, read=300.0)
            ) as event_source:
                print("    ✅ GET stream established for logging")

                async for sse in event_source.aiter_sse():
                    if sse.event == "message":
                        try:
                            parsed = json.loads(sse.data)

                            # Handle logging notifications from GET stream
                            if parsed.get("method") == "notifications/message":
                                params = parsed.get("params", {})
                                level = params.get("level", "info")
                                logger_name = params.get("logger")
                                data = params.get("data", "")

                                self._format_log_message(
                                    level, logger_name, data)

                        except json.JSONDecodeError as e:
                            print(f"    ❌ GET stream JSON decode error: {e}")

        except Exception as e:
            print(f"    ⚠️  GET stream error: {e}")

    async def initialize_mcp(self, client: httpx.AsyncClient) -> str | None:
        """Initialize MCP connection"""
        print("🔌 Initializing MCP connection for logging...")

        init_request = JSONRPCRequest(
            jsonrpc="2.0",
            id=1,
            method="initialize",
            params={
                "protocolVersion": "2025-06-18",
                "capabilities": ClientCapabilities(
                    experimental={},
                    sampling=None,
                    roots=None
                ).model_dump(exclude_none=True),
                "clientInfo": Implementation(
                    name="httpx-logging-client",
                    version="1.0.0"
                ).model_dump()
            }
        )

        message = JSONRPCMessage(init_request)
        headers = self.request_headers.copy()

        response = await client.post(
            self.url,
            json=message.model_dump(
                by_alias=True, mode="json", exclude_none=True),
            headers=headers
        )
        response.raise_for_status()

        self.session_id = response.headers.get("mcp-session-id")
        print(f"✅ Connected! Session ID: {self.session_id}")
        return self.session_id

    async def send_initialized(self, client: httpx.AsyncClient):
        """Send initialized notification and start GET stream"""
        initialized_notification = JSONRPCNotification(
            jsonrpc="2.0",
            method="notifications/initialized",
            params={}
        )

        message = JSONRPCMessage(initialized_notification)
        headers = self._update_headers_with_session(self.request_headers)

        response = await client.post(
            self.url,
            json=message.model_dump(
                by_alias=True, mode="json", exclude_none=True),
            headers=headers
        )

        if response.status_code == 202:
            print("✅ Initialized notification sent")

            # Start GET stream after initialization for logging notifications
            self.get_stream_task = asyncio.create_task(
                self.start_get_stream(client))

    async def set_logging_level(self, client: httpx.AsyncClient, level: str):
        """Set the logging level on the server"""
        request_id = 2

        set_level_request = JSONRPCRequest(
            jsonrpc="2.0",
            id=request_id,
            method="logging/setLevel",
            params={
                "level": level
            }
        )

        message = JSONRPCMessage(set_level_request)
        headers = self._update_headers_with_session(self.request_headers)

        print(f"🎚️ Setting logging level to: {level}")

        response = await client.post(
            self.url,
            json=message.model_dump(
                by_alias=True, mode="json", exclude_none=True),
            headers=headers
        )

        if response.status_code == 200:
            print(f"✅ Logging level set to {level}")
        else:
            print(f"❌ Failed to set logging level: {response.status_code}")

    async def call_tool_with_logging(self, client: httpx.AsyncClient,
                                     tool_name: str, arguments: Dict[str, Any]):
        """Call MCP tool and receive logging notifications"""

        request_id = 3

        tool_request = JSONRPCRequest(
            jsonrpc="2.0",
            id=request_id,
            method="tools/call",
            params={
                "name": tool_name,
                "arguments": arguments
            }
        )

        message = JSONRPCMessage(tool_request)
        headers = self._update_headers_with_session(self.request_headers)

        print(f"\n🛠️ Calling tool: {tool_name} (httpx logging)")
        print("-" * 50)

        async with client.stream(
            "POST",
            self.url,
            json=message.model_dump(
                by_alias=True, mode="json", exclude_none=True),
            headers=headers
        ) as response:

            if response.status_code != 200:
                print(f"❌ Request failed: {response.status_code}")
                return None

            content_type = response.headers.get("content-type", "").lower()

            if "text/event-stream" in content_type:
                event_source = EventSource(response)
                message_count = 0
                final_result = None

                async for sse in event_source.aiter_sse():
                    message_count += 1

                    if sse.event == "message":
                        try:
                            parsed = json.loads(sse.data)

                            # Handle logging notifications from POST stream
                            if parsed.get("method") == "notifications/message":
                                params = parsed.get("params", {})
                                level = params.get("level", "info")
                                logger_name = params.get("logger")
                                data = params.get("data", "")

                                self._format_log_message(
                                    level, logger_name, data)

                            # Handle final result
                            elif "result" in parsed:
                                final_result = parsed["result"]
                                break

                        except json.JSONDecodeError as e:
                            print(f"    ❌ JSON decode error: {e}")

                return final_result

            else:
                # Handle JSON response
                content = await response.aread()
                try:
                    data = json.loads(content)
                    return data.get("result")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    return None

    async def cleanup(self):
        """Clean up resources"""
        if self.get_stream_task:
            self.get_stream_task.cancel()
            try:
                await self.get_stream_task
            except asyncio.CancelledError:
                pass


async def main():
    """httpx client demo for MCP logging notifications"""

    print("🚀 httpx MCP Logging Demo")
    print("=" * 50)

    url = "http://localhost:8000/mcp/"

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, read=300.0)
    ) as client:

        mcp_client = MCPLoggingHTTPXClient(url)

        try:
            # Initialize MCP connection
            session_id = await mcp_client.initialize_mcp(client)
            if not session_id:
                print("❌ Failed to get session ID")
                return

            # Send initialized notification and start GET stream
            await mcp_client.send_initialized(client)

            # Give GET stream time to establish
            await asyncio.sleep(0.5)

            # Set logging level to see debug messages
            await mcp_client.set_logging_level(client, "debug")

            # Test logging scenarios
            scenarios = [
                {
                    "name": "📊 Data Task",
                    "tool": "do_work",
                    "args": {"task": "data processing"}
                },
                {
                    "name": "⚙️ General Task",
                    "tool": "do_work",
                    "args": {"task": "system maintenance"}
                }
            ]

            for scenario in scenarios:
                print(f"\n{scenario['name']}")

                result = await mcp_client.call_tool_with_logging(
                    client,
                    scenario["tool"],
                    scenario["args"]
                )

                print("-" * 50)
                if result and "content" in result:
                    for content in result["content"]:
                        print(
                            f"✅ Result: {content.get('text', 'No text content')}")
                else:
                    print("✅ Tool completed successfully")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await mcp_client.cleanup()

    print("\n🎉 httpx Logging Demo completed!")
    print("\n💡 The log messages above came directly from the server via httpx + MCP protocol!")

if __name__ == "__main__":
    asyncio.run(main())
