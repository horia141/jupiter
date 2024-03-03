"""A note in the notebook."""

import abc

from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.base.entity_name import NOT_USED_NAME
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafSupportEntity,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.repository import LeafEntityRepository
from jupiter.core.framework.update_action import UpdateAction


@entity
class Note(LeafSupportEntity):
    """A note in the notebook."""

    note_collection: ParentLink
    domain: NoteDomain
    source_entity_ref_id: EntityId
    content: list[OneOfNoteContentBlock]

    @staticmethod
    @create_entity_action
    def new_note(
        ctx: DomainContext,
        note_collection_ref_id: EntityId,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        content: list[OneOfNoteContentBlock],
    ) -> "Note":
        """Create a note."""
        return Note._create(
            ctx,
            name=NOT_USED_NAME,
            note_collection=ParentLink(note_collection_ref_id),
            domain=domain,
            source_entity_ref_id=source_entity_ref_id,
            content=content,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        content: UpdateAction[list[OneOfNoteContentBlock]],
    ) -> "Note":
        """Update the note name and content."""
        return self._new_version(
            ctx,
            content=content.or_else(self.content),
        )

    @property
    def can_be_removed_independently(self) -> bool:
        """Whether the note can be removed independently."""
        if self.domain == NoteDomain.DOC:
            return False
        return True


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
