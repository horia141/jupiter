"""The command for doing a garbage collection run."""
import logging
from dataclasses import dataclass
from typing import Final, Iterable, List, cast

from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.infra.big_plan_notion_manager import (
    BigPlanNotionManager,
    NotionBigPlanNotFoundError,
)
from jupiter.domain.big_plans.service.archive_service import BigPlanArchiveService
from jupiter.domain.big_plans.service.remove_service import BigPlanRemoveService
from jupiter.domain.chores.chore import Chore
from jupiter.domain.chores.infra.chore_notion_manager import (
    ChoreNotionManager,
    NotionChoreNotFoundError,
)
from jupiter.domain.chores.service.remove_service import ChoreRemoveService
from jupiter.domain.habits.habit import Habit
from jupiter.domain.habits.infra.habit_notion_manager import (
    HabitNotionManager,
    NotionHabitNotFoundError,
)
from jupiter.domain.habits.service.remove_service import HabitRemoveService
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
    NotionInboxTaskNotFoundError,
)
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service import (
    InboxTaskBigPlanRefOptionsUpdateService,
)
from jupiter.domain.inbox_tasks.service.remove_service import InboxTaskRemoveService
from jupiter.domain.metrics.infra.metric_notion_manager import (
    MetricNotionManager,
    NotionMetricNotFoundError,
    NotionMetricEntryNotFoundError,
)
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.domain.metrics.metric_entry import MetricEntry
from jupiter.domain.metrics.service.remove_service import MetricRemoveService
from jupiter.domain.persons.infra.person_notion_manager import (
    PersonNotionManager,
    NotionPersonNotFoundError,
)
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.domain.persons.service.remove_service import PersonRemoveService
from jupiter.domain.projects.infra.project_notion_manager import (
    NotionProjectNotFoundError,
    ProjectNotionManager,
)
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_collection import ProjectCollection
from jupiter.domain.projects.service.project_label_update_service import (
    ProjectLabelUpdateService,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
    NotionSlackTaskNotFoundError,
)
from jupiter.domain.push_integrations.slack.service.archive_service import (
    SlackTaskArchiveService,
)
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
    NotionSmartListNotFoundError,
    NotionSmartListItemNotFoundError,
)
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_target import SyncTarget
from jupiter.domain.vacations.infra.vacation_notion_manager import (
    VacationNotionManager,
    NotionVacationNotFoundError,
)
from jupiter.domain.vacations.vacation import Vacation
from jupiter.domain.vacations.vacation_collection import VacationCollection
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    MutationUseCaseInvocationRecorder,
)
from jupiter.use_cases.infra.use_cases import AppMutationUseCase, AppUseCaseContext
from jupiter.utils.time_provider import TimeProvider

LOGGER = logging.getLogger(__name__)


