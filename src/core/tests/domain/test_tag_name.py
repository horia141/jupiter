"""Tests for tag name."""
import pytest
from jupiter.core.domain.core.tags.tag_name import TagName
from jupiter.core.framework.errors import InputValidationError


def test_construction() -> None:
    tag_name = TagName("tag-name")
    assert str(tag_name) == "tag-name"

