"""A metric on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.entity_icon import EntityIcon
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_name import MetricName
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionBranchEntity
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionMetric(NotionBranchEntity[Metric]):
    """A metric on Notion-side."""

    name: str
    icon: Optional[str]

    @staticmethod
    def new_notion_entity(entity: Metric) -> 'NotionMetric':
        """Construct a new Notion row from a given entity."""
        return NotionMetric(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            name=str(entity.name),
            icon=entity.icon.to_safe() if entity.icon else None)

    def apply_to_entity(self, entity: Metric, modification_time: Timestamp) -> Metric:
        """Obtain the entity form of this, with a possible error."""
        name = MetricName.from_raw(self.name)
        icon = EntityIcon.from_safe(self.icon) if self.icon else None
        return entity.update(
            name=UpdateAction.change_to(name),
            icon=UpdateAction.change_to(icon),
            collection_params=UpdateAction.do_nothing(),
            source=EventSource.NOTION,
            modification_time=
            modification_time
            if (name != entity.name or icon != entity.icon)
            else entity.last_modified_time)
