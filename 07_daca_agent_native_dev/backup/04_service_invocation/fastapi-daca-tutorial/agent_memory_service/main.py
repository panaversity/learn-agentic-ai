from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Memories

app = FastAPI(
    title="Agent Memory Service",
    description="Provides procedural memories for AI agents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Allow Chat Service
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock procedural memories (e.g., past actions)
MOCK_MEMORIES = {
    "alice": {"past_actions": ["scheduled a meeting", "analyzed data"]},
    "bob": {"past_actions": ["wrote a report"]}
}

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent Memory Service!"}

@app.get("/memories/{user_id}", response_model=Memories)
async def get_memories(user_id: str):
    if user_id not in MOCK_MEMORIES:
        raise HTTPException(status_code=404, detail="User not found")
    return Memories(**MOCK_MEMORIES[user_id])