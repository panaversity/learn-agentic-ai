# Step 08: Push Notifications 📲

**Implement push notifications for disconnected scenarios**

> **Goal**: Learn A2A push notifications for long-running tasks when clients can't maintain persistent connections.

## 🎯 What You'll Learn

- [Push Notifications](https://google-a2a.github.io/A2A/latest/topics/streaming-and-async/#2-push-notifications-for-disconnected-scenarios) for disconnected scenarios
- Webhook-based notification patterns
- Security considerations for push notifications
- PushNotificationConfig setup
- Long-running task management

## 📋 Prerequisites

- Completed Steps 01-07 (Agent Card through Multiturn)
- Understanding of webhooks and HTTP callbacks
- UV package manager installed

## 🚀 Implementation

### 1. Create UV Project
```bash
cd 08_push_notifications
uv init a2a08_code
cd a2a08_code
uv add a2a-server a2a-client fastapi uvicorn
```

### 2. Long-Running Agent with Push Notifications

**File**: `long_running_agent.py`

```python
import asyncio
import uvicorn
from datetime import datetime

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from a2a.utils import new_agent_text_message


class LongRunningAgent:
    """Agent that simulates long-running tasks."""

    async def invoke(self, task_description: str) -> str:
        # Simulate a long-running task (e.g., data processing, model training)
        print(f"🔄 Starting long-running task: {task_description}")
        
        # Simulate work that takes time
        await asyncio.sleep(10)  # 10 seconds for demo
        
        result = f"✅ Completed long-running task: {task_description} at {datetime.now().isoformat()}"
        print(result)
        return result


class LongRunningAgentExecutor(AgentExecutor):
    """Agent Executor for long-running tasks with push notification support."""

    def __init__(self):
        self.agent = LongRunningAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute long-running agent task."""
        # Extract task description from message
        message = context.message
        task_description = "default task"
        
        for part in message.parts:
            if part.kind == "text":
                task_description = part.text
                break
        
        # Execute the long-running task
        result = await self.agent.invoke(task_description)
        
        # Send result back
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the long-running task."""
        await event_queue.enqueue_event(
            new_agent_text_message("❌ Long-running task was cancelled")
        )


if __name__ == '__main__':
    # Agent skill for long-running tasks
    skill = AgentSkill(
        id='long_running_task',
        name='Long Running Task Processor',
        description='Processes long-running tasks with push notification support',
        tags=['long-running', 'async', 'push-notifications'],
        examples=[
            'process large dataset',
            'train machine learning model', 
            'generate comprehensive report'
        ],
    )

    # Agent card with push notification capability
    agent_card = AgentCard(
        name='Long Running Task Agent',
        description='Agent that handles long-running tasks with push notifications',
        url='http://localhost:8000/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=True  # Enable push notifications
        ),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=LongRunningAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    print("📲 Starting Long-Running Agent with Push Notifications...")
    print("📋 Agent Discovery: http://localhost:8000/.well-known/agent.json")
    print("💬 A2A Endpoint: http://localhost:8000/a2a")
    print("⏱️ Tasks will take ~10 seconds to complete")
    uvicorn.run(server.build(), host='0.0.0.0', port=8000)
```

### 3. Webhook Notification Receiver

**File**: `webhook_receiver.py`

```python
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
import json

app = FastAPI(title="Push Notification Webhook Receiver")

# Store received notifications for demo
received_notifications = []

@app.post("/webhook/notifications")
async def receive_notification(request: Request):
    """Receive push notifications from A2A server."""
    try:
        # Get the notification payload
        body = await request.body()
        notification_data = json.loads(body) if body else {}
        
        # Log the notification
        timestamp = datetime.now().isoformat()
        notification = {
            "timestamp": timestamp,
            "headers": dict(request.headers),
            "payload": notification_data
        }
        
        received_notifications.append(notification)
        
        print(f"📲 Received push notification at {timestamp}:")
        print(f"   Headers: {dict(request.headers)}")
        print(f"   Payload: {notification_data}")
        
        # Validate notification token if provided
        notification_token = request.headers.get("X-A2A-Notification-Token")
        if notification_token:
            print(f"   Token: {notification_token}")
        
        return {"status": "received", "timestamp": timestamp}
        
    except Exception as e:
        print(f"❌ Error processing notification: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/webhook/notifications")
async def list_notifications():
    """List all received notifications."""
    return {
        "total_notifications": len(received_notifications),
        "notifications": received_notifications
    }

@app.get("/webhook/health")
async def webhook_health():
    """Health check for webhook receiver."""
    return {"status": "healthy", "service": "webhook-receiver"}

if __name__ == "__main__":
    print("🎣 Starting Webhook Notification Receiver...")
    print("📲 Webhook URL: http://localhost:9000/webhook/notifications")
    print("📋 View notifications: http://localhost:9000/webhook/notifications")
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

### 4. Client with Push Notification Setup

**File**: `push_notification_client.py`

```python
import logging
import asyncio
from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    PushNotificationConfig,
)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    base_url = 'http://localhost:8000'
    webhook_url = 'http://localhost:9000/webhook/notifications'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        # Fetch agent card
        logger.info(f'Fetching agent card from: {base_url}/.well-known/agent.json')
        agent_card: AgentCard = await resolver.get_agent_card()
        
        # Check if agent supports push notifications
        if not agent_card.capabilities.pushNotifications:
            logger.error("❌ Agent does not support push notifications!")
            return
            
        logger.info("✅ Agent supports push notifications")
        logger.info(agent_card.model_dump_json(indent=2, exclude_none=True))

        # Initialize client
        client = A2AClient(
            httpx_client=httpx_client, agent_card=agent_card
        )
        logger.info('A2AClient initialized.')

        # Configure push notifications
        push_config = PushNotificationConfig(
            url=webhook_url,
            token="demo-notification-token-123",  # Optional validation token
            # authentication could be added here for production
        )

        # Send message with push notification config
        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'Process a large dataset for analysis'}
                ],
                'messageId': uuid4().hex,
            },
            'pushNotification': push_config.model_dump()  # Add push notification config
        }
        
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        logger.info(f"📤 Sending long-running task with push notification to: {webhook_url}")
        response = await client.send_message(request)
        
        logger.info("📋 Task submitted successfully!")
        logger.info(f"Task ID: {response.result.id}")
        logger.info(f"Task Status: {response.result.status.state}")
        
        logger.info("⏱️ Task is running... Check webhook receiver for completion notification")
        logger.info(f"🎣 Monitor notifications at: http://localhost:9000/webhook/notifications")


