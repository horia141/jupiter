"""Shared domain objects."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.framework.base.entity_id import EntityId


@dataclass()
class RecurringTaskGenParams:
    """Parameters for metric collection."""

    project_ref_id: EntityId
    period: RecurringTaskPeriod
    eisen: Eisen
    difficulty: Optional[Difficulty]
    actionable_from_day: Optional[RecurringTaskDueAtDay]
    actionable_from_month: Optional[RecurringTaskDueAtMonth]
    due_at_time: Optional[RecurringTaskDueAtTime]
    due_at_day: Optional[RecurringTaskDueAtDay]
    due_at_month: Optional[RecurringTaskDueAtMonth]

    def with_new_project_ref_id(self, project_ref_id: EntityId) -> 'RecurringTaskGenParams':
        """Return a new params object, with the project changed to the argument."""
        return RecurringTaskGenParams(
            project_ref_id=project_ref_id,
            period=self.period,
            eisen=self.eisen,
            difficulty=self.difficulty,
            actionable_from_day=self.actionable_from_day,
            actionable_from_month=self.actionable_from_month,
            due_at_time=self.due_at_time,
            due_at_day=self.due_at_day,
            due_at_month=self.due_at_month)
