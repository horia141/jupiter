"""The collections link repository."""
import abc
from typing import Optional

from jupiter.framework.repository import Repository
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_link import NotionCollectionLink


class NotionCollectionLinkNotFoundError(Exception):
    """Exception raised when a Notion collection link isn't found."""


class NotionCollectionLinkRepository(Repository, abc.ABC):
    """The collections link repository."""

    @abc.abstractmethod
    def create(
        self, notion_collection_link: NotionCollectionLink
    ) -> NotionCollectionLink:
        """Create a notion collection link."""

    @abc.abstractmethod
    def save(
        self, notion_collection_link: NotionCollectionLink
    ) -> NotionCollectionLink:
        """Save a notion collection link."""

    @abc.abstractmethod
    def load(self, key: NotionLockKey) -> NotionCollectionLink:
        """Load a particular notion collection link."""

    @abc.abstractmethod
    def load_optional(self, key: NotionLockKey) -> Optional[NotionCollectionLink]:
        """Load a particular notion collection link or return null if it cannot be found."""

    @abc.abstractmethod
    def remove(self, key: NotionLockKey) -> None:
        """Remove a notion collection link."""
