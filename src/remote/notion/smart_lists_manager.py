"""The centralised point for interacting with Notion smart lists."""
from types import TracebackType
from typing import Optional
import typing

from remote.notion.common import NotionPageLink


class NotionSmartListsManager:
    """The centralised point for interacting with Notion smart lists."""

    def __enter__(self) -> 'NotionSmartListsManager':
        """Enter context."""
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def upsert_root_page(self, parent_page: NotionPageLink) -> None:
        """Upsert the root page for the smart lists section."""

    def get_root_page(self) -> NotionPageLink:
        """Retrieve the root page for the smart lists section."""
        return typing.cast(NotionPageLink, None)

    def upsert_smart_list(self, parent_page: NotionPageLink) -> None:
        """Upsert the Notion-side smart list."""

    def upsert_smart_list_item(self) -> None:
        """Upsert the Notion-side smart list item."""
