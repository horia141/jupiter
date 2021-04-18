"""A person on Notion-side."""
from dataclasses import dataclass
from typing import Optional, List

from domain.prm.person import Person
from models.framework import NotionRow


@dataclass(frozen=True)
class NotionPerson(NotionRow[Person]):
    """A person on Notion-side."""

    name: str
    archived: bool
    relationship: Optional[str]
    period: Optional[str]
    eisen: Optional[List[str]]
    difficulty: Optional[str]
    actionable_from_day: Optional[int]
    actionable_from_month: Optional[int]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]
    birthday: Optional[str]

    @staticmethod
    def new_aggregate_root() -> Person:
        """Construct a new aggregate root from this notion row."""

    def apply_from_aggregate_root(self, aggregate_root: Person) -> NotionPerson:
        """Construct a Notion row from a given aggregate root."""
        return NotionPerson(
            notion_id=self.notion_id,
            ref_id=aggregate_root.ref_id,
            last_edited_time=aggregate_root.last_modified_time,
            name=aggregate_root.name,
            archived=aggregate_root.archived,
            relationship=aggregate_root.relationship.value,
            period=aggregate_root.catch_up_params.period.for_notion() if aggregate_root.catch_up_params else None,
            eisen=[e.for_notion() for e in
                   aggregate_root.catch_up_params.eisen] if aggregate_root.catch_up_params and aggregate_root.catch_up_params.eisen else [],
            difficulty=aggregate_root.catch_up_params.difficulty.for_notion() if aggregate_root.catch_up_params and aggregate_root.catch_up_params.difficulty else None,
            actionable_from_day=aggregate_root.catch_up_params.actionable_from_day if aggregate_root.catch_up_params else None,
            actionable_from_month=aggregate_root.catch_up_params.actionable_from_month if aggregate_root.catch_up_params else None,
            due_at_time=aggregate_root.catch_up_params.due_at_time if aggregate_root.catch_up_params else None,
            due_at_day=aggregate_root.catch_up_params.due_at_day if aggregate_root.catch_up_params else None,
            due_at_month=aggregate_root.catch_up_params.due_at_month if aggregate_root.catch_up_params else None,
            birthday=str(aggregate_root.birthday))

    def apply_to_aggregate_root(self, aggregate_root: Person) -> Person:
        """Obtain the aggregate root form of this, with a possible error."""
        raise NotImplementedError("Can't use a base NotionRow class.")
