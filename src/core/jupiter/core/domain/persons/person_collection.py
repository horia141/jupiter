"""The person collection."""
from dataclasses import dataclass

from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, TrunkEntity
from jupiter.core.framework.event import EventSource


@dataclass
class PersonCollection(TrunkEntity):
    """The personal relationship database."""

    @dataclass
    class Created(Entity.Created):
        """Create event."""

    @dataclass
    class ChangeCatchUpProjectRefId(Entity.Updated):
        """Change catch up project ref id."""

    workspace_ref_id: EntityId
    catch_up_project_ref_id: EntityId

    @staticmethod
    def new_person_collection(
        workspace_ref_id: EntityId,
        catch_up_project_ref_id: EntityId,
        source: EventSource,
        created_time: Timestamp,
    ) -> "PersonCollection":
        """Create a new personal database."""
        person_collection = PersonCollection(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                PersonCollection.Created.make_event_from_frame_args(
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            workspace_ref_id=workspace_ref_id,
            catch_up_project_ref_id=catch_up_project_ref_id,
        )
        return person_collection

    def change_catch_up_project(
        self,
        catch_up_project_ref_id: EntityId,
        source: EventSource,
        modified_time: Timestamp,
    ) -> "PersonCollection":
        """Change the catch up project."""
        if self.catch_up_project_ref_id == catch_up_project_ref_id:
            return self
        return self._new_version(
            catch_up_project_ref_id=catch_up_project_ref_id,
            new_event=PersonCollection.ChangeCatchUpProjectRefId.make_event_from_frame_args(
                source,
                self.version,
                modified_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.workspace_ref_id
