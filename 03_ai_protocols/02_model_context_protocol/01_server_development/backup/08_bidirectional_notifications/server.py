import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)


@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("bidirectional-demo-server")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="analyze_data",
                description="Analyze data with REAL progress notifications sent to client",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Data to analyze"}
                    },
                    "required": ["data"]
                }
            ),
            types.Tool(
                name="long_running_task",
                description="Long running task with REAL progress updates to client",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "duration": {"type": "integer", "description": "Duration in seconds"}
                    },
                    "required": ["duration"]
                }
            ),
            types.Tool(
                name="send_notification_demo",
                description="Demonstrates sending REAL various notifications to client",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="simulate_error",
                description="Simulates error with REAL error notifications to client",
                inputSchema={"type": "object", "properties": {}}
            ),
            types.Tool(
                name="add_new_tool",
                description="Dynamically add tool and send REAL tool list changed notification",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string", "description": "Name of new tool"}
                    },
                    "required": ["tool_name"]
                }
            )
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.Content]:
        """Handle tool calls with REAL server→client notifications."""
        ctx = app.request_context
        session = ctx.session
        request_id = ctx.request_id

        logger.info(f"Handling tool call: {name} with request_id: {request_id}")

        if name == "analyze_data":
            return await _analyze_data_with_real_notifications(session, arguments["data"], request_id)

        elif name == "long_running_task":
            duration = arguments.get("duration", 5)
            return await _long_running_task_with_real_progress(session, duration, request_id)

        elif name == "send_notification_demo":
            return await _real_notification_demo(session, request_id)

        elif name == "simulate_error":
            return await _simulate_error_with_real_notifications(session, request_id)

        elif name == "add_new_tool":
            return await _add_tool_with_real_notification(session, arguments["tool_name"], request_id)

        else:
            raise ValueError(f"Unknown tool: {name}")

    # Create the session manager with streamable HTTP
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("🚀 Bidirectional MCP server started with StreamableHTTP!")
            try:
                yield
            finally:
                logger.info("📡 Server shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn

    logger.info(f"🌐 Starting server on http://127.0.0.1:{port}/mcp")
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0


async def _analyze_data_with_real_notifications(session, data: str, request_id: str) -> list[types.Content]:
    """Analyze data with REAL server→client notifications."""
    
    # Send REAL log notification to client
    await session.send_log_message(
        level="info",
        data=f"🔧 Starting analysis of: {data}",
        logger="analyze_data",
        related_request_id=request_id
    )

    analysis_steps = [
        "Loading data...",
        "Preprocessing...",
        "Running analysis...",
        "Generating results..."
    ]

    for i, step in enumerate(analysis_steps):
        # Send REAL progress notification to client
        progress_value = ((i + 1) / len(analysis_steps)) * 100
        await session.send_progress_notification(
            progress_token=f"analysis_{request_id}",
            progress=progress_value,
            total=100.0,
            message=f"📊 Step {i+1}/{len(analysis_steps)}: {step}",
            related_request_id=request_id
        )

        # Send REAL log for each step to client
        await session.send_log_message(
            level="info",
            data=f"📊 Step {i+1}/{len(analysis_steps)}: {step}",
            logger="analyze_data",
            related_request_id=request_id
        )

        await asyncio.sleep(1)  # Simulate work

    result = f"Analysis complete! Processed: {data}. Found 3 patterns and 2 anomalies."

    # Final REAL log notification to client
    await session.send_log_message(
        level="info",
        data=f"✅ Analysis result: {result}",
        logger="analyze_data",
        related_request_id=request_id
    )

    return [types.TextContent(type="text", text=result)]


async def _long_running_task_with_real_progress(session, duration: int, request_id: str) -> list[types.Content]:
    """Long running task with REAL progress notifications to client."""

    await session.send_log_message(
        level="info",
        data=f"🚀 Starting {duration} second task",
        logger="long_task",
        related_request_id=request_id
    )

    for i in range(duration):
        progress = ((i + 1) / duration) * 100

        # Send REAL progress notification to client
        await session.send_progress_notification(
            progress_token=f"task_{request_id}",
            progress=progress,
            total=100.0,
            message=f"⏱️ Processing... {i+1}/{duration} seconds",
            related_request_id=request_id
        )

        await asyncio.sleep(1)

    await session.send_log_message(
        level="info",
        data="✅ Long running task completed!",
        logger="long_task",
        related_request_id=request_id
    )

    return [types.TextContent(type="text", text=f"Task completed in {duration} seconds")]


async def _real_notification_demo(session, request_id: str) -> list[types.Content]:
    """Demonstrate REAL various notification types to client."""

    # REAL log notifications
    await session.send_log_message(
        level="info",
        data="📢 Demonstrating REAL log notifications",
        logger="demo",
        related_request_id=request_id
    )

    await asyncio.sleep(1)

    await session.send_log_message(
        level="warning",
        data="⚠️ This is a REAL warning notification sent to client",
        logger="demo",
        related_request_id=request_id
    )

    await asyncio.sleep(1)

    # REAL progress notification
    await session.send_progress_notification(
        progress_token=f"demo_{request_id}",
        progress=50.0,
        total=100.0,
        message="📊 REAL demo progress notification sent to client",
        related_request_id=request_id
    )

    await asyncio.sleep(1)

    await session.send_log_message(
        level="info",
        data="✅ REAL notification demo complete",
        logger="demo",
        related_request_id=request_id
    )

    return [types.TextContent(type="text", text="REAL notification demo completed! Client received actual MCP notifications.")]


async def _simulate_error_with_real_notifications(session, request_id: str) -> list[types.Content]:
    """Simulate error with REAL error notifications to client."""

    await session.send_log_message(
        level="info",
        data="🧪 Simulating error scenario with REAL notifications",
        logger="error_demo",
        related_request_id=request_id
    )

    try:
        await asyncio.sleep(1)
        await session.send_log_message(
            level="info",
            data="🔄 Step 1: Preparing...",
            logger="error_demo",
            related_request_id=request_id
        )

        await asyncio.sleep(1)
        await session.send_log_message(
            level="info",
            data="🔄 Step 2: Processing...",
            logger="error_demo",
            related_request_id=request_id
        )

        # Send REAL error notification to client
        await session.send_log_message(
            level="error",
            data="💥 REAL simulated error occurred! (sent to client)",
            logger="error_demo",
            related_request_id=request_id
        )

        # Actually raise the error
        raise ValueError("This is a simulated error for demonstration")

    except Exception as e:
        await session.send_log_message(
            level="error",
            data=f"❌ REAL error handled: {str(e)} (sent to client)",
            logger="error_demo",
            related_request_id=request_id
        )
        return [types.TextContent(type="text", text=f"Error was caught and handled: {str(e)}")]


async def _add_tool_with_real_notification(session, tool_name: str, request_id: str) -> list[types.Content]:
    """Add tool dynamically and send REAL tool list changed notification to client."""

    await session.send_log_message(
        level="info",
        data=f"🔧 Adding new tool: {tool_name}",
        logger="tool_manager",
        related_request_id=request_id
    )

    # In a real implementation, you'd actually add the tool to your registry
    # For demo purposes, we'll just send the REAL notification

    # Send REAL tool list changed notification to client
    await session.send_tool_list_changed()

    await session.send_log_message(
        level="info",
        data=f"✅ Tool '{tool_name}' added! REAL notification sent to client.",
        logger="tool_manager",
        related_request_id=request_id
    )

    return [types.TextContent(type="text", text=f"Tool '{tool_name}' added successfully. Client received REAL tool list changed notification.")]


if __name__ == "__main__":
    main()
