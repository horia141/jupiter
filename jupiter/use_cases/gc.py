"""The command for doing a garbage collection run."""
import logging
from dataclasses import dataclass
from typing import Final, Optional, Iterable

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.infra.big_plan_engine import BigPlanEngine
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager, NotionBigPlanNotFoundError
from jupiter.domain.big_plans.service.archive_service import BigPlanArchiveService
from jupiter.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.infra.inbox_task_engine import InboxTaskEngine
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import InboxTaskNotionManager
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service \
    import InboxTaskBigPlanRefOptionsUpdateService
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.metrics.infra.metric_engine import MetricEngine
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager, NotionMetricNotFoundError, \
    NotionMetricEntryNotFoundError
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.domain.prm.infra.prm_engine import PrmEngine
from jupiter.domain.prm.infra.prm_notion_manager import PrmNotionManager, NotionPersonNotFoundError
from jupiter.domain.prm.person import Person
from jupiter.domain.prm.service.remove_service import PersonRemoveService
from jupiter.domain.projects.infra.project_engine import ProjectEngine
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.recurring_tasks.infra.recurring_task_engine import RecurringTaskEngine
from jupiter.domain.recurring_tasks.infra.recurring_task_notion_manager import RecurringTaskNotionManager, \
    NotionRecurringTaskNotFoundError
