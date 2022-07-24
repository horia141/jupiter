"""The collection items block link repository."""
import abc
from typing import List

from jupiter.framework.repository import Repository
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_item_block_link import (
    NotionCollectionItemBlockLink,
)


class NotionCollectionItemBlockLinkNotFoundError(Exception):
    """Exception raised when a Notion collection item block link isn't found."""


class NotionCollectionItemBlockLinkRepository(Repository, abc.ABC):
    """The collections item block link repository."""

    @abc.abstractmethod
    def create(
        self, notion_collection_item_block_link: NotionCollectionItemBlockLink
    ) -> NotionCollectionItemBlockLink:
        """Create a notion collection item block link."""

    @abc.abstractmethod
    def save(
        self, notion_collection_item_block_link: NotionCollectionItemBlockLink
    ) -> NotionCollectionItemBlockLink:
        """Save a notion collection item link."""

    @abc.abstractmethod
    def find_all_for_item(
        self, item_key: NotionLockKey
    ) -> List[NotionCollectionItemBlockLink]:
        """Load all Notion collection item block links for a particular collection."""

    @abc.abstractmethod
    def remove(self, item_key: NotionLockKey, position: int) -> None:
        """Remove a notion collection item block link."""

    @abc.abstractmethod
    def remove_all_for_item(self, item_key: NotionLockKey) -> None:
        """Remove all notion collection item block links for a particular item."""
