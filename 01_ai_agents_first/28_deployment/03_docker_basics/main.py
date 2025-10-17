"""Chainlit app running inside Docker."""

import logging
import os
from typing import Dict, List

import chainlit as cl
from dotenv import load_dotenv
from fastapi.responses import PlainTextResponse
from openai import OpenAI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("chainlit_docker_demo")

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Pass it with -e OPENAI_API_KEY=... when you run the container."
    )

client = OpenAI(api_key=API_KEY)
async_openai = cl.make_async(client.responses.create)

@cl.http_router.get("/health", response_class=PlainTextResponse)
async def health_check() -> str:
    """Render and Railway call this path to make sure the app is alive."""
    return "ready"

@cl.on_chat_start
async def start_chat() -> None:
    """Say hello and get ready to store the conversation."""
    cl.user_session.set("history", [])
    await cl.Message(content="Hi! I am chatting from inside a Docker container.").send()

@cl.on_message
async def handle_message(message: cl.Message) -> None:
    """Send the message to the model and stream back the answer."""
    history: List[Dict[str, str]] = cl.user_session.get("history", [])
    history.append({"role": "user", "content": message.content})
    cl.user_session.set("history", history)

    logger.info("User: %s", message.content)

    thinking = cl.Message(content="Thinking...")
    await thinking.send()

    try:
        response = await async_openai(
            model=MODEL_NAME,
            input=[{"role": "system", "content": "You help kindly and clearly."}, *history],
        )
        answer = (response.output_text or "I do not have an answer yet.").strip()

        history.append({"role": "assistant", "content": answer})
        cl.user_session.set("history", history)

        thinking.content = answer
        await thinking.update()

        logger.info("Assistant: %s", answer)
    except Exception as error:  # noqa: BLE001 keep broad for lesson clarity
        logger.error("OpenAI call failed", exc_info=error)
        thinking.content = "Oops! Something went wrong inside the container."
        await thinking.update()