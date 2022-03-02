"""A big plan collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionBigPlanCollection(NotionEntity[BigPlanCollection]):
    """A big plan collection on Notion-side."""

    @staticmethod
    def new_notion_row(entity: BigPlanCollection) -> 'NotionBigPlanCollection':
        """Construct a new Notion row from a given entity."""
        return NotionBigPlanCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: BigPlanCollection, modification_time: Timestamp) -> BigPlanCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity
