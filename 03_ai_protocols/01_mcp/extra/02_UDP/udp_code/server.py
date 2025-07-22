import socket

HOST = '127.0.0.1'  # Localhost
PORT = 65433        # Port to listen on

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"UDP server listening on {HOST}:{PORT}")
    while True:
        data, addr = s.recvfrom(1024) # Buffer size is 1024 bytes; returns (bytes, address)
        print(f"Received from {addr}: {data.decode()}")
        s.sendto(data, addr)  # Echo back to the sender's address