"""A note in the notebook."""
from dataclasses import dataclass

from jupiter.core.domain.core.entity_name import NOT_USED_NAME
from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    LeafEntity,
    create_entity_action,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Note(LeafEntity):
    """A note in the notebook."""

    note_collection_ref_id: EntityId
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
            note_collection_ref_id=note_collection_ref_id,
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
        if self.domain == NoteDomain.DOC:
            return False
        return True

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.note_collection_ref_id
