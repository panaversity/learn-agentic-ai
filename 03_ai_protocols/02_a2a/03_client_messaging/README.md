# Step 3: [Client Messaging](https://a2a-protocol.org/latest/specification/#7-protocol-rpc-methods) & Discovery

**Learning Goal**: Master the client side of A2A - discover agents, send messages, and build single-agent communication patterns. Build complete A2A client applications using the official SDK.

## 🎯 Learning Objectives

By the end of this step, you will:

- ✅ **Master Agent Discovery**: Use A2ACardResolver to find and analyze agents
- ✅ **Implement A2A Messaging**: Send messages using A2AClient and raw HTTP APIs
- ✅ **Parse Agent Capabilities**: Understand agent cards, skills, and transport options
- ✅ **Build Client Applications**: Create complete client-side A2A applications
- ✅ **Debug Communication Issues**: Troubleshoot common client-side problems
- ✅ **Use Starter Code**: Leverage Step 1 agent implementation as your test target

## 🌐 The Client Side of A2A

### You've Built Agents, Now Use Them!

In Steps 1-2, you learned to **build** A2A agents:

- ✅ Agent cards and skills (Step 1)
- ✅ Agent executors and routing (Step 2)

Now you'll learn to **use** those agents as a client:

- 🔍 **Discover** agents automatically
- 📨 **Send messages** to remote agents
- 🤝 **Coordinate** multiple agents together

### The Complete A2A Ecosystem

```
┌─────────────────┐    A2A Discovery     ┌─────────────────┐
│                 │◄─────────────────────►│                 │
│  Client Agent   │                      │  Remote Agent   │
│                 │    A2A Messaging     │                 │
│ (Your Code)     │◄─────────────────────►│ (From Steps 1-2)│
└─────────────────┘                      └─────────────────┘
        │                                         │
        │ Discovers Multiple                      │ Specialized
        │ Specialized Agents                      │ Capabilities
        ▼                                         ▼
┌─────────────────┐                      ┌─────────────────┐
│ Calendar Agent  │                      │ Travel Agent    │
│ Weather Agent   │                      │ Shopping Agent  │
│ Email Agent     │                      │ etc...          │
└─────────────────┘                      └─────────────────┘
```

## 📚 Core Client Concepts

### 1. Agent Discovery with A2ACardResolver

```python
import httpx
from a2a.client import A2ACardResolver

# Set up resolver for your Step 1 agent

async def main():
    # Discover your calendar agent
    try:
        async with httpx.AsyncClient() as httpx_client:
            
            resolver = A2ACardResolver(base_url="http://localhost:8000", httpx_client=httpx_client)
            agent_card = await resolver.get_agent_card()
            print(f"Found agent: {agent_card}")

            # Access specific agent card
            print(f"Agent name: {agent_card.name}")
            print(f"Skills: {[skill.name for skill in agent_card.skills]}")
            print(f"Transport: {agent_card.preferred_transport}")

    except Exception as e:
        print(f"Error fetching agent cards: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 2. Messaging with A2AClient

```python
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig, Client
from a2a.types import Message, TextPart

async def main():
    # Discover your calendar agent
    try:
        async with httpx.AsyncClient() as httpx_client:
            
            resolver = A2ACardResolver(base_url="http://localhost:8000", httpx_client=httpx_client)
            agent_card = await resolver.get_agent_card()
            print(f"Found agent: {agent_card}")

            # Create A2A client with discovered agent cards
            client: Client = ClientFactory(config=ClientConfig(httpx_client=httpx_client, streaming=False)).create(card=agent_card)

            # Create message with proper structure
            message = Message(
                role="user",
                message_id="123",
                parts=[TextPart(text="Schedule a team meeting for tomorrow at 2 PM")]
            )

            response = client.send_message(message)
            async for chunk in response:
                print("CHUNK", chunk)

    except Exception as e:
        print(f"Error fetching agent cards: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 3. Raw HTTP API Communication (Alternative)

You can also communicate directly using HTTP APIs from **Step 0** transport specs and **Step 2** Postman collection:

```python
import httpx
import json

async def main():
    # Method 1: Direct A2A endpoint (JSON-RPC 2.0)
    async with httpx.AsyncClient() as client:
        discovery_response = await client.get("http://localhost:8000/.well-known/agent-card.json")
        agent_card = discovery_response.json()
        print("\n\nAgent Card:\n\n", json.dumps(agent_card, indent=2), "\n\n")

        response = await client.post("http://localhost:8000", json={
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    'messageId': '123', 
                    'metadata': None, 
                    'parts': [{'kind': 'text', 'metadata': None, 'text': 'Schedule a team meeting for tomorrow at 2 PM'}], 
                    'referenceTaskIds': None, 
                    'role': 'user', 
                    'taskId': None
                    }
            },
            "id": "req-123"
        })
        result = response.json()
        print("\n\nRES\n\n", result)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**💡 When to use each approach:**

- **A2A SDK**: For production applications, type safety, automatic retries
- **Raw HTTP**: For learning transport details, custom integrations, debugging

## 🎯 Quick Success Check

After completing exercises, you should be able to:

- [ ] **Discover your Step 1 agent** and see its skills
- [ ] **Send a message** and get a response
- [ ] **Understand the difference** between A2A SDK and raw HTTP

**⚡ Fast Track**: If all three work, you've mastered A2A client basics!

## ✅ Success Criteria

You've mastered A2A client basics when you can:

- [ ] **Discover your Step 1 agent** using A2ACardResolver
- [ ] **Send messages** using A2AClient with proper Message/TextPart structure
- [ ] **Understand raw HTTP** as alternative to A2A SDK (optional)
- [ ] **Handle basic errors** like connection failures

## 🎓 Key Takeaways

1. **Discovery is Powerful**: Automatic agent discovery enables dynamic communication patterns
2. **Two Communication Paths**: A2A SDK for ease vs raw HTTP for control and learning
3. **Step 1 as Foundation**: Your calendar agent provides perfect testing ground for client development
4. **Error Handling Matters**: Network issues are common in distributed systems
5. **Protocol Understanding**: Step 0 transport specs and Step 2 Postman collection provide HTTP details
6. **Simple Before Complex**: Master single-agent communication before multi-agent coordination

## 🚀 Next Step

With A2A fundamentals, executor patterns, and client communication mastered, you're ready for **Step 4: Streaming & Real-time** where you'll learn streaming responses and real-time communication patterns.

---

**Time Investment**: ~2 hours  
**Difficulty**: Beginner-Intermediate  
**Skills Gained**: Agent discovery, A2A messaging, HTTP APIs, client development  
**Prerequisites**: Steps 0-2 (Transport Specs, A2A Fundamentals, Agent Executor)

**🎉 Congratulations! You've mastered A2A client communication patterns!**
