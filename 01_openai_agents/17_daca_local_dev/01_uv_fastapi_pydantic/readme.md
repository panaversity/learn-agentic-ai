# Getting Started with FastAPI, UV, and Pydantic 

Welcome to the first tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this baby step, we’ll set up a FastAPI project using the `uv` Python dependency manager, dive deep into FastAPI and Pydantic, and build a more robust API with unit tests, CORS middleware, and complex data models. FastAPI will serve as the REST API layer for our agentic AI system, enabling communication between users, agents, and microservices. Let’s get started!

---

## What You’ll Learn
- How to install and use the `uv` Python dependency manager.
- Setting up a FastAPI project with `uv`.
- Understanding FastAPI’s key features: automatic documentation, async support, and Pydantic integration.
- A deep dive into Pydantic for data validation and serialization.
- Building a FastAPI application with complex Pydantic models.
- Adding CORS middleware for cross-origin requests.
- Writing unit tests with `pytest` to ensure API reliability.
- Testing and running the API with practical examples.

## Prerequisites
- Python 3.12+ installed on your system.
- Basic familiarity with Python, command-line tools, and REST APIs.
- A code editor (e.g., VS Code).

---

## Step 1: Introduction to UV Python Dependency Manager
### What is UV?
`uv` is a modern, fast, and lightweight Python dependency manager built by the team at **Astral**. It’s designed to replace tools like `pip` and `virtualenv` by providing a unified, high-performance solution for managing Python projects. Key features include:

- **Speed**: Blazing fast dependency resolution and installation (written in Rust).
- **Unified Workflow**: Combines dependency management, virtual environment creation, and project setup.
- **Locking**: Generates a `uv.lock` file for reproducible builds.
- **Modern Features**: Supports PEP 582 (no need to activate virtualenvs manually in supported environments).

`uv` is ideal for DACA projects as it streamlines dependency management for FastAPI, Dapr, and other components.

### Installing UV
#### On macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### On Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Verify Installation
```bash
uv --version
```
You should see output like `uv 0.4.18` (or the latest version).

---

## Step 2: Setting Up a FastAPI Project with UV
### Create a Project Directory
```bash
mkdir fastapi-daca-tutorial
cd fastapi-daca-tutorial
```

### Initialize a Python Project with UV
```bash
uv init
```
This creates:
- A `pyproject.toml` file for project metadata and dependencies.
- A virtual environment (`.venv`).

### Activate the Virtual Environment
On macOS/Linux:
```bash
source .venv/bin/activate
```
On Windows:
```bash
.venv\Scripts\activate
```

**Note**: With PEP 582 support (Python 3.11+), `uv` may not require manual activation for running commands.

### Add Dependencies
We’ll need FastAPI, Uvicorn (ASGI server), and additional packages for testing:
```bash
uv add fastapi uvicorn pytest pytest-asyncio httpx
```
- `fastapi`: The web framework.
- `uvicorn`: The ASGI server to run the app.
- `pytest` and `pytest-asyncio`: For unit testing.
- `httpx`: An HTTP client for testing FastAPI endpoints.

This updates `pyproject.toml`:
```toml
[project]
name = "fastapi-daca-tutorial"
version = "0.1.0"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.30.6",
    "pytest>=8.3.3",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.2",
]
```

Verify the installed dependencies:
```bash
uv pip list
```

---

## Step 3: Deep Dive into Pydantic
### What is Pydantic?
Pydantic is a data validation and settings management library that uses Python type annotations to define and validate data schemas. It’s a core dependency of FastAPI, used for request/response validation, serialization, and deserialization. Pydantic ensures type safety and provides automatic error handling, making it ideal for DACA’s agentic workflows where data integrity is critical.

### Key Features of Pydantic
- **Type-Safe Validation**: Validates data against Python type hints (e.g., `str`, `int`, `List[str]`).
- **Automatic Conversion**: Converts data to the correct type (e.g., string `"123"` to `int` 123).
- **Error Handling**: Raises detailed validation errors for invalid data.
- **Nested Models**: Supports complex, nested data structures.
- **Serialization**: Converts models to JSON (or other formats) for API responses.
- **Default Values and Optional Fields**: Simplifies schema definitions.
- **Custom Validators**: Allows custom validation logic.

