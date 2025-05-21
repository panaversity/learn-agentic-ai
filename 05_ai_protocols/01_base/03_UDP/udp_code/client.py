import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65433        # The port used by the server
MESSAGE = b"Hello, UDP server!"

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(MESSAGE, (HOST, PORT)) # Specify server address and port
    data, server_addr = s.recvfrom(1024) # Returns (bytes, address)

print(f"Received from server {server_addr}: {data.decode()}")