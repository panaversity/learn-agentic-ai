import uuid
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Dict

# --- Session State Management ---
# In a real application, this would be a database or a Redis cache.
# For this example, a simple dictionary is perfect for demonstration.
# The key will be the session_id (a string), and the value will be another
# dictionary holding the data for that session.
SESSIONS: Dict[str, Dict] = {}

mcp = FastMCP(name="session-server")

# --- Session-Aware Tool ---
@mcp.tool()
async def increment_counter(request: Request) -> int:
    """
    Increments a counter specific to the current session.
    Returns the new value of the counter.
    """
    # The 'request' object gives us access to the incoming HTTP request,
    # including its headers.
    session_id = request.headers.get("mcp-session-id")
    
    if not session_id or session_id not in SESSIONS:
        # This should not happen if the client is behaving correctly after the
        # first request, but it's good practice to handle it.
        return JSONResponse(
            status_code=400, 
            content={"error": "Bad Request: Missing or invalid Mcp-Session-Id"}
        )

    # Retrieve the session from our "database"
    session = SESSIONS[session_id]
    
    # Get the counter, defaulting to 0 if it doesn't exist yet
    counter = session.get("counter", 0)
    counter += 1
    
    # Save the new value back to the session
    session["counter"] = counter
    print(f"Server: Incremented counter for session {session_id} to {counter}")
    
    # Return the new value
    return counter

# --- Overriding the Default HTTP Handler ---
# This is the core of our session logic. We need to intercept the raw
# HTTP request *before* FastMCP processes the JSON-RPC payload.
@mcp.app.post("/mcp/")
async def mcp_post_handler(request: Request):
    """
    This custom handler intercepts POST requests to manage sessions.
    """
    headers = dict(request.headers)
    session_id = headers.get("mcp-session-id")
    
    # 1. Check if the client sent a session ID.
    if session_id and session_id in SESSIONS:
        print(f"Server: Existing session found: {session_id}")
    else:
        # 2. If no valid ID was found, create a new session.
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {}  # Create an empty context for the new session
        print(f"Server: New session created: {session_id}")
        
    # 3. Process the actual MCP request.
    # We pass the raw request down to FastMCP's default handler.
    response = await mcp.default_http_handler(request)
    
    # 4. Inject our session ID into the response headers.
    # The client will receive this and know which ID to use for the next request.
    response.headers["Mcp-Session-Id"] = session_id
    
    return response

# --- Expose the app for Uvicorn ---
mcp_app = mcp.app 