### Getting Started with Pydantic
Let’s explore Pydantic with examples before integrating it into our FastAPI app.

#### Basic Pydantic Model
Create a file named `pydantic_examples.py`:
```python
from pydantic import BaseModel, ValidationError

# Define a simple model
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int | None = None  # Optional field with default None

# Valid data
user_data = {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25}
user = User(**user_data)
print(user)  # id=1 name='Alice' email='alice@example.com' age=25
print(user.dict())  # {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', 'age': 25}

# Invalid data (will raise an error)
try:
    invalid_user = User(id="not_an_int", name="Bob", email="bob@example.com")
except ValidationError as e:
    print(e)
```

Run the script:
```bash
uv run python pydantic_examples.py
```
Output for invalid data:
```
1 validation error for User
id
  value is not a valid integer (type=type_error.integer)
```

#### Nested Models
Pydantic supports nested structures, which we’ll use in our FastAPI app. Extend `pydantic_examples.py`:
```python
from pydantic import BaseModel, EmailStr
from typing import List

# Define a nested model
class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class UserWithAddress(BaseModel):
    id: int
    name: str
    email: EmailStr  # Built-in validator for email format
    addresses: List[Address]  # List of nested Address models

# Valid data with nested structure
user_data = {
    "id": 2,
    "name": "Bob",
    "email": "bob@example.com",
    "addresses": [
        {"street": "123 Main St", "city": "New York", "zip_code": "10001"},
        {"street": "456 Oak Ave", "city": "Los Angeles", "zip_code": "90001"},
    ],
}
user = UserWithAddress(**user_data)
print(user.dict())
```

Output:
```json
{
    'id': 2,
    'name': 'Bob',
    'email': 'bob@example.com',
    'addresses': [
        {'street': '123 Main St', 'city': 'New York', 'zip_code': '10001'},
        {'street': '456 Oak Ave', 'city': 'Los Angeles', 'zip_code': '90001'}
    ]
}
```

#### Custom Validators
Add a custom validator to ensure the user’s name is at least 2 characters long:
```python
from pydantic import BaseModel, EmailStr, validator
from typing import List

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class UserWithAddress(BaseModel):
    id: int
    name: str
    email: EmailStr
    addresses: List[Address]

    @validator("name")
    def name_must_be_at_least_two_chars(cls, v):
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v

# Test with invalid data
try:
    invalid_user = UserWithAddress(
        id=3,
        name="A",  # Too short
        email="charlie@example.com",
        addresses=[{"street": "789 Pine Rd", "city": "Chicago", "zip_code": "60601"}],
    )
except ValidationError as e:
    print(e)
```

Output:
```
1 validation error for UserWithAddress
name
  ValueError: Name must be at least 2 characters long
```

#### Advanced Features
- **Field Aliases**: Map JSON keys to Python attributes (e.g., `email_address` in JSON to `email` in Python):
  ```python
  class UserAlias(BaseModel):
      email: str = Field(..., alias="email_address")

  user = UserAlias(**{"email_address": "dave@example.com"})
  print(user.email)  # dave@example.com
  ```
- **Default Factories**: Use a function to set default values:
  ```python
  from pydantic import Field
  from uuid import uuid4

  class UserWithUUID(BaseModel):
      user_id: str = Field(default_factory=lambda: str(uuid4()))

  user = UserWithUUID()
  print(user.user_id)  # e.g., "123e4567-e89b-12d3-a456-426614174000"
  ```
- **Validation Modes**: Configure strictness (e.g., `strict=True` to disable type coercion):
  ```python
  class StrictUser(BaseModel, strict=True):
      id: int

  try:
      user = StrictUser(id="123")  # Will fail because "123" is a string
  except ValidationError as e:
      print(e)  # type_error.integer
  ```

#### Why Pydantic for DACA?
Pydantic is critical for DACA because:
- **Data Integrity**: Ensures incoming user data and agent responses are valid and type-safe.
- **Complex Workflows**: Supports nested models for agentic AI scenarios (e.g., user messages with metadata, agent responses with context).
- **Serialization**: Seamlessly converts models to JSON for API responses.
- **Error Handling**: Provides clear validation errors, improving debugging in distributed systems.

