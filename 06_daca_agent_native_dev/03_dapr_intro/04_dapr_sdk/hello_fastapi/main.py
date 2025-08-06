from fastapi import FastAPI, HTTPException
from dapr.clients import DaprClient
import json

app = FastAPI(title="Dapr FastAPI Hello World")


@app.get("/")
async def root():
    return {"message": "Hello from Live AGI and Dapr SDK!"}


@app.post("/messages")
async def save_message(user_id: str, message: str):
    try:
        with DaprClient() as client:
            # Save state
            state_data = {"user_id": user_id, "message": message}
            client.save_state(store_name="statestore", key=user_id, value=json.dumps(state_data))

            # Publish event
            event_data = {"user_id": user_id, "message": message}
            client.publish_event(pubsub_name="pubsub", topic_name="message-updated", data=json.dumps(event_data))

        return {"status": f"Stored and published message for {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/{user_id}")
async def get_message(user_id: str):
    try:
        with DaprClient() as client:
            # Get state
            response = client.get_state(store_name="statestore", key=user_id)
            if response.data:
                return json.loads(response.data.decode('utf-8'))
            else:
                raise HTTPException(status_code=404, detail="Message not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
