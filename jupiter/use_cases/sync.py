"""Synchronise between Notion and local."""
from dataclasses import dataclass
from typing import Final, Optional, Iterable, Dict, Tuple, cast, FrozenSet

from jupiter.domain import schedules
from jupiter.domain.big_plans.big_plan import BigPlan
from jupiter.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.domain.big_plans.infra.big_plan_notion_manager import BigPlanNotionManager
from jupiter.domain.big_plans.notion_big_plan import NotionBigPlan
from jupiter.domain.big_plans.notion_big_plan_collection import NotionBigPlanCollection
from jupiter.domain.big_plans.service.sync_service import BigPlanSyncService
from jupiter.domain.chores.chore import Chore
from jupiter.domain.chores.infra.chore_notion_manager import ChoreNotionManager
from jupiter.domain.chores.notion_chore import NotionChore
from jupiter.domain.chores.notion_chore_collection import NotionChoreCollection
from jupiter.domain.chores.service.sync_service import ChoreSyncService
from jupiter.domain.habits.habit import Habit
from jupiter.domain.habits.infra.habit_notion_manager import HabitNotionManager
from jupiter.domain.habits.notion_habit import NotionHabit
from jupiter.domain.habits.notion_habit_collection import NotionHabitCollection
from jupiter.domain.habits.service.sync_service import HabitSyncService
from jupiter.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.domain.inbox_tasks.inbox_task_source import InboxTaskSource
from jupiter.domain.inbox_tasks.infra.inbox_task_notion_manager import (
    InboxTaskNotionManager,
)
from jupiter.domain.inbox_tasks.notion_inbox_task import NotionInboxTask
from jupiter.domain.inbox_tasks.notion_inbox_task_collection import (
    NotionInboxTaskCollection,
)
from jupiter.domain.inbox_tasks.service.archive_service import InboxTaskArchiveService
from jupiter.domain.inbox_tasks.service.big_plan_ref_options_update_service import (
    InboxTaskBigPlanRefOptionsUpdateService,
)
from jupiter.domain.inbox_tasks.service.sync_service import InboxTaskSyncService
from jupiter.domain.metrics.infra.metric_notion_manager import MetricNotionManager
from jupiter.domain.metrics.metric import Metric
from jupiter.domain.metrics.metric_collection import MetricCollection
from jupiter.domain.metrics.metric_key import MetricKey
from jupiter.domain.metrics.notion_metric_collection import NotionMetricCollection
from jupiter.domain.metrics.service.sync_service import MetricSyncService
from jupiter.domain.persons.infra.person_notion_manager import PersonNotionManager
from jupiter.domain.persons.notion_person_collection import NotionPersonCollection
from jupiter.domain.persons.person import Person
from jupiter.domain.persons.person_birthday import PersonBirthday
from jupiter.domain.persons.person_collection import PersonCollection
from jupiter.domain.persons.service.sync_service import PersonSyncService
from jupiter.domain.projects.infra.project_notion_manager import ProjectNotionManager
from jupiter.domain.projects.notion_project_collection import NotionProjectCollection
from jupiter.domain.projects.project import Project
from jupiter.domain.projects.project_key import ProjectKey
from jupiter.domain.projects.service.project_label_update_service import (
    ProjectLabelUpdateService,
)
from jupiter.domain.projects.service.sync_service import ProjectSyncServiceNew
from jupiter.domain.push_integrations.email.email_task import EmailTask
from jupiter.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.domain.push_integrations.email.infra.email_task_notion_manager import (
    EmailTaskNotionManager,
)
from jupiter.domain.push_integrations.email.notion_email_task import NotionEmailTask
from jupiter.domain.push_integrations.email.notion_email_task_collection import (
    NotionEmailTaskCollection,
)
from jupiter.domain.push_integrations.email.service.sync_service import (
    EmailTaskSyncService,
)
from jupiter.domain.push_integrations.group.infra.push_integration_group_notion_manager import (
    PushIntegrationGroupNotionManager,
)
from jupiter.domain.push_integrations.group.notion_push_integration_group import (
    NotionPushIntegrationGroup,
)
from jupiter.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.domain.push_integrations.slack.infra.slack_task_notion_manager import (
    SlackTaskNotionManager,
)
from jupiter.domain.push_integrations.slack.notion_slack_task import NotionSlackTask
from jupiter.domain.push_integrations.slack.notion_slack_task_collection import (
    NotionSlackTaskCollection,
)
from jupiter.domain.push_integrations.slack.service.sync_service import (
    SlackTaskSyncService,
)
from jupiter.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.domain.recurring_task_due_at_day import RecurringTaskDueAtDay
from jupiter.domain.recurring_task_due_at_month import RecurringTaskDueAtMonth
from jupiter.domain.recurring_task_gen_params import RecurringTaskGenParams
from jupiter.domain.recurring_task_period import RecurringTaskPeriod
from jupiter.domain.smart_lists.infra.smart_list_notion_manager import (
    SmartListNotionManager,
)
from jupiter.domain.smart_lists.notion_smart_list_collection import (
    NotionSmartListCollection,
)
from jupiter.domain.smart_lists.service.sync_service import SmartListSyncServiceNew
from jupiter.domain.smart_lists.smart_list import SmartList
from jupiter.domain.smart_lists.smart_list_key import SmartListKey
from jupiter.domain.storage_engine import DomainStorageEngine
from jupiter.domain.sync_prefer import SyncPrefer
from jupiter.domain.sync_target import SyncTarget
from jupiter.domain.vacations.infra.vacation_notion_manager import VacationNotionManager
from jupiter.domain.vacations.notion_vacation_collection import NotionVacationCollection
from jupiter.domain.vacations.service.sync_service import VacationSyncService
from jupiter.domain.workspaces.infra.workspace_notion_manager import (
    WorkspaceNotionManager,
)
from jupiter.domain.workspaces.service.sync_service import WorkspaceSyncService
from jupiter.domain.workspaces.workspace import Workspace
from jupiter.framework.base.entity_id import EntityId
from jupiter.framework.base.timestamp import Timestamp
from jupiter.framework.event import EventSource
from jupiter.framework.use_case import (
    UseCaseArgsBase,
    MutationUseCaseInvocationRecorder,
    ProgressReporter,
)
from jupiter.remote.notion.common import format_name_for_option
from jupiter.use_cases.infra.use_cases import (
    AppUseCaseContext,
    AppMutationUseCase,
)
from jupiter.utils.global_properties import GlobalProperties
from jupiter.utils.time_provider import TimeProvider


