"""A recurring task on Notion-side."""
from dataclasses import dataclass
from typing import Optional

from jupiter.domain.adate import ADate
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.domain.recurring_task_type import RecurringTaskType
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.recurring_tasks.recurring_task_name import RecurringTaskName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction


@dataclass(frozen=True)
class NotionRecurringTask(NotionRow[RecurringTask, None, 'NotionRecurringTask.InverseExtraInfo']):
    """A recurring task on Notion-side."""

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Info when copying from Notion to app side."""
        project_ref_id: EntityId
        recurring_task_collection_ref_id: EntityId

    name: str
    period: Optional[str]
    the_type: Optional[str]
    eisen: Optional[str]
    difficulty: Optional[str]
    actionable_from_day: Optional[int]
    actionable_from_month: Optional[int]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]
    suspended: bool
    skip_rule: Optional[str]
    must_do: bool
    start_at_date: Optional[ADate]
    end_at_date: Optional[ADate]

    @staticmethod
    def new_notion_row(aggregate_root: RecurringTask, extra_info: None) -> 'NotionRecurringTask':
        """Construct a new Notion row from a given recurring task."""
        return NotionRecurringTask(
            notion_id=BAD_NOTION_ID,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            archived=aggregate_root.archived,
            name=str(aggregate_root.name),
            period=aggregate_root.gen_params.period.for_notion(),
            the_type=aggregate_root.the_type.for_notion(),
            eisen=aggregate_root.gen_params.eisen.for_notion(),
            difficulty=
            aggregate_root.gen_params.difficulty.for_notion() if aggregate_root.gen_params.difficulty else None,
            actionable_from_day=
            aggregate_root.gen_params.actionable_from_day.as_int()
            if aggregate_root.gen_params.actionable_from_day else None,
            actionable_from_month=
            aggregate_root.gen_params.actionable_from_month.as_int()
            if aggregate_root.gen_params.actionable_from_month else None,
            due_at_time=str(aggregate_root.gen_params.due_at_time) if aggregate_root.gen_params.due_at_time else None,
            due_at_day=aggregate_root.gen_params.due_at_day.as_int() if aggregate_root.gen_params.due_at_day else None,
            due_at_month=
            aggregate_root.gen_params.due_at_month.as_int() if aggregate_root.gen_params.due_at_month else None,
            skip_rule=str(aggregate_root.skip_rule),
            must_do=aggregate_root.must_do,
            start_at_date=aggregate_root.start_at_date,
            end_at_date=aggregate_root.end_at_date,
            suspended=aggregate_root.suspended)

    def new_aggregate_root(self, extra_info: InverseExtraInfo) -> RecurringTask:
        """Create a new recurring task from this."""
        recurring_task_period = RecurringTaskPeriod.from_raw(self.period)
        return RecurringTask.new_recurring_task(
            recurring_task_collection_ref_id=extra_info.recurring_task_collection_ref_id,
            archived=self.archived,
            name=RecurringTaskName.from_raw(self.name),
            the_type=RecurringTaskType.from_raw(self.the_type),
            gen_params=RecurringTaskGenParams(
                project_ref_id=extra_info.project_ref_id,
                period=RecurringTaskPeriod.from_raw(self.period),
                eisen=Eisen.from_raw(self.eisen) if self.eisen else Eisen.REGULAR,
                difficulty=Difficulty.from_raw(self.difficulty) if self.difficulty else None,
                actionable_from_day=
                RecurringTaskDueAtDay.from_raw(recurring_task_period, self.actionable_from_day)
                if self.actionable_from_day else None,
                actionable_from_month=
                RecurringTaskDueAtMonth.from_raw(recurring_task_period, self.actionable_from_month)
                if self.actionable_from_month else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(self.due_at_time) if self.due_at_time else None,
                due_at_day=
                RecurringTaskDueAtDay.from_raw(recurring_task_period, self.due_at_day) if self.due_at_day else None,
                due_at_month=
                RecurringTaskDueAtMonth.from_raw(recurring_task_period, self.due_at_month)
                if self.due_at_month else None),
            suspended=self.suspended,
            skip_rule=RecurringTaskSkipRule.from_raw(self.skip_rule) if self.skip_rule else None,
            must_do=self.must_do,
            start_at_date=self.start_at_date,
            end_at_date=self.end_at_date,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: RecurringTask, extra_info: InverseExtraInfo) -> RecurringTask:
        """Apply to an already existing recurring task."""
        recurring_task_period = RecurringTaskPeriod.from_raw(self.period)
        new_aggregate_root = aggregate_root\
            .update(
                name=UpdateAction.change_to(RecurringTaskName.from_raw(self.name)),
                the_type=UpdateAction.change_to(RecurringTaskType.from_raw(self.the_type)),
                gen_params=UpdateAction.change_to(
                    RecurringTaskGenParams(
                        project_ref_id=extra_info.project_ref_id,
                        period=RecurringTaskPeriod.from_raw(self.period),
                        eisen=Eisen.from_raw(self.eisen) if self.eisen else Eisen.REGULAR,
                        difficulty=Difficulty.from_raw(self.difficulty) if self.difficulty else None,
                        actionable_from_day=
                        RecurringTaskDueAtDay.from_raw(recurring_task_period, self.actionable_from_day)
                        if self.actionable_from_day else None,
                        actionable_from_month=
                        RecurringTaskDueAtMonth.from_raw(recurring_task_period, self.actionable_from_month)
                        if self.actionable_from_month else None,
                        due_at_time=RecurringTaskDueAtTime.from_raw(self.due_at_time) if self.due_at_time else None,
                        due_at_day=
                        RecurringTaskDueAtDay.from_raw(recurring_task_period, self.due_at_day)
                        if self.due_at_day else None,
                        due_at_month=
                        RecurringTaskDueAtMonth.from_raw(recurring_task_period, self.due_at_month)
                        if self.due_at_month else None)),
                must_do=UpdateAction.change_to(self.must_do),
                skip_rule=UpdateAction.change_to(
                    RecurringTaskSkipRule.from_raw(self.skip_rule) if self.skip_rule else None),
                start_at_date=UpdateAction.change_to(
                    self.start_at_date if self.start_at_date else aggregate_root.start_at_date),
                end_at_date=UpdateAction.change_to(self.end_at_date),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time)
        if self.suspended:
            new_aggregate_root = new_aggregate_root\
               .suspend(source=EventSource.NOTION, modification_time=self.last_edited_time)
        else:
            new_aggregate_root = new_aggregate_root\
                .unsuspend(source=EventSource.NOTION, modification_time=self.last_edited_time)
        return new_aggregate_root.change_archived(
            archived=self.archived, source=EventSource.NOTION, archived_time=self.last_edited_time)
