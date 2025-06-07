import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@pytest.mark.asyncio
async def test_chat_empty_message():
    response = client.post("/chat/", json={"user_id": "junaid", "text": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Message text cannot be empty"

