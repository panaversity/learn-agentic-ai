import asyncio
import logging
import os
from typing import Optional, cast
from urllib.parse import urlparse

from aioquic.asyncio import QuicConnectionProtocol, connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived, DatagramFrameReceived, ConnectionTerminated, HandshakeCompleted
from aioquic.quic.logger import QuicLogger
from aioquic.h3.connection import H3_ALPN
from aioquic.h3.events import H3Event # For type hinting if deeper H3 handling was needed
from aioquic.webtransport import WebTransportSession, SessionID

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebTransport_CLIENT - %(levelname)s - %(message)s')

# Path to the server's self-signed certificate for verification (optional but recommended for local dev)
# If this is not provided, client will need to run with `insecure=True` in QuicConfiguration.
SERVER_CERTIFICATE_FILE = "ssl_cert.pem" # Assumes server generated this in the same directory

class WebTransportEchoClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session_id: Optional[SessionID] = None
        self._webtransport: Optional[WebTransportSession] = None
        self._acknowledged_webtransport_support = False
        self.handshake_event = asyncio.Event()
        self.webtransport_ready_event = asyncio.Event()
        self.received_stream_data = []
        self.received_datagram_data = []

    async def wait_handshake_completion(self):
        await self.handshake_event.wait()
    
    async def wait_webtransport_ready(self):
        await self.webtransport_ready_event.wait()

    def quic_event_received(self, event: QuicEvent) -> None:
        # logging.debug(f"QUIC Event: {event}")
        if isinstance(event, HandshakeCompleted):
            logging.info("QUIC handshake completed.")
            if event.alpn_protocol == H3_ALPN[0]: # Check if H3 was negotiated
                self._acknowledged_webtransport_support = True
                logging.info("HTTP/3 ALPN negotiated. WebTransport should be supported.")
            else:
                logging.warning(f"HTTP/3 ALPN not negotiated (got {event.alpn_protocol}). WebTransport may not work.")
            self.handshake_event.set()

        elif isinstance(event, ConnectionTerminated):
            logging.info(f"Connection terminated. Reason: {event.reason_phrase}")
            self.webtransport_ready_event.set() # Unblock if waiting

        if self._webtransport:
            self._webtransport.handle_event(event)
            if isinstance(event, WebTransportStreamDataReceived):
                data_str = event.data.decode('utf-8')
                logging.info(f"WT Client: Received on stream {event.stream_id} (session {event.session_id}): {data_str}")
                self.received_stream_data.append(data_str)
            
            if isinstance(event, DatagramFrameReceived):
                # This is a raw datagram, WebTransportSession handles decryption if it's a WT datagram
                # For this client, we assume handle_event in WebTransportSession will trigger its own datagram_received.
                pass 

    # Method to be called by WebTransportSession when it receives a datagram
    def datagram_received(self, data: bytes, session_id: SessionID) -> None:
        data_str = data.decode("utf-8")
        logging.info(f"WT Client: Received datagram (session {session_id}): {data_str}")
        self.received_datagram_data.append(data_str)

    async def establish_webtransport_session(self, url: str):
        await self.wait_handshake_completion()
        if not self._acknowledged_webtransport_support:
            logging.error("Cannot establish WebTransport session: HTTP/3 not confirmed.")
            return False

        logging.info(f"Attempting to establish WebTransport session with {url}")
        self._webtransport = WebTransportSession(
            connection=self._quic,
            protocol=self # The QuicConnectionProtocol itself to handle callbacks
        )
        self._session_id = self._webtransport.connect(authority=urlparse(url).netloc, path=urlparse(url).path)
        if self._session_id is not None:
            logging.info(f"WebTransport session negotiation started (H3 Stream ID: {self._session_id}). Waiting for server 200 OK...")
            # In aioquic, the session is considered ready after the CONNECT request is made.
            # The actual confirmation comes when the server responds with 200 OK on that H3 stream.
            # We'll use an event that the H3 layer (if we were parsing it here) or app logic would set.
            # For this demo, we assume it will be ready shortly if connect() succeeds.
            self.webtransport_ready_event.set()
            return True
        else:
            logging.error("Failed to initiate WebTransport connection (connect returned None).")
            return False

    async def send_webtransport_stream_data(self, data: str, end_stream: bool = False):
        if self._webtransport and self._webtransport.can_create_stream() and self.webtransport_ready_event.is_set():
            stream_id = self._webtransport.create_stream(is_unidirectional=False) # Create a bidi stream
            if stream_id is not None:
                logging.info(f"WT Client: Sending on new stream {stream_id}: {data}")
                self._webtransport.send_stream_data(stream_id, data.encode("utf-8"), end_stream=end_stream)
                return stream_id
            else:
                logging.warning("WT Client: Could not create new stream.")
        else:
            logging.warning("WT Client: WebTransport session not ready or cannot create stream.")
        return None

    async def send_webtransport_datagram(self, data: str):
        if self._webtransport and self.webtransport_ready_event.is_set():
            logging.info(f"WT Client: Sending datagram: {data}")
            self._webtransport.send_datagram(data.encode("utf-8"))
        else:
            logging.warning("WT Client: WebTransport session not ready to send datagram.")

