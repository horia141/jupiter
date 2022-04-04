"""A metric."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.entity_key import EntityKey
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.domain.metrics.metric_unit import MetricUnit
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.entity import Entity, FIRST_VERSION, BranchEntity
from jupiter.framework.event import EventSource
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class Metric(BranchEntity):
    """A metric."""

    @dataclass(frozen=True)
    class Created(Entity.Created):
        """Created event."""

    @dataclass(frozen=True)
    class Updated(Entity.Updated):
        """Updated event."""

    metric_collection_ref_id: EntityId
    key: MetricKey
    name: MetricName
    icon: Optional[EntityIcon]
    collection_params: Optional[RecurringTaskGenParams]
    metric_unit: Optional[MetricUnit]

    @staticmethod
    def new_metric(
        metric_collection_ref_id: EntityId,
        key: MetricKey,
        name: MetricName,
        icon: Optional[EntityIcon],
        collection_params: Optional[RecurringTaskGenParams],
        metric_unit: Optional[MetricUnit],
        source: EventSource,
        created_time: Timestamp,
    ) -> "Metric":
        """Create a metric."""
        metric = Metric(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            archived_time=None,
            last_modified_time=created_time,
            events=[
                Metric.Created.make_event_from_frame_args(
                    source, FIRST_VERSION, created_time
                )
            ],
            metric_collection_ref_id=metric_collection_ref_id,
            key=key,
            name=name,
            icon=icon,
            collection_params=collection_params,
            metric_unit=metric_unit,
        )
        return metric

    def update(
        self,
        name: UpdateAction[MetricName],
        icon: UpdateAction[Optional[EntityIcon]],
        collection_params: UpdateAction[Optional[RecurringTaskGenParams]],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "Metric":
        """Change the metric."""
        return self._new_version(
            name=name.or_else(self.name),
            icon=icon.or_else(self.icon),
            collection_params=collection_params.or_else(self.collection_params),
            new_event=Metric.Updated.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )

    @property
    def branch_key(self) -> EntityKey:
        """The branch key."""
        return self.key

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.metric_collection_ref_id
