"""Simple Chainlit app made ready for sharing."""

import logging
import os
from typing import List, Dict

import chainlit as cl
from fastapi.responses import PlainTextResponse
from openai import OpenAI
from dotenv import load_dotenv

# Load keys from .env at start so the app fails fast if the file is missing.
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("chainlit_deploy_demo")

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Set it in a .env file before starting Chainlit."
    )

client = OpenAI(api_key=API_KEY)
async_openai = cl.make_async(client.responses.create)

@cl.http_router.get("/health", response_class=PlainTextResponse)
async def health_check() -> str:
    """Used by hosts to see if the app is alive."""
    return "ready"

@cl.on_chat_start
async def start_chat() -> None:
    """Say hello and prepare a place to store the chat history."""
    cl.user_session.set("history", [])
    await cl.Message(content="Hi there! I am ready to answer your questions.").send()

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
    except Exception as error:  # noqa: BLE001 broad to keep lesson simple
        logger.error("Failed to fetch reply", exc_info=error)
        thinking.content = "Oops! Something went wrong. Check the server log."
        await thinking.update()
