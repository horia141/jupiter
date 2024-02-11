"""Tests for the timezone."""
import pytest
from jupiter.core.domain.core.timezone import UTC, Timezone
from jupiter.core.framework.errors import InputValidationError


def test_creation() -> None:
    timezone = Timezone("Europe/Paris")
    assert str(timezone) == "Europe/Paris"

def test_utc() -> None:
    assert str(UTC) == "UTC"
