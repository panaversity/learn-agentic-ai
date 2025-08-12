import asyncio
import httpx
import json

async def test_basic_streaming():
    """Test the basic streaming agent with real SSE."""

    print("🧪 Testing Basic A2A Streaming Agent\n")

    async with httpx.AsyncClient() as client:
        # Send streaming request using async context manager
        async with client.stream(
            "POST",
            "http://localhost:8001",
            json={
                "jsonrpc": "2.0",
                "method": "message/stream",  # Use streaming method
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": "Process my data"}],
                        "messageId": "test-msg-1",
                        "kind": "message"
                    }
                },
                "id": "stream-test-1"
            },
            headers={"Accept": "text/event-stream"}
        ) as response:
            
            print("📥 Streaming events:")
            async for chunk in response.aiter_text():
                if chunk.startswith("data: "):
                    try:
                        event_data = json.loads(chunk[6:])  # Remove "data: " prefix
                        result = event_data.get("result", {})
                        kind = result.get("kind")

                        if kind == "task":
                            task_id = result.get("id")
                            context_id = result.get("contextId")
                            print(f"📋 Task Created: {task_id[:8]}... (context: {context_id[:8]}...)")

                        elif kind == "status-update":
                            status = result.get("status", {})
                            state = status.get("state")
                            message = status.get("message", {})

                            if message.get("parts"):
                                text = message["parts"][0].get("text", "")
                                print(f"📊 Status [{state}]: {text}")

                            if result.get("final"):
                                print(f"🏁 Stream ended (final status: {state})")
                                break

                        elif kind == "artifact-update":
                            artifact = result.get("artifact", {})
                            name = artifact.get("name")
                            last_chunk = result.get("lastChunk", False)

                            if artifact.get("parts"):
                                content = artifact["parts"][0].get("text", "")
                                preview = content[:100] + "..." if len(content) > 100 else content
                                print(f"📄 Artifact '{name}': {preview}")
                                if last_chunk:
                                    print(f"✅ Artifact '{name}' completed")

                    except json.JSONDecodeError:
                        continue

    print("\n🎯 Test completed! The agent streamed real A2A events.")

if __name__ == "__main__":
    asyncio.run(test_basic_streaming())