from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import StreamingResponse
from collections import defaultdict
import asyncio
import json
import uuid
import time
import uvicorn
import random

app = FastAPI(title="Simplified SSE Server with Mock AI Agent")

# Store sessions: {session_id: {"queue": asyncio.Queue(), "last_active": float}}
sessions = defaultdict(lambda: {"queue": asyncio.Queue(), "last_active": time.time()})
SESSION_TIMEOUT = 180  # Seconds
MOCK_MESSAGES = [
    "Classifying image X: 80% confidence...",
    "Training model on dataset Y: 50% complete...",
    "Generating response for query Z...",
    "Optimizing parameters for task Q...",
    "Idle: awaiting new tasks..."
]
MOCK_STATUSES = ["processing", "completed", "pending"]

async def sse_stream(session_id: str, request: Request):
    """Generate SSE events for a client session, including mock AI agent messages."""
    async def event_generator():
        # Send connection confirmation
        yield {"event": "connection_confirmation", "data": {"sessionId": session_id, "message": "Connected"}}
        sessions[session_id]["last_active"] = time.time()

        while not await request.is_disconnected():
            try:
                # Wait for queued messages or timeout for mock data
                event = await asyncio.wait_for(sessions[session_id]["queue"].get(), timeout=3.0)
                yield event
                sessions[session_id]["queue"].task_done()
                sessions[session_id]["last_active"] = time.time()
            except asyncio.TimeoutError:
                # Send mock AI agent message
                yield {
                    "event": "ai_agent_message",
                    "data": {
                        "message": random.choice(MOCK_MESSAGES),
                        "agent_id": f"Agent-{random.randint(1, 100):03d}",
                        "timestamp": time.time(),
                        "status": random.choice(MOCK_STATUSES)
                    }
                }
                # Send keep-alive comment
                yield {"event": None, "data": None}
                sessions[session_id]["last_active"] = time.time()

    async def format_sse():
        async for event in event_generator():
            if event["event"] is None:
                yield ":keep-alive\n\n"
            else:
                event_type = event["event"]
                data = json.dumps(event["data"])
                yield f"event: {event_type}\ndata: {data}\n\n"

    if session_id not in sessions:
        sessions[session_id] = {"queue": asyncio.Queue(), "last_active": time.time()}

    return StreamingResponse(
        format_sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/sse_stream")
async def sse_endpoint(request: Request, session_id: str = Query(default_factory=lambda: str(uuid.uuid4()))):
    """SSE endpoint for clients to receive events."""
    return await sse_stream(session_id, request)

@app.post("/send_message")
async def send_message(session_id: str = Query(...), message: str = Query(...)):
    """Receive client message and push SSE confirmation."""
    if session_id not in sessions:
        return Response(content=json.dumps({"error": "Invalid session ID"}), status_code=404)

    await sessions[session_id]["queue"].put({
        "event": "message_receipt",
        "data": {"original_message": message, "timestamp": time.time(), "confirmation": f"Received for {session_id}"}
    })
    sessions[session_id]["last_active"] = time.time()
    return {"status": "Message queued"}

async def cleanup_sessions():
    """Remove inactive sessions periodically."""
    while True:
        await asyncio.sleep(60)
        now = time.time()
        for sid in list(sessions):
            if now - sessions[sid]["last_active"] > SESSION_TIMEOUT:
                del sessions[sid]

@app.on_event("startup")
async def startup():
    asyncio.create_task(cleanup_sessions())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)