import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

message = "Hello Server!"
client.sendto(
    message.encode("utf-8"),
    (SERVER_IP,SERVER_PORT)
)
print("Message sent to server!")

data, server_addresss = client.recvfrom(1024)
response = data.decode("utf-8")
print(f"Server response:{response}")

client.close()