"""Tests for tag name."""
import pytest
from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.framework.errors import InputValidationError


def test_construction() -> None:
    tag_name = TagName("tag-name")
    assert str(tag_name) == "tag-name"


def test_parse_raw_tag_name() -> None:
    raw_tag_name = "tag-name"
    tag_name_obj = TagName.from_raw(raw_tag_name)
    assert str(tag_name_obj) == raw_tag_name


def test_parse_raw_does_some_cleanup() -> None:
    raw_tag_name = " tag-name "
    tag_name_obj = TagName.from_raw(raw_tag_name)
    assert str(tag_name_obj) == "tag-name"


def test_parse_null_tag_name_raises_error() -> None:
    null_tag_name = None
    with pytest.raises(InputValidationError):
        TagName.from_raw(null_tag_name)


def test_empty_tag_name_raises_error() -> None:
    empty_tag_name = ""
    with pytest.raises(InputValidationError):
        TagName.from_raw(empty_tag_name)


def test_parse_bad_tag_name_raises_error() -> None:
    bad_tag_name = "_bad-tag-name"
    with pytest.raises(InputValidationError):
        TagName.from_raw(bad_tag_name)


def test_comparison() -> None:
    tag_name1 = TagName.from_raw("tag-name1")
    tag_name2 = TagName.from_raw("tag-name2")

    assert tag_name1 < tag_name2
    assert not (tag_name2 < tag_name1)
    assert tag_name1 == tag_name1
    assert tag_name2 == tag_name2
    assert not (tag_name1 == tag_name2)
