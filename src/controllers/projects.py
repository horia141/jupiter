"""The controller for projects."""
from dataclasses import dataclass
from typing import Final, Iterable, Optional

from models.basic import ProjectKey
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService, Project
from service.recurring_tasks import RecurringTasksService


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

    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]

    def __init__(
            self, projects_service: ProjectsService, inbox_tasks_service: InboxTasksService,
            recurring_tasks_service: RecurringTasksService, big_plans_service: BigPlansService) -> None:
        """Constructor."""
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service

    def create_project(self, key: ProjectKey, name: str) -> None:
        """Create a project."""
        response = self._projects_service.create_project(key, name)
        self._inbox_tasks_service.upsert_notion_structure(response.ref_id, response.notion_page_link)
        self._recurring_tasks_service.create_recurring_tasks_collection(response.ref_id, response.notion_page_link)
        self._big_plans_service.create_big_plans_collection(response.ref_id, response.notion_page_link)

    def archive_project(self, key: ProjectKey) -> Project:
        """Archive a project."""
        project = self._projects_service.load_project_by_key(key)

        self._inbox_tasks_service.remove_notion_structure(project.ref_id)
        self._recurring_tasks_service.archive_recurring_tasks_collection_structure(project.ref_id)
        self._big_plans_service.archive_big_plans_collection(project.ref_id)

        return self._projects_service.archive_project(project.ref_id)

    def set_project_name(self, key: ProjectKey, name: str) -> Project:
        """Change the name of a project."""
        project = self._projects_service.load_project_by_key(key)
        return self._projects_service.set_project_name(project.ref_id, name)

    def load_all_projects(self, filter_project_keys: Optional[Iterable[ProjectKey]] = None) -> LoadAllProjectsResponse:
        """Retrieve all projects."""
        projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)

        return LoadAllProjectsResponse(
            projects=[LoadAllProjectsEntry(project=p) for p in projects])
