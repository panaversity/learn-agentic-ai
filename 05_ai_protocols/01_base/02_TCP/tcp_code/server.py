import socket

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024) # Receive data from the client
            if not data: # If recv returns 0 bytes, the client has closed the connection
                break
            print(f"Received: {data.decode()}")
            conn.sendall(data)  # Echo back the received data to the client