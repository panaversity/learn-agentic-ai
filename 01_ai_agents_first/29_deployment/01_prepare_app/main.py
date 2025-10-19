"""Chainlit agent that uses OpenAI's managed vector store via FileSearchTool."""

from __future__ import annotations

import logging
import os

import chainlit as cl
from agents import Agent, FileSearchTool, Runner
from dotenv import load_dotenv

# Load secrets once at start-up.
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("managed_rag_chainlit")

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
VECTOR_STORE_ID = os.getenv("OPENAI_VECTOR_STORE_ID")

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is missing. Set it in .env before starting Chainlit.")

if not VECTOR_STORE_ID:
    raise RuntimeError(
        "OPENAI_VECTOR_STORE_ID is missing. Run prepare_vector_store.py or add it to .env."
    )

file_tool = FileSearchTool(vector_store_ids=[VECTOR_STORE_ID], max_num_results=3, include_search_results=True)

assistant = Agent(
    name="LibraryGuide",
    instructions=(
        "You answer questions using the uploaded study notes. Use file_search to look for relevant notes and then answer. Do not self-invent facts."
        "Explain answers in short friendly sentences. If the notes do not contain the info, say that."
    ),
    model=MODEL_NAME,
    tools=[file_tool],
)

@cl.on_chat_start
async def start_chat() -> None:
    """Warm welcome plus a place to store the conversation history."""
    cl.user_session.set("history", [])
    await cl.Message(
        content="Hi! I can read our Panaversity notes using OpenAI's managed vector store. Ask anything!"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message) -> None:
    """Send the question to the Agent SDK and stream back the answer."""
    history: list[dict[str, str]] = cl.user_session.get("history", [])
    history.append({"role": "user", "content": message.content})
    cl.user_session.set("history", history)

    logger.info("User: %s", message.content)

    thinking = cl.Message(content="Let me search our notes...")
    await thinking.send()

    try:
        result = await Runner.run(assistant, message.content)
        answer = (result.final_output or "I did not find anything useful in the notes.").strip()
        history.append({"role": "assistant", "content": answer})
        cl.user_session.set("history", history)

        thinking.content = answer
        await thinking.update()

        logger.info("Assistant: %s", answer)
    except Exception as error:  # noqa: BLE001 keep broad so learners see any issue quickly
        logger.error("Agent run failed", exc_info=error)
        thinking.content = (
            "Something went wrong while calling the managed store. "
            "Check the server log for more details."
        )
        await thinking.update()
