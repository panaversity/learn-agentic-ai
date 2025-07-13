import datetime
import json
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, TextContent, FileUrl, Annotations

VIRTUAL_FILE_SYSTEM: dict[str, dict[str, Any]] = {
    "file:///project/README.md": {
        "content": """# MCP Resources Demo Project""",
        "metadata": {
            "type": "documentation",
            "language": "markdown",
            "last_modified": "2024-01-15T10:30:00Z",
            "size_bytes": 512,
            "author": "MCP Demo Team",
            "version": "1.0.0"
        }
    },
    "file:///project/main.py": {
        "content": """#!/usr/bin/env python3""",
        "metadata": {
            "type": "source_code",
            "language": "python",
            "last_modified": "2024-01-15T09:45:00Z",
            "size_bytes": 645,
            "author": "MCP Demo Team",
            "executable": True,
            "dependencies": ["asyncio", "mcp"]
        }
    }
}

# Initialize FastMCP server with enhanced 2025-06-18 metadata
mcp = FastMCP(
    name="my-resources-server",
    stateless_http=True
)

# --- Resource 1: Enhanced static welcome message ---


@mcp.resource(
    uri="app:///messages/welcome",
    name="Welcome Message",
    title="Server Welcome Message",  # NEW: Title field for 2025-06-18
    description="A comprehensive welcome message with server information and usage guidelines.",
    mime_type="text/markdown"  # Enhanced to support markdown
)
async def get_welcome_message() -> dict:
    """Provides an enhanced welcome message with server details."""

    return VIRTUAL_FILE_SYSTEM.get("file:///project/README.md", {})

# --- Resource 2: Enhanced user profile template ---
@mcp.resource(
    uri="users://{user_id}/profile",
    name="User Profile",
    title="Dynamic User Profile Information",
    description="Dynamically generated user profile with comprehensive information, activity data, and preferences based on user ID parameter.",
    mime_type="text/plain"
)
def get_user_profile(user_id: str) -> str:
    """Returns a comprehensive profile for a given user ID."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Generate a simple profile without trying to parse the user_id as a number
    return f"""# User Profile: {user_id}
Status: Active
Last Active: {timestamp}
Display Name: User {user_id}
Email: {user_id}@example.com
"""

# --- Resource 3: NEW - List of files in the project ---
@mcp.resource(
    uri="app:///files/list",
    name="List of Files",
    title="List of Files",  # NEW: Title field
    description="List of files in the project",
    mime_type="text/markdown"
)
async def list_project_files() -> list[Resource]:
    """Returns enhanced list of all available project files with rich metadata."""
    print("   -> Client requested 'resources/list' for file:// scheme. Serving enhanced virtual files.")

    resources = []
    for uri, file_data in VIRTUAL_FILE_SYSTEM.items():
        metadata = file_data["metadata"]

        # Create Resource with enhanced 2025-06-18 fields
        resource = Resource(
            uri=FileUrl(uri),
            name=uri.split("/")[-1],
            title=f"{metadata['type'].replace('_', ' ').title()}: {uri.split('/')[-1]}",
            description=f"{metadata['type'].replace('_', ' ').title()} file ({metadata['language']}) - {metadata['size_bytes']} bytes, modified {metadata['last_modified']}",
            mimeType=_get_mime_type(metadata['language'])
        )
        resources.append(resource)

    return resources


def _get_mime_type(language: str) -> str:
    """Helper to determine MIME type from language."""
    mime_map = {
        "markdown": "text/markdown",
        "python": "text/x-python",
        "json": "application/json",
        "csv": "text/csv",
        "yaml": "application/yaml"
    }
    return mime_map.get(language, "text/plain")

# --- Enhanced Resource Getter with structured content ---


@mcp.resource(
    uri="file:///project/{file_name}",
    name="File",
    title="File",
    description="File",
    mime_type="text/plain"
)
async def get_project_file(file_name: str) -> list[TextContent]:
    """
    Returns enhanced content for a specific project file with metadata.

    Args:
        file_name: The file_nameof the file to retrieve.

    Returns:
        The content of the file with optional metadata header.
    """
    uri = f"file:///project/{file_name}"
    print(f"   -> Client requested 'resources/read' for URI: {uri}")

    if uri not in VIRTUAL_FILE_SYSTEM:
        return [
            TextContent(
                type="text",
                text=f"""# ❌ File Not Found"""
            )
        ]

    file_data = VIRTUAL_FILE_SYSTEM[uri]
    content = file_data["content"]

    return [
        TextContent(
            type="text",
            text=content,
            annotations=Annotations(
                audience=["user"],
                priority=0.5
            )
        )

    ]


# --- Expose the app for Uvicorn ---
mcp_app = mcp.streamable_http_app()
