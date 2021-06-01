"""Shared domain objects."""
from dataclasses import dataclass
from typing import List, Optional

from models.basic import RecurringTaskPeriod, Eisen, Difficulty
from models.framework import EntityId


@dataclass()
class RecurringTaskGenParams:
    """Parameters for metric collection."""

    project_ref_id: EntityId
    period: RecurringTaskPeriod
    eisen: List[Eisen]
    difficulty: Optional[Difficulty]
    actionable_from_day: Optional[int]
    actionable_from_month: Optional[int]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]

    def with_new_project_ref_id(self, project_ref_id: EntityId) -> 'RecurringTaskGenParams':
        """Return a new params object, with the project changed to the argument."""
        return RecurringTaskGenParams(
            project_ref_id=project_ref_id,
            period=self.period,
            eisen=list(self.eisen),
            difficulty=self.difficulty,
            actionable_from_day=self.actionable_from_day,
            actionable_from_month=self.actionable_from_month,
            due_at_time=self.due_at_time,
            due_at_day=self.due_at_day,
            due_at_month=self.due_at_month)
