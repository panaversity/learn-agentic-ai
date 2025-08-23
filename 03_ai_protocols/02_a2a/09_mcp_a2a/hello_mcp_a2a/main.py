import contextlib
from fastapi import FastAPI

from a2a_server import agent_app
from mcp_server import mcp_app, mcp_app_instance

# Create a combined lifespan to manage both session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(mcp_app.session_manager.run())
            yield
    except Exception as e:
        print("Error occurred:", e)


app = FastAPI(lifespan=lifespan)

app.mount("/a2a", agent_app)
app.mount("/exchange", mcp_app_instance)

async def main():
    print("🔗 Agent Card: http://localhost:8000/a2a/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8000/a2a")
    print("📮 MCP Endpoint: http://localhost:8000/exchange/mcp")

    import uvicorn
    config = uvicorn.Config(
        app = app,
        host="localhost",
        port=8000,
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    