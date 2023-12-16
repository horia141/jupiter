"""Tests for URL."""
import pytest
from jupiter.core.domain.core.url import URL
from jupiter.core.framework.errors import InputValidationError


def test_construct_url() -> None:
    url = URL("https://www.example.com")
    assert str(url) == "https://www.example.com"


def test_parse_raw_url() -> None:
    raw_url = "https://www.example.com"
    url_obj = URL.from_raw(raw_url)
    assert str(url_obj) == raw_url


def test_parse_raw_does_some_cleanup() -> None:
    raw_url = " https://www.example.com "
    url_obj = URL.from_raw(raw_url)
    assert str(url_obj) == "https://www.example.com"


def test_empty_url_raises_error() -> None:
    empty_url = ""
    with pytest.raises(InputValidationError):
        URL.from_raw(empty_url)


def test_parse_null_url_raises_error() -> None:
    null_url = None
    with pytest.raises(InputValidationError):
        URL.from_raw(null_url)


def test_parse_bad_url_raises_error() -> None:
    bad_url = "bad-url"
    with pytest.raises(InputValidationError):
        URL.from_raw(bad_url)


def test_comparison() -> None:
    url1 = URL.from_raw("https://www.example.com")
    url2 = URL.from_raw("https://www.tesla.com")

    assert url1 < url2
    assert not (url2 < url1)
    assert url1 == url1
    assert url2 == url2
    assert not (url1 == url2)
