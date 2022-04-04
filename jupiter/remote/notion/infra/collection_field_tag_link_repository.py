"""The collections link repository."""
import abc
from typing import Optional, Iterable

from jupiter.framework.repository import Repository
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.collection_field_tag_link import (
    NotionCollectionFieldTagLink,
)


class NotionCollectionFieldTagLinkNotFoundError(Exception):
    """Exception raised when a Notion collection field tag link isn't found."""


class NotionCollectionFieldTagLinkRepository(Repository, abc.ABC):
    """The collections field tag link repository."""

    @abc.abstractmethod
    def create(
        self, notion_collection_field_tag_link: NotionCollectionFieldTagLink
    ) -> NotionCollectionFieldTagLink:
        """Create a notion collection field tag link."""

    @abc.abstractmethod
    def save(
        self, notion_collection_field_tag_link: NotionCollectionFieldTagLink
    ) -> NotionCollectionFieldTagLink:
        """Save a notion collection field tag link."""

    @abc.abstractmethod
    def load(self, key: NotionLockKey) -> NotionCollectionFieldTagLink:
        """Load a particular notion collection field tag link."""

    @abc.abstractmethod
    def load_optional(
        self, key: NotionLockKey
    ) -> Optional[NotionCollectionFieldTagLink]:
        """Load a particular notion collection field tag link or return null if it cannot be found."""

    @abc.abstractmethod
    def find_all_for_collection(
        self, collection_key: NotionLockKey, field: str
    ) -> Iterable[NotionCollectionFieldTagLink]:
        """Load all Notion collection field tags for a particular collection."""

    @abc.abstractmethod
    def remove(self, key: NotionLockKey) -> None:
        """Remove a notion collection field tag link."""
