# Basic Security - Securing A2A with API Key Authentication 🔒

**Build an A2A-compliant agent with basic security using API key authentication. This involves issuing API keys out-of-band, declaring authentication requirements in the Agent Card, and validating API keys in client-server interactions to secure communication for production.**

> **🎯 Learning Goal**: Learn how to implement API key-based authentication in A2A communication, ensuring secure agent interactions. Understand how to declare security schemes in the Agent Card, issue and validate API keys, and handle authentication errors, aligning with enterprise-ready security practices for production deployment.

## 🧠 Why This Matters for Learning

### **Why API Key Authentication for A2A?**
- **Simplicity**: API keys provide a straightforward authentication mechanism, ideal for initial production setups with minimal complexity.
- **Enterprise-Ready**: Aligns with A2A’s security model, using standard HTTP headers (`X-API-Key`) and Agent Card declarations for interoperability.
- **Secure Communication**: Ensures only authorized clients can interact with the agent, protecting sensitive tasks and data.
- **Production Readiness**: Implements transport security (HTTPS) and authentication to meet basic production requirements.

### **Keeping It Practical**
- **Agent Card Security**: Declare the API key scheme in the Agent Card for client discovery.
- **Out-of-Band Key Issuance**: Issue API keys securely outside the A2A protocol (e.g., via a web portal or admin process).
- **Client-Server Validation**: Validate API keys in HTTP headers to authorize requests, returning standard HTTP errors (e.g., 401 Unauthorized) for failures.
- **Task Protection**: Ensure task operations (e.g., `message/send`, `tasks/get`) are restricted to authenticated clients.

## 🚀 How to Build API Key Authentication for A2A

