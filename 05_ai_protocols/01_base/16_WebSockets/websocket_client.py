import asyncio
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLIENT - %(levelname)s - %(message)s')

async def send_and_receive_messages(uri):
    """
    Connects to the WebSocket server, sends a few messages,
    and receives responses.
    """
    try:
        async with websockets.connect(uri) as websocket:
            logging.info(f"Connected to WebSocket server at {uri}")

            messages_to_send = [
                "Hello WebSocket Server!",
                "This is a test message.",
                "How are you today?",
                "QUIT" # A special message to gracefully close from client side if server handles it
            ]

            for message in messages_to_send:
                if not websocket.open:
                    logging.warning("Connection closed before sending all messages.")
                    break
                
                logging.info(f"Sending message: '{message}'")
                await websocket.send(message)
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    logging.info(f"Received response: '{response}'")
                except asyncio.TimeoutError:
                    logging.error("Timeout waiting for server response.")
                    break # Stop if server isn't responding
                except websockets.exceptions.ConnectionClosed:
                    logging.warning("Connection closed by server while waiting for response.")
                    break
                
                await asyncio.sleep(1) # Small delay between messages

            # Explicitly close the connection if it's still open
            if websocket.open:
                logging.info("Closing WebSocket connection.")
                await websocket.close(code=1000, reason="Client finished")
            
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection to {uri} closed with error: {e}")
    except websockets.exceptions.InvalidURI:
        logging.error(f"Invalid WebSocket URI: {uri}")
    except ConnectionRefusedError:
        logging.error(f"Connection refused by the server at {uri}. Is the server running?")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

async def main():
    server_uri = "ws://localhost:8765"
    await send_and_receive_messages(server_uri)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("WebSocket client shutting down.") 