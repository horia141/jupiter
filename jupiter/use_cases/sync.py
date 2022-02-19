"""Synchronise between Notion and local."""
import logging
import typing
from dataclasses import dataclass
from typing import Final, Optional, Iterable

from jupiter.domain import schedules
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
from jupiter.domain.big_plans.service.sync_service import BigPlanSyncService
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.notion_chore_collection import NotionChoreCollection
from jupiter.domain.chores.service.sync_service import ChoreSyncService
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit_collection import NotionHabitCollection
from jupiter.domain.habits.service.sync_service import HabitSyncService
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import NotionInboxTaskCollection
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service \
    import InboxTaskBigPlanRefOptionsUpdateService
from jupiter.domain.inbox_tasks.service.sync_service import InboxTaskSyncService
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.notion_metric_collection import NotionMetricCollection
from jupiter.domain.metrics.service.sync_service import MetricSyncService
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.persons.notion_person_collection import NotionPersonCollection
from jupiter.domain.persons.person_birthday import PersonBirthday
from jupiter.domain.persons.service.sync_service import PersonSyncService
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.notion_project_collection import NotionProjectCollection
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.service.project_label_update_service import ProjectLabelUpdateService
from jupiter.domain.projects.service.sync_service import ProjectSyncService
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.notion_smart_list_collection import NotionSmartListCollection
from jupiter.domain.smart_lists.service.sync_service import SmartListSyncService
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.sync_target import SyncTarget
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.notion_vacation_collection import NotionVacationCollection
from jupiter.domain.vacations.service.sync_service import VacationSyncService
from jupiter.domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from jupiter.domain.workspaces.service.sync_service import WorkspaceSyncService
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCaseArgsBase, MutationUseCaseInvocationRecorder
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SyncUseCase(AppMutationUseCase['SyncUseCase.Args', None]):
    """Synchronise between Notion and local."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""
        sync_targets: Iterable[SyncTarget]
        drop_all_notion: bool
        sync_even_if_not_modified: bool
        filter_vacation_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]
        filter_inbox_task_ref_ids: Optional[Iterable[EntityId]]
        filter_big_plan_ref_ids: Optional[Iterable[EntityId]]
        filter_habit_ref_ids: Optional[Iterable[EntityId]]
        filter_chore_ref_ids: Optional[Iterable[EntityId]]
        filter_smart_list_keys: Optional[Iterable[SmartListKey]]
        filter_smart_list_item_ref_ids: Optional[Iterable[EntityId]]
        filter_metric_keys: Optional[Iterable[MetricKey]]
        filter_metric_entry_ref_ids: Optional[Iterable[EntityId]]
        filter_person_ref_ids: Optional[Iterable[EntityId]]
        sync_prefer: SyncPrefer

    _global_properties: Final[GlobalProperties]
    _workspace_notion_manager: Final[WorkspaceNotionManager]
    _vacation_notion_manager: Final[VacationNotionManager]
    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]
    _smart_list_notion_manager: Final[SmartListNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]
    _person_notion_manager: Final[PersonNotionManager]

    def __init__(
            self,
            global_properties: GlobalProperties,
            time_provider: TimeProvider,
            invocation_recorder: MutationUseCaseInvocationRecorder,
            storage_engine: DomainStorageEngine,
            workspace_notion_manager: WorkspaceNotionManager,
            vacation_notion_manager: VacationNotionManager,
            project_notion_manager: ProjectNotionManager,
            inbox_task_notion_manager: InboxTaskNotionManager,
            habit_notion_manager: HabitNotionManager,
            chore_notion_manager: ChoreNotionManager,
            big_plan_notion_manager: BigPlanNotionManager,
            smart_list_notion_manager: SmartListNotionManager,
            metric_notion_manager: MetricNotionManager,
            person_notion_manager: PersonNotionManager) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._global_properties = global_properties
        self._workspace_notion_manager = workspace_notion_manager
        self._vacation_notion_manager = vacation_notion_manager
        self._project_notion_manager = project_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager
        self._chore_notion_manager = chore_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager
        self._smart_list_notion_manager = smart_list_notion_manager
        self._metric_notion_manager = metric_notion_manager
        self._person_notion_manager = person_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        filter_habit_ref_ids_set = \
            frozenset(args.filter_habit_ref_ids) if args.filter_habit_ref_ids else None
        filter_chore_ref_ids_set = \
            frozenset(args.filter_chore_ref_ids) if args.filter_chore_ref_ids else None
        sync_targets = frozenset(args.sync_targets)

        workspace = context.workspace
        notion_workspace = self._workspace_notion_manager.load_workspace(workspace.ref_id)

        with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = uow.vacation_collection_repository.load_by_workspace(workspace.ref_id)
            project_collection = uow.project_collection_repository.load_by_workspace(workspace.ref_id)
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_workspace(workspace.ref_id)
            habit_collection = uow.habit_collection_repository.load_by_workspace(workspace.ref_id)
            chore_collection = uow.chore_collection_repository.load_by_workspace(workspace.ref_id)
            big_plan_collection = uow.big_plan_collection_repository.load_by_workspace(workspace.ref_id)
            smart_list_collection = uow.smart_list_collection_repository.load_by_workspace(workspace.ref_id)
            metric_collection = uow.metric_collection_repository.load_by_workspace(workspace.ref_id)
            person_collection = uow.person_collection_repository.load_by_workspace(workspace.ref_id)

            all_smart_lists = \
                uow.smart_list_repository.find_all(
                    smart_list_collection_ref_id=smart_list_collection.ref_id, allow_archived=True)
            all_metrics = \
                uow.metric_repository.find_all(metric_collection_ref_id=metric_collection.ref_id, allow_archived=True)
            all_persons = \
                uow.person_repository.find_all(person_collection_ref_id=person_collection.ref_id, allow_archived=True)

        if SyncTarget.STRUCTURE in args.sync_targets:
            LOGGER.info("Recreating vacations structure")
            notion_vacation_collection = NotionVacationCollection.new_notion_row(vacation_collection)
            self._vacation_notion_manager.upsert_root_page(notion_workspace, notion_vacation_collection)

            LOGGER.info("Recreating projects structure")
            notion_project_collection = NotionProjectCollection.new_notion_row(project_collection)
            self._project_notion_manager.upsert_root_page(notion_workspace, notion_project_collection)

            LOGGER.info("Recreating inbox tasks structure")
            notion_inbox_task_collection = NotionInboxTaskCollection.new_notion_row(inbox_task_collection)
            self._inbox_task_notion_manager.upsert_inbox_task_collection(notion_workspace, notion_inbox_task_collection)

            LOGGER.info("Recreating habits structure")
            notion_habit_collection = NotionHabitCollection.new_notion_row(habit_collection)
            self._habit_notion_manager.upsert_habit_collection(notion_workspace, notion_habit_collection)

            LOGGER.info("Recreating chores structure")
            notion_chore_collection = NotionChoreCollection.new_notion_row(chore_collection)
            self._chore_notion_manager.upsert_chore_collection(notion_workspace, notion_chore_collection)

            LOGGER.info("Recreating big plan structure")
            notion_big_plan_collection = NotionBigPlanCollection.new_notion_row(big_plan_collection)
            self._big_plan_notion_manager.upsert_big_plan_collection(notion_workspace, notion_big_plan_collection)

            LOGGER.info("Recreating lists structure")
            notion_smart_list_collection = NotionSmartListCollection.new_notion_row(smart_list_collection)
            self._smart_list_notion_manager.upsert_root_page(notion_workspace, notion_smart_list_collection)

            LOGGER.info("Recreating metrics structure")
            notion_metric_collection = NotionMetricCollection.new_notion_row(metric_collection)
            self._metric_notion_manager.upsert_root_page(notion_workspace, notion_metric_collection)

            LOGGER.info("Recreating the persons structure")
            notion_person_collection = NotionPersonCollection.new_notion_row(person_collection)
            self._person_notion_manager.upsert_root_page(notion_workspace, notion_person_collection)

        if SyncTarget.WORKSPACE in args.sync_targets:
            LOGGER.info("Syncing the workspace")
            workspace_sync_service = WorkspaceSyncService(self._storage_engine, self._workspace_notion_manager)
            workspace = \
                workspace_sync_service.sync(
                    right_now=self._time_provider.get_current_time(), sync_prefer=args.sync_prefer)

        if SyncTarget.VACATIONS in sync_targets:
            LOGGER.info("Syncing the vacations")
            vacation_sync_service = VacationSyncService(self._storage_engine, self._vacation_notion_manager)
            vacation_sync_service.sync(
                workspace, args.drop_all_notion, args.sync_even_if_not_modified, args.filter_vacation_ref_ids,
                args.sync_prefer)

        if SyncTarget.PROJECTS in sync_targets:
            LOGGER.info("Syncing the projects")
            project_sync_service = ProjectSyncService(self._storage_engine, self._project_notion_manager)
            all_projects = project_sync_service.sync(
                workspace=workspace,
                filter_project_keys=args.filter_project_keys,
                drop_all_notion_side=args.drop_all_notion,
                sync_even_if_not_modified=args.sync_even_if_not_modified,
                sync_prefer=args.sync_prefer)

            ProjectLabelUpdateService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._habit_notion_manager,
                self._chore_notion_manager,
                self._big_plan_notion_manager) \
                .sync(workspace, all_projects)

        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.NOTION, time_provider=self._time_provider,
            storage_engine=self._storage_engine, inbox_task_notion_manager=self._inbox_task_notion_manager)

        notion_inbox_task_collection = \
            self._inbox_task_notion_manager.load_inbox_task_collection(inbox_task_collection.ref_id)

        with self._storage_engine.get_unit_of_work() as uow:
            all_projects = uow.project_repository.find_all(project_collection_ref_id=project_collection.ref_id)
        projects_by_ref_id = {p.ref_id: p for p in all_projects}
        filter_project_ref_ids = None
        if args.filter_project_keys:
            filter_project_ref_ids = [p.ref_id for p in all_projects if p.key in args.filter_project_keys]

        if SyncTarget.BIG_PLANS in sync_targets:
            LOGGER.info("Syncing big plans")
            big_plan_sync_service = \
                BigPlanSyncService(self._time_provider, self._storage_engine, self._big_plan_notion_manager)
            all_big_plans = \
                big_plan_sync_service.big_plans_sync(
                    workspace=workspace,
                    all_projects=all_projects,
                    inbox_task_collection=notion_inbox_task_collection,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_ref_ids=args.filter_big_plan_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                    sync_prefer=args.sync_prefer)
            InboxTaskBigPlanRefOptionsUpdateService(
                self._storage_engine, self._inbox_task_notion_manager) \
                .sync(big_plan_collection)
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_big_plans = uow.big_plan_repository.find_all(
                    big_plan_collection_ref_id=big_plan_collection.ref_id,
                    allow_archived=True, filter_ref_ids=args.filter_big_plan_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids)
        big_plans_by_ref_id = {bp.ref_id: bp for bp in all_big_plans}

        if SyncTarget.HABITS in sync_targets:
            LOGGER.info("Syncing habits")
            habit_sync_service = HabitSyncService(self._time_provider, self._storage_engine, self._habit_notion_manager)
            all_habits = \
                habit_sync_service.habits_sync(
                    workspace=workspace,
                    all_projects=all_projects,
                    inbox_task_collection=notion_inbox_task_collection,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_ref_ids=args.filter_habit_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                    sync_prefer=args.sync_prefer)
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_habits = uow.habit_repository.find_all(
                    habit_collection_ref_id=habit_collection.ref_id,
                    allow_archived=True, filter_ref_ids=args.filter_habit_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids)
        habits_by_ref_id = {rt.ref_id: rt for rt in all_habits}

        if SyncTarget.CHORES in sync_targets:
            LOGGER.info("Syncing chores")
            chore_sync_service = ChoreSyncService(self._time_provider, self._storage_engine, self._chore_notion_manager)
            all_chores = \
                chore_sync_service.chores_sync(
                    workspace=workspace,
                    all_projects=all_projects,
                    inbox_task_collection=notion_inbox_task_collection,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_ref_ids=args.filter_chore_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                    sync_prefer=args.sync_prefer)
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_chores = uow.chore_repository.find_all(
                    chore_collection_ref_id=chore_collection.ref_id,
                    allow_archived=True, filter_ref_ids=args.filter_chore_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids)
        chores_by_ref_id = {rt.ref_id: rt for rt in all_chores}

        if SyncTarget.INBOX_TASKS in args.sync_targets:
            LOGGER.info("Syncing inbox tasks")
            inbox_task_sync_service = \
                InboxTaskSyncService(self._time_provider, self._storage_engine, self._inbox_task_notion_manager)
            all_inbox_tasks = \
                inbox_task_sync_service.inbox_tasks_sync(
                    workspace=workspace,
                    all_projects=all_projects,
                    all_big_plans=all_big_plans,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_ref_ids=args.filter_inbox_task_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                    sync_prefer=args.sync_prefer)
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_inbox_tasks = uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_ref_ids=args.filter_inbox_task_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids)

        if SyncTarget.HABITS in args.sync_targets:
            LOGGER.info("Syncing inbox tasks generated by habits")
            for inbox_task in all_inbox_tasks:
                if inbox_task.archived:
                    continue
                if inbox_task.status.is_completed:
                    continue
                if inbox_task.habit_ref_id is None:
                    continue
                if filter_habit_ref_ids_set is not None \
                        and inbox_task.habit_ref_id not in filter_habit_ref_ids_set:
                    continue
                habit = habits_by_ref_id[inbox_task.habit_ref_id]
                project = projects_by_ref_id[habit.project_ref_id]
                if habit.last_modified_time < self._time_provider.get_current_time():
                    LOGGER.info(f"Skipping {inbox_task.name} because it was not modified")
                    continue
                LOGGER.info(f"Updating inbox task '{inbox_task.name}'")
                schedule = schedules.get_schedule(
                    habit.gen_params.period, habit.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now or inbox_task.created_time),
                    self._global_properties.timezone, habit.skip_rule,
                    habit.gen_params.actionable_from_day,
                    habit.gen_params.actionable_from_month, habit.gen_params.due_at_time,
                    habit.gen_params.due_at_day, habit.gen_params.due_at_month)

                inbox_task = inbox_task.update_link_to_habit(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    repeat_index=inbox_task.recurring_repeat_index,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    eisen=habit.gen_params.eisen,
                    difficulty=habit.gen_params.difficulty,
                    source=EventSource.NOTION,
                    modification_time=self._time_provider.get_current_time())

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")

        if SyncTarget.CHORES in args.sync_targets:
            LOGGER.info("Syncing inbox tasks generated by chores")
            for inbox_task in all_inbox_tasks:
                if inbox_task.archived:
                    continue
                if inbox_task.status.is_completed:
                    continue
                if inbox_task.chore_ref_id is None:
                    continue
                if filter_chore_ref_ids_set is not None \
                        and inbox_task.chore_ref_id not in filter_chore_ref_ids_set:
                    continue
                chore = chores_by_ref_id[inbox_task.chore_ref_id]
                project = projects_by_ref_id[chore.project_ref_id]
                if chore.last_modified_time < self._time_provider.get_current_time():
                    LOGGER.info(f"Skipping {inbox_task.name} because it was not modified")
                    continue
                LOGGER.info(f"Updating inbox task '{inbox_task.name}'")
                schedule = schedules.get_schedule(
                    chore.gen_params.period, chore.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now or inbox_task.created_time),
                    self._global_properties.timezone, chore.skip_rule,
                    chore.gen_params.actionable_from_day,
                    chore.gen_params.actionable_from_month, chore.gen_params.due_at_time,
                    chore.gen_params.due_at_day, chore.gen_params.due_at_month)

                inbox_task = inbox_task.update_link_to_chore(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    eisen=chore.gen_params.eisen,
                    difficulty=chore.gen_params.difficulty,
                    source=EventSource.NOTION,
                    modification_time=self._time_provider.get_current_time())

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")

        if SyncTarget.BIG_PLANS in sync_targets:
            LOGGER.info("Archiving any inbox task whose big plan has been archived")
            for inbox_task in all_inbox_tasks:
                if inbox_task.big_plan_ref_id is None:
                    continue
                if args.filter_big_plan_ref_ids is not None \
                        and inbox_task.big_plan_ref_id not in args.filter_big_plan_ref_ids:
                    continue
                big_blan = big_plans_by_ref_id[inbox_task.big_plan_ref_id]
                if not (big_blan.archived and not inbox_task.archived):
                    continue
                inbox_task_archive_service.do_it(inbox_task)
                LOGGER.info(f"Archived inbox task {inbox_task.name}")

        if SyncTarget.HABITS in sync_targets:
            LOGGER.info("Archiving any inbox task whose habit has been archived")
            for inbox_task in all_inbox_tasks:
                if inbox_task.habit_ref_id is None:
                    continue
                if args.filter_habit_ref_ids is not None \
                        and inbox_task.habit_ref_id not in args.filter_habit_ref_ids:
                    continue
                habit = habits_by_ref_id[inbox_task.habit_ref_id]
                if not (habit.archived and not inbox_task.archived):
                    continue
                inbox_task_archive_service.do_it(inbox_task)
                LOGGER.info(f"Archived inbox task {inbox_task.name}")

        if SyncTarget.CHORES in sync_targets:
            LOGGER.info("Archiving any inbox task whose chore has been archived")
            for inbox_task in all_inbox_tasks:
                if inbox_task.chore_ref_id is None:
                    continue
                if args.filter_chore_ref_ids is not None \
                        and inbox_task.chore_ref_id not in args.filter_chore_ref_ids:
                    continue
                chore = chores_by_ref_id[inbox_task.chore_ref_id]
                if not (chore.archived and not inbox_task.archived):
                    continue
                inbox_task_archive_service.do_it(inbox_task)
                LOGGER.info(f"Archived inbox task {inbox_task.name}")

        if SyncTarget.SMART_LISTS in sync_targets:
            for smart_list in all_smart_lists:
                if args.filter_smart_list_keys is not None and smart_list.key not in args.filter_smart_list_keys:
                    LOGGER.info(f"Skipping smart list '{smart_list.name}' on account of filtering")
                    continue

                LOGGER.info(f"Syncing smart list '{smart_list.name}'")
                smart_list_sync_service = SmartListSyncService(self._storage_engine, self._smart_list_notion_manager)
                smart_list_sync_service.sync(
                    workspace=workspace,
                    right_now=self._time_provider.get_current_time(),
                    smart_list=smart_list,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_smart_list_item_ref_ids=args.filter_smart_list_item_ref_ids,
                    sync_prefer=args.sync_prefer)

        if SyncTarget.METRICS in sync_targets:
            all_metrics_by_ref_id = {m.ref_id: m for m in all_metrics}
            for metric in all_metrics:
                if args.filter_metric_keys is not None and metric.key not in args.filter_metric_keys:
                    LOGGER.info(f"Skipping metric '{metric.name}' on account of filtering")
                    continue

                LOGGER.info(f"Syncing metric '{metric.name}'")
                metric_sync_service = MetricSyncService(self._storage_engine, self._metric_notion_manager)
                metric_sync_service.sync(
                    workspace=workspace,
                    right_now=self._time_provider.get_current_time(),
                    metric=metric,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_metric_entry_ref_ids=args.filter_metric_entry_ref_ids,
                    sync_prefer=args.sync_prefer)

            with self._storage_engine.get_unit_of_work() as uow:
                all_metric_collection_tasks = \
                    uow.inbox_task_repository.find_all(
                        inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True, filter_sources=[InboxTaskSource.METRIC],
                        filter_metric_ref_ids=[m.ref_id for m in all_metrics])

            for inbox_task in all_metric_collection_tasks:
                if inbox_task.archived:
                    continue
                metric = all_metrics_by_ref_id[typing.cast(EntityId, inbox_task.metric_ref_id)]
                project = projects_by_ref_id[metric_collection.collection_project_ref_id]
                if args.filter_metric_keys is not None and metric.key not in args.filter_metric_keys:
                    LOGGER.info(f"Skipping inbox task '{inbox_task.name}' on account of metric filtering")
                    continue
                if metric.last_modified_time < self._time_provider.get_current_time():
                    LOGGER.info(f"Skipping {inbox_task.name} because it was not modified")
                    continue
                LOGGER.info(f"Syncing inbox task '{inbox_task.name}'")
                collection_params = typing.cast(RecurringTaskGenParams, metric.collection_params)
                schedule = schedules.get_schedule(
                    typing.cast(RecurringTaskGenParams, metric.collection_params).period, metric.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, collection_params.actionable_from_day, collection_params.actionable_from_month,
                    collection_params.due_at_time, collection_params.due_at_day, collection_params.due_at_month)
                inbox_task = \
                    inbox_task.update_link_to_metric(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        eisen=collection_params.eisen,
                        difficulty=collection_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time,
                        source=EventSource.NOTION,
                        modification_time=self._time_provider.get_current_time())

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)

                direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")

        if SyncTarget.PERSONS in sync_targets:
            LOGGER.info("Syncing the persons")
            project = projects_by_ref_id[person_collection.catch_up_project_ref_id]
            person_sync_service = PersonSyncService(self._storage_engine, self._person_notion_manager)
            persons = \
                person_sync_service.sync(
                    workspace=workspace,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_ref_ids=args.filter_person_ref_ids,
                    sync_prefer=args.sync_prefer)
            all_persons_by_ref_id = {p.ref_id: p for p in persons}
            with self._storage_engine.get_unit_of_work() as uow:
                all_person_catch_up_tasks = uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                    filter_person_ref_ids=[p.ref_id for p in all_persons])
                all_person_birthday_tasks = uow.inbox_task_repository.find_all(
                    inbox_task_collection_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True, filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                    filter_person_ref_ids=[p.ref_id for p in all_persons])

            for inbox_task in all_person_catch_up_tasks:
                if inbox_task.archived:
                    continue
                person = all_persons_by_ref_id[typing.cast(EntityId, inbox_task.person_ref_id)]
                if args.filter_person_ref_ids is not None and person.ref_id not in args.filter_person_ref_ids:
                    LOGGER.info(f"Skipping inbox task '{inbox_task.name}' on account of inbox task filterring")
                    continue
                if person.last_modified_time < self._time_provider.get_current_time():
                    LOGGER.info(f"Skipping {inbox_task.name} because it was not modified")
                    continue
                LOGGER.info(f"Syncing inbox task '{inbox_task.name}'")
                if person.archived:
                    if not inbox_task.archived:
                        inbox_task_archive_service.do_it(inbox_task)
                else:
                    catch_up_params = typing.cast(RecurringTaskGenParams, person.catch_up_params)
                    schedule = schedules.get_schedule(
                        typing.cast(RecurringTaskGenParams, person.catch_up_params).period, person.name,
                        typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                        None, catch_up_params.actionable_from_day, catch_up_params.actionable_from_month,
                        catch_up_params.due_at_time, catch_up_params.due_at_day, catch_up_params.due_at_month)
                    inbox_task = inbox_task.update_link_to_person_catch_up(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        eisen=catch_up_params.eisen,
                        difficulty=catch_up_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time,
                        source=EventSource.NOTION,
                        modification_time=self._time_provider.get_current_time())

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)

                    direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                    notion_inbox_task = \
                        self._inbox_task_notion_manager.load_inbox_task(
                            inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                    notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
                    self._inbox_task_notion_manager.save_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                    LOGGER.info("Applied Notion changes")

            for inbox_task in all_person_birthday_tasks:
                if inbox_task.archived:
                    continue
                person = all_persons_by_ref_id[typing.cast(EntityId, inbox_task.person_ref_id)]
                if args.filter_person_ref_ids is not None and person.ref_id not in args.filter_person_ref_ids:
                    LOGGER.info(f"Skipping inbox task '{inbox_task.name}' on account of inbox task filterring")
                    continue
                if person.last_modified_time < self._time_provider.get_current_time():
                    LOGGER.info(f"Skipping {inbox_task.name} because it was not modified")
                    continue
                LOGGER.info(f"Syncing inbox task '{inbox_task.name}'")
                if person.archived:
                    if not inbox_task.archived:
                        inbox_task_archive_service.do_it(inbox_task)
                else:
                    birthday = typing.cast(PersonBirthday, person.birthday)
                    schedule = schedules.get_schedule(
                        RecurringTaskPeriod.YEARLY, person.name,
                        typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                        None, None, None, None,
                        RecurringTaskDueAtDay.from_raw(RecurringTaskPeriod.MONTHLY, birthday.day),
                        RecurringTaskDueAtMonth.from_raw(RecurringTaskPeriod.YEARLY, birthday.month))
                    inbox_task = inbox_task.update_link_to_person_birthday(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                        due_time=schedule.due_time,
                        source=EventSource.NOTION,
                        modification_time=self._time_provider.get_current_time())

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)

                    direct_info = NotionInboxTask.DirectInfo(project_name=project.name, big_plan_name=None)
                    notion_inbox_task = \
                        self._inbox_task_notion_manager.load_inbox_task(
                            inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                    notion_inbox_task = notion_inbox_task.join_with_aggregate_root(inbox_task, direct_info)
                    self._inbox_task_notion_manager.save_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                    LOGGER.info("Applied Notion changes")