from jupiter.domain.recurring_tasks.recurring_task import RecurringTask
from jupiter.domain.recurring_tasks.service.remove_service import RecurringTaskRemoveService
from jupiter.domain.smart_lists.infra.smart_list_engine import SmartListEngine
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import SmartListNotionManager,\
    NotionSmartListNotFoundError, NotionSmartListItemNotFoundError
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.sync_target import SyncTarget
from jupiter.domain.vacations.infra.vacation_engine import VacationEngine
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager, NotionVacationNotFoundError
from jupiter.domain.vacations.vacation import Vacation
from jupiter.framework.use_case import UseCase
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class GCUseCase(UseCase['GCUseCase.Args', None]):
    """The command for doing a garbage collection run."""

    @dataclass()
    class Args:
        """Args."""
        sync_targets: Iterable[SyncTarget]
        project_keys: Optional[Iterable[ProjectKey]]
        do_archival: bool
        do_anti_entropy: bool
        do_notion_cleanup: bool

    _time_provider: Final[TimeProvider]
    _vacation_engine: Final[VacationEngine]
    _vacation_notion_manager: Final[VacationNotionManager]
    _project_engine: Final[ProjectEngine]
    _inbox_task_engine: Final[InboxTaskEngine]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _recurring_task_engine: Final[RecurringTaskEngine]
    _recurring_task_notion_manager: Final[RecurringTaskNotionManager]
    _big_plan_engine: Final[BigPlanEngine]
    _big_plan_notion_manager: Final[BigPlanNotionManager]
    _smart_list_engine: Final[SmartListEngine]
    _smart_list_notion_manager: Final[SmartListNotionManager]
    _metric_engine: Final[MetricEngine]
    _metric_notion_manager: Final[MetricNotionManager]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, vacation_engine: VacationEngine,
            vacation_notion_manager: VacationNotionManager, project_engine: ProjectEngine,
            inbox_task_engine: InboxTaskEngine, inbox_task_notion_manager: InboxTaskNotionManager,
            recurring_task_engine: RecurringTaskEngine, recurring_task_notion_manager: RecurringTaskNotionManager,
            big_plan_engine: BigPlanEngine, big_plan_notion_manager: BigPlanNotionManager,
            smart_list_engine: SmartListEngine,
            smart_list_notion_manager: SmartListNotionManager,
            metric_engine: MetricEngine, metric_notion_manager: MetricNotionManager, prm_engine: PrmEngine,
            prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._vacation_engine = vacation_engine
        self._vacation_notion_manager = vacation_notion_manager
        self._project_engine = project_engine
        self._inbox_task_engine = inbox_task_engine
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._recurring_task_engine = recurring_task_engine
        self._recurring_task_notion_manager = recurring_task_notion_manager
        self._big_plan_engine = big_plan_engine
        self._big_plan_notion_manager = big_plan_notion_manager
        self._smart_list_engine = smart_list_engine
        self._smart_list_notion_manager = smart_list_notion_manager
        self._metric_engine = metric_engine
        self._metric_notion_manager = metric_notion_manager
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager

    def execute(self, args: Args) -> None:
        """Execute the command's action."""
        if SyncTarget.VACATIONS in args.sync_targets:
            if args.do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for vacations")
                with self._vacation_engine.get_unit_of_work() as vacation_uow:
                    vacations = vacation_uow.vacation_repository.find_all(allow_archived=True)
                self._do_anti_entropy_for_vacations(vacations)
            if args.do_notion_cleanup:
                LOGGER.info(f"Garbage collecting vacations which were archived")

                allowed_ref_ids = self._vacation_notion_manager.load_all_saved_vacation_ref_ids()

                with self._vacation_engine.get_unit_of_work() as vacation_uow:
                    vacations = vacation_uow.vacation_repository.find_all(allow_archived=True,
                                                                          filter_ref_ids=allowed_ref_ids)
                self._do_drop_all_archived_vacations(vacations)

        with self._project_engine.get_unit_of_work() as project_uow:
            all_projects = project_uow.project_repository.find_all(filter_keys=args.project_keys)

        for project in all_projects:
            LOGGER.info(f"Garbage collecting project '{project.name}'")

            if SyncTarget.INBOX_TASKS in args.sync_targets:
                with self._inbox_task_engine.get_unit_of_work() as uow:
                    inbox_task_collection = uow.inbox_task_collection_repository.load_by_project(project.ref_id)
                if args.do_archival:
                    LOGGER.info(f"Archiving all done inbox tasks")
                    self._archive_done_inbox_tasks_for_project(project)
                if args.do_anti_entropy:
                    LOGGER.info(f"Performing anti-entropy adjustments for inbox tasks")
                    with self._inbox_task_engine.get_unit_of_work() as uow:
                        inbox_tasks = uow.inbox_task_repository.find_all(
                            allow_archived=True, filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])
                    self._do_anti_entropy_for_inbox_tasks(inbox_tasks)
                if args.do_notion_cleanup:
                    LOGGER.info(f"Garbage collecting inbox tasks which were archived")
                    allowed_ref_ids = \
                        self._inbox_task_notion_manager.load_all_saved_inbox_tasks_ref_ids(inbox_task_collection.ref_id)
                    with self._inbox_task_engine.get_unit_of_work() as uow:
                        inbox_tasks = uow.inbox_task_repository.find_all(
                            allow_archived=True, filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id],
                            filter_ref_ids=allowed_ref_ids)
                    self._do_drop_all_archived_inbox_tasks(inbox_tasks)

            if SyncTarget.RECURRING_TASKS in args.sync_targets:
                if args.do_anti_entropy:
                    LOGGER.info(f"Performing anti-entropy adjustments for recurring tasks")
                    with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
                        recurring_task_collection = \
                            recurring_task_uow.recurring_task_collection_repository.load_by_project(project.ref_id)
                        recurring_tasks = recurring_task_uow.recurring_task_repository.find_all(
                            allow_archived=True,
                            filter_recurring_task_collection_ref_ids=[recurring_task_collection.ref_id])
                    self._do_anti_entropy_for_recurring_tasks(recurring_tasks)
                if args.do_notion_cleanup:
                    LOGGER.info(f"Garbage collecting recurring tasks which were archived")
                    allowed_ref_ids = \
                        self._recurring_task_notion_manager.load_all_saved_recurring_tasks_ref_ids(
                            recurring_task_collection.ref_id)
                    with self._recurring_task_engine.get_unit_of_work() as recurring_task_uow:
                        recurring_task_collection = \
                            recurring_task_uow.recurring_task_collection_repository.load_by_project(project.ref_id)
                        recurring_tasks = \
                            recurring_task_uow.recurring_task_repository.find_all(
                                allow_archived=True, filter_ref_ids=allowed_ref_ids,
                                filter_recurring_task_collection_ref_ids=[recurring_task_collection.ref_id])
                    self._do_drop_all_archived_recurring_tasks(recurring_tasks)

            if SyncTarget.BIG_PLANS in args.sync_targets:
                with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
                    big_plan_collection = big_plan_uow.big_plan_collection_repository.load_by_project(project.ref_id)
                if args.do_archival:
                    LOGGER.info(f"Archiving all done big plans")
                    self._archive_done_big_plans_for_project(project)
                if args.do_anti_entropy:
                    LOGGER.info(f"Performing anti-entropy adjustments for big plans")
                    with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
                        big_plans = big_plan_uow.big_plan_repository.find_all(
                            allow_archived=True, filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])
                    self._do_anti_entropy_for_big_plans(big_plans)
                if args.do_notion_cleanup:
                    LOGGER.info(f"Garbage collecting big plans which were archived")
                    allowed_ref_ids = \
                        self._big_plan_notion_manager.load_all_saved_big_plans_ref_ids(big_plan_collection.ref_id)
                    with self._big_plan_engine.get_unit_of_work() as big_plan_uow:
                        big_plans = \
                            big_plan_uow.big_plan_repository.find_all(
                                allow_archived=True, filter_ref_ids=allowed_ref_ids,
                                filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])
                    self._do_drop_all_archived_big_plans(big_plans)

                InboxTaskBigPlanRefOptionsUpdateService(
                    self._big_plan_engine, self._inbox_task_engine, self._inbox_task_notion_manager)\
                    .sync(big_plan_collection)

        if SyncTarget.SMART_LISTS in args.sync_targets:
            smart_lists: Iterable[SmartList] = []
            if args.do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for smart lists")
                with self._smart_list_engine.get_unit_of_work() as smart_list_uow:
                    smart_lists = smart_list_uow.smart_list_repository.find_all(allow_archived=True)
                smart_lists = self._do_anti_entropy_for_smart_lists(smart_lists)
            if args.do_notion_cleanup:
                LOGGER.info(f"Garbage collecting smart lists which were archived")
                with self._smart_list_engine.get_unit_of_work() as smart_list_uow:
                    smart_lists = smart_lists or smart_list_uow.smart_list_repository.find_all(allow_archived=True)
                self._do_drop_all_archived_smart_lists(smart_lists)
            if args.do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for smart list items")
                with self._smart_list_engine.get_unit_of_work() as smart_list_uow:
                    smart_list_items = smart_list_uow.smart_list_item_repository.find_all(allow_archived=True)
                self._do_anti_entropy_for_smart_list_items(smart_list_items)
            if args.do_notion_cleanup:
                LOGGER.info(f"Garbage collecting smart list items which were archived")
                for smart_list in smart_lists:
                    allowed_ref_ids = set(
                        self._smart_list_notion_manager.load_all_saved_smart_list_items_ref_ids(smart_list.ref_id))
                    with self._smart_list_engine.get_unit_of_work() as smart_list_uow:
                        smart_list_items = smart_list_uow.smart_list_item_repository.find_all(
                            allow_archived=True, filter_ref_ids=allowed_ref_ids,
                            filter_smart_list_ref_ids=[smart_list.ref_id])
                    self._do_drop_all_archived_smart_list_items(smart_list_items)

        if SyncTarget.METRICS in args.sync_targets:
            metrics: Iterable[Metric] = []
            if args.do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for metrics")
                with self._metric_engine.get_unit_of_work() as metric_uow:
                    metrics = metric_uow.metric_repository.find_all(allow_archived=True)
                metrics = self._do_anti_entropy_for_metrics(metrics)
            if args.do_notion_cleanup:
                LOGGER.info(f"Garbage collecting metrics which were archived")
                with self._metric_engine.get_unit_of_work() as metric_uow:
                    metrics = metrics or metric_uow.metric_repository.find_all(allow_archived=True)
                self._do_drop_all_archived_metrics(metrics)
            if args.do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for metric entries")
                with self._metric_engine.get_unit_of_work() as metric_uow:
                    metric_entries = metric_uow.metric_entry_repository.find_all(allow_archived=True)
                self._do_anti_entropy_for_metric_entries(metric_entries)
            if args.do_notion_cleanup:
                LOGGER.info(f"Garbage collecting metric entries which were archived")
                for metric in metrics:
                    allowed_ref_ids = \
                        set(self._metric_notion_manager.load_all_saved_metric_entries_ref_ids(metric.ref_id))
                    with self._metric_engine.get_unit_of_work() as metric_uow:
                        metric_entries = metric_uow.metric_entry_repository.find_all(
                            allow_archived=True, filter_ref_ids=allowed_ref_ids, filter_metric_ref_ids=[metric.ref_id])
                    self._do_drop_all_archived_metric_entries(metric_entries)

        if SyncTarget.PRM in args.sync_targets:
            if args.do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for persons in the PRM database")
                with self._prm_engine.get_unit_of_work() as prm_uow:
                    persons = prm_uow.person_repository.find_all(allow_archived=True)
                self._do_anti_entropy_for_persons(persons)
            if args.do_notion_cleanup:
                LOGGER.info(f"Garbage collecting persons which were archived")
                allowed_person_ref_ids = self._prm_notion_manager.load_all_saved_person_ref_ids()

                with self._prm_engine.get_unit_of_work() as prm_uow:
                    persons = \
                        prm_uow.person_repository.find_all(allow_archived=True, filter_ref_ids=allowed_person_ref_ids)
                self._do_drop_all_archived_persons(persons)

    def _archive_done_inbox_tasks_for_project(self, project: Project) -> None:
        with self._inbox_task_engine.get_unit_of_work() as uow:
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_project(project.ref_id)
            inbox_tasks = uow.inbox_task_repository.find_all(
                allow_archived=False, filter_inbox_task_collection_ref_ids=[inbox_task_collection.ref_id])

        inbox_task_archive_service = InboxTaskArchiveService(
            self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager)
        for inbox_task in inbox_tasks:
            if not inbox_task.status.is_completed:
                continue

            inbox_task_archive_service.do_it(inbox_task)

    def _archive_done_big_plans_for_project(self, project: Project) -> None:
        """Archive the done big plans."""
        # TODO(horia141): should probably archive related tasks too here. ALso for recurring tasks and others linked
        with self._big_plan_engine.get_unit_of_work() as uow:
            big_plan_collection = uow.big_plan_collection_repository.load_by_project(project.ref_id)
            big_plans = uow.big_plan_repository.find_all(
                allow_archived=False, filter_big_plan_collection_ref_ids=[big_plan_collection.ref_id])

        big_plan_archive_service = \
            BigPlanArchiveService(self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager,
                                  self._big_plan_engine, self._big_plan_notion_manager)
        for big_plan in big_plans:
            if not big_plan.status.is_completed:
                continue
            big_plan_archive_service.do_it(big_plan)

    def _do_anti_entropy_for_vacations(
            self, all_vacation: Iterable[Vacation]) -> Iterable[Vacation]:
        vacations_names_set = {}
        for vacation in all_vacation:
            if vacation.name in vacations_names_set:
                LOGGER.info(f"Found a duplicate vacation '{vacation.name}' - removing in anti-entropy")
                # Apply changes locally
                with self._vacation_engine.get_unit_of_work() as uow:
                    uow.vacation_repository.remove(vacation.ref_id)
                    LOGGER.info("Applied local changes")

                try:
                    self._vacation_notion_manager.remove_vacation(vacation.ref_id)
                    LOGGER.info("Applied Notion changes")
                except NotionVacationNotFoundError:
                    LOGGER.info("Skipping removal on Notion side because vacation was not found")
                continue
            vacations_names_set[vacation.name] = vacation
        return vacations_names_set.values()

    def _do_anti_entropy_for_big_plans(self, all_big_plans: Iterable[BigPlan]) -> Iterable[BigPlan]:
        big_plans_names_set = {}
        for big_plan in all_big_plans:
            big_plan_remove_service = BigPlanRemoveService(
                self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager,
                self._big_plan_engine, self._big_plan_notion_manager)
            if big_plan.name in big_plans_names_set:
                LOGGER.info(f"Found a duplicate big plan '{big_plan.name}' - removing in anti-entropy")
                big_plan_remove_service.remove(big_plan.ref_id)
                continue
            big_plans_names_set[big_plan.name] = big_plan
        return big_plans_names_set.values()

    def _do_anti_entropy_for_recurring_tasks(
            self, all_recurring_tasks: Iterable[RecurringTask]) -> Iterable[RecurringTask]:
        recurring_tasks_names_set = {}
        for recurring_task in all_recurring_tasks:
            recurring_task_remove_service = RecurringTaskRemoveService(
                self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager,
                self._recurring_task_engine, self._recurring_task_notion_manager)
            if recurring_task.name in recurring_tasks_names_set:
                LOGGER.info(f"Found a duplicate recurring task '{recurring_task.name}' - removing in anti-entropy")
                recurring_task_remove_service.remove(recurring_task.ref_id)
                continue
            recurring_tasks_names_set[recurring_task.name] = recurring_task
        return recurring_tasks_names_set.values()

    def _do_anti_entropy_for_inbox_tasks(self, all_inbox_tasks: Iterable[InboxTask]) -> Iterable[InboxTask]:
        inbox_tasks_names_set = {}
        for inbox_task in all_inbox_tasks:
            if inbox_task.name in inbox_tasks_names_set:
                LOGGER.info(f"Found a duplicate inbox task '{inbox_task.name}' - removing in anti-entropy")
                InboxTaskRemoveService(
                    self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager).do_it(inbox_task)
                continue
            inbox_tasks_names_set[inbox_task.name] = inbox_task
        return inbox_tasks_names_set.values()

    def _do_anti_entropy_for_smart_lists(self, all_smart_lists: Iterable[SmartList]) -> Iterable[SmartList]:
        smart_lists_name_set = {}
        for smart_list in all_smart_lists:
            if smart_list.name in smart_lists_name_set:
                LOGGER.info(f"Found a duplicate smart list '{smart_list.name}' - removing in anti-entropy")

                with self._smart_list_engine.get_unit_of_work() as uow:
                    for smart_list_item in \
                            uow.smart_list_item_repository.find_all(
                                    allow_archived=True, filter_smart_list_ref_ids=[smart_list.ref_id]):
                        uow.smart_list_item_repository.remove(smart_list_item.ref_id)

                    for smart_list_tag in \
                            uow.smart_list_tag_repository.find_all(
                                    allow_archived=True, filter_smart_list_ref_ids=[smart_list.ref_id]):
                        uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)

                    uow.smart_list_repository.remove(smart_list.ref_id)

                LOGGER.info("Applied local changes")

                try:
                    self._smart_list_notion_manager.remove_smart_list(smart_list.ref_id)
                    LOGGER.info("Applied Notion changes")
                except NotionSmartListNotFoundError:
                    LOGGER.info("Skipping removal on Notion side because smart list was not found")
                continue
            smart_lists_name_set[smart_list.name] = smart_list
        return smart_lists_name_set.values()

    def _do_anti_entropy_for_smart_list_items(
            self, all_smart_list_items: Iterable[SmartListItem]) -> Iterable[SmartListItem]:
        smart_list_items_name_set = {}
        for smart_list_item in all_smart_list_items:
            if smart_list_item.name in smart_list_items_name_set:
                LOGGER.info(f"Found a duplicate smart list item '{smart_list_item.name}' - removing in anti-entropy")
                with self._smart_list_engine.get_unit_of_work() as uow:
                    uow.smart_list_item_repository.remove(smart_list_item.ref_id)
                    LOGGER.info("Applied local changes")

                try:
                    self._smart_list_notion_manager.remove_smart_list_item(
                        smart_list_item.smart_list_ref_id, smart_list_item.ref_id)
                    LOGGER.info("Applied Notion changes")
                except NotionSmartListItemNotFoundError:
                    LOGGER.info("Skipping har removal on Notion side because recurring task was not found")
                continue
            smart_list_items_name_set[smart_list_item.name] = smart_list_item
        return smart_list_items_name_set.values()

    def _do_anti_entropy_for_metrics(self, all_metrics: Iterable[Metric]) -> Iterable[Metric]:
        metrics_name_set = {}
        for metric in all_metrics:
            metric_remove_service = MetricRemoveService(
                self._time_provider, self._inbox_task_engine, self._inbox_task_notion_manager,
                self._metric_engine, self._metric_notion_manager)
            if metric.name in metrics_name_set:
                LOGGER.info(f"Found a duplicate metric '{metric.name}' - removing in anti-entropy")
                metric_remove_service.execute(metric)
                continue
            metrics_name_set[metric.name] = metric
        return metrics_name_set.values()

    def _do_anti_entropy_for_metric_entries(
            self, all_metric_entrys: Iterable[MetricEntry]) -> Iterable[MetricEntry]:
        metric_entries_collection_time_set = {}
        for metric_entry in all_metric_entrys:
            if metric_entry.collection_time in metric_entries_collection_time_set:
                LOGGER.info(
                    f"Found a duplicate metric entry '{metric_entry.collection_time}' - removing in anti-entropy")
                with self._metric_engine.get_unit_of_work() as uow:
                    metric_entry = uow.metric_entry_repository.remove(metric_entry.ref_id)
                    LOGGER.info("Applied local changes")

                try:
                    self._metric_notion_manager.remove_metric_entry(metric_entry.metric_ref_id, metric_entry.ref_id)
                    LOGGER.info("Applied Notion changes")
                except NotionMetricEntryNotFoundError:
                    LOGGER.info("Skipping har removal on Notion side because recurring task was not found")
                continue
            metric_entries_collection_time_set[metric_entry.collection_time] = metric_entry
        return metric_entries_collection_time_set.values()

    def _do_anti_entropy_for_persons(self, all_persons: Iterable[Person]) -> Iterable[Person]:
        persons_name_set = {}
        person_remove_service = PersonRemoveService(
            self._time_provider, self._prm_engine, self._prm_notion_manager,
            self._inbox_task_engine, self._inbox_task_notion_manager)
        for person in all_persons:
            if person.name in persons_name_set:
                LOGGER.info(
                    f"Found a duplicate person '{person.name}' - removing in anti-entropy")
                person_remove_service.do_it(person)
                continue
            persons_name_set[person.name] = person
        return persons_name_set.values()

    def _do_drop_all_archived_vacations(self, all_vacations: Iterable[Vacation]) -> None:
        for vacation in all_vacations:
            if not vacation.archived:
                continue
            LOGGER.info(f"Removed an archived vacation '{vacation.name}' on Notion side")
            try:
                self._vacation_notion_manager.remove_vacation(vacation.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionVacationNotFoundError:
                LOGGER.info("Skipping removal on Notion side because vacation was not found")

    def _do_drop_all_archived_big_plans(self, big_plans: Iterable[BigPlan]) -> None:
        for big_plan in big_plans:
            if not big_plan.archived:
                continue
            LOGGER.info(f"Removed an archived big plan '{big_plan.name}' on Notion side")
            try:
                self._big_plan_notion_manager.remove_big_plan(big_plan.big_plan_collection_ref_id, big_plan.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionBigPlanNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because big plan was not found")

    def _do_drop_all_archived_recurring_tasks(self, recurring_tasks: Iterable[RecurringTask]) -> None:
        for recurring_task in recurring_tasks:
            if not recurring_task.archived:
                continue
            LOGGER.info(f"Removed an archived recurring task '{recurring_task.name}' on Notion side")
            try:
                self._recurring_task_notion_manager.remove_recurring_task(
                    recurring_task.recurring_task_collection_ref_id, recurring_task.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionRecurringTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because big plan was not found")
            #TODO(horia141): more can be done here surely!

    def _do_drop_all_archived_inbox_tasks(self, inbox_tasks: Iterable[InboxTask]) -> None:
        for inbox_task in inbox_tasks:
            if not inbox_task.archived:
                continue
            LOGGER.info(f"Removed an archived inbox tasks '{inbox_task.name}' on Notion side")
            try:
                self._inbox_task_notion_manager.remove_inbox_task(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionRecurringTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info("Skipping removal on Notion side because inbox task was not found")

    def _do_drop_all_archived_smart_lists(self, smart_lists: Iterable[SmartList]) -> None:
        for smart_list in smart_lists:
            if not smart_list.archived:
                continue
            LOGGER.info(f"Removed an archived smart list '{smart_list.name}' on Notion side")

            try:
                self._smart_list_notion_manager.remove_smart_list(smart_list.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionSmartListNotFoundError:
                LOGGER.info("Skipping removal on Notion side because smart list was not found")

    def _do_drop_all_archived_smart_list_items(self, smart_list_items: Iterable[SmartListItem]) -> None:
        for smart_list_item in smart_list_items:
            if not smart_list_item.archived:
                continue
            LOGGER.info(f"Removed an archived smart list item '{smart_list_item.name}' on Notion side")
            try:
                self._smart_list_notion_manager.remove_smart_list_item(
                    smart_list_item.smart_list_ref_id, smart_list_item.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionSmartListItemNotFoundError:
                LOGGER.info("Skipping archival on Notion side because smart list was not found")

    def _do_drop_all_archived_metrics(self, metrics: Iterable[Metric]) -> None:
        for metric in metrics:
            if not metric.archived:
                continue
            LOGGER.info(f"Removed an archived metric '{metric.name}' on Notion side")
            try:
                self._metric_notion_manager.remove_metric(metric.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionMetricNotFoundError:
                LOGGER.info("Skipping archival on Notion side because metric was not found")

    def _do_drop_all_archived_metric_entries(self, metric_entries: Iterable[MetricEntry]) -> None:
        for metric_entry in metric_entries:
            if not metric_entry.archived:
                continue
            LOGGER.info(f"Removed an archived metric entry '{metric_entry.collection_time}' on Notion side")
            try:
                self._metric_notion_manager.remove_metric_entry(metric_entry.metric_ref_id, metric_entry.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionMetricEntryNotFoundError:
                LOGGER.info("Skipping the removal on Notion side because recurring task was not found")

    def _do_drop_all_archived_persons(self, persons: Iterable[Person]) -> None:
        for person in persons:
            if not person.archived:
                continue
            LOGGER.info(f"Removed an archived person '{person.name}' on Notion side")
            try:
                self._prm_notion_manager.remove_person(person.ref_id)
                LOGGER.info("Applied Notion changes")
            except NotionPersonNotFoundError:
                LOGGER.info("Skipping the removal on Notion side because person was not found")
