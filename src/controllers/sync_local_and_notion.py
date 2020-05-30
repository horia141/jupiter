"""The controller for syncing the local and Notion data."""
import logging
from typing import Final, Optional, Iterable

import pendulum

from models import schedules
from models.basic import SyncPrefer, ProjectKey, SyncTarget
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService

LOGGER = logging.getLogger(__name__)


class SyncLocalAndNotionController:
    """The controller for syncing the local and Notion data."""

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

    def sync(
            self, sync_targets: Iterable[SyncTarget], filter_project_keys: Optional[Iterable[ProjectKey]] = None,
            sync_prefer: SyncPrefer = SyncPrefer.NOTION) -> None:
        """Sync the local and Notion data."""
        sync_targets = frozenset(sync_targets)

        if SyncTarget.WORKSPACE in sync_targets:
            LOGGER.info("Syncing the workspace")
            self._workspaces_service.workspace_sync(sync_prefer)

        if SyncTarget.VACATIONS in sync_targets:
            LOGGER.info("Syncing the vacations")
            self._vacations_service.vacations_sync(sync_prefer)

        for project in self._projects_service.load_all_projects(filter_keys=filter_project_keys):
            inbox_collection_link = self._inbox_tasks_service.get_notion_structure(project.ref_id)

            if SyncTarget.PROJECTS in sync_targets:
                LOGGER.info(f"Syncing project '{project.name}'")
                self._projects_service.sync_projects(project.key, sync_prefer)

            if SyncTarget.BIG_PLANS in sync_targets:
                LOGGER.info(f"Syncing big plans for '{project.name}'")
                all_big_plans = self._big_plans_service.big_plans_sync(
                    project.ref_id, inbox_collection_link, sync_prefer)
                self._inbox_tasks_service.upsert_notion_big_plan_ref_options(project.ref_id, all_big_plans)
            else:
                all_big_plans = self._big_plans_service.load_all_big_plans(
                    filter_archived=False, filter_project_ref_ids=[project.ref_id])

            if SyncTarget.RECURRING_TASKS in sync_targets:
                LOGGER.info(f"Syncing recurring tasks for '{project.name}'")
                all_recurring_tasks = self._recurring_tasks_service.recurring_tasks_sync(
                    project.ref_id, inbox_collection_link, sync_prefer)
            else:
                all_recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
                    filter_archived=False, filter_project_ref_ids=[project.ref_id])
            all_recurring_tasks_set = {rt.ref_id: rt for rt in all_recurring_tasks}

            if SyncTarget.INBOX_TASKS in sync_targets:
                LOGGER.info(f"Syncing inbox tasks for '{project.name}'")
                all_inbox_tasks = self._inbox_tasks_service.inbox_tasks_sync(
                    project.ref_id, all_big_plans, all_recurring_tasks, sync_prefer)
            else:
                all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
                    filter_archived=False, filter_project_ref_ids=[project.ref_id])

            if SyncTarget.RECURRING_TASKS in sync_targets:
                LOGGER.info(f"Syncing recurring tasks instances for '{project.name}'")
                for inbox_task in all_inbox_tasks:
                    if inbox_task.is_considered_done:
                        continue
                    if inbox_task.recurring_task_ref_id is None:
                        continue
                    LOGGER.info(f"Updating inbox task '{inbox_task.name}'")
                    recurring_task = all_recurring_tasks_set[inbox_task.recurring_task_ref_id]
                    schedule = schedules.get_schedule(
                        recurring_task.period, recurring_task.name, pendulum.instance(inbox_task.created_date),
                        recurring_task.skip_rule, recurring_task.due_at_time, recurring_task.due_at_day,
                        recurring_task.due_at_month)
                    self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                        ref_id=inbox_task.ref_id,
                        name=schedule.full_name,
                        period=recurring_task.period,
                        due_time=schedule.due_time,
                        eisen=recurring_task.eisen,
                        difficulty=recurring_task.difficulty,
                        timeline=schedule.timeline)
