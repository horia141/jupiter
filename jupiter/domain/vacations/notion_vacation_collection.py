"""A vacation collection on Notion-side."""
from dataclasses import dataclass

from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.notion import NotionEntity
from jupiter.framework.base.notion_id import BAD_NOTION_ID


@dataclass(frozen=True)
class NotionVacationCollection(NotionEntity[VacationCollection]):
    """A vacation collection on Notion-side."""

    @staticmethod
    def new_notion_row(entity: VacationCollection) -> 'NotionVacationCollection':
        """Construct a new Notion row from a given entity."""
        return NotionVacationCollection(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id)

    def apply_to_entity(
            self, entity: VacationCollection, modification_time: Timestamp) -> VacationCollection:
        """Obtain the entity form of this, with a possible error."""
        return entity
