"""The CLI entry-point for Jupiter."""
import argparse
import logging

import coloredlogs

from jupiter.command.big_plan_archive import BigPlanArchive
from jupiter.command.big_plan_change_project import BigPlanChangeProject
from jupiter.command.big_plan_create import BigPlanCreate
from jupiter.command.big_plan_remove import BigPlanRemove
from jupiter.command.big_plan_show import BigPlanShow
from jupiter.command.big_plan_update import BigPlanUpdate
from jupiter.command.chore_archive import ChoreArchive
from jupiter.command.chore_change_project import ChoreChangeProject
from jupiter.command.chore_create import ChoreCreate
from jupiter.command.chore_remove import ChoreRemove
from jupiter.command.chore_show import ChoreShow
from jupiter.command.chore_suspend import ChoreSuspend
from jupiter.command.chore_unsuspend import ChoreUnsuspend
from jupiter.command.chore_update import ChoreUpdate
from jupiter.command.gc import GC
from jupiter.command.gen import Gen
from jupiter.command.habit_archive import HabitArchive
from jupiter.command.habit_change_project import HabitChangeProject
from jupiter.command.habit_create import HabitCreate
from jupiter.command.habit_remove import HabitRemove
from jupiter.command.habit_show import HabitShow
from jupiter.command.habit_suspend import HabitSuspend
from jupiter.command.habit_unsuspend import HabitUnsuspend
from jupiter.command.habit_update import HabitUpdate
from jupiter.command.inbox_task_archive import InboxTaskArchive
from jupiter.command.inbox_task_associate_with_big_plan import (
    InboxTaskAssociateWithBigPlan,
)
from jupiter.command.inbox_task_change_project import InboxTaskChangeProject
from jupiter.command.inbox_task_create import InboxTaskCreate
from jupiter.command.inbox_task_remove import InboxTaskRemove
from jupiter.command.inbox_task_show import InboxTaskShow
from jupiter.command.inbox_task_update import InboxTaskUpdate
from jupiter.command.initialize import Initialize
from jupiter.command.metric_archive import MetricArchive
from jupiter.command.metric_change_collection_project import (
    MetricChangeCollectionProject,
)
from jupiter.command.metric_create import MetricCreate
from jupiter.command.metric_entry_archive import MetricEntryArchive
from jupiter.command.metric_entry_create import MetricEntryCreate
from jupiter.command.metric_entry_remove import MetricEntryRemove
from jupiter.command.metric_entry_update import MetricEntryUpdate
from jupiter.command.metric_remove import MetricRemove
from jupiter.command.metric_show import MetricShow
from jupiter.command.metric_update import MetricUpdate
from jupiter.command.notion_connection_update_token import NotionConnectionUpdateToken
from jupiter.command.person_archive import PersonArchive
from jupiter.command.person_change_catch_up_project import PersonChangeCatchUpProject
from jupiter.command.person_create import PersonCreate
from jupiter.command.person_remove import PersonRemove
from jupiter.command.person_show import PersonShow
from jupiter.command.person_update import PersonUpdate
from jupiter.command.project_create import ProjectCreate
from jupiter.command.project_show import ProjectShow
from jupiter.command.project_update import ProjectUpdate
from jupiter.command.report import Report
from jupiter.command.slack_task_archive import SlackTaskArchive
from jupiter.command.slack_task_change_generation_project import (
    SlackTaskChangeGenerationProject,
)
from jupiter.command.slack_task_remove import SlackTaskRemove
from jupiter.command.slack_task_show import SlackTaskShow
from jupiter.command.slack_task_update import SlackTaskUpdate
from jupiter.command.smart_list_archive import SmartListArchive
from jupiter.command.smart_list_create import SmartListCreate
from jupiter.command.smart_list_item_archive import SmartListItemArchive
from jupiter.command.smart_list_item_create import SmartListItemCreate
from jupiter.command.smart_list_item_remove import SmartListItemRemove
from jupiter.command.smart_list_item_update import SmartListItemUpdate
from jupiter.command.smart_list_remove import SmartListsRemove
from jupiter.command.smart_list_show import SmartListShow
from jupiter.command.smart_list_tag_archive import SmartListTagArchive
from jupiter.command.smart_list_tag_create import SmartListTagCreate
from jupiter.command.smart_list_tag_remove import SmartListTagRemove
from jupiter.command.smart_list_tag_update import SmartListTagUpdate
from jupiter.command.smart_list_update import SmartListUpdate
from jupiter.command.sync import Sync
from jupiter.command.vacation_archive import VacationArchive
from jupiter.command.vacation_create import VacationCreate
from jupiter.command.vacation_remove import VacationRemove
from jupiter.command.vacation_show import VacationsShow
from jupiter.command.vacation_update import VacationUpdate
from jupiter.command.workspace_change_default_project import (
    WorkspaceChangeDefaultProject,
)
from jupiter.command.workspace_show import WorkspaceShow
from jupiter.command.workspace_update import WorkspaceUpdate
from jupiter.domain.timezone import Timezone
from jupiter.domain.workspaces.infra.workspace_notion_manager import (
    NotionWorkspaceNotFoundError,
)
from jupiter.domain.workspaces.infra.workspace_repository import (
    WorkspaceNotFoundError,
    WorkspaceAlreadyExistsError,
)
from jupiter.framework.errors import InputValidationError
from jupiter.framework.repository import EntityNotFoundError
from jupiter.remote.notion.big_plans_manager import NotionBigPlansManager
from jupiter.remote.notion.chores_manager import NotionChoresManager
from jupiter.remote.notion.habits_manager import NotionHabitsManager
from jupiter.remote.notion.inbox_tasks_manager import NotionInboxTasksManager
from jupiter.remote.notion.infra.client_builder import (
    MissingNotionConnectionError,
    OldTokenForNotionConnectionError,
    NotionClientBuilder,
)
from jupiter.remote.notion.infra.collections_manager import NotionCollectionsManager
from jupiter.remote.notion.infra.pages_manager import NotionPagesManager
from jupiter.remote.notion.metrics_manager import NotionMetricsManager
from jupiter.remote.notion.persons_manager import NotionPersonsManager
from jupiter.remote.notion.projects_manager import NotionProjectsManager
from jupiter.remote.notion.push_integration.push_integration_groups_manager import (
    NotionPushIntegrationGroupsManager,
)
from jupiter.remote.notion.push_integration.slack_tasks import NotionSlackTasksManager
from jupiter.remote.notion.smart_lists_manager import NotionSmartListsManager
from jupiter.remote.notion.vacations_manager import NotionVacationsManager
from jupiter.remote.notion.workspaces_manager import NotionWorkspacesManager
from jupiter.repository.sqlite.domain.storage_engine import SqliteDomainStorageEngine
from jupiter.repository.sqlite.remote.notion.storage_engine import (
    SqliteNotionStorageEngine,
)
from jupiter.repository.sqlite.use_case.storage_engine import SqliteUseCaseStorageEngine
from jupiter.use_cases.big_plans.archive import BigPlanArchiveUseCase
from jupiter.use_cases.big_plans.change_project import BigPlanChangeProjectUseCase
from jupiter.use_cases.big_plans.create import BigPlanCreateUseCase
from jupiter.use_cases.big_plans.find import BigPlanFindUseCase
from jupiter.use_cases.big_plans.remove import BigPlanRemoveUseCase
from jupiter.use_cases.big_plans.update import BigPlanUpdateUseCase
from jupiter.use_cases.chores.archive import ChoreArchiveUseCase
from jupiter.use_cases.chores.change_project import ChoreChangeProjectUseCase
from jupiter.use_cases.chores.create import ChoreCreateUseCase
from jupiter.use_cases.chores.find import ChoreFindUseCase
from jupiter.use_cases.chores.remove import ChoreRemoveUseCase
from jupiter.use_cases.chores.suspend import ChoreSuspendUseCase
from jupiter.use_cases.chores.unsuspend import ChoreUnsuspendUseCase
from jupiter.use_cases.chores.update import ChoreUpdateUseCase
from jupiter.use_cases.gc import GCUseCase
from jupiter.use_cases.gen import GenUseCase
from jupiter.use_cases.habits.archive import HabitArchiveUseCase
from jupiter.use_cases.habits.change_project import HabitChangeProjectUseCase
from jupiter.use_cases.habits.create import HabitCreateUseCase
from jupiter.use_cases.habits.find import HabitFindUseCase
from jupiter.use_cases.habits.remove import HabitRemoveUseCase
from jupiter.use_cases.habits.suspend import HabitSuspendUseCase
from jupiter.use_cases.habits.unsuspend import HabitUnsuspendUseCase
from jupiter.use_cases.habits.update import HabitUpdateUseCase
from jupiter.use_cases.inbox_tasks.archive import InboxTaskArchiveUseCase
from jupiter.use_cases.inbox_tasks.associate_with_big_plan import (
    InboxTaskAssociateWithBigPlanUseCase,
)
from jupiter.use_cases.inbox_tasks.change_project import InboxTaskChangeProjectUseCase
from jupiter.use_cases.inbox_tasks.create import InboxTaskCreateUseCase
from jupiter.use_cases.inbox_tasks.find import InboxTaskFindUseCase
from jupiter.use_cases.inbox_tasks.remove import InboxTaskRemoveUseCase
from jupiter.use_cases.inbox_tasks.update import InboxTaskUpdateUseCase
from jupiter.use_cases.infra.persistent_mutation_use_case_recoder import (
    PersistentMutationUseCaseInvocationRecorder,
)
from jupiter.use_cases.init import InitUseCase
from jupiter.use_cases.metrics.archive import MetricArchiveUseCase
from jupiter.use_cases.metrics.change_collection_project import (
    MetricChangeCollectionProjectUseCase,
)
from jupiter.use_cases.metrics.create import MetricCreateUseCase
from jupiter.use_cases.metrics.entry.archive import MetricEntryArchiveUseCase
from jupiter.use_cases.metrics.entry.create import MetricEntryCreateUseCase
from jupiter.use_cases.metrics.entry.remove import MetricEntryRemoveUseCase
from jupiter.use_cases.metrics.entry.update import MetricEntryUpdateUseCase
from jupiter.use_cases.metrics.find import MetricFindUseCase
from jupiter.use_cases.metrics.remove import MetricRemoveUseCase
from jupiter.use_cases.metrics.update import MetricUpdateUseCase
from jupiter.use_cases.persons.archive import PersonArchiveUseCase
from jupiter.use_cases.persons.change_catch_up_project import (
    PersonChangeCatchUpProjectUseCase,
)
from jupiter.use_cases.persons.create import PersonCreateUseCase
from jupiter.use_cases.persons.find import PersonFindUseCase
from jupiter.use_cases.persons.remove import PersonRemoveUseCase
from jupiter.use_cases.persons.update import PersonUpdateUseCase
from jupiter.use_cases.projects.create import ProjectCreateUseCase
from jupiter.use_cases.projects.find import ProjectFindUseCase
from jupiter.use_cases.projects.update import ProjectUpdateUseCase
from jupiter.use_cases.push_integrations.slack.archive import SlackTaskArchiveUseCase
from jupiter.use_cases.push_integrations.slack.change_generation_project import (
    SlackTaskChangeGenerationProjectUseCase,
)
from jupiter.use_cases.push_integrations.slack.find import SlackTaskFindUseCase
from jupiter.use_cases.push_integrations.slack.remove import SlackTaskRemoveUseCase
from jupiter.use_cases.push_integrations.slack.update import SlackTaskUpdateUseCase
from jupiter.use_cases.remote.notion.update_token import (
    NotionConnectionUpdateTokenUseCase,
)
from jupiter.use_cases.report import ReportUseCase
from jupiter.use_cases.smart_lists.archive import SmartListArchiveUseCase
from jupiter.use_cases.smart_lists.create import SmartListCreateUseCase
from jupiter.use_cases.smart_lists.find import SmartListFindUseCase
from jupiter.use_cases.smart_lists.item.archive import SmartListItemArchiveUseCase
from jupiter.use_cases.smart_lists.item.create import SmartListItemCreateUseCase
from jupiter.use_cases.smart_lists.item.remove import SmartListItemRemoveUseCase
from jupiter.use_cases.smart_lists.item.update import SmartListItemUpdateUseCase
from jupiter.use_cases.smart_lists.remove import SmartListRemoveUseCase
from jupiter.use_cases.smart_lists.tag.archive import SmartListTagArchiveUseCase
from jupiter.use_cases.smart_lists.tag.create import SmartListTagCreateUseCase
from jupiter.use_cases.smart_lists.tag.remove import SmartListTagRemoveUseCase
from jupiter.use_cases.smart_lists.tag.update import SmartListTagUpdateUseCase
from jupiter.use_cases.smart_lists.update import SmartListUpdateUseCase
from jupiter.use_cases.sync import SyncUseCase
from jupiter.use_cases.vacations.archive import VacationArchiveUseCase
from jupiter.use_cases.vacations.create import VacationCreateUseCase
from jupiter.use_cases.vacations.find import VacationFindUseCase
from jupiter.use_cases.vacations.remove import VacationRemoveUseCase
from jupiter.use_cases.vacations.update import VacationUpdateUseCase
from jupiter.use_cases.workspaces.change_default_project import (
    WorkspaceChangeDefaultProjectUseCase,
)
from jupiter.use_cases.workspaces.find import WorkspaceFindUseCase
from jupiter.use_cases.workspaces.update import WorkspaceUpdateUseCase
from jupiter.utils.global_properties import build_global_properties
from jupiter.utils.time_provider import TimeProvider


