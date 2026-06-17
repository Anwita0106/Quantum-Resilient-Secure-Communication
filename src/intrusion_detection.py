"""
Intrusion detection based on the Quantum Bit Error Rate (QBER).

In BB84, any eavesdropper that measures qubits in transit unavoidably
disturbs them (no-cloning theorem), which shows up as an elevated error
rate between Alice's and Bob's sifted keys. Comparing the measured QBER
against a threshold is the standard, simple way to decide whether to
trust a given key.

The default threshold of 0.11 (11%) is the commonly cited BB84 security
bound under simple intercept-resend attacks and individual-attack models;
above this, no secure key can be distilled with the privacy-amplification
techniques typically paired with BB84. Real-world systems set this based
on their specific error-correction/privacy-amplification scheme and
hardware noise floor — treat 0.11 as a reasonable default, not a law.
"""

from __future__ import annotations

DEFAULT_QBER_THRESHOLD = 0.11


def adaptive_intrusion_detection(error_rate: float, threshold: float = DEFAULT_QBER_THRESHOLD) -> bool:
    """
    Decide whether the quantum channel is safe to use.

    Args:
        error_rate: measured QBER (fraction of sifted bits that disagree).
        threshold: QBER above which the channel is treated as compromised.

    Returns:
        True if the channel is considered secure, False if intrusion is
        suspected and the key should be rejected.
    """
    if not 0.0 <= error_rate <= 1.0:
        raise ValueError(f"error_rate must be between 0 and 1, got {error_rate}")
    return error_rate < threshold
