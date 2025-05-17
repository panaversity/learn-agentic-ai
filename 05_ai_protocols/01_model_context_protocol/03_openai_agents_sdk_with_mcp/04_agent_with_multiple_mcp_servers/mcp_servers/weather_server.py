import logging
from mcp.server.fastmcp import FastMCP

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="WeatherServer",
    description="A simple shared MCP server for OpenAI Agents SDK examples.",
    stateless_http=True,
    json_response=True, # Generally easier for HTTP clients if they don't need full SSE parsing
)


@mcp.tool()  # Using this mcp instance
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.

    Args:
        city(str): The name of the city
    """
    return f"The weather in {city} will be warm and sunny"

if __name__ == "__main__":
    port = 8002
    streamable_http_app = mcp.streamable_http_app()
    print(f"Starting {streamable_http_app}")
    import uvicorn
    # uvicorn.run(streamable_http_app, host="0.0.0.0", port=port)
    # start with hot reload
    uvicorn.run("weather_server:mcp.streamable_http_app", host="0.0.0.0", port=port, reload=True)