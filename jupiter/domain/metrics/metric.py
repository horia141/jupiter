"""A metric."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.metrics.metric_unit import MetricUnit
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.framework.aggregate_root import AggregateRoot, FIRST_VERSION
from jupiter.framework.base.entity_id import BAD_REF_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
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
            metric_unit: Optional[MetricUnit], source: EventSource, created_time: Timestamp) -> 'Metric':
        """Create a metric."""
        metric = Metric(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[Metric.Created.make_event_from_frame_args(source, FIRST_VERSION, created_time)],
            key=key,
            name=name,
            collection_params=collection_params,
            metric_unit=metric_unit)
        return metric

    def update(
            self, name: UpdateAction[MetricName], collection_params: UpdateAction[Optional[RecurringTaskGenParams]],
            source: EventSource, modification_time: Timestamp) -> 'Metric':
        """Change the metric."""
        return self._new_version(
            name=name.or_else(self.name),
            collection_params=collection_params.or_else(self.collection_params),
            new_event=Metric.Updated.make_event_from_frame_args(source, self.version, modification_time))
