from pydantic import BaseModel

class Memories(BaseModel):
    past_actions: list[str]