# Step 11: [Monitoring and Debugging with Dapr Observability](https://docs.dapr.io/operations/observability)

Welcome to Step 11 of the **Dapr Agentic Cloud Ascent (DACA)** series! In this tutorial, we enhance the Chat Service from **10_dapr_actors** by integrating Dapr’s observability features. Our current Chat Service uses Dapr’s State Management, Pub/Sub Messaging, and Actors to process messages and maintain conversation history, but we lack visibility into its performance and interactions. Here, we’ll enable distributed tracing, metrics, and logging to monitor and debug the system, preparing it for production-level reliability and insight.

---

## What You’ll Learn

- Enable Dapr’s observability features: distributed tracing, metrics, and logging.
- Configure Dapr to export traces to Zipkin and metrics to Prometheus.
- Enhance application logging for detailed debugging.
- Use observability tools to monitor the Chat Service and troubleshoot issues.

## Prerequisites

- Completion of **10_dapr_actors** (Chat Service with `UserSessionActor`).
- **Dapr CLI** and runtime installed ([instructions](https://docs.dapr.io/getting-started/install-dapr-cli/)).
- **Docker** installed for Redis, Zipkin, and Prometheus ([install](https://docs.docker.com/get-docker/)).
- **Python 3.9+** installed.
- Basic understanding of observability concepts (tracing, metrics, logging).

## Reading Material

- [Concepts](https://docs.dapr.io/concepts/observability-concept/)
- [Tracing](https://docs.dapr.io/operations/observability/tracing/)
- [Metrics](https://docs.dapr.io/operations/observability/metrics/)
- [Logging](https://docs.dapr.io/operations/observability/logging/)

---

## Step 1: Recap of the Current Setup

In **10_dapr_actors**, we built a Chat Service that:

- Uses a `UserSessionActor` to manage per-user conversation history, stored in Redis via Dapr’s State Management.
- Processes chat requests via a `/chat/` endpoint, fetching history and adding messages using Dapr’s actor API (`http://localhost:3500/v1.0/actors/...`).
- Publishes a `ConversationUpdated` event via Pub/Sub Messaging (Redis-backed).
- Integrates an AI agent (e.g., Gemini) for reply generation, with a fallback to mock metadata if `agent-memory-service` is unavailable.

### Current Limitations

- **No Visibility**: We can’t trace requests through the Chat Service, actor interactions, or pub/sub events.
- **Performance Unknown**: Latency, throughput, and error rates aren’t measurable.
- **Debugging Blind**: Issues like actor state errors or pub/sub failures are hard to pinpoint without detailed logs or traces.

### Goal

Enable Dapr’s observability features to:

- Trace requests with Zipkin across the Chat Service, actors, and pub/sub.
- Collect metrics with Prometheus to monitor performance.
- Enhance logging for detailed debugging insights.

### Project Structure

````
11_dapr_observability/
├── chat-service/
│   ├── main.py              # FastAPI app with chat endpoint and observability
│   ├── user_session_actor.py # UserSessionActor definition
│   ├── models.py            # Message and Metadata models
│   ├── utils.py             # Utility functions (e.g., get_gemini_api_key)
│   └── requirements.txt     # Python dependencies
│   ├── pyproject.toml
│   └── uv.lock
├── agent_memory_service/
│   ├── main.py
│   ├── models.py
│   ├── test_main.py
│   ├── pyproject.toml
│   └── uv.lock
├── components/
│   ├── pubsub.yaml
│   ├── statestore.yaml
│   ├── subscriptions.yaml
│   └── secretstore.yaml
│   └── tracing.yaml         # NEW Tracing configuration
├── prometheus.yml           # NEW Prometheus configuration
└── README.md                # This file


---

## Step 2: Why Dapr Observability?
Dapr’s observability features provide:
- **Distributed Tracing**: Tracks requests across services and Dapr components (e.g., actors, pub/sub).
- **Metrics**: Measures performance (e.g., request latency, actor counts).
- **Logging**: Captures detailed sidecar and app interactions.

For DACA, this means:
- Insight into actor method calls (`GetConversationHistory`, `AddMessage`) and pub/sub events.
- Performance monitoring for scalability.
- Easier debugging of distributed issues.

---

## Step 3: Enable Distributed Tracing with Zipkin
Dapr supports tracing and exports to Zipkin by default when configured. We’ll set up Zipkin and configure Dapr to use it.

### 3.1: Configure Dapr Tracing
Create `components/tracing.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
spec:
  tracing:
    samplingRate: "1"  # 100% sampling
    zipkin:
      endpointAddress: "http://localhost:9411/api/v2/spans"
````

- samplingRate: "1": Traces all requests (adjust lower in production).
- endpointAddress: Points to Zipkin at localhost:9411.

Note: Dapr doesn’t run Zipkin; we’ll start it alongside the Chat Service in Step 6.```

---

## Step 4: Enable Metrics with Prometheus

We’ll collect Dapr metrics using Prometheus.

### 4.1: Configure Prometheus

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: "dapr"
    static_configs:
      - targets: ["localhost:9091"] # Dapr metrics port (Chat Service)
```

Run Prometheus:

```bash
nerdctl run -d -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

- Verify: `http://localhost:9090`.

---

## Step 5: Enhance Logging

We’ll add structured logging to the Chat Service and use Dapr’s debug logs.

### 5.1: Update `main.py` with Logging

Modify `chat-service/main.py` to include logging (this matches our Step 10 code with added observability):

```python
import logging
import httpx
from typing import List, Dict, Any
from uuid import uuid4
from datetime import datetime, UTC
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dapr.ext.fastapi import DaprActor
from dapr.actor.runtime.runtime import ActorRuntime
from dapr.actor.runtime.config import ActorRuntimeConfig, ActorTypeConfig, ActorReentrancyConfig
from agents import Agent, Runner, function_tool, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ModelProvider
from models import Message, Metadata
from user_session_actor import UserSessionActor, UserSessionActorInterface
from utils import get_gemini_api_key, settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ChatService")

external_client = None
model = None

app = FastAPI(
    title="DACA Chat Service",
    description="A FastAPI-based Chat Service for the DACA tutorial series",
    version="0.1.0"
)

config = ActorRuntimeConfig()
config.update_actor_type_configs([ActorTypeConfig(actor_type=UserSessionActor.__name__, reentrancy=ActorReentrancyConfig(enabled=True))])
ActorRuntime.set_actor_config(config)

actor = DaprActor(app)

@app.on_event("startup")
async def startup():
    global external_client, model
    logger.info("Starting up Chat Service")
    await actor.register_actor(UserSessionActor)
    logger.info(f"Registered actor: {UserSessionActor.__name__}")
    try:
        api_key = await get_gemini_api_key()
        external_client = AsyncOpenAI(api_key=api_key, base_url=settings.MODEL_BASE_URL)
        model = OpenAIChatCompletionsModel(model=settings.MODEL_NAME, openai_client=external_client)
        logger.info("Initialized AI client")
    except Exception as e:
        logger.error(f"Error initializing AI client: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_run_config():
    if model and external_client:
        return RunConfig(model=model, model_provider=external_client, tracing_disabled=True)
    return None

@function_tool
def get_current_time() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

async def publish_conversation_event(user_id: str, session_id: str, user_text: str, reply_text: str, dapr_port: int = 3500) -> None:
    dapr_url = f"http://localhost:{dapr_port}/v1.0/publish/pubsub/conversations"
    event_data = {"user_id": user_id, "session_id": session_id, "event_type": "ConversationUpdated", "user_message": user_text, "assistant_reply": reply_text}
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Publishing event for user {user_id}, session {session_id}")
            response = await client.post(dapr_url, json=event_data)
            response.raise_for_status()
            logger.info(f"Published ConversationUpdated event for user {user_id}, session {session_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to publish event: {e}")

async def get_memory_data(user_id: str, dapr_port: int = 3500) -> Dict[str, str]:
    metadata_url = f"http://localhost:{dapr_port}/v1.0/invoke/agent-memory-service/method/memories/{user_id}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Fetching metadata for user {user_id}")
            response = await client.get(metadata_url)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched metadata for user {user_id}: {data}")
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for user {user_id}: {e}")
            return {"name": user_id, "preferred_style": "casual", "user_summary": f"{user_id} is a new user."}

async def generate_reply(user_id: str, message_text: str, history: List[Dict[str, str]]) -> str:
    try:
        logger.info(f"Generating reply for user {user_id}: {message_text}")
        memory_data = await get_memory_data(user_id)
        name = memory_data.get("name", user_id)
        style = memory_data.get("preferred_style", "casual")
        summary = memory_data.get("user_summary", f"{name} is a new user.")
        history_summary = "No prior conversation." if not history else "\n".join(
            f"User: {entry.get('user_text', '')}\nAssistant: {entry.get('reply_text', '')}" for entry in history[-3:]
        )
        instructions = f"You are a helpful chatbot. Respond in a {style} way. If the user asks for the time, use the get_current_time tool. The user's name is {name}. User summary: {summary}. Conversation history:\n{history_summary}"
        config = get_run_config()
        if not config:
            logger.warning("AI not initialized")
            return "I'm sorry, but I'm not fully initialized yet. Please try again in a moment."
        chat_agent = Agent(name="ChatAgent", instructions=instructions, tools=[get_current_time], model=model)
        result = await Runner.run(chat_agent, input=message_text, run_config=config)
        reply = result.final_output
        logger.info(f"Generated reply: {reply}")
        return reply
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        return "I'm sorry, I encountered an error while processing your message."

async def get_conversation_history(user_id: str, dapr_port: int = 3500) -> List[Dict[str, Any]]:
    url = f"http://localhost:{dapr_port}/v1.0/actors/UserSessionActor/{user_id}/method/GetConversationHistory"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Fetching history for user {user_id}")
            response = await client.post(url, json={})
            response.raise_for_status()
            history = response.json()
            logger.info(f"Received history for user {user_id}: {history}")
            return history if history is not None else []
        except httpx.HTTPStatusError as e:
            logger.warning(f"Error getting history: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 404 or "ERR_ACTOR_INSTANCE_MISSING" in e.response.text:
                return []
            raise
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            raise

async def add_message(user_id: str, message_data: Dict[str, Any], dapr_port: int = 3500) -> None:
    url = f"http://localhost:{dapr_port}/v1.0/actors/UserSessionActor/{user_id}/method/AddMessage"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            logger.info(f"Adding message for user {user_id}: {message_data}")
            headers = {"Content-Type": "application/json"}
            response = await client.post(url, json=message_data, headers=headers)
            response.raise_for_status()
            logger.info(f"Message added for user {user_id}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error adding message: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to add message: {e}")
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add message: {e}")

@app.get("/")
async def root() -> Dict[str, str]:
    logger.info("Received request to root endpoint")
    return {"message": "Welcome to the DACA Chat Service! Access /docs for the API documentation."}

@app.post("/chat/", response_model=Dict[str, Any])
async def chat(message: Message) -> Dict[str, Any]:
    if not message.text.strip():
        logger.warning("Empty message text received")
        raise HTTPException(status_code=400, detail="Message text cannot be empty")
    logger.info(f"Processing chat request for user {message.user_id}: {message.text}")
    session_id = message.metadata.session_id if message.metadata and message.metadata.session_id else str(uuid4())
    try:
        history = await get_conversation_history(message.user_id)
        reply_text = await generate_reply(message.user_id, message.text, history)
        await add_message(message.user_id, {"user_text": message.text, "reply_text": reply_text})
        await publish_conversation_event(message.user_id, session_id, message.text, reply_text, int(settings.DAPR_HTTP_PORT))
        logger.info(f"Chat request completed for user {message.user_id}")
        return {"user_id": message.user_id, "reply": reply_text, "metadata": Metadata(session_id=session_id)}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
```

### 5.2: Dapr Logging

Run Dapr with `--log-level debug` for detailed sidecar logs.

---

## Step 6: Run with Observability

1. **Start Dapr**:

   ```bash
   dapr init
   ```

2. Start Agent Memory Service

```bash
dapr run --app-id agent-memory-service --app-port 8001 --dapr-http-port 3501 --resources-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

2. **Run Chat Service with Observability**:

   ```bash
   cd chat-service
   dapr run --app-id chat-service --app-port 8010 --dapr-http-port 3500 --metrics-port 9091 --log-level debug --config ../components/tracing.yaml --resources-path ../components -- uv run uvicorn main:app --host 0.0.0.0 --port 8010 --reload
   ```

   - `--metrics-port 9091`: Exposes Dapr metrics.
   - `--config ../components/tracing.yaml`: Enables Zipkin tracing.

3. **Test the Chat Endpoint**:
   ```bash
   curl -X POST http://localhost:8010/chat/ -H "Content-Type: application/json" -d '{"user_id": "junaid", "text": "Hi there"}'
   ```
   - Expected response:
     ```json
     {
       "user_id": "junaid",
       "reply": "Hey junaid! Hi there!",
       "metadata": { "session_id": "..." }
     }
     ```

---

## Step 7: Observe the System

### Logs

Check Chat Service logs:

```
2025-04-09 12:00:00,123 - ChatService - INFO - Starting up Chat Service
2025-04-09 12:00:00,124 - ChatService - INFO - Registered actor: UserSessionActor
2025-04-09 12:00:00,125 - ChatService - INFO - Processing chat request for user junaid: Hi there
2025-04-09 12:00:00,126 - ChatService - INFO - Fetching history for user junaid
2025-04-09 12:00:00,130 - ChatService - INFO - Received history for user junaid: []
2025-04-09 12:00:00,131 - ChatService - INFO - Generating reply for user junaid: Hi there
2025-04-09 12:00:00,135 - ChatService - INFO - Generated reply: Hey junaid! Hi there!
2025-04-09 12:00:00,136 - ChatService - INFO - Adding message for user junaid: {"user_text": "Hi there", "reply_text": "Hey junaid! Hi there!"}
2025-04-09 12:00:00,140 - ChatService - INFO - Message added for user junaid
2025-04-09 12:00:00,141 - ChatService - INFO - Publishing event for user junaid, session ...
2025-04-09 12:00:00,145 - ChatService - INFO - Published ConversationUpdated event for user junaid, session ...
2025-04-09 12:00:00,146 - ChatService - INFO - Chat request completed for user junaid
```

### Traces in Zipkin

- Visit `http://localhost:9411`.
- Search for `chat-service` traces.
- Expect spans for:
  - `/chat/` endpoint.
  - Actor calls (`GetConversationHistory`, `AddMessage`).
  - Pub/sub (`conversations` topic).

### Metrics

Dapr exposes metrics on the port specified by --metrics-port (in our case, 9091 for the Chat Service).
Check if the metrics endpoint is accessible:

```bash
curl http://localhost:9091/metrics
```

Send multiple requests to the Chat Service:

```bash
curl -X POST http://localhost:8010/chat/ -H "Content-Type: application/json" -d '{"user_id": "junaid", "text": "Hi there"}'
curl -X POST http://localhost:8010/chat/ -H "Content-Type: application/json" -d '{"user_id": "junaid", "text": "What time is it?"}'
```

Wait a few seconds, then check the metrics endpoint again:

```bash
curl http://localhost:9091/metrics | grep dapr
```

### Metrics in Prometheus

- Visit `http://localhost:9090`.
- Query:
  - `dapr_http_server_request_count{app_id="chat-service"}`: Request count.
  - `dapr_actor_active_actors{app_id="chat-service", actor_type="UserSessionActor"}`: Active actors.

#### Debugging

If you see nothing change your port

1. First check: http://localhost:9090/targets?search=
2. Get your ip `bash ifconfig | grep inet ` it shall be something like 192.164.0.000 (from inet 192.164.0.000 netmask 0xffffff00)
3. In promethous.yaml update your

```yaml
- targets: ["192.164.0.000"] # Dapr metrics port (Chat Service)
```

4. Stop and start the container
5. Test time

- http://localhost:9090/targets?search=
- Visit `http://localhost:9090`.
- Query:
  - `dapr_http_server_request_count{app_id="chat-service"}`: Request count.
  - `dapr_actor_active_actors{app_id="chat-service", actor_type="UserSessionActor"}`: Active actors.

---

## Step 8: Why Observability for DACA?

- **Visibility**: Traces show request flows through actors and pub/sub.
- **Performance**: Metrics monitor latency and throughput.
- **Debugging**: Logs and traces pinpoint issues (e.g., actor state errors).

---

## Step 9: Next Steps

Next, in **12_dapr_containerization**, we’ll containerize the Chat Service and deploy it to Kubernetes with Dapr.

### Optional Exercises

- Add Grafana for Prometheus dashboards.
- Simulate a failure (e.g., stop Redis) and debug with Zipkin.
- Log custom metrics (e.g., messages per user).

---

## Conclusion

You’ve added Dapr observability to the Chat Service, enabling tracing, metrics, and logging for monitoring and debugging. This step enhances DACA’s production readiness, providing critical insights into our distributed system.
