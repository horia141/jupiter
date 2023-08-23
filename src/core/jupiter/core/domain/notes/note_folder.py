"""A folder for notes in the notebook."""
from dataclasses import dataclass

from jupiter.core.domain.notes.note_folder_name import NoteFolderName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, LeafEntity
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.event import EventSource


@dataclass
class NoteFolder(LeafEntity):
    """A folder for notes in the notebook."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class ChangeParent(Entity.Updated):
        """Change parent event."""

    @dataclass
    class Rename(Entity.Updated):
        """Rename event."""

    note_collection_ref_id: EntityId
    parent_folder_ref_id: EntityId | None
    name: NoteFolderName

    @staticmethod
    def new_root_folder(
        note_collection_ref_id: EntityId, source: EventSource, created_time: Timestamp
    ) -> "NoteFolder":
        """Create the single root folder."""
        note_folder = NoteFolder(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                NoteFolder.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            note_collection_ref_id=note_collection_ref_id,
            parent_folder_ref_id=None,
            name=NoteFolderName("Root"),
        )
        return note_folder

    @staticmethod
    def new_folder(
        note_collection_ref_id: EntityId,
        parent_folder_ref_id: EntityId,
        source: EventSource,
        created_time: Timestamp,
    ) -> "NoteFolder":
        """Create a new folder."""
        note_folder = NoteFolder(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                NoteFolder.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            note_collection_ref_id=note_collection_ref_id,
            parent_folder_ref_id=parent_folder_ref_id,
            name=NoteFolderName("Root"),
        )
        return note_folder

    def change_parent(
        self,
        parent_folder_ref_id: EntityId,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "NoteFolder":
        """Change the parent folder."""
        if self.parent_folder_ref_id is None:
            raise InputValidationError("Cannot change the parent of the root folder.")
        return self._new_version(
            parent_folder_ref_id=parent_folder_ref_id,
            new_event=NoteFolder.ChangeParent.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    def rename(
        self, name: NoteFolderName, source: EventSource, modification_time: Timestamp
    ) -> "NoteFolder":
        """Rename the folder."""
        return self._new_version(
            name=name,
            new_event=NoteFolder.Rename.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.note_collection_ref_id
