import base64
import json
import mcp.types as types

from pydantic import AnyUrl
from starlette.applications import Starlette
from starlette.routing import Route, Mount

from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

# --- 1. Large Dataset Generation ---
# To demonstrate pagination, we need a dataset larger than the page size.
# This function generates a list of 150 dummy items.
DUMMY_ITEMS = [
    {"id": i, "name": f"item_{i:03d}"} for i in range(1, 151)
]
PAGE_SIZE = 20

# --- 2. Low-Level MCP Server Setup ---
# This is the core protocol logic, without any web transport.
server: Server = Server("MCP Pagination Demo Server (Low-Level)")


# --- 3. Cursor Encoding/Decoding Helpers ---
# The cursor is an opaque string to the client, but the server needs to
# encode state into it. Here, we encode the next page number.
def _encode_cursor(page: int) -> str:
    """Encodes the next page number into a base64 string."""
    return base64.b64encode(json.dumps({"page": page}).encode()).decode()


def _decode_cursor(cursor: str | None) -> int:
    """Decodes a base64 cursor string back to a page number."""
    if not cursor:
        return 1  # Start at page 1 if no cursor is provided
    try:
        data = json.loads(base64.b64decode(cursor))
        page = data.get("page")
        if not isinstance(page, int):
            raise ValueError(
                "Invalid cursor format: 'page' must be an integer.")
        return page
    except (json.JSONDecodeError, TypeError, KeyError, ValueError) as e:
        # Raise a specific, serializable MCP error for invalid cursors.
        # The StreamableHTTPSessionManager will catch this and format a
        # proper JSON-RPC error response.
        raise types.JSONRPCError(
            types.ErrorData(
                code=types.INVALID_PARAMS,
                message=f"Invalid cursor format: {e}",
            )
        )


# --- 4. Manual Pagination for `tools/list` ---
# The decorator for the low-level server must accept the full request object
# to get access to the `params` which contain the `cursor` and `limit`.
async def list_all_tools(request: types.ListToolsRequest) -> types.ServerResult:
    print(
        f"\n[SERVER LOG] Received tools/list request: {request.model_dump_json(indent=2)}")
    cursor = request.params.cursor if request.params else None
    limit = None  # Not supported in this version of the spec

    page_number = _decode_cursor(cursor)
    page_size = limit or PAGE_SIZE
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size

    page_items = DUMMY_ITEMS[start_index:end_index]
    tools = [
        types.Tool(
            name=item["name"],
            title=f"Tool {item['name']}",
            description=f"This is a dummy tool with ID {item['id']}",
            inputSchema={"type": "object", "properties": {}},
        )
        for item in page_items
    ]

    next_cursor = None
    if end_index < len(DUMMY_ITEMS):
        next_cursor = _encode_cursor(page_number + 1)

    return types.ServerResult(types.ListToolsResult(tools=tools, nextCursor=next_cursor))

server.request_handlers[types.ListToolsRequest] = list_all_tools


# --- 5. Manual Pagination for `resources/list` ---
async def list_all_resources(request: types.ListResourcesRequest) -> types.ServerResult:
    print(
        f"\n[SERVER LOG] Received resources/list request: {request.model_dump_json(indent=2)}")
    cursor = request.params.cursor if request.params else None
    limit = None  # Not supported in this version of the spec

    print(f"cursor: {cursor}")
    print(f"limit: {limit}")

    page_number = _decode_cursor(cursor)
    page_size = limit or PAGE_SIZE
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size

    page_items = DUMMY_ITEMS[start_index:end_index]
    resources = [
        types.Resource(
            uri=AnyUrl(f"resource://item-{item['id']}"),
            name=item["name"],
            title=f"Resource {item['name']}",
            description=f"This is a dummy resource with ID {item['id']}",
            mimeType="text/plain",
        )
        for item in page_items
    ]

    next_cursor = None
    if end_index < len(DUMMY_ITEMS):
        print(f"end_index: {end_index}")
        print(f"len(DUMMY_ITEMS): {len(DUMMY_ITEMS)}")
        next_cursor = _encode_cursor(page_number + 1)

    print(f"next_cursor: {next_cursor}")
    return types.ServerResult(types.ListResourcesResult(resources=resources, nextCursor=next_cursor))

server.request_handlers[types.ListResourcesRequest] = list_all_resources


# --- 6. Expose the Server over HTTP using StreamableHTTPSessionManager ---
# The StreamableHTTPSessionManager is the bridge that adapts the low-level Server
# to an ASGI interface, making it accessible over the web.

session_manager = StreamableHTTPSessionManager(app=server)

# The final Starlette application.
# We mount the session manager's handler at "/mcp/" and use its lifespan.
# The lifespan from Starlette receives the `app` object as an argument,
# so we use a lambda to adapt the call to `session_manager.run()`.
app = Starlette(
    routes=[
        Mount("/mcp/", app=session_manager.handle_request),
    ],
    lifespan=lambda app: session_manager.run(),
)
