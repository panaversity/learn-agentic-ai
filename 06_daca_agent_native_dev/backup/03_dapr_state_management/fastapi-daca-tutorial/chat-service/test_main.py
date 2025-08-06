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
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        # Mock metadata and history responses
        mock_get.side_effect = [
            AsyncMock(status_code=200, json=lambda: {"name": "Alice", "preferred_style": "formal", "goal": "schedule tasks"}),
            AsyncMock(status_code=200, json=lambda: {"history": []})
        ]
        mock_run.return_value.final_output = "Greetings, Alice!"
        mock_post.return_value = AsyncMock(status_code=200)

        request_data = {
            "user_id": "alice",
            "text": "Hello",
            "tags": ["greeting"]
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["reply"] == "Greetings, Alice!"
        assert "session_id" in response.json()["metadata"]