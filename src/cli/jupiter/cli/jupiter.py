"""The CLI entry-point for Jupiter."""
import argparse
import asyncio
import logging
import sys
from typing import List

import aiohttp
from jupiter.core.use_cases.infra.realms import ModuleExplorerRealmCodecRegistry
from jupiter.cli.command.auth_change_password import AuthChangePassword
from jupiter.cli.command.big_plan_archive import BigPlanArchive
from jupiter.cli.command.big_plan_change_project import BigPlanChangeProject
from jupiter.cli.command.big_plan_create import BigPlanCreate
from jupiter.cli.command.big_plan_remove import BigPlanRemove
from jupiter.cli.command.big_plan_show import BigPlanShow
from jupiter.cli.command.big_plan_update import BigPlanUpdate
from jupiter.cli.command.chore_archive import ChoreArchive
from jupiter.cli.command.chore_change_project import ChoreChangeProject
from jupiter.cli.command.chore_create import ChoreCreate
from jupiter.cli.command.chore_remove import ChoreRemove
from jupiter.cli.command.chore_show import ChoreShow
from jupiter.cli.command.chore_suspend import ChoreSuspend
from jupiter.cli.command.chore_unsuspend import ChoreUnsuspend
from jupiter.cli.command.chore_update import ChoreUpdate
from jupiter.cli.command.command import Command
from jupiter.cli.command.email_task_archive import EmailTaskArchive
from jupiter.cli.command.email_task_change_generation_project import (
    EmailTaskChangeGenerationProject,
)
from jupiter.cli.command.email_task_remove import EmailTaskRemove
from jupiter.cli.command.email_task_show import EmailTaskShow
from jupiter.cli.command.email_task_update import EmailTaskUpdate
from jupiter.cli.command.gc_do import GCDo
from jupiter.cli.command.gc_show import GCShow
from jupiter.cli.command.gen_do import GenDo
from jupiter.cli.command.gen_show import GenShow
from jupiter.cli.command.habit_archive import HabitArchive
from jupiter.cli.command.habit_change_project import HabitChangeProject
from jupiter.cli.command.habit_create import HabitCreate
from jupiter.cli.command.habit_remove import HabitRemove
from jupiter.cli.command.habit_show import HabitShow
from jupiter.cli.command.habit_suspend import HabitSuspend
from jupiter.cli.command.habit_unsuspend import HabitUnsuspend
from jupiter.cli.command.habit_update import HabitUpdate
from jupiter.cli.command.inbox_task_archive import InboxTaskArchive
from jupiter.cli.command.inbox_task_associate_with_big_plan import (
    InboxTaskAssociateWithBigPlan,
)
from jupiter.cli.command.inbox_task_change_project import InboxTaskChangeProject
from jupiter.cli.command.inbox_task_create import InboxTaskCreate
from jupiter.cli.command.inbox_task_remove import InboxTaskRemove
from jupiter.cli.command.inbox_task_show import InboxTaskShow
from jupiter.cli.command.inbox_task_update import InboxTaskUpdate
from jupiter.cli.command.initialize import Initialize
from jupiter.cli.command.login import Login
from jupiter.cli.command.logout import Logout
from jupiter.cli.command.metric_archive import MetricArchive
from jupiter.cli.command.metric_change_collection_project import (
    MetricChangeCollectionProject,
)
from jupiter.cli.command.metric_create import MetricCreate
from jupiter.cli.command.metric_entry_archive import MetricEntryArchive
from jupiter.cli.command.metric_entry_create import MetricEntryCreate
from jupiter.cli.command.metric_entry_remove import MetricEntryRemove
from jupiter.cli.command.metric_entry_update import MetricEntryUpdate
from jupiter.cli.command.metric_remove import MetricRemove
from jupiter.cli.command.metric_show import MetricShow
from jupiter.cli.command.metric_update import MetricUpdate
from jupiter.cli.command.person_archive import PersonArchive
from jupiter.cli.command.person_change_catch_up_project import (
    PersonChangeCatchUpProject,
)
from jupiter.cli.command.person_create import PersonCreate
from jupiter.cli.command.person_remove import PersonRemove
from jupiter.cli.command.person_show import PersonShow
from jupiter.cli.command.person_update import PersonUpdate
from jupiter.cli.command.pomodoro import Pomodoro
from jupiter.cli.command.project_archive import ProjectArchive
from jupiter.cli.command.project_create import ProjectCreate
from jupiter.cli.command.project_remove import ProjectRemove
from jupiter.cli.command.project_show import ProjectShow
from jupiter.cli.command.project_update import ProjectUpdate
from jupiter.cli.command.rendering import RichConsoleProgressReporterFactory
from jupiter.cli.command.report import Report
from jupiter.cli.command.reset_password import ResetPassword
from jupiter.cli.command.search import Search
from jupiter.cli.command.slack_task_archive import SlackTaskArchive
from jupiter.cli.command.slack_task_change_generation_project import (
    SlackTaskChangeGenerationProject,
)
from jupiter.cli.command.slack_task_remove import SlackTaskRemove
from jupiter.cli.command.slack_task_show import SlackTaskShow
from jupiter.cli.command.slack_task_update import SlackTaskUpdate
from jupiter.cli.command.smart_list_archive import SmartListArchive
from jupiter.cli.command.smart_list_create import SmartListCreate
from jupiter.cli.command.smart_list_item_archive import SmartListItemArchive
from jupiter.cli.command.smart_list_item_create import SmartListItemCreate
from jupiter.cli.command.smart_list_item_remove import SmartListItemRemove
from jupiter.cli.command.smart_list_item_update import SmartListItemUpdate
from jupiter.cli.command.smart_list_remove import SmartListsRemove
from jupiter.cli.command.smart_list_show import SmartListShow
from jupiter.cli.command.smart_list_tag_archive import SmartListTagArchive
from jupiter.cli.command.smart_list_tag_create import SmartListTagCreate
from jupiter.cli.command.smart_list_tag_remove import SmartListTagRemove
from jupiter.cli.command.smart_list_tag_update import SmartListTagUpdate
from jupiter.cli.command.smart_list_update import SmartListUpdate
from jupiter.cli.command.test_helper_clear_all import TestHelperClearAll
from jupiter.cli.command.test_helper_nuke import TestHelperNuke
from jupiter.cli.command.user_change_feature_flags import UserChangeFeatureFlags
from jupiter.cli.command.user_show import UserShow
from jupiter.cli.command.user_update import UserUpdate
from jupiter.cli.command.vacation_archive import VacationArchive
from jupiter.cli.command.vacation_create import VacationCreate
from jupiter.cli.command.vacation_remove import VacationRemove
from jupiter.cli.command.vacation_show import VacationsShow
from jupiter.cli.command.vacation_update import VacationUpdate
from jupiter.cli.command.workspace_change_default_project import (
    WorkspaceChangeDefaultProject,
)
from jupiter.cli.command.workspace_change_feature_flags import (
    WorkspaceChangeFeatureFlags,
)
from jupiter.cli.command.workspace_show import WorkspaceShow
from jupiter.cli.command.workspace_update import WorkspaceUpdate
from jupiter.cli.session_storage import SessionInfoNotFoundError, SessionStorage
from jupiter.cli.top_level_context import TopLevelContext
from jupiter.core.domain.auth.auth_token import (
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.features import FeatureUnavailableError
from jupiter.core.domain.projects.errors import ProjectInSignificantUseError
from jupiter.core.domain.user.infra.user_repository import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceNotFoundError,
)
from jupiter.core.framework.errors import InputValidationError
from jupiter.core.framework.repository import LeafEntityNotFoundError
from jupiter.core.framework.storage import ConnectionPrepareError
from jupiter.core.repository.sqlite.connection import SqliteConnection
from jupiter.core.repository.sqlite.domain.storage_engine import (
    SqliteDomainStorageEngine,
    SqliteSearchStorageEngine,
)
from jupiter.core.repository.sqlite.use_case.storage_engine import (
    SqliteUseCaseStorageEngine,
)
from jupiter.core.use_cases.auth.change_password import ChangePasswordUseCase
from jupiter.core.use_cases.auth.reset_password import ResetPasswordUseCase
from jupiter.core.use_cases.big_plans.archive import BigPlanArchiveUseCase
from jupiter.core.use_cases.big_plans.change_project import BigPlanChangeProjectUseCase
from jupiter.core.use_cases.big_plans.create import BigPlanCreateUseCase
from jupiter.core.use_cases.big_plans.find import BigPlanFindUseCase
from jupiter.core.use_cases.big_plans.remove import BigPlanRemoveUseCase
from jupiter.core.use_cases.big_plans.update import BigPlanUpdateUseCase
from jupiter.core.use_cases.chores.archive import ChoreArchiveUseCase
from jupiter.core.use_cases.chores.change_project import ChoreChangeProjectUseCase
from jupiter.core.use_cases.chores.create import ChoreCreateUseCase
from jupiter.core.use_cases.chores.find import ChoreFindUseCase
from jupiter.core.use_cases.chores.remove import ChoreRemoveUseCase
from jupiter.core.use_cases.chores.suspend import ChoreSuspendUseCase
from jupiter.core.use_cases.chores.unsuspend import ChoreUnsuspendUseCase
from jupiter.core.use_cases.chores.update import ChoreUpdateUseCase
from jupiter.core.use_cases.gc.do import GCDoUseCase
from jupiter.core.use_cases.gc.load_runs import GCLoadRunsUseCase
from jupiter.core.use_cases.gen.do import GenDoUseCase
from jupiter.core.use_cases.gen.load_runs import GenLoadRunsUseCase
from jupiter.core.use_cases.habits.archive import HabitArchiveUseCase
from jupiter.core.use_cases.habits.change_project import HabitChangeProjectUseCase
from jupiter.core.use_cases.habits.create import HabitCreateUseCase
from jupiter.core.use_cases.habits.find import HabitFindUseCase
from jupiter.core.use_cases.habits.remove import HabitRemoveUseCase
from jupiter.core.use_cases.habits.suspend import HabitSuspendUseCase
from jupiter.core.use_cases.habits.unsuspend import HabitUnsuspendUseCase
from jupiter.core.use_cases.habits.update import HabitUpdateUseCase
from jupiter.core.use_cases.inbox_tasks.archive import InboxTaskArchiveUseCase
from jupiter.core.use_cases.inbox_tasks.associate_with_big_plan import (
    InboxTaskAssociateWithBigPlanUseCase,
)
from jupiter.core.use_cases.inbox_tasks.change_project import (
    InboxTaskChangeProjectUseCase,
)
from jupiter.core.use_cases.inbox_tasks.create import InboxTaskCreateUseCase
from jupiter.core.use_cases.inbox_tasks.find import InboxTaskFindUseCase
from jupiter.core.use_cases.inbox_tasks.remove import InboxTaskRemoveUseCase
from jupiter.core.use_cases.inbox_tasks.update import InboxTaskUpdateUseCase
from jupiter.core.use_cases.infra.persistent_mutation_use_case_recoder import (
    PersistentMutationUseCaseInvocationRecorder,
)
from jupiter.core.use_cases.infra.use_cases import AppGuestUseCaseSession
from jupiter.core.use_cases.init import InitUseCase
from jupiter.core.use_cases.load_top_level_info import (
    LoadTopLevelInfoArgs,
    LoadTopLevelInfoUseCase,
)
from jupiter.core.use_cases.login import InvalidLoginCredentialsError, LoginUseCase
from jupiter.core.use_cases.metrics.archive import MetricArchiveUseCase
from jupiter.core.use_cases.metrics.change_collection_project import (
    MetricChangeCollectionProjectUseCase,
)
from jupiter.core.use_cases.metrics.create import MetricCreateUseCase
from jupiter.core.use_cases.metrics.entry.archive import MetricEntryArchiveUseCase
from jupiter.core.use_cases.metrics.entry.create import MetricEntryCreateUseCase
from jupiter.core.use_cases.metrics.entry.remove import MetricEntryRemoveUseCase
from jupiter.core.use_cases.metrics.entry.update import MetricEntryUpdateUseCase
from jupiter.core.use_cases.metrics.find import MetricFindUseCase
from jupiter.core.use_cases.metrics.remove import MetricRemoveUseCase
from jupiter.core.use_cases.metrics.update import MetricUpdateUseCase
from jupiter.core.use_cases.persons.archive import PersonArchiveUseCase
from jupiter.core.use_cases.persons.change_catch_up_project import (
    PersonChangeCatchUpProjectUseCase,
)
from jupiter.core.use_cases.persons.create import PersonCreateUseCase
from jupiter.core.use_cases.persons.find import PersonFindUseCase
from jupiter.core.use_cases.persons.remove import PersonRemoveUseCase
from jupiter.core.use_cases.persons.update import PersonUpdateUseCase
from jupiter.core.use_cases.projects.archive import ProjectArchiveUseCase
from jupiter.core.use_cases.projects.create import ProjectCreateUseCase
from jupiter.core.use_cases.projects.find import ProjectFindUseCase
from jupiter.core.use_cases.projects.remove import ProjectRemoveUseCase
from jupiter.core.use_cases.projects.update import ProjectUpdateUseCase
from jupiter.core.use_cases.push_integrations.email.archive import (
    EmailTaskArchiveUseCase,
)
from jupiter.core.use_cases.push_integrations.email.change_generation_project import (
    EmailTaskChangeGenerationProjectUseCase,
)
from jupiter.core.use_cases.push_integrations.email.find import EmailTaskFindUseCase
from jupiter.core.use_cases.push_integrations.email.remove import EmailTaskRemoveUseCase
from jupiter.core.use_cases.push_integrations.email.update import EmailTaskUpdateUseCase
from jupiter.core.use_cases.push_integrations.slack.archive import (
    SlackTaskArchiveUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.change_generation_project import (
    SlackTaskChangeGenerationProjectUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.find import SlackTaskFindUseCase
from jupiter.core.use_cases.push_integrations.slack.remove import SlackTaskRemoveUseCase
from jupiter.core.use_cases.push_integrations.slack.update import SlackTaskUpdateUseCase
from jupiter.core.use_cases.report import ReportUseCase
from jupiter.core.use_cases.search import SearchUseCase
from jupiter.core.use_cases.smart_lists.archive import SmartListArchiveUseCase
from jupiter.core.use_cases.smart_lists.create import SmartListCreateUseCase
from jupiter.core.use_cases.smart_lists.find import SmartListFindUseCase
from jupiter.core.use_cases.smart_lists.item.archive import SmartListItemArchiveUseCase
from jupiter.core.use_cases.smart_lists.item.create import SmartListItemCreateUseCase
from jupiter.core.use_cases.smart_lists.item.remove import SmartListItemRemoveUseCase
from jupiter.core.use_cases.smart_lists.item.update import SmartListItemUpdateUseCase
from jupiter.core.use_cases.smart_lists.remove import SmartListRemoveUseCase
from jupiter.core.use_cases.smart_lists.tag.archive import SmartListTagArchiveUseCase
from jupiter.core.use_cases.smart_lists.tag.create import SmartListTagCreateUseCase
from jupiter.core.use_cases.smart_lists.tag.remove import SmartListTagRemoveUseCase
from jupiter.core.use_cases.smart_lists.tag.update import SmartListTagUpdateUseCase
from jupiter.core.use_cases.smart_lists.update import SmartListUpdateUseCase
from jupiter.core.use_cases.test_helper.clear_all import ClearAllUseCase
from jupiter.core.use_cases.test_helper.nuke import NukeUseCase
from jupiter.core.use_cases.user.change_feature_flags import (
    UserChangeFeatureFlagsUseCase,
)
from jupiter.core.use_cases.user.load import UserLoadUseCase
from jupiter.core.use_cases.user.update import UserUpdateUseCase
from jupiter.core.use_cases.vacations.archive import VacationArchiveUseCase
from jupiter.core.use_cases.vacations.create import VacationCreateUseCase
from jupiter.core.use_cases.vacations.find import VacationFindUseCase
from jupiter.core.use_cases.vacations.remove import VacationRemoveUseCase
from jupiter.core.use_cases.vacations.update import VacationUpdateUseCase
from jupiter.core.use_cases.workspaces.change_default_project import (
    WorkspaceChangeDefaultProjectUseCase,
)
from jupiter.core.use_cases.workspaces.change_feature_flags import (
    WorkspaceChangeFeatureFlagsUseCase,
)
from jupiter.core.use_cases.workspaces.load import WorkspaceLoadUseCase
from jupiter.core.use_cases.workspaces.update import WorkspaceUpdateUseCase
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.core.utils.noop_use_case import NoOpUseCase
from jupiter.core.utils.progress_reporter import (
    EmptyProgressReporterFactory,
    NoOpProgressReporterFactory,
)
from jupiter.core.utils.time_provider import TimeProvider
from rich.console import Console
from rich.panel import Panel
import jupiter.core.domain

# import coverage


async def main() -> None:
    """Application main function."""
    logging.disable()

    time_provider = TimeProvider()

    global_properties = build_global_properties()

    realm_codec_registry = ModuleExplorerRealmCodecRegistry.build_from_module_root(jupiter.core.domain)

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        ),
    )

    domain_storage_engine = SqliteDomainStorageEngine(realm_codec_registry, sqlite_connection)
    search_storage_engine = SqliteSearchStorageEngine(realm_codec_registry, sqlite_connection)
    usecase_storage_engine = SqliteUseCaseStorageEngine(sqlite_connection)

    session_storage = SessionStorage(global_properties.session_info_path)

    auth_token_stamper = AuthTokenStamper(
        auth_token_secret=global_properties.auth_token_secret,
        time_provider=time_provider,
    )

    aio_session = aiohttp.ClientSession()

    invocation_recorder = PersistentMutationUseCaseInvocationRecorder(
        usecase_storage_engine,
    )

    console = Console()

    progress_reporter_factory = RichConsoleProgressReporterFactory(console)

    load_top_level_info_use_case = LoadTopLevelInfoUseCase(
        auth_token_stamper=auth_token_stamper,
        storage_engine=domain_storage_engine,
        global_properties=global_properties,
        time_provider=time_provider,
    )

    await sqlite_connection.prepare()

    session_info = session_storage.load_optional()
    guest_session = AppGuestUseCaseSession(
        session_info.auth_token_ext if session_info else None
    )
    top_level_info = await load_top_level_info_use_case.execute(
        guest_session, LoadTopLevelInfoArgs()
    )

    top_level_context = TopLevelContext(
        default_workspace_name=top_level_info.deafult_workspace_name,
        default_first_project_name=top_level_info.default_first_project_name,
        user=top_level_info.user,
        workspace=top_level_info.workspace,
    )

    no_session_command = [
        Initialize(
            session_storage=session_storage,
            top_level_context=top_level_context,
            use_case=InitUseCase(
                time_provider,
                invocation_recorder,
                NoOpProgressReporterFactory(),
                auth_token_stamper,
                domain_storage_engine,
                search_storage_engine,
                global_properties,
            ),
        ),
        Login(
            session_storage=session_storage,
            use_case=LoginUseCase(
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
    ]

    commands: List[Command] = no_session_command

    if top_level_info.user is not None and top_level_info.workspace is not None:
        commands.extend(
            [
                # Complex commands.
                AuthChangePassword(
                    session_storage=session_storage,
                    top_level_context=top_level_context.to_logged_in(),
                    use_case=ChangePasswordUseCase(
                        time_provider=time_provider,
                        invocation_recorder=invocation_recorder,
                        progress_reporter_factory=progress_reporter_factory,
                        auth_token_stamper=auth_token_stamper,
                        domain_storage_engine=domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ResetPassword(
                    session_storage=session_storage,
                    use_case=ResetPasswordUseCase(
                        time_provider=time_provider,
                        invocation_recorder=invocation_recorder,
                        progress_reporter_factory=NoOpProgressReporterFactory(),
                        auth_token_stamper=auth_token_stamper,
                        storage_engine=domain_storage_engine,
                    ),
                ),
                Search(
                    session_storage=session_storage,
                    top_level_context=top_level_context.to_logged_in(),
                    global_properties=global_properties,
                    time_provider=time_provider,
                    use_case=SearchUseCase(
                        auth_token_stamper=auth_token_stamper,
                        domain_storage_engine=domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                GenDo(
                    global_properties,
                    time_provider,
                    session_storage,
                    top_level_context.to_logged_in(),
                    GenDoUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                GenShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    GenLoadRunsUseCase(
                        auth_token_stamper,
                        domain_storage_engine,
                    ),
                ),
                Report(
                    global_properties,
                    time_provider,
                    session_storage,
                    top_level_context.to_logged_in(),
                    ReportUseCase(auth_token_stamper, domain_storage_engine),
                ),
                GCDo(
                    session_storage,
                    top_level_context.to_logged_in(),
                    GCDoUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                GCShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    GCLoadRunsUseCase(
                        auth_token_stamper,
                        domain_storage_engine,
                    ),
                ),
                Pomodoro(
                    session_storage,
                    top_level_context.to_logged_in(),
                    NoOpUseCase(
                        auth_token_stamper=auth_token_stamper,
                        storage_engine=domain_storage_engine,
                    ),
                ),
                Logout(session_storage=session_storage),
                # CRUD Commands.
                UserUpdate(
                    session_storage=session_storage,
                    top_level_context=top_level_context.to_logged_in(),
                    use_case=UserUpdateUseCase(
                        time_provider=time_provider,
                        invocation_recorder=invocation_recorder,
                        progress_reporter_factory=progress_reporter_factory,
                        auth_token_stamper=auth_token_stamper,
                        domain_storage_engine=domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                UserChangeFeatureFlags(
                    session_storage,
                    top_level_context.to_logged_in(),
                    UserChangeFeatureFlagsUseCase(
                        time_provider=time_provider,
                        invocation_recorder=invocation_recorder,
                        progress_reporter_factory=progress_reporter_factory,
                        auth_token_stamper=auth_token_stamper,
                        domain_storage_engine=domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                        global_properties=global_properties,
                    ),
                ),
                UserShow(
                    session_storage=session_storage,
                    top_level_context=top_level_context.to_logged_in(),
                    use_case=UserLoadUseCase(
                        auth_token_stamper=auth_token_stamper,
                        storage_engine=domain_storage_engine,
                        time_provider=time_provider,
                    ),
                ),
                WorkspaceUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    WorkspaceUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                WorkspaceChangeDefaultProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    WorkspaceChangeDefaultProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                WorkspaceChangeFeatureFlags(
                    session_storage,
                    top_level_context.to_logged_in(),
                    WorkspaceChangeFeatureFlagsUseCase(
                        time_provider=time_provider,
                        invocation_recorder=invocation_recorder,
                        progress_reporter_factory=progress_reporter_factory,
                        auth_token_stamper=auth_token_stamper,
                        domain_storage_engine=domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                        global_properties=global_properties,
                    ),
                ),
                WorkspaceShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    WorkspaceLoadUseCase(auth_token_stamper, domain_storage_engine),
                ),
                InboxTaskCreate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    InboxTaskCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                InboxTaskArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    InboxTaskArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                InboxTaskChangeProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    InboxTaskChangeProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                InboxTaskAssociateWithBigPlan(
                    session_storage,
                    top_level_context.to_logged_in(),
                    InboxTaskAssociateWithBigPlanUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                InboxTaskRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    InboxTaskRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                InboxTaskUpdate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    InboxTaskUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                InboxTaskShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    InboxTaskFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                HabitCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                HabitArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                HabitChangeProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitChangeProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                HabitSuspend(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitSuspendUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                HabitUnsuspend(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitUnsuspendUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                HabitUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                HabitRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                HabitShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    HabitFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                ChoreCreate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ChoreArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ChoreChangeProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreChangeProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ChoreSuspend(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreSuspendUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ChoreUnsuspend(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreUnsuspendUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ChoreUpdate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ChoreRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ChoreShow(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    ChoreFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                BigPlanCreate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    BigPlanCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                BigPlanArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    BigPlanArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                BigPlanRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    BigPlanRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                BigPlanChangeProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    BigPlanChangeProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                BigPlanUpdate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    BigPlanUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                BigPlanShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    BigPlanFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                VacationCreate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    VacationCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                VacationArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    VacationArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                VacationUpdate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    VacationUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                VacationRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    VacationRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                VacationsShow(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    VacationFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                ProjectCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ProjectCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ProjectArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ProjectArchiveUseCase(
                        time_provider=time_provider,
                        invocation_recorder=invocation_recorder,
                        progress_reporter_factory=progress_reporter_factory,
                        auth_token_stamper=auth_token_stamper,
                        domain_storage_engine=domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ProjectUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ProjectUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                ProjectShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ProjectFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                ProjectRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    ProjectRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                SmartListsRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListTagCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListTagCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListTagArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListTagArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListTagUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListTagUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListTagRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListTagRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListItemCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListItemCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListItemArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListItemArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListItemUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListItemUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SmartListItemRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SmartListItemRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricChangeCollectionProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricChangeCollectionProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                MetricRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricEntryCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricEntryCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricEntryArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricEntryArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricEntryUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricEntryUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                MetricEntryRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    MetricEntryRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                PersonChangeCatchUpProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    PersonChangeCatchUpProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                PersonCreate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    PersonCreateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                PersonArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    PersonArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                PersonUpdate(
                    session_storage,
                    top_level_context.to_logged_in(),
                    PersonUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                PersonRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    PersonRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                PersonShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    PersonFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                SlackTaskArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SlackTaskArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SlackTaskRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SlackTaskRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SlackTaskUpdate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    SlackTaskUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SlackTaskChangeGenerationProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SlackTaskChangeGenerationProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                SlackTaskShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    SlackTaskFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                EmailTaskArchive(
                    session_storage,
                    top_level_context.to_logged_in(),
                    EmailTaskArchiveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                EmailTaskRemove(
                    session_storage,
                    top_level_context.to_logged_in(),
                    EmailTaskRemoveUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                EmailTaskUpdate(
                    global_properties,
                    session_storage,
                    top_level_context.to_logged_in(),
                    EmailTaskUpdateUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                EmailTaskChangeGenerationProject(
                    session_storage,
                    top_level_context.to_logged_in(),
                    EmailTaskChangeGenerationProjectUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
                ),
                EmailTaskShow(
                    session_storage,
                    top_level_context.to_logged_in(),
                    EmailTaskFindUseCase(auth_token_stamper, domain_storage_engine),
                ),
                # Test Helper Commands
                TestHelperClearAll(
                    session_storage,
                    ClearAllUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine,
                        usecase_storage_engine,
                        global_properties,
                    ),
                ),
                TestHelperNuke(
                    NukeUseCase(
                        EmptyProgressReporterFactory(),
                        sqlite_connection,
                        domain_storage_engine,
                    ),
                ),
            ]
        )

    parser = argparse.ArgumentParser(description=global_properties.description)
    parser.add_argument(
        "--version",
        dest="just_show_version",
        action="store_const",
        default=False,
        const=True,
        help="Show the version of the application",
    )

    subparsers = parser.add_subparsers(
        dest="subparser_name",
        help="Sub-command help",
        metavar="{command}",
    )

    for command in commands:
        if (
            command.should_appear_in_global_help
            and (
                top_level_info.user is None
                or command.is_allowed_for_user(top_level_info.user)
            )
            and (
                top_level_info.workspace is None
                or command.is_allowed_for_workspace(top_level_info.workspace)
            )
        ):
            command_parser = subparsers.add_parser(
                command.name(),
                help=command.description(),
                description=command.description(),
            )
        else:
            command_parser = subparsers.add_parser(
                command.name(),
                description=command.description(),
            )
        command.build_parser(command_parser)

    try:
        args = parser.parse_args(sys.argv[1:])

        if args.just_show_version:
            print(f"{global_properties.description} {global_properties.version}")
            return

        for command in commands:
            if args.subparser_name != command.name():
                continue

            with progress_reporter_factory.envelope(
                command.should_have_streaming_progress_report, command.name(), args
            ):
                await command.run(args)

            command_postscript = command.get_postscript()
            if command_postscript is not None:
                postscript_panel = Panel(
                    command_postscript, title="PS.", title_align="left"
                )
                console.print(postscript_panel)

            break
    except SessionInfoNotFoundError:
        print(
            f"There doesn't seem to be a workspace. Please run '{Initialize.name()}' or '{Login.name()}' to create a workspace!",
        )
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(1)
    except InputValidationError as err:
        print("Looks like there's something wrong with the command's arguments:")
        print(f"  {err}")
        sys.exit(1)
    except FeatureUnavailableError as err:
        print(f"{err}")
        sys.exit(1)
    except UserAlreadyExistsError:
        print("A user with the same identity already seems to exist here!")
        print("Please try creating another user.")
        sys.exit(1)
    except ExpiredAuthTokenError:
        print(
            f"Your session seems to be expired! Please run '{Login.name()}' to login."
        )
        sys.exit(1)
    except InvalidLoginCredentialsError:
        print("The user and/or password are invalid!")
        print("You can:")
        print(f" * Run `{Login.name()}` to login.")
        print(f" * Run '{Initialize.name()}' to create a user and workspace!")
        print(f" * Run '{ResetPassword.name()}' to reset your password!")
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(1)
    except ProjectInSignificantUseError as err:
        print(f"The selected project is still being used. Reason: {err}")
        print("Please select a backup project via --backup-project-id")
        sys.exit(1)
    except LeafEntityNotFoundError as err:
        print(str(err))
        sys.exit(1)
    except InvalidAuthTokenError:
        print(
            f"Your session seems to be invalid! Please run '{Initialize.name()}' or '{Login.name()}' to fix this!"
        )
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)
    except ConnectionPrepareError as err:
        print("A connection to the database couldn't be established!")
        print("Check if the database path exists")
        print(err.__traceback__)
        sys.exit(2)
    except UserNotFoundError:
        print(
            f"The user you're trying to operate as does't seem to exist! Please run `{Initialize.name()}` to create a user and workspace."
        )
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)
    except WorkspaceNotFoundError:
        print(
            f"The workspace you're trying to operate in does't seem to exist! Please run `{Initialize.name()}` to create a user and workspace."
        )
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)
    finally:
        try:
            await sqlite_connection.dispose()
        finally:
            pass
        try:
            await aio_session.close()
        finally:
            pass


# coverage.process_startup()  # type: ignore

if __name__ == "__main__":
    asyncio.run(main())
