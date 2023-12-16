"""Tests for the timezone."""
import pytest
from jupiter.core.domain.core.timezone import UTC, Timezone
from jupiter.core.framework.errors import InputValidationError


def test_creation() -> None:
    timezone = Timezone("Europe/Paris")
    assert str(timezone) == "Europe/Paris"


def test_parse_raw_timezone() -> None:
    raw_timezone = "Europe/Paris"
    timezone_obj = Timezone.from_raw(raw_timezone)
    assert str(timezone_obj) == raw_timezone


def test_parse_bad_timezone_raises_error() -> None:
    bad_timezone = "bad-timezone"
    with pytest.raises(InputValidationError):
        Timezone.from_raw(bad_timezone)


def test_comparison() -> None:
    timezone1 = Timezone.from_raw("America/Los_Angeles")
    timezone2 = Timezone.from_raw("Europe/Paris")

    assert timezone1 < timezone2
    assert not (timezone2 < timezone1)
    assert timezone1 == timezone1
    assert timezone2 == timezone2
    assert not (timezone1 == timezone2)


def test_utc() -> None:
    assert str(UTC) == "UTC"
