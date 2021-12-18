"""A vacation on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from domain.adate import ADate
from domain.entity_name import EntityName
from domain.errors import ServiceValidationError
from domain.vacations.vacation import Vacation
from models.framework import NotionRow, BAD_NOTION_ID


@dataclass()
class NotionVacation(NotionRow[Vacation, None]):
    """A vacation on Notion-side."""

    name: str
    archived: bool
    start_date: Optional[ADate]
    end_date: Optional[ADate]

    @staticmethod
    def new_notion_row(aggregate_root: Vacation) -> 'NotionVacation':
        """Construct a new Notion row from a given vacation."""
        return NotionVacation(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            name=str(aggregate_root.name),
            archived=aggregate_root.archived,
            start_date=aggregate_root.start_date,
            end_date=aggregate_root.end_date)

    def join_with_aggregate_root(self, aggregate_root: Vacation) -> 'NotionVacation':
        """Construct a Notion row from this and a vacation."""
        return NotionVacation(
            notion_id=self.notion_id,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            name=str(aggregate_root.name),
            archived=aggregate_root.archived,
            start_date=aggregate_root.start_date,
            end_date=aggregate_root.end_date)

    def new_aggregate_root(self, extra_info: None) -> Vacation:
        """Create a new vacation from this."""
        vacation_name = EntityName.from_raw(self.name)
        if self.start_date is None:
            raise ServiceValidationError(f"Vacation '{self.name}' should have a start date")
        if self.end_date is None:
            raise ServiceValidationError(f"Vacation '{self.name}' should have an end date")
        return Vacation.new_vacation(
            archived=self.archived,
            name=vacation_name,
            start_date=self.start_date,
            end_date=self.end_date,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: Vacation, extra_info: None) -> Vacation:
        """Apply to an already existing vacation."""
        vacation_name = EntityName.from_raw(self.name)
        if self.start_date is None:
            raise ServiceValidationError(f"Vacation '{self.name}' should have a start date")
        if self.end_date is None:
            raise ServiceValidationError(f"Vacation '{self.name}' should have an end date")
        aggregate_root.change_archived(self.archived, self.last_edited_time)
        aggregate_root.change_name(vacation_name, self.last_edited_time)
        aggregate_root.change_start_date(self.start_date, self.last_edited_time)
        aggregate_root.change_end_date(self.end_date, self.last_edited_time)
        return aggregate_root
