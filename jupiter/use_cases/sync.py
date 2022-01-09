"""Synchronise between Notion and local."""
import logging
import typing
from dataclasses import dataclass
from typing import Final, Optional, Iterable

from jupiter.domain import schedules
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.service.sync_service import BigPlanSyncService
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service \
    import InboxTaskBigPlanRefOptionsUpdateService
from jupiter.domain.inbox_tasks.service.sync_service import InboxTaskSyncService
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.service.sync_service import MetricSyncService
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager
from jupiter.domain.prm.person_birthday import PersonBirthday
from jupiter.domain.prm.service.sync_service import PrmSyncService
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.service.sync_service import ProjectSyncService
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager
from jupiter.domain.recurring_tasks.service.sync_service import RecurringTaskSyncService
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager
from jupiter.domain.smart_lists.service.sync_service import SmartListSyncService
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.storage_engine import StorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.sync_target import SyncTarget
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.service.sync_service import VacationSyncService
from jupiter.domain.workspaces.infra.workspace_notion_manager import WorkspaceNotionManager
from jupiter.domain.workspaces.service.sync_service import WorkspaceSyncService
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import UseCase
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class SyncUseCase(UseCase['SyncUseCase.Args', None]):
    """Synchronise between Notion and local."""

    @dataclass()
    class Args:
        """Args."""
        sync_targets: Iterable[SyncTarget]
        drop_all_notion: bool
        sync_even_if_not_modified: bool
        filter_vacation_ref_ids: Optional[Iterable[EntityId]]
        filter_project_keys: Optional[Iterable[ProjectKey]]
        filter_inbox_task_ref_ids: Optional[Iterable[EntityId]]
        filter_big_plan_ref_ids: Optional[Iterable[EntityId]]
        filter_recurring_task_ref_ids: Optional[Iterable[EntityId]]
        filter_smart_list_keys: Optional[Iterable[SmartListKey]]
        filter_smart_list_item_ref_ids: Optional[Iterable[EntityId]]
        filter_metric_keys: Optional[Iterable[MetricKey]]
        filter_metric_entry_ref_ids: Optional[Iterable[EntityId]]
        filter_person_ref_ids: Optional[Iterable[EntityId]]
        sync_prefer: SyncPrefer

    _global_properties: Final[GlobalProperties]
    _time_provider: Final[TimeProvider]
    _storage_engine: Final[StorageEngine]
    _workspace_notion_manager: Final[WorkspaceNotionManager]
    _vacation_notion_manager: Final[VacationNotionManager]
    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]
    _smart_list_notion_manager: Final[SmartListNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self,
            global_properties: GlobalProperties, time_provider: TimeProvider,
            storage_engine: StorageEngine, workspace_notion_manager: WorkspaceNotionManager,
            vacation_notion_manager: VacationNotionManager, project_notion_manager: ProjectNotionManager,
            inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_notion_manager: RecurringTaskNotionManager,
            big_plan_notion_manager: BigPlanNotionManager, smart_list_notion_manager: SmartListNotionManager,
            metric_notion_manager: MetricNotionManager, prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._global_properties = global_properties
        self._time_provider = time_provider
        self._storage_engine = storage_engine
        self._workspace_notion_manager = workspace_notion_manager
        self._vacation_notion_manager = vacation_notion_manager
        self._project_notion_manager = project_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_notion_manager = recurring_task_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager
        self._smart_list_notion_manager = smart_list_notion_manager
        self._metric_notion_manager = metric_notion_manager
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        filter_recurring_task_ref_ids_set = \
            frozenset(args.filter_recurring_task_ref_ids) if args.filter_recurring_task_ref_ids else None
        sync_targets = frozenset(args.sync_targets)

        notion_workspace = self._workspace_notion_manager.load_workspace()

        if SyncTarget.WORKSPACE in args.sync_targets:
            if SyncTarget.STRUCTURE in args.sync_targets:
                LOGGER.info("Recreating vacations structure")
                self._vacation_notion_manager.upsert_root_page(notion_workspace)

                LOGGER.info("Recreating projects structure")
                self._project_notion_manager.upsert_root_page(notion_workspace)

                LOGGER.info("Recreating lists structure")
                self._smart_list_notion_manager.upsert_root_page(notion_workspace)

                LOGGER.info("Recreating metrics structure")
                self._metric_notion_manager.upsert_root_page(notion_workspace)

                LOGGER.info("Recreating the PRM database structure")
                self._prm_notion_manager.upsert_root_notion_structure(notion_workspace)

            LOGGER.info("Syncing the workspace")
            workspace_sync_service = WorkspaceSyncService(self._storage_engine, self._workspace_notion_manager)
            workspace_sync_service.sync(right_now=self._time_provider.get_current_time(), sync_prefer=args.sync_prefer)

        if SyncTarget.VACATIONS in sync_targets:
            LOGGER.info("Syncing the vacations")
            vacation_sync_service = VacationSyncService(self._storage_engine, self._vacation_notion_manager)
            _ = vacation_sync_service.sync(
                args.drop_all_notion, args.sync_even_if_not_modified, args.filter_vacation_ref_ids, args.sync_prefer)

        with self._storage_engine.get_unit_of_work() as uow:
            all_smart_lists = uow.smart_list_repository.find_all(allow_archived=True)
            all_metrics = uow.metric_repository.find_all(allow_archived=True)
            all_persons = uow.person_repository.find_all(allow_archived=True)

        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.NOTION, time_provider=self._time_provider,
            storage_engine=self._storage_engine, inbox_task_notion_manager=self._inbox_task_notion_manager)

        if SyncTarget.PROJECTS in sync_targets \
                or SyncTarget.INBOX_TASKS in sync_targets \
                or SyncTarget.BIG_PLANS in sync_targets \
                or SyncTarget.RECURRING_TASKS in sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                all_projects = uow.project_repository.find_all(filter_keys=args.filter_project_keys)
            project_sync_service = ProjectSyncService(self._storage_engine, self._project_notion_manager)
            for project in all_projects:
                with self._storage_engine.get_unit_of_work() as uow:
                    inbox_task_collection = \
                        uow.inbox_task_collection_repository.load_by_project(project.ref_id)
                    recurring_task_collection = \
                        uow.recurring_task_collection_repository.load_by_project(project.ref_id)
                    big_plan_collection = \
                        uow.big_plan_collection_repository.load_by_project(project.ref_id)

                if SyncTarget.STRUCTURE in sync_targets:
                    LOGGER.info(f"Recreating project {project.name} structure")

                    notion_project = self._project_notion_manager.load_project(project.ref_id)
                    notion_project = notion_project.join_with_aggregate_root(project)
                    notion_project = self._project_notion_manager.save_project(notion_project)

                    LOGGER.info("Recreating inbox tasks")
                    notion_inbox_tasks_collection = \
                        self._inbox_task_notion_manager.load_inbox_task_collection(inbox_task_collection.ref_id)
                    notion_inbox_tasks_collection = \
                        notion_inbox_tasks_collection.join_with_aggregate_root(inbox_task_collection)
                    self._inbox_task_notion_manager.upsert_inbox_task_collection(
                        notion_project, notion_inbox_tasks_collection)

                    LOGGER.info("Recreating recurring tasks")
                    notion_recurring_task_collection = \
                        self._recurring_task_notion_manager.load_recurring_task_collection(
                            recurring_task_collection.ref_id)
                    notion_recurring_task_collection = \
                        notion_recurring_task_collection.join_with_aggregate_root(recurring_task_collection)
                    self._recurring_task_notion_manager.upsert_recurring_task_collection(
                        notion_project, notion_recurring_task_collection)

                    LOGGER.info("Recreating big plans")
                    notion_big_plan_collection = \
                        self._big_plan_notion_manager.load_big_plan_collection(big_plan_collection.ref_id)
                    notion_big_plan_collection = \
                        notion_big_plan_collection.join_with_aggregate_root(big_plan_collection)
                    self._big_plan_notion_manager.upsert_big_plan_collection(
                        notion_project, notion_big_plan_collection)

                notion_inbox_tasks_collection = \
                    self._inbox_task_notion_manager.load_inbox_task_collection(inbox_task_collection.ref_id)

                if SyncTarget.PROJECTS in sync_targets:
                    LOGGER.info(f"Syncing project '{project.name}'")
                    # TODO(horia141): this can be better!
                    project_sync_service.sync(self._time_provider.get_current_time(), [project.key], args.sync_prefer)

                if SyncTarget.BIG_PLANS in sync_targets:
                    LOGGER.info(f"Syncing big plans for '{project.name}'")
                    all_big_plans = \
                        BigPlanSyncService(self._time_provider, self._storage_engine, self._big_plan_notion_manager)\
                        .big_plans_sync(
                            project.ref_id, args.drop_all_notion, notion_inbox_tasks_collection,
                            args.sync_even_if_not_modified, args.filter_big_plan_ref_ids, args.sync_prefer)
                    InboxTaskBigPlanRefOptionsUpdateService(
                        self._storage_engine, self._inbox_task_notion_manager)\
                        .sync(big_plan_collection)
                else:
                    with self._storage_engine.get_unit_of_work() as uow:
                        big_plan_collection = \
                            uow.big_plan_collection_repository.load_by_project(project.ref_id)
                        all_big_plans = uow.big_plan_repository.find_all(
                            allow_archived=True, filter_ref_ids=args.filter_big_plan_ref_ids,
                            filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])
                big_plans_by_ref_id = {bp.ref_id: bp for bp in all_big_plans}

                if SyncTarget.RECURRING_TASKS in sync_targets:
                    LOGGER.info(f"Syncing recurring tasks for '{project.name}'")
                    recurring_task_sync_service = RecurringTaskSyncService(
                        self._time_provider, self._storage_engine, self._recurring_task_notion_manager)
                    all_recurring_tasks = recurring_task_sync_service.recurring_tasks_sync(
                        project.ref_id, args.drop_all_notion, notion_inbox_tasks_collection,
                        args.sync_even_if_not_modified, args.filter_recurring_task_ref_ids, args.sync_prefer)
                else:
                    with self._storage_engine.get_unit_of_work() as uow:
                        recurring_task_collection = \
                            uow.recurring_task_collection_repository.load_by_project(project.ref_id)
                        all_recurring_tasks = uow.recurring_task_repository.find_all(
                            allow_archived=True, filter_ref_ids=args.filter_recurring_task_ref_ids,
                            filter_recurring_task_collection_ref_ids=[recurring_task_collection.ref_id])
                recurring_tasks_by_ref_id = {rt.ref_id: rt for rt in all_recurring_tasks}

                if SyncTarget.INBOX_TASKS in args.sync_targets:
                    LOGGER.info(f"Syncing inbox tasks for '{project.name}'")
                    all_inbox_tasks = \
                        InboxTaskSyncService(
                            self._time_provider, self._storage_engine, self._inbox_task_notion_manager)\
                            .inbox_tasks_sync(
                                project.ref_id,
                                args.drop_all_notion,
                                all_big_plans,
                                args.sync_even_if_not_modified,
                                args.filter_inbox_task_ref_ids,
                                args.sync_prefer)
                else:
                    with self._storage_engine.get_unit_of_work() as uow:
                        inbox_task_collection = \
                            uow.inbox_task_collection_repository.load_by_project(project.ref_id)
                        all_inbox_tasks = uow.inbox_task_repository.find_all(
                            allow_archived=True, filter_ref_ids=args.filter_inbox_task_ref_ids,
                            filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])

                if SyncTarget.RECURRING_TASKS in args.sync_targets:
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
                            typing.cast(Timestamp, inbox_task.recurring_gen_right_now or inbox_task.created_time),
                            self._global_properties.timezone, recurring_task.skip_rule,
                            recurring_task.gen_params.actionable_from_day,
                            recurring_task.gen_params.actionable_from_month, recurring_task.gen_params.due_at_time,
                            recurring_task.gen_params.due_at_day, recurring_task.gen_params.due_at_month)

                        inbox_task = inbox_task.update_link_to_recurring_task(
                            name=schedule.full_name,
                            timeline=schedule.timeline,
                            the_type=recurring_task.the_type,
                            actionable_date=schedule.actionable_date,
                            due_time=schedule.due_time,
                            eisen=recurring_task.gen_params.eisen,
                            difficulty=recurring_task.gen_params.difficulty,
                            source=EventSource.NOTION,
                            modification_time=self._time_provider.get_current_time())

                        with self._storage_engine.get_unit_of_work() as uow:
                            uow.inbox_task_repository.save(inbox_task)

                        notion_inbox_task = \
                            self._inbox_task_notion_manager.load_inbox_task(
                                inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                        notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                            inbox_task, NotionInboxTask.DirectInfo(None))
                        self._inbox_task_notion_manager.save_inbox_task(
                            inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                        LOGGER.info("Applied Notion changes")

                if SyncTarget.BIG_PLANS in sync_targets:
                    LOGGER.info(f"Archiving any inbox task whose big plan has been archived")
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

                if SyncTarget.RECURRING_TASKS in sync_targets:
                    LOGGER.info(f"Archiving any inbox task whose recurring task has been archived")
                    for inbox_task in all_inbox_tasks:
                        if inbox_task.recurring_task_ref_id is None:
                            continue
                        if args.filter_recurring_task_ref_ids is not None \
                                and inbox_task.recurring_task_ref_id not in args.filter_recurring_task_ref_ids:
                            continue
                        recurring_task = recurring_tasks_by_ref_id[inbox_task.recurring_task_ref_id]
                        if not (recurring_task.archived and not inbox_task.archived):
                            continue
                        inbox_task_archive_service.do_it(inbox_task)
                        LOGGER.info(f"Archived inbox task {inbox_task.name}")

        if SyncTarget.SMART_LISTS in sync_targets:
            for smart_list in all_smart_lists:
                if args.filter_smart_list_keys is not None and smart_list.key not in args.filter_smart_list_keys:
                    LOGGER.info(f"Skipping smart list '{smart_list.name}' on account of filtering")
                    continue

                if SyncTarget.STRUCTURE in sync_targets:
                    LOGGER.info(f"Recreating smart list '{smart_list.name}'")
                    notion_smart_list = self._smart_list_notion_manager.load_smart_list(smart_list.ref_id)
                    notion_smart_list = notion_smart_list.join_with_aggregate_root(smart_list)
                    self._smart_list_notion_manager.upsert_smart_list(notion_smart_list)

                LOGGER.info(f"Syncing smart list '{smart_list.name}'")
                smart_list_sync_service = SmartListSyncService(self._storage_engine, self._smart_list_notion_manager)
                smart_list_sync_service.sync(
                    right_now=self._time_provider.get_current_time(), smart_list=smart_list,
                    drop_all_notion_side=args.drop_all_notion, sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_smart_list_item_ref_ids=args.filter_smart_list_item_ref_ids, sync_prefer=args.sync_prefer)

        if SyncTarget.METRICS in sync_targets:
            all_metrics_by_ref_id = {m.ref_id: m for m in all_metrics}
            for metric in all_metrics:
                if args.filter_metric_keys is not None and metric.key not in args.filter_metric_keys:
                    LOGGER.info(f"Skipping metric '{metric.name}' on account of filtering")
                    continue

                if SyncTarget.STRUCTURE in sync_targets:
                    LOGGER.info(f"Recreating metric '{metric.name}'")
                    notion_metric = self._metric_notion_manager.load_metric(metric.ref_id)
                    notion_metric = notion_metric.join_with_aggregate_root(metric)
                    self._metric_notion_manager.save_metric(notion_metric)

                LOGGER.info(f"Syncing metric '{metric.name}'")
                metric_sync_service = MetricSyncService(self._storage_engine, self._metric_notion_manager)
                metric_sync_service.sync(
                    right_now=self._time_provider.get_current_time(), metric=metric,
                    drop_all_notion_side=args.drop_all_notion,
                    sync_even_if_not_modified=args.sync_even_if_not_modified,
                    filter_metric_entry_ref_ids=args.filter_metric_entry_ref_ids, sync_prefer=args.sync_prefer)

            with self._storage_engine.get_unit_of_work() as uow:
                all_metric_collection_tasks = uow.inbox_task_repository.find_all(
                    allow_archived=True, filter_metric_ref_ids=[m.ref_id for m in all_metrics])

            for inbox_task in all_metric_collection_tasks:
                if inbox_task.archived:
                    continue
                metric = all_metrics_by_ref_id[typing.cast(EntityId, inbox_task.metric_ref_id)]
                if args.filter_metric_keys is not None and metric.key not in args.filter_metric_keys:
                    LOGGER.info(f"Skipping inbox task '{inbox_task.name}' on account of metric filtering")
                    continue
                LOGGER.info(f"Syncing inbox task '{inbox_task.name}'")
                collection_params = typing.cast(RecurringTaskGenParams, metric.collection_params)
                schedule = schedules.get_schedule(
                    typing.cast(RecurringTaskGenParams, metric.collection_params).period, metric.name,
                    typing.cast(Timestamp, inbox_task.recurring_gen_right_now), self._global_properties.timezone,
                    None, collection_params.actionable_from_day, collection_params.actionable_from_month,
                    collection_params.due_at_time, collection_params.due_at_day, collection_params.due_at_month)
                inbox_task = inbox_task.update_link_to_metric(
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

                notion_inbox_task = \
                    self._inbox_task_notion_manager.load_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                    inbox_task, NotionInboxTask.DirectInfo(None))
                self._inbox_task_notion_manager.save_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                LOGGER.info("Applied Notion changes")

        if SyncTarget.PRM in sync_targets:
            LOGGER.info("Syncing the PRM database")
            prm_sync_service = PrmSyncService(self._storage_engine, self._prm_notion_manager)
            persons = prm_sync_service.sync(
                drop_all_notion_side=args.drop_all_notion, sync_even_if_not_modified=args.sync_even_if_not_modified,
                filter_ref_ids=args.filter_person_ref_ids, sync_prefer=args.sync_prefer)
            all_persons_by_ref_id = {p.ref_id: p for p in persons}
            with self._storage_engine.get_unit_of_work() as uow:
                all_person_catch_up_tasks = uow.inbox_task_repository.find_all(
                    allow_archived=True, filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                    filter_person_ref_ids=[p.ref_id for p in all_persons])
                all_person_birthday_tasks = uow.inbox_task_repository.find_all(
                    allow_archived=True, filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                    filter_person_ref_ids=[p.ref_id for p in all_persons])

            for inbox_task in all_person_catch_up_tasks:
                if inbox_task.archived:
                    continue
                person = all_persons_by_ref_id[typing.cast(EntityId, inbox_task.person_ref_id)]
                if args.filter_person_ref_ids is not None and person.ref_id not in args.filter_person_ref_ids:
                    LOGGER.info(f"Skipping inbox task '{inbox_task.name}' on account of inbox task filterring")
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
                        name=schedule.full_name, recurring_timeline=schedule.timeline,
                        eisen=catch_up_params.eisen, difficulty=catch_up_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time,
                        source=EventSource.NOTION,
                        modification_time=self._time_provider.get_current_time())

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)

                    notion_inbox_task = \
                        self._inbox_task_notion_manager.load_inbox_task(
                            inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                    notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                        inbox_task, NotionInboxTask.DirectInfo(None))
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
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                        due_time=schedule.due_time,
                        source=EventSource.NOTION,
                        modification_time=self._time_provider.get_current_time())

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)

                    notion_inbox_task = \
                        self._inbox_task_notion_manager.load_inbox_task(
                            inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                    notion_inbox_task = notion_inbox_task.join_with_aggregate_root(
                        inbox_task, NotionInboxTask.DirectInfo(None))
                    self._inbox_task_notion_manager.save_inbox_task(
                        inbox_task.inbox_task_collection_ref_id, notion_inbox_task)
                    LOGGER.info("Applied Notion changes")
