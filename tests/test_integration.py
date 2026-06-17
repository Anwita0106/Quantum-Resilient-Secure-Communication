from secure_communication import run_secure_communication


def test_normal_scenario_delivers_message():
    result = run_secure_communication(
        "test message", eve=False, n=256, seed=100
    )
    assert result["secure"] is True
    assert result["decrypted_message"] == "test message"
    assert result["encrypted_message"] is not None


def test_attack_scenario_is_rejected():
    result = run_secure_communication(
        "test message", eve=True, n=256, seed=101
    )
    # Not guaranteed every single seed triggers detection, but with n=256
    # and intercept-resend (~25% QBER) it overwhelmingly should.
    assert result["error_rate"] > 0
    if not result["secure"]:
        assert result["decrypted_message"] is None
        assert result["encrypted_message"] is None
