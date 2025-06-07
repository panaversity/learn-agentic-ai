from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Metadata(SQLModel):
    name: str
    preferred_style: str
    user_summary: str

class ConversationEntry(SQLModel):
    role: str
    content: str


class Conversation(ConversationEntry, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationResponse(SQLModel):
    history: list[ConversationEntry] = []
    session_id: str
    user_id: str
