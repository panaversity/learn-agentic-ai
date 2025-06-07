# Microservices with FastAPI

Let’s proceed with the third tutorial in the **Dapr Agentic Cloud Ascent (DACA)** series. In this tutorial, we’ll introduce the concept of microservices, build two stateless microservices using FastAPI and the OpenAI Agents SDK, and demonstrate synchronous inter-service communication using `httpx`. We’ll also explain what stateless services are and why they’re a key part of DACA’s architecture. This tutorial builds on the previous ones, where we set up a FastAPI app and integrated the OpenAI Agents SDK to create an agentic chatbot.

---

## Building Stateless Microservices with FastAPI and OpenAI Agents SDK

Welcome to the third tutorial in our **Dapr Agentic Cloud Ascent (DACA)** series! In this step, we’ll explore microservices architecture by creating two stateless microservices: a **Chat Service** and an **Agent Memory Service**. The Chat Service handles user messages and uses the OpenAI Agents SDK to generate responses, while the Agent Memory Service provides procedural memories (e.g., past actions or skills) to enrich the chatbot’s context. The Chat Service will synchronously call the Agent Memory Service using `httpx`, demonstrating inter-service communication. We’ll also explain why stateless services are critical for DACA’s scalability. Let’s get started!

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
- An LLM API key.
- Familiarity with FastAPI, Pydantic, and the OpenAI Agents SDK.

---

## Step 1: Introduction to Microservices
### What Are Microservices?
Microservices are an architectural style where an application is composed of small, independent services that communicate over a network (e.g., via HTTP, message queues). Each service focuses on a specific business capability, can be developed, deployed, and scaled independently, and communicates through well-defined APIs.

#### Key Characteristics of Microservices
- **Single Responsibility**: Each service handles a specific function (e.g., chat processing, memory retrieval).
- **Independence**: Services can be developed, deployed, and scaled separately.
- **Decentralized Data**: Each service typically manages its own data (mocked here for simplicity).
- **Communication**: Services interact via APIs (e.g., HTTP/REST, gRPC) or asynchronous messaging.
- **Technology Diversity**: Different services can use different tech stacks (we’ll use FastAPI for both).

#### Benefits of Microservices in DACA
- **Scalability**: Scale only the services that need more resources (e.g., the Chat Service during peak usage).
- **Resilience**: If one service fails, others can continue functioning.
- **Modularity**: Easier to develop, test, and maintain smaller services.
- **Flexibility**: Teams can work on different services independently, aligning with DACA’s distributed nature.

### What Are Stateless Services?
A **stateless service** does not retain information (state) between requests. Each request is processed independently, without relying on data from previous requests stored in the service itself. State, if needed, is stored externally (e.g., in a database or Dapr state store).

#### Characteristics of Stateless Services
- **No Session Data**: The service doesn’t store user sessions or history in memory.
- **External State**: State is offloaded to external systems (mocked here with in-memory data).
- **Scalability**: Any instance can handle any request, enabling horizontal scaling.
- **Fault Tolerance**: If an instance fails, another can take over without losing state.

#### Why Stateless Services in DACA?
- **Horizontal Scaling**: DACA aims for planetary scale, and stateless services allow load balancers to distribute requests without session affinity.
- **Containerization**: Stateless services fit DACA’s containerized architecture (Docker, Kubernetes), where instances can be dynamic.
- **Resilience**: Reduces risk of data loss if an instance crashes.
- **Simplified Design**: External state management simplifies service logic.

In this tutorial, both services are stateless, using mock data for now, with plans to integrate Dapr later.

---

## Step 2: Project Structure
Each service has its own directory with its own FastAPI app, Pydantic models, tests, and dependency management files.

### Create the New Project Structure
```
fastapi-daca-tutorial/
├── chat_service/
│   ├── main.py
│   ├── models.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── test_main.py
├── agent_memory_service/
│   ├── main.py
│   ├── models.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── test_main.py
└── README.md
```

Each service has its own `pyproject.toml`, ensuring independent dependency management, unlike the original single-TOML structure.

---

