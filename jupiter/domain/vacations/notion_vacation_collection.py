"""A vacation collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.notion import NotionTrunkEntity


@dataclass(frozen=True)
class NotionVacationCollection(NotionTrunkEntity[VacationCollection]):
    """A vacation collection on Notion-side."""

    @staticmethod
    def new_notion_entity(entity: VacationCollection) -> 'NotionVacationCollection':
        """Construct a new Notion row from a given entity."""
        return NotionVacationCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)
