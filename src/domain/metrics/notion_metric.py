"""A metric on Notion-side."""
from dataclasses import dataclass

from domain.entity_name import EntityName
from domain.metrics.metric import Metric
from domain.timestamp import Timestamp
from models.framework import NotionEntity, BAD_NOTION_ID


@dataclass(frozen=True)
class NotionMetric(NotionEntity[Metric]):
    """A metric on Notion-side."""

    name: str

    @staticmethod
    def new_notion_row(aggregate_root: Metric) -> 'NotionMetric':
        """Construct a new Notion row from a given aggregate root."""
        return NotionMetric(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            name=str(aggregate_root.name))

    def join_with_aggregate_root(self, aggregate_root: Metric) -> 'NotionMetric':
        """Add to this Notion row from a given aggregate root."""
        return NotionMetric(
            notion_id=self.notion_id,
            ref_id=aggregate_root.ref_id,
            name=str(aggregate_root.name))

    def apply_to_aggregate_root(self, aggregate_root: Metric, modification_time: Timestamp) -> Metric:
        """Obtain the aggregate root form of this, with a possible error."""
        workspace_name = EntityName.from_raw(self.name)
        aggregate_root.change_name(workspace_name, modification_time)
        return aggregate_root
