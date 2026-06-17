"""
BB84 Quantum Key Distribution simulator.

This module simulates the BB84 protocol between Alice and Bob using Qiskit,
optionally with an eavesdropper (Eve) performing a realistic
intercept-resend attack.

Design notes / fixes vs. the original implementation:
  * Eve now performs a genuine intercept-resend attack: she measures the
    qubit in a randomly chosen basis and *re-prepares* a fresh qubit using
    her measured bit and basis before forwarding it to Bob. The previous
    version measured and then reset the qubit to |0> unconditionally,
    discarding her measurement result and overstating the disturbance.
  * All circuits for a given stage are batched into a single
    `backend.run([...])` call instead of one call per qubit. This avoids
    per-circuit simulator overhead and makes runs with hundreds of qubits
    practical.
  * `seed` is accepted for reproducible runs (used by the test suite).
"""

from __future__ import annotations

import random
from typing import List, Tuple, Optional

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

BASES = ("+", "x")


def _prepare_circuit(bit: int, basis: str) -> QuantumCircuit:
    """Encode `bit` into a single qubit using the given basis ('+' = Z, 'x' = X)."""
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == "x":
        qc.h(0)
    return qc


def _measure_in_basis(qc: QuantumCircuit, basis: str) -> QuantumCircuit:
    """Append a measurement in the given basis to an existing circuit."""
    if basis == "x":
        qc.h(0)
    qc.measure(0, 0)
    return qc


def _run_batch(
    circuits: List[QuantumCircuit], backend: AerSimulator, seed: Optional[int] = None
) -> List[int]:
    """Run a batch of single-qubit circuits (1 shot each) and return the measured bits."""
    if not circuits:
        return []
    run_kwargs = {"shots": 1}
    if seed is not None:
        run_kwargs["seed_simulator"] = seed
    job = backend.run(circuits, **run_kwargs)
    result = job.result()
    bits = []
    for i in range(len(circuits)):
        counts = result.get_counts(i)
        bits.append(int(next(iter(counts))))
    return bits


def generate_quantum_key(
    n: int = 256,
    eve: bool = False,
    seed: Optional[int] = None,
) -> Tuple[List[int], float, dict]:
    """
    Run a BB84 exchange between Alice and Bob.

    Args:
        n: Number of qubits Alice sends (raw key length before sifting).
        eve: If True, simulate an eavesdropper performing intercept-resend.
        seed: Optional seed for reproducible randomness (basis/bit choices).

    Returns:
        (final_key, error_rate, stats) where:
          - final_key: sifted key bits where Alice's and Bob's bases agreed.
          - error_rate: fraction of sifted bits where Alice and Bob disagree
            (this is the Quantum Bit Error Rate, QBER).
          - stats: dict with raw_length, sifted_length, and errors, useful
            for logging/reporting.
    """
    rng = random.Random(seed)
    backend = AerSimulator()

    alice_bits = [rng.randint(0, 1) for _ in range(n)]
    alice_bases = [rng.choice(BASES) for _ in range(n)]
    bob_bases = [rng.choice(BASES) for _ in range(n)]

    if eve:
        eve_bases = [rng.choice(BASES) for _ in range(n)]

        # Stage 1: Alice -> Eve. Eve measures each qubit in her own basis.
        stage1 = [
            _measure_in_basis(_prepare_circuit(alice_bits[i], alice_bases[i]), eve_bases[i])
            for i in range(n)
        ]
        eve_bits = _run_batch(stage1, backend, seed=seed)

        # Stage 2: Eve resends what she measured -> Bob measures in his basis.
        stage2 = [
            _measure_in_basis(_prepare_circuit(eve_bits[i], eve_bases[i]), bob_bases[i])
            for i in range(n)
        ]
        bob_bits = _run_batch(stage2, backend, seed=None if seed is None else seed + 1)
    else:
        stage = [
            _measure_in_basis(_prepare_circuit(alice_bits[i], alice_bases[i]), bob_bases[i])
            for i in range(n)
        ]
        bob_bits = _run_batch(stage, backend, seed=seed)

    final_key: List[int] = []
    errors = 0
    for i in range(n):
        if alice_bases[i] == bob_bases[i]:
            final_key.append(alice_bits[i])
            if bob_bits[i] != alice_bits[i]:
                errors += 1

    error_rate = errors / max(1, len(final_key))
    stats = {
        "raw_length": n,
        "sifted_length": len(final_key),
        "errors": errors,
    }
    return final_key, error_rate, stats
