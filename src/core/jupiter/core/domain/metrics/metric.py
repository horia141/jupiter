"""A metric."""

from jupiter.core.domain.core.entity_icon import EntityIcon
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
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
    OwnsAtMostOne,
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
    icon: EntityIcon | None = None
    collection_params: RecurringTaskGenParams | None = None
    metric_unit: MetricUnit | None = None

    entries = OwnsMany(MetricEntry, metric_ref_id=IsRefId())
    collection_tasks = OwnsMany(
        InboxTask, source=InboxTaskSource.METRIC, metric_ref_id=IsRefId()
    )
    note = OwnsAtMostOne(Note, domain=NoteDomain.METRIC, source_entity_ref_id=IsRefId())

    @staticmethod
    @create_entity_action
    def new_metric(
        ctx: DomainContext,
        metric_collection_ref_id: EntityId,
        name: MetricName,
        icon: EntityIcon | None,
        collection_params: RecurringTaskGenParams | None,
        metric_unit: MetricUnit | None,
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
        icon: UpdateAction[EntityIcon | None],
        collection_params: UpdateAction[RecurringTaskGenParams | None],
    ) -> "Metric":
        """Change the metric."""
        return self._new_version(
            ctx,
            name=name.or_else(self.name),
            icon=icon.or_else(self.icon),
            collection_params=collection_params.or_else(self.collection_params),
        )
