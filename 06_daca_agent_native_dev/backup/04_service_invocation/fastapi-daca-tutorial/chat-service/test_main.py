import httpx
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch

# Create a test client
client = TestClient(app)

# Test the root endpoint


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."
    }

# Mock the OpenAI Agents SDK Runner
@pytest.mark.asyncio
async def test_chat():
    with patch("main.Runner.run", new_callable=AsyncMock) as mock_run, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Mock the Dapr Service Invocation response
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"past_actions": ["scheduled a meeting", "analyzed data"]})
        mock_run.return_value.final_output = "Hi Alice! I see you’ve scheduled a meeting and analyzed data before. How can I assist you today?"
        
        request_data = {
            "user_id": "alice",
            "text": "Hello, how are you?",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            },
            "tags": ["greeting"]
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["user_id"] == "alice"
        assert response.json()["reply"] == "Hi Alice! I see you’ve scheduled a meeting and analyzed data before. How can I assist you today?"
        assert "metadata" in response.json()

        # Mock a tool-using response
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"past_actions": ["wrote a report"]})
        mock_run.return_value.final_output = "Bob, you’ve written a report before. The current time is 2025-04-06 04:01:23 UTC."
        request_data = {
            "user_id": "bob",
            "text": "What time is it?",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174001"
            },
            "tags": ["question"]
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["user_id"] == "bob"
        assert response.json()["reply"] == "Bob, you’ve written a report before. The current time is 2025-04-06 04:01:23 UTC."
        assert "metadata" in response.json()

        # Test failure of Agent Memory Service via Dapr
        mock_get.side_effect = httpx.HTTPStatusError(
            message="Not Found", request=AsyncMock(), response=AsyncMock(status_code=404)
        )
        mock_run.return_value.final_output = "Hi Alice! How can I help you today?"
        request_data = {
            "user_id": "alice",
            "text": "Hello again!",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 200
        assert response.json()["reply"] == "Hi Alice! How can I help you today?"

        # Invalid request
        request_data = {
            "user_id": "bob",
            "text": "",
            "metadata": {
                "timestamp": "2025-04-06T12:00:00Z",
                "session_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }
        response = client.post("/chat/", json=request_data)
        assert response.status_code == 400
        assert response.json() == {"detail": "Message text cannot be empty"}