class SyncUseCase(AppMutationUseCase["SyncUseCase.Args", None]):
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
        filter_slack_task_ref_ids: Optional[Iterable[EntityId]]
        filter_email_task_ref_ids: Optional[Iterable[EntityId]]
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
    _push_integration_group_notion_manager: Final[PushIntegrationGroupNotionManager]
    _slack_task_notion_manager: Final[SlackTaskNotionManager]
    _email_task_notion_manager: Final[EmailTaskNotionManager]

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
        person_notion_manager: PersonNotionManager,
        push_integration_group_notion_manager: PushIntegrationGroupNotionManager,
        slack_task_notion_manager: SlackTaskNotionManager,
        email_task_notion_manager: EmailTaskNotionManager,
    ) -> None:
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
        self._push_integration_group_notion_manager = (
            push_integration_group_notion_manager
        )
        self._slack_task_notion_manager = slack_task_notion_manager
        self._email_task_notion_manager = email_task_notion_manager

    def _execute(
        self,
        progress_reporter: ProgressReporter,
        context: AppUseCaseContext,
        args: Args,
    ) -> None:
        """Execute the command's action."""
        filter_habit_ref_ids_set = (
            frozenset(args.filter_habit_ref_ids) if args.filter_habit_ref_ids else None
        )
        filter_chore_ref_ids_set = (
            frozenset(args.filter_chore_ref_ids) if args.filter_chore_ref_ids else None
        )
        sync_targets = frozenset(args.sync_targets)

        workspace = context.workspace
        notion_workspace = self._workspace_notion_manager.load_workspace(
            workspace.ref_id
        )

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

            all_smart_lists = uow.smart_list_repository.find_all(
                parent_ref_id=smart_list_collection.ref_id, allow_archived=True
            )
            all_metrics = uow.metric_repository.find_all(
                parent_ref_id=metric_collection.ref_id, allow_archived=True
            )

        if SyncTarget.STRUCTURE in args.sync_targets:
            with progress_reporter.section("Recreating Notion structure"):
                notion_vacation_collection = NotionVacationCollection.new_notion_entity(
                    vacation_collection
                )
                with progress_reporter.start_work_related_to_entity(
                    "vacation structure", vacation_collection.ref_id, "Vacations"
                ) as entity_reporter:
                    self._vacation_notion_manager.upsert_trunk(
                        notion_workspace, notion_vacation_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_project_collection = NotionProjectCollection.new_notion_entity(
                    project_collection
                )
                with progress_reporter.start_work_related_to_entity(
                    "projects structure", project_collection.ref_id, "Projects"
                ) as entity_reporter:
                    self._project_notion_manager.upsert_trunk(
                        notion_workspace, notion_project_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_inbox_task_collection = (
                    NotionInboxTaskCollection.new_notion_entity(inbox_task_collection)
                )
                with progress_reporter.start_work_related_to_entity(
                    "inbox tasks structure", inbox_task_collection.ref_id, "Inbox Tasks"
                ) as entity_reporter:
                    self._inbox_task_notion_manager.upsert_trunk(
                        notion_workspace, notion_inbox_task_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_habit_collection = NotionHabitCollection.new_notion_entity(
                    habit_collection
                )
                with progress_reporter.start_work_related_to_entity(
                    "habits structure", habit_collection.ref_id, "Habits"
                ) as entity_reporter:
                    self._habit_notion_manager.upsert_trunk(
                        notion_workspace, notion_habit_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_chore_collection = NotionChoreCollection.new_notion_entity(
                    chore_collection
                )
                with progress_reporter.start_work_related_to_entity(
                    "chores structure", chore_collection.ref_id, "Chores"
                ) as entity_reporter:
                    self._chore_notion_manager.upsert_trunk(
                        notion_workspace, notion_chore_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_big_plan_collection = NotionBigPlanCollection.new_notion_entity(
                    big_plan_collection
                )
                with progress_reporter.start_work_related_to_entity(
                    "big plans structure", big_plan_collection.ref_id, "Big Plans"
                ) as entity_reporter:
                    self._big_plan_notion_manager.upsert_trunk(
                        notion_workspace, notion_big_plan_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_smart_list_collection = (
                    NotionSmartListCollection.new_notion_entity(smart_list_collection)
                )
                with progress_reporter.start_work_related_to_entity(
                    "smart lists structure", smart_list_collection.ref_id, "Smart Lists"
                ) as entity_reporter:
                    self._smart_list_notion_manager.upsert_trunk(
                        notion_workspace, notion_smart_list_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_metric_collection = NotionMetricCollection.new_notion_entity(
                    metric_collection
                )
                with progress_reporter.start_work_related_to_entity(
                    "metrics structure", metric_collection.ref_id, "Metrics"
                ) as entity_reporter:
                    self._metric_notion_manager.upsert_trunk(
                        notion_workspace, notion_metric_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_person_collection = NotionPersonCollection.new_notion_entity(
                    person_collection
                )
                with progress_reporter.start_work_related_to_entity(
                    "persons structure", person_collection.ref_id, "Persons"
                ) as entity_reporter:
                    self._person_notion_manager.upsert_trunk(
                        notion_workspace, notion_person_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_push_integration_group = (
                    NotionPushIntegrationGroup.new_notion_entity(push_integration_group)
                )
                with progress_reporter.start_work_related_to_entity(
                    "push integrations structure",
                    push_integration_group.ref_id,
                    "Push Integrations",
                ) as entity_reporter:
                    notion_push_integration_group = self._push_integration_group_notion_manager.upsert_push_integration_group(
                        notion_workspace, notion_push_integration_group
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_slack_task_collection = (
                    NotionSlackTaskCollection.new_notion_entity(slack_task_collection)
                )
                with progress_reporter.start_work_related_to_entity(
                    "slack tasks structure", slack_task_collection.ref_id, "Slack Tasks"
                ) as entity_reporter:
                    self._slack_task_notion_manager.upsert_trunk(
                        notion_push_integration_group, notion_slack_task_collection
                    )
                    entity_reporter.mark_other_progress("structure")

                notion_email_task_collection = (
                    NotionEmailTaskCollection.new_notion_entity(email_task_collection)
                )
                with progress_reporter.start_work_related_to_entity(
                    "email tasks structure", email_task_collection.ref_id, "Email Tasks"
                ) as entity_reporter:
                    self._email_task_notion_manager.upsert_trunk(
                        notion_push_integration_group, notion_email_task_collection
                    )
                    entity_reporter.mark_other_progress("structure")

        if SyncTarget.WORKSPACE in args.sync_targets:
            with progress_reporter.section("Syncing the workspace"):
                workspace = self._sync_workspace(progress_reporter, args)

        if SyncTarget.VACATIONS in sync_targets:
            with progress_reporter.section("Syncing the vacations"):
                self._sync_vacations(progress_reporter, args, workspace)

        if SyncTarget.PROJECTS in sync_targets:
            with progress_reporter.section("Syncing the projects"):
                self._sync_projects(progress_reporter, args, workspace)

        inbox_task_archive_service = InboxTaskArchiveService(
            source=EventSource.NOTION,
            time_provider=self._time_provider,
            storage_engine=self._storage_engine,
            inbox_task_notion_manager=self._inbox_task_notion_manager,
        )

        with self._storage_engine.get_unit_of_work() as uow:
            all_projects = uow.project_repository.find_all(
                parent_ref_id=project_collection.ref_id
            )

        projects_by_ref_id = {p.ref_id: p for p in all_projects}
        filter_project_ref_ids = None
        if args.filter_project_keys:
            filter_project_ref_ids = [
                p.ref_id for p in all_projects if p.key in args.filter_project_keys
            ]

        if SyncTarget.HABITS in sync_targets:
            with progress_reporter.section("Syncing the habits"):
                all_habits = self._sync_habits(
                    progress_reporter, all_projects, args, workspace
                )
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_habits = uow.habit_repository.find_all_with_filters(
                    parent_ref_id=habit_collection.ref_id,
                    allow_archived=True,
                    filter_ref_ids=args.filter_habit_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                )
        habits_by_ref_id = {rt.ref_id: rt for rt in all_habits}

        if SyncTarget.CHORES in sync_targets:
            with progress_reporter.section("Syncing the chores"):
                all_chores = self._sync_chores(
                    progress_reporter, all_projects, args, workspace
                )
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_chores = uow.chore_repository.find_all_with_filters(
                    parent_ref_id=chore_collection.ref_id,
                    allow_archived=True,
                    filter_ref_ids=args.filter_chore_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                )
        chores_by_ref_id = {rt.ref_id: rt for rt in all_chores}

        if SyncTarget.BIG_PLANS in sync_targets:
            with progress_reporter.section("Syncing the big plans"):
                all_big_plans = self._sync_big_plans(
                    progress_reporter,
                    all_projects,
                    args,
                    big_plan_collection,
                    workspace,
                )
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_big_plans = uow.big_plan_repository.find_all_with_filters(
                    parent_ref_id=big_plan_collection.ref_id,
                    allow_archived=True,
                    filter_ref_ids=args.filter_big_plan_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                )
        big_plans_by_ref_id = {bp.ref_id: bp for bp in all_big_plans}

        if SyncTarget.INBOX_TASKS in args.sync_targets:
            with progress_reporter.section("Syncing the inbox tasks"):
                all_inbox_tasks = self._sync_inbox_tasks(
                    progress_reporter, all_big_plans, all_projects, args, workspace
                )
        else:
            with self._storage_engine.get_unit_of_work() as uow:
                all_inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_ref_ids=args.filter_inbox_task_ref_ids,
                    filter_project_ref_ids=filter_project_ref_ids,
                )

        if SyncTarget.HABITS in args.sync_targets:
            with progress_reporter.section(
                "Syncing the inbox tasks associated with habits"
            ):
                self._sync_habit_inbox_tasks(
                    progress_reporter,
                    all_inbox_tasks,
                    filter_habit_ref_ids_set,
                    habits_by_ref_id,
                    projects_by_ref_id,
                )

        if SyncTarget.CHORES in args.sync_targets:
            with progress_reporter.section(
                "Syncing the inbox tasks associated with chores"
            ):
                self._sync_chores_inbox_tasks(
                    progress_reporter,
                    all_inbox_tasks,
                    chores_by_ref_id,
                    filter_chore_ref_ids_set,
                    projects_by_ref_id,
                )

        if SyncTarget.HABITS in sync_targets:
            with progress_reporter.section(
                "Archiving the inbox tasks for archived habits"
            ):
                self._archive_habits_inbox_tasks(
                    progress_reporter,
                    all_inbox_tasks,
                    args,
                    habits_by_ref_id,
                    inbox_task_archive_service,
                )

        if SyncTarget.CHORES in sync_targets:
            with progress_reporter.section(
                "Archiving the inbox tasks for archived chores"
            ):
                self._archive_chores_inbox_tasks(
                    progress_reporter,
                    all_inbox_tasks,
                    args,
                    chores_by_ref_id,
                    inbox_task_archive_service,
                )

        if SyncTarget.BIG_PLANS in sync_targets:
            with progress_reporter.section(
                "Archiving the inbox tasks for archived big plans"
            ):
                self._archive_big_plan_inbox_tasks(
                    progress_reporter,
                    all_inbox_tasks,
                    args,
                    big_plans_by_ref_id,
                    inbox_task_archive_service,
                )

        if SyncTarget.SMART_LISTS in sync_targets:
            with progress_reporter.section("Syncing the smart lists"):
                self._sync_smart_lists(
                    progress_reporter, all_smart_lists, args, workspace
                )

        if SyncTarget.METRICS in sync_targets:
            with progress_reporter.section("Syncing the metrics"):
                all_metrics_by_ref_id = {m.ref_id: m for m in all_metrics}
                for metric in all_metrics:
                    if (
                        args.filter_metric_keys is not None
                        and metric.key not in args.filter_metric_keys
                    ):
                        continue

                    metric_sync_service = MetricSyncService(
                        self._storage_engine, self._metric_notion_manager
                    )
                    metric_sync_service.sync(
                        progress_reporter=progress_reporter,
                        right_now=self._time_provider.get_current_time(),
                        parent_ref_id=workspace.ref_id,
                        branch=metric,
                        direct_info=None,
                        inverse_info=None,
                        drop_all_notion_side=args.drop_all_notion,
                        sync_even_if_not_modified=args.sync_even_if_not_modified,
                        filter_ref_ids=args.filter_metric_entry_ref_ids,
                        sync_prefer=args.sync_prefer,
                    )

            with progress_reporter.section(
                "Syncing the inbox tasks associated with metrics"
            ):
                self._sync_metric_inbox_tasks(
                    progress_reporter,
                    all_metrics_by_ref_id,
                    args,
                    inbox_task_collection,
                    metric_collection,
                    projects_by_ref_id,
                )

        if SyncTarget.PERSONS in sync_targets:
            with progress_reporter.section("Syncing the persons"):
                all_persons_by_ref_id, project = self._sync_persons(
                    progress_reporter,
                    args,
                    person_collection,
                    projects_by_ref_id,
                    workspace,
                )
                self._sync_person_catch_up_inbox_tasks(
                    progress_reporter,
                    all_persons_by_ref_id,
                    args,
                    inbox_task_archive_service,
                    inbox_task_collection,
                    project,
                )
                self._sync_person_birthday_inbox_tasks(
                    progress_reporter,
                    all_persons_by_ref_id,
                    args,
                    inbox_task_archive_service,
                    inbox_task_collection,
                    project,
                )

        if SyncTarget.SLACK_TASKS in sync_targets:
            with progress_reporter.section("Syncing the Slack tasks"):
                all_slack_tasks_by_ref_id, project = self._sync_slack_tasks(
                    progress_reporter,
                    args,
                    projects_by_ref_id,
                    slack_task_collection,
                    push_integration_group,
                )
                self._sync_slack_tasks_inbox_tasks(
                    progress_reporter,
                    all_slack_tasks_by_ref_id,
                    args,
                    inbox_task_archive_service,
                    inbox_task_collection,
                    project,
                )

        if SyncTarget.EMAIL_TASKS in sync_targets:
            with progress_reporter.section("Syncing the email tasks"):
                all_email_tasks_by_ref_id, project = self._sync_email_tasks(
                    progress_reporter,
                    args,
                    projects_by_ref_id,
                    email_task_collection,
                    push_integration_group,
                )
                self._sync_email_tasks_inbox_tasks(
                    progress_reporter,
                    all_email_tasks_by_ref_id,
                    args,
                    inbox_task_archive_service,
                    inbox_task_collection,
                    project,
                )

    def _sync_slack_tasks_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_slack_tasks_by_ref_id: Dict[EntityId, SlackTask],
        args: Args,
        inbox_task_archive_service: InboxTaskArchiveService,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
    ) -> None:
        with self._storage_engine.get_unit_of_work() as uow:
            all_slack_inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.SLACK_TASK],
                filter_slack_task_ref_ids=all_slack_tasks_by_ref_id.keys(),
            )
        for inbox_task in all_slack_inbox_tasks:
            if inbox_task.archived:
                continue
            slack_task = all_slack_tasks_by_ref_id[
                cast(EntityId, inbox_task.slack_task_ref_id)
            ]
            if (
                args.filter_slack_task_ref_ids is not None
                and slack_task.ref_id not in args.filter_slack_task_ref_ids
            ):
                continue
            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                if not slack_task.last_modified_time.is_within_ten_minutes(
                    self._time_provider.get_current_time()
                ):
                    entity_reporter.mark_not_needed()
                    continue
                if slack_task.archived:
                    if not inbox_task.archived:
                        inbox_task_archive_service.do_it(progress_reporter, inbox_task)
                else:
                    inbox_task = inbox_task.update_link_to_slack_task(
                        project_ref_id=project.ref_id,
                        user=slack_task.user,
                        channel=slack_task.channel,
                        message=slack_task.message,
                        generation_extra_info=slack_task.generation_extra_info,
                        source=EventSource.SLACK,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(inbox_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    notion_inbox_task = notion_inbox_task.join_with_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.save_leaf(
                        inbox_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _sync_slack_tasks(
        self,
        progress_reporter: ProgressReporter,
        args: Args,
        projects_by_ref_id: Dict[EntityId, Project],
        slack_task_collection: SlackTaskCollection,
        push_integration_group: PushIntegrationGroup,
    ) -> Tuple[Dict[EntityId, SlackTask], Project]:
        project = projects_by_ref_id[slack_task_collection.generation_project_ref_id]
        slack_task_sync_service = SlackTaskSyncService(
            self._storage_engine, self._slack_task_notion_manager
        )
        all_slack_tasks = slack_task_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=push_integration_group.ref_id,
            direct_info=None,
            inverse_info=NotionSlackTask.InverseInfo(
                timezone=self._global_properties.timezone
            ),
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_slack_task_ref_ids,
            sync_prefer=args.sync_prefer,
        ).all
        all_slack_tasks_by_ref_id = {st.ref_id: st for st in all_slack_tasks}
        return all_slack_tasks_by_ref_id, project

    def _sync_email_tasks_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_email_tasks_by_ref_id: Dict[EntityId, EmailTask],
        args: Args,
        inbox_task_archive_service: InboxTaskArchiveService,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
    ) -> None:
        with self._storage_engine.get_unit_of_work() as uow:
            all_email_inbox_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.EMAIL_TASK],
                filter_email_task_ref_ids=all_email_tasks_by_ref_id.keys(),
            )
        for inbox_task in all_email_inbox_tasks:
            if inbox_task.archived:
                continue
            email_task = all_email_tasks_by_ref_id[
                cast(EntityId, inbox_task.email_task_ref_id)
            ]
            if (
                args.filter_email_task_ref_ids is not None
                and email_task.ref_id not in args.filter_email_task_ref_ids
            ):
                continue
            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                if not email_task.last_modified_time.is_within_ten_minutes(
                    self._time_provider.get_current_time()
                ):
                    entity_reporter.mark_not_needed()
                    continue
                if email_task.archived:
                    if not inbox_task.archived:
                        inbox_task_archive_service.do_it(progress_reporter, inbox_task)
                else:
                    inbox_task = inbox_task.update_link_to_email_task(
                        project_ref_id=project.ref_id,
                        from_address=email_task.from_address,
                        from_name=email_task.from_name,
                        to_address=email_task.to_address,
                        subject=email_task.subject,
                        body=email_task.body,
                        generation_extra_info=email_task.generation_extra_info,
                        source=EventSource.EMAIL,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(inbox_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    notion_inbox_task = notion_inbox_task.join_with_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.save_leaf(
                        inbox_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _sync_email_tasks(
        self,
        progress_reporter: ProgressReporter,
        args: Args,
        projects_by_ref_id: Dict[EntityId, Project],
        email_task_collection: EmailTaskCollection,
        push_integration_group: PushIntegrationGroup,
    ) -> Tuple[Dict[EntityId, EmailTask], Project]:
        project = projects_by_ref_id[email_task_collection.generation_project_ref_id]
        email_task_sync_service = EmailTaskSyncService(
            self._storage_engine, self._email_task_notion_manager
        )
        all_email_tasks = email_task_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=push_integration_group.ref_id,
            direct_info=None,
            inverse_info=NotionEmailTask.InverseInfo(
                timezone=self._global_properties.timezone
            ),
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_email_task_ref_ids,
            sync_prefer=args.sync_prefer,
        ).all
        all_email_tasks_by_ref_id = {st.ref_id: st for st in all_email_tasks}
        return all_email_tasks_by_ref_id, project

    def _sync_person_catch_up_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_persons_by_ref_id: Dict[EntityId, Person],
        args: Args,
        inbox_task_archive_service: InboxTaskArchiveService,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
    ) -> None:
        with self._storage_engine.get_unit_of_work() as uow:
            all_person_catch_up_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.PERSON_CATCH_UP],
                filter_person_ref_ids=all_persons_by_ref_id.keys(),
            )
        for inbox_task in all_person_catch_up_tasks:
            if inbox_task.archived:
                continue
            person = all_persons_by_ref_id[cast(EntityId, inbox_task.person_ref_id)]
            if (
                args.filter_person_ref_ids is not None
                and person.ref_id not in args.filter_person_ref_ids
            ):
                continue

            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                if not person.last_modified_time.is_within_ten_minutes(
                    self._time_provider.get_current_time()
                ):
                    entity_reporter.mark_not_needed()
                    continue

                if person.archived:
                    if not inbox_task.archived:
                        inbox_task_archive_service.do_it(progress_reporter, inbox_task)
                elif person.catch_up_params is None:
                    if not inbox_task.archived:
                        inbox_task_archive_service.do_it(progress_reporter, inbox_task)
                else:
                    catch_up_params = cast(
                        RecurringTaskGenParams, person.catch_up_params
                    )
                    schedule = schedules.get_schedule(
                        catch_up_params.period,
                        person.name,
                        cast(Timestamp, inbox_task.recurring_gen_right_now),
                        self._global_properties.timezone,
                        None,
                        catch_up_params.actionable_from_day,
                        catch_up_params.actionable_from_month,
                        catch_up_params.due_at_time,
                        catch_up_params.due_at_day,
                        catch_up_params.due_at_month,
                    )
                    inbox_task = inbox_task.update_link_to_person_catch_up(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        eisen=catch_up_params.eisen,
                        difficulty=catch_up_params.difficulty,
                        actionable_date=schedule.actionable_date,
                        due_time=schedule.due_time,
                        source=EventSource.NOTION,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(inbox_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    notion_inbox_task = notion_inbox_task.join_with_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.save_leaf(
                        inbox_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _sync_person_birthday_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_persons_by_ref_id: Dict[EntityId, Person],
        args: Args,
        inbox_task_archive_service: InboxTaskArchiveService,
        inbox_task_collection: InboxTaskCollection,
        project: Project,
    ) -> None:
        with self._storage_engine.get_unit_of_work() as uow:
            all_person_birthday_tasks = uow.inbox_task_repository.find_all_with_filters(
                parent_ref_id=inbox_task_collection.ref_id,
                allow_archived=True,
                filter_sources=[InboxTaskSource.PERSON_BIRTHDAY],
                filter_person_ref_ids=all_persons_by_ref_id.keys(),
            )
        for inbox_task in all_person_birthday_tasks:
            if inbox_task.archived:
                continue
            person = all_persons_by_ref_id[cast(EntityId, inbox_task.person_ref_id)]
            if (
                args.filter_person_ref_ids is not None
                and person.ref_id not in args.filter_person_ref_ids
            ):
                continue

            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                if not person.last_modified_time.is_within_ten_minutes(
                    self._time_provider.get_current_time()
                ):
                    entity_reporter.mark_not_needed()
                    continue

                if person.archived:
                    if not inbox_task.archived:
                        inbox_task_archive_service.do_it(progress_reporter, inbox_task)
                else:
                    birthday = cast(PersonBirthday, person.birthday)
                    schedule = schedules.get_schedule(
                        RecurringTaskPeriod.YEARLY,
                        person.name,
                        cast(Timestamp, inbox_task.recurring_gen_right_now),
                        self._global_properties.timezone,
                        None,
                        None,
                        None,
                        None,
                        RecurringTaskDueAtDay.from_raw(
                            RecurringTaskPeriod.MONTHLY, birthday.day
                        ),
                        RecurringTaskDueAtMonth.from_raw(
                            RecurringTaskPeriod.YEARLY, birthday.month
                        ),
                    )
                    inbox_task = inbox_task.update_link_to_person_birthday(
                        project_ref_id=project.ref_id,
                        name=schedule.full_name,
                        recurring_timeline=schedule.timeline,
                        preparation_days_cnt=person.preparation_days_cnt_for_birthday,
                        due_time=schedule.due_time,
                        source=EventSource.NOTION,
                        modification_time=self._time_provider.get_current_time(),
                    )
                    entity_reporter.mark_known_name(str(inbox_task.name))

                    with self._storage_engine.get_unit_of_work() as uow:
                        uow.inbox_task_repository.save(inbox_task)
                        entity_reporter.mark_local_change()

                    direct_info = NotionInboxTask.DirectInfo(
                        all_projects_map={project.ref_id: project}, all_big_plans_map={}
                    )
                    notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                        inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                    )
                    notion_inbox_task = notion_inbox_task.join_with_entity(
                        inbox_task, direct_info
                    )
                    self._inbox_task_notion_manager.save_leaf(
                        inbox_task.inbox_task_collection_ref_id,
                        notion_inbox_task,
                    )
                    entity_reporter.mark_remote_change()

    def _sync_persons(
        self,
        progress_reporter: ProgressReporter,
        args: Args,
        person_collection: PersonCollection,
        projects_by_ref_id: Dict[EntityId, Project],
        workspace: Workspace,
    ) -> Tuple[Dict[EntityId, Person], Project]:
        project = projects_by_ref_id[person_collection.catch_up_project_ref_id]
        person_sync_service = PersonSyncService(
            self._storage_engine, self._person_notion_manager
        )
        persons = person_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=workspace.ref_id,
            direct_info=None,
            inverse_info=None,
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_person_ref_ids,
            sync_prefer=args.sync_prefer,
        ).all
        all_persons_by_ref_id = {p.ref_id: p for p in persons}
        return all_persons_by_ref_id, project

    def _sync_metric_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_metrics_by_ref_id: Dict[EntityId, Metric],
        args: Args,
        inbox_task_collection: InboxTaskCollection,
        metric_collection: MetricCollection,
        projects_by_ref_id: Dict[EntityId, Project],
    ) -> None:
        with self._storage_engine.get_unit_of_work() as uow:
            all_metric_collection_tasks = (
                uow.inbox_task_repository.find_all_with_filters(
                    parent_ref_id=inbox_task_collection.ref_id,
                    allow_archived=True,
                    filter_sources=[InboxTaskSource.METRIC],
                    filter_metric_ref_ids=all_metrics_by_ref_id.keys(),
                )
            )
        for inbox_task in all_metric_collection_tasks:
            if inbox_task.archived:
                continue
            metric = all_metrics_by_ref_id[cast(EntityId, inbox_task.metric_ref_id)]
            project = projects_by_ref_id[metric_collection.collection_project_ref_id]

            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                if (
                    args.filter_metric_keys is not None
                    and metric.key not in args.filter_metric_keys
                ):
                    entity_reporter.mark_not_needed()
                    continue
                if not metric.last_modified_time.is_within_ten_minutes(
                    self._time_provider.get_current_time()
                ):
                    entity_reporter.mark_not_needed()
                    continue
                collection_params = cast(
                    RecurringTaskGenParams, metric.collection_params
                )
                schedule = schedules.get_schedule(
                    cast(RecurringTaskGenParams, metric.collection_params).period,
                    metric.name,
                    cast(Timestamp, inbox_task.recurring_gen_right_now),
                    self._global_properties.timezone,
                    None,
                    collection_params.actionable_from_day,
                    collection_params.actionable_from_month,
                    collection_params.due_at_time,
                    collection_params.due_at_day,
                    collection_params.due_at_month,
                )
                inbox_task = inbox_task.update_link_to_metric(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    recurring_timeline=schedule.timeline,
                    eisen=collection_params.eisen,
                    difficulty=collection_params.difficulty,
                    actionable_date=schedule.actionable_date,
                    due_time=schedule.due_time,
                    source=EventSource.NOTION,
                    modification_time=self._time_provider.get_current_time(),
                )
                entity_reporter.mark_known_name(str(inbox_task.name))

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)
                    entity_reporter.mark_local_change()

                direct_info = NotionInboxTask.DirectInfo(
                    all_projects_map={project.ref_id: project}, all_big_plans_map={}
                )
                notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
                notion_inbox_task = notion_inbox_task.join_with_entity(
                    inbox_task, direct_info
                )
                self._inbox_task_notion_manager.save_leaf(
                    inbox_task.inbox_task_collection_ref_id,
                    notion_inbox_task,
                )
                entity_reporter.mark_remote_change()

    def _sync_smart_lists(
        self,
        progress_reporter: ProgressReporter,
        all_smart_lists: Iterable[SmartList],
        args: Args,
        workspace: Workspace,
    ) -> None:
        for smart_list in all_smart_lists:
            if (
                args.filter_smart_list_keys is not None
                and smart_list.key not in args.filter_smart_list_keys
            ):
                continue

            smart_list_sync_service = SmartListSyncServiceNew(
                self._storage_engine, self._smart_list_notion_manager
            )
            smart_list_sync_service.sync(
                progress_reporter=progress_reporter,
                right_now=self._time_provider.get_current_time(),
                parent_ref_id=workspace.ref_id,
                branch=smart_list,
                drop_all_notion_side=args.drop_all_notion,
                sync_even_if_not_modified=args.sync_even_if_not_modified,
                filter_ref_ids=args.filter_smart_list_item_ref_ids,
                sync_prefer=args.sync_prefer,
            )

    @staticmethod
    def _archive_habits_inbox_tasks(
        progress_reporter: ProgressReporter,
        all_inbox_tasks: Iterable[InboxTask],
        args: Args,
        habits_by_ref_id: Dict[EntityId, Habit],
        inbox_task_archive_service: InboxTaskArchiveService,
    ) -> None:
        for inbox_task in all_inbox_tasks:
            if inbox_task.habit_ref_id is None:
                continue
            if (
                args.filter_habit_ref_ids is not None
                and inbox_task.habit_ref_id not in args.filter_habit_ref_ids
            ):
                continue
            habit = habits_by_ref_id[inbox_task.habit_ref_id]
            if not (habit.archived and not inbox_task.archived):
                continue
            inbox_task_archive_service.do_it(progress_reporter, inbox_task)

    @staticmethod
    def _archive_chores_inbox_tasks(
        progress_reporter: ProgressReporter,
        all_inbox_tasks: Iterable[InboxTask],
        args: Args,
        chores_by_ref_id: Dict[EntityId, Chore],
        inbox_task_archive_service: InboxTaskArchiveService,
    ) -> None:
        for inbox_task in all_inbox_tasks:
            if inbox_task.chore_ref_id is None:
                continue
            if (
                args.filter_chore_ref_ids is not None
                and inbox_task.chore_ref_id not in args.filter_chore_ref_ids
            ):
                continue
            chore = chores_by_ref_id[inbox_task.chore_ref_id]
            if not (chore.archived and not inbox_task.archived):
                continue
            inbox_task_archive_service.do_it(progress_reporter, inbox_task)

    @staticmethod
    def _archive_big_plan_inbox_tasks(
        progress_reporter: ProgressReporter,
        all_inbox_tasks: Iterable[InboxTask],
        args: Args,
        big_plans_by_ref_id: Dict[EntityId, BigPlan],
        inbox_task_archive_service: InboxTaskArchiveService,
    ) -> None:
        for inbox_task in all_inbox_tasks:
            if inbox_task.big_plan_ref_id is None:
                continue
            if (
                args.filter_big_plan_ref_ids is not None
                and inbox_task.big_plan_ref_id not in args.filter_big_plan_ref_ids
            ):
                continue
            big_blan = big_plans_by_ref_id[inbox_task.big_plan_ref_id]
            if not (big_blan.archived and not inbox_task.archived):
                continue
            inbox_task_archive_service.do_it(progress_reporter, inbox_task)

    def _sync_habit_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_inbox_tasks: Iterable[InboxTask],
        filter_habit_ref_ids_set: Optional[FrozenSet[EntityId]],
        habits_by_ref_id: Dict[EntityId, Habit],
        projects_by_ref_id: Dict[EntityId, Project],
    ) -> None:
        for inbox_task in all_inbox_tasks:
            if inbox_task.archived:
                continue
            if inbox_task.status.is_completed:
                continue
            if inbox_task.habit_ref_id is None:
                continue
            if (
                filter_habit_ref_ids_set is not None
                and inbox_task.habit_ref_id not in filter_habit_ref_ids_set
            ):
                continue
            habit = habits_by_ref_id[inbox_task.habit_ref_id]
            project = projects_by_ref_id[habit.project_ref_id]

            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                if not habit.last_modified_time.is_within_ten_minutes(
                    self._time_provider.get_current_time()
                ):
                    entity_reporter.mark_not_needed()
                    continue

                schedule = schedules.get_schedule(
                    habit.gen_params.period,
                    habit.name,
                    cast(
                        Timestamp,
                        inbox_task.recurring_gen_right_now or inbox_task.created_time,
                    ),
                    self._global_properties.timezone,
                    habit.skip_rule,
                    habit.gen_params.actionable_from_day,
                    habit.gen_params.actionable_from_month,
                    habit.gen_params.due_at_time,
                    habit.gen_params.due_at_day,
                    habit.gen_params.due_at_month,
                )
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
                    modification_time=self._time_provider.get_current_time(),
                )
                entity_reporter.mark_known_name(str(inbox_task.name))

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)
                    entity_reporter.mark_local_change()

                direct_info = NotionInboxTask.DirectInfo(
                    all_projects_map={project.ref_id: project}, all_big_plans_map={}
                )
                notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
                notion_inbox_task = notion_inbox_task.join_with_entity(
                    inbox_task, direct_info
                )
                self._inbox_task_notion_manager.save_leaf(
                    inbox_task.inbox_task_collection_ref_id,
                    notion_inbox_task,
                )
                entity_reporter.mark_remote_change()

    def _sync_chores_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_inbox_tasks: Iterable[InboxTask],
        chores_by_ref_id: Dict[EntityId, Chore],
        filter_chore_ref_ids_set: Optional[FrozenSet[EntityId]],
        projects_by_ref_id: Dict[EntityId, Project],
    ) -> None:
        for inbox_task in all_inbox_tasks:
            if inbox_task.archived:
                continue
            if inbox_task.status.is_completed:
                continue
            if inbox_task.chore_ref_id is None:
                continue
            if (
                filter_chore_ref_ids_set is not None
                and inbox_task.chore_ref_id not in filter_chore_ref_ids_set
            ):
                continue
            chore = chores_by_ref_id[inbox_task.chore_ref_id]
            project = projects_by_ref_id[chore.project_ref_id]

            with progress_reporter.start_updating_entity(
                "inbox task", inbox_task.ref_id, str(inbox_task.name)
            ) as entity_reporter:
                if not chore.last_modified_time.is_within_ten_minutes(
                    self._time_provider.get_current_time()
                ):
                    entity_reporter.mark_not_needed()
                    continue

                schedule = schedules.get_schedule(
                    chore.gen_params.period,
                    chore.name,
                    cast(
                        Timestamp,
                        inbox_task.recurring_gen_right_now or inbox_task.created_time,
                    ),
                    self._global_properties.timezone,
                    chore.skip_rule,
                    chore.gen_params.actionable_from_day,
                    chore.gen_params.actionable_from_month,
                    chore.gen_params.due_at_time,
                    chore.gen_params.due_at_day,
                    chore.gen_params.due_at_month,
                )
                inbox_task = inbox_task.update_link_to_chore(
                    project_ref_id=project.ref_id,
                    name=schedule.full_name,
                    timeline=schedule.timeline,
                    actionable_date=schedule.actionable_date,
                    due_date=schedule.due_time,
                    eisen=chore.gen_params.eisen,
                    difficulty=chore.gen_params.difficulty,
                    source=EventSource.NOTION,
                    modification_time=self._time_provider.get_current_time(),
                )
                entity_reporter.mark_known_name(str(inbox_task.name))

                with self._storage_engine.get_unit_of_work() as uow:
                    uow.inbox_task_repository.save(inbox_task)
                    entity_reporter.mark_local_change()

                direct_info = NotionInboxTask.DirectInfo(
                    all_projects_map={project.ref_id: project}, all_big_plans_map={}
                )
                notion_inbox_task = self._inbox_task_notion_manager.load_leaf(
                    inbox_task.inbox_task_collection_ref_id, inbox_task.ref_id
                )
                notion_inbox_task = notion_inbox_task.join_with_entity(
                    inbox_task, direct_info
                )
                self._inbox_task_notion_manager.save_leaf(
                    inbox_task.inbox_task_collection_ref_id,
                    notion_inbox_task,
                )
                entity_reporter.mark_remote_change()

    def _sync_inbox_tasks(
        self,
        progress_reporter: ProgressReporter,
        all_big_plans: Iterable[BigPlan],
        all_projects: Iterable[Project],
        args: Args,
        workspace: Workspace,
    ) -> Iterable[InboxTask]:
        inbox_task_sync_service = InboxTaskSyncService(
            self._storage_engine, self._inbox_task_notion_manager
        )
        all_big_plans_by_name = {
            format_name_for_option(bp.name): bp for bp in all_big_plans
        }
        all_big_plans_map = {bp.ref_id: bp for bp in all_big_plans}
        all_projects_by_name = {format_name_for_option(p.name): p for p in all_projects}
        all_projects_map = {p.ref_id: p for p in all_projects}
        default_project = all_projects_map[workspace.default_project_ref_id]
        all_inbox_tasks = inbox_task_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=workspace.ref_id,
            direct_info=NotionInboxTask.DirectInfo(
                all_projects_map=all_projects_map, all_big_plans_map=all_big_plans_map
            ),
            inverse_info=NotionInboxTask.InverseInfo(
                default_project=default_project,
                all_projects_by_name=all_projects_by_name,
                all_projects_map=all_projects_map,
                all_big_plans_by_name=all_big_plans_by_name,
                all_big_plans_map=all_big_plans_map,
            ),
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_inbox_task_ref_ids,
            sync_prefer=args.sync_prefer,
        ).all
        return all_inbox_tasks

    def _sync_chores(
        self,
        progress_reporter: ProgressReporter,
        all_projects: Iterable[Project],
        args: Args,
        workspace: Workspace,
    ) -> Iterable[Chore]:
        all_projects_by_name = {format_name_for_option(p.name): p for p in all_projects}
        all_projects_map = {p.ref_id: p for p in all_projects}
        default_project = all_projects_map[workspace.default_project_ref_id]
        chore_sync_service = ChoreSyncService(
            self._storage_engine, self._chore_notion_manager
        )
        all_chores = chore_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=workspace.ref_id,
            direct_info=NotionChore.DirectInfo(all_projects_map=all_projects_map),
            inverse_info=NotionChore.InverseInfo(
                default_project=default_project,
                all_projects_by_name=all_projects_by_name,
                all_projects_map=all_projects_map,
            ),
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_chore_ref_ids,
            sync_prefer=args.sync_prefer,
        ).all
        return all_chores

    def _sync_habits(
        self,
        progress_reporter: ProgressReporter,
        all_projects: Iterable[Project],
        args: Args,
        workspace: Workspace,
    ) -> Iterable[Habit]:
        all_projects_by_name = {format_name_for_option(p.name): p for p in all_projects}
        all_projects_map = {p.ref_id: p for p in all_projects}
        default_project = all_projects_map[workspace.default_project_ref_id]
        habit_sync_service = HabitSyncService(
            self._storage_engine, self._habit_notion_manager
        )
        all_habits = habit_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=workspace.ref_id,
            direct_info=NotionHabit.DirectInfo(all_projects_map=all_projects_map),
            inverse_info=NotionHabit.InverseInfo(
                default_project=default_project,
                all_projects_by_name=all_projects_by_name,
                all_projects_map=all_projects_map,
            ),
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_habit_ref_ids,
            sync_prefer=args.sync_prefer,
        ).all
        return all_habits

    def _sync_big_plans(
        self,
        progress_reporter: ProgressReporter,
        all_projects: Iterable[Project],
        args: Args,
        big_plan_collection: BigPlanCollection,
        workspace: Workspace,
    ) -> Iterable[BigPlan]:
        all_projects_by_name = {format_name_for_option(p.name): p for p in all_projects}
        all_projects_map = {p.ref_id: p for p in all_projects}
        default_project = all_projects_map[workspace.default_project_ref_id]
        big_plan_sync_service = BigPlanSyncService(
            self._storage_engine, self._big_plan_notion_manager
        )
        sync_result = big_plan_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=workspace.ref_id,
            direct_info=NotionBigPlan.DirectInfo(all_projects_map=all_projects_map),
            inverse_info=NotionBigPlan.InverseInfo(
                default_project=default_project,
                all_projects_by_name=all_projects_by_name,
                all_projects_map=all_projects_map,
            ),
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_big_plan_ref_ids,
            sync_prefer=args.sync_prefer,
        )

        if sync_result.has_a_local_change:
            InboxTaskBigPlanRefOptionsUpdateService(
                self._storage_engine, self._inbox_task_notion_manager
            ).sync(big_plan_collection)
        return sync_result.all

    def _sync_projects(
        self, progress_reporter: ProgressReporter, args: Args, workspace: Workspace
    ) -> None:
        filter_project_ref_ids = None
        filter_project_keys = (
            list(args.filter_project_keys) if args.filter_project_keys else None
        )
        if filter_project_keys is not None:
            with self._storage_engine.get_unit_of_work() as uow:
                filter_project_ref_ids = (
                    uow.project_repository.exchange_keys_for_ref_ids(
                        filter_project_keys
                    )
                )
        project_sync_service = ProjectSyncServiceNew(
            self._storage_engine, self._project_notion_manager
        )
        project_sync_result = project_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=workspace.ref_id,
            direct_info=None,
            inverse_info=None,
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=filter_project_ref_ids,
            sync_prefer=args.sync_prefer,
        )

        if project_sync_result.has_a_local_change:
            ProjectLabelUpdateService(
                self._storage_engine,
                self._inbox_task_notion_manager,
                self._habit_notion_manager,
                self._chore_notion_manager,
                self._big_plan_notion_manager,
            ).sync(workspace, project_sync_result.all)

    def _sync_vacations(
        self, progress_reporter: ProgressReporter, args: Args, workspace: Workspace
    ) -> None:
        vacation_sync_service = VacationSyncService(
            self._storage_engine, self._vacation_notion_manager
        )
        vacation_sync_service.sync(
            progress_reporter=progress_reporter,
            parent_ref_id=workspace.ref_id,
            direct_info=None,
            inverse_info=None,
            drop_all_notion_side=args.drop_all_notion,
            sync_even_if_not_modified=args.sync_even_if_not_modified,
            filter_ref_ids=args.filter_vacation_ref_ids,
            sync_prefer=args.sync_prefer,
        )

    def _sync_workspace(
        self, progress_reporter: ProgressReporter, args: Args
    ) -> Workspace:
        workspace_sync_service = WorkspaceSyncService(
            self._storage_engine, self._workspace_notion_manager
        )
        workspace = workspace_sync_service.sync(
            progress_reporter=progress_reporter,
            right_now=self._time_provider.get_current_time(),
            sync_prefer=args.sync_prefer,
        )
        return workspace
