"""The controller for correcting the Notion-side structure."""
import logging
from typing import Final

from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService

LOGGER = logging.getLogger(__name__)


class CorrectNotionStructureController:
    """The controller for correcting the Notion-side structure."""

    _workspaces_service: Final[WorkspacesService]
    _vacations_service: Final[VacationsService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]

    def __init__(
            self, workspaces_service: WorkspacesService, vacations_service: VacationsService,
            projects_service: ProjectsService, inbox_tasks_service: InboxTasksService,
            recurring_tasks_service: RecurringTasksService, big_plans_service: BigPlansService) -> None:
        """Constructor."""
        self._workspaces_service = workspaces_service
        self._vacations_service = vacations_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service

    def correct_structure(self) -> None:
        """Correct the Notion-side structures."""
        LOGGER.info("Recreating workspace page")
        workspace_page = self._workspaces_service.get_workspace_notion_structure()

        LOGGER.info("Recreating vacations structure")
        self._vacations_service.upsert_notion_structure(workspace_page)

        for project in self._projects_service.load_all_projects():
            LOGGER.info(f"Recreating project {project.name}")
            project_page = self._projects_service.get_project_notion_structure(project.ref_id)
            LOGGER.info("Reacreating inbox tasks")
            self._inbox_tasks_service.upsert_notion_structure(project.ref_id, project_page)
            LOGGER.info("Recreating recurring tasks")
            self._recurring_tasks_service.upsert_notion_structure(project.ref_id, project_page)
            LOGGER.info("Recreating big plans")
            self._big_plans_service.upsert_notion_structure(project.ref_id, project_page)
