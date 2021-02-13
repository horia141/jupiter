"""The controller for big plans."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, Optional, List

from controllers.common import ControllerInputValidationError
from models.basic import EntityId, ProjectKey, BigPlanStatus, ADate
from remote.notion.inbox_tasks_manager import InboxTaskBigPlanLabel
from service.big_plans import BigPlansService, BigPlan
from service.inbox_tasks import InboxTasksService, InboxTask
from service.projects import ProjectsService

LOGGER = logging.getLogger(__name__)


@dataclass()
class LoadAllBigPlansEntry:
    """A single entry in the load all big plans response."""
    big_plan: BigPlan
    inbox_tasks: Iterable[InboxTask]


@dataclass()
class LoadAllBigPlansResponse:
    """Response object for the load_all_big_plans controller method."""

    big_plans: Iterable[LoadAllBigPlansEntry]


class BigPlansController:
    """The controller for big plans."""

    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _big_plans_service: Final[BigPlansService]

    def __init__(
            self, projects_service: ProjectsService, inbox_tasks_service: InboxTasksService,
            big_plans_service: BigPlansService) -> None:
        """Constructor."""
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._big_plans_service = big_plans_service

    def create_big_plan(self, project_key: ProjectKey, name: str, due_date: Optional[ADate]) -> BigPlan:
        """Create an big plan."""
        project = self._projects_service.load_project_by_key(project_key)
        inbox_tasks_collection = self._inbox_tasks_service.get_inbox_tasks_collection(project.ref_id)
        big_plan = self._big_plans_service.create_big_plan(project.ref_id, inbox_tasks_collection, name, due_date)
        all_big_plans = self._big_plans_service.load_all_big_plans(filter_project_ref_ids=[project.ref_id])
        self._inbox_tasks_service.upsert_notion_big_plan_ref_options(
            project.ref_id,
            [InboxTaskBigPlanLabel(notion_link_uuid=bp.notion_link_uuid, name=bp.name) for bp in all_big_plans])

        return big_plan

    def archive_big_plan(self, ref_id: EntityId) -> BigPlan:
        """Archive a big plan."""
        inbox_tasks_for_big_plan = self._inbox_tasks_service.load_all_inbox_tasks(
            filter_big_plan_ref_ids=[ref_id])

        for inbox_task in inbox_tasks_for_big_plan:
            LOGGER.info(f"Archiving task {inbox_task.name} for plan")
            self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
        LOGGER.info("Archived all tasks")

        big_plan = self._big_plans_service.archive_big_plan(ref_id)
        LOGGER.info(f"Archived the big plan")

        all_big_plans = self._big_plans_service.load_all_big_plans(filter_project_ref_ids=[big_plan.project_ref_id])
        self._inbox_tasks_service.upsert_notion_big_plan_ref_options(
            big_plan.project_ref_id,
            [InboxTaskBigPlanLabel(notion_link_uuid=bp.notion_link_uuid, name=bp.name) for bp in all_big_plans])
        LOGGER.info(f"Updated the schema for the associated inbox")

        return big_plan

    def set_big_plan_name(self, ref_id: EntityId, name: str) -> BigPlan:
        """Change the due date of a big plan."""
        big_plan = self._big_plans_service.load_big_plan_by_id(ref_id)
        inbox_tasks_collection = self._inbox_tasks_service.get_inbox_tasks_collection(big_plan.project_ref_id)
        big_plan = self._big_plans_service.set_big_plan_name(ref_id, name, inbox_tasks_collection)
        all_big_plans = self._big_plans_service.load_all_big_plans(filter_project_ref_ids=[big_plan.project_ref_id])
        self._inbox_tasks_service.upsert_notion_big_plan_ref_options(
            big_plan.project_ref_id,
            [InboxTaskBigPlanLabel(notion_link_uuid=bp.notion_link_uuid, name=bp.name) for bp in all_big_plans])
        all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_big_plan_ref_ids=[big_plan.ref_id])

        for inbox_task in all_inbox_tasks:
            LOGGER.info(f'Updating the associated inbox task "{inbox_task.name}"')
            self._inbox_tasks_service.set_inbox_task_to_big_plan_link(inbox_task.ref_id, big_plan.ref_id, big_plan.name)

        return big_plan

    def set_big_plan_status(self, ref_id: EntityId, status: BigPlanStatus) -> BigPlan:
        """Change the due date of a big plan."""
        return self._big_plans_service.set_big_plan_status(ref_id, status)

    def set_big_plan_due_date(self, ref_id: EntityId, due_date: Optional[ADate]) -> BigPlan:
        """Change the due date of a big plan."""
        return self._big_plans_service.set_big_plan_due_date(ref_id, due_date)

    def load_all_big_plans(
            self, show_archived: bool = False, filter_ref_ids: Optional[Iterable[EntityId]] = None,
            filter_project_keys: Optional[Iterable[ProjectKey]] = None) -> LoadAllBigPlansResponse:
        """Retrieve all big plan."""
        filter_project_ref_ids: Optional[List[EntityId]] = None
        if filter_project_keys:
            projects = self._projects_service.load_all_projects(filter_keys=filter_project_keys)
            filter_project_ref_ids = [p.ref_id for p in projects]

        big_plans = self._big_plans_service.load_all_big_plans(
            allow_archived=show_archived, filter_ref_ids=filter_ref_ids,
            filter_project_ref_ids=filter_project_ref_ids)
        inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_big_plan_ref_ids=(bp.ref_id for bp in big_plans))

        return LoadAllBigPlansResponse(
            big_plans=[LoadAllBigPlansEntry(
                big_plan=bp,
                inbox_tasks=[it for it in inbox_tasks if it.big_plan_ref_id == bp.ref_id])
                       for bp in big_plans])

    def hard_remove_big_plans(self, ref_ids: Iterable[EntityId]) -> None:
        """Hard remove big plans."""
        ref_ids = list(ref_ids)
        if len(ref_ids) == 0:
            raise ControllerInputValidationError("Expected at least one entity to remove")

        inbox_tasks_for_big_plan = self._inbox_tasks_service.load_all_inbox_tasks(
            allow_archived=True, filter_big_plan_ref_ids=ref_ids)

        for inbox_task in inbox_tasks_for_big_plan:
            LOGGER.info(f"Hard removing task {inbox_task.name} for plan")
            self._inbox_tasks_service.hard_remove_inbox_task(inbox_task.ref_id)
        LOGGER.info("Hard removed all tasks")

        for ref_id in ref_ids:
            self._big_plans_service.hard_remove_big_plan(ref_id)
