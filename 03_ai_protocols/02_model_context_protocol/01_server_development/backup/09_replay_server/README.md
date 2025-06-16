# MCP EventStore Examples

This directory contains UV projectsdemonstrating MCP EventStore functionality

## Project: `replay_server` - Event Replay  
Shows how EventStore can replay events for debugging and recovery.

## Setup Instructions


### Replay Server Setup
```bash
# 1. Create and setup replay_server
cd replay_server  
uv sync  # Install dependencies

# 2. Run the server (in one terminal)
python server.py
# Server starts on http://localhost:8001

# 3. Run the client (in another terminal)
python client.py
```

## What You'll See

### Replay Server Demo
- **Event generation**: Multiple events per request
- **Event logging**: Server logs all events
- **EventStore**: Stores events for replay capability
- **Demonstration**: Shows how events can be replayed

## Key Concepts

### EventStore Interface
```python
class EventStore(ABC):
    async def store_event(self, stream_id: str, message: JSONRPCMessage) -> str:
        """Store an event and return event ID"""
        
    async def replay_events_after(self, last_event_id: str, send_callback) -> str | None:
        """Replay events after the given event ID"""
```

### Production EventStore Options
- **Redis**: For horizontal scaling
- **PostgreSQL**: For ACID compliance  
- **CockroachDB**: For global distribution
- **Local Files**: For development

## Troubleshooting

### Common Issues
- **Import errors**: Make sure you're in the right directory and ran `uv sync`
- **Port conflicts**: Resume server uses 8000, replay server uses 8001
- **Connection refused**: Make sure the server is running before starting client

### Manual Dependencies (if UV fails)
```bash
pip install mcp httpx uvicorn
``` 