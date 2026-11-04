
from pathlib import Path

CHUNK_SIZE = 1024


def split_data(data, filename, chunk_size=CHUNK_SIZE):
    """
    Split bytes data into chunks.

    Returns:
        filename: Original file name
        total_chunks: Number of chunks
        chunks: List of (sequence_number, payload)
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    chunks = []

    for sequence_number, start in enumerate(range(0, len(data), chunk_size)):
        payload = data[start:start + chunk_size]
        chunks.append((sequence_number, payload))

    return filename, len(chunks), chunks


def split_file(file_path, chunk_size=CHUNK_SIZE):
    """
    Read a file and split it into smaller chunks.
    """

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    data = file_path.read_bytes()

    return split_data(data, file_path.name, chunk_size)


def reassemble_file(chunks, output_path, total_chunks):
    """
    Reassemble chunks into the original file.
    """

    if total_chunks < 0:
        raise ValueError("Invalid total_chunks")

    if len(chunks) != total_chunks:
        raise ValueError("Missing or extra chunks")

    chunk_dict = {}

    for sequence_number, payload in chunks:
        if not 0 <= sequence_number < total_chunks:
            raise ValueError("Invalid sequence number")

        if sequence_number in chunk_dict:
            raise ValueError("Duplicate chunk")

        chunk_dict[sequence_number] = payload

    if len(chunk_dict) != total_chunks:
        raise ValueError("Missing chunks")

    output_path = Path(output_path)

    with open(output_path, "wb") as file:
        for sequence_number in range(total_chunks):
            file.write(chunk_dict[sequence_number])

    return output_path
