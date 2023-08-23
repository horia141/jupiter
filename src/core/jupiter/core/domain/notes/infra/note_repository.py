"""A repository of notes."""
import abc
from typing import Iterable, Optional

from jupiter.core.domain.notes.note import Note
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class NoteNotFoundError(LeafEntityNotFoundError):
    """Error raised when a note is not found."""


class NoteRepository(LeafEntityRepository[Note], abc.ABC):
    """A repository of notes."""

    @abc.abstractmethod
    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_parent_folder_ref_id: Optional[EntityId] = None,
    ) -> list[Note]:
        """Find all notes."""
