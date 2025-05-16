import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP application
mcp = FastMCP(name="my-resources-server")

# --- Resource 1: Static Welcome Message ---
WELCOME_MESSAGE_URI = "app:///messages/welcome"


@mcp.resource(
    uri=WELCOME_MESSAGE_URI,  # Exact URI match
    name="Welcome Message",
    description="A static welcome message from the server.",
    mime_type="text/plain"
)
async def get_welcome_message() -> str:
    """Provides a static welcome message."""
    return "Hello from the MCP Resource Server! Welcome."

# --- Resource 2: Dynamic Current Server Time ---
SERVER_TIME_URI = "app:///system/time"


@mcp.resource(
    uri=SERVER_TIME_URI,
    name="Current Server Time",
    description="Provides the current date and time of the server.",
    mime_type="application/json"  # Example: returning as JSON
)
async def get_server_time() -> dict:
    """Provides the current server time as a JSON object."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "iso_timestamp": now.isoformat(),
        "pretty_time": now.strftime("%Y-%m-%d %H:%M:%S %Z")
    }


# --- Resource 3: Simulated Project File Content ---
# This demonstrates a slightly more complex URI and simulates file access.
# For actual file serving, consider security implications carefully (e.g., path traversal).


PROJECT_README_URI = "file:///project/docs/README.md"
SIMULATED_README_CONTENT = """
# My Project README

This is a simulated README file content provided as an MCP Resource.
It demonstrates how file-like resources can be exposed.

- Feature A
- Feature B
"""


@mcp.resource(
    uri=PROJECT_README_URI,
    name="Project README",
    description="Simulated content of the project's README.md file.",
    mime_type="text/markdown"
)
async def get_project_readme() -> str:
    """Provides the simulated content of a project README file."""
    print(f"[Server Log] Resource requested: {PROJECT_README_URI}")
    # In a real scenario, you would read this from an actual file:
    # with open("path/to/your/project/README.md", "r") as f:
    #     return f.read()
    return SIMULATED_README_CONTENT
