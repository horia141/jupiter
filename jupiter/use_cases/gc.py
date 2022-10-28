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
from jupiter.domain.push_integrations.email.email_task import EmailTask
from jupiter.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
    NotionEmailTaskNotFoundError,
)
from jupiter.domain.push_integrations.email.service.archive_service import (
    EmailTaskArchiveService,
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
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
    MarkProgressStatus,
)
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
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
    _email_task_notion_manager: Final[EmailTaskNotionManager]

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
        email_task_notion_manager: EmailTaskNotionManager,
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
        self._email_task_notion_manager = email_task_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        workspace = context.workspace

        with self._storage_engine.get_unit_of_work() as uow:
            vacation_collection = uow.vacation_collection_repository.load_by_parent(
                workspace.ref_id
            )
            project_collection = uow.project_collection_repository.load_by_parent(
                workspace.ref_id
            )
            inbox_task_collection = uow.inbox_task_collection_repository.load_by_parent(
                workspace.ref_id
            )
            habit_collection = uow.habit_collection_repository.load_by_parent(
                workspace.ref_id
            )
            chore_collection = uow.chore_collection_repository.load_by_parent(
                workspace.ref_id
            )
            big_plan_collection = uow.big_plan_collection_repository.load_by_parent(
                workspace.ref_id
            )
            smart_list_collection = uow.smart_list_collection_repository.load_by_parent(
                workspace.ref_id
            )
            metric_collection = uow.metric_collection_repository.load_by_parent(
                workspace.ref_id
            )
            person_collection = uow.person_collection_repository.load_by_parent(
                workspace.ref_id
            )
            push_integration_group = (
                uow.push_integration_group_repository.load_by_parent(workspace.ref_id)
            )
            slack_task_collection = uow.slack_task_collection_repository.load_by_parent(
                push_integration_group.ref_id
            )
            email_task_collection = uow.email_task_collection_repository.load_by_parent(
                push_integration_group.ref_id
            )

        if SyncTarget.VACATIONS in args.sync_targets:
            with progress_reporter.section("Vacations"):
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for vacations"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            vacations = uow.vacation_repository.find_all(
                                parent_ref_id=vacation_collection.ref_id,
                                allow_archived=True,
                            )
                        self._do_anti_entropy_for_vacations(
                            progress_reporter, vacation_collection, vacations
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting vacations which were archived"
                    ):
                        allowed_ref_ids = (
                            self._vacation_notion_manager.load_all_saved_ref_ids(
                                vacation_collection.ref_id
                            )
                        )

                        with self._storage_engine.get_unit_of_work() as uow:
                            vacations = uow.vacation_repository.find_all(
                                parent_ref_id=vacation_collection.ref_id,
                                allow_archived=True,
                                filter_ref_ids=allowed_ref_ids,
                            )
                        self._do_drop_all_archived_vacations(
                            progress_reporter, vacation_collection, vacations
                        )

        if SyncTarget.PROJECTS in args.sync_targets:
            need_to_modifiy_something = False
            with progress_reporter.section("Projects"):
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for projects"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            projects = uow.project_repository.find_all(
                                parent_ref_id=project_collection.ref_id,
                                allow_archived=True,
                            )
                        did_work = self._do_anti_entropy_for_projects(
                            progress_reporter, project_collection, projects
                        )
                        need_to_modifiy_something = (
                            need_to_modifiy_something or did_work
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting projects which were archived"
                    ):
                        allowed_ref_ids = (
                            self._project_notion_manager.load_all_saved_ref_ids(
                                project_collection.ref_id
                            )
                        )

                        with self._storage_engine.get_unit_of_work() as uow:
                            projects = uow.project_repository.find_all_with_filters(
                                parent_ref_id=project_collection.ref_id,
                                allow_archived=True,
                                filter_ref_ids=allowed_ref_ids,
                            )
                        self._do_drop_all_archived_projects(
                            progress_reporter, project_collection, projects
                        )

                if need_to_modifiy_something:
                    ProjectLabelUpdateService(
                        self._storage_engine,
                        self._inbox_task_notion_manager,
                        self._habit_notion_manager,
                        self._chore_notion_manager,
                        self._big_plan_notion_manager,
                    ).sync(workspace, projects)

        if SyncTarget.INBOX_TASKS in args.sync_targets:
            with progress_reporter.section("Inbox Tasks"):
                if args.do_archival:
                    with progress_reporter.section("Archiving all done inbox tasks"):
                        with self._storage_engine.get_unit_of_work() as uow:
                            inbox_tasks = uow.inbox_task_repository.find_all(
                                parent_ref_id=inbox_task_collection.ref_id,
                                allow_archived=False,
                            )
                        self._archive_done_inbox_tasks(progress_reporter, inbox_tasks)
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for inbox tasks"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            inbox_tasks = uow.inbox_task_repository.find_all(
                                parent_ref_id=inbox_task_collection.ref_id,
                                allow_archived=True,
                            )
                        self._do_anti_entropy_for_inbox_tasks(
                            progress_reporter, inbox_tasks
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting inbox tasks which were archived"
                    ):
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
                        self._do_drop_all_archived_inbox_tasks(
                            progress_reporter, inbox_tasks
                        )

        if SyncTarget.HABITS in args.sync_targets:
            with progress_reporter.section("Habits"):
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for habits"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            habits = uow.habit_repository.find_all(
                                parent_ref_id=habit_collection.ref_id,
                                allow_archived=True,
                            )
                        self._do_anti_entropy_for_habits(progress_reporter, habits)
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting habits which were archived"
                    ):
                        allowed_ref_ids = (
                            self._habit_notion_manager.load_all_saved_ref_ids(
                                habit_collection.ref_id
                            )
                        )
                        with self._storage_engine.get_unit_of_work() as uow:
                            habits = uow.habit_repository.find_all(
                                parent_ref_id=habit_collection.ref_id,
                                allow_archived=True,
                                filter_ref_ids=allowed_ref_ids,
                            )
                        self._do_drop_all_archived_habits(progress_reporter, habits)

        if SyncTarget.CHORES in args.sync_targets:
            with progress_reporter.section("Chores"):
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for chores"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            chores = uow.chore_repository.find_all(
                                parent_ref_id=chore_collection.ref_id,
                                allow_archived=True,
                            )
                        self._do_anti_entropy_for_chores(progress_reporter, chores)
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting chores which were archived"
                    ):
                        allowed_ref_ids = (
                            self._chore_notion_manager.load_all_saved_ref_ids(
                                chore_collection.ref_id
                            )
                        )
                        with self._storage_engine.get_unit_of_work() as uow:
                            chores = uow.chore_repository.find_all(
                                parent_ref_id=chore_collection.ref_id,
                                allow_archived=True,
                                filter_ref_ids=allowed_ref_ids,
                            )
                        self._do_drop_all_archived_chores(progress_reporter, chores)

        if SyncTarget.BIG_PLANS in args.sync_targets:
            need_to_modifiy_something = False
            with progress_reporter.section("Big Plans"):
                if args.do_archival:
                    with progress_reporter.section("Archiving all done big plans"):
                        with self._storage_engine.get_unit_of_work() as uow:
                            big_plans = uow.big_plan_repository.find_all(
                                parent_ref_id=big_plan_collection.ref_id,
                                allow_archived=False,
                            )
                        did_work = self._archive_done_big_plans(
                            progress_reporter, big_plans
                        )
                        need_to_modifiy_something = (
                            need_to_modifiy_something or did_work
                        )
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for big plans"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            big_plans = uow.big_plan_repository.find_all(
                                parent_ref_id=big_plan_collection.ref_id,
                                allow_archived=True,
                            )
                        did_work = self._do_anti_entropy_for_big_plans(
                            progress_reporter, workspace, big_plans
                        )
                        need_to_modifiy_something = (
                            need_to_modifiy_something or did_work
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting big plans which were archived"
                    ):
                        allowed_ref_ids = (
                            self._big_plan_notion_manager.load_all_saved_ref_ids(
                                big_plan_collection.ref_id
                            )
                        )
                        with self._storage_engine.get_unit_of_work() as uow:
                            big_plans = uow.big_plan_repository.find_all(
                                parent_ref_id=big_plan_collection.ref_id,
                                allow_archived=True,
                                filter_ref_ids=allowed_ref_ids,
                            )
                        self._do_drop_all_archived_big_plans(
                            progress_reporter, big_plans
                        )

                if need_to_modifiy_something:
                    InboxTaskBigPlanRefOptionsUpdateService(
                        self._storage_engine, self._inbox_task_notion_manager
                    ).sync(big_plan_collection)

        if SyncTarget.SMART_LISTS in args.sync_targets:
            smart_lists: Iterable[SmartList] = []
            with progress_reporter.section("Smart Lists"):
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for smart lists"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            smart_lists = uow.smart_list_repository.find_all(
                                parent_ref_id=smart_list_collection.ref_id,
                                allow_archived=True,
                            )
                        smart_lists = self._do_anti_entropy_for_smart_lists(
                            progress_reporter, smart_list_collection, smart_lists
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting smart lists which were archived"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            smart_lists = (
                                smart_lists
                                or uow.smart_list_repository.find_all(
                                    parent_ref_id=smart_list_collection.ref_id,
                                    allow_archived=True,
                                )
                            )
                        self._do_drop_all_archived_smart_lists(
                            progress_reporter, smart_list_collection, smart_lists
                        )
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for smart list items"
                    ):
                        for smart_list in smart_lists:
                            with self._storage_engine.get_unit_of_work() as uow:
                                smart_list_items = (
                                    uow.smart_list_item_repository.find_all(
                                        parent_ref_id=smart_list.ref_id,
                                        allow_archived=True,
                                    )
                                )
                            self._do_anti_entropy_for_smart_list_items(
                                progress_reporter,
                                smart_list_collection,
                                smart_list,
                                smart_list_items,
                            )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting smart list items which were archived"
                    ):
                        for smart_list in smart_lists:
                            allowed_ref_ids = set(
                                self._smart_list_notion_manager.load_all_saved_ref_ids(
                                    smart_list_collection.ref_id, smart_list.ref_id
                                )
                            )
                            with self._storage_engine.get_unit_of_work() as uow:
                                smart_list_items = (
                                    uow.smart_list_item_repository.find_all(
                                        parent_ref_id=smart_list.ref_id,
                                        allow_archived=True,
                                        filter_ref_ids=allowed_ref_ids,
                                    )
                                )
                            self._do_drop_all_archived_smart_list_items(
                                progress_reporter,
                                smart_list_collection,
                                smart_list,
                                smart_list_items,
                            )

        if SyncTarget.METRICS in args.sync_targets:
            metrics: Iterable[Metric] = []
            with progress_reporter.section("Metrics"):
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for metrics"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            metrics = uow.metric_repository.find_all(
                                parent_ref_id=metric_collection.ref_id,
                                allow_archived=True,
                            )
                        metrics = self._do_anti_entropy_for_metrics(
                            progress_reporter, metric_collection, metrics
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting metrics which were archived"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            metrics = metrics or uow.metric_repository.find_all(
                                parent_ref_id=metric_collection.ref_id,
                                allow_archived=True,
                            )
                        self._do_drop_all_archived_metrics(
                            progress_reporter, metric_collection, metrics
                        )
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for metric entries"
                    ):
                        for metric in metrics:
                            with self._storage_engine.get_unit_of_work() as uow:
                                metric_entries = uow.metric_entry_repository.find_all(
                                    parent_ref_id=metric.ref_id, allow_archived=True
                                )
                            self._do_anti_entropy_for_metric_entries(
                                progress_reporter, metric, metric_entries
                            )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting metric entries which were archived"
                    ):
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
                            self._do_drop_all_archived_metric_entries(
                                progress_reporter, metric, metric_entries
                            )

        if SyncTarget.PERSONS in args.sync_targets:
            with progress_reporter.section("Persons"):
                if args.do_anti_entropy:
                    with progress_reporter.section(
                        "Performing anti-entropy adjustments for persons"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            persons = uow.person_repository.find_all(
                                parent_ref_id=person_collection.ref_id,
                                allow_archived=True,
                            )
                        self._do_anti_entropy_for_persons(
                            progress_reporter, person_collection, persons
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting persons which were archived"
                    ):
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
                        self._do_drop_all_archived_persons(
                            progress_reporter, person_collection, persons
                        )

        if SyncTarget.SLACK_TASKS in args.sync_targets:
            with progress_reporter.section("Slack Tasks"):
                if args.do_archival:
                    with progress_reporter.section(
                        "Archiving all Slack tasks whose inbox tasks are done or archived"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            slack_tasks = uow.slack_task_repository.find_all(
                                parent_ref_id=slack_task_collection.ref_id,
                                allow_archived=False,
                            )
                            inbox_tasks = (
                                uow.inbox_task_repository.find_all_with_filters(
                                    parent_ref_id=inbox_task_collection.ref_id,
                                    allow_archived=True,
                                    filter_sources=[InboxTaskSource.SLACK_TASK],
                                    filter_slack_task_ref_ids=[
                                        st.ref_id for st in slack_tasks
                                    ],
                                )
                            )
                        self._archive_slack_tasks_whose_inbox_tasks_are_completed_or_archived(
                            progress_reporter, slack_tasks, inbox_tasks
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting Slack tasks which were archived"
                    ):
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
                            progress_reporter, slack_task_collection, slack_tasks
                        )

        if SyncTarget.EMAIL_TASKS in args.sync_targets:
            with progress_reporter.section("Email Tasks"):
                if args.do_archival:
                    with progress_reporter.section(
                        "Archiving all email tasks whose inbox tasks are done or archived"
                    ):
                        with self._storage_engine.get_unit_of_work() as uow:
                            email_tasks = uow.email_task_repository.find_all(
                                parent_ref_id=email_task_collection.ref_id,
                                allow_archived=False,
                            )
                            inbox_tasks = (
                                uow.inbox_task_repository.find_all_with_filters(
                                    parent_ref_id=inbox_task_collection.ref_id,
                                    allow_archived=True,
                                    filter_sources=[InboxTaskSource.EMAIL_TASK],
                                    filter_email_task_ref_ids=[
                                        et.ref_id for et in email_tasks
                                    ],
                                )
                            )
                        self._archive_email_tasks_whose_inbox_tasks_are_completed_or_archived(
                            progress_reporter, email_tasks, inbox_tasks
                        )
                if args.do_notion_cleanup:
                    with progress_reporter.section(
                        "Garbage collecting email tasks which were archived"
                    ):
                        allowed_email_task_ref_ids = (
                            self._email_task_notion_manager.load_all_saved_ref_ids(
                                email_task_collection.ref_id
                            )
                        )

                        with self._storage_engine.get_unit_of_work() as uow:
                            email_tasks = uow.email_task_repository.find_all(
                                parent_ref_id=email_task_collection.ref_id,
                                allow_archived=True,
                                filter_ref_ids=allowed_email_task_ref_ids,
                            )
                        self._do_drop_all_archived_email_tasks(
                            progress_reporter, email_task_collection, email_tasks
                        )

    def _archive_done_inbox_tasks(
        self, progress_reporter: ProgressReporter, inbox_tasks: Iterable[InboxTask]
    ) -> None:
        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
        )
        for inbox_task in inbox_tasks:
            if not inbox_task.status.is_completed:
                continue
            inbox_task_archive_service.do_it(progress_reporter, inbox_task)

    def _archive_done_big_plans(
        self, progress_reporter: ProgressReporter, big_plans: Iterable[BigPlan]
    ) -> bool:
        """Archive the done big plans."""
        big_plan_archive_service = BigPlanArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
            big_plan_notion_manager=self._big_plan_notion_manager,
        )
        need_to_modify_something = False
        for big_plan in big_plans:
            if not big_plan.status.is_completed:
                continue
            big_plan_archive_service.do_it(progress_reporter, big_plan)
            need_to_modify_something = True
        return need_to_modify_something

    def _archive_slack_tasks_whose_inbox_tasks_are_completed_or_archived(
        self,
        progress_reporter: ProgressReporter,
        slack_tasks: List[SlackTask],
        inbox_tasks: List[InboxTask],
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
                progress_reporter,
                slack_tasks_by_ref_id[cast(EntityId, inbox_task.slack_task_ref_id)],
            )

    def _archive_email_tasks_whose_inbox_tasks_are_completed_or_archived(
        self,
        progress_reporter: ProgressReporter,
        email_tasks: List[EmailTask],
        inbox_tasks: List[InboxTask],
    ) -> None:
        email_tasks_by_ref_id = {st.ref_id: st for st in email_tasks}
        email_task_arhive_service = EmailTaskArchiveService(
            source=EventSource.CLI,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
            email_task_notion_manager=self._email_task_notion_manager,
        )
        for inbox_task in inbox_tasks:
            if not (inbox_task.status.is_completed or inbox_task.archived):
                continue
            email_task_arhive_service.do_it(
                progress_reporter,
                email_tasks_by_ref_id[cast(EntityId, inbox_task.email_task_ref_id)],
            )

    def _do_anti_entropy_for_vacations(
        self,
        progress_reporter: ProgressReporter,
        vacation_collection: VacationCollection,
        all_vacations: Iterable[Vacation],
    ) -> Iterable[Vacation]:
        vacations_names_set = {}
        for vacation in all_vacations:
            if vacation.name in vacations_names_set:
                with progress_reporter.start_removing_entity(
                    "vacation", vacation.ref_id, str(vacation.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.vacation_repository.remove(vacation.ref_id)
                        entity_reporter.mark_local_change()

                    try:
                        self._vacation_notion_manager.remove_leaf(
                            vacation_collection.ref_id, vacation.ref_id
                        )
                        entity_reporter.mark_remote_change()
                    except NotionVacationNotFoundError:
                        LOGGER.info(
                            "Skipping removal on Notion side because vacation was not found"
                        )
                        entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
                    continue
            vacations_names_set[vacation.name] = vacation
        return vacations_names_set.values()

    def _do_anti_entropy_for_projects(
        self,
        progress_reporter: ProgressReporter,
        project_collection: ProjectCollection,
        all_projects: Iterable[Project],
    ) -> bool:
        projects_names_set = {}
        need_to_modify_something = False
        for project in all_projects:
            if project.name in projects_names_set:
                with progress_reporter.start_removing_entity(
                    "project", project.ref_id, str(project.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.project_repository.remove(project.ref_id)
                        entity_reporter.mark_local_change()

                    try:
                        self._project_notion_manager.remove_leaf(
                            project_collection.ref_id, project.ref_id
                        )
                        entity_reporter.mark_remote_change()
                    except NotionProjectNotFoundError:
                        LOGGER.info(
                            "Skipping removal on Notion side because project was not found"
                        )
                        entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
                need_to_modify_something = True
                continue
            projects_names_set[project.name] = project
        return need_to_modify_something

    def _do_anti_entropy_for_inbox_tasks(
        self, progress_reporter: ProgressReporter, inbox_tasks: Iterable[InboxTask]
    ) -> Iterable[InboxTask]:
        inbox_tasks_names_set = {}
        inbox_task_remove_service = InboxTaskRemoveService(
            self._storage_engine, self._inbox_task_notion_manager
        )
        for inbox_task in inbox_tasks:
            if inbox_task.name in inbox_tasks_names_set:
                inbox_task_remove_service.do_it(progress_reporter, inbox_task)
                continue
            inbox_tasks_names_set[inbox_task.name] = inbox_task
        return inbox_tasks_names_set.values()

    def _do_anti_entropy_for_habits(
        self, progress_reporter: ProgressReporter, all_habits: Iterable[Habit]
    ) -> Iterable[Habit]:
        habits_names_set = {}
        habit_remove_service = HabitRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._habit_notion_manager,
        )
        for habit in all_habits:
            if habit.name in habits_names_set:
                habit_remove_service.remove(progress_reporter, habit.ref_id)
                continue
            habits_names_set[habit.name] = habit
        return habits_names_set.values()

    def _do_anti_entropy_for_chores(
        self, progress_reporter: ProgressReporter, all_chores: Iterable[Chore]
    ) -> Iterable[Chore]:
        chores_names_set = {}
        chore_remove_service = ChoreRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._chore_notion_manager,
        )
        for chore in all_chores:
            if chore.name in chores_names_set:
                chore_remove_service.remove(progress_reporter, chore.ref_id)
                continue
            chores_names_set[chore.name] = chore
        return chores_names_set.values()

    def _do_anti_entropy_for_big_plans(
        self,
        progress_reporter: ProgressReporter,
        workspace: Workspace,
        all_big_plans: Iterable[BigPlan],
    ) -> bool:
        big_plans_names_set = {}
        big_plan_remove_service = BigPlanRemoveService(
            self._storage_engine,
            self._inbox_task_notion_manager,
            self._big_plan_notion_manager,
        )
        need_to_modify_something = False
        for big_plan in all_big_plans:
            if big_plan.name in big_plans_names_set:
                big_plan_remove_service.remove(
                    progress_reporter, workspace, big_plan.ref_id
                )
                continue
            big_plans_names_set[big_plan.name] = big_plan
            need_to_modify_something = True
        return need_to_modify_something

    def _do_anti_entropy_for_smart_lists(
        self,
        progress_reporter: ProgressReporter,
        smart_list_collection: SmartListCollection,
        all_smart_lists: Iterable[SmartList],
    ) -> Iterable[SmartList]:
        smart_lists_name_set = {}
        for smart_list in all_smart_lists:
            if smart_list.name in smart_lists_name_set:
                with self._storage_engine.get_unit_of_work() as uow:
                    for smart_list_item in uow.smart_list_item_repository.find_all(
                        parent_ref_id=smart_list.ref_id, allow_archived=True
                    ):
                        with progress_reporter.start_removing_entity(
                            "smart list item",
                            smart_list_item.ref_id,
                            str(smart_list_item.name),
                        ) as entity_reporter:
                            uow.smart_list_item_repository.remove(
                                smart_list_item.ref_id
                            )
                            entity_reporter.mark_local_change()

                    for smart_list_tag in uow.smart_list_tag_repository.find_all(
                        parent_ref_id=smart_list.ref_id, allow_archived=True
                    ):
                        with progress_reporter.start_removing_entity(
                            "smart list tag",
                            smart_list_tag.ref_id,
                            str(smart_list_tag.tag_name),
                        ) as entity_reporter:
                            uow.smart_list_tag_repository.remove(smart_list_tag.ref_id)
                            entity_reporter.mark_local_change()

                with progress_reporter.start_removing_entity(
                    "smart list", smart_list.ref_id, str(smart_list.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.smart_list_repository.remove(smart_list.ref_id)
                        entity_reporter.mark_local_change()

                    try:
                        self._smart_list_notion_manager.remove_branch(
                            smart_list_collection.ref_id, smart_list.ref_id
                        )
                        entity_reporter.mark_remote_change()
                    except NotionSmartListNotFoundError:
                        LOGGER.info(
                            "Skipping removal on Notion side because smart list was not found"
                        )
                        entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
                continue
            smart_lists_name_set[smart_list.name] = smart_list
        return smart_lists_name_set.values()

    def _do_anti_entropy_for_smart_list_items(
        self,
        progress_reporter: ProgressReporter,
        smart_list_collection: SmartListCollection,
        smart_list: SmartList,
        all_smart_list_items: Iterable[SmartListItem],
    ) -> Iterable[SmartListItem]:
        smart_list_items_name_set = {}
        for smart_list_item in all_smart_list_items:
            if smart_list_item.name in smart_list_items_name_set:
                with progress_reporter.start_removing_entity(
                    "smart list item", smart_list_item.ref_id, str(smart_list_item.name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.smart_list_item_repository.remove(smart_list_item.ref_id)
                        entity_reporter.mark_local_change()

                    try:
                        self._smart_list_notion_manager.remove_leaf(
                            smart_list_collection.ref_id,
                            smart_list.ref_id,
                            smart_list_item.ref_id,
                        )
                        entity_reporter.mark_remote_change()
                    except NotionSmartListItemNotFoundError:
                        LOGGER.info(
                            "Skipping har removal on Notion side because recurring task was not found"
                        )
                        entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
                continue
            smart_list_items_name_set[smart_list_item.name] = smart_list_item
        return smart_list_items_name_set.values()

    def _do_anti_entropy_for_metrics(
        self,
        progress_reporter: ProgressReporter,
        metric_collection: MetricCollection,
        all_metrics: Iterable[Metric],
    ) -> Iterable[Metric]:
        metrics_name_set = {}
        for metric in all_metrics:
            metric_remove_service = MetricRemoveService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._metric_notion_manager,
            )
            if metric.name in metrics_name_set:
                metric_remove_service.execute(
                    progress_reporter, metric_collection, metric
                )
                continue
            metrics_name_set[metric.name] = metric
        return metrics_name_set.values()

    def _do_anti_entropy_for_metric_entries(
        self,
        progress_reporter: ProgressReporter,
        metric: Metric,
        all_metric_entrys: Iterable[MetricEntry],
    ) -> Iterable[MetricEntry]:
        metric_entries_collection_time_set = {}
        for metric_entry in all_metric_entrys:
            if metric_entry.collection_time in metric_entries_collection_time_set:
                with progress_reporter.start_removing_entity(
                    "metric entry", metric_entry.ref_id, str(metric_entry.simple_name)
                ) as entity_reporter:
                    with self._storage_engine.get_unit_of_work() as uow:
                        metric_entry = uow.metric_entry_repository.remove(
                            metric_entry.ref_id
                        )
                        entity_reporter.mark_local_change()

                    try:
                        self._metric_notion_manager.remove_leaf(
                            metric.metric_collection_ref_id,
                            metric_entry.metric_ref_id,
                            metric_entry.ref_id,
                        )
                        entity_reporter.mark_remote_change()
                    except NotionMetricEntryNotFoundError:
                        LOGGER.info(
                            "Skipping har removal on Notion side because recurring task was not found"
                        )
                        entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
                continue
            metric_entries_collection_time_set[
                metric_entry.collection_time
            ] = metric_entry
        return metric_entries_collection_time_set.values()

    def _do_anti_entropy_for_persons(
        self,
        progress_reporter: ProgressReporter,
        person_collection: PersonCollection,
        all_persons: Iterable[Person],
    ) -> Iterable[Person]:
        persons_name_set = {}
        person_remove_service = PersonRemoveService(
            self._storage_engine,
            self._person_notion_manager,
            self._inbox_task_notion_manager,
        )
        for person in all_persons:
            if person.name in persons_name_set:
                person_remove_service.do_it(
                    progress_reporter, person_collection, person
                )
                continue
            persons_name_set[person.name] = person
        return persons_name_set.values()

    def _do_drop_all_archived_vacations(
        self,
        progress_reporter: ProgressReporter,
        vacation_collection: VacationCollection,
        all_vacations: Iterable[Vacation],
    ) -> None:
        for vacation in all_vacations:
            if not vacation.archived:
                continue
            with progress_reporter.start_updating_entity(
                "vacation", vacation.ref_id, str(vacation.name)
            ) as entity_reporter:
                try:
                    self._vacation_notion_manager.remove_leaf(
                        vacation_collection.ref_id, vacation.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionVacationNotFoundError:
                    LOGGER.info(
                        "Skipping removal on Notion side because vacation was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_projects(
        self,
        progress_reporter: ProgressReporter,
        project_collection: ProjectCollection,
        all_projects: Iterable[Project],
    ) -> None:
        for project in all_projects:
            if not project.archived:
                continue
            with progress_reporter.start_updating_entity(
                "project", project.ref_id, str(project.name)
            ) as entity_reporter:
                try:
                    self._project_notion_manager.remove_leaf(
                        project_collection.ref_id, project.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionProjectNotFoundError:
                    LOGGER.info(
                        "Skipping removal on Notion side because project was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_inbox_tasks(
        self, progress_reporter: ProgressReporter, inbox_tasks: Iterable[InboxTask]
    ) -> None:
        for inbox_task in inbox_tasks:
            if not inbox_task.archived:
                continue
            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                try:
                    self._inbox_task_notion_manager.remove_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionInboxTaskNotFoundError:
                    # If we can't find this locally it means it's already gone
                    LOGGER.info(
                        "Skipping removal on Notion side because inbox task was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_habits(
        self, progress_reporter: ProgressReporter, habits: Iterable[Habit]
    ) -> None:
        for habit in habits:
            if not habit.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "habit", habit.ref_id, str(habit.name)
            ) as entity_reporter:
                try:
                    self._habit_notion_manager.remove_leaf(
                        habit.habit_collection_ref_id, habit.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionHabitNotFoundError:
                    # If we can't find this locally it means it's already gone
                    LOGGER.info(
                        "Skipping removal on Notion side because big plan was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
            # TODO(horia141): more can be done here surely!

    def _do_drop_all_archived_chores(
        self, progress_reporter: ProgressReporter, chores: Iterable[Chore]
    ) -> None:
        for chore in chores:
            if not chore.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "chore", chore.ref_id, str(chore.name)
            ) as entity_reporter:
                try:
                    self._chore_notion_manager.remove_leaf(
                        chore.chore_collection_ref_id, chore.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionChoreNotFoundError:
                    # If we can't find this locally it means it's already gone
                    LOGGER.info(
                        "Skipping removal on Notion side because big plan was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
            # TODO(horia141): more can be done here surely!

    def _do_drop_all_archived_big_plans(
        self, progress_reporter: ProgressReporter, big_plans: Iterable[BigPlan]
    ) -> None:
        for big_plan in big_plans:
            if not big_plan.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "big plan", big_plan.ref_id, str(big_plan.name)
            ) as entity_reporter:
                try:
                    self._big_plan_notion_manager.remove_leaf(
                        big_plan.big_plan_collection_ref_id, big_plan.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionBigPlanNotFoundError:
                    # If we can't find this locally it means it's already gone
                    LOGGER.info(
                        "Skipping removal on Notion side because big plan was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_smart_lists(
        self,
        progress_reporter: ProgressReporter,
        smart_list_collection: SmartListCollection,
        smart_lists: Iterable[SmartList],
    ) -> None:
        for smart_list in smart_lists:
            if not smart_list.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "smart list", smart_list.ref_id, str(smart_list.name)
            ) as entity_reporter:
                try:
                    self._smart_list_notion_manager.remove_branch(
                        smart_list_collection.ref_id, smart_list.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionSmartListNotFoundError:
                    LOGGER.info(
                        "Skipping removal on Notion side because smart list was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_smart_list_items(
        self,
        progress_reporter: ProgressReporter,
        smart_list_collection: SmartListCollection,
        smart_list: SmartList,
        smart_list_items: Iterable[SmartListItem],
    ) -> None:
        for smart_list_item in smart_list_items:
            if not smart_list_item.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "smart list items", smart_list_item.ref_id, str(smart_list_item.name)
            ) as entity_reporter:
                try:
                    self._smart_list_notion_manager.remove_leaf(
                        smart_list_collection.ref_id,
                        smart_list.ref_id,
                        smart_list_item.ref_id,
                    )
                    entity_reporter.mark_remote_change()
                except NotionSmartListItemNotFoundError:
                    LOGGER.info(
                        "Skipping archival on Notion side because smart list was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_metrics(
        self,
        progress_reporter: ProgressReporter,
        metric_collection: MetricCollection,
        metrics: Iterable[Metric],
    ) -> None:
        for metric in metrics:
            if not metric.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "metric", metric.ref_id, str(metric.name)
            ) as entity_reporter:
                try:
                    self._metric_notion_manager.remove_branch(
                        metric_collection.ref_id, metric.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionMetricNotFoundError:
                    LOGGER.info(
                        "Skipping archival on Notion side because metric was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_metric_entries(
        self,
        progress_reporter: ProgressReporter,
        metric: Metric,
        metric_entries: Iterable[MetricEntry],
    ) -> None:
        for metric_entry in metric_entries:
            if not metric_entry.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "habit", metric_entry.ref_id, str(metric_entry.simple_name)
            ) as entity_reporter:
                try:
                    self._metric_notion_manager.remove_leaf(
                        metric.metric_collection_ref_id,
                        metric_entry.metric_ref_id,
                        metric_entry.ref_id,
                    )
                    entity_reporter.mark_remote_change()
                except NotionMetricEntryNotFoundError:
                    LOGGER.info(
                        "Skipping the removal on Notion side because recurring task was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_persons(
        self,
        progress_reporter: ProgressReporter,
        person_collection: PersonCollection,
        persons: Iterable[Person],
    ) -> None:
        for person in persons:
            if not person.archived:
                continue
            with progress_reporter.start_archiving_entity(
                "habit", person.ref_id, str(person.name)
            ) as entity_reporter:
                try:
                    self._person_notion_manager.remove_leaf(
                        person_collection.ref_id, person.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionPersonNotFoundError:
                    LOGGER.info(
                        "Skipping the removal on Notion side because person was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_slack_tasks(
        self,
        progress_reporter: ProgressReporter,
        slack_task_collection: SlackTaskCollection,
        slack_tasks: Iterable[SlackTask],
    ) -> None:
        for slack_task in slack_tasks:
            if not slack_task.archived:
                continue
            with progress_reporter.start_removing_entity(
                "slack task", slack_task.ref_id, str(slack_task.simple_name)
            ) as entity_reporter:
                try:
                    self._slack_task_notion_manager.remove_leaf(
                        slack_task_collection.ref_id, slack_task.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionSlackTaskNotFoundError:
                    LOGGER.info(
                        "Skipping the removal on Notion side because slack task was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)

    def _do_drop_all_archived_email_tasks(
        self,
        progress_reporter: ProgressReporter,
        email_task_collection: EmailTaskCollection,
        email_tasks: Iterable[EmailTask],
    ) -> None:
        for email_task in email_tasks:
            if not email_task.archived:
                continue
            with progress_reporter.start_removing_entity(
                "email task", email_task.ref_id, str(email_task.simple_name)
            ) as entity_reporter:
                try:
                    self._email_task_notion_manager.remove_leaf(
                        email_task_collection.ref_id, email_task.ref_id
                    )
                    entity_reporter.mark_remote_change()
                except NotionEmailTaskNotFoundError:
                    LOGGER.info(
                        "Skipping the removal on Notion side because email task was not found"
                    )
                    entity_reporter.mark_remote_change(MarkProgressStatus.FAILED)
