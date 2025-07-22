import asyncio
from typing import cast
from aioquic.asyncio import QuicConnectionProtocol, connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived, ConnectionTerminated

SERVER_ADDRESS = "localhost"
SERVER_PORT = 4433
# Path to the server's certificate for verification (since it's self-signed)
SERVER_CERTIFICATE_FILE = "certs/cert.pem"

class EchoClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_to_send = b"Hello, QUIC World from Python!"
        self._data_received_event = asyncio.Event()
        self._received_data = b""

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, StreamDataReceived):
            self._received_data += event.data
            print(f"Client received on stream {event.stream_id}: {event.data.decode()}")
            if event.end_stream:
                self._data_received_event.set() # Signal that all data for this message is received
                print(f"Client received end of stream {event.stream_id}")
        elif isinstance(event, ConnectionTerminated):
            print(f"Client connection terminated. Error: {event.error_code}, Reason: {event.reason_phrase}")
            self._data_received_event.set() # Ensure we don't hang if connection closes prematurely


    async def send_and_receive(self):
        stream_id = self._quic.get_next_available_stream_id()
        print(f"Client sending on stream {stream_id}: {self._data_to_send.decode()}")
        self._quic.send_stream_data(stream_id, self._data_to_send, end_stream=True)

        # Wait for the response
        try:
            await asyncio.wait_for(self._data_received_event.wait(), timeout=5.0)
            if self._data_to_send == self._received_data:
                print(f"Client SUCCESS: Sent and received data match!")
            else:
                print(f"Client FAILURE: Data mismatch.")
                print(f"  Sent: {self._data_to_send.decode()}")
                print(f"  Received: {self._received_data.decode()}")
        except asyncio.TimeoutError:
            print("Client TIMEOUT: Did not receive echoed data in time.")

        # Close the connection
        self.close()
        await self.wait_closed()
        print("Client connection closed.")


async def run_client(host: str, port: int, configuration: QuicConfiguration) -> None:
    print(f"Connecting to QUIC server at {host}:{port}...")
    async with connect(
        host,
        port,
        configuration=configuration,
        create_protocol=EchoClientProtocol,
    ) as protocol:
        protocol = cast(EchoClientProtocol, protocol)
        await protocol.send_and_receive()

if __name__ == "__main__":
    client_config = QuicConfiguration(
        is_client=True,
        alpn_protocols=None # No ALPN needed for simple echo
    )
    # For self-signed certificates, the client needs to trust the server's CA
    # or the specific certificate. aioquic by default tries to verify against
    # system CAs. For local testing with a self-signed cert, we load it.
    try:
        client_config.load_verify_locations(cafile=SERVER_CERTIFICATE_FILE)
    except FileNotFoundError:
        print(f"Error: Server certificate file '{SERVER_CERTIFICATE_FILE}' not found for client verification.")
        print("Ensure the server is running and the certificate was generated to 'certs/cert.pem'.")
        exit(1)
    except Exception as e:
        print(f"Error loading server certificate for client: {e}")
        exit(1)


    try:
        asyncio.run(run_client(SERVER_ADDRESS, SERVER_PORT, client_config))
    except ConnectionRefusedError:
        print(f"Client Error: Connection refused. Is the server running at {SERVER_ADDRESS}:{SERVER_PORT}?")
    except Exception as e:
        print(f"Client Error: An unexpected error occurred: {e}")