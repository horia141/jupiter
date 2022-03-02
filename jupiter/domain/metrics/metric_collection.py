"""A metric collection."""
from dataclasses import dataclass

from jupiter.framework.entity import Entity, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource


@dataclass(frozen=True)
class MetricCollection(Entity):
    """A metric collection."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class ChangeCollectionProjectRefId(Entity.Updated):
        """Change catch up project ref id."""

    workspace_ref_id: EntityId
    collection_project_ref_id: EntityId

    @staticmethod
    def new_metric_collection(
            workspace_ref_id: EntityId, collection_project_ref_id: EntityId, source: EventSource,
            created_time: Timestamp) -> 'MetricCollection':
        """Create a metric collection."""
        metric_collection = MetricCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[MetricCollection.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            workspace_ref_id=workspace_ref_id,
            collection_project_ref_id=collection_project_ref_id)
        return metric_collection

    def change_collection_project(
            self, collection_project_ref_id: EntityId, source: EventSource,
            modified_time: Timestamp) -> 'MetricCollection':
        """Change the catch up project."""
        if self.collection_project_ref_id == collection_project_ref_id:
            return self
        return self._new_version(
            collection_project_ref_id=collection_project_ref_id,
            new_event=MetricCollection.ChangeCollectionProjectRefId.make_event_from_frame_args(
                source, self.version, modified_time))
