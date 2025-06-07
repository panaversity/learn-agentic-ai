import logging
import json
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone

from dapr.ext.fastapi import DaprActor, DaprApp
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod
from dapr.clients import DaprClient

logging.basicConfig(level=logging.INFO)

APP_ID = "learning-analytics-app"
PUBSUB_NAME = "student-pubsub"
STUDENT_ACTIVITY_TOPIC = "student-activity-topic"
TEACHER_NOTIFICATIONS_TOPIC = "teacher-notifications-topic"
TEACHER_NOTIFICATIONS_ROUTE = '/SubscriberActor/ReceiveTeacherNotification'
STUDENT_ACTIVITY_SUBSCRIPTION_ROUTE = "/SubscriberActor/ReceiveStudentAction"

# Number of incorrect answers to trigger alert
STRUGGLE_THRESHOLD = 3

app = FastAPI(title="LearningAnalyticsService")
actor_extension = DaprActor(app)
dapr_app = DaprApp(app)


class IStudentAnalyticsActor(ActorInterface):
    @actormethod(name="ProcessAnswerEvent")
    async def process_answer_event(self, event_data: dict) -> None:
        pass


class StudentAnalyticsActor(Actor, IStudentAnalyticsActor):
    def __init__(self, ctx, actor_id):
        super().__init__(ctx, actor_id)
        # State tracks recent performance for triggering alerts
        # list of recent bool (is_correct)
        self._recent_answers_key: str = "recent_answers"

    async def _on_activate(self) -> None:
        exists = await self._state_manager.contains_state(self._recent_answers_key)
        if not exists:
            await self._state_manager.set_state(self._recent_answers_key, [])
        logging.info(f"StudentAnalyticsActor {self.id.id} activated.")

    async def process_answer_event(self, event_data: dict):
        student_id = self.id.id
        is_correct = event_data.get('is_correct')
        question_id = event_data.get('question_id')
        logging.info(
            f"StudentAnalyticsActor {student_id}: Processing event for question {question_id}. Correct: {is_correct}")

        if is_correct is None:
            logging.warning(
                f"StudentAnalyticsActor {student_id}: Received event without 'is_correct' flag.")
            return

        try:
            recent_answers = await self._state_manager.get_state(self._recent_answers_key)
            if recent_answers is None:
                recent_answers = []
            recent_answers.append(is_correct)
            # Keep only the last N answers relevant for threshold check
            recent_answers = recent_answers[-STRUGGLE_THRESHOLD:]
            await self._state_manager.save_state()

            # Check if student is struggling
            # All last N were incorrect
            # if len(recent_answers) >= STRUGGLE_THRESHOLD and not any(recent_answers):
            # For now, just log the event
            logging.warning(
                f"StudentAnalyticsActor {student_id}: Struggle detected! Threshold: {STRUGGLE_THRESHOLD}")
            # Publish assistance required event
            assistance_payload = {
                "student_id": student_id,
                "reason": f"Struggled with last {STRUGGLE_THRESHOLD} questions.",
                "triggering_question_id": question_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            with DaprClient() as dapr_client:
                dapr_client.publish_event(
                    pubsub_name=PUBSUB_NAME,
                    topic_name=TEACHER_NOTIFICATIONS_TOPIC,
                    data=json.dumps(assistance_payload),
                    data_content_type='application/json',
                )
                logging.info(
                    f"StudentAnalyticsActor {student_id}: Published student_assistance_required_event")
                # Reset recent answers after alert? Optional logic.
                await self._state_manager.set_state(self._recent_answers_key, [])
                await self._state_manager.save_state()

        except Exception as e:
            logging.error(
                f"StudentAnalyticsActor {student_id}: Error processing event: {e}")


@app.on_event("startup")
async def startup():
    await actor_extension.register_actor(StudentAnalyticsActor)
    logging.info("LearningAnalyticsService with StudentAnalyticsActor")

# # Subscription handler


@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=STUDENT_ACTIVITY_TOPIC, route=STUDENT_ACTIVITY_SUBSCRIPTION_ROUTE)
async def analyze_student_activity_handler(event_data: dict):
    logging.info(
        f"[analytics-app] Subscription handler received: {event_data}")
    payload = event_data.get('data', {})
    student_id = payload.get('student_id')

    if not student_id:
        logging.error("[analytics-app] Received event without student_id.")
        return {"status": "REJECTED_NO_STUDENT_ID"}

    try:
        proxy = ActorProxy.create("StudentAnalyticsActor", ActorId(
            student_id), IStudentAnalyticsActor)
        await proxy.ProcessAnswerEvent(payload)
        return {"status": "SUCCESS"}
    except Exception as e:
        logging.error(
            f"[analytics-app] Failed to proxy to StudentAnalyticsActor for {student_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to analyze interaction")
