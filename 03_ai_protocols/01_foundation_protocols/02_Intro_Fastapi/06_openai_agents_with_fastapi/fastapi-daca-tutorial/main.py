import json
import os
from uuid import uuid4
from typing import cast

from dotenv import load_dotenv

from pydantic import BaseModel, Field
from datetime import datetime, UTC

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

# Import OpenAI Agents SDK
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=cast(ModelProvider, external_client), # satisfy type checker
    tracing_disabled=True
)

# Initialize the FastAPI app
app = FastAPI(
    title="DACA Chatbot API",
    description="A FastAPI-based API for a chatbot in the DACA tutorial series",
    version="0.1.0",
)

# Pydantic models
class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str = Field(default_factory=lambda: str(uuid4()))


class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata | None = None
    tags: list[str] | None = None


class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

# Create a tool to fetch the current time
@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


# Create an AI agent using OpenAI Agents SDK
chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool.",
    tools=[get_current_time],  # Add the time tool
    model=model
)

# Root endpoint


@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}

# GET endpoint with query parameters


@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

# POST endpoint for chatting


@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")

    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text, run_config=config)
    reply_text = result.final_output  # Get the agent's response

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )


# POST endpoint for chatting
async def stream_response(message: Message):
    result = Runner.run_streamed(chat_agent, input=message.text, run_config=config)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
            # Serialize dictionary to JSON string
            chunk = json.dumps({"chunk": event.data.delta})
            yield f"data: {chunk}\n\n"
            
@app.post("/chat/stream", response_model=Response)
async def chat_stream(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")

    return StreamingResponse(
        stream_response(message),
        media_type="text/event-stream"
    )
