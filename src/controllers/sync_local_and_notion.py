"""The controller for syncing the local and Notion data."""
import logging
from typing import Final, Optional, Iterable

import typing

from models import schedules
from models.basic import SyncPrefer, ProjectKey, SyncTarget, EntityId, Timestamp
from repository.big_plans import BigPlan
from repository.inbox_tasks import InboxTask
from repository.recurring_tasks import RecurringTask
from repository.vacations import Vacation
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService
from utils.global_properties import GlobalProperties

LOGGER = logging.getLogger(__name__)


class SyncLocalAndNotionController:
    """The controller for syncing the local and Notion data."""

    _global_properties: Final[GlobalProperties]
    _workspaces_service: Final[WorkspacesService]
    _vacations_service: Final[VacationsService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]

    def __init__(
            self, global_properties: GlobalProperties, workspaces_service: WorkspacesService,
            vacations_service: VacationsService, projects_service: ProjectsService,
            inbox_tasks_service: InboxTasksService, recurring_tasks_service: RecurringTasksService,
            big_plans_service: BigPlansService) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._workspaces_service = workspaces_service
        self._vacations_service = vacations_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service

    def sync(
            self, sync_targets: Iterable[SyncTarget], anti_entropy_by_name: bool, drop_all_notion: bool,
            drop_all_notion_archived: bool, vacation_ref_ids: Optional[Iterable[EntityId]],
            filter_project_keys: Optional[Iterable[ProjectKey]],
            filter_inbox_task_ref_ids: Optional[Iterable[EntityId]],
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]],
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer = SyncPrefer.NOTION) -> None:
        """Sync the local and Notion data."""
        filter_recurring_task_ref_ids_set = \
            frozenset(filter_recurring_task_ref_ids) if filter_recurring_task_ref_ids else None
        sync_targets = frozenset(sync_targets)

        if SyncTarget.STRUCTURE in sync_targets:
            LOGGER.info("Recreating workspace page")
            workspace_page = self._workspaces_service.get_workspace_notion_structure()

            LOGGER.info("Recreating vacations structure")
            self._vacations_service.upsert_notion_structure(workspace_page)

        if SyncTarget.WORKSPACE in sync_targets:
            LOGGER.info("Syncing the workspace")
            self._workspaces_service.workspace_sync(sync_prefer)

        if SyncTarget.VACATIONS in sync_targets:
            LOGGER.info("Syncing the vacations")
            all_vacations = self._vacations_service.vacations_sync(False, vacation_ref_ids, sync_prefer)
            if anti_entropy_by_name:
                _ = self._do_anti_entropy_for_vacations(all_vacations)
            if drop_all_notion_archived:
                self._do_drop_all_archived_vacations(all_vacations)

        for project in self._projects_service.load_all_projects(filter_keys=filter_project_keys):
            if SyncTarget.STRUCTURE in sync_targets:
                LOGGER.info(f"Recreating project {project.name}")
                project_page = self._projects_service.get_project_notion_structure(project.ref_id)
                LOGGER.info("Recreating inbox tasks")
                self._inbox_tasks_service.upsert_notion_structure(project.ref_id, project_page)
                LOGGER.info("Recreating recurring tasks")
                self._recurring_tasks_service.upsert_notion_structure(project.ref_id, project_page)
                LOGGER.info("Recreating big plans")
                self._big_plans_service.upsert_notion_structure(project.ref_id, project_page)

            inbox_collection_link = self._inbox_tasks_service.get_notion_structure(project.ref_id)

            if SyncTarget.PROJECTS in sync_targets:
                LOGGER.info(f"Syncing project '{project.name}'")
                self._projects_service.sync_projects(project.key, sync_prefer)

            if SyncTarget.BIG_PLANS in sync_targets:
                LOGGER.info(f"Syncing big plans for '{project.name}'")
                all_big_plans = self._big_plans_service.big_plans_sync(
                    project.ref_id, drop_all_notion, inbox_collection_link, filter_big_plan_ref_ids, sync_prefer)
                if anti_entropy_by_name:
                    all_big_plans = self._do_anti_entropy_for_big_plans(all_big_plans)
                if drop_all_notion_archived:
                    self._do_drop_all_big_plans(all_big_plans)
                self._inbox_tasks_service.upsert_notion_big_plan_ref_options(project.ref_id, all_big_plans)
            else:
                all_big_plans = self._big_plans_service.load_all_big_plans(
                    filter_archived=False, filter_ref_ids=filter_big_plan_ref_ids,
                    filter_project_ref_ids=[project.ref_id])
            big_plans_by_ref_id = {bp.ref_id: bp for bp in all_big_plans}

            if SyncTarget.RECURRING_TASKS in sync_targets:
                LOGGER.info(f"Syncing recurring tasks for '{project.name}'")
                all_recurring_tasks = self._recurring_tasks_service.recurring_tasks_sync(
                    project.ref_id, drop_all_notion, inbox_collection_link, filter_recurring_task_ref_ids, sync_prefer)
                if anti_entropy_by_name:
                    all_recurring_tasks = self._do_anti_entropy_for_recurring_tasks(all_recurring_tasks)
                if drop_all_notion_archived:
                    self._do_drop_all_recurring_tasks(all_recurring_tasks)
            else:
                all_recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
                    filter_archived=False, filter_ref_ids=filter_recurring_task_ref_ids,
                    filter_project_ref_ids=[project.ref_id])
            recurring_tasks_by_ref_id = {rt.ref_id: rt for rt in all_recurring_tasks}

            if SyncTarget.INBOX_TASKS in sync_targets:
                LOGGER.info(f"Syncing inbox tasks for '{project.name}'")
                all_inbox_tasks = self._inbox_tasks_service.inbox_tasks_sync(
                    project.ref_id, drop_all_notion, all_big_plans, all_recurring_tasks, filter_inbox_task_ref_ids,
                    sync_prefer)
                if anti_entropy_by_name:
                    all_inbox_tasks = self._do_anti_entropy_for_inbox_tasks(all_inbox_tasks)
                if drop_all_notion_archived:
                    self._do_drop_all_inbox_tasks(all_inbox_tasks)
            else:
                all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
                    filter_archived=False, filter_ref_ids=filter_inbox_task_ref_ids,
                    filter_project_ref_ids=[project.ref_id])

            if SyncTarget.RECURRING_TASKS in sync_targets:
                LOGGER.info(f"Syncing recurring tasks instances for '{project.name}'")
                for inbox_task in all_inbox_tasks:
                    if inbox_task.archived:
                        continue
                    if inbox_task.status.is_completed:
                        continue
                    if inbox_task.recurring_task_ref_id is None:
                        continue
                    if filter_recurring_task_ref_ids_set is not None \
                            and inbox_task.recurring_task_ref_id not in filter_recurring_task_ref_ids_set:
                        continue
                    LOGGER.info(f"Updating inbox task '{inbox_task.name}'")
                    recurring_task = recurring_tasks_by_ref_id[inbox_task.recurring_task_ref_id]
                    schedule = schedules.get_schedule(
                        recurring_task.period, recurring_task.name,
                        typing.cast(Timestamp, inbox_task.recurring_task_gen_right_now),
                        self._global_properties.timezone, recurring_task.skip_rule, recurring_task.due_at_time,
                        recurring_task.due_at_day, recurring_task.due_at_month)
                    self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                        ref_id=inbox_task.ref_id,
                        name=schedule.full_name,
                        due_time=schedule.due_time,
                        eisen=recurring_task.eisen,
                        difficulty=recurring_task.difficulty,
                        timeline=schedule.timeline,
                        period=recurring_task.period,
                        the_type=recurring_task.the_type)

            if SyncTarget.BIG_PLANS in sync_targets:
                LOGGER.info(f"Archiving any inbox task whose big plan has been archived")
                for inbox_task in all_inbox_tasks:
                    if inbox_task.big_plan_ref_id is None:
                        continue
                    if filter_big_plan_ref_ids is not None \
                            and inbox_task.big_plan_ref_id not in filter_big_plan_ref_ids:
                        continue
                    big_blan = big_plans_by_ref_id[inbox_task.big_plan_ref_id]
                    if not (big_blan.archived and not inbox_task.archived):
                        continue
                    self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
                    LOGGER.info(f"Archived inbox task {inbox_task.name}")

            if SyncTarget.RECURRING_TASKS in sync_targets:
                LOGGER.info(f"Archiving any inbox task whose recurring task has been archived")
                for inbox_task in all_inbox_tasks:
                    if inbox_task.recurring_task_ref_id is None:
                        continue
                    if filter_recurring_task_ref_ids is not None \
                            and inbox_task.recurring_task_ref_id not in filter_recurring_task_ref_ids:
                        continue
                    recurring_task = recurring_tasks_by_ref_id[inbox_task.recurring_task_ref_id]
                    if not (recurring_task.archived and not inbox_task.archived):
                        continue
                    self._inbox_tasks_service.archive_inbox_task(inbox_task.ref_id)
                    LOGGER.info(f"Archived inbox task {inbox_task.name}")

    def _do_anti_entropy_for_vacations(
            self, all_vacation: Iterable[Vacation]) -> Iterable[Vacation]:
        vacations_names_set = {}
        for vacation in all_vacation:
            if vacation.name in vacations_names_set:
                LOGGER.info(f"Found a duplicate vacation '{vacation.name}' - removing in anti-entropy")
                self._vacations_service.hard_remove_vacation(vacation.ref_id)
                continue
            vacations_names_set[vacation.name] = vacation
        return vacations_names_set.values()

    def _do_drop_all_archived_vacations(self, all_vacations: Iterable[Vacation]) -> None:
        for vacation in all_vacations:
            if not vacation.archived:
                continue
            LOGGER.info(f"Removed an archived vacation '{vacation.name}' on Notion side")
            self._vacations_service.remove_vacation_on_notion_side(vacation.ref_id)

    def _do_anti_entropy_for_big_plans(self, all_big_plans: Iterable[BigPlan]) -> Iterable[BigPlan]:
        big_plans_names_set = {}
        for big_plan in all_big_plans:
            if big_plan.name in big_plans_names_set:
                LOGGER.info(f"Found a duplicate big plan '{big_plan.name}' - removing in anti-entropy")
                self._inbox_tasks_service.hard_remove_inbox_task(big_plan.ref_id)
                continue
            big_plans_names_set[big_plan.name] = big_plan
        return big_plans_names_set.values()

    def _do_drop_all_big_plans(self, big_plans: Iterable[BigPlan]) -> None:
        for big_plan in big_plans:
            if not big_plan.archived:
                continue
            LOGGER.info(f"Removed an archived big plan '{big_plan.name}' on Notion side")
            self._big_plans_service.remove_big_plan_on_notion_side(big_plan.ref_id)

    def _do_anti_entropy_for_recurring_tasks(
            self, all_recurring_tasks: Iterable[RecurringTask]) -> Iterable[RecurringTask]:
        recurring_tasks_names_set = {}
        for recurring_task in all_recurring_tasks:
            if recurring_task.name in recurring_tasks_names_set:
                LOGGER.info(f"Found a duplicate recurring task '{recurring_task.name}' - removing in anti-entropy")
                self._recurring_tasks_service.hard_remove_recurring_task(recurring_task.ref_id)
                continue
            recurring_tasks_names_set[recurring_task.name] = recurring_task
        return recurring_tasks_names_set.values()

    def _do_drop_all_recurring_tasks(self, recurring_tasks: Iterable[RecurringTask]) -> None:
        for recurring_task in recurring_tasks:
            if not recurring_task.archived:
                continue
            LOGGER.info(f"Removed an archived recurring task '{recurring_task.name}' on Notion side")
            self._recurring_tasks_service.remove_recurring_task_on_notion_side(recurring_task.ref_id)

    def _do_anti_entropy_for_inbox_tasks(self, all_inbox_tasks: Iterable[InboxTask]) -> Iterable[InboxTask]:
        inbox_tasks_names_set = {}
        for inbox_task in all_inbox_tasks:
            if inbox_task.name in inbox_tasks_names_set:
                LOGGER.info(f"Found a duplicate inbox task '{inbox_task.name}' - removing in anti-entropy")
                self._inbox_tasks_service.hard_remove_inbox_task(inbox_task.ref_id)
                continue
            inbox_tasks_names_set[inbox_task.name] = inbox_task
        return inbox_tasks_names_set.values()

    def _do_drop_all_inbox_tasks(self, inbox_tasks: Iterable[InboxTask]) -> None:
        for inbox_task in inbox_tasks:
            if not inbox_task.archived:
                continue
            LOGGER.info(f"Removed an archived recurring task '{inbox_task.name}' on Notion side")
            self._inbox_tasks_service.remove_inbox_task_on_notion_side(inbox_task.ref_id)
