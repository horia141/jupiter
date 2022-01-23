"""The pages link repository."""
import abc
from typing import Optional

from jupiter.framework.storage import Repository
from jupiter.remote.notion.common import NotionLockKey
from jupiter.remote.notion.infra.page_link import NotionPageLink


class NotionPageLinkNotFoundError(Exception):
    """Exception raised when a Notion page link isn't found."""


class NotionPageLinkRepository(Repository, abc.ABC):
    """The pages link repository."""

    @abc.abstractmethod
    def create(self, notion_page_link: NotionPageLink) -> NotionPageLink:
        """Create a notion page link."""

    @abc.abstractmethod
    def save(self, notion_page_link: NotionPageLink) -> NotionPageLink:
        """Save a notion page link."""

    @abc.abstractmethod
    def load(self, key: NotionLockKey) -> NotionPageLink:
        """Load a particular notion page link."""

    @abc.abstractmethod
    def load_optional(self, key: NotionLockKey) -> Optional[NotionPageLink]:
        """Load a particular notion page link or return null if it cannot be found."""

    @abc.abstractmethod
    def remove(self, key: NotionLockKey) -> None:
        """Remove a notion page link."""
