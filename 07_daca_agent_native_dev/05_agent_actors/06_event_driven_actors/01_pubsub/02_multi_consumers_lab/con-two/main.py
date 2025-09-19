import logging
from fastapi import FastAPI

from dapr.ext.fastapi import DaprApp # This is the extension
# 1. Configure Logging
logging.basicConfig(level=logging.INFO)

# 2. Define Constants
APP_ID = "con-two"
PUBSUB_NAME = "daca-pubsub" # Ensure this matches your pubsub.yaml component name
PUBSUB_TOPIC = "agent-news" # Ensure this matches your subscription.yaml topic

# 3. Initialize FastAPI
app = FastAPI(title=APP_ID, description=f"Dapr Pub/Sub Consumer 2 - {APP_ID}")
dapr_app = DaprApp(app)


@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=PUBSUB_TOPIC, route="/SubscriberActor/ReceiveAgentNews")
async def receive_agent_news(data: dict):
    """Receive agent news from pub/sub."""
    logging.info(f"\n\n->[SUBSCRIPTION] Received Agent News: {data}\n\n")

    return {"status": "SUCCESS"}