class GCUseCase(AppMutationUseCase["GCUseCase.Args", None]):
    """The command for doing a garbage collection run."""

    @dataclass(frozen=True)
    class Args(UseCaseArgsBase):
        """Args."""

        sync_targets: Iterable[SyncTarget]
        do_archival: bool
        do_anti_entropy: bool
        do_notion_cleanup: bool

    _vacation_notion_manager: Final[VacationNotionManager]
    _project_notion_manager: Final[ProjectNotionManager]
    _inbox_task_notion_manager: Final[InboxTaskNotionManager]
    _habit_notion_manager: Final[HabitNotionManager]
    _chore_notion_manager: Final[ChoreNotionManager]
    _big_plan_notion_manager: Final[BigPlanNotionManager]
    _smart_list_notion_manager: Final[SmartListNotionManager]
    _metric_notion_manager: Final[MetricNotionManager]
    _person_notion_manager: Final[PersonNotionManager]
    _slack_task_notion_manager: Final[SlackTaskNotionManager]

    def __init__(
        self,
        time_provider: TimeProvider,
        invocation_recorder: MutationUseCaseInvocationRecorder,
        storage_engine: DomainStorageEngine,
        vacation_notion_manager: VacationNotionManager,
        project_notion_manager: ProjectNotionManager,
        inbox_task_notion_manager: InboxTaskNotionManager,
        habit_notion_manager: HabitNotionManager,
        chore_notion_manager: ChoreNotionManager,
        big_plan_notion_manager: BigPlanNotionManager,
        smart_list_notion_manager: SmartListNotionManager,
        metric_notion_manager: MetricNotionManager,
        person_notion_manager: PersonNotionManager,
        slack_task_notion_manager: SlackTaskNotionManager,
    ) -> None:
        """Constructor."""
        super().__init__(time_provider, invocation_recorder, storage_engine)
        self._vacation_notion_manager = vacation_notion_manager
        self._project_notion_manager = project_notion_manager
        self._inbox_task_notion_manager = inbox_task_notion_manager
        self._habit_notion_manager = habit_notion_manager
        self._chore_notion_manager = chore_notion_manager
        self._big_plan_notion_manager = big_plan_notion_manager
        self._smart_list_notion_manager = smart_list_notion_manager
        self._metric_notion_manager = metric_notion_manager
        self._person_notion_manager = person_notion_manager
        self._slack_task_notion_manager = slack_task_notion_manager

    def _execute(self, context: AppUseCaseContext, args: Args) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        if SyncTarget.VACATIONS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                vacation_collection = uow.vacation_collection_repository.load_by_parent(
                    workspace.ref_id
                )
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for vacations")
                with self._storage_engine.get_unit_of_work() as uow:
                    vacations = uow.vacation_repository.find_all(
                        parent_ref_id=vacation_collection.ref_id, allow_archived=True
                    )
                self._do_anti_entropy_for_vacations(vacation_collection, vacations)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting vacations which were archived")

                allowed_ref_ids = self._vacation_notion_manager.load_all_saved_ref_ids(
                    vacation_collection.ref_id
                )

                with self._storage_engine.get_unit_of_work() as uow:
                    vacations = uow.vacation_repository.find_all(
                        parent_ref_id=vacation_collection.ref_id,
                        allow_archived=True,
                        filter_ref_ids=allowed_ref_ids,
                    )
                self._do_drop_all_archived_vacations(vacation_collection, vacations)

        if SyncTarget.PROJECTS in args.sync_targets:
            need_to_modifiy_something = False
            with self._storage_engine.get_unit_of_work() as uow:
                project_collection = uow.project_collection_repository.load_by_parent(
                    workspace.ref_id
                )
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for projects")
                with self._storage_engine.get_unit_of_work() as uow:
                    projects = uow.project_repository.find_all(
                        parent_ref_id=project_collection.ref_id, allow_archived=True
                    )
                self._do_anti_entropy_for_projects(project_collection, projects)
                need_to_modifiy_something = True
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting projects which were archived")

                allowed_ref_ids = self._project_notion_manager.load_all_saved_ref_ids(
                    project_collection.ref_id
                )

                with self._storage_engine.get_unit_of_work() as uow:
                    projects = uow.project_repository.find_all_with_filters(
                        parent_ref_id=project_collection.ref_id,
                        allow_archived=True,
                        filter_ref_ids=allowed_ref_ids,
                    )
                self._do_drop_all_archived_projects(project_collection, projects)
                need_to_modifiy_something = True

            if need_to_modifiy_something:
                ProjectLabelUpdateService(
                    self._storage_engine,
                    self._inbox_task_notion_manager,
                    self._habit_notion_manager,
                    self._chore_notion_manager,
                    self._big_plan_notion_manager,
                ).sync(workspace, projects)

        if SyncTarget.INBOX_TASKS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                inbox_task_collection = (
                    uow.inbox_task_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                )
            if args.do_archival:
                LOGGER.info("Archiving all done inbox tasks")
                with self._storage_engine.get_unit_of_work() as uow:
                    inbox_tasks = uow.inbox_task_repository.find_all(
                        parent_ref_id=inbox_task_collection.ref_id, allow_archived=False
                    )
                self._archive_done_inbox_tasks(inbox_tasks)
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for inbox tasks")
                with self._storage_engine.get_unit_of_work() as uow:
                    inbox_tasks = uow.inbox_task_repository.find_all(
                        parent_ref_id=inbox_task_collection.ref_id, allow_archived=True
                    )
                self._do_anti_entropy_for_inbox_tasks(inbox_tasks)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting inbox tasks which were archived")
                allowed_ref_ids = (
                    self._inbox_task_notion_manager.load_all_saved_ref_ids(
                        inbox_task_collection.ref_id
                    )
                )
                with self._storage_engine.get_unit_of_work() as uow:
                    inbox_tasks = uow.inbox_task_repository.find_all(
                        parent_ref_id=inbox_task_collection.ref_id,
                        allow_archived=True,
                        filter_ref_ids=allowed_ref_ids,
                    )
                self._do_drop_all_archived_inbox_tasks(inbox_tasks)

        if SyncTarget.HABITS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                habit_collection = uow.habit_collection_repository.load_by_parent(
                    workspace.ref_id
                )
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for habits")
                with self._storage_engine.get_unit_of_work() as uow:
                    habits = uow.habit_repository.find_all(
                        parent_ref_id=habit_collection.ref_id, allow_archived=True
                    )
                self._do_anti_entropy_for_habits(habits)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting habits which were archived")
                allowed_ref_ids = self._habit_notion_manager.load_all_saved_ref_ids(
                    habit_collection.ref_id
                )
                with self._storage_engine.get_unit_of_work() as uow:
                    habits = uow.habit_repository.find_all(
                        parent_ref_id=habit_collection.ref_id,
                        allow_archived=True,
                        filter_ref_ids=allowed_ref_ids,
                    )
                self._do_drop_all_archived_habits(habits)

        if SyncTarget.CHORES in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                chore_collection = uow.chore_collection_repository.load_by_parent(
                    workspace.ref_id
                )
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for chores")
                with self._storage_engine.get_unit_of_work() as uow:
                    chores = uow.chore_repository.find_all(
                        parent_ref_id=chore_collection.ref_id, allow_archived=True
                    )
                self._do_anti_entropy_for_chores(chores)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting chores which were archived")
                allowed_ref_ids = self._chore_notion_manager.load_all_saved_ref_ids(
                    chore_collection.ref_id
                )
                with self._storage_engine.get_unit_of_work() as uow:
                    chores = uow.chore_repository.find_all(
                        parent_ref_id=chore_collection.ref_id,
                        allow_archived=True,
                        filter_ref_ids=allowed_ref_ids,
                    )
                self._do_drop_all_archived_chores(chores)

        if SyncTarget.BIG_PLANS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                big_plan_collection = uow.big_plan_collection_repository.load_by_parent(
                    workspace.ref_id
                )
            if args.do_archival:
                LOGGER.info("Archiving all done big plans")
                with self._storage_engine.get_unit_of_work() as uow:
                    big_plans = uow.big_plan_repository.find_all(
                        parent_ref_id=big_plan_collection.ref_id, allow_archived=False
                    )
                self._archive_done_big_plans(big_plans)
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for big plans")
                with self._storage_engine.get_unit_of_work() as uow:
                    big_plans = uow.big_plan_repository.find_all(
                        parent_ref_id=big_plan_collection.ref_id, allow_archived=True
                    )
                self._do_anti_entropy_for_big_plans(big_plans)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting big plans which were archived")
                allowed_ref_ids = self._big_plan_notion_manager.load_all_saved_ref_ids(
                    big_plan_collection.ref_id
                )
                with self._storage_engine.get_unit_of_work() as uow:
                    big_plans = uow.big_plan_repository.find_all(
                        parent_ref_id=big_plan_collection.ref_id,
                        allow_archived=True,
                        filter_ref_ids=allowed_ref_ids,
                    )
                self._do_drop_all_archived_big_plans(big_plans)

            InboxTaskBigPlanRefOptionsUpdateService(
                self._storage_engine, self._inbox_task_notion_manager
            ).sync(big_plan_collection)

        if SyncTarget.SMART_LISTS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                smart_list_collection = (
                    uow.smart_list_collection_repository.load_by_parent(
                        workspace.ref_id
                    )
                )

            smart_lists: Iterable[SmartList] = []
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for smart lists")
                with self._storage_engine.get_unit_of_work() as uow:
                    smart_lists = uow.smart_list_repository.find_all(
                        parent_ref_id=smart_list_collection.ref_id, allow_archived=True
                    )
                smart_lists = self._do_anti_entropy_for_smart_lists(
                    smart_list_collection, smart_lists
                )
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting smart lists which were archived")
                with self._storage_engine.get_unit_of_work() as uow:
                    smart_lists = smart_lists or uow.smart_list_repository.find_all(
                        parent_ref_id=smart_list_collection.ref_id, allow_archived=True
                    )
                self._do_drop_all_archived_smart_lists(
                    smart_list_collection, smart_lists
                )
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for smart list items")
                for smart_list in smart_lists:
                    with self._storage_engine.get_unit_of_work() as uow:
                        smart_list_items = uow.smart_list_item_repository.find_all(
                            parent_ref_id=smart_list.ref_id, allow_archived=True
                        )
                    self._do_anti_entropy_for_smart_list_items(
                        smart_list_collection, smart_list, smart_list_items
                    )
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting smart list items which were archived")
                for smart_list in smart_lists:
                    allowed_ref_ids = set(
                        self._smart_list_notion_manager.load_all_saved_ref_ids(
                            smart_list_collection.ref_id, smart_list.ref_id
                        )
                    )
                    with self._storage_engine.get_unit_of_work() as uow:
                        smart_list_items = uow.smart_list_item_repository.find_all(
                            parent_ref_id=smart_list.ref_id,
                            allow_archived=True,
                            filter_ref_ids=allowed_ref_ids,
                        )
                    self._do_drop_all_archived_smart_list_items(
                        smart_list_collection, smart_list, smart_list_items
                    )

        if SyncTarget.METRICS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                metric_collection = uow.metric_collection_repository.load_by_parent(
                    workspace.ref_id
                )

            metrics: Iterable[Metric] = []
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for metrics")
                with self._storage_engine.get_unit_of_work() as uow:
                    metrics = uow.metric_repository.find_all(
                        parent_ref_id=metric_collection.ref_id, allow_archived=True
                    )
                metrics = self._do_anti_entropy_for_metrics(metric_collection, metrics)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting metrics which were archived")
                with self._storage_engine.get_unit_of_work() as uow:
                    metrics = metrics or uow.metric_repository.find_all(
                        parent_ref_id=metric_collection.ref_id, allow_archived=True
                    )
                self._do_drop_all_archived_metrics(metric_collection, metrics)
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for metric entries")
                for metric in metrics:
                    with self._storage_engine.get_unit_of_work() as uow:
                        metric_entries = uow.metric_entry_repository.find_all(
                            parent_ref_id=metric.ref_id, allow_archived=True
                        )
                    self._do_anti_entropy_for_metric_entries(metric, metric_entries)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting metric entries which were archived")
                for metric in metrics:
                    allowed_ref_ids = set(
                        self._metric_notion_manager.load_all_saved_ref_ids(
                            metric_collection.ref_id, metric.ref_id
                        )
                    )
                    with self._storage_engine.get_unit_of_work() as uow:
                        metric_entries = uow.metric_entry_repository.find_all(
                            parent_ref_id=metric.ref_id,
                            allow_archived=True,
                            filter_ref_ids=allowed_ref_ids,
                        )
                    self._do_drop_all_archived_metric_entries(metric, metric_entries)

        if SyncTarget.PERSONS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                person_collection = uow.person_collection_repository.load_by_parent(
                    workspace.ref_id
                )
            if args.do_anti_entropy:
                LOGGER.info("Performing anti-entropy adjustments for persons")
                with self._storage_engine.get_unit_of_work() as uow:
                    persons = uow.person_repository.find_all(
                        parent_ref_id=person_collection.ref_id, allow_archived=True
                    )
                self._do_anti_entropy_for_persons(person_collection, persons)
            if args.do_notion_cleanup:
                LOGGER.info("Garbage collecting persons which were archived")
                allowed_person_ref_ids = (
                    self._person_notion_manager.load_all_saved_ref_ids(
                        person_collection.ref_id
                    )
                )

                with self._storage_engine.get_unit_of_work() as uow:
                    persons = uow.person_repository.find_all(
                        parent_ref_id=person_collection.ref_id,
                        allow_archived=True,
                        filter_ref_ids=allowed_person_ref_ids,
                    )
                self._do_drop_all_archived_persons(person_collection, persons)

        if SyncTarget.SLACK_TASKS in args.sync_targets:
            with self._storage_engine.get_unit_of_work() as uow:
                push_integration_group = (
                    uow.push_integration_group_repository.load_by_parent(
                        workspace.ref_id
                    )
                )
                slack_task_collection = (
                    uow.slack_task_collection_repository.load_by_parent(
                        push_integration_group.ref_id
                    )
                )
                if args.do_archival:
                    LOGGER.info(
                        "Archiving all Slack tasks whose inbox tasks are done or archived"
                    )
                    with self._storage_engine.get_unit_of_work() as uow:
                        slack_tasks = uow.slack_task_repository.find_all(
                            parent_ref_id=slack_task_collection.ref_id,
                            allow_archived=False,
                        )
                        inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                            parent_ref_id=inbox_task_collection.ref_id,
                            allow_archived=True,
                            filter_sources=[InboxTaskSource.SLACK_TASK],
                            filter_slack_task_ref_ids=[st.ref_id for st in slack_tasks],
                        )
                    self._archive_slack_tasks_whose_inbox_tasks_are_completed_or_archived(
                        slack_tasks, inbox_tasks
                    )
                if args.do_notion_cleanup:
                    LOGGER.info("Garbage collecting Slack tasks which were archived")
                    allowed_slack_task_ref_ids = (
                        self._slack_task_notion_manager.load_all_saved_ref_ids(
                            slack_task_collection.ref_id
                        )
                    )

                    with self._storage_engine.get_unit_of_work() as uow:
                        slack_tasks = uow.slack_task_repository.find_all(
                            parent_ref_id=slack_task_collection.ref_id,
                            allow_archived=True,
                            filter_ref_ids=allowed_slack_task_ref_ids,
                        )
                    self._do_drop_all_archived_slack_tasks(
                        slack_task_collection, slack_tasks
                    )

    def _archive_done_inbox_tasks(self, inbox_tasks: Iterable[InboxTask]) -> None:
        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
        )
        for inbox_task in inbox_tasks:
            if not inbox_task.status.is_completed:
                continue

            inbox_task_archive_service.do_it(inbox_task)

    def _archive_done_big_plans(self, big_plans: Iterable[BigPlan]) -> None:
        """Archive the done big plans."""
        big_plan_archive_service = BigPlanArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
            big_plan_notion_manager=self._big_plan_notion_manager,
        )
        for big_plan in big_plans:
            if not big_plan.status.is_completed:
                continue
            big_plan_archive_service.do_it(big_plan)

    def _archive_slack_tasks_whose_inbox_tasks_are_completed_or_archived(
        self, slack_tasks: List[SlackTask], inbox_tasks: List[InboxTask]
    ) -> None:
        slack_tasks_by_ref_id = {st.ref_id: st for st in slack_tasks}
        slack_task_arhive_service = SlackTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
            slack_task_notion_manager=self._slack_task_notion_manager,
        )
        for inbox_task in inbox_tasks:
            if not (inbox_task.status.is_completed or inbox_task.archived):
                continue
            slack_task_arhive_service.do_it(
                slack_tasks_by_ref_id[cast(EntityId, inbox_task.slack_task_ref_id)]
            )

    def _do_anti_entropy_for_vacations(
        self, vacation_collection: VacationCollection, all_vacations: Iterable[Vacation]
    ) -> Iterable[Vacation]:
        vacations_names_set = {}
        for vacation in all_vacations:
            if vacation.name in vacations_names_set:
                LOGGER.info(
                    f"Found a duplicate vacation '{vacation.name}' - removing in anti-entropy"
                )
                # Apply changes locally
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.vacation_repository.remove(vacation.ref_id)
                    LOGGER.info("Applied local changes")

                try:
                    self._vacation_notion_manager.remove_leaf(
                        vacation_collection.ref_id, vacation.ref_id
                    )
                    LOGGER.info("Applied Notion changes")
                except NotionVacationNotFoundError:
                    LOGGER.info(
                        "Skipping removal on Notion side because vacation was not found"
                    )
                continue
            vacations_names_set[vacation.name] = vacation
        return vacations_names_set.values()

    def _do_anti_entropy_for_projects(
        self, project_collection: ProjectCollection, all_projects: Iterable[Project]
    ) -> Iterable[Project]:
        projects_names_set = {}
        for project in all_projects:
            if project.name in projects_names_set:
                LOGGER.info(
                    f"Found a duplicate project '{project.name}' - removing in anti-entropy"
                )
                # Apply changes locally
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.project_repository.remove(project.ref_id)
                    LOGGER.info("Applied local changes")

                try:
                    self._project_notion_manager.remove_leaf(
                        project_collection.ref_id, project.ref_id
                    )
                    LOGGER.info("Applied Notion changes")
                except NotionProjectNotFoundError:
                    LOGGER.info(
                        "Skipping removal on Notion side because project was not found"
                    )
                continue
            projects_names_set[project.name] = project
        return projects_names_set.values()

    def _do_anti_entropy_for_inbox_tasks(
        self, inbox_tasks: Iterable[InboxTask]
    ) -> Iterable[InboxTask]:
        inbox_tasks_names_set = {}
        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine, self._inbox_task_notion_manager
        )
        for inbox_task in inbox_tasks:
            if inbox_task.name in inbox_tasks_names_set:
                LOGGER.info(
                    f"Found a duplicate inbox task '{inbox_task.name}' - removing in anti-entropy"
                )
                inbox_task_remove_service.do_it(inbox_task)
                continue
            inbox_tasks_names_set[inbox_task.name] = inbox_task
        return inbox_tasks_names_set.values()

    def _do_anti_entropy_for_habits(
        self, all_habits: Iterable[Habit]
    ) -> Iterable[Habit]:
        habits_names_set = {}
        habit_remove_service = HabitRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._habit_notion_manager,
        )
        for habit in all_habits:
            if habit.name in habits_names_set:
                LOGGER.info(
                    f"Found a duplicate habit '{habit.name}' - removing in anti-entropy"
                )
                habit_remove_service.remove(habit.ref_id)
                continue
            habits_names_set[habit.name] = habit
        return habits_names_set.values()

    def _do_anti_entropy_for_chores(
        self, all_chores: Iterable[Chore]
    ) -> Iterable[Chore]:
        chores_names_set = {}
        chore_remove_service = ChoreRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._chore_notion_manager,
        )
        for chore in all_chores:
            if chore.name in chores_names_set:
                LOGGER.info(
                    f"Found a duplicate chore '{chore.name}' - removing in anti-entropy"
                )
                chore_remove_service.remove(chore.ref_id)
                continue
            chores_names_set[chore.name] = chore
        return chores_names_set.values()

    def _do_anti_entropy_for_big_plans(
        self, all_big_plans: Iterable[BigPlan]
    ) -> Iterable[BigPlan]:
        big_plans_names_set = {}
        big_plan_remove_service = BigPlanRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._big_plan_notion_manager,
        )
        for big_plan in all_big_plans:
            if big_plan.name in big_plans_names_set:
                LOGGER.info(
                    f"Found a duplicate big plan '{big_plan.name}' - removing in anti-entropy"
                )
                big_plan_remove_service.remove(big_plan.ref_id)
                continue
            big_plans_names_set[big_plan.name] = big_plan
        return big_plans_names_set.values()

    def _do_anti_entropy_for_smart_lists(
        self,
        smart_list_collection: SmartListCollection,
        all_smart_lists: Iterable[SmartList],
    ) -> Iterable[SmartList]:
        smart_lists_name_set = {}
        for smart_list in all_smart_lists:
            if smart_list.name in smart_lists_name_set:
                LOGGER.info(
                    f"Found a duplicate smart list '{smart_list.name}' - removing in anti-entropy"
                )

                with self._storage_engine.get_unit_of_work() as uow:
                    for smart_list_item in uow.smart_list_item_repository.find_all(
                        parent_ref_id=smart_list.ref_id, allow_archived=True
                    ):
                        uow.smart_list_item_repository.remove(smart_list_item.ref_id)

                    for smart_list_tag in uow.smart_list_tag_repository.find_all(
                        parent_ref_id=smart_list.ref_id, allow_archived=True
                    ):
                        uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)

                    uow.smart_list_repository.remove(smart_list.ref_id)

                LOGGER.info("Applied local changes")

                try:
                    self._smart_list_notion_manager.remove_branch(
                        smart_list_collection.ref_id, smart_list.ref_id
                    )
                    LOGGER.info("Applied Notion changes")
                except NotionSmartListNotFoundError:
                    LOGGER.info(
                        "Skipping removal on Notion side because smart list was not found"
                    )
                continue
            smart_lists_name_set[smart_list.name] = smart_list
        return smart_lists_name_set.values()

    def _do_anti_entropy_for_smart_list_items(
        self,
        smart_list_collection: SmartListCollection,
        smart_list: SmartList,
        all_smart_list_items: Iterable[SmartListItem],
    ) -> Iterable[SmartListItem]:
        smart_list_items_name_set = {}
        for smart_list_item in all_smart_list_items:
            if smart_list_item.name in smart_list_items_name_set:
                LOGGER.info(
                    f"Found a duplicate smart list item '{smart_list_item.name}' - removing in anti-entropy"
                )
                with self._storage_engine.get_unit_of_work() as uow:
                    uow.smart_list_item_repository.remove(smart_list_item.ref_id)
                    LOGGER.info("Applied local changes")

                try:
                    self._smart_list_notion_manager.remove_leaf(
                        smart_list_collection.ref_id,
                        smart_list.ref_id,
                        smart_list_item.ref_id,
                    )
                    LOGGER.info("Applied Notion changes")
                except NotionSmartListItemNotFoundError:
                    LOGGER.info(
                        "Skipping har removal on Notion side because recurring task was not found"
                    )
                continue
            smart_list_items_name_set[smart_list_item.name] = smart_list_item
        return smart_list_items_name_set.values()

    def _do_anti_entropy_for_metrics(
        self, metric_collection: MetricCollection, all_metrics: Iterable[Metric]
    ) -> Iterable[Metric]:
        metrics_name_set = {}
        for metric in all_metrics:
            metric_remove_service = MetricRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._metric_notion_manager,
            )
            if metric.name in metrics_name_set:
                LOGGER.info(
                    f"Found a duplicate metric '{metric.name}' - removing in anti-entropy"
                )
                metric_remove_service.execute(metric_collection, metric)
                continue
            metrics_name_set[metric.name] = metric
        return metrics_name_set.values()

    def _do_anti_entropy_for_metric_entries(
        self, metric: Metric, all_metric_entrys: Iterable[MetricEntry]
    ) -> Iterable[MetricEntry]:
        metric_entries_collection_time_set = {}
        for metric_entry in all_metric_entrys:
            if metric_entry.collection_time in metric_entries_collection_time_set:
                LOGGER.info(
                    f"Found a duplicate metric entry '{metric_entry.collection_time}' - removing in anti-entropy"
                )
                with self._storage_engine.get_unit_of_work() as uow:
                    metric_entry = uow.metric_entry_repository.remove(
                        metric_entry.ref_id
                    )
                    LOGGER.info("Applied local changes")

                try:
                    self._metric_notion_manager.remove_leaf(
                        metric.metric_collection_ref_id,
                        metric_entry.metric_ref_id,
                        metric_entry.ref_id,
                    )
                    LOGGER.info("Applied Notion changes")
                except NotionMetricEntryNotFoundError:
                    LOGGER.info(
                        "Skipping har removal on Notion side because recurring task was not found"
                    )
                continue
            metric_entries_collection_time_set[
                metric_entry.collection_time
            ] = metric_entry
        return metric_entries_collection_time_set.values()

    def _do_anti_entropy_for_persons(
        self, person_collection: PersonCollection, all_persons: Iterable[Person]
    ) -> Iterable[Person]:
        persons_name_set = {}
        person_remove_service = PersonRemoveService(
            self._storage_engine,
            self._person_notion_manager,
            self._inbox_task_notion_manager,
        )
        for person in all_persons:
            if person.name in persons_name_set:
                LOGGER.info(
                    f"Found a duplicate person '{person.name}' - removing in anti-entropy"
                )
                person_remove_service.do_it(person_collection, person)
                continue
            persons_name_set[person.name] = person
        return persons_name_set.values()

    def _do_drop_all_archived_vacations(
        self, vacation_collection: VacationCollection, all_vacations: Iterable[Vacation]
    ) -> None:
        for vacation in all_vacations:
            if not vacation.archived:
                continue
            LOGGER.info(
                f"Removed an archived vacation '{vacation.name}' on Notion side"
            )
            try:
                self._vacation_notion_manager.remove_leaf(
                    vacation_collection.ref_id, vacation.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionVacationNotFoundError:
                LOGGER.info(
                    "Skipping removal on Notion side because vacation was not found"
                )

    def _do_drop_all_archived_projects(
        self, project_collection: ProjectCollection, all_projects: Iterable[Project]
    ) -> None:
        for project in all_projects:
            if not project.archived:
                continue
            LOGGER.info(f"Removed an archived project '{project.name}' on Notion side")
            try:
                self._project_notion_manager.remove_leaf(
                    project_collection.ref_id, project.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionProjectNotFoundError:
                LOGGER.info(
                    "Skipping removal on Notion side because project was not found"
                )

    def _do_drop_all_archived_inbox_tasks(
        self, inbox_tasks: Iterable[InboxTask]
    ) -> None:
        for inbox_task in inbox_tasks:
            if not inbox_task.archived:
                continue
            LOGGER.info(
                f"Removed an archived inbox tasks '{inbox_task.name}' on Notion side"
            )
            try:
                self._inbox_task_notion_manager.remove_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionInboxTaskNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping removal on Notion side because inbox task was not found"
                )

    def _do_drop_all_archived_habits(self, habits: Iterable[Habit]) -> None:
        for habit in habits:
            if not habit.archived:
                continue
            LOGGER.info(f"Removed an archived habit '{habit.name}' on Notion side")
            try:
                self._habit_notion_manager.remove_leaf(
                    habit.habit_collection_ref_id, habit.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionHabitNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping removal on Notion side because big plan was not found"
                )
            # TODO(horia141): more can be done here surely!

    def _do_drop_all_archived_chores(self, chores: Iterable[Chore]) -> None:
        for chore in chores:
            if not chore.archived:
                continue
            LOGGER.info(f"Removed an archived chore '{chore.name}' on Notion side")
            try:
                self._chore_notion_manager.remove_leaf(
                    chore.chore_collection_ref_id, chore.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionChoreNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping removal on Notion side because big plan was not found"
                )
            # TODO(horia141): more can be done here surely!

    def _do_drop_all_archived_big_plans(self, big_plans: Iterable[BigPlan]) -> None:
        for big_plan in big_plans:
            if not big_plan.archived:
                continue
            LOGGER.info(
                f"Removed an archived big plan '{big_plan.name}' on Notion side"
            )
            try:
                self._big_plan_notion_manager.remove_leaf(
                    big_plan.big_plan_collection_ref_id, big_plan.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionBigPlanNotFoundError:
                # If we can't find this locally it means it's already gone
                LOGGER.info(
                    "Skipping removal on Notion side because big plan was not found"
                )

    def _do_drop_all_archived_smart_lists(
        self,
        smart_list_collection: SmartListCollection,
        smart_lists: Iterable[SmartList],
    ) -> None:
        for smart_list in smart_lists:
            if not smart_list.archived:
                continue
            LOGGER.info(
                f"Removed an archived smart list '{smart_list.name}' on Notion side"
            )

            try:
                self._smart_list_notion_manager.remove_branch(
                    smart_list_collection.ref_id, smart_list.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionSmartListNotFoundError:
                LOGGER.info(
                    "Skipping removal on Notion side because smart list was not found"
                )

    def _do_drop_all_archived_smart_list_items(
        self,
        smart_list_collection: SmartListCollection,
        smart_list: SmartList,
        smart_list_items: Iterable[SmartListItem],
    ) -> None:
        for smart_list_item in smart_list_items:
            if not smart_list_item.archived:
                continue
            LOGGER.info(
                f"Removed an archived smart list item '{smart_list_item.name}' on Notion side"
            )
            try:
                self._smart_list_notion_manager.remove_leaf(
                    smart_list_collection.ref_id,
                    smart_list.ref_id,
                    smart_list_item.ref_id,
                )
                LOGGER.info("Applied Notion changes")
            except NotionSmartListItemNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because smart list was not found"
                )

    def _do_drop_all_archived_metrics(
        self, metric_collection: MetricCollection, metrics: Iterable[Metric]
    ) -> None:
        for metric in metrics:
            if not metric.archived:
                continue
            LOGGER.info(f"Removed an archived metric '{metric.name}' on Notion side")
            try:
                self._metric_notion_manager.remove_branch(
                    metric_collection.ref_id, metric.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionMetricNotFoundError:
                LOGGER.info(
                    "Skipping archival on Notion side because metric was not found"
                )

    def _do_drop_all_archived_metric_entries(
        self, metric: Metric, metric_entries: Iterable[MetricEntry]
    ) -> None:
        for metric_entry in metric_entries:
            if not metric_entry.archived:
                continue
            LOGGER.info(
                f"Removed an archived metric entry '{metric_entry.collection_time}' on Notion side"
            )
            try:
                self._metric_notion_manager.remove_leaf(
                    metric.metric_collection_ref_id,
                    metric_entry.metric_ref_id,
                    metric_entry.ref_id,
                )
                LOGGER.info("Applied Notion changes")
            except NotionMetricEntryNotFoundError:
                LOGGER.info(
                    "Skipping the removal on Notion side because recurring task was not found"
                )

    def _do_drop_all_archived_persons(
        self, person_collection: PersonCollection, persons: Iterable[Person]
    ) -> None:
        for person in persons:
            if not person.archived:
                continue
            LOGGER.info(f"Removed an archived person '{person.name}' on Notion side")
            try:
                self._person_notion_manager.remove_leaf(
                    person_collection.ref_id, person.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionPersonNotFoundError:
                LOGGER.info(
                    "Skipping the removal on Notion side because person was not found"
                )

    def _do_drop_all_archived_slack_tasks(
        self,
        slack_task_collection: SlackTaskCollection,
        slack_tasks: Iterable[SlackTask],
    ) -> None:
        for slack_task in slack_tasks:
            if not slack_task.archived:
                continue
            LOGGER.info(
                f"Removed an archived slack task '{slack_task.simple_name}' on Notion side"
            )
            try:
                self._slack_task_notion_manager.remove_leaf(
                    slack_task_collection.ref_id, slack_task.ref_id
                )
                LOGGER.info("Applied Notion changes")
            except NotionSlackTaskNotFoundError:
                LOGGER.info(
                    "Skipping the removal on Notion side because slack_task was not found"
                )
