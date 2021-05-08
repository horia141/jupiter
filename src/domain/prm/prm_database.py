"""The personal relationship database."""
from dataclasses import dataclass, field

from models.basic import EntityId, Timestamp
from models.framework import AggregateRoot, Event, UpdateAction, BAD_REF_ID


@dataclass()
class PrmDatabase(AggregateRoot):
    """The personal relationship database."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Create event."""
        catch_up_project_ref_id: EntityId

    @dataclass(frozen=True)
    class ChangeCatchUpProjectRefId(Event):
        """Change catch up project ref id."""
        catch_up_project_ref_id: UpdateAction[EntityId] = field(default_factory=UpdateAction.do_nothing)

    _catch_up_project_ref_id: EntityId

    @staticmethod
    def new_prm_database(catch_up_project_ref_id: EntityId, created_time: Timestamp) -> 'PrmDatabase':
        """Create a new personal database."""
        person = PrmDatabase(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _catch_up_project_ref_id=catch_up_project_ref_id)
        person.record_event(PrmDatabase.Created(
            catch_up_project_ref_id=catch_up_project_ref_id, timestamp=created_time))
        return person

    def change_catch_up_project_ref_id(
            self, catch_up_project_ref_id: EntityId, modified_time: Timestamp) -> 'PrmDatabase':
        """Change the catch up project."""
        if self._catch_up_project_ref_id == catch_up_project_ref_id:
            return self
        self._catch_up_project_ref_id = catch_up_project_ref_id
        self.record_event(PrmDatabase.ChangeCatchUpProjectRefId(
            catch_up_project_ref_id=UpdateAction.change_to(catch_up_project_ref_id), timestamp=modified_time))
        return self

    @property
    def catch_up_project_ref_id(self) -> EntityId:
        """The catch up project where catch up tasks are generated."""
        return self._catch_up_project_ref_id
