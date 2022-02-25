"""A metric collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionMetricCollection(NotionEntity[MetricCollection]):
    """A metric collection on Notion-side."""

    @staticmethod
    def new_notion_row(aggregate_root: MetricCollection) -> 'NotionMetricCollection':
        """Construct a new Notion row from a given aggregate root."""
        return NotionMetricCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id)

    def apply_to_aggregate_root(
            self, aggregate_root: MetricCollection, modification_time: Timestamp) -> MetricCollection:
        """Obtain the aggregate root form of this, with a possible error."""
        return aggregate_root
