import socket
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

server.bind((SERVER_IP,SERVER_PORT))
print("UDP Server is running...")
print(f"Listening on {SERVER_IP}:{SERVER_PORT}")


while True:
    data, client_address = server.recvfrom(1024)
    message = data.decode("utf-8")
    print(f"Received from{client_address} : {message}")

    response = "Message received successfully!"

    server.sendto(
    response.encode("utf-8"),
    client_address
)   