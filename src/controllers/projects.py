"""The controller for projects."""
from dataclasses import dataclass
from typing import Final, Iterable, Optional

from models.basic import ProjectKey, SyncPrefer
from repository.projects import Project
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
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

    def create_project(self, key: ProjectKey, name: str) -> None:
        """Create a project."""
        workspace = self._workspaces_service.get_workspace_notion_structure()

        response = self._projects_service.create_project(key, name, workspace)
        self._inbox_tasks_service.upsert_notion_structure(response.project.ref_id, response.page)
        self._recurring_tasks_service.upsert_notion_structure(response.project.ref_id, response.page)
        self._big_plans_service.upsert_notion_structure(response.project.ref_id, response.page)

    def archive_project(self, key: ProjectKey) -> Project:
        """Archive a project."""
        project = self._projects_service.load_project_by_key(key)

        self._inbox_tasks_service.remove_notion_structure(project.ref_id)
        self._recurring_tasks_service.remove_notion_structure(project.ref_id)
        self._big_plans_service.remove_notion_structure(project.ref_id)

        return self._projects_service.archive_project(key)

    def set_project_name(self, key: ProjectKey, name: str) -> Project:
        """Change the name of a project."""
        return self._projects_service.set_project_name(key, name)

    def load_all_projects(self, filter_project_keys: Optional[Iterable[ProjectKey]] = None) -> LoadAllProjectsResponse:
        """Retrieve all projects."""
        projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)

        return LoadAllProjectsResponse(
            projects=[LoadAllProjectsEntry(project=p) for p in projects])

    def sync_projects(self, project_key: ProjectKey, sync_prefer: SyncPrefer) -> None:
        """Synchronise projects between Notion and local."""
        project = self._projects_service.load_project_by_key(project_key)
        project_page = self._projects_service.get_project_notion_structure(project.ref_id)
        self._inbox_tasks_service.upsert_notion_structure(project.ref_id, project_page)
        self._recurring_tasks_service.upsert_notion_structure(project.ref_id, project_page)
        self._big_plans_service.upsert_notion_structure(project.ref_id, project_page)
        self._projects_service.sync_projects(project_key, sync_prefer)
