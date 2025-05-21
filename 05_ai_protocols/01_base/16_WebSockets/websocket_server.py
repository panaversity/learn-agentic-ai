import asyncio
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SERVER - %(levelname)s - %(message)s')

connections = set()

async def handler(websocket, path):
    """
    Handles incoming WebSocket connections, registers them,
    echoes messages, and unregisters on disconnection.
    """
    connections.add(websocket)
    logging.info(f"Client connected from {websocket.remote_address}. Path: {path}. Total connections: {len(connections)}")
    try:
        async for message in websocket:
            logging.info(f"Received message from {websocket.remote_address}: {message}")
            # Echo the message back to the sender
            await websocket.send(f"Server echoes: {message}")
            logging.info(f"Echoed message to {websocket.remote_address}: {message}")

            # Example of broadcasting to all other clients (except sender)
            # for conn in connections:
            #     if conn != websocket:
            #         await conn.send(f"Broadcast from {websocket.remote_address}: {message}")
    except websockets.exceptions.ConnectionClosedOK:
        logging.info(f"Client {websocket.remote_address} disconnected gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.info(f"Client {websocket.remote_address} connection closed with error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred with client {websocket.remote_address}: {e}")
    finally:
        connections.remove(websocket)
        logging.info(f"Client {websocket.remote_address} removed. Total connections: {len(connections)}")

async def main():
    # Start the WebSocket server
    logging.info("Starting WebSocket server on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("WebSocket server shutting down.") 