async def main_client():
    # The URL for the WebTransport endpoint
    # Note: Browsers typically require `https://` and a specific path.
    # aioquic examples often use the authority and path from the URL in `_webtransport.connect()`
    url = "https://localhost:4433/webtransport_echo" # Path must be handled by server
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or 4433

    # QUIC configuration
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=H3_ALPN, # Important for WebTransport
        quic_logger=QuicLogger() if os.environ.get("AIOQUIC_LOG_LEVEL") else None,
        # To trust the server's self-signed certificate:
        # You can load the CA cert if it's different from the server cert itself,
        # or for a self-signed server cert, you might need to add it to a trust store
        # or run in `insecure=True` mode for local testing (NOT FOR PRODUCTION).
        # cafile=SERVER_CERTIFICATE_FILE, # if server cert is its own CA for self-signed
    )
    # For local testing with self-signed cert, often easier to bypass verification:
    configuration.verify_mode = ssl.CERT_NONE # Insecure, for local demo only!
    # Or load the specific self-signed cert if you have it as a CA
    # if os.path.exists(SERVER_CERTIFICATE_FILE):
    #     configuration.load_verify_locations(cafile=SERVER_CERTIFICATE_FILE)
    # else:
    #     logging.warning(f"Server certificate {SERVER_CERTIFICATE_FILE} not found. Client may fail TLS if verify_mode is not CERT_NONE.")

    logging.info(f"Attempting to connect to WebTransport server at {host}:{port} for URL {url}")
    logging.info("If using self-signed certs, ensure client is configured to trust it or ignore TLS errors.")

    try:
        async with connect(
            host,
            port,
            configuration=configuration,
            create_protocol=WebTransportEchoClientProtocol,
            # session_ticket_handler=lambda ticket: None, # To handle session resumption tickets
        ) as client_protocol:
            client_protocol = cast(WebTransportEchoClientProtocol, client_protocol) # For type hinting
            
            if not await client_protocol.establish_webtransport_session(url):
                logging.error("Failed to establish WebTransport session with server.")
                return

            await client_protocol.wait_webtransport_ready()
            logging.info("WebTransport session should be ready.")

            # Test sending data on a stream
            stream_msg1 = "Hello via WebTransport Stream!"
            sent_stream_id = await client_protocol.send_webtransport_stream_data(stream_msg1)
            
            await asyncio.sleep(1) # Give time for echo

            # Test sending a datagram
            datagram_msg1 = "Hello via WebTransport Datagram!"
            await client_protocol.send_webtransport_datagram(datagram_msg1)

            # Wait for a few seconds to receive echoes
            logging.info("Waiting for 5 seconds to receive echoes...")
            await asyncio.sleep(5)

            logging.info(f"Received stream messages: {client_protocol.received_stream_data}")
            logging.info(f"Received datagram messages: {client_protocol.received_datagram_data}")

            logging.info("Client operations complete.")

    except ConnectionRefusedError:
        logging.error(f"Connection refused by server at {host}:{port}. Is it running?")
    except asyncio.TimeoutError:
        logging.error("Connection or operation timed out.")
    except Exception as e:
        logging.error(f"Client main error: {e}", exc_info=True)
    finally:
        logging.info("Client shutting down.")

if __name__ == "__main__":
    # Note: Running this client requires aioquic, cryptography, and the server to be running.
    # The server (webtransport_server.py) should generate ssl_cert.pem.
    # This client is set to insecurely skip TLS verification for local demo with self-signed certs.
    import ssl # For ssl.CERT_NONE, should be at top ideally
    asyncio.run(main_client()) 