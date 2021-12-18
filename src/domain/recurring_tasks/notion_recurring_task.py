"""A recurring task on Notion-side."""
from dataclasses import dataclass
from typing import Optional, List

from domain.adate import ADate
from domain.difficulty import Difficulty
from domain.eisen import Eisen
from domain.entity_name import EntityName
from domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from domain.recurring_task_gen_params import RecurringTaskGenParams
from domain.recurring_task_period import RecurringTaskPeriod
from domain.recurring_task_skip_rule import RecurringTaskSkipRule
from domain.recurring_task_type import RecurringTaskType
from domain.recurring_tasks.recurring_task import RecurringTask
from models.framework import NotionRow2, EntityId, BAD_NOTION_ID


@dataclass()
class NotionRecurringTask(NotionRow2[RecurringTask, None, 'NotionRecurringTask.InverseExtraInfo']):
    """A recurring task on Notion-side."""

    @dataclass(frozen=True)
    class InverseExtraInfo:
        """Info when copying from Notion to app side."""
        project_ref_id: EntityId
        recurring_task_collection_ref_id: EntityId

    name: str
    archived: bool
    period: Optional[str]
    the_type: Optional[str]
    eisen: Optional[List[str]]
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
            period=aggregate_root.period.for_notion(),
            the_type=aggregate_root.the_type.for_notion(),
            eisen=[e.for_notion() for e in aggregate_root.gen_params.eisen],
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

    def join_with_aggregate_root(self, aggregate_root: RecurringTask, extra_info: None) -> 'NotionRecurringTask':
        """Construct a Notion row from this and a recurring task."""
        return NotionRecurringTask(
            notion_id=self.notion_id,
            ref_id=str(aggregate_root.ref_id),
            last_edited_time=aggregate_root.last_modified_time,
            archived=aggregate_root.archived,
            name=str(aggregate_root.name),
            period=aggregate_root.period.for_notion(),
            the_type=aggregate_root.the_type.for_notion(),
            eisen=[e.for_notion() for e in aggregate_root.gen_params.eisen],
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
            name=EntityName.from_raw(self.name),
            period=RecurringTaskPeriod.from_raw(self.period),
            the_type=RecurringTaskType.from_raw(self.the_type),
            gen_params=RecurringTaskGenParams(
                project_ref_id=extra_info.project_ref_id,
                period=RecurringTaskPeriod.from_raw(self.period),
                eisen=[Eisen.from_raw(e) for e in self.eisen] if self.eisen else [],
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
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: RecurringTask, extra_info: InverseExtraInfo) -> RecurringTask:
        """Apply to an already existing recurring task."""
        recurring_task_period = RecurringTaskPeriod.from_raw(self.period)
        aggregate_root.change_archived(self.archived, self.last_edited_time)
        aggregate_root.change_name(EntityName.from_raw(self.name), self.last_edited_time)
        aggregate_root.change_period(RecurringTaskPeriod.from_raw(self.period), self.last_edited_time)
        aggregate_root.change_type(RecurringTaskType.from_raw(self.the_type), self.last_edited_time)
        aggregate_root.change_gen_params(
            RecurringTaskGenParams(
                project_ref_id=extra_info.project_ref_id,
                period=RecurringTaskPeriod.from_raw(self.period),
                eisen=[Eisen.from_raw(e) for e in self.eisen] if self.eisen else [],
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
            self.last_edited_time)
        aggregate_root.change_must_do(self.must_do, self.last_edited_time)
        aggregate_root.change_skip_rule(
            RecurringTaskSkipRule.from_raw(self.skip_rule) if self.skip_rule else None, self.last_edited_time)
        aggregate_root.change_active_interval(
            self.start_at_date or aggregate_root.start_at_date,
            self.end_at_date,
            self.last_edited_time)
        return aggregate_root