---

## Step 4: Building a FastAPI Application with Complex Pydantic Models
Let’s build a FastAPI app for a chatbot with a more complex data model, simulating an agentic AI workflow where users send messages with metadata (e.g., timestamps, session IDs).

### Create the Main Application File
Create `main.py`:
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

# Initialize the FastAPI app
app = FastAPI(
    title="DACA Chatbot API",
    description="A FastAPI-based API for a chatbot in the DACA tutorial series",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin (e.g., React app)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Complex Pydantic models
class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str = Field(default_factory=lambda: str(uuid4()))

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata
    tags: Optional[List[str]] = None  # Optional list of tags

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

# Simulate a database dependency
async def get_db():
    return {"connection": "Mock DB Connection"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}

# GET endpoint with query parameters
@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

# POST endpoint for chatting
@app.post("/chat/", response_model=Response)
async def chat(message: Message, db: dict = Depends(get_db)):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    print(f"DB Connection: {db['connection']}")
    reply_text = f"Hello, {message.user_id}! You said: '{message.text}'. How can I assist you today?"
    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()  # Auto-generate timestamp and session_id
    )
```

### Explanation of the Code
1. **Complex Pydantic Models**:
   - `Metadata`: A nested model with a `timestamp` (defaults to current UTC time) and `session_id` (defaults to a UUID).
   - `Message`: The request model, including `user_id`, `text`, `metadata` (nested `Metadata`), and optional `tags`.
   - `Response`: The response model, returning `user_id`, `reply`, and `metadata`.

2. **CORS Middleware**:
   - `CORSMiddleware`: Allows cross-origin requests from a frontend (e.g., a React app at `http://localhost:3000`).
   - `allow_origins`: Specifies allowed origins (update this for production).
   - `allow_credentials`, `allow_methods`, `allow_headers`: Configures CORS behavior.

3. **Endpoint Updates**:
   - The `/chat/` endpoint now accepts a `Message` with nested `Metadata` and returns a `Response` with similar structure.

---

## Step 5: Adding CORS Middleware (Detailed)
### Why CORS?
CORS (Cross-Origin Resource Sharing) is a security mechanism that allows or restricts web applications running at one origin (e.g., `http://localhost:3000`) to make requests to another origin (e.g., `http://localhost:8000`). In DACA, your FastAPI backend might be accessed by a frontend (e.g., a Next.js UI), requiring CORS to be enabled.

### Configuring CORS in FastAPI
We already added the `CORSMiddleware` in `main.py`. Let’s test it to confirm it works.

#### Simulate a Frontend Request
Assume you have a simple HTML page served at `http://localhost:3000`:
```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Test CORS</title>
</head>
<body>
    <h1>Test CORS with FastAPI</h1>
    <button onclick="fetchData()">Fetch Data</button>
    <pre id="result"></pre>

    <script>
        async function fetchData() {
            const response = await fetch("http://localhost:8000/", {
                method: "GET",
                credentials: "include"
            });
            const data = await response.json();
            document.getElementById("result").textContent = JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>
```

Serve this file using a simple HTTP server:
```bash
python -m http.server 3000
```
Visit `http://localhost:3000`, click the button, and you should see the response from the FastAPI root endpoint:
```json
{
  "message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."
}
```

Without CORS, this request would fail with a browser error like `CORS policy: No 'Access-Control-Allow-Origin' header is present`.

---

## Step 6: Writing Unit Tests with Pytest
### Why Unit Tests?
Unit tests ensure your API endpoints behave as expected, catching bugs early. In DACA, testing is crucial as we’ll integrate with Dapr, OpenAI Agents SDK, and other components.

### Create a Test File
Create a directory for tests and a test file:
```bash
mkdir tests
touch tests/test_main.py
```

Add the following to `tests/test_main.py`:
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
uv run pytest tests/test_main.py -v
```
Output:
```
collected 3 items

