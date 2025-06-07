import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Agent Memory Service! Access /docs for the API documentation."
    }

@pytest.mark.asyncio
async def test_get_memories():
    with patch("main.get_user_metadata", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"name": "Alice", "preferred_style": "formal", "goal": "schedule tasks"}
        response = client.get("/memories/alice")
        assert response.status_code == 200
        assert response.json() == {"name": "Alice", "preferred_style": "formal", "goal": "schedule tasks"}

@pytest.mark.asyncio
async def test_initialize_memories():
    with patch("main.set_user_metadata", new_callable=AsyncMock) as mock_set:
        metadata = {"name": "Bob", "preferred_style": "casual", "goal": "learn coding"}
        response = client.post("/memories/bob/initialize", json=metadata)
        assert response.status_code == 200
        assert response.json() == {"status": "success", "user_id": "bob", "metadata": metadata}

@pytest.mark.asyncio
async def test_conversation():
    with patch("main.get_conversation_history", new_callable=AsyncMock) as mock_get, \
         patch("main.set_conversation_history", new_callable=AsyncMock) as mock_set:
        mock_get.return_value = [{"role": "user", "content": "Hi", "timestamp": "2025-04-07T15:00:00Z"}]
        response = client.get("/conversations/session123")
        assert response.status_code == 200
        assert len(response.json()["history"]) == 1

        history = {"history": [{"role": "assistant", "content": "Hello!", "timestamp": "2025-04-07T15:01:00Z"}]}
        response = client.post("/conversations/session123", json=history)
        assert response.status_code == 200
        assert response.json()["status"] == "success"