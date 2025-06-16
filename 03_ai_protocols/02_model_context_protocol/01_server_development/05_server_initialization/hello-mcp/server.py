from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather", stateless_http=False) # No reason to initialize stateless


@mcp.tool()  # Using this mcp instance
async def get_forecast(city: str) -> str:
    """Get weather forecast for a city.

    Args:
        city(str): The name of the city
    """
    return f"The weather in {city} will be warm and sunny"

mcp_app = mcp.streamable_http_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)