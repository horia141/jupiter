"""A note in the notebook."""
from dataclasses import dataclass

from jupiter.core.domain.core.entity_name import NOT_USED_NAME
from jupiter.core.domain.core.notes.note_content_block import OneOfNoteContentBlock
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, LeafEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Note(LeafEntity):
    """A note in the notebook."""

    @dataclass
    class Created(LeafEntity.Created):
        """Created event."""

    @dataclass
    class Update(LeafEntity.Updated):
        """Update content event."""

    note_collection_ref_id: EntityId
    domain: NoteDomain
    source_entity_ref_id: EntityId
    content: list[OneOfNoteContentBlock]

    @staticmethod
    def new_note(
        note_collection_ref_id: EntityId,
        domain: NoteDomain,
        source_entity_ref_id: EntityId,
        content: list[OneOfNoteContentBlock],
        source: EventSource,
        created_time: Timestamp,
    ) -> "Note":
        """Create a note."""
        note = Note(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                Note.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            name=NOT_USED_NAME,
            note_collection_ref_id=note_collection_ref_id,
            domain=domain,
            source_entity_ref_id=source_entity_ref_id,
            content=content,
        )
        return note

    def update(
        self,
        content: UpdateAction[list[OneOfNoteContentBlock]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Note":
        """Update the note name and content."""
        return self._new_version(
            content=content.or_else(self.content),
            new_event=Note.Update.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
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
