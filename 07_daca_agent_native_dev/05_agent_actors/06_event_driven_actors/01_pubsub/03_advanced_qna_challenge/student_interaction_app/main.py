import logging
import json
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone

from dapr.ext.fastapi import DaprActor, DaprApp
from dapr.actor import Actor, ActorInterface, ActorProxy, ActorId, actormethod
from dapr.clients import DaprClient

logging.basicConfig(level=logging.INFO)

APP_ID = "student-interaction-app"
PUBSUB_NAME = "student-pubsub"
STUDENT_ACTIVITY_TOPIC = "student-activity-topic"
SUBSCRIPTION_ROUTE = "/SubscriberActor/ReceiveStudentAction"

app = FastAPI(title="StudentInteractionService")
actor_extension = DaprActor(app)
dapr_app = DaprApp(app)

# Mock Questions
mock_questions = {
    "q101": "What is the capital of Pakistan?",
    "q102": "What is 2 + 2?",
    "q103": "Who is the founder of Pakistan?",
}
mock_answers = {
    "q101": "Islamabad",
    "q102": "4",
    "q103": "Quaid-e-Azam",
}


class AnswerSubmission(BaseModel):
    question_id: str
    answer_text: str


class IInteractionHandlerActor(ActorInterface):
    @actormethod(name="ProcessAnswer")
    async def process_answer(self, data: dict) -> None: pass


class InteractionHandlerActor(Actor, IInteractionHandlerActor):
    async def process_answer(self, data: dict) -> None:
        student_id = data.get("student_id")
        question_id = data.get("question_id")
        answer_given = data.get("answer_text", "").lower()
        correct_answer = mock_answers.get(question_id, "").lower()
        is_correct = answer_given == correct_answer

        logging.info(
            f"InteractionHandlerActor: Processing answer for student {student_id}, question {question_id}. Correct: {is_correct}")

        event_payload = {
            "student_id": student_id,
            "question_id": question_id,
            "answer_given": data.get("answer_text"),
            "is_correct": is_correct,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        try:
            with DaprClient() as dapr_client:
                dapr_client.publish_event(
                    pubsub_name=PUBSUB_NAME,
                    topic_name=STUDENT_ACTIVITY_TOPIC,
                    data=json.dumps(event_payload),
                    data_content_type='application/json',
                )
                logging.info(
                    f"InteractionHandlerActor: Published student_answer_processed_event for student {student_id}")
        except Exception as e:
            logging.error(
                f"InteractionHandlerActor: Error publishing event: {e}")
            # Consider retry or dead-lettering for production


@app.on_event("startup")
async def startup():
    await actor_extension.register_actor(InteractionHandlerActor)
    logging.info("StudentInteractionService with  InteractionHandlerActor")


@app.get("/learn/question/{student_id}")
async def get_question(student_id: str):
    q_id = random.choice(list(mock_questions.keys()))
    return {"student_id": student_id, "question_id": q_id, "text": mock_questions[q_id]}


@app.post("/learn/answer/{student_id}")
async def submit_answer(student_id: str, submission: AnswerSubmission):
    # Unique handler instance per attempt maybe? Or just one per student? Let's use one per interaction attempt.
    actor_id = f"handler_{student_id}_{submission.question_id}"
    logging.info(
        f"API: Received answer from student {student_id} for question {submission.question_id}")
    try:
        proxy = ActorProxy.create("InteractionHandlerActor", ActorId(actor_id), IInteractionHandlerActor)
        payload = submission.model_dump()
        payload["student_id"] = student_id  # Add student ID to payload
        await proxy.ProcessAnswer(payload)
        return {"status": "Answer received and processing initiated"}
    except Exception as e:
        logging.error(f"API: Failed to trigger InteractionHandlerActor: {e}")
        raise HTTPException(status_code=500, detail="Failed to process answer")


@dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=STUDENT_ACTIVITY_TOPIC, route=SUBSCRIPTION_ROUTE)
async def store_student_activity_handler(event_data: dict):
    logging.info(
        f"[student-interaction-app] Subscription handler received: {event_data}")
    payload = event_data.get('data', {})
    student_id = payload.get('student_id')
    logging.info(
        f"[student-interaction-app] Received event for student {student_id}")
    return {"status": "SUCCESS"}
