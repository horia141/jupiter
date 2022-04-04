"""A metric entry on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionLeafEntity, NotionLeafApplyToEntityResult
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionMetricEntry(NotionLeafEntity[MetricEntry, None, None]):
    """A metric entry on Notion-side."""

    collection_time: ADate
    value: float
    notes: Optional[str]

    @staticmethod
    def new_notion_entity(entity: MetricEntry, extra_info: None) -> "NotionMetricEntry":
        """Construct a new Notion row from a given metric entry."""
        return NotionMetricEntry(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            archived=entity.archived,
            collection_time=entity.collection_time,
            value=entity.value,
            notes=entity.notes,
        )

    def new_entity(self, parent_ref_id: EntityId, extra_info: None) -> MetricEntry:
        """Create a new metric entry from this."""
        return MetricEntry.new_metric_entry(
            archived=self.archived,
            metric_ref_id=parent_ref_id,
            collection_time=self.collection_time,
            value=self.value,
            notes=self.notes,
            source=EventSource.NOTION,
            created_time=self.last_edited_time,
        )

    def apply_to_entity(
        self, entity: MetricEntry, extra_info: None
    ) -> NotionLeafApplyToEntityResult[MetricEntry]:
        """Apply to an already existing metric entry."""
        return NotionLeafApplyToEntityResult.just(
            entity.update(
                collection_time=UpdateAction.change_to(self.collection_time),
                value=UpdateAction.change_to(self.value),
                notes=UpdateAction.change_to(self.notes),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time,
            ).change_archived(
                archived=self.archived,
                source=EventSource.NOTION,
                archived_time=self.last_edited_time,
            )
        )

    @property
    def nice_name(self) -> str:
        """A nice name for the Notion-side entity."""
        return f"Metric entry for {self.collection_time}"
