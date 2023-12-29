"""A metric."""
from typing import Optional

from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.metrics.metric_name import MetricName
from jupiter.core.domain.metrics.metric_unit import MetricUnit
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    BranchEntity,
    IsRefId,
    OwnsMany,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class Metric(BranchEntity):
    """A metric."""

    metric_collection: ParentLink
    name: MetricName
    icon: Optional[EntityIcon] = None
    collection_params: Optional[RecurringTaskGenParams] = None
    metric_unit: Optional[MetricUnit] = None

    entries = OwnsMany(MetricEntry, metric_ref_id=IsRefId())
    collection_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.METRIC, metric_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_metric(
        ctx: DomainContext,
        metric_collection_ref_id: EntityId,
        name: MetricName,
        icon: Optional[EntityIcon],
        collection_params: Optional[RecurringTaskGenParams],
        metric_unit: Optional[MetricUnit],
    ) -> "Metric":
        """Create a metric."""
        return Metric._create(
            ctx,
            metric_collection=ParentLink(metric_collection_ref_id),
            name=name,
            icon=icon,
            collection_params=collection_params,
            metric_unit=metric_unit,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        name: UpdateAction[MetricName],
        icon: UpdateAction[Optional[EntityIcon]],
        collection_params: UpdateAction[Optional[RecurringTaskGenParams]],
    ) -> "Metric":
        """Change the metric."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            icon=icon.or_else(self.icon),
            collection_params=collection_params.or_else(self.collection_params),
        )
