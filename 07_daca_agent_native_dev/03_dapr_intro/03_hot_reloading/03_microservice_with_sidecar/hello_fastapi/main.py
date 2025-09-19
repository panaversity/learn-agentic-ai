import json
import httpx
import os

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Dapr FastAPI Hello World")

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
STATE_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/statestore"
PUBSUB_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/pubsub/message-updated"

@app.get("/")
async def root():
    return {"message": "Hello from Live AGI!"}

@app.post("/messages")
async def save_message(user_id: str, message: str):
    async with httpx.AsyncClient() as client:
        try:
            state_payload = [{"key": user_id, "value": {"user_id": user_id, "message": message}}]
            response = await client.post(STATE_URL, json=state_payload)
            response.raise_for_status()
            event_payload = {"user_id": user_id, "message": message}
            response = await client.post(PUBSUB_URL, json=event_payload)
            response.raise_for_status()
            return {"status": f"Stored and published message for {user_id}"}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages/{user_id}")
async def get_message(user_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{STATE_URL}/{user_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=404, detail="Message not found")

@app.post("/subscribe")
async def subscribe_message(data: dict):
    # The inner "data" field is a JSON string, parse it
    try:
        event_data_raw = data.get("data", "{}")
        event_data = json.loads(event_data_raw)
    except json.JSONDecodeError as e:
        print("Failed to decode event data:", e)
        return {"status": "Invalid event data format"}
    
    user_id = event_data.get("user_id", "unknown")
    message = event_data.get("message", "no message")
    print(f"Received event: User {user_id} updated message to '{message}'")
    return {"status": "Event processed"}