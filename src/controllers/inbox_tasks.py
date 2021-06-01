"""The controller for inbox tasks."""
from dataclasses import dataclass
from typing import Final, Iterable, Optional, List

from controllers.common import ControllerInputValidationError
from models.basic import ProjectKey, Eisen, Difficulty, InboxTaskStatus, ADate, InboxTaskSource
from models.framework import EntityId
from service.big_plans import BigPlansService, BigPlan
from service.errors import ServiceError
from service.inbox_tasks import InboxTasksService, InboxTask
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService, RecurringTask
from service.workspaces import WorkspacesService


@dataclass()
class LoadAllInboxTasksEntry:
    """A single entry in the load all inbox tasks response."""
    inbox_task: InboxTask
    big_plan: Optional[BigPlan]
    recurring_task: Optional[RecurringTask]


@dataclass()
class LoadAllInboxTasksResponse:
    """Response object for the load_all_inbox_tasks controller method."""

    inbox_tasks: Iterable[LoadAllInboxTasksEntry]


class InboxTasksController:
    """The controller for inbox tasks."""

    _workspaces_service: Final[WorkspacesService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]

    def __init__(
            self, workspaces_service: WorkspacesService, projects_service: ProjectsService,
            inbox_tasks_service: InboxTasksService, recurring_tasks_service: RecurringTasksService,
            big_plans_service: BigPlansService) -> None:
        """Constructor."""
        self._workspaces_service = workspaces_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service

    def create_inbox_task(
            self, project_key: Optional[ProjectKey], name: str, big_plan_ref_id: Optional[EntityId], eisen: List[Eisen],
            difficulty: Optional[Difficulty], actionable_date: Optional[ADate], due_date: Optional[ADate]) -> InboxTask:
        """Create an inbox task."""
        if project_key is not None:
            project = self._projects_service.load_project_by_key(project_key)
            project_ref_id = project.ref_id
        else:
            workspace = self._workspaces_service.load_workspace()
            if workspace.default_project_ref_id is None:
                raise ServiceError(f"Expected a project and default project is missing")
            project_ref_id = workspace.default_project_ref_id

        big_plan_name: Optional[str] = None
        if big_plan_ref_id:
            big_plan = self._big_plans_service.load_big_plan_by_id(big_plan_ref_id)
            big_plan_name = big_plan.name

        return self._inbox_tasks_service.create_inbox_task(
            project_ref_id, name, big_plan_ref_id, big_plan_name, eisen, difficulty, actionable_date, due_date)

    def archive_inbox_task(self, ref_id: EntityId) -> InboxTask:
        """Archive an inbox task."""
        return self._inbox_tasks_service.archive_inbox_task(ref_id)

    def associate_inbox_task_with_big_plan(self, ref_id: EntityId, big_plan_ref_id: Optional[EntityId]) -> InboxTask:
        """Associate a big plan with an inbox task."""
        big_plan_name: Optional[str] = None
        if big_plan_ref_id:
            big_plan = self._big_plans_service.load_big_plan_by_id(big_plan_ref_id)
            big_plan_name = big_plan.name

        return self._inbox_tasks_service.associate_inbox_task_with_big_plan(ref_id, big_plan_ref_id, big_plan_name)

    def set_inbox_task_name(self, ref_id: EntityId, name: str) -> InboxTask:
        """Change the difficulty of an inbox task."""
        return self._inbox_tasks_service.set_inbox_task_name(ref_id, name)

    def set_inbox_task_status(self, ref_id: EntityId, status: InboxTaskStatus) -> InboxTask:
        """Change the difficulty of an inbox task."""
        return self._inbox_tasks_service.set_inbox_task_status(ref_id, status)

    def set_inbox_task_eisen(self, ref_id: EntityId, eisen: List[Eisen]) -> InboxTask:
        """Change the difficulty of an inbox task."""
        return self._inbox_tasks_service.set_inbox_task_eisen(ref_id, eisen)

    def set_inbox_task_difficulty(self, ref_id: EntityId, difficulty: Optional[Difficulty]) -> InboxTask:
        """Change the difficulty of an inbox task."""
        return self._inbox_tasks_service.set_inbox_task_difficulty(ref_id, difficulty)

    def set_inbox_task_actionable_date(self, ref_id: EntityId, actionable_date: Optional[ADate]) -> InboxTask:
        """Change the due date of an inbox task."""
        return self._inbox_tasks_service.set_inbox_task_actionable_date(ref_id, actionable_date)

    def set_inbox_task_due_date(self, ref_id: EntityId, due_date: Optional[ADate]) -> InboxTask:
        """Change the due date of an inbox task."""
        return self._inbox_tasks_service.set_inbox_task_due_date(ref_id, due_date)

    def load_all_inbox_tasks(
            self, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_keys: Optional[Iterable[ProjectKey]] = None,
            filter_sources: Optional[Iterable[InboxTaskSource]] = None) -> LoadAllInboxTasksResponse:
        """Retrieve all inbox tasks."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if filter_project_keys:
            projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_ref_ids=filter_ref_ids, filter_project_ref_ids=filter_project_ref_ids, filter_sources=filter_sources)
        big_plans = self._big_plans_service.load_all_big_plans(
            filter_ref_ids=(it.big_plan_ref_id for it in inbox_tasks if it.big_plan_ref_id is not None))
        big_plans_map = {bp.ref_id: bp for bp in big_plans}
        recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
            filter_ref_ids=(it.recurring_task_ref_id for it in inbox_tasks if it.recurring_task_ref_id is not None))
        recurring_tasks_map = {rt.ref_id: rt for rt in recurring_tasks}

        return LoadAllInboxTasksResponse(
            inbox_tasks=[LoadAllInboxTasksEntry(
                inbox_task=it,
                big_plan=big_plans_map[it.big_plan_ref_id] if it.big_plan_ref_id is not None else None,
                recurring_task=recurring_tasks_map[it.recurring_task_ref_id]
                if it.recurring_task_ref_id is not None else None)
                         for it in inbox_tasks])

    def hard_remove_inbox_tasks(self, ref_ids: Iterable[EntityId]) -> None:
        """Hard remove inbox tasks."""
        ref_ids = list(ref_ids)
        if len(ref_ids) == 0:
            raise ControllerInputValidationError("Expected at least one entity to remove")
        for ref_id in ref_ids:
            self._inbox_tasks_service.hard_remove_inbox_task(ref_id)
