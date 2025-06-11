import asyncio
import uuid
import json
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response
from typing import Dict, List, Tuple

# --- Session State Management ---
# We are expanding our session state to include a replay buffer for messages.
SESSIONS: Dict[str, Dict] = {}
REPLAY_BUFFER_SIZE = 10  # How many recent messages to store per session

mcp = FastMCP(name="resumption-server")

async def _send_event(session_id: str, message: dict):
    """A helper to send a message to a session and store it in the buffer."""
    if session_id not in SESSIONS:
        return
        
    session = SESSIONS[session_id]
    
    # Each session now has its own event counter to generate unique IDs
    event_id = session.get("event_counter", 0) + 1
    session["event_counter"] = event_id
    
    # Format the message in SSE format with an ID
    sse_message = f"id: {event_id}\ndata: {json.dumps(message)}\n\n"
    
    # Add the message and its ID to our replay buffer
    if "buffer" not in session:
        session["buffer"] = []
    
    session["buffer"].append((event_id, sse_message))
    
    # Keep the buffer from growing too large
    if len(session["buffer"]) > REPLAY_BUFFER_SIZE:
        session["buffer"].pop(0)
    
    # If the session has an active listener queue, send the message
    if "queue" in session:
        await session["queue"].put(sse_message)
        print(f"Server: Sent event {event_id} to session {session_id[:8]}")

@mcp.tool()
async def send_burst(request: Request):
    """Sends a quick burst of 5 messages to the client."""
    session_id = request.headers.get("mcp-session-id")
    if not session_id or session_id not in SESSIONS:
        return Response(status_code=400, content="Missing or invalid session ID")

    print(f"\nServer: Received 'send_burst' for session {session_id[:8]}")
    for i in range(5):
        await _send_event(session_id, {"message": f"This is message #{i+1} in the burst."})
        await asyncio.sleep(0.1) # Small delay between messages
    return "Burst sent."

# --- Core MCP Handlers for Session and Resumption ---
@mcp.app.post("/mcp/")
async def mcp_post_handler(request: Request):
    session_id = request.headers.get("mcp-session-id")
    if not session_id or session_id not in SESSIONS:
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {}
        print(f"Server: New session created: {session_id[:8]}")
    
    response = await mcp.default_http_handler(request)
    response.headers["Mcp-Session-Id"] = session_id
    return response

@mcp.app.get("/mcp/")
async def mcp_get_handler(req: Request):
    session_id = req.headers.get("mcp-session-id")
    if not session_id or session_id not in SESSIONS:
        return Response(status_code=400, content="GET request requires a valid Mcp-Session-Id")

    session = SESSIONS[session_id]
    session["queue"] = asyncio.Queue()
    print(f"\nServer: Listener connected for session {session_id[:8]}")
    
    # --- Resumption Logic ---
    last_event_id = req.headers.get("last-event-id")
    if last_event_id:
        print(f"Server: Client is resuming from event ID: {last_event_id}")
        try:
            last_id = int(last_event_id)
            if "buffer" in session:
                missed_messages = [msg for id, msg in session["buffer"] if id > last_id]
                if missed_messages:
                    print(f"Server: Replaying {len(missed_messages)} missed messages.")
                    for msg in missed_messages:
                        await session["queue"].put(msg)
        except (ValueError, TypeError):
            print(f"Server: Invalid Last-Event-ID format: {last_event_id}")
    
    async def event_stream():
        try:
            while True:
                message = await session["queue"].get()
                yield message
        finally:
            print(f"Server: Listener disconnected for session {session_id[:8]}")
            session.pop("queue", None)

    return Response(event_stream(), media_type="text/event-stream")

mcp_app = mcp.app 