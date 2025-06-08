# Writing Unit Tests with Pytest

### Why Unit Tests?

Unit tests ensure your API endpoints behave as expected, catching bugs early. In DACA, testing is crucial as we’ll integrate with Dapr, OpenAI Agents SDK, and other components.

## Setup

Get code from step 02 and let's write unit tests for it

### Create a Test File

Create a directory for tests and a test file:

```bash
touch test_chat.py
````

Add the following to `test_chat.py`:

```python
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
```

### Run the Tests

```bash
uv run pytest test_chat.py -v
```

Output:

```
collected 3 items

tests/test_chat.py::test_root PASSED
tests/test_chat.py::test_get_user PASSED
tests/test_chat.py::test_chat PASSED

================= 3 passed in 0.36s =================
```

### Explanation of the Tests

1. **Test Client**:
   - `TestClient(app)`: Creates a client to simulate HTTP requests to the FastAPI app.
2. **Tests**:
   - `test_root`: Tests the root endpoint (`GET /`).
   - `test_get_user`: Tests the `/users/{user_id}` endpoint with and without query parameters.
   - `test_chat`: Tests the `/chat/` endpoint with both valid and invalid requests, including nested `metadata`.

## Why FastAPI and Pydantic for DACA?

- **FastAPI**:
  - **Asynchronous Support**: Handles high-concurrency workloads.
  - **Automatic Docs**: Simplifies testing and integration.
  - **Scalability**: Stateless design fits DACA’s containerized architecture.
- **Pydantic**:
  - **Data Integrity**: Ensures type-safe data for agentic workflows.
  - **Complex Models**: Supports nested structures for rich data (e.g., metadata, tags).
  - **Error Handling**: Provides clear validation errors for debugging.

---