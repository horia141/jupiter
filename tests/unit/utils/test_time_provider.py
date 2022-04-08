"""Tests for the time provider."""
import unittest
from pendulum import UTC

from jupiter.utils.time_provider import TimeProvider


class TimeProviderTestCase(unittest.TestCase):
    """Time provider tests."""

    def test_get_current_time_is_in_utc(self) -> None:
        """Current time is in UTC."""
        time_provider = TimeProvider()
        current_time = time_provider.get_current_time()

        self.assertEqual(current_time.as_datetime().timezone, UTC)

    def test_get_current_time_is_constant(self) -> None:
        """Current time is always the same once set."""
        time_provider = TimeProvider()
        current_time_1 = time_provider.get_current_time()
        current_time_2 = time_provider.get_current_time()

        self.assertEqual(current_time_1, current_time_2)
