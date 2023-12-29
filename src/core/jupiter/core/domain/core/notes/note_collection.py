"""The note collection."""

from jupiter.core.domain.core.notes.note import Note
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    ContainsMany,
    IsRefId,
    ParentLink,
    TrunkEntity,
    entity,
)


@entity
class NoteCollection(TrunkEntity):
    """A note collection."""

    workspace: ParentLink

    notes = ContainsMany(Note, note_collection_ref_id=IsRefId())

    @staticmethod
    def new_note_collection(
        ctx: DomainContext,
        workspace_ref_id: EntityId,
    ) -> "NoteCollection":
        """Create a inbox task collection."""
        return NoteCollection._create(ctx, workspace=ParentLink(workspace_ref_id))
