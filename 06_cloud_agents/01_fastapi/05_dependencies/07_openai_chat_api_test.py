# Run pytest 07_openai_chat_api_test.py -s to run the output:
# We are overriding the OpenAI ChatCompletion dependency in this test file
# This test passes without calling the openai chatcompletions API.

from fastapi.testclient import TestClient
from openai_chat_api import app, chat_completion

test_db = ["Test DB"]

def fake_chat_completion():
    """
    Simulates a chat completion by returning a predefined message.

    Returns:
        str: The predefined message "hello".
    """
    return "hello"

# Comment out this line to stop overriding the dependency
app.dependency_overrides[chat_completion] = fake_chat_completion
client = TestClient(app)

def test_item_should_add_to_database():
    response = client.get("/chat/hello")

    assert response.status_code == 200
    assert response.json() ==  {"openai": "hello"}