"""
Key derivation / privacy amplification.

BB84 gives Alice and Bob a *sifted* key (bits where their bases agreed),
but a real protocol still needs to:
  1. Compress that raw sifted key down to a uniformly-random symmetric key
     (privacy amplification), so any partial information an eavesdropper
     gained does not carry over to the final key.
  2. Produce a key in the exact format the chosen cipher needs.

This module derives a 32-byte key via HKDF-SHA256 from the sifted quantum
key and base64url-encodes it for use with `cryptography.fernet.Fernet`.

Note: this is a practical simplification, not a rigorous information-
theoretic privacy-amplification scheme (which would size its output based
on an estimate of Eve's mutual information from the measured QBER). HKDF
is still the right primitive for "turn non-uniform secret material into a
uniform key," and is what makes this project's quantum key actually do
something cryptographically meaningful instead of being discarded after
the error-rate check.
"""

from __future__ import annotations

import base64
from typing import List, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def bits_to_bytes(bits: List[int]) -> bytes:
    """Pack a list of 0/1 bits into bytes (MSB-first, zero-padded)."""
    if not bits:
        return b""
    bit_str = "".join(str(b) for b in bits)
    padding = (-len(bit_str)) % 8
    bit_str += "0" * padding
    return int(bit_str, 2).to_bytes(len(bit_str) // 8, byteorder="big")


def derive_fernet_key(
    quantum_bits: List[int],
    salt: Optional[bytes] = None,
    info: bytes = b"qkd-fernet-key-v1",
) -> bytes:
    """
    Derive a Fernet-compatible (base64url, 32-byte) key from a sifted
    quantum key.

    Raises:
        ValueError: if the quantum key is empty (e.g. the channel was so
            noisy that no bits survived sifting). Callers should reject
            the channel via intrusion detection before reaching this point.
    """
    if not quantum_bits:
        raise ValueError(
            "Cannot derive an encryption key from an empty quantum key. "
            "The channel should have been rejected before this point."
        )

    raw_key_material = bits_to_bytes(quantum_bits)
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=info)
    derived = hkdf.derive(raw_key_material)
    return base64.urlsafe_b64encode(derived)
