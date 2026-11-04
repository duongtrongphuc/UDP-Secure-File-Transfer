
from pathlib import Path
import hashlib

from file_transfer.packet import split_file, reassemble_file


Path("tests").mkdir(exist_ok=True)

original_path = Path("tests/original.txt")
received_path = Path("tests/received.txt")

original_content = (
    "Hello! This is a file transfer test.\n" * 200
)

original_path.write_text(original_content, encoding="utf-8")

filename, total_chunks, chunks = split_file(
    original_path,
    chunk_size=1024
)

print("Original filename:", filename)
print("Total chunks:", total_chunks)

for sequence_number, payload in chunks:
    print(
        f"Chunk {sequence_number}: "
        f"{len(payload)} bytes"
    )

received_chunks = list(reversed(chunks))

reassemble_file(
    received_chunks,
    received_path,
    total_chunks
)


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


original_hash = calculate_sha256(original_path)
received_hash = calculate_sha256(received_path)

print("\nOriginal SHA-256:", original_hash)
print("Received SHA-256:", received_hash)

if original_hash == received_hash:
    print("\nSUCCESS: File reassembled correctly!")
else:
    print("\nFAILED: File integrity check failed!")
