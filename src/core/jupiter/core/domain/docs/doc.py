"""A doc in the docbook."""
from dataclasses import dataclass

from jupiter.core.domain.docs.doc_name import DocName
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, LeafEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Doc(LeafEntity):
    """A doc in the docbook."""

    @dataclass
    class Created(LeafEntity.Created):
        """Created event."""

    @dataclass
    class ChangeParent(LeafEntity.Updated):
        """Change parent event."""

    @dataclass
    class Update(LeafEntity.Updated):
        """Update content event."""

    doc_collection_ref_id: EntityId
    parent_doc_ref_id: EntityId | None
    name: DocName

    @staticmethod
    def new_doc(
        doc_collection_ref_id: EntityId,
        parent_doc_ref_id: EntityId | None,
        name: DocName,
        source: EventSource,
        created_time: Timestamp,
    ) -> "Doc":
        """Create a doc."""
        doc = Doc(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                Doc.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            doc_collection_ref_id=doc_collection_ref_id,
            parent_doc_ref_id=parent_doc_ref_id,
            name=name,
        )
        return doc

    def change_parent(
        self,
        parent_doc_ref_id: EntityId | None,
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Doc":
        """Change the parent doc of the doc."""
        return self._new_version(
            parent_doc_ref_id=parent_doc_ref_id,
            new_event=Doc.ChangeParent.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    def update(
        self,
        name: UpdateAction[DocName],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Doc":
        """Update the doc name and content."""
        return self._new_version(
            name=name.or_else(self.name),
            new_event=Doc.Update.make_event_from_frame_args(
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.doc_collection_ref_id
