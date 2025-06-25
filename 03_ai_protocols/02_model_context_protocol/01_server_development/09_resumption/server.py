import logging
import asyncio
from mcp.server.fastmcp import FastMCP
from memory_store import InMemoryEventStore
from datetime import datetime
import json

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
    
    This tool has an intentional 6-second delay to test resumption!
    Clients with 3-second timeouts will fail and need to resume.

    Args:
        city(str): The name of the city
    """
    start_time = datetime.now().isoformat()
    print(f"🌤️ Starting forecast for {city} at {start_time}")
    
    # Simulate long-running operation (server processing delay)
    print(f"🌤️ Processing... (6 second delay)")
    await asyncio.sleep(6)
    
    end_time = datetime.now().isoformat()
    result = {
        "result": f"The weather in {city} will be warm and sunny! ☀️ (Retrieved via resumption)",
        "indicator_date": end_time,
    }
    
    print(f"🌤️ Forecast complete for {city} at {end_time}")
    return json.dumps(result)



# Create the ASGI app
app = mcp.streamable_http_app()

if __name__ == "__main__":

    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
