"""A metric entry on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionMetricEntry(NotionRow[MetricEntry, None, 'NotionMetricEntry.InverseExtraInfo']):
    """A metric entry on Notion-side."""

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Inverse info."""
        metric_ref_id: EntityId

    collection_time: ADate
    value: float
    notes: Optional[str]

    @staticmethod
    def new_notion_row(aggregate_root: MetricEntry, extra_info: None) -> 'NotionMetricEntry':
        """Construct a new Notion row from a given metric entry."""
        return NotionMetricEntry(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            archived=aggregate_root.archived,
            collection_time=aggregate_root.collection_time,
            value=aggregate_root.value,
            notes=aggregate_root.notes)

    def new_aggregate_root(self, extra_info: InverseExtraInfo) -> MetricEntry:
        """Create a new metric entry from this."""
        return MetricEntry.new_metric_entry(
            archived=self.archived,
            metric_ref_id=extra_info.metric_ref_id,
            collection_time=self.collection_time,
            value=self.value,
            notes=self.notes,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: MetricEntry, extra_info: InverseExtraInfo) -> MetricEntry:
        """Apply to an already existing metric entry."""
        aggregate_root.update(
            collection_time=UpdateAction.change_to(self.collection_time), value=UpdateAction.change_to(self.value),
            notes=UpdateAction.change_to(self.notes), source=EventSource.NOTION,
            modification_time=self.last_edited_time)
        aggregate_root.change_archived(
            archived=self.archived, source=EventSource.NOTION, archived_time=self.last_edited_time)
        return aggregate_root
