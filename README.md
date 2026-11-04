# UDP-Based Secure File Transfer System

## 1. Project Overview

This project implements a UDP-based file transfer system using Python.

It provides:

- File chunking.
- ACK and retransmission using Stop-and-Wait ARQ.
- AES-256-GCM encryption and decryption.
- SHA-256 integrity verification.
- Incorrect AES key detection.

## 2. Project Structure

```text
CN/
├── udp_file_client.py
├── udp_file_server.py
├── sample.txt
├── requirements.txt
├── README.md
├── file_transfer/
│   ├── __init__.py
│   └── packet.py
├── security/
│   ├── __init__.py
│   └── encryption.py
├── received_files/
└── secret.key
```

## 3. Requirements

- Python 3.10 or later
- cryptography

## 4. Installation

Install the required dependency:

```bash
pip install -r requirements.txt
```

## 5. Encryption Key Setup

Generate a 32-byte AES key:

```bash
python -c "import secrets; open('secret.key','wb').write(secrets.token_bytes(32))"
```

The Client and Server must use the same AES key.

**Important:** Never share or upload secret encryption keys to public repositories.

## 6. Running the Application

Open two terminals in the project directory.

**Terminal 1 – Start the Server:**

```bash
python udp_file_server.py
```

**Terminal 2 – Start the Client:**

```bash
python udp_file_client.py
```

The Client sends `sample.txt` to the Server through UDP.

The received file is saved in the `received_files/` directory.

## 7. Testing

The system supports the following tests:

1. UDP Client-Server communication.
2. File chunking.
3. ACK and retransmission.
4. AES-256-GCM encryption and decryption.
5. SHA-256 integrity verification.
6. Incorrect AES key authentication failure.

## 8. Security Notes

- AES keys must be kept confidential.
- The Client and Server must use the same key for successful decryption.
- Encryption keys must not be transmitted through UDP.
- Do not commit key files to public repositories.
