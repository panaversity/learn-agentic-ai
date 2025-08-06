@echo off
start cmd /k "cd agent_memory_service && uv run fastapi dev"
start cmd /k "cd chat-service && uv run fastapi dev"
