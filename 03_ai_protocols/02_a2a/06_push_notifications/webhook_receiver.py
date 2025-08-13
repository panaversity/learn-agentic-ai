import uvicorn

from datetime import datetime
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.body()
    print(f"\n📡 Webhook received at {datetime.now().isoformat()}")
    print("Headers", request.headers)
    print(f"Payload: {payload.decode()}")
    return {"status": "received"}

@app.get("/")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "running", 
        "service": "A2A Webhook Receiver",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🎣 Starting A2A Webhook Receiver on port 9000...")
    print("📡 Ready to receive notifications!")
    uvicorn.run(app, host="localhost", port=9000)