"""The controller for recurring tasks."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, Optional, List

import typing

from controllers.common import ControllerInputValidationError
from models import schedules
from models.basic import EntityId, Difficulty, Eisen, RecurringTaskPeriod, ProjectKey, RecurringTaskType, Timestamp, \
    ADate
from service.errors import ServiceError
from service.inbox_tasks import InboxTasksService, InboxTask
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService, RecurringTask
from service.workspaces import WorkspacesService
from utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


@dataclass()
class LoadAllRecurringTasksEntry:
    """A single entry in the load all recurring tasks response."""
    recurring_task: RecurringTask
    inbox_tasks: Iterable[InboxTask]


@dataclass()
class LoadAllRecurringTasksResponse:
    """Response object for the load_all_recurring_tasks controller method."""

    recurring_tasks: Iterable[LoadAllRecurringTasksEntry]


class RecurringTasksController:
    """The controller for recurring tasks."""

    _global_properties: Final[GlobalProperties]
    _workspaces_service: Final[WorkspacesService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]

    def __init__(
            self, global_properties: GlobalProperties, workspaces_service: WorkspacesService,
            projects_service: ProjectsService, inbox_tasks_service: InboxTasksService,
            recurring_tasks_service: RecurringTasksService) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._workspaces_service = workspaces_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service

    def create_recurring_task(
            self, project_key: Optional[ProjectKey], name: str, period: RecurringTaskPeriod,
            the_type: RecurringTaskType, eisen: List[Eisen], difficulty: Optional[Difficulty],
            actionable_from_day: Optional[int], actionable_from_month: Optional[int], due_at_time: Optional[str],
            due_at_day: Optional[int], due_at_month: Optional[int], must_do: bool, skip_rule: Optional[str],
            start_at_date: Optional[ADate], end_at_date: Optional[ADate]) -> RecurringTask:
        """Create an recurring task."""
        if project_key is not None:
            project = self._projects_service.load_project_by_key(project_key)
            project_ref_id = project.ref_id
        else:
            workspace = self._workspaces_service.load_workspace()
            if workspace.default_project_ref_id is None:
                raise ServiceError(f"Expected a project and default project is missing")
            project_ref_id = workspace.default_project_ref_id
        inbox_tasks_collection = self._inbox_tasks_service.get_inbox_tasks_collection(project_ref_id)
        recurring_task = self._recurring_tasks_service.create_recurring_task(
            project_ref_id=project_ref_id,
            inbox_tasks_collection=inbox_tasks_collection,
            name=name,
            period=period,
            the_type=the_type,
            eisen=eisen,
            difficulty=difficulty,
            actionable_from_day=actionable_from_day,
            actionable_from_month=actionable_from_month,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            must_do=must_do,
            skip_rule=skip_rule,
            start_at_date=start_at_date,
            end_at_date=end_at_date)

        return recurring_task

    def archive_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Archive an recurring task."""
        recurring_task = self._recurring_tasks_service.load_recurring_task_by_id(ref_id)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
            LOGGER.info(f"Removing inbox task instance {inbox_task.name}")
        return self._recurring_tasks_service.archive_recurring_task(ref_id)

    def set_recurring_task_name(self, ref_id: EntityId, name: str) -> RecurringTask:
        """Change the name for a recurring task."""
        recurring_task = self._recurring_tasks_service.load_recurring_task_by_id(ref_id)
        inbox_tasks_collection = self._inbox_tasks_service.get_inbox_tasks_collection(recurring_task.project_ref_id)
        recurring_task = self._recurring_tasks_service.set_recurring_task_name(ref_id, name, inbox_tasks_collection)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name,
                typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                recurring_task.skip_rule, recurring_task.actionable_from_day, recurring_task.actionable_from_month,
                recurring_task.due_at_time, recurring_task.due_at_day, recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_name(inbox_task.ref_id, schedule.full_name)
        return recurring_task

    def set_recurring_task_period(self, ref_id: EntityId, period: RecurringTaskPeriod) -> RecurringTask:
        """Change the period for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_period(ref_id, period)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            if inbox_task.status.is_completed:
                continue
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name,
                typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                recurring_task.skip_rule, recurring_task.actionable_from_day, recurring_task.actionable_from_month,
                recurring_task.due_at_time, recurring_task.due_at_day, recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                inbox_task.ref_id, schedule.full_name, schedule.timeline, schedule.period, recurring_task.the_type,
                schedule.actionable_date, schedule.due_time, recurring_task.eisen, recurring_task.difficulty)
        return recurring_task

    def set_recurring_task_type(self, ref_id: EntityId, the_type: RecurringTaskType) -> RecurringTask:
        """Change the type for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_type(ref_id, the_type)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            if inbox_task.status.is_completed:
                continue
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name,
                typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                recurring_task.skip_rule, recurring_task.actionable_from_day, recurring_task.actionable_from_month,
                recurring_task.due_at_time, recurring_task.due_at_day, recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                inbox_task.ref_id, schedule.full_name, schedule.timeline, schedule.period, recurring_task.the_type,
                schedule.actionable_date, schedule.due_time, recurring_task.eisen, recurring_task.difficulty)
        return recurring_task

    def set_recurring_task_eisen(self, ref_id: EntityId, eisen: List[Eisen]) -> RecurringTask:
        """Change the difficulty for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_eisen(ref_id, eisen)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.set_inbox_task_eisen(inbox_task.ref_id, eisen)
        return recurring_task

    def set_recurring_task_difficulty(self, ref_id: EntityId, difficulty: Optional[Difficulty]) -> RecurringTask:
        """Change the difficulty for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_difficulty(ref_id, difficulty)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.set_inbox_task_difficulty(inbox_task.ref_id, difficulty)
        return recurring_task

    def set_recurring_task_actionable_config(
            self, ref_id: EntityId, actionable_from_day: Optional[int],
            actionable_from_month: Optional[int]) -> RecurringTask:
        """Change the actionable date config for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_actionable_config(
            ref_id, actionable_from_day, actionable_from_month)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name,
                typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                recurring_task.skip_rule, recurring_task.actionable_from_day, recurring_task.actionable_from_month,
                recurring_task.due_at_time, recurring_task.due_at_day, recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_actionable_date(inbox_task.ref_id, schedule.actionable_date)
        return recurring_task

    def set_recurring_task_deadlines(
            self, ref_id: EntityId, due_at_time: Optional[str], due_at_day: Optional[int],
            due_at_month: Optional[int]) -> RecurringTask:
        """Change the deadlines for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_deadlines(
            ref_id, due_at_time, due_at_day, due_at_month)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name,
                typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                recurring_task.skip_rule, recurring_task.actionable_from_day, recurring_task.actionable_from_month,
                due_at_time, due_at_day, due_at_month)
            self._inbox_tasks_service.set_inbox_task_due_date(inbox_task.ref_id, schedule.due_time)
        return recurring_task

    def set_recurring_task_must_do_state(self, ref_id: EntityId, must_do: bool) -> RecurringTask:
        """Change the skip rule for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_must_do_state(ref_id, must_do)

    def set_recurring_task_skip_rule(self, ref_id: EntityId, skip_rule: Optional[str]) -> RecurringTask:
        """Change the skip rule for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_skip_rule(ref_id, skip_rule)

    def set_recurring_task_suspended(self, ref_id: EntityId, suspended: bool) -> RecurringTask:
        """Change the suspended state for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_suspended(ref_id, suspended)

    def set_recurring_task_active_interval(
            self, ref_id: EntityId, start_at_date: Optional[ADate], end_at_date: Optional[ADate]) -> RecurringTask:
        """Change the suspended state for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_active_interval(ref_id, start_at_date, end_at_date)

    def load_all_recurring_tasks(
            self, show_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_keys: Optional[Iterable[ProjectKey]] = None) -> LoadAllRecurringTasksResponse:
        """Retrieve all recurring tasks."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if filter_project_keys:
            projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
            allow_archived=show_archived, filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)
        inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=(bp.ref_id for bp in recurring_tasks))

        return LoadAllRecurringTasksResponse(
            recurring_tasks=[LoadAllRecurringTasksEntry(
                                recurring_task=rt,
                                inbox_tasks=[it for it in inbox_tasks if it.recurring_task_ref_id == rt.ref_id])
                             for rt in recurring_tasks])

    def hard_remove_recurring_tasks(self, ref_ids: Iterable[EntityId]) -> None:
        """Hard remove a recurring task."""
        ref_ids = list(ref_ids)
        if len(ref_ids) == 0:
            raise ControllerInputValidationError("Expected at least one entity to remove")

        inbox_tasks_for_recurring_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_recurring_task_ref_ids=ref_ids)

        for inbox_task in inbox_tasks_for_recurring_tasks:
            LOGGER.info(f"Hard removing task {inbox_task.name} for recurring task")
            self._inbox_tasks_service.hard_remove_inbox_task(inbox_task.ref_id)
        LOGGER.info("Hard removed all tasks")

        for ref_id in ref_ids:
            self._recurring_tasks_service.hard_remove_recurring_task(ref_id)
