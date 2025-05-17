# 02_mcp_over_http/server/main.py
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent # For prompt templates

# 1. Initialize FastMCP
# We're making it stateless and enabling json_response optimization
mcp_app = FastMCP(
    name="my-simple-http-server",
    description="A basic MCP server for HTTP client demonstration.",
    stateless_http=True,      # Makes the server treat each HTTP request independently
    json_response=True,       # Allows single JSON responses for non-streaming calls (optimization)
)

# 2. Define a simple tool
@mcp_app.tool()
def greet(name: str = "World") -> str:
    """Returns a greeting message."""
    print(f"[Server Log] greet tool called with name: {name}")
    return f"Hello, {name} from the MCP HTTP server!"

# 3. Define a simple static resource
APP_WELCOME_MSG_URI = "app:///messages/welcome" # URI for this specific resource
@mcp_app.resource(
    uri=APP_WELCOME_MSG_URI, # Register with this exact URI
    name="Welcome Message",
    description="A static welcome message from the server.",
    mime_type="text/plain"
)
async def get_welcome_message_resource() -> str:
    """Provides a static welcome message."""
    print(f"[Server Log] Welcome resource ('{APP_WELCOME_MSG_URI}') requested.")
    return "This is a welcome resource from the HTTP server!"

# 4. Define a resource template (parameterized URI)
@mcp_app.resource("users://{user_id}/profile") # URI template
async def get_user_profile(user_id: str) -> str:
    """Provides dynamic profile data for a given user ID."""
    print(f"[Server Log] User profile requested for user_id: {user_id}")
    return f"Profile data for user {user_id}"

# 5. Define a simple prompt template
@mcp_app.prompt(
    name="simple_question",
    description="Generates a prompt asking a simple question."
)
async def simple_question_prompt(entity: str = "the sky") -> list[PromptMessage]:
    """Generates a prompt asking why something is a certain color."""
    print(f"[Server Log] simple_question prompt requested for entity: {entity}")
    return [
        PromptMessage(
            role="user",
            content=TextContent(text=f"Why is {entity} blue?", type="text")
        )
    ]

# 6. Make the server runnable
if __name__ == "__main__":
    print(f"Starting MCP server '{mcp_app.name}'...")
    # This uses the built-in server runner from the MCP SDK.
    mcp_app.run(transport="streamable-http")