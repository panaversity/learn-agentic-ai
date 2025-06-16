import time
import logging
from mcp.server.fastmcp import FastMCP
from memory_store import InMemoryEventStore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Create event store for resumption
event_store = InMemoryEventStore()

# Initialize FastMCP server with EventStore
mcp = FastMCP(
    name="simple-resume-server",
    event_store=event_store,  # This enables resumption!
    stateless_http=False,     # Keep session state
)


@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.
    
    This tool has an intentional 4-second delay to test resumption!
    Clients with 3-second timeouts will fail and need to resume.

    Args:
        city(str): The name of the city
    """
    logger.info(f"🌤️ Getting forecast for {city}...")
    logger.info("⏰ Processing (this takes 4 seconds - testing resumption)...")

    # Intentional delay to cause client timeouts
    time.sleep(6)  # 6 second delay

    result = f"The weather in {city} will be warm and sunny! ☀️ (Retrieved via resumption)"
    logger.info(f"✅ Forecast complete for {city}")

    return result

# Create the ASGI app
app = mcp.streamable_http_app()

if __name__ == "__main__":
    print("=" * 60)
    print("         SIMPLE MCP RESUME SERVER")
    print("=" * 60)
    print("🚀 Starting server with resumption capabilities...")
    print("📋 EventStore: Enabled (tracks messages for resumption)")
    print("⏰ Tool delay: 4 seconds (to test client timeouts)")
    print("🌐 Server URL: http://localhost:8000")
    print("=" * 60)
    print()
    print("💡 How to test:")
    print("1. Run: python client.py")
    print("2. Watch client timeout on tool call")
    print("3. See resumption in action!")
    print()
