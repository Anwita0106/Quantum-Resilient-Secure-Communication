import pytest

from key_derivation import bits_to_bytes, derive_fernet_key


def test_bits_to_bytes_basic():
    assert bits_to_bytes([0, 0, 0, 0, 0, 0, 0, 1]) == b"\x01"
    assert bits_to_bytes([1, 1, 1, 1, 1, 1, 1, 1]) == b"\xff"


def test_bits_to_bytes_pads_partial_byte():
    # 4 bits -> padded to 8 bits with trailing zeros: 1010 0000 = 0xA0
    assert bits_to_bytes([1, 0, 1, 0]) == b"\xa0"


def test_bits_to_bytes_empty():
    assert bits_to_bytes([]) == b""


def test_derive_fernet_key_is_usable_length():
    key = derive_fernet_key([1, 0, 1, 1, 0, 0, 1, 0] * 8)
    # Fernet keys are 44-byte base64url strings (32 raw bytes encoded).
    assert len(key) == 44


def test_derive_fernet_key_is_deterministic():
    bits = [0, 1, 1, 0, 1, 0, 0, 1] * 4
    assert derive_fernet_key(bits) == derive_fernet_key(bits)


def test_derive_fernet_key_differs_for_different_input():
    bits_a = [0, 1, 0, 1] * 8
    bits_b = [1, 0, 1, 0] * 8
    assert derive_fernet_key(bits_a) != derive_fernet_key(bits_b)


def test_empty_key_raises():
    with pytest.raises(ValueError):
        derive_fernet_key([])
