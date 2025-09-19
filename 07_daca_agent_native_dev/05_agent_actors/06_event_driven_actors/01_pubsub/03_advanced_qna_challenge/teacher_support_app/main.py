import logging
from fastapi import FastAPI, HTTPException

from dapr.ext.fastapi import DaprActor, DaprApp
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod

logging.basicConfig(level=logging.INFO)

APP_ID = "teacher-support-app"
PUBSUB_NAME = "student-pubsub"
TEACHER_NOTIFICATIONS_TOPIC = "teacher-notifications-topic"
TEACHER_NOTIFICATIONS_ROUTE = '/SubscriberActor/ReceiveTeacherNotification'

app = FastAPI(title="TeacherSupportService")
actor_extension = DaprActor(app)
dapr_app = DaprApp(app)

# Mock Resources
mock_resources = {
    "topic_capitals": ["wiki/Capitals", "video/EuropeanCapitals"],
    "topic_math": ["khanacademy/basic-arithmetic", "math-games/addition"],
    "topic_elements": ["periodic-table.com", "chem-guide/oxygen"],
    "default": ["general-study-tips.com"]
}

class ITeacherSupportAgentActor(ActorInterface):
    @actormethod(name="HandleAssistanceRequest")
    async def handle_assistance_request(self, request_data: dict) -> None:
        pass

class TeacherSupportAgentActor(Actor, ITeacherSupportAgentActor):
    async def _on_activate(self) -> None:
        logging.info(f"TeacherSupportAgentActor {self.id.id} activated.")

    async def handle_assistance_request(self, request_data: dict):
        student_id = request_data.get("student_id", "Unknown")
        reason = request_data.get("reason", "No reason provided")
        triggering_question = request_data.get("triggering_question_id", "N/A")
        logging.warning(f"ALERT for Teacher Actor {self.id.id}: Student {student_id} requires assistance. Reason: {reason}. Trigger Question: {triggering_question}")

        # Simulate resource curation based on reason/question (very basic)
        resources = mock_resources.get("default")
        if "capitals" in reason.lower() or triggering_question == "q101":
            resources = mock_resources["topic_capitals"]
        elif "math" in reason.lower() or triggering_question == "q102":
            resources = mock_resources["topic_math"]
        elif "element" in reason.lower() or triggering_question == "q103":
            resources = mock_resources["topic_elements"]

        logging.info(f"Teacher Actor {self.id.id}: Curated resources for {student_id}: {resources}")

        # Simulate sending email
        logging.info(f"Teacher Actor {self.id.id}: SIMULATING email send to {student_id} with resources {resources}.")
        # In a real app, integrate with an email service (e.g., via Dapr output binding or SDK)

@app.on_event("startup")
async def startup():
    await actor_extension.register_actor(TeacherSupportAgentActor)

# Subscription handler
@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=TEACHER_NOTIFICATIONS_TOPIC, route=TEACHER_NOTIFICATIONS_ROUTE)
async def handle_assistance_request_handler(event_data: dict):
    logging.info(f"[teacher-support-app] Subscription handler received: {event_data}")
    payload = event_data.get('data', {})
    student_id = payload.get('student_id') # Used mainly for context/logging here

    # Assign to a specific teacher agent or a pool - using singleton for simplicity
    teacher_actor_id = "primaryTeacherAgent"

    if not student_id:
        logging.error("[teacher-support-app] Received assistance request without student_id.")
        return {"status": "REJECTED_NO_STUDENT_ID"}

    try:
        proxy = ActorProxy.create("TeacherSupportAgentActor", ActorId(teacher_actor_id), ITeacherSupportAgentActor)
        await proxy.HandleAssistanceRequest(payload)
        return {"status": "SUCCESS"}
    except Exception as e:
        logging.error(f"[teacher-support-app] Failed to proxy to TeacherSupportAgentActor for {student_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to handle assistance request")