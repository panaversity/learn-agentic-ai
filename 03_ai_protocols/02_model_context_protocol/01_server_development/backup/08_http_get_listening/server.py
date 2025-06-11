import asyncio
from typing import List
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response
import json

# This list will hold asyncio.Queue objects for each connected listener.
# A queue is like a waiting line for messages for a specific client.
#
# NOTE: This is a simple, in-memory solution for demonstration.
# In a real-world, multi-worker production environment (like with Gunicorn),
# you would need a more robust message broker like Redis Pub/Sub, RabbitMQ,
# or Kafka to manage listeners across different processes.
listeners: List[asyncio.Queue] = []

mcp = FastMCP(
    name="push-server",
    description="A server that demonstrates pushing events to listening clients.",
)

@mcp.tool()
async def send_notification(message: str) -> str:
    """
    A tool that, when called, sends a notification to all listening clients.
    """
    print(f"Server: Received request to send notification: '{message}'")
    
    # Create the notification payload that will be sent to the listeners.
    # This is a standard MCP JSON-RPC Notification (it has no 'id').
    notification = {
        "jsonrpc": "2.0",
        "method": "app/notification",
        "params": {
            "type": "broadcast_message",
            "content": message,
        }
    }
    
    # Use 'json.dumps' to turn the Python dict into a JSON string.
    # The 'data: ' prefix and '\\n\\n' suffix are required by the SSE protocol.
    sse_formatted_message = f"data: {json.dumps(notification)}\n\n"
    
    print(f"Server: Broadcasting to {len(listeners)} listeners...")
    
    # We go through our list of active listeners and put the message in each
    # of their queues. The listener's web server connection will then pick
    # it up and send it to the client.
    for queue in listeners:
        await queue.put(sse_formatted_message)
        
    return f"Notification sent to {len(listeners)} clients."


# This part is a bit more advanced. We are overriding the default HTTP
# handler to manage the long-lived GET connections for our listeners.
# First, get the FastAPI app instance from the streamable_http_app function
app = mcp.streamable_http_app()

@app.get("/mcp/")
async def mcp_get_handler(req: Request) -> Response:
    """
    Handles incoming GET requests, establishing a Server-Sent Events (SSE) stream.
    """
    # Create a new message queue for this specific client.
    queue = asyncio.Queue()
    listeners.append(queue)
    print(f"Server: New listener connected. Total listeners: {len(listeners)}")

    async def event_stream():
        """Yields messages from the queue as they arrive."""
        try:
            while True:
                # Wait for a message to appear in this client's queue.
                message = await queue.get()
                yield message
        except asyncio.CancelledError:
            # This happens when the client disconnects.
            print("Server: Listener disconnected.")
        finally:
            # Clean up by removing the listener's queue from our list.
            listeners.remove(queue)
            print(f"Server: Listener queue removed. Total listeners: {len(listeners)}")

    # Return a StreamingResponse that will keep the connection open and send
    # events from our event_stream generator function.
    return Response(
        event_stream(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

# --- Expose the app for Uvicorn ---
mcp_app = mcp.app() 