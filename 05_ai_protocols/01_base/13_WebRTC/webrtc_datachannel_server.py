import asyncio
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling, object_from_string, object_to_string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebRTC_SERVER - %(levelname)s - %(message)s')

async def run_server(pc, signaling):
    """Handles the WebRTC connection and data channel for the server side."""
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
        await signaling.close()

async def main():
    SIGNALING_HOST = "127.0.0.1"
    SIGNALING_PORT = 12345 # Changed port to avoid conflict with other examples

    signaling = TcpSocketSignaling(SIGNALING_HOST, SIGNALING_PORT)
    pc = RTCPeerConnection()

    logging.info(f"Starting WebRTC server with TCP signaling on {SIGNALING_HOST}:{SIGNALING_PORT}")
    logging.info("Waiting for client connection...")

    # Connect signaling channel
    await signaling.connect() 
    # Note: For TcpSocketSignaling, connect() on server side means starting to listen.

    try:
        await run_server(pc, signaling)
    except KeyboardInterrupt:
        logging.info("Server shutting down due to KeyboardInterrupt.")
    except Exception as e:
        logging.error(f"Server main loop encountered an error: {e}", exc_info=True)
    finally:
        if not pc.signalingState == "closed":
            await pc.close()
        if signaling._reader is not None or signaling._writer is not None: # Check if signaling is open
             await signaling.close()
        logging.info("Server shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main()) 