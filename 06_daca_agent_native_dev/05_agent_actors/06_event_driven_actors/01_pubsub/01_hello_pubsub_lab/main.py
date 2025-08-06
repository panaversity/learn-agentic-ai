import logging
import json
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Any # Corrected typing import

from dapr.ext.fastapi import DaprActor, DaprApp # This is the extension
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod
from dapr.clients import DaprClient

# 1. Configure Logging
logging.basicConfig(level=logging.INFO)

# 2. Define Constants
APP_ID = "pubsub-app"
PUBSUB_NAME = "daca-pubsub" # Ensure this matches your pubsub.yaml component name
PUBSUB_TOPIC = "agent-news" # Ensure this matches your subscription.yaml topic

# 3. Initialize FastAPI
app = FastAPI(title="PubSubActorService", description="Dapr Pub/Sub with Actors Example - Primary Lab")
dapr_app = DaprApp(app)


# 4. Data Models
class AgentMessage(BaseModel):
    message_id: str
    content: str
    source_agent: str

# 5. Actor Interfaces
class IPublisherActor(ActorInterface):
    @actormethod(name="PublishMessage")
    async def publish_message(self, data: dict[str, Any]) -> None: # Use dict from typing
        pass

class ISubscriberActor(ActorInterface):
    @actormethod(name="ReceiveAgentNews")
    async def receive_agent_news(self, data: dict[str, Any]) -> None: # Use dict from typing
        pass

# 6. Actor Implementations
# Note: No decorator like @actor_extension.actor_type here
class PublisherActor(Actor, IPublisherActor):
    def __init__(self, ctx, actor_id): # Standard actor constructor
        super().__init__(ctx, actor_id)

    async def _on_activate(self) -> None:
        logging.info(f"PublisherActor {self.id.id} activated.")

    async def publish_message(self, data: dict[str, Any]) -> None:
        actor_id = self.id.id
        logging.info(f"PublisherActor {actor_id}: Publishing message: {data} to topic '{PUBSUB_TOPIC}' via pubsub '{PUBSUB_NAME}'")
        try:
            # It's often better to create DaprClient instances when needed or manage them carefully
            # For actors, self.dapr_client is also available if you need to make calls from an actor to Dapr APIs
            # Make Actor Id part of the data
            data["actor_id"] = actor_id
            with DaprClient() as d_client: # Renamed to avoid conflict if self.dapr_client is used
                d_client.publish_event(
                    pubsub_name=PUBSUB_NAME,
                    topic_name=PUBSUB_TOPIC,
                    data=json.dumps(data),
                    data_content_type='application/json',
                )
            logging.info(f"PublisherActor {actor_id}: Message successfully published.")
        except Exception as e:
            logging.error(f"PublisherActor {actor_id}: Error publishing message: {e}")
            raise

class SubscriberActor(Actor, ISubscriberActor):
    def __init__(self, ctx, actor_id): # Standard actor constructor
        super().__init__(ctx, actor_id)

    async def _on_activate(self) -> None:
        logging.info(f"SubscriberActor {self.id.id} activated. Ready to receive messages on topic '{PUBSUB_TOPIC}'.")

    async def receive_agent_news(self, data: dict[str, Any]) -> None:
        logging.info(f"SubscriberActor {self.id.id}: Received message on topic '{PUBSUB_TOPIC}': {data}")
        # Add any processing logic here

# 7. Initialize DaprActor extension AFTER FastAPI app is created
#    AND AFTER actor classes are defined.
actor_extension = DaprActor(app)

# 8. Register Actors with the DaprActor extension
@app.on_event("startup")
async def startup_event():
    await actor_extension.register_actor(PublisherActor)
    await actor_extension.register_actor(SubscriberActor)
    logging.info("Registered PublisherActor and SubscriberActor.")

# 9. FastAPI Endpoint to Trigger Publisher
@app.post("/publish/{publisher_actor_id}")
async def trigger_publish_message(
    publisher_actor_id: str,
    message: AgentMessage = Body(...)
):
    logging.info(f"API: Received request for PublisherActor {publisher_actor_id} to publish: {message.content}")
    try:
        # DaprClient for proxy creation should be managed correctly,
        # it's often fine to create it on-demand for one-off calls.
        proxy = ActorProxy.create("PublisherActor", ActorId(publisher_actor_id), IPublisherActor)
        await proxy.PublishMessage(message.model_dump())
        return {"status": "Message publishing initiated", "actor_id": publisher_actor_id, "message_content": message.content}
    except Exception as e:
        logging.error(f"API: Error invoking PublisherActor {publisher_actor_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 10. Health Check
@app.get("/health")
async def health_check():
    return {"status": "OK", "app_id": APP_ID}



@dapr_app.subscribe(pubsub="daca-pubsub", topic="agent-news", route="/SubscriberActor/ReceiveAgentNews")
async def receive_agent_news(data: dict):
    """Receive agent news from pub/sub."""
    logging.info(f"\n\n->[SUBSCRIPTION] Received Agent News: {data}\n\n")
    event_data = data.get("data", "{}")
    actor_id = event_data.get("actor_id", "unknown")    
    logging.info(f"Received event: Actor {actor_id} ")
    proxy = ActorProxy.create("SubscriberActor", ActorId(actor_id), ISubscriberActor)
    await proxy.ReceiveAgentNews(data)
    
    return {"status": "SUCCESS"}