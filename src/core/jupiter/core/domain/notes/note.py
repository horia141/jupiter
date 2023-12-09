"""A note in the notebook."""
from dataclasses import dataclass

from jupiter.core.domain.adate import ADate
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.notes.note_content_block import OneOfNoteContentBlock
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
    class ChangeParent(LeafEntity.Updated):
        """Change parent event."""

    @dataclass
    class Update(LeafEntity.Updated):
        """Update content event."""

    @dataclass
    class UpdateForEntity(LeafEntity.Updated):
        """Update content event for an entity."""

    note_collection_ref_id: EntityId
    parent_note_ref_id: EntityId | None
    source: NoteSource
    source_entity_ref_id: EntityId | None
    name: NoteName
    content: list[OneOfNoteContentBlock]

    @staticmethod
    def new_note(
        note_collection_ref_id: EntityId,
        parent_note_ref_id: EntityId | None,
        name: NoteName,
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
            note_collection_ref_id=note_collection_ref_id,
            parent_note_ref_id=parent_note_ref_id,
            source=NoteSource.USER,
            source_entity_ref_id=None,
            name=name,
            content=content,
        )
        return note

    @staticmethod
    def new_note_for_metric_entry(
        note_collection_ref_id: EntityId,
        metric_name: MetricName,
        metric_entry_ref_id: EntityId,
        collection_time: ADate,
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
            note_collection_ref_id=note_collection_ref_id,
            parent_note_ref_id=None,
            source=NoteSource.METRIC_ENTRY,
            source_entity_ref_id=metric_entry_ref_id,
            name=NoteName.from_raw(
                f'Note for metric "{str(metric_name)}" on {ADate.to_user_date_str(collection_time)}'
            ),
            content=content,
        )
        return note

    def change_parent(
        self,
        parent_note_ref_id: EntityId | None,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Note":
        """Change the parent note of the note."""
        if self.source is not NoteSource.USER:
            raise Exception("Cannot change the parent of a non-user note")
        return self._new_version(
            parent_note_ref_id=parent_note_ref_id,
            new_event=Note.ChangeParent.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def update(
        self,
        name: UpdateAction[NoteName],
        content: UpdateAction[list[OneOfNoteContentBlock]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Note":
        """Update the note name and content."""
        if self.source is not NoteSource.USER:
            raise Exception("Cannot update a non-user note")
        return self._new_version(
            name=name.or_else(self.name),
            content=content.or_else(self.content),
            new_event=Note.Update.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def update_for_entity(
        self,
        content: UpdateAction[list[OneOfNoteContentBlock]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Note":
        """Update the note name and content."""
        if self.source is NoteSource.USER:
            raise Exception("Cannot update a user note")
        return self._new_version(
            content=content.or_else(self.content),
            new_event=Note.UpdateForEntity.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.note_collection_ref_id
