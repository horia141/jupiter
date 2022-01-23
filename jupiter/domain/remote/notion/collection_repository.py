"""The Notion connection repository."""
import abc

from jupiter.domain.remote.notion.connection import NotionConnection
from jupiter.framework.base.entity_id import EntityId


class NotionConnectionAlreadyExistsError(Exception):
    """Error raised when the Notion connection already exists."""


class NotionConnectionNotFoundError(Exception):
    """Error raised when the Notion connection is not found."""


class NotionConnectionRepository(abc.ABC):
    """A repository for Notion connections."""

    @abc.abstractmethod
    def create(self, notion_connection: NotionConnection) -> NotionConnection:
        """Create a Notion connection."""

    @abc.abstractmethod
    def save(self, notion_connection: NotionConnection) -> NotionConnection:
        """Save a workspace."""

    @abc.abstractmethod
    def load_for_workspace(self, workspace_ref_id: EntityId) -> NotionConnection:
        """Loads the workspace."""