if __name__ == '__main__':
    asyncio.run(main())
```

## 🧪 Testing

### 1. Start the Webhook Receiver
```bash
# Terminal 1
cd a2a08_code
python webhook_receiver.py
```

### 2. Start the Long-Running Agent
```bash
# Terminal 2
cd a2a08_code
python long_running_agent.py
```

### 3. Send Task with Push Notification
```bash
# Terminal 3
cd a2a08_code
python push_notification_client.py
```

### 4. Monitor Notifications
```bash
# Check received notifications
curl http://localhost:9000/webhook/notifications | jq '.'

# Or open in browser
open http://localhost:9000/webhook/notifications
```

### 5. Manual Push Notification Test
```bash
# Send task with push notification via curl
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "Train a machine learning model"
          }
        ],
        "messageId": "test-123"
      },
      "pushNotification": {
        "url": "http://localhost:9000/webhook/notifications",
        "token": "manual-test-token"
      }
    },
    "id": "req-456"
  }' | jq '.'
```

## 📊 Expected Flow

1. **Task Submission**: Client submits long-running task with push notification config
2. **Immediate Response**: Server returns task ID and "working" status
3. **Background Processing**: Agent processes task asynchronously (10 seconds)
4. **Push Notification**: Server sends HTTP POST to webhook URL when task completes
5. **Client Retrieval**: Client can fetch completed task using task ID

**Push Notification Payload Example:**
```json
{
  "taskId": "task-abc123",
  "status": "completed",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔍 Key A2A Concepts

### Push Notification Configuration
- **url**: Webhook URL where server sends notifications
- **token**: Optional validation token for security
- **authentication**: Optional auth config for webhook security

### Security Considerations
- **Webhook URL Validation**: Servers should validate webhook URLs
- **Authentication**: Webhook receivers should authenticate notifications
- **Token Validation**: Use tokens to validate notification authenticity
- **HTTPS Requirements**: Production should use HTTPS for webhooks

### Use Cases
- **Long-running tasks**: Data processing, model training, report generation
- **Mobile clients**: Apps that can't maintain persistent connections
- **Serverless functions**: Functions with limited execution time
- **Batch processing**: Tasks that run for hours or days

## ✅ Success Criteria

- ✅ Agent supports push notifications (capabilities.pushNotifications: true)
- ✅ Webhook receiver handles incoming notifications
- ✅ Client configures push notifications properly
- ✅ Long-running tasks trigger push notifications
- ✅ Notifications include task ID and status
- ✅ Security tokens are properly handled

## 🎯 Next Step

**Ready for Step 09?** → [09_agent_discovery](../09_agent_discovery/) - Discover and connect to other agents

---

## 💡 Key Insights

1. **Disconnected scenarios**: Push notifications enable long-running tasks without persistent connections
2. **Webhook pattern**: Standard HTTP callback pattern for async notifications
3. **Security is crucial**: Validate webhook URLs and authenticate notifications
4. **Task-based workflow**: Tasks continue running even if client disconnects
5. **Production considerations**: Use HTTPS, proper authentication, and error handling

## 📖 Official Reference

This step implements: [Push Notifications for Disconnected Scenarios](https://google-a2a.github.io/A2A/latest/topics/streaming-and-async/#2-push-notifications-for-disconnected-scenarios)

**🎉 Congratulations! You've implemented A2A push notifications for disconnected scenarios!** 