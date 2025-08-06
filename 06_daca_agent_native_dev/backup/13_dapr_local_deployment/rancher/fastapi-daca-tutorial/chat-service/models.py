from pydantic import BaseModel, Field
from datetime import datetime, UTC
from uuid import uuid4

class Metadata(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str = Field(default_factory=lambda: str(uuid4()))

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata | None = None
    tags: list[str] = []

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

class ConversationEntry(BaseModel):
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())