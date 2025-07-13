from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, Annotations, ToolAnnotations

# Initialize a stateless FastMCP server with enhanced metadata for 2025-06-18
mcp = FastMCP(
    name="my-tools-server",
    stateless_http=True
)

# Lists and other types are wrapped automatically
@mcp.tool()
def list_cities() -> list[str]:
    """Get a list of cities"""
    return ["London", "Paris", "Tokyo"]
    # Returns: {"result": ["London", "Paris", "Tokyo"]}


@mcp.tool(structured_output=False)
def get_temperature(city: str) -> float:
    """Get temperature as a simple float"""
    return 22.5
    # Returns: {"result": 22.5}
    
# === Using Pydantic models for rich structured data ===
class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    condition: str
    wind_speed: float


@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Get structured weather data"""
    return WeatherData(
        temperature=22.5, humidity=65.0, condition="partly cloudy", wind_speed=12.3
    )
    
# --- Tool 1: Basic Structured Output with Rich Annotations ---
@mcp.tool(structured_output=True, annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True, readOnlyHint=True))
def add_numbers(a: float, b: float) -> list[TextContent]:
    """
    Demonstrates BASIC structured tool output with rich annotations.

    Args:
        a: The first number to add
        b: The second number to add

    Returns:
        list containing single TextContent with calculation details and annotations
    """
    result = a + b

    # Create human-readable text
    calculation_text = f"🧮 **Addition Calculation**\n\n"
    calculation_text += f"**Input:** {a} + {b}\n"
    calculation_text += f"**Result:** {result}\n"

    return [
        TextContent(
            type="text",
            text=calculation_text,
            # RICH ANNOTATIONS - Key feature of 2025-06-18
            annotations=Annotations(
                audience=["user", "assistant"],
                priority=1.0
            )
        )
    ]

# --- Tool 2: Multi-Content Structured Output ---
@mcp.tool(structured_output=True, annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True, readOnlyHint=True))
async def analyze_data(data_type: str, sample_size: int = 100) -> list[TextContent | ImageContent]:
    """
    Demonstrates MULTI-CONTENT structured tool output.
    
    Args:
        data_type: Type of data to analyze (sales, users, performance)
        sample_size: Number of samples to analyze (10-1000)

    Returns:
        list containing multiple content items with different purposes
    """
    sample_size = max(10, min(1000, sample_size))  # Clamp values

    # Content 1: Summary Report
    summary_text = f"📊 **Data Analysis Report**\n\n"
    summary_text += f"**Analysis Type:** {data_type.title()}\n"
    summary_text += f"**Sample Size:** {sample_size:,} records\n"


    return [
        # Content 1: Executive Summary
        TextContent(
            type="text",
            text=summary_text,
            annotations=Annotations(
                audience=["user", "assistant"],
                priority=1.0
            )
        ),
        # Content 3: Recommendations
        ImageContent(
            type="image",
            data="",
            mimeType="text/plain",
            annotations=Annotations(
                audience=["user"],
                priority=0.9,
            )
        )
    ]

# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()
