from pydantic import BaseModel

class Metadata(BaseModel):
    session_id: str | None = None
    timestamp: str | None = None
    tags: list[str] = []

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata = Metadata()

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

class ConversationEntry(BaseModel):
    role: str
    content: str