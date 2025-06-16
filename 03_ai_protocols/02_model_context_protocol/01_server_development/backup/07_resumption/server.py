"""
Resume Server Example - Demonstrates MCP EventStore Resumability

This server shows how to use EventStore for resumable connections.
- Uses InMemoryEventStore for simplicity
- Server has intentional delays to test client timeouts
- Demonstrates resumability when clients disconnect/reconnect
"""

import time
import logging
from mcp.server.fastmcp import FastMCP
from memory_store import InMemoryEventStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create event store
event_store = InMemoryEventStore()

# Initialize FastMCP server with EventStore
mcp = FastMCP(
    name="resume-weather-server",
    event_store=event_store,  # Enable resumability
    stateless_http=False,     # Disable session tracking
)


@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.

    Args:
        city(str): The name of the city
    """
    logger.info(f"Getting forecast for {city}")

    # Simulate some processing time - this will cause client timeouts
    # to test resumability
    time.sleep(4)  # 4 second delay

    result = f"The weather in {city} will be warm and sunny (with resume capability!)"
    logger.info(f"Forecast complete for {city}")

    return result

app = mcp.streamable_http_app()

if __name__ == "__main__":
    logger.info("🚀 Starting Resume Server with EventStore")
    logger.info("   - Server running on http://localhost:8000")

    # Run with uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
