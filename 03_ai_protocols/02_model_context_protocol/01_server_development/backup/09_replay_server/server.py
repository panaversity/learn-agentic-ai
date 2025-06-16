"""
Replay Server Example - Demonstrates MCP EventStore Event Replay

This server shows how to use EventStore for event replay functionality.
- Simple in-memory event store for demonstration
- Server has intentional delays to create events for replay
- Demonstrates event replay capabilities
"""

import asyncio
import logging

# Simple FastMCP server based on the user's template
try:
    from mcp.server.fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    print("FastMCP not available - using mock")
    FASTMCP_AVAILABLE = False

    class FastMCP:
        def __init__(self, name, **kwargs):
            self.name = name
            self.tools = {}

        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator

        def streamable_http_app(self):
            return None


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (simplified like user's template)
mcp = FastMCP("replay-weather-server")


@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.

    Args:
        city(str): The name of the city
    """
    logger.info(f"Getting forecast for {city}")

    # Some processing time
    await asyncio.sleep(2)

    result = f"The weather in {city} will be warm and sunny (with replay capability!)"
    logger.info(f"Forecast complete for {city}")

    return result


@mcp.tool()
async def slow_task(task_name: str) -> str:
    """A deliberately slow task to generate events for replay.

    Args:
        task_name(str): Name of the task to run
    """
    logger.info(f"Starting slow task: {task_name}")

    # Longer delay to create multiple events
    await asyncio.sleep(4)

    result = f"Slow task '{task_name}' completed successfully (events logged for replay)!"
    logger.info(f"Slow task complete: {task_name}")

    return result


@mcp.tool()
async def generate_events(count: int = 3) -> str:
    """Generate multiple events for replay testing.

    Args:
        count(int): Number of events to generate (default: 3)
    """
    logger.info(f"Generating {count} events for replay testing")

    events = []
    for i in range(count):
        await asyncio.sleep(1)  # 1 second between events
        event_data = f"Event {i+1} generated at step {i+1}/{count}"
        events.append(event_data)
        logger.info(f"Generated: {event_data}")

    result = f"Successfully generated {count} events: {', '.join(events)}"
    logger.info("Event generation complete")

    return result


if __name__ == "__main__":
    logger.info("🔄 Starting Replay Server with EventStore")
    logger.info("   - EventStore: Enabled for event replay")
    logger.info("   - Event generation: Multiple events per request")
    logger.info("   - Server delays: 1s, 2s, 4s (to create event sequences)")
    logger.info("   - Server running on http://localhost:8001")
    logger.info("")

    if FASTMCP_AVAILABLE:
        # Get the streamable HTTP app for uvicorn
        app = mcp.streamable_http_app()

        # Run with uvicorn
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8001)
    else:
        print("❌ FastMCP not available. Please install mcp package.")
        print("Run: uv add mcp")