def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    timezone = _get_timezone()

    global_properties = build_global_properties(timezone)

    domain_storage_engine = SqliteDomainStorageEngine(
        SqliteDomainStorageEngine.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        )
    )

    notion_storage_engine = SqliteNotionStorageEngine(
        SqliteNotionStorageEngine.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        )
    )

    usecase_storage_engine = SqliteUseCaseStorageEngine(
        SqliteUseCaseStorageEngine.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        )
    )

    notion_client_builder = NotionClientBuilder(domain_storage_engine)
    notion_pages_manager = NotionPagesManager(
        time_provider, notion_client_builder, notion_storage_engine
    )
    notion_collections_manager = NotionCollectionsManager(
        time_provider, notion_client_builder, notion_storage_engine
    )

    notion_workspace_manager = NotionWorkspacesManager(notion_pages_manager)
    notion_vacation_manager = NotionVacationsManager(
        global_properties, time_provider, notion_collections_manager
    )
    notion_projects_manager = NotionProjectsManager(
        global_properties, time_provider, notion_collections_manager
    )
    notion_inbox_tasks_manager = NotionInboxTasksManager(
        global_properties, time_provider, notion_collections_manager
    )
    notion_chores_manager = NotionChoresManager(
        global_properties, time_provider, notion_collections_manager
    )
    notion_habits_manager = NotionHabitsManager(
        global_properties, time_provider, notion_collections_manager
    )
    notion_big_plans_manager = NotionBigPlansManager(
        global_properties, time_provider, notion_collections_manager
    )
    notion_smart_lists_manager = NotionSmartListsManager(
        global_properties,
        time_provider,
        notion_pages_manager,
        notion_collections_manager,
    )
    notion_metrics_manager = NotionMetricsManager(
        global_properties,
        time_provider,
        notion_pages_manager,
        notion_collections_manager,
    )
    notion_persons_manager = NotionPersonsManager(
        global_properties, time_provider, notion_collections_manager
    )
    notion_push_integration_group_manager = NotionPushIntegrationGroupsManager(
        notion_pages_manager
    )
    notion_slack_tasks_manager = NotionSlackTasksManager(
        global_properties, notion_collections_manager
    )

    invocation_recorder = PersistentMutationUseCaseInvocationRecorder(
        usecase_storage_engine
    )

    commands = {
        # Complex commands.
        Initialize(
            InitUseCase(
                time_provider,
                domain_storage_engine,
                notion_workspace_manager,
                notion_vacation_manager,
                notion_projects_manager,
                notion_inbox_tasks_manager,
                notion_habits_manager,
                notion_chores_manager,
                notion_big_plans_manager,
                notion_smart_lists_manager,
                notion_metrics_manager,
                notion_persons_manager,
                notion_push_integration_group_manager,
                notion_slack_tasks_manager,
            )
        ),
        Sync(
            SyncUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_workspace_manager,
                notion_vacation_manager,
                notion_projects_manager,
                notion_inbox_tasks_manager,
                notion_habits_manager,
                notion_chores_manager,
                notion_big_plans_manager,
                notion_smart_lists_manager,
                notion_metrics_manager,
                notion_persons_manager,
                notion_push_integration_group_manager,
                notion_slack_tasks_manager,
            )
        ),
        Gen(
            global_properties,
            time_provider,
            GenUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
            ),
        ),
        Report(
            global_properties,
            time_provider,
            ReportUseCase(global_properties, domain_storage_engine),
        ),
        GC(
            GCUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_vacation_manager,
                notion_projects_manager,
                notion_inbox_tasks_manager,
                notion_habits_manager,
                notion_chores_manager,
                notion_big_plans_manager,
                notion_smart_lists_manager,
                notion_metrics_manager,
                notion_persons_manager,
                notion_slack_tasks_manager,
            )
        ),
        # CRUD Commands.
        WorkspaceUpdate(
            WorkspaceUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_workspace_manager,
            )
        ),
        WorkspaceChangeDefaultProject(
            WorkspaceChangeDefaultProjectUseCase(
                time_provider, invocation_recorder, domain_storage_engine
            )
        ),
        WorkspaceShow(WorkspaceFindUseCase(domain_storage_engine)),
        VacationCreate(
            global_properties,
            VacationCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_vacation_manager,
            ),
        ),
        VacationArchive(
            VacationArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_vacation_manager,
            )
        ),
        VacationUpdate(
            global_properties,
            VacationUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_vacation_manager,
            ),
        ),
        VacationRemove(
            VacationRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_vacation_manager,
            )
        ),
        VacationsShow(global_properties, VacationFindUseCase(domain_storage_engine)),
        ProjectCreate(
            ProjectCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_projects_manager,
                notion_inbox_tasks_manager,
                notion_habits_manager,
                notion_chores_manager,
                notion_big_plans_manager,
            )
        ),
        ProjectUpdate(
            ProjectUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_projects_manager,
                notion_inbox_tasks_manager,
                notion_habits_manager,
                notion_chores_manager,
                notion_big_plans_manager,
            )
        ),
        ProjectShow(ProjectFindUseCase(domain_storage_engine)),
        InboxTaskCreate(
            global_properties,
            InboxTaskCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
            ),
        ),
        InboxTaskArchive(
            InboxTaskArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
            )
        ),
        InboxTaskChangeProject(
            InboxTaskChangeProjectUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
            )
        ),
        InboxTaskAssociateWithBigPlan(
            InboxTaskAssociateWithBigPlanUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
            )
        ),
        InboxTaskRemove(
            InboxTaskRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
            )
        ),
        InboxTaskUpdate(
            global_properties,
            InboxTaskUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
            ),
        ),
        InboxTaskShow(global_properties, InboxTaskFindUseCase(domain_storage_engine)),
        HabitCreate(
            global_properties,
            HabitCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_habits_manager,
            ),
        ),
        HabitArchive(
            HabitArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_habits_manager,
            )
        ),
        HabitChangeProject(
            HabitChangeProjectUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_habits_manager,
            )
        ),
        HabitSuspend(
            HabitSuspendUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_habits_manager,
            )
        ),
        HabitUnsuspend(
            HabitUnsuspendUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_habits_manager,
            )
        ),
        HabitUpdate(
            global_properties,
            HabitUpdateUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_habits_manager,
            ),
        ),
        HabitRemove(
            HabitRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_habits_manager,
            )
        ),
        HabitShow(global_properties, HabitFindUseCase(domain_storage_engine)),
        ChoreCreate(
            global_properties,
            ChoreCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_chores_manager,
            ),
        ),
        ChoreArchive(
            ChoreArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_chores_manager,
            )
        ),
        ChoreChangeProject(
            ChoreChangeProjectUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_chores_manager,
            )
        ),
        ChoreSuspend(
            ChoreSuspendUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_chores_manager,
            )
        ),
        ChoreUnsuspend(
            ChoreUnsuspendUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_chores_manager,
            )
        ),
        ChoreUpdate(
            global_properties,
            ChoreUpdateUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_chores_manager,
            ),
        ),
        ChoreRemove(
            ChoreRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_chores_manager,
            )
        ),
        ChoreShow(global_properties, ChoreFindUseCase(domain_storage_engine)),
        BigPlanCreate(
            global_properties,
            BigPlanCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_big_plans_manager,
            ),
        ),
        BigPlanArchive(
            BigPlanArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_big_plans_manager,
            )
        ),
        BigPlanRemove(
            BigPlanRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_big_plans_manager,
            )
        ),
        BigPlanChangeProject(
            BigPlanChangeProjectUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_big_plans_manager,
            )
        ),
        BigPlanUpdate(
            global_properties,
            BigPlanUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_big_plans_manager,
            ),
        ),
        BigPlanShow(global_properties, BigPlanFindUseCase(domain_storage_engine)),
        SmartListCreate(
            SmartListCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListArchive(
            SmartListArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListUpdate(
            SmartListUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListShow(SmartListFindUseCase(domain_storage_engine)),
        SmartListsRemove(
            SmartListRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListTagCreate(
            SmartListTagCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListTagArchive(
            SmartListTagArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListTagUpdate(
            SmartListTagUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListTagRemove(
            SmartListTagRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListItemCreate(
            SmartListItemCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListItemArchive(
            SmartListItemArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListItemUpdate(
            SmartListItemUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        SmartListItemRemove(
            SmartListItemRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_smart_lists_manager,
            )
        ),
        MetricChangeCollectionProject(
            MetricChangeCollectionProjectUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_metrics_manager,
            )
        ),
        MetricCreate(
            MetricCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_metrics_manager,
            )
        ),
        MetricArchive(
            MetricArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_metrics_manager,
            )
        ),
        MetricUpdate(
            MetricUpdateUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_metrics_manager,
            )
        ),
        MetricShow(global_properties, MetricFindUseCase(domain_storage_engine)),
        MetricRemove(
            MetricRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_metrics_manager,
            )
        ),
        MetricEntryCreate(
            MetricEntryCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_metrics_manager,
            )
        ),
        MetricEntryArchive(
            MetricEntryArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_metrics_manager,
            )
        ),
        MetricEntryUpdate(
            MetricEntryUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_metrics_manager,
            )
        ),
        MetricEntryRemove(
            MetricEntryRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_metrics_manager,
            )
        ),
        PersonChangeCatchUpProject(
            PersonChangeCatchUpProjectUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_persons_manager,
            )
        ),
        PersonCreate(
            PersonCreateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_persons_manager,
            )
        ),
        PersonArchive(
            PersonArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_persons_manager,
            )
        ),
        PersonUpdate(
            PersonUpdateUseCase(
                global_properties,
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_persons_manager,
            )
        ),
        PersonRemove(
            PersonRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_persons_manager,
            )
        ),
        PersonShow(PersonFindUseCase(domain_storage_engine)),
        SlackTaskArchive(
            SlackTaskArchiveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_slack_tasks_manager,
            )
        ),
        SlackTaskRemove(
            SlackTaskRemoveUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_slack_tasks_manager,
            )
        ),
        SlackTaskUpdate(
            global_properties,
            SlackTaskUpdateUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_slack_tasks_manager,
            ),
        ),
        SlackTaskChangeGenerationProject(
            SlackTaskChangeGenerationProjectUseCase(
                time_provider,
                invocation_recorder,
                domain_storage_engine,
                notion_inbox_tasks_manager,
                notion_slack_tasks_manager,
            )
        ),
        SlackTaskShow(global_properties, SlackTaskFindUseCase(domain_storage_engine)),
        # Remote connection commands
        NotionConnectionUpdateToken(
            NotionConnectionUpdateTokenUseCase(
                time_provider, invocation_recorder, domain_storage_engine
            )
        ),
    }

    parser = argparse.ArgumentParser(description=global_properties.description)
    parser.add_argument(
        "--min-log-level",
        dest="min_log_level",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="The logging level to use",
    )
    parser.add_argument(
        "--verbose",
        dest="verbose_logging",
        action="store_const",
        default=False,
        const=True,
        help="Show more log messages",
    )
    parser.add_argument(
        "--version",
        dest="just_show_version",
        action="store_const",
        default=False,
        const=True,
        help="Show the version of the application",
    )

    subparsers = parser.add_subparsers(dest="subparser_name", help="Sub-command help")

    for command in commands:
        command_parser = subparsers.add_parser(
            command.name(),
            help=command.description(),
            description=command.description(),
        )
        command.build_parser(command_parser)

    args = parser.parse_args()

    coloredlogs.install(
        level=_map_log_level_to_log_class(args.min_log_level),
        fmt="%(asctime)s %(name)-12s %(levelname)-6s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.just_show_version:
        print(f"{global_properties.description} {global_properties.version}")
        return

    if not args.verbose_logging:
        for handler in logging.root.handlers:
            handler.addFilter(CommandsAndControllersLoggerFilter())

    domain_storage_engine.prepare()
    # not technically needed --> notion_storage_engine.prepare()
    # not technically needed -> usecase_storage_engine.prepare()

    try:
        for command in commands:
            if args.subparser_name != command.name():
                continue
            command.run(args)
            break
    except InputValidationError as err:
        print("Looks like there's something wrong with the command's arguments:")
        print(f"  {err}")
    except WorkspaceAlreadyExistsError:
        print("A workspace already seems to exist here!")
        print("Please try another location if you want a new one.")
    except (
        WorkspaceNotFoundError,
        NotionWorkspaceNotFoundError,
        MissingNotionConnectionError,
    ):
        print(
            f"The Notion connection isn't setup, please run '{Initialize.name()}' to create a workspace!"
        )
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}"
        )
    except OldTokenForNotionConnectionError:
        print(
            f"The Notion connection's token has expired, please refresh it with '{NotionConnectionUpdateToken.name()}'"
        )
        print(
            f"For more information checkout: {global_properties.docs_update_expired_token_url}"
        )
    except EntityNotFoundError as err:
        print(
            f"For more information checkout: {global_properties.docs_fix_data_inconsistencies_url}"
        )
        raise err


class CommandsAndControllersLoggerFilter(logging.Filter):
    """A filter for commands and controllers."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filtering the log records for commands."""
        if record.name.startswith("command."):
            return True
        return False


def _get_timezone() -> Timezone:
    global_properties = build_global_properties()

    storage_engine = SqliteDomainStorageEngine(
        SqliteDomainStorageEngine.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        )
    )

    with storage_engine.get_unit_of_work() as uow:
        workspace = uow.workspace_repository.load_optional()

    if workspace is not None:
        return workspace.timezone
    else:
        return global_properties.timezone


def _map_log_level_to_log_class(log_level: str) -> int:
    if log_level == "debug":
        return logging.DEBUG
    elif log_level == "info":
        return logging.INFO
    elif log_level == "warning":
        return logging.WARNING
    elif log_level == "error":
        return logging.ERROR
    elif log_level == "critical":
        return logging.CRITICAL
    else:
        raise InputValidationError(f"Invalid log level '{log_level}'")


if __name__ == "__main__":
    main()
