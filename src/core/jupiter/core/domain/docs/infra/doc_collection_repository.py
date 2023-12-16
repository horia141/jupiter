"""A repository of doc collections."""
import abc

from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.framework.repository import (
    TrunkEntityNotFoundError,
    TrunkEntityRepository,
)


class DocCollectionNotFoundError(TrunkEntityNotFoundError):
    """Error raised when the doc collection is not found."""


class DocCollectionRepository(TrunkEntityRepository[DocCollection], abc.ABC):
    """A repository of doc collections."""
