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
        mock_get.return_value = {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid enjoys coding."}
        response = client.get("/memories/junaid")
        assert response.status_code == 200
        assert response.json() == {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid enjoys coding."}

@pytest.mark.asyncio
async def test_initialize_memories():
    with patch("main.set_user_metadata", new_callable=AsyncMock) as mock_set:
        metadata = {"name": "Junaid", "preferred_style": "casual", "user_summary": "Junaid is a new user."}
        response = client.post("/memories/junaid/initialize", json=metadata)
        assert response.status_code == 200
        assert response.json() == {"status": "success", "user_id": "junaid", "metadata": metadata}

@pytest.mark.asyncio
async def test_conversation():
    with patch("main.get_conversation_history", new_callable=AsyncMock) as mock_get_history, \
         patch("main.set_conversation_history", new_callable=AsyncMock) as mock_set_history, \
         patch("main.get_user_metadata", new_callable=AsyncMock) as mock_get_meta, \
         patch("main.set_user_metadata", new_callable=AsyncMock) as mock_set_meta, \
         patch("main.generate_user_summary", new_callable=AsyncMock) as mock_summary:
        mock_get_history.return_value = [{"role": "user", "content": "Hi", "timestamp": "2025-04-07T15:00:00Z"}]
        mock_get_meta.return_value = {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid is a new user."}
        mock_summary.return_value = "Junaid enjoys coding."
        response = client.get("/conversations/session123")
        assert response.status_code == 200
        assert len(response.json()["history"]) == 1

        event = {
            "event_type": "ConversationUpdated",
            "user_id": "junaid",
            "session_id": "session123",
            "user_message": "Hello",
            "assistant_reply": "Hi Junaid!"
        }
        response = client.post("/conversations", json=event)
        assert response.status_code == 200
        assert response.json()["status"] == "ignored"