tests/test_main.py::test_root PASSED
tests/test_main.py::test_get_user PASSED
tests/test_main.py::test_chat PASSED

================= 3 passed in 0.12s =================
```

### Explanation of the Tests
1. **Test Client**:
   - `TestClient(app)`: Creates a client to simulate HTTP requests to the FastAPI app.
2. **Tests**:
   - `test_root`: Tests the root endpoint (`GET /`).
   - `test_get_user`: Tests the `/users/{user_id}` endpoint with and without query parameters.
   - `test_chat`: Tests the `/chat/` endpoint with both valid and invalid requests, including nested `metadata`.

---

## Step 7: Running and Testing the API
### Start the Server
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Test the API
#### Root Endpoint
- Visit `http://localhost:8000/`  
  Response: `{"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}`

#### Interactive Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Test `/chat/` with Complex Data
Use Swagger UI to send a request:
```json
{
  "user_id": "alice",
  "text": "Hello, how are you?",
  "metadata": {
    "timestamp": "2025-04-06T12:00:00Z",
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "tags": ["greeting", "question"]
}
```
Response:
```json
{
  "user_id": "alice",
  "reply": "Hello, alice! You said: 'Hello, how are you?'. How can I assist you today?",
  "metadata": {
    "timestamp": "2025-04-06T12:00:00Z",
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

#### Test CORS
Using the HTML page from Step 5, confirm that CORS works by fetching data from `http://localhost:3000`.

---

## Step 8: Why FastAPI and Pydantic for DACA?
- **FastAPI**:
  - **Asynchronous Support**: Handles high-concurrency workloads.
  - **Automatic Docs**: Simplifies testing and integration.
  - **Scalability**: Stateless design fits DACA’s containerized architecture.
- **Pydantic**:
  - **Data Integrity**: Ensures type-safe data for agentic workflows.
  - **Complex Models**: Supports nested structures for rich data (e.g., metadata, tags).
  - **Error Handling**: Provides clear validation errors for debugging.

---

## Step 9: Next Steps
You’ve built a robust FastAPI app with complex Pydantic models, CORS support, and unit tests! In the next tutorial (**02_openai_agents_with_fastapi**), we’ll integrate the OpenAI Agents SDK to make our chatbot agentic, enabling autonomous task execution.

### Optional Exercises
1. Add a new endpoint to retrieve all messages for a `user_id` (use a mock dictionary for now).
2. Extend the `Message` model with a custom validator (e.g., ensure `text` is not longer than 500 characters).
3. Add more unit tests for edge cases (e.g., invalid `timestamp` format in `metadata`).

---

## Conclusion
In this enhanced tutorial, we set up a FastAPI project with `uv`, explored Pydantic in depth, and built a chatbot API with complex data models, CORS middleware, and unit tests. FastAPI and Pydantic provide a solid foundation for DACA’s REST API layer, ensuring scalability, type safety, and ease of integration. You’re now ready to add agentic AI capabilities in the next tutorial!

---

### Final Code for `main.py`
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

app = FastAPI(
    title="DACA Chatbot API",
    description="A FastAPI-based API for a chatbot in the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str = Field(default_factory=lambda: str(uuid4()))

class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata
    tags: Optional[List[str]] = None

class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata

async def get_db():
    return {"connection": "Mock DB Connection"}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}

@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

@app.post("/chat/", response_model=Response)
async def chat(message: Message, db: dict = Depends(get_db)):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    print(f"DB Connection: {db['connection']}")
    reply_text = f"Hello, {message.user_id}! You said: '{message.text}'. How can I assist you today?"
    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

---

### Final Code for `tests/test_main.py`
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."
    }

def test_get_user():
    response = client.get("/users/alice?role=admin")
    assert response.status_code == 200
    assert response.json() == {"user_id": "alice", "role": "admin"}

    response = client.get("/users/bob")
    assert response.status_code == 200
    assert response.json() == {"user_id": "bob", "role": "guest"}

@pytest.mark.asyncio
async def test_chat():
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

---

This enhanced tutorial now provides a comprehensive introduction to FastAPI, Pydantic, and related concepts, preparing learners for the rest of the DACA series. 