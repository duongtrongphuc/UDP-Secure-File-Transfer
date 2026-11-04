
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BASE_DIR = Path(__file__).resolve().parent.parent


def load_key(key_file="secret.key"):
    key_path = BASE_DIR / key_file

    if not key_path.exists():
        raise FileNotFoundError(f"{key_file} not found!")

    key = key_path.read_bytes()

    if len(key) != 32:
        raise ValueError("AES-256 key must be exactly 32 bytes!")

    return key


def encrypt_data(data: bytes):
    key = load_key("client.key")
    aesgcm = AESGCM(key)

    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)

    return nonce + ciphertext


def decrypt_data(encrypted_data: bytes):
    if len(encrypted_data) < 28:
        raise ValueError("Encrypted data is too short!")

    key = load_key("server.key")
    aesgcm = AESGCM(key)

    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    return aesgcm.decrypt(nonce, ciphertext, None)
