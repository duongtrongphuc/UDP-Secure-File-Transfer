
from security.encryption import encrypt_data, decrypt_data

original_data = b"Hello! This is a secret file transfer."

encrypted_data = encrypt_data(original_data)
decrypted_data = decrypt_data(encrypted_data)

print("Original:", original_data)
print("Encrypted:", encrypted_data)
print("Decrypted:", decrypted_data)

if original_data == decrypted_data:
    print("SUCCESS: AES encryption/decryption works!")
else:
    print("ERROR: Data mismatch!")
