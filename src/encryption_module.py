"""
Symmetric encryption (AES via Fernet) for the secured channel.

Fixed vs. the original implementation: this module no longer generates
its own random key. Generating an independent key here meant the
BB84-derived quantum key was computed, used for the error-rate check,
and then thrown away — the actual message was encrypted with a key that
had nothing to do with the quantum exchange. Callers (see
`secure_communication.py`) now derive the Fernet key from the quantum
key via `key_derivation.derive_fernet_key` and pass it in here, so the
quantum key is what actually protects the message.
"""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken


def encrypt_message(message: str, key: bytes) -> bytes:
    """Encrypt `message` with the given Fernet key (AES-128-CBC + HMAC)."""
    cipher = Fernet(key)
    return cipher.encrypt(message.encode("utf-8"))


def decrypt_message(encrypted_message: bytes, key: bytes) -> str:
    """
    Decrypt `encrypted_message` with the given Fernet key.

    Raises:
        InvalidToken: if the key is wrong or the ciphertext was tampered
            with. Callers should treat this as a failed/compromised
            decryption rather than letting it propagate as a crash.
    """
    cipher = Fernet(key)
    try:
        return cipher.decrypt(encrypted_message).decode("utf-8")
    except InvalidToken as exc:
        raise InvalidToken(
            "Decryption failed: the key is incorrect or the message was tampered with."
        ) from exc
