import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."
    }

@pytest.mark.asyncio
async def test_chat():
    with patch("main.Runner.run", new_callable=AsyncMock) as mock_run, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("main.publish_conversation_event", new_callable=AsyncMock) as mock_publish:
        mock_get.side_effect = [
            AsyncMock(status_code=200, json=lambda: {"name": "Junaid", "preferred_style": "formal", "user_summary": "Junaid is a new user."}),
            AsyncMock(status_code=200, json=lambda: {"history": []})
        ]
        mock_run.return_value.final_output = "Greetings, Junaid! How may I assist you today?"
        request_data = {"user_id": "junaid", "text": "Hello", "tags": ["greeting"]}
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["reply"] == "Greetings, Junaid! How may I assist you today?"
        mock_publish.assert_called_once()
