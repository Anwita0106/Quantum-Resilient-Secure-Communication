from quantum_key_generator import generate_quantum_key


def test_key_length_does_not_exceed_n():
    key, error_rate, stats = generate_quantum_key(n=64, eve=False, seed=1)
    assert len(key) <= 64
    assert stats["sifted_length"] == len(key)
    assert all(bit in (0, 1) for bit in key)


def test_no_eavesdropper_has_low_error_rate():
    _, error_rate, _ = generate_quantum_key(n=300, eve=False, seed=2)
    # With no eavesdropper, the simulator is noiseless, so QBER should be 0.
    assert error_rate == 0.0


def test_eavesdropper_introduces_significant_errors():
    _, error_rate, _ = generate_quantum_key(n=300, eve=True, seed=3)
    # Intercept-resend theoretically yields ~25% QBER on average; allow
    # a wide tolerance since this is a stochastic simulation.
    assert error_rate > 0.10


def test_seed_gives_reproducible_results():
    key1, rate1, _ = generate_quantum_key(n=128, eve=True, seed=7)
    key2, rate2, _ = generate_quantum_key(n=128, eve=True, seed=7)
    assert key1 == key2
    assert rate1 == rate2


def test_error_rate_is_bounded():
    _, error_rate, _ = generate_quantum_key(n=200, eve=True, seed=11)
    assert 0.0 <= error_rate <= 1.0
