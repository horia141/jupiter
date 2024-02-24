"""A repository of notes."""
import abc

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.repository import (
    LeafEntityRepository,
)


class NoteRepository(LeafEntityRepository[Note], abc.ABC):
    """A repository of notes."""

    @abc.abstractmethod
    async def load_for_source(
        self,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Note:
        """Load a particular note via its source entity."""

    @abc.abstractmethod
    async def load_optional_for_source(
        self,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        allow_archived: bool = False,
    ) -> Note | None:
        """Load a particular note via its source entity."""
