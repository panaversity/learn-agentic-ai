import json
import os
import logging

from fastapi import FastAPI, HTTPException
from dapr.clients import DaprClient


app = FastAPI(title="Security Fundamentals")

### 1. ENV VARIABLES BASED CONFIGMAPS APPROACH
# Configure logging based on environment variable
# log_level = os.getenv("LOG_LEVEL", "INFO")
# logging.basicConfig(level=getattr(logging, log_level))
# logger = logging.getLogger(__name__)

# # Read API endpoint from environment variable
# health_endpoint = os.getenv("API_ENDPOINT", "/local/health")

# @app.get(health_endpoint)
# async def health_check():
#     logger.debug("Health check endpoint called")
#     logger.info(f"API_ENDPOINT {os.getenv("API_ENDPOINT")}")
#     logger.info(f"LOG_LEVEL {os.getenv("LOG_LEVEL")}")
#     return {"status": "healthy"}

### 2. VOLUME MOUNTED CONFIGMAPS APPROACH

# Read config values from mounted files
def read_config(path, default=""):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return default

log_level = read_config("/etc/name/log_level", "INFO")
api_endpoint = read_config("/etc/name/api_endpoint", "/local/health")
# Setup logging
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

@app.get(api_endpoint)
async def health_check():
    logger.debug("Health check endpoint called")
    logger.info(f"API_ENDPOINT {api_endpoint}")
    logger.info(f"LOG_LEVEL {log_level}")
    logger.debug(f"LIVE_VOLUME {read_config("/etc/name/live_volume", "not_working")}")
    return {"status": "healthy"}

@app.get("/secret")
def get_secret():
    gemini_api_key_vol = read_config("/etc/secrets/gemini_api_key")
    another_secret = read_config("/etc/secrets/name")
    return {"gemini_api_key": gemini_api_key_vol, "another_secret": another_secret}

@app.get("/")
async def root():
    return {"message": "Hello from Security Fundamentals for Daca!"}

@app.post("/messages")
async def save_message(user_id: str, message: str):
    try:
        with DaprClient() as client:
            # Save state
            state_data = {"user_id": user_id, "message": message}
            client.save_state(store_name="statestore", key=user_id, value=json.dumps(state_data))

            # Publish event
            event_data = {"user_id": user_id, "message": message}
            client.publish_event(pubsub_name="daca-pubsub", topic_name="user-chat", data=json.dumps(event_data))

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
    print("\n[DATA RAW]", type(data), data)
    # The inner "data" field is a JSON string, parse it
    try:
        event_data_raw = data.get("data", "{}")
        event_data = json.loads(event_data_raw)
    except json.JSONDecodeError as e:
        print("Failed to decode event data:", e)
        return {"status": "Invalid event data format"}
    
    user_id = event_data.get("user_id", "unknown")
    message = event_data.get("message", "no message")
    
    print(f"\n -> Received event: User {user_id} updated message to '{message}'")
    return {"status": "Event processed"}
