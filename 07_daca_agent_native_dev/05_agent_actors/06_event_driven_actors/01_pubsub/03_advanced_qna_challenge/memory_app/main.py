import logging
from fastapi import FastAPI, HTTPException

from dapr.ext.fastapi import DaprActor, DaprApp
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod

logging.basicConfig(level=logging.INFO)

APP_ID = "memory-app"
PUBSUB_NAME = "student-pubsub"
STUDENT_ACTIVITY_TOPIC = "student-activity-topic"
SUBSCRIPTION_ROUTE = "/SubscriberActor/ReceiveStudentAction"

app = FastAPI(title="MemoryService")
actor_extension = DaprActor(app)
dapr_app = DaprApp(app)


class IStudentMemoryActor(ActorInterface):
    @actormethod(name="RecordInteraction")
    async def record_interaction(self, interaction_data: dict) -> None:
        pass

    @actormethod(name="GetHistory")
    async def get_history(self) -> list[dict] | None:
        pass  # Optional: For debugging/viewing state


class StudentMemoryActor(Actor, IStudentMemoryActor):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        self._state_key = "interaction_history"

    async def _on_activate(self) -> None:
        exists = await self._state_manager.contains_state(self._state_key)
        if not exists:
            await self._state_manager.set_state(self._state_key, [])
        logging.info(f"StudentMemoryActor {self.id.id} activated.")

    async def record_interaction(self, interaction_data: dict):
        logging.info(
            f"StudentMemoryActor {self.id.id}: Recording interaction: {interaction_data}")
        try:
            history = await self._state_manager.get_state(self._state_key)
            if history is None:
                history = []
            history.append(interaction_data)
            # Optional: Limit history size
            # history = history[-100:]
            # Save state implicitly includes the updated history
            await self._state_manager.save_state()
            logging.info(
                f"StudentMemoryActor {self.id.id}: Interaction recorded. History length: {len(history)}")
        except Exception as e:
            logging.error(
                f"StudentMemoryActor {self.id.id}: Failed to record interaction: {e}")

    async def get_history(self) -> list[dict]:
        history = await self._state_manager.get_state(self._state_key)
        return history if history else []


@app.on_event("startup")
async def startup():
    await actor_extension.register_actor(StudentMemoryActor)
    logging.info("MemoryService with StudentMemoryActor")

# # Subscription handler


@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=STUDENT_ACTIVITY_TOPIC, route=SUBSCRIPTION_ROUTE)
async def store_student_activity_handler(event_data: dict):
    logging.info(f"[memory-app] Subscription handler received: {event_data}")
    payload = event_data.get('data', {})
    student_id = payload.get('student_id')

    if not student_id:
        logging.error("[memory-app] Received event without student_id.")
        # Optionally return error status - check Dapr docs for pub/sub error handling (e.g., 4xx to prevent retry, 5xx for retry)
        return {"status": "REJECTED_NO_STUDENT_ID"}

    try:
        proxy = ActorProxy.create("StudentMemoryActor", ActorId(
            student_id), IStudentMemoryActor)
        await proxy.RecordInteraction(payload)
        return {"status": "SUCCESS"}
    except Exception as e:
        logging.error(
            f"[memory-app] Failed to proxy to StudentMemoryActor for {student_id}: {e}")
        # Decide on retry strategy - returning non-2xx status might trigger Dapr retry/deadlettering
        raise HTTPException(
            status_code=500, detail="Failed to store interaction")

# Optional: Endpoint to view history for debugging


@app.get("/memory/{student_id}")
async def get_student_memory(student_id: str):
    try:
        proxy = ActorProxy.create("StudentMemoryActor", ActorId(
            student_id), IStudentMemoryActor)
        history = await proxy.GetHistory()
        return {"student_id": student_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
