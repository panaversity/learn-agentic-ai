"""Chainlit app ready to run on Hugging Face Spaces."""

import logging
import os
from typing import Dict, List

import chainlit as cl
from fastapi.responses import PlainTextResponse
from openai import OpenAI
from dotenv import load_dotenv

# Load optional .env when running locally. On Spaces the secrets menu sets the key.
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("chainlit_spaces_demo")

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Add it as a Space secret or in a .env file."
    )

client = OpenAI(api_key=API_KEY)
async_openai = cl.make_async(client.responses.create)

@cl.http_router.get("/health", response_class=PlainTextResponse)
async def health_check() -> str:
    """Hugging Face calls this endpoint to see if the app is alive."""
    return "ready"

@cl.on_chat_start
async def start_chat() -> None:
    """Say hello when the Space first loads."""
    cl.user_session.set("history", [])
    await cl.Message(content="Hello from Hugging Face Spaces! How can I help?").send()

@cl.on_message
async def handle_message(message: cl.Message) -> None:
    """Send the user message plus chat history to the model and stream the reply."""
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
    except Exception as error:  # noqa: BLE001 keep broad for the lesson
        logger.error("Failed to fetch reply", exc_info=error)
        thinking.content = "Oops! Something went wrong. Check the Space logs."
        await thinking.update()
