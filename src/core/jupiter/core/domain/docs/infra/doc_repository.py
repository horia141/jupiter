"""A repository of docs."""
import abc
from typing import Iterable, Optional

from jupiter.core.domain.docs.doc import Doc
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class DocNotFoundError(LeafEntityNotFoundError):
    """Error raised when a doc is not found."""


class DocRepository(LeafEntityRepository[Doc], abc.ABC):
    """A repository of docs."""

    @abc.abstractmethod
    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_parent_doc_ref_ids: Optional[Iterable[EntityId | None]] = None,
    ) -> list[Doc]:
        """Find all docs."""
