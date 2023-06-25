"""A collection of email tasks."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, TrunkEntity
from jupiter.core.framework.event import EventSource


@dataclass
class EmailTaskCollection(TrunkEntity):
    """A collection of email tasks."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class ChangeGenerationProjectRefId(Entity.Updated):
        """Change generation project ref id."""

    push_integration_group_ref_id: EntityId
    generation_project_ref_id: EntityId

    @staticmethod
    def new_email_task_collection(
        push_integration_group_ref_id: EntityId,
        generation_project_ref_id: EntityId,
        source: EventSource,
        created_time: Timestamp,
    ) -> "EmailTaskCollection":
        """Create a email task collection."""
        email_task_collection = EmailTaskCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                EmailTaskCollection.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            push_integration_group_ref_id=push_integration_group_ref_id,
            generation_project_ref_id=generation_project_ref_id,
        )
        return email_task_collection

    def change_generation_project(
        self,
        generation_project_ref_id: EntityId,
        source: EventSource,
        modified_time: Timestamp,
    ) -> "EmailTaskCollection":
        """Change the generation project."""
        if self.generation_project_ref_id == generation_project_ref_id:
            return self
        return self._new_version(
            generation_project_ref_id=generation_project_ref_id,
            new_event=EmailTaskCollection.ChangeGenerationProjectRefId.make_event_from_frame_args(
                source,
                self.version,
                modified_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.push_integration_group_ref_id
