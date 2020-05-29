"""The controller for workspaces."""
import logging
from typing import Final

from models.basic import WorkspaceSpaceId, WorkspaceToken, SyncPrefer
from remote.notion.connection import NotionConnection
from repository.workspace import Workspace
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService

LOGGER = logging.getLogger(__name__)


class WorkspacesController:
    """The controller for workspaces."""

    _notion_connection: Final[NotionConnection]
    _workspaces_service: Final[WorkspacesService]
    _vacations_service: Final[VacationsService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]

    def __init__(
            self, notion_connection: NotionConnection, workspaces_service: WorkspacesService,
            vacations_service: VacationsService, projects_service: ProjectsService,
            inbox_tasks_service: InboxTasksService, recurring_tasks_service: RecurringTasksService,
            big_plans_service: BigPlansService) -> None:
        """Constructor."""
        self._notion_connection = notion_connection
        self._workspaces_service = workspaces_service
        self._vacations_service = vacations_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service

    def create_workspace(self, name: str, space_id: WorkspaceSpaceId, token: WorkspaceToken) -> None:
        """Create a workspace."""
        self._notion_connection.initialize(space_id, token)
        LOGGER.info("Initialised Notion connection")

        new_workspace_page = self._workspaces_service.create_workspace(name)
        self._vacations_service.upsert_notion_structure(new_workspace_page)

    def set_workspace_name(self, name: str) -> Workspace:
        """Change the workspace name."""
        return self._workspaces_service.set_workspace_name(name)

    def set_workspace_token(self, token: WorkspaceToken) -> None:
        """Change the workspace token."""
        self._notion_connection.update_token(token)

    def load_workspace(self) -> Workspace:
        """Retrieve a workspace."""
        return self._workspaces_service.load_workspace()

    def workspace_sync(self, sync_prefer: SyncPrefer) -> None:
        """Synchronise the workspace between Notion and local."""
        all_projects = self._projects_service.load_all_projects()
        for project in all_projects:
            project_page = self._projects_service.get_project_notion_structure(project.ref_id)
            self._inbox_tasks_service.upsert_notion_structure(project.ref_id, project_page)
            self._recurring_tasks_service.upsert_notion_structure(project.ref_id, project_page)
            self._big_plans_service.upsert_notion_structure(project.ref_id, project_page)
        self._workspaces_service.workspace_sync(sync_prefer)
