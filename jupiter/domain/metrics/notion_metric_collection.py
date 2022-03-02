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
    def new_notion_row(entity: MetricCollection) -> 'NotionMetricCollection':
        """Construct a new Notion row from a given entity."""
        return NotionMetricCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: MetricCollection, modification_time: Timestamp) -> MetricCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity
