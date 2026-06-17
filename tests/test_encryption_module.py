import pytest
from cryptography.fernet import InvalidToken, Fernet

from encryption_module import encrypt_message, decrypt_message
from key_derivation import derive_fernet_key


def test_round_trip():
    key = derive_fernet_key([1, 0, 1, 1, 0, 0, 1, 0] * 4)
    message = "Hello Bob, this is a quantum-resilient secure message"
    encrypted = encrypt_message(message, key)
    assert decrypt_message(encrypted, key) == message


def test_wrong_key_fails_to_decrypt():
    key_a = derive_fernet_key([1, 0, 1, 1] * 8)
    key_b = derive_fernet_key([0, 1, 0, 1] * 8)
    encrypted = encrypt_message("secret message", key_a)
    with pytest.raises(InvalidToken):
        decrypt_message(encrypted, key_b)


def test_tampered_ciphertext_fails_to_decrypt():
    key = Fernet.generate_key()
    encrypted = bytearray(encrypt_message("secret message", key))
    encrypted[-5] ^= 0xFF  # flip some bits near the end
    with pytest.raises(InvalidToken):
        decrypt_message(bytes(encrypted), key)
