"""A metric."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.metrics.metric_unit import MetricUnit
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.framework.aggregate_root import AggregateRoot
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.update_action import UpdateAction


@dataclass()
class Metric(AggregateRoot):
    """A metric."""

    @dataclass(frozen=True)
    class Created(AggregateRoot.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(AggregateRoot.Updated):
        """Updated event."""

    key: MetricKey
    name: MetricName
    collection_params: Optional[RecurringTaskGenParams]
    metric_unit: Optional[MetricUnit]

    @staticmethod
    def new_metric(
            key: MetricKey, name: MetricName, collection_params: Optional[RecurringTaskGenParams],
            metric_unit: Optional[MetricUnit], created_time: Timestamp) -> 'Metric':
        """Create a metric."""
        metric = Metric(
            _ref_id=BAD_REF_ID,
            _archived=False,
            _created_time=created_time,
            _archived_time=None,
            _last_modified_time=created_time,
            _events=[],
            key=key,
            name=name,
            collection_params=collection_params,
            metric_unit=metric_unit)
        metric.record_event(Metric.Created.make_event_from_frame_args(created_time))

        return metric

    def update(
            self, name: UpdateAction[MetricName], collection_params: UpdateAction[Optional[RecurringTaskGenParams]],
            modification_time: Timestamp) -> 'Metric':
        """Change the metric."""
        self.name = name.or_else(self.name)
        self.collection_params = collection_params.or_else(self.collection_params)
        self.record_event(Metric.Updated.make_event_from_frame_args(modification_time))
        return self
