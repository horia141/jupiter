"""A metric entry."""
from jupiter.core.domain.core.adate import ADate
from jupiter.core.domain.core.entity_name import EntityName
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_domain import NoteDomain
from jupiter.core.framework.base.entity_id import EntityId
from jupiter.core.framework.context import DomainContext
from jupiter.core.framework.entity import (
    IsRefId,
    LeafEntity,
    OwnsAtMostOne,
    ParentLink,
    create_entity_action,
    entity,
    update_entity_action,
)
from jupiter.core.framework.update_action import UpdateAction


@entity
class MetricEntry(LeafEntity):
    """A metric entry."""

    metric: ParentLink
    collection_time: ADate
    value: float

    note = OwnsAtMostOne(
        Note, domain=NoteDomain.METRIC_ENTRY, source_entity_ref_id=IsRefId()
    )

    @staticmethod
    @create_entity_action
    def new_metric_entry(
        ctx: DomainContext,
        metric_ref_id: EntityId,
        collection_time: ADate,
        value: float,
    ) -> "MetricEntry":
        """Create a metric entry."""
        return MetricEntry._create(
            ctx,
            name=MetricEntry.build_name(collection_time, value),
            metric=ParentLink(metric_ref_id),
            collection_time=collection_time,
            value=value,
        )

    @update_entity_action
    def update(
        self,
        ctx: DomainContext,
        collection_time: UpdateAction[ADate],
        value: UpdateAction[float],
    ) -> "MetricEntry":
        """Change the metric entry."""
        return self._new_version(
            ctx,
            collection_time=collection_time.or_else(self.collection_time),
            value=value.or_else(self.value),
        )

    @staticmethod
    def build_name(collection_time: ADate, value: float) -> EntityName:
        """Construct a name."""
        return EntityName(
            f"Entry for {ADate.to_user_date_str(collection_time)} value={value}",
        )
