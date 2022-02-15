"""A habit on Notion-side."""
from dataclasses import dataclass
from typing import Optional, Dict

from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.habits.habit import Habit
from jupiter.domain.habits.habit_name import HabitName
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_name import ProjectName
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_due_at_time import RecurringTaskDueAtTime
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_task_skip_rule import RecurringTaskSkipRule
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction
from jupiter.remote.notion.common import format_name_for_option


@dataclass(frozen=True)
class NotionHabit(
        NotionRow[Habit, 'NotionHabit.DirectInfo', 'NotionHabit.InverseInfo']):
    """A habit on Notion-side."""

    @dataclass(frozen=True)
    class DirectInfo:
        """Info when copying from the app to Notion."""
        project_name: ProjectName

    @dataclass(frozen=True)
    class InverseInfo:
        """Info when copying from Notion to app side."""
        habit_collection_ref_id: EntityId
        default_project: Project
        all_projects_by_name: Dict[str, Project]
        all_projects_map: Dict[EntityId, Project]

    name: str
    period: Optional[str]
    eisen: Optional[str]
    difficulty: Optional[str]
    actionable_from_day: Optional[int]
    actionable_from_month: Optional[int]
    due_at_time: Optional[str]
    due_at_day: Optional[int]
    due_at_month: Optional[int]
    suspended: bool
    skip_rule: Optional[str]
    project_ref_id: Optional[str]
    project_name: Optional[str]

    @staticmethod
    def new_notion_row(aggregate_root: Habit, extra_info: DirectInfo) -> 'NotionHabit':
        """Construct a new Notion row from a given habit."""
        return NotionHabit(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            last_edited_time=aggregate_root.last_modified_time,
            archived=aggregate_root.archived,
            name=str(aggregate_root.name),
            period=aggregate_root.gen_params.period.for_notion(),
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
            suspended=aggregate_root.suspended,
            project_ref_id=str(aggregate_root.project_ref_id),
            project_name=format_name_for_option(extra_info.project_name))

    def new_aggregate_root(self, extra_info: InverseInfo) -> Habit:
        """Create a new habit from this."""
        habit_period = RecurringTaskPeriod.from_raw(self.period)

        project_ref_id = EntityId.from_raw(self.project_ref_id) \
            if self.project_ref_id else None
        project_name = ProjectName.from_raw(self.project_name) \
            if self.project_name else None

        if project_ref_id is not None:
            project = extra_info.all_projects_map[project_ref_id]
        elif project_name is not None:
            project = extra_info.all_projects_by_name[format_name_for_option(project_name)]
        else:
            project = extra_info.default_project

        return Habit.new_habit(
            habit_collection_ref_id=extra_info.habit_collection_ref_id,
            project_ref_id=project.ref_id,
            archived=self.archived,
            name=HabitName.from_raw(self.name),
            gen_params=RecurringTaskGenParams(
                period=RecurringTaskPeriod.from_raw(self.period),
                eisen=Eisen.from_raw(self.eisen) if self.eisen else Eisen.REGULAR,
                difficulty=Difficulty.from_raw(self.difficulty) if self.difficulty else None,
                actionable_from_day=
                RecurringTaskDueAtDay.from_raw(habit_period, self.actionable_from_day)
                if self.actionable_from_day else None,
                actionable_from_month=
                RecurringTaskDueAtMonth.from_raw(habit_period, self.actionable_from_month)
                if self.actionable_from_month else None,
                due_at_time=RecurringTaskDueAtTime.from_raw(self.due_at_time) if self.due_at_time else None,
                due_at_day=
                RecurringTaskDueAtDay.from_raw(habit_period, self.due_at_day) if self.due_at_day else None,
                due_at_month=
                RecurringTaskDueAtMonth.from_raw(habit_period, self.due_at_month)
                if self.due_at_month else None),
            suspended=self.suspended,
            skip_rule=RecurringTaskSkipRule.from_raw(self.skip_rule) if self.skip_rule else None,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: Habit, extra_info: InverseInfo) -> Habit:
        """Apply to an already existing habit."""
        habit_period = RecurringTaskPeriod.from_raw(self.period)

        project_ref_id = EntityId.from_raw(self.project_ref_id) \
            if self.project_ref_id else None
        project_name = ProjectName.from_raw(self.project_name) \
            if self.project_name else None

        if project_ref_id is not None:
            project = extra_info.all_projects_map[project_ref_id]
        elif project_name is not None:
            project = extra_info.all_projects_by_name[format_name_for_option(project_name)]
        else:
            project = extra_info.default_project

        new_aggregate_root = aggregate_root \
            .change_project(
                project_ref_id=project.ref_id, source=EventSource.NOTION, modification_time=self.last_edited_time) \
            .update(
                name=UpdateAction.change_to(HabitName.from_raw(self.name)),
                gen_params=UpdateAction.change_to(
                    RecurringTaskGenParams(
                        period=RecurringTaskPeriod.from_raw(self.period),
                        eisen=Eisen.from_raw(self.eisen) if self.eisen else Eisen.REGULAR,
                        difficulty=Difficulty.from_raw(self.difficulty) if self.difficulty else None,
                        actionable_from_day=
                        RecurringTaskDueAtDay.from_raw(habit_period, self.actionable_from_day)
                        if self.actionable_from_day else None,
                        actionable_from_month=
                        RecurringTaskDueAtMonth.from_raw(habit_period, self.actionable_from_month)
                        if self.actionable_from_month else None,
                        due_at_time=RecurringTaskDueAtTime.from_raw(self.due_at_time) if self.due_at_time else None,
                        due_at_day=
                        RecurringTaskDueAtDay.from_raw(habit_period, self.due_at_day)
                        if self.due_at_day else None,
                        due_at_month=
                        RecurringTaskDueAtMonth.from_raw(habit_period, self.due_at_month)
                        if self.due_at_month else None)),
                skip_rule=UpdateAction.change_to(
                    RecurringTaskSkipRule.from_raw(self.skip_rule) if self.skip_rule else None),
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