This standalone example demonstrates how to secure an A2A agent using API key authentication, based on the A2A specification ([Authentication and Authorization](https://a2a-protocol.org/latest/specification/#4-authentication-and-authorization)) and the [headless agent auth sample](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/headless_agent_auth). The agent processes simple queries (e.g., answering questions) and requires clients to provide a valid API key in the `X-API-Key` header for all requests.

### Authentication Flow Explained Simply
1. **Agent Card Declaration**: The server publishes an Agent Card specifying the `ApiKey` security scheme, indicating that clients must include an API key in the `X-API-Key` header.
2. **Out-of-Band Key Issuance**: Clients obtain an API key through a secure process (e.g., a registration portal or admin-provided key), outside the A2A protocol.
3. **Client Request**: The client sends an A2A request (e.g., `message/send`) with the API key in the `X-API-Key` header.
4. **Server Validation**:
   - The server checks the `X-API-Key` header against a stored list of valid keys.
   - If valid, the request is processed, and a task is created or updated.
   - If invalid or missing, the server returns a 401 Unauthorized error with a `WWW-Authenticate` header.
5. **Task Lifecycle**:
   - **Submitted**: Task is created after successful authentication.
   - **Working**: Agent processes the request (e.g., answers a query).
   - **Completed**: Task finishes, returning an artifact (e.g., text response).
   - **Failed/Rejected**: Task fails if authentication fails or input is invalid.
6. **Follow-Ups**: Clients use the same API key for subsequent requests within the same `contextId`.

This example uses a **Secure Query Agent** that answers user questions (e.g., "What’s the weather like today?") and requires API key authentication for all interactions.

### Key Files
1. **agent_card.json**: JSON file defining the Agent Card, including the `ApiKey` security scheme and supported methods.
2. **query_agent.py**: Defines the Secure Query Agent, which processes text queries and generates text artifacts, accessible only to authenticated clients.
3. **agent_executor.py**: Custom AgentExecutor that validates API keys and bridges A2A task logic to the FastAPI server, using `TaskUpdater` for task state management.
4. **server.py**: FastAPI server implementing A2A methods (e.g., `message/send`, `tasks/get`) with API key validation middleware, using `InMemoryTaskStore` or SQLite for persistence.
5. **client.py**: Client script simulating authenticated requests, including the API key in the `X-API-Key` header.
6. **conversations.db**: SQLite database for persisting task and session states (managed by `SQLiteSession`).
7. **api_keys.json**: File storing valid API keys for server-side validation (for simplicity; in production, use a secure database or key management system).

### How to Demo
- **Scenario**: Client sends a query ("What’s the weather like today?") with a valid API key. The agent processes the query and returns a text artifact. An invalid key results in a 401 error.
- **Follow-Up**: Client sends a related query ("What about tomorrow?") with the same `contextId` and API key.

### Setup and Running
1. **Install Dependencies**:
   ```bash
   uv sync
   ```
   Installs `a2a-sdk[http-server]`, `fastapi`, `python-jose` (for potential JWT extensions), and other dependencies.
2. **Generate API Key**:
   - Create a sample API key (e.g., `secure-api-key-123`) and store it in `api_keys.json`:
     ```json
     ["secure-api-key-123"]
     ```
   - In production, use a secure key management system (e.g., AWS Secrets Manager, HashiCorp Vault) or a registration portal.
3. **Run the Server**:
   ```bash
   uv run server.py
   ```
   Starts the FastAPI server at `https://localhost:8001` (ensure HTTPS for production).
4. **Simulate Client Interactions**:
   - Valid request:
     ```bash
     uv run client.py --query "What’s the weather like today?" --api-key "secure-api-key-123"
     ```
     Agent responds with a `Task` containing the answer.
   - Invalid request:
     ```bash
     uv run client.py --query "What’s the weather like today?" --api-key "invalid-key"
     ```
     Server returns a 401 Unauthorized error.
5. **Monitor Logs**: Check authentication successes/failures and task state transitions in the server logs.

### Code Highlights
#### agent_card.json (Declaring API Key Authentication)
```json
{
  "protocolVersion": "0.3.0",
  "name": "Secure Query Agent",
  "description": "Answers general knowledge questions with API key authentication.",
  "url": "https://localhost:8001/a2a/v1",
  "preferredTransport": "JSONRPC",
  "securitySchemes": {
    "api-key": {
      "type": "apiKey",
      "name": "X-API-Key",
      "in": "header"
    }
  },
  "security": [{"api-key": []}],
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "query-answering",
      "name": "General Knowledge Query",
      "description": "Answers general knowledge questions.",
      "tags": ["query", "knowledge"],
      "examples": ["What’s the weather like today?"]
    }
  ]
}
```

#### server.py (FastAPI with API Key Validation)
```python
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from a2a_sdk import DefaultRequestHandler, InMemoryTaskStore
import json

app = FastAPI()
task_store = InMemoryTaskStore()
handler = DefaultRequestHandler(task_store=task_store)

# Load API keys (in production, use a secure store)
with open("api_keys.json", "r") as f:
    VALID_API_KEYS = json.load(f)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    return api_key

@app.post("/a2a/v1/message:send", dependencies=[Security(verify_api_key)])
async def message_send(request: dict):
    return await handler.handle_request(request)

@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    with open("agent_card.json", "r") as f:
        return json.load(f)
```

#### client.py (Sending Authenticated Requests)
```python
import httpx
import uuid
import json

async def send_query(query, api_key, context_id=None):
    async with httpx.AsyncClient() as client:
        request = {
            "jsonrpc": "2.0",
            "id": "req-001",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": query}],
                    "messageId": str(uuid.uuid4()),
                    "contextId": context_id or str(uuid.uuid4())
                }
            }
        }
        headers = {"X-API-Key": api_key}
        response = await client.post("https://localhost:8001/a2a/v1/message:send", json=request, headers=headers)
        if response.status_code == 401:
            print("Authentication failed:", response.json())
        else:
            result = response.json()
            print(f"Task ID: {result['result']['id']}, Status: {result['result']['status']['state']}")
            for artifact in result["result"].get("artifacts", []):
                for part in artifact["parts"]:
                    if part["kind"] == "text":
                        print(f"Response: {part['text']}")

# Example usage
import asyncio
asyncio.run(send_query("What’s the weather like today?", "secure-api-key-123"))
```

### Example Interaction
1. **Client Request (Valid API Key)**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "req-001",
     "method": "message/send",
     "params": {
       "message": {
         "role": "user",
         "parts": [{"kind": "text", "text": "What’s the weather like today?"}],
         "messageId": "msg-001",
         "contextId": "ctx-001"
       }
     }
   }
   Headers: {"X-API-Key": "secure-api-key-123"}
   ```
2. **Agent Response**:
   ```json
   {
     "jsonrpc": "2.0",
     "id": "req-001",
     "result": {
       "id": "task-001",
       "contextId": "ctx-001",
       "status": {"state": "completed", "timestamp": "2025-08-15T17:08:00Z"},
       "artifacts": [
         {
           "artifactId": "artifact-001",
           "name": "query_response",
           "parts": [{"kind": "text", "text": "The weather today is sunny with a high of 75°F."}]
         }
       ],
       "kind": "task"
     }
   }
   ```
3. **Client Request (Invalid API Key)**:
   ```json
   Headers: {"X-API-Key": "invalid-key"}
   ```
   **Server Response**:
   ```json
   {
     "status_code": 401,
     "detail": "Invalid or missing API key",
     "headers": {"WWW-Authenticate": "ApiKey"}
   }
   ```

---

## 📖 Key Takeaway

**Remember**: API key authentication provides a simple, effective way to secure A2A communication, ensuring only authorized clients can access your agent. By implementing this basic security flow, you’re ready to deploy a production-ready A2A system with minimal complexity! 🔒

### Concepts Demonstrated
- **API Key Authentication**: Use the `ApiKey` security scheme with `X-API-Key` header for client authentication.
- **Agent Card Security**: Declare authentication requirements in the Agent Card for client discovery.
- **HTTP Security**: Enforce HTTPS and validate API keys, returning 401 errors for unauthorized requests.
- **Production Readiness**: Align with A2A’s enterprise-ready practices for secure, interoperable communication.

### Ideas Shown
- **Out-of-Band Key Issuance**: Securely provide API keys to clients outside the A2A protocol.
- **Server-Side Validation**: Check API keys against a stored list or database to authorize requests.
- **Error Handling**: Return standard HTTP 401 errors with `WWW-Authenticate` headers for authentication failures.
- **Task Protection**: Restrict task operations to authenticated clients, ensuring secure data exchange.

### Resources to Learn More
- [A2A Specification: Authentication and Authorization](https://a2a-protocol.org/latest/specification/#4-authentication-and-authorization)
- [A2A Enterprise-Ready Features](https://a2a-protocol.org/latest/topics/enterprise-ready/)
- [A2A Agent Card Security](https://a2a-protocol.org/latest/specification/#54-security-of-agent-cards)
- [A2A Headless Agent Auth Sample](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/headless_agent_auth)