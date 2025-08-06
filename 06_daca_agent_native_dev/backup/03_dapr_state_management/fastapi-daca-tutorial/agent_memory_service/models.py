from pydantic import BaseModel, Field
from datetime import datetime, UTC

class UserMetadata(BaseModel):
    name: str
    preferred_style: str
    goal: str

class ConversationEntry(BaseModel):
    role: str
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

class ConversationHistory(BaseModel):
    history: list[ConversationEntry] = []