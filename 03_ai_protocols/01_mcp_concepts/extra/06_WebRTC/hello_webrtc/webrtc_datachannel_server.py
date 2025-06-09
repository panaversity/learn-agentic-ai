import asyncio
import logging
import socket
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling, object_from_string, object_to_string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebRTC_SERVER - %(levelname)s - %(message)s')

async def run_server(pc, reader, writer):
    """Handles the WebRTC connection and data channel for the server side."""
    # Create signaling instance for this connection
    signaling = TcpSocketSignaling(None, None)
    signaling._reader = reader
    signaling._writer = writer

    @pc.on("datachannel")
    def on_datachannel(channel):
        logging.info(f"Data channel '{channel.label}' created by client.")

        @channel.on("open")
        def on_open():
            logging.info(f"Data channel '{channel.label}' opened.")
            # channel.send(f"Server says: Welcome to the data channel '{channel.label}'!")

        @channel.on("message")
        def on_message(message):
            logging.info(f"Received message on '{channel.label}': {message}")
            response = f"Server echoes: {message}"
            logging.info(f"Sending response on '{channel.label}': {response}")
            channel.send(response)

        @channel.on("close")
        def on_close():
            logging.info(f"Data channel '{channel.label}' closed.")

    # Consume signaling messages
    try:
        while True:
            obj = await signaling.receive()

            if isinstance(obj, RTCSessionDescription):
                logging.info("Received session description from client.")
                await pc.setRemoteDescription(obj)

                if obj.type == "offer":
                    logging.info("Creating answer...")
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    logging.info("Sending answer to client.")
                    await signaling.send(pc.localDescription)
            elif isinstance(obj, str) and obj == "bye":
                logging.info("Client said bye, closing connection.")
                break
            else:
                logging.warning(f"Received unexpected object: {obj}")

    except asyncio.CancelledError:
        logging.info("Run_server task cancelled.")
    except Exception as e:
        logging.error(f"Error in server run loop: {e}", exc_info=True)
    finally:
        logging.info("Closing the peer connection.")
        await pc.close()
        logging.info("Closing the signaling channel.")
        writer.close()
        await writer.wait_closed()

async def listen_for_connections(host, port):
    """Sets up a TCP server to listen for signaling connections."""
    server = await asyncio.start_server(
        handle_client, host, port
    )

    addr = server.sockets[0].getsockname()
    logging.info(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

async def handle_client(reader, writer):
    """Handles a new client connection."""
    addr = writer.get_extra_info('peername')
    logging.info(f"New client connection from {addr}")
    
    # Create a new peer connection for this client
    pc = RTCPeerConnection()
    
    try:
        await run_server(pc, reader, writer)
    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}", exc_info=True)
    finally:
        if not pc.signalingState == "closed":
            await pc.close()
        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()
        logging.info(f"Connection closed with {addr}")

async def main():
    SIGNALING_HOST = "127.0.0.1"
    SIGNALING_PORT = 12345 # Changed port to avoid conflict with other examples

    logging.info(f"Starting WebRTC server with TCP signaling on {SIGNALING_HOST}:{SIGNALING_PORT}")
    logging.info("Waiting for client connections...")

    try:
        await listen_for_connections(SIGNALING_HOST, SIGNALING_PORT)
    except KeyboardInterrupt:
        logging.info("Server shutting down due to KeyboardInterrupt.")
    except Exception as e:
        logging.error(f"Server main loop encountered an error: {e}", exc_info=True)
    finally:
        logging.info("Server shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())