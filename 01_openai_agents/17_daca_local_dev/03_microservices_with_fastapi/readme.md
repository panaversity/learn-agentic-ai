# Microservices with FastAPI

Let’s proceed with the third tutorial in the **Dapr Agentic Cloud Ascent (DACA)** series. In this tutorial, we’ll introduce the concept of microservices, build two stateless microservices using FastAPI and the OpenAI Agents SDK, and demonstrate synchronous inter-service communication using `httpx`. We’ll also explain what stateless services are and why they’re a key part of DACA’s architecture. This tutorial builds on the previous ones, where we set up a FastAPI app and integrated the OpenAI Agents SDK to create an agentic chatbot.

---

## Building Stateless Microservices with FastAPI and OpenAI Agents SDK

Welcome to the third tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll explore microservices architecture, a foundational concept for building scalable, distributed systems like DACA. We’ll create two stateless microservices using FastAPI and the OpenAI Agents SDK: one for handling user messages (Chat Service) and another for generating user analytics (Analytics Service). The Chat Service will synchronously call the Analytics Service using `httpx` to retrieve user data, demonstrating inter-service communication. We’ll also explain what stateless services are and why they’re critical for DACA’s scalability. Let’s get started!

---

## What You’ll Learn
- What microservices are and their benefits in distributed systems.
- What stateless services are and why they’re important for DACA.
- How to build two stateless microservices using FastAPI and the OpenAI Agents SDK.
- Implementing synchronous inter-service communication using `httpx`.
- Updating unit tests to cover inter-service interactions.

## Prerequisites
- Completion of the previous tutorial.
- Python 3.12+ installed.
- An OpenAI API key (set as `OPENAI_API_KEY`) or Google Gemini Flash 2.0 key.
- Familiarity with FastAPI, Pydantic, and the OpenAI Agents SDK.

---

## Step 1: Introduction to Microservices
### What Are Microservices?
Microservices are an architectural style where an application is composed of small, independent services that communicate over a network (e.g., via HTTP, message queues). Each service focuses on a specific business capability, can be developed, deployed, and scaled independently, and communicates with other services through well-defined APIs.

#### Key Characteristics of Microservices
- **Single Responsibility**: Each service handles a specific function (e.g., user authentication, message processing).
- **Independence**: Services can be developed, deployed, and scaled separately.
- **Decentralized Data**: Each service typically manages its own data (though we’ll simulate this for now).
- **Communication**: Services interact via APIs (e.g., HTTP/REST, gRPC) or asynchronous messaging (e.g., RabbitMQ, Kafka).
- **Technology Diversity**: Different services can use different tech stacks (though we’ll use FastAPI for both).

#### Benefits of Microservices in DACA
- **Scalability**: Scale only the services that need more resources (e.g., scale the Chat Service during peak usage).
- **Resilience**: If one service fails, others can continue functioning.
- **Modularity**: Easier to develop, test, and maintain smaller services.
- **Flexibility**: Teams can work on different services independently, aligning with DACA’s distributed nature.

### What Are Stateless Services?
A **stateless service** does not retain information (state) between requests. Each request is processed independently, without relying on data from previous requests stored in the service itself. State, if needed, is stored externally (e.g., in a database, cache, or Dapr state store in later tutorials).

#### Characteristics of Stateless Services
- **No Session Data**: The service doesn’t store user sessions or request history in memory.
- **External State**: State is offloaded to external systems (e.g., Redis, CockroachDB).
- **Scalability**: Any instance of the service can handle any request, making it easy to scale horizontally by adding more instances.
- **Fault Tolerance**: If a service instance fails, another can take over without losing state.

#### Why Stateless Services in DACA?
- **Horizontal Scaling**: DACA aims for planetary scale, requiring services to scale out easily. Stateless services allow load balancers to distribute requests across instances without worrying about session affinity.
- **Containerization**: Stateless services align with DACA’s containerized architecture (Docker, Kubernetes), where containers can be spun up or down dynamically.
- **Resilience**: In a distributed system, stateless services reduce the risk of data loss if an instance crashes.
- **Simplified Design**: Offloading state to external systems (e.g., Dapr in later tutorials) simplifies service logic.

In this tutorial, both microservices (Chat Service and Analytics Service) will be stateless, meaning they won’t store user data in memory between requests. We’ll simulate external state with mock data for now, but in future tutorials, we’ll use Dapr to manage state.

---

## Step 2: Project Structure
We’ll reorganize our project to support multiple microservices. Each service will have its own directory with its own FastAPI app, Pydantic models, and tests.

### Create the New Project Structure
From the `fastapi-daca-tutorial` directory, reorganize as follows:
```
fastapi-daca-tutorial/
├── chat_service/
│   ├── main.py
│   ├── models.py
│   └── tests/
│       └── test_main.py
├── analytics_service/
│   ├── main.py
│   ├── models.py
│   └── tests/
│       └── test_main.py
├── pyproject.toml
└── uv.lock
```

