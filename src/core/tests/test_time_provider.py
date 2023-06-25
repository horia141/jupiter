"""Tests for the time provider."""
from jupiter.core.utils.time_provider import TimeProvider
from pendulum.tz.timezone import UTC


def test_get_current_time_is_in_utc() -> None:
    """Current time is in UTC."""
    time_provider = TimeProvider()
    current_time = time_provider.get_current_time()

    assert current_time.as_datetime().timezone == UTC


def test_get_current_time_is_constant() -> None:
    """Current time is always the same once set."""
    time_provider = TimeProvider()
    current_time_1 = time_provider.get_current_time()
    current_time_2 = time_provider.get_current_time()

    assert current_time_1 == current_time_2
