# Changelog

## v2.0.0 — Correctness & quality pass

### Fixed
- **Quantum key was never actually used for encryption.** `encrypt_message`
  generated its own independent Fernet key, so the BB84 key only fed the
  error-rate check and was discarded afterward — the "hybrid
  quantum-classical encryption" the README described wasn't actually
  happening. Added `key_derivation.py`, which derives the Fernet key via
  HKDF-SHA256 from the sifted quantum key, and wired it through
  `secure_communication.py`.
- **Eve's attack model discarded her measurement.** The original code had
  Eve measure the qubit, then unconditionally reset it to `|0⟩` before
  Bob's stage — meaning Eve's result was thrown away rather than resent.
  Rewrote `quantum_key_generator.py` to perform a proper two-stage
  intercept-resend: Eve measures in a random basis, then *re-prepares* a
  qubit from her own measured bit/basis to forward to Bob. This now
  produces the textbook ~25% QBER for intercept-resend, instead of an
  inflated, less meaningful number.
- **`results/` files were hand-written samples, not generated output.**
  `main.py` only printed to the console. It now writes `no_attack_output.txt`,
  `attack_output.txt`, and a real `error_rate_comparison.png` chart
  (via the new `visualization.py`) on every run.

### Improved
- Quantum simulation is now batched (`backend.run([...])`) instead of
  issuing one simulator call per qubit — much faster for larger key
  lengths.
- `--seed` support throughout (including seeding the Aer simulator
  itself, not just Python's `random`) for fully reproducible runs —
  used by the test suite.
- `main.py` is now a real CLI (`--message`, `--key-length`, `--threshold`,
  `--seed`, `--output-dir`) instead of a hardcoded script.
- Default intrusion-detection threshold changed from an arbitrary 0.15
  to 0.11, the commonly cited BB84 security bound against intercept-resend/
  individual attacks; documented why in `intrusion_detection.py`.
- `decrypt_message` now raises a clear `InvalidToken` with a helpful
  message instead of an opaque crash on a bad key/tampered ciphertext.
- Added type hints and docstrings throughout `src/`.

### Added
- `tests/` — 22 pytest tests covering BB84 key generation, intrusion
  detection, key derivation, encryption round-trips/failure modes, and
  an end-to-end integration test.
- Pinned `requirements.txt` (previously unpinned).
- `.gitignore` (compiled `__pycache__`/`.pyc` files were previously
  committed to the repo).

### Notes on remaining simplifications
This is still a demo/education project, not a production QKD system.
Two things worth knowing if you build on it:
- Privacy amplification here is a practical HKDF-based step, not a
  rigorous information-theoretic calculation sized to the eavesdropper's
  estimated mutual information (which is what real QKD systems use).
- There's no classical-channel authentication for the basis-reconciliation
  step, so this doesn't defend against man-in-the-middle attacks on that
  channel — only against passive/active eavesdropping on the quantum
  channel itself.
