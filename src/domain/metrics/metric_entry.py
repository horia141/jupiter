"""A metric entry."""
from dataclasses import dataclass, field
from typing import Optional

from models.basic import ADate, Timestamp
from models.framework import AggregateRoot, Event, UpdateAction, EntityId, BAD_REF_ID


@dataclass()
class MetricEntry(AggregateRoot):
    """A metric entry."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        metric_ref_id: EntityId
        collection_time: ADate
        value: float
        notes: Optional[str]
        archived: bool

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        collection_time: UpdateAction[ADate] = field(default_factory=UpdateAction.do_nothing)
        value: UpdateAction[float] = field(default_factory=UpdateAction.do_nothing)
        notes: UpdateAction[Optional[str]] = field(default_factory=UpdateAction.do_nothing)

    _metric_ref_id: EntityId
    _collection_time: ADate
    _value: float
    _notes: Optional[str]

    @staticmethod
    def new_metric_entry(
            archived: bool, metric_ref_id: EntityId, collection_time: ADate, value: float, notes: Optional[str],
            created_time: Timestamp) -> 'MetricEntry':
        """Create a metric entry."""
        metric_entry = MetricEntry(
            _ref_id=BAD_REF_ID,
            _archived=archived,
            _created_time=created_time,
            _archived_time=created_time if archived else None,
            _last_modified_time=created_time,
            _events=[],
            _metric_ref_id=metric_ref_id,
            _collection_time=collection_time,
            _value=value,
            _notes=notes)
        metric_entry.record_event(
            MetricEntry.Created(
                timestamp=created_time, metric_ref_id=metric_ref_id, collection_time=collection_time,
                value=value, notes=notes, archived=archived))
        return metric_entry

    def change_collection_time(self, collection_time: ADate, modification_time: Timestamp) -> 'MetricEntry':
        """Change the collection time for the metric entry."""
        if self._collection_time == collection_time:
            return self
        self._collection_time = collection_time
        self.record_event(MetricEntry.Updated(
            collection_time=UpdateAction.change_to(collection_time), timestamp=modification_time))
        return self

    def change_value(self, value: float, modification_time: Timestamp) -> 'MetricEntry':
        """Change the value for the metric entry."""
        if self._value == value:
            return self
        self._value = value
        self.record_event(MetricEntry.Updated(
            value=UpdateAction.change_to(value), timestamp=modification_time))
        return self

    def change_notes(self, notes: Optional[str], modification_time: Timestamp) -> 'MetricEntry':
        """Change the value for the metric entry."""
        if self._notes == notes:
            return self
        self._notes = notes
        self.record_event(MetricEntry.Updated(
            notes=UpdateAction.change_to(notes), timestamp=modification_time))
        return self

    @property
    def metric_ref_id(self) -> EntityId:
        """The ref id of the owning metric."""
        return self._metric_ref_id

    @property
    def collection_time(self) -> ADate:
        """The collection time of the metric entry."""
        return self._collection_time

    @property
    def value(self) -> float:
        """The value of the metric entry."""
        return self._value

    @property
    def notes(self) -> Optional[str]:
        """The notes for the metric entry."""
        return self._notes
