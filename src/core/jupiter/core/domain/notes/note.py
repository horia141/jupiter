"""A note in the notebook."""
from dataclasses import dataclass

from jupiter.core.domain.notes.note_content_block import NoteContentBlock
from jupiter.core.domain.notes.note_name import NoteName
from jupiter.core.domain.notes.note_source import NoteSource
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

    @dataclass
    class ChangeParent(LeafEntity.Updated):
        """Change parent event."""

    note_collection_ref_id: EntityId
    source: NoteSource
    name: NoteName
    parent_folder_ref_id: EntityId
    content: list[NoteContentBlock]

    @staticmethod
    def new_note(
        note_collection_ref_id: EntityId,
        name: NoteName,
        parent_folder_ref_id: EntityId,
        content: list[NoteContentBlock],
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
            note_collection_ref_id=note_collection_ref_id,
            source=NoteSource.USER,
            name=name,
            parent_folder_ref_id=parent_folder_ref_id,
            content=content,
        )
        return note

    def update(
        self,
        name: UpdateAction[NoteName],
        content: UpdateAction[list[NoteContentBlock]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Note":
        """Update the note name and content."""
        return self._new_version(
            name=name.or_else(self.name),
            content=content.or_else(self.content),
            new_event=Note.Update.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def change_parent(
        self,
        parent_folder_ref_id: EntityId,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Note":
        """Change the parent folder of the note."""
        return self._new_version(
            parent_folder_ref_id=parent_folder_ref_id,
            new_event=Note.ChangeParent.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.note_collection_ref_id
