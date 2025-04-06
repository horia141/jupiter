"""Tests for tag name."""

from jupiter.core.domain.core.tags.tag_name import TagName


def test_construction() -> None:
    tag_name = TagName("tag-name")
    assert str(tag_name) == "tag-name"
