"""The Notion connection repository."""

from jupiter.domain.remote.notion.connection import NotionConnection
from jupiter.framework.repository import StubEntityRepository, StubEntityAlreadyExistsError, StubEntityNotFoundError


class NotionConnectionAlreadyExistsError(StubEntityAlreadyExistsError):
    """Error raised when the Notion connection already exists."""


class NotionConnectionNotFoundError(StubEntityNotFoundError):
    """Error raised when the Notion connection is not found."""


class NotionConnectionRepository(StubEntityRepository[NotionConnection]):
    """A repository for Notion connections."""
