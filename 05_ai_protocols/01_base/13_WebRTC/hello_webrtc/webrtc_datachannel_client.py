import asyncio
import logging
import json
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import object_from_string, object_to_string

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebRTC_CLIENT - %(levelname)s - %(message)s')

async def run_client(pc, reader, writer, data_channel_label="chat"):
    """Handles the WebRTC connection and data channel for the client side."""

    @pc.on("track")
    def on_track(track):
        logging.info(f"Track {track.kind} received")
        # We are not handling media tracks in this data-channel only example
        # If you were, you might do: recorder.addTrack(track)
        @track.on("ended")
        async def on_ended():
            logging.info(f"Track {track.kind} ended")

    # Create data channel
    try:
        channel = pc.createDataChannel(data_channel_label)
        logging.info(f"Data channel '{channel.label}' created.")
    except Exception as e:
        logging.error(f"Failed to create data channel: {e}", exc_info=True)
        return

    @channel.on("open")
    async def on_open():
        logging.info(f"Data channel '{channel.label}' opened. Sending messages...")
        messages = ["Hello WebRTC Server!", "This is a data channel test.", "How are you?"]
        for i, msg in enumerate(messages):
            full_msg = f"{msg} (msg_{i+1})"
            logging.info(f"Sending: {full_msg}")
            channel.send(full_msg)
            await asyncio.sleep(1) # Small delay between sends
        # After sending all messages, could send a "bye" or just close
        # channel.send("Client says: bye!")
        # await asyncio.sleep(1) # ensure it's sent before closing pc

    @channel.on("message")
    def on_message(message):
        logging.info(f"Received on '{channel.label}': {message}")
        # You might want to stop or do something else after receiving certain messages
        # For this demo, we'll let the server echo and client eventually times out or is stopped manually

    @channel.on("close")
    def on_close():
        logging.info(f"Data channel '{channel.label}' closed.")

    # Send offer
    try:
        logging.info("Creating offer...")
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        logging.info("Sending offer to server.")
        
        # Send the offer to the server
        writer.write(object_to_string(pc.localDescription).encode() + b'\n')
        await writer.drain()
    except Exception as e:
        logging.error(f"Error creating/sending offer: {e}", exc_info=True)
        writer.close()
        return

    # Consume signaling messages
    try:
        while True:
            # Read response from server
            data = await reader.readline()
            if not data:  # Connection closed
                logging.info("Signaling channel closed by server or network issue.")
                break
                
            # Parse the response
            obj = object_from_string(data.decode())

            if isinstance(obj, RTCSessionDescription):
                logging.info("Received session description from server.")
                await pc.setRemoteDescription(obj)
                if obj.type == "answer":
                    logging.info("Received answer. Peer connection established.")
                    # Connection is now set up, data channel should open soon if not already.
            else:
                logging.warning(f"Received unexpected object: {obj}")

        # Keep client alive for a bit to allow data channel messages to flow
        # In a real app, this would be event-driven or user-controlled.
        logging.info("Client will stay active for 10 seconds to exchange data channel messages.")
        await asyncio.sleep(10)
        logging.info("Client demo period over.")

    except asyncio.CancelledError:
        logging.info("Run_client task cancelled.")
    except Exception as e:
        logging.error(f"Error in client run loop: {e}", exc_info=True)
    finally:
        logging.info("Closing the peer connection.")
        await pc.close()
        logging.info("Closing the connection.")
        writer.close()
        await writer.wait_closed()

async def main():
    SIGNALING_HOST = "127.0.0.1"
    SIGNALING_PORT = 12345 # Must match the server's port

    logging.info(f"Starting WebRTC client, trying to connect to signaling server at {SIGNALING_HOST}:{SIGNALING_PORT}")

    pc = RTCPeerConnection()
    
    try:
        # Directly connect to the server
        reader, writer = await asyncio.open_connection(SIGNALING_HOST, SIGNALING_PORT)
        logging.info("Signaling connected.")
        
        await run_client(pc, reader, writer)
    except KeyboardInterrupt:
        logging.info("Client shutting down due to KeyboardInterrupt.")
    except ConnectionRefusedError:
        logging.error(f"Signaling connection refused at {SIGNALING_HOST}:{SIGNALING_PORT}. Is the server running?")
    except Exception as e:
        logging.error(f"Client main loop encountered an error: {e}", exc_info=True)
    finally:
        if not pc.signalingState == "closed":
            await pc.close()
        logging.info("Client shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())