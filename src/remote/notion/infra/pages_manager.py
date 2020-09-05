"""The handler of ad-hoc pages on Notion side."""
from types import TracebackType
from typing import Optional

import typing

from remote.notion.common import NotionPageLink


class PagesManager:
    """The handler of ad-hoc pages on Notion side."""

    def __enter__(self) -> 'PagesManager':
        """Enter context."""
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def upsert_page(self, key: str, name: str, parent_page: Optional[NotionPageLink]) -> NotionPageLink:
        """Create a page with a given name."""

    def get_page(self, key: str) -> NotionPageLink:
        """Get a page with a given key."""
