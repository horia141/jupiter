"""The controller for recurring tasks."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, Optional, List

from controllers.common import ControllerInputValidationError
from models import schedules
from models.basic import EntityId, Difficulty, Eisen, RecurringTaskPeriod, ProjectKey, EntityName, RecurringTaskType
from repository.inbox_tasks import InboxTask
from repository.recurring_tasks import RecurringTask
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService

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

    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]

    def __init__(
            self, projects_service: ProjectsService, inbox_tasks_service: InboxTasksService,
            recurring_tasks_service: RecurringTasksService) -> None:
        """Constructor."""
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service

    def create_recurring_task(
            self, project_key: ProjectKey, name: str, period: RecurringTaskPeriod, the_type: RecurringTaskType,
            group: EntityName, eisen: List[Eisen], difficulty: Optional[Difficulty], due_at_time: Optional[str],
            due_at_day: Optional[int], due_at_month: Optional[int], must_do: bool,
            skip_rule: Optional[str]) -> RecurringTask:
        """Create an recurring task."""
        project = self._projects_service.load_project_by_key(project_key)
        inbox_collection_link = self._inbox_tasks_service.get_notion_structure(project.ref_id)
        recurring_task = self._recurring_tasks_service.create_recurring_task(
            project_ref_id=project.ref_id,
            inbox_collection_link=inbox_collection_link,
            name=name,
            period=period,
            the_type=the_type,
            group=group,
            eisen=eisen,
            difficulty=difficulty,
            due_at_time=due_at_time,
            due_at_day=due_at_day,
            due_at_month=due_at_month,
            must_do=must_do,
            skip_rule=skip_rule)

        return recurring_task

    def archive_recurring_task(self, ref_id: EntityId) -> RecurringTask:
        """Archive an recurring task."""
        recurring_task = self._recurring_tasks_service.load_recurring_task_by_id(ref_id)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
            LOGGER.info(f"Removing inbox task instance {inbox_task.name}")
        return self._recurring_tasks_service.archive_recurring_task(ref_id)

    def set_recurring_task_name(self, ref_id: EntityId, name: str) -> RecurringTask:
        """Change the name for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_name(ref_id, name)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name, inbox_task.created_time,
                recurring_task.skip_rule, recurring_task.due_at_time, recurring_task.due_at_day,
                recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_name(inbox_task.ref_id, schedule.full_name)
        return recurring_task

    def set_recurring_task_period(self, ref_id: EntityId, period: RecurringTaskPeriod) -> RecurringTask:
        """Change the period for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_period(ref_id, period)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            if inbox_task.status.is_completed:
                continue
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name, inbox_task.created_time,
                recurring_task.skip_rule, recurring_task.due_at_time, recurring_task.due_at_day,
                recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                inbox_task.ref_id, schedule.full_name, schedule.timeline, schedule.period, recurring_task.the_type,
                schedule.due_time, recurring_task.eisen, recurring_task.difficulty)
        return recurring_task

    def set_recurring_task_type(self, ref_id: EntityId, the_type: RecurringTaskType) -> RecurringTask:
        """Change the group for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_type(ref_id, the_type)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            if inbox_task.status.is_completed:
                continue
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name, inbox_task.created_time,
                recurring_task.skip_rule, recurring_task.due_at_time, recurring_task.due_at_day,
                recurring_task.due_at_month)
            self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                inbox_task.ref_id, schedule.full_name, schedule.timeline, schedule.period, recurring_task.the_type,
                schedule.due_time, recurring_task.eisen, recurring_task.difficulty)
        return recurring_task

    def set_recurring_task_group(self, ref_id: EntityId, group: EntityName) -> RecurringTask:
        """Change the group for a recurring task."""
        return self._recurring_tasks_service.set_recurring_task_group(ref_id, group)

    def set_recurring_task_eisen(self, ref_id: EntityId, eisen: List[Eisen]) -> RecurringTask:
        """Change the difficulty for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_eisen(ref_id, eisen)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.set_inbox_task_eisen(inbox_task.ref_id, eisen)
        return recurring_task

    def set_recurring_task_difficulty(self, ref_id: EntityId, difficulty: Optional[Difficulty]) -> RecurringTask:
        """Change the difficulty for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_difficulty(ref_id, difficulty)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            self._inbox_tasks_service.set_inbox_task_difficulty(inbox_task.ref_id, difficulty)
        return recurring_task

    def set_recurring_task_deadlines(
            self, ref_id: EntityId, due_at_time: Optional[str], due_at_day: Optional[int],
            due_at_month: Optional[int]) -> RecurringTask:
        """Change the deadlines for a recurring task."""
        recurring_task = self._recurring_tasks_service.set_recurring_task_deadlines(
            ref_id, due_at_time, due_at_day, due_at_month)
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=[recurring_task.ref_id])
        for inbox_task in all_inbox_tasks:
            schedule = schedules.get_schedule(
                recurring_task.period, recurring_task.name, inbox_task.created_time,
                recurring_task.skip_rule, due_at_time, due_at_day, due_at_month)
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

    def load_all_recurring_tasks(
            self, show_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_keys: Optional[Iterable[ProjectKey]] = None) -> LoadAllRecurringTasksResponse:
        """Retrieve all recurring tasks."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if filter_project_keys:
            projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
            filter_archived=not show_archived, filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)
        inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_archived=False, filter_recurring_task_ref_ids=(bp.ref_id for bp in recurring_tasks))

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
        for ref_id in ref_ids:
            self._recurring_tasks_service.hard_remove_recurring_task(ref_id)
