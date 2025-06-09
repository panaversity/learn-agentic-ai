import asyncio
import logging
import os
from typing import Dict, Optional, cast

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec #, rsa (can also use rsa)

from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import (QuicEvent, StreamDataReceived, WebTransportStreamDataReceived, DatagramFrameReceived, ConnectionTerminated)
from aioquic.quic.logger import QuicLogger
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import H3Event, HeadersReceived, DataReceived, ConnectionShutdownInitiated, StreamReset
from aioquic.webtransport import WebTransportSession

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WebTransport_SERVER - %(levelname)s - %(message)s')

SERVER_CERTIFICATE_FILE = "ssl_cert.pem" # Generated certificate
SERVER_PRIVATE_KEY_FILE = "ssl_key.pem"  # Generated private key

# --- Helper to generate self-signed cert if not present (for demo purposes) ---
def generate_self_signed_cert(cert_path, key_path, common_name="localhost"):
    if os.path.exists(cert_path) and os.path.exists(key_path):
        logging.info(f"Using existing certificate '{cert_path}' and key '{key_path}'.")
        return

    logging.info(f"Generating self-signed certificate for {common_name}...")
    # private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_key = ec.generate_private_key(ec.SECP256R1())

    subject = issuer = x509.Name([
        x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, common_name)
    ])

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(x509.datetime.datetime.now(x509.datetime.timezone.utc))
        .not_valid_after(x509.datetime.datetime.now(x509.datetime.timezone.utc) + x509.datetime.timedelta(days=30))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    )
    # For WebTransport/HTTP3, Subject Alternative Name (SAN) is important.
    # Typically for localhost, you might use DNS:localhost or an IP address.
    builder = builder.add_extension(
        x509.SubjectAlternativeName([x509.DNSName(common_name)]),
        critical=False,
    )
    certificate = builder.sign(private_key, hashes.SHA256())

    with open(key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
        logging.info(f"Private key saved to {key_path}")
    with open(cert_path, "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))
        logging.info(f"Certificate saved to {cert_path}")


class WebTransportEchoServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http: Optional[H3Connection] = None
        self._webtransport_sessions: Dict[int, WebTransportSession] = {}

    def quic_event_received(self, event: QuicEvent) -> None:
        # logging.debug(f"QUIC Event: {event}")
        if isinstance(event, ConnectionTerminated):
            logging.info(f"Connection terminated from {self._quic.remote_address}. Reason: {event.reason_phrase}")

        if self._http is None and self._quic.configuration.alpn_protocols[0] == H3_ALPN[0]:
            # Initialize H3 connection upon QUIC connection establishment
            self._http = H3Connection(self._quic, enable_webtransport=True)

        if self._http is not None:
            # Pass QUIC events to the H3 connection
            for h3_event in self._http.handle_event(event):
                self._h3_event_received(h3_event)
        
        # WebTransport specific stream data (outside H3 framing, for accepted WebTransport sessions)
        if isinstance(event, WebTransportStreamDataReceived):
            session = self._webtransport_sessions.get(event.session_id)
            if session:
                message = event.data.decode("utf-8")
                logging.info(f"WT Session {event.session_id} - Stream {event.stream_id} - Received data: {message}")
                response = f"Server echoes (WT Stream {event.stream_id}): {message}"
                session.send_stream_data(event.stream_id, response.encode("utf-8"), end_stream=False)
                # session.send_stream_data(event.stream_id, b"", end_stream=True) # If you want to close stream after echo
            else:
                logging.warning(f"Received WT data for unknown session ID: {event.session_id}")

        if isinstance(event, DatagramFrameReceived):
            session_id = self._quic.get_session_id_for_datagram(event.data)
            if session_id is not None and session_id in self._webtransport_sessions:
                payload = self._quic.decrypt_datagram_payload(event.data, session_id)
                logging.info(f"WT Session {session_id} - Received datagram: {payload.decode()}")
                response_datagram = f"Server echoes (Datagram): {payload.decode()}".encode("utf-8")
                self._webtransport_sessions[session_id].send_datagram(response_datagram)
            else:
                logging.info(f"Received datagram (可能是H3): {event.data.hex()}")


    def _h3_event_received(self, event: H3Event) -> None:
        # logging.debug(f"H3 Event: {event}")
        if isinstance(event, HeadersReceived):
            headers = dict(event.headers)
            method = headers.get(b":method", b"").decode()
            path = headers.get(b":path", b"").decode()
            logging.info(f"H3 Request: Stream {event.stream_id} - Method {method}, Path {path}")

            if method == "CONNECT" and headers.get(b":protocol") == b"webtransport":
                # This is a WebTransport session negotiation request
                logging.info(f"WebTransport session negotiation request on stream {event.stream_id}")
                session = WebTransportSession(self._http, event.stream_id, self._quic.configuration)
                self._webtransport_sessions[session.session_id] = session # Store the session
                logging.info(f"WebTransport session {session.session_id} established for H3 stream {event.stream_id}")
                # Server accepts the WebTransport session by sending HTTP 200
                self._http.send_headers(event.stream_id, [(b":status", b"200")])
                # The client will now be able to open streams and send datagrams for this session.
            else:
                # Handle other H3 requests (e.g., GET for a simple webpage)
                if method == "GET" and path == "/":
                    body = b"<html><body><h1>Hello from aioquic WebTransport/H3 server!</h1></body></html>"
                    self._http.send_headers(event.stream_id, [(b":status", b"200"), (b"content-type", b"text/html")],)
                    self._http.send_data(event.stream_id, body, end_stream=True)
                else:
                    # Generic 404 for other paths/methods
                    self._http.send_headers(event.stream_id, [(b":status", b"404")])
                    self._http.send_data(event.stream_id, b"Not Found", end_stream=True)
        
        elif isinstance(event, DataReceived):
            logging.info(f"H3 Data on stream {event.stream_id}: {event.data.decode() if event.data else ''} (End: {event.stream_ended})")
            # For regular H3 streams (not WebTransport session stream itself)
            if event.stream_ended:
                # Example: Echo back data on a regular H3 POST stream (not WebTransport)
                # headers = dict(self._http.get_headers(event.stream_id))
                # if headers.get(b':method') == b'POST':
                #     self._http.send_headers(event.stream_id, [(b':status', b'200')])
                #     self._http.send_data(event.stream_id, event.data, end_stream=True)
                pass # No specific action here for this demo for generic H3 data

        elif isinstance(event, ConnectionShutdownInitiated):
            logging.info("H3 Connection shutdown initiated by client.")
            # self.close() # This would close the QUIC connection

        elif isinstance(event, StreamReset):
            logging.info(f"H3 Stream {event.stream_id} was reset. Error code: {event.error_code}")

async def main_server():
    generate_self_signed_cert(SERVER_CERTIFICATE_FILE, SERVER_PRIVATE_KEY_FILE)

    configuration = QuicConfiguration(
        alpn_protocols=H3_ALPN, # Specify ALPN for HTTP/3
        is_client=False,
        max_datagram_frame_size=65536, # Enable datagrams
        quic_logger=QuicLogger() if os.environ.get("AIOQUIC_LOG_LEVEL") else None
    )
    configuration.load_cert_chain(SERVER_CERTIFICATE_FILE, SERVER_PRIVATE_KEY_FILE)

    host = "0.0.0.0"
    port = 4433

    logging.info(f"Starting WebTransport/HTTP3 server on https://{host}:{port}")
    logging.info("Make sure your client trusts the self-signed certificate or is configured to ignore errors for localhost.")
    logging.info("AIOQUIC_LOG_LEVEL=info can be set for detailed QUIC logs (qlog format).")

    try:
        await serve(
            host,
            port,
            configuration=configuration,
            create_protocol=WebTransportEchoServerProtocol,
            # Example for session_ticket_fetcher and session_ticket_handler if needed:
            # session_ticket_fetcher=lambda: None, # Implement if client sends session tickets
            # session_ticket_handler=lambda ticket: None, # Implement to store session tickets
        )
        await asyncio.Future() # Run forever
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
    except Exception as e:
        logging.error(f"Server main error: {e}", exc_info=True)

if __name__ == "__main__":
    # Note: Running this server requires aioquic and cryptography.
    # pip install aioquic cryptography
    # The server will generate self-signed certificates (ssl_cert.pem, ssl_key.pem) on first run.
    # Clients (browsers or Python client) need to be configured to trust this cert or ignore errors for localhost.
    asyncio.run(main_server()) 