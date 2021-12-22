"""A metric entry on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from domain.adate import ADate
from domain.metrics.metric_entry import MetricEntry
from models.framework import BAD_NOTION_ID, EntityId, NotionRow


@dataclass()
class NotionMetricEntry(NotionRow[MetricEntry, None, EntityId]):
    """A metric entry on Notion-side."""

    archived: bool
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

    def join_with_aggregate_root(self, aggregate_root: MetricEntry, extra_info: None) -> 'NotionMetricEntry':
        """Construct a Notion row from this and a metric entry."""
        return NotionMetricEntry(
            notion_id=self.notion_id,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            collection_time=aggregate_root.collection_time,
            archived=aggregate_root.archived,
            value=aggregate_root.value,
            notes=aggregate_root.notes)

    def new_aggregate_root(self, extra_info: EntityId) -> MetricEntry:
        """Create a new metric entry from this."""
        return MetricEntry.new_metric_entry(
            archived=self.archived,
            metric_ref_id=extra_info,
            collection_time=self.collection_time,
            value=self.value,
            notes=self.notes,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: MetricEntry, extra_info: EntityId) -> MetricEntry:
        """Apply to an already existing metric entry."""
        aggregate_root.change_archived(self.archived, self.last_edited_time)
        aggregate_root.change_collection_time(self.collection_time, self.last_edited_time)
        aggregate_root.change_value(self.value, self.last_edited_time)
        aggregate_root.change_notes(self.notes, self.last_edited_time)
        return aggregate_root
