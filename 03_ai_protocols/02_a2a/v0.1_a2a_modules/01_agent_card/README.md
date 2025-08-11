# Step 01: [Agent Card 🏷️](https://google-a2a.github.io/A2A/latest/specification/#55-agentcard-object-structure)

The Agent Card is a JSON document that an A2A Server makes available, typically at a .well-known/agent-card.json endpoint. It's like a digital business card for the agent.

> **Goal**: Create the simplest possible A2A agent that serves an agent card for discovery.

## 🎯 What You'll Learn

- What an A2A agent card looks like
- How agent discovery works via `/.well-known/agent-card.json`
- Basic server setup and [AgentCard using official sdk](https://google-a2a.github.io/A2A/latest/sdk/python/#a2a.types.AgentCard).
- Visual testing in browser
- Foundation for all A2A agents

## 💡 Key Insights

1. **A2A agents are discoverable** - The `/.well-known/agent-card.json` endpoint is how agents find each other
2. **Agent cards are metadata** - They describe what an agent can do before actually using it
3. **Visual testing works** - Browser testing gives immediate feedback on JSON structure
4. **Standards matter** - Following the A2A specification ensures interoperability
5. **Simple foundation** - This basic pattern is the foundation for all A2A agents

## 🚀 Implementation

```bash
uv init agent_card_server
cd agent_card_server

uv add a2a-sdk uvicorn
```

**File**: `agent_card.py`

```python
from a2a.types import AgentCapabilities, AgentCard, AgentProvider

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue


class HelloWorldAgentExecutor(AgentExecutor):

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        ...

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        ...


# Complete Agent Card following A2A specification
public_agent_card = AgentCard(
    name='Hello World A2A Agent',
    description='A simple A2A agent that demonstrates basic agent card discovery and structure. This agent serves as a foundation for learning A2A protocol concepts.',
    url='http://localhost:8000/',
    version='1.0.0',
    provider=AgentProvider(
        organization='A2A Learning Lab',
        url='https://github.com/your-org/a2a-learning'
    ),
    iconUrl='http://localhost:8000/icon.png',  # Optional: agent icon
    documentationUrl='http://localhost:8000/docs',  # Optional: documentation
    defaultInputModes=['text/plain', 'application/json'],
    defaultOutputModes=['text/plain', 'application/json'],
    capabilities=AgentCapabilities(
        streaming=True,
        pushNotifications=False,
        stateTransitionHistory=False
    ),
    skills=[],  # Empty for basic agent card - skills added in Step 02
    # Security schemes would be added for production agents
    securitySchemes=None,  # None for development - add authentication in production
    security=None,  # None for development
    supportsAuthenticatedExtendedCard=False  # Set to True if supporting extended cards
)
```

```python
# main.py
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from agent_card import HelloWorldAgentExecutor, public_agent_card

# --8<-- [end:AgentCard]
request_handler = DefaultRequestHandler(
    agent_executor=HelloWorldAgentExecutor(),
    task_store=InMemoryTaskStore(),
)

server_app = A2AStarletteApplication(
    agent_card=public_agent_card,
    http_handler=request_handler
)

server = server_app.build()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(server, host='0.0.0.0', port=8000)

```

## 🧪 Testing

### 1. Start the Server

```bash
uv run python main.py
```

### 2. Visual Test in Browser

Open this URL in your browser:

**Agent Card**: http://localhost:8000/.well-known/agent-card.json

- **This is the key!** - Shows the complete agent card JSON
- Notice all the fields: name, description, provider, capabilities, etc.
- This is how other A2A agents discover us and understand our capabilities

### 3. Examine Agent Card Structure

When you view the agent card, you should see:

```json
{
  "capabilities": {
    "pushNotifications": false,
    "stateTransitionHistory": false,
    "streaming": true
  },
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "description": "A simple A2A agent that demonstrates basic agent card discovery and structure. This agent serves as a foundation for learning A2A protocol concepts.",
  "documentationUrl": "http://localhost:8000/docs",
  "iconUrl": "http://localhost:8000/icon.png",
  "name": "Hello World A2A Agent",
  "provider": {
    "organization": "A2A Learning Lab",
    "url": "https://github.com/your-org/a2a-learning"
  },
  "skills": [],
  "supportsAuthenticatedExtendedCard": false,
  "url": "http://localhost:8000/",
  "version": "1.0.0"
}
```

## 🔍 Key A2A Concepts

### Complete Agent Card Structure

Following the [official A2A specification](https://google-a2a.github.io/A2A/latest/specification/#55-agentcard-object-structure):

#### Required Fields

- **name**: Human-readable agent name
- **description**: What this agent does (supports CommonMark markdown)
- **url**: Base URL where agent is hosted (must be absolute, HTTPS for production)
- **version**: Agent version for compatibility tracking
- **defaultInputModes**: Media types agent accepts (e.g., 'text/plain', 'application/json')
- **defaultOutputModes**: Media types agent produces
- **capabilities**: Advanced A2A protocol features supported
- **skills**: Array of specific skills agent offers

#### Optional Fields (Production Important)

- **provider**: Information about organization providing the agent
- **iconUrl**: URL to agent icon for visual identification
- **documentationUrl**: Link to human-readable documentation
- **securitySchemes**: Authentication methods supported (OAuth, API keys, etc.)
- **security**: Security requirements for accessing agent
- **supportsAuthenticatedExtendedCard**: Whether agent provides extended capabilities when authenticated

#### Capabilities Object

- **streaming**: Supports Server-Sent Events (SSE) for real-time updates
- **pushNotifications**: Can send async notifications to client webhooks
- **stateTransitionHistory**: Exposes detailed task status change history

### Discovery Mechanism

- **`/.well-known/agent-card.json`** is the standard A2A discovery endpoint
- Other agents can find and understand our capabilities
- This follows the "well-known URI" standard (RFC 8615)
- Essential for agent-to-agent communication

### Why This Matters

- **Foundation**: Every A2A agent must serve an agent card
- **Interoperability**: Standard format enables agent discovery
- **Capabilities advertising**: Agents know what others can do before using them

### 🔒 Security Considerations

Based on [A2A security research](https://arxiv.org/html/2504.16902), agent cards require careful security attention:

#### Agent Card Security

- **Treat as untrusted input**: Agent cards from external sources should be sanitized
- **Validate all fields**: Ensure proper structure and content validation
- **Secure hosting**: Use HTTPS and proper access controls for agent card endpoints
- **Avoid sensitive data**: Don't include secrets or sensitive information in public agent cards

## 🎯 Next Step

**Ready for Step 02?** → [02_agent_skill](../02_agent_skill/) - Add skills to your agent card

---

## 📖 Official Reference

This step introduces concepts from: [Agent Skills & Agent Card](https://google-a2a.github.io/A2A/latest/tutorials/python/3-agent-skills-and-agent-card/)

**🎉 Congratulations! You've created your first discoverable A2A agent!**
