"""A vacation on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionVacation(NotionRow[Vacation, None, 'NotionVacation.InverseInfo']):
    """A vacation on Notion-side."""

    @dataclass(frozen=True)
    class InverseInfo:
        """Extra info for the Notion to app copy."""
        vacation_collection_ref_id: EntityId

    name: str
    start_date: Optional[ADate]
    end_date: Optional[ADate]

    @staticmethod
    def new_notion_row(entity: Vacation, extra_info: None) -> 'NotionVacation':
        """Construct a new Notion row from a given vacation."""
        return NotionVacation(
            notion_id=BAD_NOTION_ID,
            ref_id=entity.ref_id,
            last_edited_time=entity.last_modified_time,
            name=str(entity.name),
            archived=entity.archived,
            start_date=entity.start_date,
            end_date=entity.end_date)

    def new_entity(self, extra_info: InverseInfo) -> Vacation:
        """Create a new vacation from this."""
        vacation_name = VacationName.from_raw(self.name)
        if self.start_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have a start date")
        if self.end_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have an end date")
        return Vacation.new_vacation(
            archived=self.archived,
            vacation_collection_ref_id=extra_info.vacation_collection_ref_id,
            name=vacation_name,
            start_date=self.start_date,
            end_date=self.end_date,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_entity(self, entity: Vacation, extra_info: InverseInfo) -> Vacation:
        """Apply to an already existing vacation."""
        vacation_name = VacationName.from_raw(self.name)
        if self.start_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have a start date")
        if self.end_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have an end date")
        return entity\
            .update(
                name=UpdateAction.change_to(vacation_name),
                start_date=UpdateAction.change_to(self.start_date),
                end_date=UpdateAction.change_to(self.end_date),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time)\
            .change_archived(
                archived=self.archived, source=EventSource.NOTION, archived_time=self.last_edited_time)
