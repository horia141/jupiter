"""A metric."""
from dataclasses import dataclass
from typing import Optional

from jupiter.core.domain.entity_icon import EntityIcon
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.framework.base.entity_id import BAD_REF_ID, EntityId
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, BranchEntity, Entity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class Metric(BranchEntity):
    """A metric."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Updated(Entity.Updated):
        """Updated event."""

    metric_collection_ref_id: EntityId
    name: MetricName
    icon: Optional[EntityIcon] = None
    collection_params: Optional[RecurringTaskGenParams] = None
    metric_unit: Optional[MetricUnit] = None

    @staticmethod
    def new_metric(
        metric_collection_ref_id: EntityId,
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
                    source,
                    FIRST_VERSION,
                    created_time,
                ),
            ],
            metric_collection_ref_id=metric_collection_ref_id,
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
                source,
                self.version,
                modification_time,
            ),
        )

    @property
    def parent_ref_id(self) -> EntityId:
        """The parent."""
        return self.metric_collection_ref_id
