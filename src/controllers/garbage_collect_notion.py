"""The controller for Notion garbage collection."""
import logging
from typing import Final, Optional, Iterable

from domain.metrics.metric import Metric
from domain.metrics.metric_entry import MetricEntry
from domain.prm.commands.person_remove import PersonRemoveCommand
from domain.prm.infra.prm_engine import PrmEngine
from domain.prm.infra.prm_notion_manager import PrmNotionManager
from domain.prm.person import Person
from domain.smart_lists.smart_list import SmartList
from domain.smart_lists.smart_list_item import SmartListItem
from domain.vacations.vacation import Vacation
from models.basic import ProjectKey, SyncTarget
from service.big_plans import BigPlansService, BigPlan
from service.inbox_tasks import InboxTasksService, InboxTask
from service.metrics import MetricsService
from service.projects import ProjectsService
from service.recurring_tasks import RecurringTasksService, RecurringTask
from service.smart_lists import SmartListsService
from service.vacations import VacationsService
from utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class GarbageCollectNotionController:
    """The controller for Notion systems garbage collection."""

    _time_provider: Final[TimeProvider]
    _vacations_service: Final[VacationsService]
    _projects_service: Final[ProjectsService]
    _inbox_tasks_service: Final[InboxTasksService]
    _recurring_tasks_service: Final[RecurringTasksService]
    _big_plans_service: Final[BigPlansService]
    _smart_lists_service: Final[SmartListsService]
    _metrics_service: Final[MetricsService]
    _prm_engine: Final[PrmEngine]
    _prm_notion_manager: Final[PrmNotionManager]

    def __init__(
            self, time_provider: TimeProvider, vacations_service: VacationsService, projects_service: ProjectsService,
            inbox_tasks_service: InboxTasksService, recurring_tasks_service: RecurringTasksService,
            big_plans_service: BigPlansService, smart_lists_service: SmartListsService,
            metrics_service: MetricsService, prm_engine: PrmEngine, prm_notion_manager: PrmNotionManager) -> None:
        """Constructor."""
        self._time_provider = time_provider
        self._vacations_service = vacations_service
        self._projects_service = projects_service
        self._inbox_tasks_service = inbox_tasks_service
        self._recurring_tasks_service = recurring_tasks_service
        self._big_plans_service = big_plans_service
        self._smart_lists_service = smart_lists_service
        self._metrics_service = metrics_service
        self._prm_engine = prm_engine
        self._prm_notion_manager = prm_notion_manager

    def garbage_collect(
            self, sync_targets: Iterable[SyncTarget], project_keys: Optional[Iterable[ProjectKey]],
            do_archival: bool, do_anti_entropy: bool, do_notion_cleanup: bool) -> None:
        """Garbage collect everything."""
        if SyncTarget.VACATIONS in sync_targets:
            if do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for vacations")
                vacations = self._vacations_service.load_all_vacations(allow_archived=True)
                self._do_anti_entropy_for_vacations(vacations)
            if do_notion_cleanup:
                LOGGER.info(f"Garbage collecting vacations which were archived")
                vacations = self._vacations_service.load_all_vacations_not_notion_gced()
                self._do_drop_all_archived_vacations(vacations)

        for project in self._projects_service.load_all_projects(filter_keys=project_keys):
            LOGGER.info(f"Garbage collecting project '{project.name}'")

            if SyncTarget.INBOX_TASKS in sync_targets:
                if do_archival:
                    LOGGER.info(f"Archiving all done inbox tasks")
                    self._inbox_tasks_service.archive_done_inbox_tasks([project.ref_id])
                if do_anti_entropy:
                    LOGGER.info(f"Performing anti-entropy adjustments for inbox tasks")
                    inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks(
                        allow_archived=True, filter_project_ref_ids=[project.ref_id])
                    self._do_anti_entropy_for_inbox_tasks(inbox_tasks)
                if do_notion_cleanup:
                    LOGGER.info(f"Garbage collecting inbox tasks which were archived")
                    inbox_tasks = self._inbox_tasks_service.load_all_inbox_tasks_not_notion_gced(project.ref_id)
                    self._do_drop_all_archived_inbox_tasks(inbox_tasks)

            if SyncTarget.RECURRING_TASKS in sync_targets:
                if do_anti_entropy:
                    LOGGER.info(f"Performing anti-entropy adjustments for recurring tasks")
                    recurring_tasks = self._recurring_tasks_service.load_all_recurring_tasks(
                        allow_archived=True, filter_project_ref_ids=[project.ref_id])
                    self._do_anti_entropy_for_recurring_tasks(recurring_tasks)
                if do_notion_cleanup:
                    LOGGER.info(f"Garbage collecting recurring tasks which were archived")
                    recurring_tasks = \
                        self._recurring_tasks_service.load_all_recurring_tasks_not_notion_gced(project.ref_id)
                    self._do_drop_all_archived_recurring_tasks(recurring_tasks)

            if SyncTarget.BIG_PLANS in sync_targets:
                if do_archival:
                    LOGGER.info(f"Archiving all done big plans")
                    self._big_plans_service.archive_done_big_plans([project.ref_id])
                if do_anti_entropy:
                    LOGGER.info(f"Performing anti-entropy adjustments for big plans")
                    big_plans = self._big_plans_service.load_all_big_plans(
                        allow_archived=True, filter_project_ref_ids=[project.ref_id])
                    self._do_anti_entropy_for_big_plans(big_plans)
                if do_notion_cleanup:
                    LOGGER.info(f"Garbage collecting big plans which were archived")
                    big_plans = self._big_plans_service.load_all_recurring_tasks_not_notion_gced(project.ref_id)
                    self._do_drop_all_archived_big_plans(big_plans)

        if SyncTarget.SMART_LISTS in sync_targets:
            smart_lists: Iterable[SmartList] = []
            if do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for smart lists")
                smart_lists = self._smart_lists_service.load_all_smart_lists(allow_archived=True)
                smart_lists = self._do_anti_entropy_for_smart_lists(smart_lists)
            if do_notion_cleanup:
                LOGGER.info(f"Garbage collecting smart lists which were archived")
                smart_lists = smart_lists or self._smart_lists_service.load_all_smart_lists(allow_archived=True)
                self._do_drop_all_archived_smart_lists(smart_lists)
            if do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for smart list items")
                smart_list_items = self._smart_lists_service.load_all_smart_list_items(allow_archived=True)
                self._do_anti_entropy_for_smart_list_items(smart_list_items)
            if do_notion_cleanup:
                LOGGER.info(f"Garbage collecting smart list items which were archived")
                for smart_list in smart_lists:
                    smart_list_items = \
                        self._smart_lists_service.load_all_smart_list_items_not_notion_gced(smart_list.ref_id)
                    self._do_drop_all_archived_smart_list_items(smart_list_items)

        if SyncTarget.METRICS in sync_targets:
            metrics: Iterable[Metric] = []
            if do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for metrics")
                metrics = self._metrics_service.load_all_metrics(allow_archived=True)
                metrics = self._do_anti_entropy_for_metrics(metrics)
            if do_notion_cleanup:
                LOGGER.info(f"Garbage collecting metrics which were archived")
                metrics = metrics or self._metrics_service.load_all_metrics(allow_archived=True)
                self._do_drop_all_archived_metrics(metrics)
            if do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for metric entries")
                metric_items = self._metrics_service.load_all_metric_entries(allow_archived=True)
                self._do_anti_entropy_for_metric_entries(metric_items)
            if do_notion_cleanup:
                LOGGER.info(f"Garbage collecting metric entries which were archived")
                for metric in metrics:
                    metric_items = \
                        self._metrics_service.load_all_metric_entries_not_notion_gced(metric.ref_id)
                    self._do_drop_all_archived_metric_entries(metric_items)

        if SyncTarget.PRM in sync_targets:
            if do_anti_entropy:
                LOGGER.info(f"Performing anti-entropy adjustments for persons in the PRM database")
                with self._prm_engine.get_unit_of_work() as uow:
                    persons = uow.person_repository.find_all(allow_archived=True)
                self._do_anti_entropy_for_persons(persons)
            if do_notion_cleanup:
                LOGGER.info(f"Garbage collecting persons which were archived")
                allowed_person_ref_ids = self._prm_notion_manager.load_all_saved_person_ref_ids()

                with self._prm_engine.get_unit_of_work() as uow:
                    persons = uow.person_repository.find_all(allow_archived=True, filter_ref_ids=allowed_person_ref_ids)
                self._do_drop_all_archived_persons(persons)

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

    def _do_anti_entropy_for_big_plans(self, all_big_plans: Iterable[BigPlan]) -> Iterable[BigPlan]:
        big_plans_names_set = {}
        for big_plan in all_big_plans:
            if big_plan.name in big_plans_names_set:
                LOGGER.info(f"Found a duplicate big plan '{big_plan.name}' - removing in anti-entropy")
                self._big_plans_service.hard_remove_big_plan(big_plan.ref_id)
                continue
            big_plans_names_set[big_plan.name] = big_plan
        return big_plans_names_set.values()

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

    def _do_anti_entropy_for_inbox_tasks(self, all_inbox_tasks: Iterable[InboxTask]) -> Iterable[InboxTask]:
        inbox_tasks_names_set = {}
        for inbox_task in all_inbox_tasks:
            if inbox_task.name in inbox_tasks_names_set:
                LOGGER.info(f"Found a duplicate inbox task '{inbox_task.name}' - removing in anti-entropy")
                self._inbox_tasks_service.hard_remove_inbox_task(inbox_task.ref_id)
                continue
            inbox_tasks_names_set[inbox_task.name] = inbox_task
        return inbox_tasks_names_set.values()

    def _do_anti_entropy_for_smart_lists(self, all_smart_lists: Iterable[SmartList]) -> Iterable[SmartList]:
        smart_lists_name_set = {}
        for smart_list in all_smart_lists:
            if smart_list.name in smart_lists_name_set:
                LOGGER.info(f"Found a duplicate smart list '{smart_list.name}' - removing in anti-entropy")
                self._smart_lists_service.hard_remove_smart_list(smart_list.ref_id)
                continue
            smart_lists_name_set[smart_list.name] = smart_list
        return smart_lists_name_set.values()

    def _do_anti_entropy_for_smart_list_items(
            self, all_smart_list_items: Iterable[SmartListItem]) -> Iterable[SmartListItem]:
        smart_list_items_name_set = {}
        for smart_list_item in all_smart_list_items:
            if smart_list_item.name in smart_list_items_name_set:
                LOGGER.info(f"Found a duplicate smart list item '{smart_list_item.name}' - removing in anti-entropy")
                self._smart_lists_service.hard_remove_smart_list_item(smart_list_item.ref_id)
                continue
            smart_list_items_name_set[smart_list_item.name] = smart_list_item
        return smart_list_items_name_set.values()

    def _do_anti_entropy_for_metrics(self, all_metrics: Iterable[Metric]) -> Iterable[Metric]:
        metrics_name_set = {}
        for metric in all_metrics:
            if metric.name in metrics_name_set:
                LOGGER.info(f"Found a duplicate metric '{metric.name}' - removing in anti-entropy")
                self._metrics_service.hard_remove_metric(metric.ref_id)
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
                self._metrics_service.hard_remove_metric_entry(metric_entry.ref_id)
                continue
            metric_entries_collection_time_set[metric_entry.collection_time] = metric_entry
        return metric_entries_collection_time_set.values()

    def _do_anti_entropy_for_persons(self, all_persons: Iterable[Person]) -> Iterable[Person]:
        persons_name_set = {}
        for person in all_persons:
            if person.name in persons_name_set:
                LOGGER.info(
                    f"Found a duplicate person '{person.name}' - removing in anti-entropy")
                PersonRemoveCommand(
                    self._time_provider, self._prm_engine, self._prm_notion_manager, self._inbox_tasks_service)\
                    .execute(person.ref_id)
                continue
            persons_name_set[person.name] = person
        return persons_name_set.values()

    def _do_drop_all_archived_vacations(self, all_vacations: Iterable[Vacation]) -> None:
        for vacation in all_vacations:
            if not vacation.archived:
                continue
            LOGGER.info(f"Removed an archived vacation '{vacation.name}' on Notion side")
            self._vacations_service.remove_vacation_on_notion_side(vacation.ref_id)

    def _do_drop_all_archived_big_plans(self, big_plans: Iterable[BigPlan]) -> None:
        for big_plan in big_plans:
            if not big_plan.archived:
                continue
            LOGGER.info(f"Removed an archived big plan '{big_plan.name}' on Notion side")
            self._big_plans_service.remove_big_plan_on_notion_side(big_plan.ref_id)

    def _do_drop_all_archived_recurring_tasks(self, recurring_tasks: Iterable[RecurringTask]) -> None:
        for recurring_task in recurring_tasks:
            if not recurring_task.archived:
                continue
            LOGGER.info(f"Removed an archived recurring task '{recurring_task.name}' on Notion side")
            self._recurring_tasks_service.remove_recurring_task_on_notion_side(recurring_task.ref_id)

    def _do_drop_all_archived_inbox_tasks(self, inbox_tasks: Iterable[InboxTask]) -> None:
        for inbox_task in inbox_tasks:
            if not inbox_task.archived:
                continue
            LOGGER.info(f"Removed an archived inbox tasks '{inbox_task.name}' on Notion side")
            self._inbox_tasks_service.remove_inbox_task_on_notion_side(inbox_task.ref_id)

    def _do_drop_all_archived_smart_lists(self, smart_lists: Iterable[SmartList]) -> None:
        for smart_list in smart_lists:
            if not smart_list.archived:
                continue
            LOGGER.info(f"Removed an archived smart list '{smart_list.name}' on Notion side")
            self._smart_lists_service.remove_smart_list_on_notion_side(smart_list.ref_id)

    def _do_drop_all_archived_smart_list_items(self, smart_list_items: Iterable[SmartListItem]) -> None:
        for smart_list_item in smart_list_items:
            if not smart_list_item.archived:
                continue
            LOGGER.info(f"Removed an archived smart list item '{smart_list_item.name}' on Notion side")
            self._smart_lists_service.remove_smart_list_item_on_notion_side(smart_list_item.ref_id)

    def _do_drop_all_archived_metrics(self, metrics: Iterable[Metric]) -> None:
        for metric in metrics:
            if not metric.archived:
                continue
            LOGGER.info(f"Removed an archived metric '{metric.name}' on Notion side")
            self._metrics_service.remove_metric_on_notion_side(metric.ref_id)

    def _do_drop_all_archived_metric_entries(self, metric_entries: Iterable[MetricEntry]) -> None:
        for metric_entry in metric_entries:
            if not metric_entry.archived:
                continue
            LOGGER.info(f"Removed an archived metric entry '{metric_entry.collection_time}' on Notion side")
            self._metrics_service.remove_metric_entry_on_notion_side(metric_entry.ref_id)

    def _do_drop_all_archived_persons(self, persons: Iterable[Person]) -> None:
        for person in persons:
            if not person.archived:
                continue
            LOGGER.info(f"Removed an archived person '{person.name}' on Notion side")
            self._prm_notion_manager.remove_person(person.ref_id)
