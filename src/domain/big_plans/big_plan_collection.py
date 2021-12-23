"""A big plan collection."""
from dataclasses import dataclass

from domain.timestamp import Timestamp
from framework.aggregate_root import AggregateRoot
from framework.entity_id import EntityId, BAD_REF_ID
from framework.event import Event2


@dataclass()
class BigPlanCollection(AggregateRoot):
    """A big plan collection."""

    @dataclass(frozen=True)
    class Created(Event2):
        """Created event."""

    _project_ref_id: EntityId

    @staticmethod
    def new_big_plan_collection(project_ref_id: EntityId, created_time: Timestamp) -> 'BigPlanCollection':
        """Create a big plan collection."""
        big_plan_collection = BigPlanCollection(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _project_ref_id=project_ref_id)
        big_plan_collection.record_event(Event2.make_event_from_frame_args(BigPlanCollection.Created, created_time))

        return big_plan_collection

    @property
    def project_ref_id(self) -> EntityId:
        """The project which owns this collection."""
        return self._project_ref_id
