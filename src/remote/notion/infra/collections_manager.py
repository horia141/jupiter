"""The handler for collections on Notion-side."""
from types import TracebackType
from typing import Optional

import typing

from remote.notion.common import NotionPageLink, NotionCollectionLink


class CollectionsManager:
    """The handler for collections on Notion-side."""

    def __enter__(self) -> 'CollectionsManager':
        """Enter context."""
        return self

    def __exit__(
            self, exc_type: Optional[typing.Type[BaseException]], _exc_val: Optional[BaseException],
            _exc_tb: Optional[TracebackType]) -> None:
        """Exit context."""
        if exc_type is not None:
            return

    def upsert_collection(self, key: str, name: str, root_page: NotionPageLink) -> None:
        """Upsert a collection."""

    def get_collection(self, key: str) -> NotionCollectionLink:
        """Get a collection."""

    def upsert_collection_item(self, collection: NotionCollectionLink, key: str, name: str, url: Optional[str]) -> None:
        """Upsert a collection item."""
