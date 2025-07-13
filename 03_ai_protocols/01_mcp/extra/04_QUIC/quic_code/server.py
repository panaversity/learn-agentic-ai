import asyncio
from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived

SERVER_ADDRESS = "localhost"
SERVER_PORT = 4433
CERTIFICATE_FILE = "certs/cert.pem"
PRIVATE_KEY_FILE = "certs/key.pem"

class EchoServerProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, StreamDataReceived):
            print(f"Server received on stream {event.stream_id}: {event.data.decode()}")
            # Echo the data back on the same stream
            self._quic.send_stream_data(event.stream_id, event.data, end_stream=event.end_stream)
            if event.end_stream:
                print(f"Server echoed and closed stream {event.stream_id}")

async def run_server(host: str, port: int, configuration: QuicConfiguration) -> None:
    print(f"Starting QUIC server on {host}:{port}...")
    await serve(
        host,
        port,
        configuration=configuration,
        create_protocol=EchoServerProtocol,
        session_ticket_fetcher=lambda *args, **kwargs: None, # Simplified for echo
        session_ticket_handler=lambda *args, **kwargs: None, # Simplified for echo
    )
    print(f"QUIC server listening on {host}:{port}")
    try:
        await asyncio.Event().wait() # Keep server running indefinitely
    except KeyboardInterrupt:
        print("Server shutting down...")

if __name__ == "__main__":
    config = QuicConfiguration(
        is_client=False,
        alpn_protocols=None # No ALPN needed for simple echo
    )
    config.load_cert_chain(CERTIFICATE_FILE, PRIVATE_KEY_FILE)

    try:
        asyncio.run(run_server(SERVER_ADDRESS, SERVER_PORT, config))
    except KeyboardInterrupt:
        print("Server process terminated.")
    except FileNotFoundError:
        print(f"Error: Certificate or key file not found. Ensure '{CERTIFICATE_FILE}' and '{PRIVATE_KEY_FILE}' exist.")
        print("You can generate them using the openssl command provided in the readme.")