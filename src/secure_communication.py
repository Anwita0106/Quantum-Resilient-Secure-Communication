"""
End-to-end orchestration: BB84 key exchange -> intrusion detection ->
key derivation -> AES (Fernet) encryption.

This ties the previously-disconnected pieces together correctly: the
quantum key that survives intrusion detection is the same key material
used to derive the AES key, instead of encryption using an unrelated
freshly-generated key.
"""

from __future__ import annotations

from typing import Optional

from quantum_key_generator import generate_quantum_key
from intrusion_detection import adaptive_intrusion_detection, DEFAULT_QBER_THRESHOLD
from key_derivation import derive_fernet_key
from encryption_module import encrypt_message, decrypt_message


def run_secure_communication(
    message: str,
    eve: bool = False,
    n: int = 256,
    threshold: float = DEFAULT_QBER_THRESHOLD,
    seed: Optional[int] = None,
) -> dict:
    """
    Run one full secure-communication attempt and return a result dict.

    Returns a dict with keys:
        secure (bool), error_rate (float), sifted_key_length (int),
        raw_key_length (int), encrypted_message (bytes | None),
        decrypted_message (str | None), log (str — human-readable transcript).
    """
    log_lines = ["Starting Quantum Key Distribution..."]

    quantum_key, error_rate, stats = generate_quantum_key(n=n, eve=eve, seed=seed)

    log_lines.append(f"Raw qubits sent     : {stats['raw_length']}")
    log_lines.append(f"Sifted key length   : {stats['sifted_length']}")
    log_lines.append(f"Error Rate (QBER)   : {error_rate:.2f}")

    secure = adaptive_intrusion_detection(error_rate, threshold=threshold)

    result = {
        "secure": secure,
        "error_rate": error_rate,
        "sifted_key_length": stats["sifted_length"],
        "raw_key_length": stats["raw_length"],
        "encrypted_message": None,
        "decrypted_message": None,
    }

    if secure:
        log_lines.append("Secure Channel Established")

        fernet_key = derive_fernet_key(quantum_key)
        encrypted = encrypt_message(message, fernet_key)
        decrypted = decrypt_message(encrypted, fernet_key)

        log_lines.append(f"Encrypted Message   : {encrypted}")
        log_lines.append(f"Decrypted Message   : {decrypted}")

        result["encrypted_message"] = encrypted
        result["decrypted_message"] = decrypted
    else:
        log_lines.append("Intrusion Detected!")
        log_lines.append("Quantum Key Rejected. A new key exchange would be required.")

    result["log"] = "\n".join(log_lines)
    print("\n" + result["log"])
    return result
