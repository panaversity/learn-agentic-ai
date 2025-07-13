"""
MCP Elicitation Server (2025-06-18)

This server demonstrates the core elicitation feature, allowing tools
to request additional information from users during execution.
"""
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context

# A stateful server is required for elicitation (server-to-client requests)
mcp = FastMCP(
    name="mcp-elicitation-server",
    stateless_http=False,
)


class OrderPreferences(BaseModel):
    """Schema for collecting user's pizza order preferences."""
    want_toppings: bool = Field(
        description="Would you like to add extra toppings?"
    )
    toppings: str = Field(
        default="mushrooms",
        description="What toppings would you like? (comma-separated)"
    )


@mcp.tool()
async def order_pizza(ctx: Context, size: str) -> str:
    """
    Orders a pizza with optional toppings through user elicitation.

    Args:
        ctx: The MCP Context, used to communicate with the client
        size: Size of the pizza (small, medium, large)

    Returns:
        Order confirmation message
    """
    print(f"-> Server: Tool 'order_pizza' called with size: '{size}'")

    try:
        # Ask user if they want toppings and what kind
        print("-> Server: Sending elicitation request to client...")
        result = await ctx.elicit(
            message=f"Ordering a {size} pizza. Would you like to customize it?",
            schema=OrderPreferences
        )

        # Handle user's response
        if result.action == "accept" and result.data:
            if result.data.want_toppings:
                return f"Order confirmed: {size} pizza with {result.data.toppings}"
            return f"Order confirmed: {size} plain pizza"
        elif result.action == "decline":
            return "Order declined: No pizza ordered"
        else:  # cancel
            return "Order cancelled"

    except Exception as e:
        print(f"-> Server: An error occurred during elicitation: {e}")
        return f"Error processing pizza order: {e}"

# Expose the server as a runnable ASGI application
mcp_app = mcp.streamable_http_app()