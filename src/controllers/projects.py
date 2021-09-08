"""The controller for projects."""
from dataclasses import dataclass
from typing import Final, Iterable, Optional

from domain.common.entity_name import EntityName
from domain.projects.project_key import ProjectKey
from service.big_plans import BigPlansService
from service.errors import ServiceError
from service.inbox_tasks import InboxTasksService
from service.metrics import MetricsService
from service.projects import ProjectsService, Project
from service.recurring_tasks import RecurringTasksService
from service.workspaces import WorkspacesService


@dataclass()
class LoadAllProjectsEntry:
    """A single entry in the load_all_projects response."""

    project: Project


@dataclass()
class LoadAllProjectsResponse:
    """The response object for the the load_all_projects controller method."""

    projects: Iterable[LoadAllProjectsEntry]


class ProjectsController:
    """The controller for projects."""

    _workspaces_service: Final[WorkspacesService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]
    _metrics_service: Final[MetricsService]

    def __init__(
            self, workspaces_service: WorkspacesService, projects_service: ProjectsService,
            inbox_tasks_service: InboxTasksService, recurring_tasks_service: RecurringTasksService,
            big_plans_service: BigPlansService, metrics_service: MetricsService) -> None:
        """Constructor."""
        self._workspaces_service = workspaces_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service
        self._metrics_service = metrics_service

    def create_project(self, key: ProjectKey, name: EntityName) -> None:
        """Create a project."""
        response = self._projects_service.create_project(key, name)
        self._inbox_tasks_service.create_inbox_tasks_collection(response.ref_id, response.notion_page_link)
        self._recurring_tasks_service.create_recurring_tasks_collection(response.ref_id, response.notion_page_link)
        self._big_plans_service.create_big_plans_collection(response.ref_id, response.notion_page_link)

    def archive_project(self, key: ProjectKey) -> Project:
        """Archive a project."""
        project = self._projects_service.load_project_by_key(key)

        workspace = self._workspaces_service.load_workspace()
        if workspace.default_project_ref_id == project.ref_id:
            raise ServiceError("Cannot archive project because it is the default workspace one")
        metrics = self._metrics_service.load_all_metrics(allow_archived=True)
        for metric in metrics:
            if metric.collection_params is not None and metric.collection_params.project_ref_id == project.ref_id:
                raise ServiceError(
                    "Cannot archive project because it is the collection project " +
                    f"for metric '{metric.name} archived={metric.archived}'")

        self._inbox_tasks_service.archive_inbox_tasks_collection(project.ref_id)
        self._recurring_tasks_service.archive_recurring_tasks_collection_structure(project.ref_id)
        self._big_plans_service.archive_big_plans_collection(project.ref_id)

        return self._projects_service.archive_project(project.ref_id)

    def set_project_name(self, key: ProjectKey, name: EntityName) -> Project:
        """Change the name of a project."""
        project = self._projects_service.load_project_by_key(key)
        return self._projects_service.set_project_name(project.ref_id, name)

    def load_all_projects(self, filter_project_keys: Optional[Iterable[ProjectKey]] = None) -> LoadAllProjectsResponse:
        """Retrieve all projects."""
        projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)

        return LoadAllProjectsResponse(
            projects=[LoadAllProjectsEntry(project=p) for p in projects])
