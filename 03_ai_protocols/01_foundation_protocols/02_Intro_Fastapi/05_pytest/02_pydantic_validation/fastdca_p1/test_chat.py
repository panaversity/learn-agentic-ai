import pytest
from fastapi.testclient import TestClient
from main import app

# Create a test client
client = TestClient(app)

# Test the root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."
    }

# Test the /users/{user_id} endpoint
def test_get_user():
    response = client.get("/users/alice?role=admin")
    assert response.status_code == 200
    assert response.json() == {"user_id": "alice", "role": "admin"}

    response = client.get("/users/bob")
    assert response.status_code == 200
    assert response.json() == {"user_id": "bob", "role": "guest"}

# Test the /chat/ endpoint (async test)
@pytest.mark.asyncio
async def test_chat():
    # Valid request
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
    assert response.json()["reply"] == "Hello, alice! You said: 'Hello, how are you?'. How can I assist you today?"
    assert "metadata" in response.json()

    # Invalid request (empty text)
    invalid_data = {
        "user_id": "bob",
        "text": "",
        "metadata": {
            "timestamp": "2025-04-06T12:00:00Z",
            "session_id": "123e4567-e89b-12d3-a456-426614174001"
        }
    }
    response = client.post("/chat/", json=invalid_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Message text cannot be empty"}