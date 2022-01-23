"""The collection items link repository."""
import abc
from typing import Optional, Iterable

from jupiter.framework.storage import Repository
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_item_link import NotionCollectionItemLink


class NotionCollectionItemLinkNotFoundError(Exception):
    """Exception raised when a Notion collection item link isn't found."""


class NotionCollectionItemLinkRepository(Repository, abc.ABC):
    """The collections item link repository."""

    @abc.abstractmethod
    def create(self, notion_collection_item_link: NotionCollectionItemLink) -> NotionCollectionItemLink:
        """Create a notion collection item link."""

    @abc.abstractmethod
    def save(self, notion_collection_item_link: NotionCollectionItemLink) -> NotionCollectionItemLink:
        """Save a notion collection item link."""

    @abc.abstractmethod
    def load(self, key: NotionLockKey) -> NotionCollectionItemLink:
        """Load a particular notion collection item link."""

    @abc.abstractmethod
    def load_optional(self, key: NotionLockKey) -> Optional[NotionCollectionItemLink]:
        """Load a particular notion collection item link or return null if it cannot be found."""

    @abc.abstractmethod
    def find_all_for_collection(self, collection_key: NotionLockKey) -> Iterable[NotionCollectionItemLink]:
        """Load all Notion collection item links for a particular collection."""

    @abc.abstractmethod
    def remove(self, key: NotionLockKey) -> None:
        """Remove a notion collection item link."""
