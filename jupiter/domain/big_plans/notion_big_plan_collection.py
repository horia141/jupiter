"""A big plan collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionBigPlanCollection(NotionTrunkEntity[BigPlanCollection]):
    """A big plan collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: BigPlanCollection) -> "NotionBigPlanCollection":
        """Construct a new Notion row from a given entity."""
        return NotionBigPlanCollection(notion_id=BAD_NOTION_ID, ref_id=entity.ref_id)
