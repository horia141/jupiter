"""A habit collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.habits.habit_collection import HabitCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionHabitCollection(NotionTrunkEntity[HabitCollection]):
    """A habit collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: HabitCollection) -> "NotionHabitCollection":
        """Construct a new Notion row from a given entity."""
        return NotionHabitCollection(notion_id=BAD_NOTION_ID, ref_id=entity.ref_id)
