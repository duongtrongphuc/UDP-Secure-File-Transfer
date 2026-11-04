
import socket
import json
import hashlib
from pathlib import Path

from file_transfer.packet import split_data
from security.encryption import encrypt_data

SERVER_ADDRESS = ("127.0.0.1", 5001)
TIMEOUT = 2
MAX_RETRIES = 5
CHUNK_SIZE = 1024


def send_json(sock, message):
    sock.sendto(
        json.dumps(message).encode("utf-8"),
        SERVER_ADDRESS
    )


def receive_json(sock):
    packet, _ = sock.recvfrom(2048)
    return json.loads(packet.decode("utf-8"))


def main():
    file_path = Path("sample.txt")

    if not file_path.is_file():
        print("ERROR: sample.txt not found!")
        return

    original_data = file_path.read_bytes()

    file_hash = hashlib.sha256(original_data).hexdigest()

    encrypted_data = encrypt_data(original_data)

    print("AES-256-GCM encryption: SUCCESS")
    print(f"Original size: {len(original_data)} bytes")
    print(f"Encrypted size: {len(encrypted_data)} bytes")

    filename, total_chunks, chunks = split_data(
        encrypted_data,
        file_path.name,
        CHUNK_SIZE
    )

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT)

    print("Connecting to UDP File Server...")

    start_message = {
        "type": "START",
        "filename": filename,
        "total_chunks": total_chunks,
        "sha256": file_hash
    }

    send_json(client, start_message)

    for attempt in range(MAX_RETRIES):
        try:
            response = receive_json(client)

            if response.get("type") == "READY":
                break

        except socket.timeout:
            send_json(client, start_message)

    else:
        print("ERROR: Server did not respond.")
        client.close()
        return

    print("Server is ready. Sending encrypted file...")

    for sequence_number, payload in chunks:

        packet = (
            json.dumps({
                "type": "CHUNK",
                "seq": sequence_number
            }).encode("utf-8")
            + b"\n"
            + payload
        )

        acknowledged = False

        for attempt in range(MAX_RETRIES):
            client.sendto(packet, SERVER_ADDRESS)

            try:
                response = receive_json(client)

                if (
                    response.get("type") == "ACK"
                    and response.get("seq") == sequence_number
                ):
                    acknowledged = True

                    print(
                        f"ACK received for chunk "
                        f"{sequence_number + 1}/{total_chunks}"
                    )
                    break

            except socket.timeout:
                print(
                    f"Timeout! Retrying chunk "
                    f"{sequence_number + 1} "
                    f"(attempt {attempt + 1})"
                )

        if not acknowledged:
            print("ERROR: Failed to send chunk.")
            client.close()
            return

    for attempt in range(MAX_RETRIES):
        send_json(client, {"type": "END"})

        try:
            response = receive_json(client)

            if response.get("type") == "DONE":
                print("\nSUCCESS: File transferred successfully!")
                print("AES-256-GCM encryption/decryption: SUCCESS")
                print("SHA-256 integrity verification: SUCCESS")
                break

            if response.get("type") == "ERROR":
                print("Server error:", response.get("message"))
                break

        except socket.timeout:
            print("Waiting for server confirmation...")

        except ConnectionResetError:
            print("Connection reset by server.")
            break

    else:
        print("ERROR: Server did not confirm file transfer.")

    client.close()


if __name__ == "__main__":
    main()
