"""A collection of slack tasks."""
from dataclasses import dataclass

from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import Entity, FIRST_VERSION, TrunkEntity
from jupiter.framework.event import EventSource


@dataclass(frozen=True)
class SlackTaskCollection(TrunkEntity):
    """A collection of slack tasks."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class ChangeGenerationProjectRefId(Entity.Updated):
        """Change generation project ref id."""

    push_integration_group_ref_id: EntityId
    generation_project_ref_id: EntityId

    @staticmethod
    def new_slack_task_collection(
            push_integration_group_ref_id: EntityId, generation_project_ref_id: EntityId, source: EventSource,
            created_time: Timestamp) -> 'SlackTaskCollection':
        """Create a slack task collection."""
        slack_task_collection = SlackTaskCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[SlackTaskCollection.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            push_integration_group_ref_id=push_integration_group_ref_id,
            generation_project_ref_id=generation_project_ref_id)
        return slack_task_collection

    def change_generation_project(
            self, generation_project_ref_id: EntityId, source: EventSource,
            modified_time: Timestamp) -> 'SlackTaskCollection':
        """Change the catch up project."""
        if self.generation_project_ref_id == generation_project_ref_id:
            return self
        return self._new_version(
            generation_project_ref_id=generation_project_ref_id,
            new_event=SlackTaskCollection.ChangeGenerationProjectRefId.make_event_from_frame_args(
                source, self.version, modified_time))

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.push_integration_group_ref_id
