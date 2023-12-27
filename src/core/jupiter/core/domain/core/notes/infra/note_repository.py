"""A repository of notes."""
import abc
from typing import Iterable, Optional

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.entity import EntityLinkFilterCompiled
from jupiter.core.framework.repository import (
    LeafEntityNotFoundError,
    LeafEntityRepository,
)


class NoteNotFoundError(LeafEntityNotFoundError):
    """Error raised when a note is not found."""


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

    @abc.abstractmethod
    async def find_all_with_filters(
        self,
        parent_ref_id: EntityId,
        domain: Optional[NoteDomain] = None,
        allow_archived: bool = False,
        filter_ref_ids: Optional[Iterable[EntityId]] = None,
        filter_source_entity_ref_ids: Optional[Iterable[EntityId]] = None,
    ) -> list[Note]:
        """Find all notes."""

    @abc.abstractmethod
    async def find_all_generic(
        self,
        allow_archived: bool,
        **kwargs: EntityLinkFilterCompiled,
    ) -> Iterable[Note]:
        """Find all habits with generic filters."""
