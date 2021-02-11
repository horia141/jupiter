"""The controller for syncing the local and Notion data."""
import logging
from typing import Final, Optional, Iterable

import typing

from models import schedules
from models.basic import SyncPrefer, ProjectKey, SyncTarget, EntityId, Timestamp, SmartListKey, MetricKey
from remote.notion.inbox_tasks_manager import InboxTaskBigPlanLabel
from service.big_plans import BigPlansService
from service.inbox_tasks import InboxTasksService
from service.metrics import MetricsService
from service.smart_lists import SmartListsService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService
from service.vacations import VacationsService
from service.workspaces import WorkspacesService
from utils.global_properties import GlobalProperties
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SyncLocalAndNotionController:
    """The controller for syncing the local and Notion data."""

    _time_provider: Final[TimeProvider]
    _global_properties: Final[GlobalProperties]
    _workspaces_service: Final[WorkspacesService]
    _vacations_service: Final[VacationsService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]
    _smart_lists_service: Final[SmartListsService]
    _metrics_service: Final[MetricsService]

    def __init__(
            self, time_provider: TimeProvider, global_properties: GlobalProperties,
            workspaces_service: WorkspacesService, vacations_service: VacationsService,
            projects_service: ProjectsService, inbox_tasks_service: InboxTasksService,
            recurring_tasks_service: RecurringTasksService, big_plans_service: BigPlansService,
            smart_lists_service: SmartListsService, metrics_service: MetricsService) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._global_properties = global_properties
        self._workspaces_service = workspaces_service
        self._vacations_service = vacations_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service
        self._smart_lists_service = smart_lists_service
        self._metrics_service = metrics_service

    def sync(
            self,
            sync_targets: Iterable[SyncTarget],
            drop_all_notion: bool,
            sync_even_if_not_modified: bool,
            filter_vacation_ref_ids: Optional[Iterable[EntityId]],
            filter_project_keys: Optional[Iterable[ProjectKey]],
            filter_inbox_task_ref_ids: Optional[Iterable[EntityId]],
            filter_big_plan_ref_ids: Optional[Iterable[EntityId]],
            filter_recurring_task_ref_ids: Optional[Iterable[EntityId]],
            filter_smart_list_keys: Optional[Iterable[SmartListKey]],
            filter_smart_list_item_ref_ids: Optional[Iterable[EntityId]],
            filter_metric_keys: Optional[Iterable[MetricKey]],
            filter_metric_entry_ref_ids: Optional[Iterable[EntityId]],
            sync_prefer: SyncPrefer = SyncPrefer.NOTION) -> None:
        """Sync the local and Notion data."""
        filter_recurring_task_ref_ids_set = \
            frozenset(filter_recurring_task_ref_ids) if filter_recurring_task_ref_ids else None
        sync_targets = frozenset(sync_targets)

        if SyncTarget.STRUCTURE in sync_targets:
            LOGGER.info("Recreating workspace page")
            workspace_page = self._workspaces_service.get_workspace_notion_structure()

            LOGGER.info("Recreating vacations structure")
            self._vacations_service.upsert_root_notion_structure(workspace_page)

            LOGGER.info("Recreating projects structure")
            self._projects_service.upsert_root_notion_structure(workspace_page)

            LOGGER.info("Recreating lists structure")
            self._smart_lists_service.upsert_root_notion_structure(workspace_page)

            LOGGER.info("Recreating metrics structure")
            self._metrics_service.upsert_root_notion_structure(workspace_page)

        if SyncTarget.WORKSPACE in sync_targets:
            LOGGER.info("Syncing the workspace")
            self._workspaces_service.workspace_sync(sync_prefer)

        if SyncTarget.VACATIONS in sync_targets:
            LOGGER.info("Syncing the vacations")
            _ = self._vacations_service.vacations_sync(
                drop_all_notion, sync_even_if_not_modified, filter_vacation_ref_ids, sync_prefer)

        for project in self._projects_service.load_all_projects(filter_keys=filter_project_keys):
            if SyncTarget.STRUCTURE in sync_targets:
                LOGGER.info(f"Recreating project {project.name} structure")
                project_page = self._projects_service.upsert_project_structure(project.ref_id)
                LOGGER.info("Recreating inbox tasks")
                self._inbox_tasks_service.upsert_inbox_tasks_collection_structure(
                    project.ref_id, project_page.notion_page_link)
                LOGGER.info("Recreating recurring tasks")
                self._recurring_tasks_service.upsert_recurring_tasks_collection_structure(
                    project.ref_id, project_page.notion_page_link)
                LOGGER.info("Recreating big plans")
                self._big_plans_service.upsert_big_plans_collection_structure(
                    project.ref_id, project_page.notion_page_link)

            inbox_tasks_collection = self._inbox_tasks_service.get_inbox_tasks_collection(project.ref_id)

            if SyncTarget.PROJECTS in sync_targets:
                LOGGER.info(f"Syncing project '{project.name}'")
                self._projects_service.sync_projects(project.ref_id, sync_prefer)

            if SyncTarget.BIG_PLANS in sync_targets:
                LOGGER.info(f"Syncing big plans for '{project.name}'")
                all_big_plans = self._big_plans_service.big_plans_sync(
                    project.ref_id, drop_all_notion, inbox_tasks_collection, sync_even_if_not_modified,
                    filter_big_plan_ref_ids, sync_prefer)
                self._inbox_tasks_service.upsert_notion_big_plan_ref_options(
                    project.ref_id,
                    [InboxTaskBigPlanLabel(notion_link_uuid=bp.notion_link_uuid, name=bp.name) for bp in all_big_plans])
            else:
                all_big_plans = self._big_plans_service.load_all_big_plans(
                    allow_archived=True, filter_ref_ids=filter_big_plan_ref_ids,
                    filter_project_ref_ids=[project.ref_id])
            big_plans_by_ref_id = {bp.ref_id: bp for bp in all_big_plans}

            if SyncTarget.RECURRING_TASKS in sync_targets:
                LOGGER.info(f"Syncing recurring tasks for '{project.name}'")
                all_recurring_tasks = self._recurring_tasks_service.recurring_tasks_sync(
                    project.ref_id, drop_all_notion, inbox_tasks_collection, sync_even_if_not_modified,
                    filter_recurring_task_ref_ids, sync_prefer)
            else:
                all_recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
                    allow_archived=True, filter_ref_ids=filter_recurring_task_ref_ids,
                    filter_project_ref_ids=[project.ref_id])
            recurring_tasks_by_ref_id = {rt.ref_id: rt for rt in all_recurring_tasks}

            if SyncTarget.INBOX_TASKS in sync_targets:
                LOGGER.info(f"Syncing inbox tasks for '{project.name}'")
                all_inbox_tasks = self._inbox_tasks_service.inbox_tasks_sync(
                    project.ref_id, drop_all_notion, all_big_plans, all_recurring_tasks, sync_even_if_not_modified,
                    filter_inbox_task_ref_ids, sync_prefer)
            else:
                all_inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
                    allow_archived=True, filter_ref_ids=filter_inbox_task_ref_ids,
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
                    recurring_task = recurring_tasks_by_ref_id[inbox_task.recurring_task_ref_id]
                    if recurring_task.last_modified_time < self._time_provider.get_current_time():
                        LOGGER.info(f"Skipping {inbox_task.name} because it was not modified")
                        continue
                    LOGGER.info(f"Updating inbox task '{inbox_task.name}'")
                    schedule = schedules.get_schedule(
                        recurring_task.period, recurring_task.name,
                        typing.cast(Timestamp, inbox_task.recurring_task_gen_right_now or inbox_task.created_time),
                        self._global_properties.timezone, recurring_task.skip_rule, recurring_task.actionable_from_day,
                        recurring_task.actionable_from_month, recurring_task.due_at_time, recurring_task.due_at_day,
                        recurring_task.due_at_month)
                    self._inbox_tasks_service.set_inbox_task_to_recurring_task_link(
                        ref_id=inbox_task.ref_id,
                        name=schedule.full_name,
                        actionable_date=schedule.actionable_date,
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

        for smart_list in self._smart_lists_service.load_all_smart_lists(filter_keys=filter_smart_list_keys):
            if SyncTarget.STRUCTURE in sync_targets:
                LOGGER.info(f"Recreating smart list '{smart_list.name}'")
                self._smart_lists_service.upsert_smart_list_structure(smart_list.ref_id)

            if SyncTarget.SMART_LISTS in sync_targets:
                LOGGER.info(f"Syncing smart list '{smart_list.name}'")
                self._smart_lists_service.sync_smart_list_and_smart_list_items(
                    smart_list_ref_id=smart_list.ref_id, drop_all_notion_side=drop_all_notion,
                    sync_even_if_not_modified=sync_even_if_not_modified,
                    filter_smart_list_item_ref_ids=filter_smart_list_item_ref_ids, sync_prefer=sync_prefer)

        for metric in self._metrics_service.load_all_metrics(filter_keys=filter_metric_keys):
            if SyncTarget.STRUCTURE in sync_targets:
                LOGGER.info(f"Recreating metric '{metric.name}'")
                self._metrics_service.upsert_metric_structure(metric.ref_id)

            if SyncTarget.METRICS in sync_targets:
                LOGGER.info(f"Syncing metric '{metric.name}'")
                self._metrics_service.sync_metric_and_metric_entries(
                    metric_ref_id=metric.ref_id, drop_all_notion_side=drop_all_notion,
                    sync_even_if_not_modified=sync_even_if_not_modified,
                    filter_metric_entry_ref_ids=filter_metric_entry_ref_ids, sync_prefer=sync_prefer)
