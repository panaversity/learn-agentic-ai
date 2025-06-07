from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import time
import uvicorn # For running the FastAPI app

app_generic_stream = FastAPI(title="Generic Streaming Server")

async def generic_data_streamer():
    # This generator function implicitly enables chunked transfer encoding
    # if the response length isn't set beforehand.
    for i in range(5):
        data_chunk = f"Timestamp: {time.time()} - Data item {i}\n"
        yield data_chunk # Data is sent as it's yielded
        print(f"Server yielded: {data_chunk.strip()}")
        await asyncio.sleep(1) # Simulate time taken to generate/fetch data
    final_message = f"Timestamp: {time.time()} - End of generic stream.\n"
    yield final_message
    print(f"Server yielded: {final_message.strip()}")

@app_generic_stream.get("/generic-stream")
async def stream_data_endpoint():
    # FastAPI's StreamingResponse with a generator automatically handles chunked encoding.
    return StreamingResponse(generic_data_streamer(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app_generic_stream, host="127.0.0.1", port=8000, log_level="info")