#### Move Existing Code
- Move the existing `main.py` to `chat_service/main.py`.
- Move the existing `tests/test_main.py` to `chat_service/tests/test_main.py`.

#### Update `pyproject.toml`
Ensure `httpx` is included for inter-service communication (already added in the previous tutorial, but double-check):
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
    "openai-agents>=0.0.8",
]
```

---

## Step 3: Define the Chat Service
The **Chat Service** will handle user messages, use the OpenAI Agents SDK to generate responses, and call the Analytics Service to fetch user analytics (e.g., message count) to personalize responses.

### Create `chat_service/models.py`
Define the Pydantic models in a separate file for better organization:
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

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
```

### Update `chat_service/main.py`
Modify the Chat Service to call the Analytics Service using `httpx`:
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool
from datetime import datetime
import httpx

from models import Message, Response, Metadata

app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool. Personalize responses using user analytics (e.g., message count).",
    model="gpt-4o",
    tools=[get_current_time],
)

async def get_db():
    return {"connection": "Mock DB Connection"}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

@app.post("/chat/", response_model=Response)
async def chat(message: Message, db: dict = Depends(get_db)):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    print(f"DB Connection: {db['connection']}")

    # Synchronously call the Analytics Service to get user analytics
    async with httpx.AsyncClient() as client:
        try:
            analytics_response = await client.get(f"http://localhost:8001/analytics/{message.user_id}")
            analytics_response.raise_for_status()
            analytics_data = analytics_response.json()
            message_count = analytics_data.get("message_count", 0)
        except httpx.HTTPStatusError as e:
            message_count = 0  # Fallback if Analytics Service fails
            print(f"Failed to fetch analytics: {e}")

    # Update the agent's instructions with user analytics
    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly and informative way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user has sent {message_count} messages so far, so personalize your response accordingly."
    )
    chat_agent.instructions = personalized_instructions

    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text)
    reply_text = result.final_output

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

### Update `chat_service/tests/test_main.py`
Update the tests to mock the Analytics Service call:
```python
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

def test_get_user():
    response = client.get("/users/alice?role=admin")
    assert response.status_code == 200
    assert response.json() == {"user_id": "alice", "role": "admin"}

    response = client.get("/users/bob")
    assert response.status_code == 200
    assert response.json() == {"user_id": "bob", "role": "guest"}

@pytest.mark.asyncio
async def test_chat():
    with patch("main.Runner.run", new_callable=AsyncMock) as mock_run, \
         patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Mock the Analytics Service response
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"message_count": 5})
        mock_run.return_value.final_output = "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?"
        
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
        assert response.json()["reply"] == "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?"
        assert "metadata" in response.json()

        # Mock a tool-using response
        mock_get.return_value = AsyncMock(status_code=200, json=lambda: {"message_count": 3})
        mock_run.return_value.final_output = "Bob, you've sent 3 messages so far. The current time is 2025-04-06 04:01:23 UTC."
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
        assert response.json()["reply"] == "Bob, you've sent 3 messages so far. The current time is 2025-04-06 04:01:23 UTC."
        assert "metadata" in response.json()

        # Test failure of Analytics Service
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
```

---

## Step 4: Define the Analytics Service
The **Analytics Service** will provide user analytics, such as the number of messages a user has sent. For now, we’ll use mock data to simulate this (in future tutorials, we’ll use a database).

### Create `analytics_service/models.py`
```python
from pydantic import BaseModel

class Analytics(BaseModel):
    message_count: int
```

### Create `analytics_service/main.py`
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Analytics

