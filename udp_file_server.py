
import socket
import json
import hashlib
from pathlib import Path

from security.encryption import decrypt_data
from cryptography.exceptions import InvalidTag

HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 2048

OUTPUT_DIR = Path("received_files")
OUTPUT_DIR.mkdir(exist_ok=True)


def send_json(sock, address, message):
    sock.sendto(
        json.dumps(message).encode("utf-8"),
        address
    )


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))

    print(f"UDP File Server listening on {HOST}:{PORT}")

    client_address = None
    filename = None
    total_chunks = 0
    expected_hash = None
    received_chunks = {}

    while True:
        packet, address = server.recvfrom(BUFFER_SIZE)

        if client_address is not None and address != client_address:
            continue

        header_data, separator, payload = packet.partition(b"\n")

        # Handle JSON control messages.
        if not separator:
            try:
                message = json.loads(packet.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue

            if message.get("type") == "START":
                client_address = address
                filename = Path(message["filename"]).name
                total_chunks = message["total_chunks"]
                expected_hash = message["sha256"]
                received_chunks = {}

                print(f"\nReceiving encrypted file: {filename}")
                print(f"Total chunks: {total_chunks}")

                send_json(server, address, {"type": "READY"})

            elif message.get("type") == "END":

                # Check whether all chunks have arrived.
                if len(received_chunks) != total_chunks:
                    send_json(server, address, {
                        "type": "ERROR",
                        "message": "Missing chunks"
                    })
                    continue

                # Reassemble encrypted data in sequence order.
                encrypted_data = b"".join(
                    received_chunks[i]
                    for i in range(total_chunks)
                )

                print("All encrypted chunks received.")

                # Decrypt using AES-256-GCM.
                try:
                    file_data = decrypt_data(encrypted_data)

                except InvalidTag:
                    send_json(server, address, {
                        "type": "ERROR",
                        "message": "AES-GCM authentication failed"
                    })
                    print("ERROR: AES-GCM authentication failed.")
                    continue

                except (ValueError, FileNotFoundError) as error:
                    send_json(server, address, {
                        "type": "ERROR",
                        "message": str(error)
                    })
                    print("Decryption error:", error)
                    continue

                print("AES-256-GCM decryption: SUCCESS")

                # Verify SHA-256 of the original plaintext.
                actual_hash = hashlib.sha256(file_data).hexdigest()

                if actual_hash != expected_hash:
                    send_json(server, address, {
                        "type": "ERROR",
                        "message": "SHA-256 mismatch"
                    })
                    print("ERROR: SHA-256 verification failed.")
                    continue

                # Save the decrypted original file.
                output_path = OUTPUT_DIR / filename
                output_path.write_bytes(file_data)

                print(f"Saved original file: {output_path}")
                print("SHA-256 verification: SUCCESS")

                send_json(server, address, {
                    "type": "DONE",
                    "message": "File received and decrypted successfully"
                })

                print("DONE confirmation sent to client.")

            continue

        # Handle incoming CHUNK packets.
        try:
            header = json.loads(header_data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

        if header.get("type") == "CHUNK":
            sequence_number = header.get("seq")

            if (
                isinstance(sequence_number, int)
                and 0 <= sequence_number < total_chunks
            ):

                if sequence_number not in received_chunks:
                    received_chunks[sequence_number] = payload

                    print(
                        f"Received encrypted chunk "
                        f"{sequence_number + 1}/{total_chunks}"
                    )

                else:
                    print(
                        f"Duplicate chunk detected: {sequence_number}"
                    )

                # Acknowledge the received chunk.
                send_json(server, address, {
                    "type": "ACK",
                    "seq": sequence_number
                })

                print(f"ACK sent for chunk {sequence_number}")


if __name__ == "__main__":
    main()
