"""The doc collection."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, TrunkEntity
from jupiter.core.framework.event import EventSource


@dataclass
class DocCollection(TrunkEntity):
    """A doc collection."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    workspace_ref_id: EntityId

    @staticmethod
    def new_doc_collection(
        workspace_ref_id: EntityId,
        source: EventSource,
        created_time: Timestamp,
    ) -> "DocCollection":
        """Create a inbox task collection."""
        doc_collection = DocCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                DocCollection.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            workspace_ref_id=workspace_ref_id,
        )
        return doc_collection

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
