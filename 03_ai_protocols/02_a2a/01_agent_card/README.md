# Step 1: Agent Card

The Agent Card is a JSON document that an A2A Server makes available, typically at a .well-known/agent-card.json endpoint. It's like a digital business card for the agent.

## 🎯 Goal

Create and serve your first A2A agent card - the "business card" that tells other agents what you can do.

## 🔍 What You'll Learn

- A2A agent card structure and fields
- How agents advertise their capabilities
- Visual feedback with browser testing
- Well-known URI pattern for discovery

## 🚀 Quick Start

```bash
# Start the simple HTTP server
python server.py

# Open browser to see agent card
open http://localhost:8000/.well-known/agent-card.json

# Test with curl
curl http://localhost:8000/.well-known/agent-card.json | jq
```

## 📋 Agent Card Structure

```json
{
  "name": "Greeting Agent",
  "description": "A simple agent that returns friendly greetings",
  "url": "localhost:8000",
  "version": "0.3.0",
  "skills": [
    {
      "name": "greet_users",
      "description": "Returns a friendly greeting message"
    }
  ],
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain", "application/json"]
}
```

## 🎯 Success Criteria

- ✅ Server starts on port 8000
- ✅ Agent card loads in browser
- ✅ JSON is valid and well-formatted
- ✅ curl command returns agent card

**Next**: [Step 2: Agent Skills](../02_agent_skills/) - Add rich skill definitions