## Step 3: Define the Chat Service
The **Chat Service** handles user messages, uses the OpenAI Agents SDK to generate responses, and fetches procedural memories from the Agent Memory Service to personalize replies. You can copy the code from last service and organize it like:

### `chat_service/models.py`
```python
from pydantic import BaseModel, Field
from datetime import datetime, UTC

# Pydantic models
class Metadata(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    session_id: str = Field(default_factory=lambda: str(uuid4()))


class Message(BaseModel):
    user_id: str
    text: str
    metadata: Metadata | None = None
    tags: list[str] | None = None


class Response(BaseModel):
    user_id: str
    reply: str
    metadata: Metadata
```

### `chat_service/main.py`
```python
import os
import httpx

from typing import cast
from dotenv import load_dotenv
from datetime import datetime, UTC

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import OpenAI Agents SDK
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider

from models import Message, Response, Metadata

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=cast(ModelProvider, external_client), # satisfy type checker
    tracing_disabled=True
)

# Initialize the FastAPI app
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

# Create a tool to fetch the current time
@function_tool
def get_current_time() -> str:
    """Returns the current time in UTC."""
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the DACA Chatbot API! Access /docs for the API documentation."}

# POST endpoint for chatting
@app.post("/chat/", response_model=Response)
async def chat(message: Message):
    if not message.text.strip():
        raise HTTPException(
            status_code=400, detail="Message text cannot be empty")

    async with httpx.AsyncClient() as client:
        try:
            memory_response = await client.get(f"http://localhost:8001/memories/{message.user_id}")
            memory_response.raise_for_status()
            memory_data = memory_response.json()
            past_actions = memory_data.get("past_actions", [])
        except httpx.HTTPStatusError:
            past_actions = []  # Fallback if Memory Service fails

    # Personalize agent instructions with procedural memories
    memory_context = "The user has no past actions." if not past_actions else f"The user’s past actions include: {', '.join(past_actions)}."
    personalized_instructions = (
        f"You are a helpful chatbot. Respond to user messages in a friendly way. "
        f"If the user asks for the time, use the get_current_time tool. "
        f"{memory_context} Use this to personalize your response."
    )

    chat_agent = Agent(
        name="ChatAgent",
        instructions=personalized_instructions,
        tools=[get_current_time],  # Add the time tool
        model=model
    )
    # Use the OpenAI Agents SDK to process the message
    result = await Runner.run(chat_agent, input=message.text, run_config=config)
    reply_text = result.final_output  # Get the agent's response

    return Response(
        user_id=message.user_id,
        reply=reply_text,
        metadata=Metadata()
    )
```

### `chat_service/pyproject.toml`
```toml
[project]
name = "fastapi-daca-tutorial"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi[standard]>=0.115.12",
    "openai-agents==0.0.7",
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
]
```

### Setup
```bash
cd chat_service
uv sync
source .venv/bin/activate
```

---

## Step 4: Define the Agent Memory Service
Quick Setup
```bash
uv init agent_memory_service
cd agent_memory_service
uv venv
source .venv/bin/activate

uv add "fastapi[standard]" pytest pytest-asyncio
```

The **Agent Memory Service** provides procedural memories (e.g., past actions or skills) for a user, mocked with in-memory data for now.

### `agent_memory_service/models.py`
```python
from pydantic import BaseModel

class Memories(BaseModel):
    past_actions: list[str]
```

### `agent_memory_service/main.py`
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Memories

