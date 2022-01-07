"""A vacation on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_name import VacationName
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionVacation(NotionRow[Vacation, None, None]):
    """A vacation on Notion-side."""

    name: str
    start_date: Optional[ADate]
    end_date: Optional[ADate]

    @staticmethod
    def new_notion_row(aggregate_root: Vacation, extra_info: None) -> 'NotionVacation':
        """Construct a new Notion row from a given vacation."""
        return NotionVacation(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            name=str(aggregate_root.name),
            archived=aggregate_root.archived,
            start_date=aggregate_root.start_date,
            end_date=aggregate_root.end_date)

    def new_aggregate_root(self, extra_info: None) -> Vacation:
        """Create a new vacation from this."""
        vacation_name = VacationName.from_raw(self.name)
        if self.start_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have a start date")
        if self.end_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have an end date")
        return Vacation.new_vacation(
            archived=self.archived,
            name=vacation_name,
            start_date=self.start_date,
            end_date=self.end_date,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: Vacation, extra_info: None) -> Vacation:
        """Apply to an already existing vacation."""
        vacation_name = VacationName.from_raw(self.name)
        if self.start_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have a start date")
        if self.end_date is None:
            raise InputValidationError(f"Vacation '{self.name}' should have an end date")
        aggregate_root.update(
            name=UpdateAction.change_to(vacation_name),
            start_date=UpdateAction.change_to(self.start_date),
            end_date=UpdateAction.change_to(self.end_date),
            source=EventSource.NOTION,
            modification_time=self.last_edited_time)
        aggregate_root.change_archived(
            archived=self.archived, source=EventSource.NOTION, archived_time=self.last_edited_time)
        return aggregate_root