app = FastAPI(
    title="DACA Analytics Service",
    description="A FastAPI-based Analytics Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Allow Chat Service
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user analytics data (in future tutorials, this will come from a database)
MOCK_ANALYTICS = {
    "alice": {"message_count": 5},
    "bob": {"message_count": 3},
}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."}

@app.get("/analytics/{user_id}", response_model=Analytics)
async def get_analytics(user_id: str):
    if user_id not in MOCK_ANALYTICS:
        raise HTTPException(status_code=404, detail="User not found")
    return Analytics(**MOCK_ANALYTICS[user_id])
```

### Create `analytics_service/tests/test_main.py`
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."
    }

def test_get_analytics():
    # Test for existing user
    response = client.get("/analytics/alice")
    assert response.status_code == 200
    assert response.json() == {"message_count": 5}

    # Test for another existing user
    response = client.get("/analytics/bob")
    assert response.status_code == 200
    assert response.json() == {"message_count": 3}

    # Test for non-existing user
    response = client.get("/analytics/charlie")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
```

---

## Step 5: Running and Testing the Microservices
### Start the Analytics Service
Run the Analytics Service on port 8001:
```bash
cd analytics_service
uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Start the Chat Service
In a separate terminal, run the Chat Service on port 8000:
```bash
cd chat_service
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Test the Analytics Service
- Visit `http://localhost:8001/docs` and test the `/analytics/{user_id}` endpoint:
  - For `alice`: `{"message_count": 5}`
  - For `bob`: `{"message_count": 3}`
  - For `charlie`: `404 Not Found`

### Test the Chat Service
Use Swagger UI (`http://localhost:8000/docs`) to send a request to the Chat Service:
```json
{
  "user_id": "alice",
  "text": "Hello, how are you?",
  "metadata": {
    "timestamp": "2025-04-06T12:00:00Z",
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
  },
  "tags": ["greeting"]
}
```
Expected response (actual reply may vary):
```json
{
  "user_id": "alice",
  "reply": "Hi Alice! You've sent 5 messages already—great to hear from you again! How can I help today?",
  "metadata": {
    "timestamp": "2025-04-06T04:01:00Z",
    "session_id": "some-uuid"
  }
}
```

### Run the Tests
- Chat Service:
  ```bash
  cd chat_service
  uv run pytest tests/test_main.py -v
  ```
- Analytics Service:
  ```bash
  cd analytics_service
  uv run pytest tests/test_main.py -v
  ```

---

## Step 6: Why Microservices and Stateless Design for DACA?
- **Microservices**:
  - The Chat Service and Analytics Service are independent, allowing us to scale or update them separately.
  - This modularity aligns with DACA’s goal of building a distributed, planetary-scale system.
- **Stateless Design**:
  - Both services are stateless: they don’t store user data in memory between requests.
  - The Chat Service fetches analytics data on each request, and the Analytics Service uses mock data (to be replaced with a database later).
  - This statelessness ensures we can scale horizontally by adding more instances, a key requirement for DACA’s Kubernetes deployment stage.

---

## Step 7: Next Steps
You’ve successfully built two stateless microservices with FastAPI and the OpenAI Agents SDK, implementing synchronous inter-service communication! In the next tutorial (**04_dapr_theory_and_cli**), we’ll introduce Dapr, which will simplify inter-service communication, state management, and more.

### Optional Exercises
1. Add a new endpoint to the Chat Service to fetch analytics data independently.
2. Add a tool to the Chat Service’s agent to call the Analytics Service directly.
3. Simulate a failure in the Analytics Service and test the Chat Service’s fallback behavior.

---

## Conclusion
In this tutorial, we explored microservices architecture and stateless services, building two microservices (Chat Service and Analytics Service) using FastAPI and the OpenAI Agents SDK. The Chat Service synchronously calls the Analytics Service using `httpx` to personalize responses, demonstrating inter-service communication. The stateless design ensures scalability, aligning with DACA’s goals. We’re now ready to introduce Dapr to enhance our microservices architecture!

---

### Final Code for `chat_service/main.py`
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from agents import Agent, Runner, function_tool
from datetime import datetime
import httpx

from models import Message, Response, Metadata

app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

chat_agent = Agent(
    name="ChatAgent",
    instructions="You are a helpful chatbot. Respond to user messages in a friendly and informative way. If the user asks for the time, use the get_current_time tool. Personalize responses using user analytics (e.g., message count).",
    model="gpt-4o",
    tools=[get_current_time],
)

async def get_db():
    return {"connection": "Mock DB Connection"}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.get("/users/{user_id}")
async def get_user(user_id: str, role: str | None = None):
    user_info = {"user_id": user_id, "role": role if role else "guest"}
    return user_info

@app.post("/chat/", response_model=Response)
async def chat(message: Message, db: dict = Depends(get_db)):
    if not message.text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    print(f"DB Connection: {db['connection']}")

    async with httpx.AsyncClient() as client:
        try:
            analytics_response = await client.get(f"http://localhost:8001/analytics/{message.user_id}")
            analytics_response.raise_for_status()
            analytics_data = analytics_response.json()
            message_count = analytics_data.get("message_count", 0)
        except httpx.HTTPStatusError as e:
            message_count = 0
            print(f"Failed to fetch analytics: {e}")

    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly and informative way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"The user has sent {message_count} messages so far, so personalize your response accordingly."
    )
    chat_agent.instructions = personalized_instructions

    result = await Runner.run(chat_agent, input=message.text)
    reply_text = result.final_output

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

---

### Final Code for `analytics_service/main.py`
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Analytics

app = FastAPI(
    title="DACA Analytics Service",
    description="A FastAPI-based Analytics Service for the DACA tutorial series",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_ANALYTICS = {
    "alice": {"message_count": 5},
    "bob": {"message_count": 3},
}

@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Analytics Service! Access /docs for the API documentation."}

@app.get("/analytics/{user_id}", response_model=Analytics)
async def get_analytics(user_id: str):
    if user_id not in MOCK_ANALYTICS:
        raise HTTPException(status_code=404, detail="User not found")
    return Analytics(**MOCK_ANALYTICS[user_id])
```

---

This tutorial successfully introduces microservices and stateless design, setting the stage for Dapr integration in the next tutorial. Would you like to add more features (e.g., a new microservice, async communication) or move on to **04_dapr_theory_and_cli**?