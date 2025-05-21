import httpx
import asyncio

async def consume_generic_stream():
    print("--- Generic Client: Attempting to connect to generic stream ---")
    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", "http://127.0.0.1:8000/generic-stream") as response:
                print(f"Generic Stream Response Status: {response.status_code}")
                response.raise_for_status()

                buffer = ""
                print("Generic Client: Receiving stream...")
                async for chunk in response.aiter_text(): # Process text chunk by chunk
                    # Buffering can be useful if messages are split across chunks
                    # or if you want to process line by line from a continuous text stream.
                    buffer += chunk
                    while "\n" in buffer: # Process complete lines
                        line, buffer = buffer.split("\n", 1)
                        if line: # Ensure the line is not empty
                            print(f"Client received complete line: {line}")
                if buffer: # Print any remaining data in the buffer (if stream doesn't end with newline)
                    print(f"Client received remaining data: {buffer.strip()}")
            print("--- Generic Client: Stream finished ---")
    except httpx.ConnectError as e:
        print(f"--- Generic Client: Connection Error: {e}. Is the server (generic_stream_server.py) running on port 8000? ---")
    except httpx.RequestError as e:
        print(f"--- Generic Client: Request Error during streaming: {e} ---")
    except Exception as e:
        print(f"--- Generic Client: An unexpected error occurred: {e} ---")

if __name__ == "__main__":
    asyncio.run(consume_generic_stream())