app = FastAPI(
    title="Agent Memory Service",
    description="Provides procedural memories for AI agents",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Allow Chat Service
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock procedural memories (e.g., past actions)
MOCK_MEMORIES = {
    "alice": {"past_actions": ["scheduled a meeting", "analyzed data"]},
    "bob": {"past_actions": ["wrote a report"]}
}

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent Memory Service!"}

@app.get("/memories/{user_id}", response_model=Memories)
async def get_memories(user_id: str):
    if user_id not in MOCK_MEMORIES:
        raise HTTPException(status_code=404, detail="User not found")
    return Memories(**MOCK_MEMORIES[user_id])
```

### `agent_memory_service/pyproject.toml`
```toml
[project]
name = "agent-memory-service"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi[standard]>=0.115.12",
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
]
```

### Setup
```bash
cd agent_memory_service
uv sync
```

---

## Step 5: Running and Testing the Microservices
### Start the Agent Memory Service (port 8001)
```bash
cd agent_memory_service
uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Start the Chat Service (port 8000)
In a separate terminal:
```bash
cd chat_service
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Test the Agent Memory Service
Visit `http://localhost:8001/docs` and test `GET /memories/alice`:
```json
{"past_actions": ["scheduled a meeting", "analyzed data"]}
```

### Test the Chat Service
Visit `http://localhost:8000/docs` and send a `POST /chat/` request:
```json
{  
"user_id": "alice",
"text": "What can you do for me today?",
"tags": ["greeting"]
}
```
Example response:
```json
{
  "user_id": "alice",
  "reply": "It's great to be chatting with you again! I know we've previously scheduled a meeting and analyzed some data together.\n\nRight now, I can get the current time for you. I can also still schedule meetings and analyze data. Just let me know what you'd like to do!\n",
  "metadata": {
    "timestamp": "2025-04-07T09:04:03.099666Z",
    "session_id": "f48d563a-1ba7-4be3-8ec1-22eef71f19f1"
  }
}
```

### Run the Tests
Tests are omitted for brevity but can be adapted from the original Chat Service tests, mocking the Agent Memory Service response.

---

## Step 6: Why Microservices and Stateless Design for DACA?
- **Microservices**: The Chat Service and Agent Memory Service are independent, allowing separate scaling and updates, aligning with DACA’s goal of a distributed, agentic system.
- **Stateless Design**: Both services fetch data per request (e.g., memories from the Agent Memory Service), ensuring scalability and resilience.

---

## Step 7: Next Steps
You’ve built two stateless microservices with FastAPI and the OpenAI Agents SDK! In the next tutorial (**04_dapr_theory_and_cli**), we’ll introduce Dapr to enhance communication and state management.

### Optional Exercises
1. Add an endpoint to store new procedural memories in the Agent Memory Service.
2. Enhance the Chat Agent with a tool to fetch memories directly.
3. Test fallback behavior by stopping the Agent Memory Service.

---

## Conclusion
In this tutorial, we explored microservices and stateless services by building a Chat Service and an Agent Memory Service. The Chat Service uses `httpx` to fetch procedural memories from the Agent Memory Service, enhancing responses with the OpenAI Agents SDK. This stateless design sets a scalable foundation for DACA, ready for Dapr integration.


---
## Optional Runing microservices with `.sh` or `.bat` files

### 🧠 FastAPI DACA Microservices

![Demo](./fastapi-daca-tutorial/output.gif)


This project comprises two FastAPI microservices:

- [agent_memory_service](./agent_memory_service/)
- [chat-service](./chat-service/)

Each service is managed using the `uv` Python package manager for efficient dependency management and execution.

### 🚀 Running the Services

#### Prerequisites

- Ensure that [uv](https://docs.astral.sh/uv/) is installed on your system.
- Navigate to the `fastapi-daca-tutorial` directory, which contains both microservices.

#### For Linux/macOS Users

1. **Make the script executable**:

   ```bash
   chmod +x run_services.sh
   ```


2. **Run the script**:

   ```bash
   ./run_services.sh
   ```


   This script will start both microservices concurrently in the background.

#### For Windows Users

1. **Run the batch file**:

   Double-click on `run_services.bat` or execute it via the Command Prompt:

   ```cmd
   run_services.bat
   ```


   This will open two separate Command Prompt windows, each running one of the microservices.

### 📝 Notes
- Both scripts utilize `uv run fastapi dev` to start the FastAPI applications in development mode.
- Ensure that each microservice directory contains a valid `pyproject.toml` file with the necessary configuratios.
- If you encounter issues with dependencies, consider running `uv sync` in each microservice directory to synchronize dependencies as specified in the `pyproject.toml` fils.
