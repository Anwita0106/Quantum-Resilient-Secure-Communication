import pytest

from intrusion_detection import adaptive_intrusion_detection, DEFAULT_QBER_THRESHOLD


def test_low_error_rate_is_secure():
    assert adaptive_intrusion_detection(0.0) is True
    assert adaptive_intrusion_detection(0.05) is True


def test_high_error_rate_is_flagged():
    assert adaptive_intrusion_detection(0.25) is False
    assert adaptive_intrusion_detection(1.0) is False


def test_custom_threshold():
    assert adaptive_intrusion_detection(0.20, threshold=0.30) is True
    assert adaptive_intrusion_detection(0.20, threshold=0.10) is False


def test_boundary_is_exclusive():
    # error_rate == threshold should NOT be considered secure
    assert adaptive_intrusion_detection(DEFAULT_QBER_THRESHOLD, threshold=DEFAULT_QBER_THRESHOLD) is False


def test_invalid_error_rate_raises():
    with pytest.raises(ValueError):
        adaptive_intrusion_detection(-0.1)
    with pytest.raises(ValueError):
        adaptive_intrusion_detection(1.1)
