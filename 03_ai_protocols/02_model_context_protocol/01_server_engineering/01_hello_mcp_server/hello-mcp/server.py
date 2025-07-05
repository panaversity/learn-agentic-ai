from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with enhanced metadata for 2025-06-18 spec
mcp = FastMCP(
    name="weather-server",
    stateless_http=True
)

@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city with structured output.

    Args:
        city: The name of the city to get weather for
        
    Returns:
        Content with weather information
    """
    # Demonstrate structured tool output (new in 2025-06-18)
    forecast_text = f"🌤️ Weather forecast for {city}:\n\n"
    forecast_text += f"Today: Warm and sunny, 75°F (24°C)\n"
    forecast_text += f"📍 Data source: Local Weather Station for {city}"
    
    return forecast_text

mcp_app = mcp.streamable_http_app()