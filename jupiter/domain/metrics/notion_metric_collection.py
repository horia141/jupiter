"""A metric collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionMetricCollection(NotionTrunkEntity[MetricCollection]):
    """A metric collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: MetricCollection) -> "NotionMetricCollection":
        """Construct a new Notion row from a given entity."""
        return NotionMetricCollection(notion_id=BAD_NOTION_ID, ref_id=entity.ref_id)
