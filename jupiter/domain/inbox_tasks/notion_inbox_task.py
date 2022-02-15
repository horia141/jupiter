"""A inbox task on Notion-side."""
from dataclasses import dataclass
from typing import Optional, Dict

from jupiter.domain.adate import ADate
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_name import BigPlanName
from jupiter.domain.difficulty import Difficulty
from jupiter.domain.eisen import Eisen
from jupiter.domain.entity_name import EntityName
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_name import InboxTaskName
from jupiter.domain.inbox_tasks.inbox_task_status import InboxTaskStatus
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_name import ProjectName
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.notion_id import BAD_NOTION_ID
from jupiter.framework.errors import InputValidationError
from jupiter.framework.event import EventSource
from jupiter.framework.notion import NotionRow
from jupiter.framework.update_action import UpdateAction
from jupiter.remote.notion.common import format_name_for_option


@dataclass(frozen=True)
class NotionInboxTask(NotionRow[InboxTask, 'NotionInboxTask.DirectInfo', 'NotionInboxTask.InverseInfo']):
    """A inbox task on Notion-side."""

    @dataclass(frozen=True)
    class DirectInfo:
        """Info when copying from the app to Notion."""
        project_name: ProjectName
        big_plan_name: Optional[EntityName]

    @dataclass(frozen=True)
    class InverseInfo:
        """Info when copying from Notion to the app."""
        inbox_task_collection_ref_id: EntityId
        default_project: Project
        all_projects_by_name: Dict[str, Project]
        all_projects_map: Dict[EntityId, Project]
        all_big_plans_by_name: Dict[str, BigPlan]
        all_big_plans_map: Dict[EntityId, BigPlan]

    source: str
    name: str
    project_ref_id: Optional[str]
    project_name: Optional[str]
    big_plan_ref_id: Optional[str]
    big_plan_name: Optional[str]
    habit_ref_id: Optional[str]
    chore_ref_id: Optional[str]
    metric_ref_id: Optional[str]
    person_ref_id: Optional[str]
    status: Optional[str]
    eisen: Optional[str]
    difficulty: Optional[str]
    actionable_date: Optional[ADate]
    due_date: Optional[ADate]
    from_script: bool
    recurring_timeline: Optional[str]
    recurring_period: Optional[str]
    recurring_gen_right_now: Optional[ADate]

    @staticmethod
    def new_notion_row(aggregate_root: InboxTask, extra_info: DirectInfo) -> 'NotionInboxTask':
        """Construct a new Notion row from a given inbox task."""
        return NotionInboxTask(
            notion_id=BAD_NOTION_ID,
            ref_id=aggregate_root.ref_id,
            last_edited_time=aggregate_root.last_modified_time,
            source=aggregate_root.source.for_notion(),
            name=str(aggregate_root.name),
            archived=aggregate_root.archived,
            project_ref_id=str(aggregate_root.project_ref_id),
            project_name=format_name_for_option(extra_info.project_name),
            big_plan_ref_id=str(aggregate_root.big_plan_ref_id) if aggregate_root.big_plan_ref_id else None,
            big_plan_name=format_name_for_option(extra_info.big_plan_name) if extra_info.big_plan_name else None,
            habit_ref_id=str(aggregate_root.habit_ref_id) if aggregate_root.habit_ref_id else None,
            chore_ref_id=str(aggregate_root.chore_ref_id) if aggregate_root.chore_ref_id else None,
            metric_ref_id=str(aggregate_root.metric_ref_id) if aggregate_root.metric_ref_id else None,
            person_ref_id=str(aggregate_root.person_ref_id) if aggregate_root.person_ref_id else None,
            status=aggregate_root.status.for_notion(),
            eisen=aggregate_root.eisen.for_notion(),
            difficulty=aggregate_root.difficulty.for_notion() if aggregate_root.difficulty else None,
            actionable_date=aggregate_root.actionable_date,
            due_date=aggregate_root.due_date,
            from_script=aggregate_root.source.is_from_script,
            recurring_timeline=aggregate_root.recurring_timeline,
            recurring_period=aggregate_root.recurring_period.for_notion() if aggregate_root.recurring_period else None,
            recurring_gen_right_now=
            ADate.from_timestamp(aggregate_root.recurring_gen_right_now)
            if aggregate_root.recurring_gen_right_now else None)

    def new_aggregate_root(self, extra_info: InverseInfo) -> InboxTask:
        """Create a new inbox task from this."""
        inbox_task_name = InboxTaskName.from_raw(self.name)

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

        inbox_task_big_plan_ref_id = \
            EntityId.from_raw(self.big_plan_ref_id) \
                if self.big_plan_ref_id else None
        inbox_task_big_plan_name = EntityName.from_raw(self.big_plan_name) \
            if self.big_plan_name else None

        inbox_task_habit_ref_id = EntityId.from_raw(self.habit_ref_id) if self.habit_ref_id else None
        inbox_task_chore_ref_id = EntityId.from_raw(self.chore_ref_id) if self.chore_ref_id else None
        inbox_task_metric_ref_id = EntityId.from_raw(self.metric_ref_id) if self.metric_ref_id else None
        inbox_task_person_ref_id = EntityId.from_raw(self.person_ref_id) if self.person_ref_id else None
        inbox_task_status = InboxTaskStatus.from_raw(self.status) if self.status else InboxTaskStatus.NOT_STARTED
        inbox_task_eisen = Eisen.from_raw(self.eisen)  if self.eisen else Eisen.REGULAR
        inbox_task_difficulty = Difficulty.from_raw(self.difficulty) if self.difficulty else None

        big_plan = None
        if inbox_task_big_plan_ref_id is not None:
            big_plan = extra_info.all_big_plans_map[inbox_task_big_plan_ref_id]
        elif inbox_task_big_plan_name is not None:
            big_plan = \
                extra_info.all_big_plans_by_name[format_name_for_option(inbox_task_big_plan_name)]
        elif inbox_task_habit_ref_id is not None:
            raise InputValidationError("Trying to create an inbox task for a habit from Notion")
        elif inbox_task_chore_ref_id is not None:
            raise InputValidationError("Trying to create an inbox task for a chore from Notion")
        elif inbox_task_metric_ref_id is not None:
            raise InputValidationError("Trying to create an inbox task for a metric from Notion")
        elif inbox_task_person_ref_id is not None:
            raise InputValidationError("Trying to create an inbox task for a person from Notion")

        return InboxTask.new_inbox_task(
            inbox_task_collection_ref_id=extra_info.inbox_task_collection_ref_id,
            project_ref_id=project.ref_id,
            archived=self.archived,
            name=inbox_task_name,
            status=inbox_task_status,
            big_plan=big_plan,
            eisen=inbox_task_eisen,
            difficulty=inbox_task_difficulty,
            actionable_date=self.actionable_date,
            due_date=self.due_date,
            source=EventSource.NOTION,
            created_time=self.last_edited_time)

    def apply_to_aggregate_root(self, aggregate_root: InboxTask, extra_info: InverseInfo) -> InboxTask:
        """Apply to an already existing inbox task."""
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

        inbox_task_big_plan_ref_id = \
            EntityId.from_raw(self.big_plan_ref_id) \
                if self.big_plan_ref_id else None
        inbox_task_big_plan_name = BigPlanName.from_raw(self.big_plan_name) \
            if self.big_plan_name else None

        big_plan = None
        if inbox_task_big_plan_ref_id is not None:
            big_plan = extra_info.all_big_plans_map[inbox_task_big_plan_ref_id]
        elif inbox_task_big_plan_name is not None:
            big_plan = \
                extra_info.all_big_plans_by_name[format_name_for_option(inbox_task_big_plan_name)]

        new_aggregate_root = aggregate_root

        if big_plan is not None:
            new_aggregate_root = new_aggregate_root.associate_with_big_plan(
                project_ref_id=big_plan.project_ref_id, big_plan_ref_id=big_plan.ref_id,
                _big_plan_name=big_plan.name, source=EventSource.NOTION,
                modification_time=self.last_edited_time)
        elif aggregate_root.allow_user_changes:
            new_aggregate_root = \
                new_aggregate_root.release_from_big_plan(EventSource.NOTION, modification_time=self.last_edited_time)

        if aggregate_root.allow_user_changes:
            new_aggregate_root = \
                new_aggregate_root \
                .change_project(
                    project_ref_id=project.ref_id,
                    source=EventSource.NOTION,
                    modification_time=self.last_edited_time)\
                .update(
                    name=UpdateAction.change_to(InboxTaskName.from_raw(self.name)),
                    status=UpdateAction.change_to(InboxTaskStatus.from_raw(self.status)),
                    actionable_date=UpdateAction.change_to(self.actionable_date),
                    due_date=UpdateAction.change_to(self.due_date),
                    eisen=UpdateAction.change_to(Eisen.from_raw(self.eisen) if self.eisen else Eisen.REGULAR),
                    difficulty=UpdateAction.change_to(
                        Difficulty.from_raw(self.difficulty) if self.difficulty else None),
                    source=EventSource.NOTION,
                    modification_time=self.last_edited_time)
        else:
            new_aggregate_root = new_aggregate_root.update_generated(
                status=UpdateAction.change_to(InboxTaskStatus.from_raw(self.status)),
                actionable_date=UpdateAction.change_to(self.actionable_date),
                due_date=UpdateAction.change_to(self.due_date),
                source=EventSource.NOTION,
                modification_time=self.last_edited_time)
        return new_aggregate_root.change_archived(
            archived=self.archived, source=EventSource.NOTION, archived_time=self.last_edited_time)
