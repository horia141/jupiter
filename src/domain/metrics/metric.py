"""A metric."""
from dataclasses import dataclass, field
from typing import Optional, List

from models.basic import MetricKey, RecurringTaskPeriod, MetricUnit, Timestamp, EntityName, EntityId, Eisen, Difficulty
from models.framework import AggregateRoot, Event, UpdateAction, BAD_REF_ID


@dataclass()
class MetricCollectionParams:
    """Parameters for metric collection."""

    project_ref_id: EntityId
    period: RecurringTaskPeriod
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    actionable_from_day: Optional[int]
    actionable_from_month: Optional[int]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]


@dataclass()
class Metric(AggregateRoot):
    """A metric."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""
        key: MetricKey
        name: EntityName
        collection_params: Optional[MetricCollectionParams]
        metric_unit: Optional[MetricUnit]

    @dataclass(frozen=True)
    class Updated(Event):
        """Updated event."""
        name: UpdateAction[EntityName] = field(default_factory=UpdateAction.do_nothing)
        collection_params: UpdateAction[Optional[MetricCollectionParams]] \
            = field(default_factory=UpdateAction.do_nothing)

    _key: MetricKey
    _name: EntityName
    _collection_params: Optional[MetricCollectionParams]
    _metric_unit: Optional[MetricUnit]

    @staticmethod
    def new_metric(
            key: MetricKey, name: EntityName, collection_params: Optional[MetricCollectionParams],
            metric_unit: Optional[MetricUnit], created_time: Timestamp) -> 'Metric':
        """Create a metric."""
        metric = Metric(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            _key=key,
            _name=name,
            _collection_params=collection_params,
            _metric_unit=metric_unit)
        metric.record_event(Metric.Created(
            key=key, name=name, collection_params=collection_params, metric_unit=metric_unit, timestamp=created_time))

        return metric

    def change_name(self, name: EntityName, modification_time: Timestamp) -> 'Metric':
        """Change the name of the metric."""
        if self._name == name:
            return self
        self._name = name
        self.record_event(Metric.Updated(name=UpdateAction.change_to(name), timestamp=modification_time))
        return self

    def change_collection_params(
            self, collection_params: Optional[MetricCollectionParams], modification_time: Timestamp) -> 'Metric':
        """Change the collection period of the metric."""
        if self._collection_params == collection_params:
            return self
        self._collection_params = collection_params
        self.record_event(
            Metric.Updated(
                collection_params=UpdateAction.change_to(collection_params), timestamp=modification_time))
        return self

    @property
    def key(self) -> MetricKey:
        """The key of the metric."""
        return self._key

    @property
    def name(self) -> EntityName:
        """The name of the metric."""
        return self._name

    @property
    def collection_params(self) -> Optional[MetricCollectionParams]:
        """The collection parameters of the metric."""
        return self._collection_params

    @property
    def metric_unit(self) -> Optional[MetricUnit]:
        """The metric unit of the metric."""
        return self._metric_unit
