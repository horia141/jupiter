"""A repository of doc collections."""
import abc

from jupiter.core.domain.concept.docs.doc_collection import DocCollection
from jupiter.core.framework.repository import (
    TrunkEntityRepository,
)


class DocCollectionRepository(TrunkEntityRepository[DocCollection], abc.ABC):
    """A repository of doc collections."""
