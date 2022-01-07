"""The personal relationship database."""
from dataclasses import dataclass

from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import EntityId, BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource


@dataclass()
class PrmDatabase(AggregateRoot):
    """The personal relationship database."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Create event."""

    @dataclass(frozen=True)
    class ChangeCatchUpProjectRefId(AggregateRoot.Updated):
        """Change catch up project ref id."""

    catch_up_project_ref_id: EntityId

    @staticmethod
    def new_prm_database(
            catch_up_project_ref_id: EntityId, source: EventSource, created_time: Timestamp) -> 'PrmDatabase':
        """Create a new personal database."""
        prm_database = PrmDatabase(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[],
            catch_up_project_ref_id=catch_up_project_ref_id)
        prm_database.record_event(
            PrmDatabase.Created.make_event_from_frame_args(source, prm_database.version, created_time))
        return prm_database

    def change_catch_up_project(
            self, catch_up_project_ref_id: EntityId, source: EventSource, modified_time: Timestamp) -> 'PrmDatabase':
        """Change the catch up project."""
        if self.catch_up_project_ref_id == catch_up_project_ref_id:
            return self
        self.catch_up_project_ref_id = catch_up_project_ref_id
        self.record_event(
            PrmDatabase.ChangeCatchUpProjectRefId.make_event_from_frame_args(source, self.version, modified_time))
        return self
