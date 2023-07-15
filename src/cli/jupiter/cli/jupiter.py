"""The CLI entry-point for Jupiter."""
import argparse
import asyncio
import logging
import sys

import aiohttp
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
from jupiter.cli.command.email_task_archive import EmailTaskArchive
from jupiter.cli.command.email_task_change_generation_project import (
    EmailTaskChangeGenerationProject,
)
from jupiter.cli.command.email_task_remove import EmailTaskRemove
from jupiter.cli.command.email_task_show import EmailTaskShow
from jupiter.cli.command.email_task_update import EmailTaskUpdate
from jupiter.cli.command.gc import GC
from jupiter.cli.command.gen import Gen
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
from jupiter.cli.command.workspace_show import WorkspaceShow
from jupiter.cli.command.workspace_update import WorkspaceUpdate
from jupiter.cli.session_storage import SessionInfoNotFoundError, SessionStorage
from jupiter.core.domain.auth.auth_token import (
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
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
from jupiter.core.use_cases.gc import GCUseCase
from jupiter.core.use_cases.gen import GenUseCase
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
from jupiter.core.use_cases.init import InitUseCase
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
from jupiter.core.use_cases.workspaces.load import WorkspaceLoadUseCase
from jupiter.core.use_cases.workspaces.update import WorkspaceUpdateUseCase
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.core.utils.noop_use_case import NoOpUseCase
from jupiter.core.utils.progress_reporter import (
    EmptyProgressReporterFactory,
    NoOpProgressReporterFactory,
)
from jupiter.core.utils.time_provider import TimeProvider

# import coverage
from rich.logging import RichHandler


async def main() -> None:
    """Application main function."""
    time_provider = TimeProvider()

    no_timezone_global_properties = build_global_properties()

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            no_timezone_global_properties.sqlite_db_url,
            no_timezone_global_properties.alembic_ini_path,
            no_timezone_global_properties.alembic_migrations_path,
        ),
    )

    global_properties = build_global_properties()

    domain_storage_engine = SqliteDomainStorageEngine(sqlite_connection)
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

    progress_reporter_factory = RichConsoleProgressReporterFactory()

    commands = {
        # Complex commands.
        Initialize(
            session_storage=session_storage,
            use_case=InitUseCase(
                time_provider,
                invocation_recorder,
                NoOpProgressReporterFactory(),
                auth_token_stamper,
                domain_storage_engine,
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
        Logout(session_storage=session_storage),
        AuthChangePassword(
            session_storage=session_storage,
            use_case=ChangePasswordUseCase(
                time_provider=time_provider,
                invocation_recorder=invocation_recorder,
                progress_reporter_factory=progress_reporter_factory,
                auth_token_stamper=auth_token_stamper,
                storage_engine=domain_storage_engine,
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
        Gen(
            global_properties,
            time_provider,
            session_storage,
            GenUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        Report(
            global_properties,
            time_provider,
            session_storage,
            ReportUseCase(auth_token_stamper, domain_storage_engine),
        ),
        GC(
            session_storage,
            GCUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        Pomodoro(
            session_storage,
            NoOpUseCase(
                auth_token_stamper=auth_token_stamper,
                storage_engine=domain_storage_engine,
            ),
        ),
        # CRUD Commands.
        UserUpdate(
            session_storage=session_storage,
            use_case=UserUpdateUseCase(
                time_provider=time_provider,
                invocation_recorder=invocation_recorder,
                progress_reporter_factory=progress_reporter_factory,
                auth_token_stamper=auth_token_stamper,
                storage_engine=domain_storage_engine,
            ),
        ),
        UserShow(
            session_storage=session_storage,
            use_case=UserLoadUseCase(
                auth_token_stamper=auth_token_stamper,
                storage_engine=domain_storage_engine,
            ),
        ),
        WorkspaceUpdate(
            session_storage,
            WorkspaceUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        WorkspaceChangeDefaultProject(
            session_storage,
            WorkspaceChangeDefaultProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        WorkspaceShow(
            session_storage,
            WorkspaceLoadUseCase(auth_token_stamper, domain_storage_engine),
        ),
        VacationCreate(
            global_properties,
            session_storage,
            VacationCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        VacationArchive(
            session_storage,
            VacationArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        VacationUpdate(
            global_properties,
            session_storage,
            VacationUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        VacationRemove(
            session_storage,
            VacationRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        VacationsShow(
            global_properties,
            session_storage,
            VacationFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        ProjectCreate(
            session_storage,
            ProjectCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ProjectArchive(
            session_storage,
            ProjectArchiveUseCase(
                time_provider=time_provider,
                invocation_recorder=invocation_recorder,
                progress_reporter_factory=progress_reporter_factory,
                auth_token_stamper=auth_token_stamper,
                storage_engine=domain_storage_engine,
            ),
        ),
        ProjectUpdate(
            session_storage,
            ProjectUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ProjectShow(
            session_storage,
            ProjectFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        ProjectRemove(
            session_storage,
            ProjectRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        InboxTaskCreate(
            global_properties,
            session_storage,
            InboxTaskCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        InboxTaskArchive(
            session_storage,
            InboxTaskArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        InboxTaskChangeProject(
            session_storage,
            InboxTaskChangeProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        InboxTaskAssociateWithBigPlan(
            session_storage,
            InboxTaskAssociateWithBigPlanUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        InboxTaskRemove(
            session_storage,
            InboxTaskRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        InboxTaskUpdate(
            global_properties,
            session_storage,
            InboxTaskUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        InboxTaskShow(
            session_storage,
            InboxTaskFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        HabitCreate(
            session_storage,
            HabitCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        HabitArchive(
            session_storage,
            HabitArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        HabitChangeProject(
            session_storage,
            HabitChangeProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        HabitSuspend(
            session_storage,
            HabitSuspendUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        HabitUnsuspend(
            session_storage,
            HabitUnsuspendUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        HabitUpdate(
            session_storage,
            HabitUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        HabitRemove(
            session_storage,
            HabitRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        HabitShow(
            session_storage, HabitFindUseCase(auth_token_stamper, domain_storage_engine)
        ),
        ChoreCreate(
            global_properties,
            session_storage,
            ChoreCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ChoreArchive(
            session_storage,
            ChoreArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ChoreChangeProject(
            session_storage,
            ChoreChangeProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ChoreSuspend(
            session_storage,
            ChoreSuspendUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ChoreUnsuspend(
            session_storage,
            ChoreUnsuspendUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ChoreUpdate(
            global_properties,
            session_storage,
            ChoreUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ChoreRemove(
            session_storage,
            ChoreRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        ChoreShow(
            global_properties,
            session_storage,
            ChoreFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        BigPlanCreate(
            global_properties,
            session_storage,
            BigPlanCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        BigPlanArchive(
            session_storage,
            BigPlanArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        BigPlanRemove(
            session_storage,
            BigPlanRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        BigPlanChangeProject(
            session_storage,
            BigPlanChangeProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        BigPlanUpdate(
            global_properties,
            session_storage,
            BigPlanUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        BigPlanShow(
            session_storage,
            BigPlanFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        SmartListCreate(
            session_storage,
            SmartListCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListArchive(
            session_storage,
            SmartListArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListUpdate(
            session_storage,
            SmartListUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListShow(
            session_storage,
            SmartListFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        SmartListsRemove(
            session_storage,
            SmartListRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListTagCreate(
            session_storage,
            SmartListTagCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListTagArchive(
            session_storage,
            SmartListTagArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListTagUpdate(
            session_storage,
            SmartListTagUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListTagRemove(
            session_storage,
            SmartListTagRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListItemCreate(
            session_storage,
            SmartListItemCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListItemArchive(
            session_storage,
            SmartListItemArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListItemUpdate(
            session_storage,
            SmartListItemUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SmartListItemRemove(
            session_storage,
            SmartListItemRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricChangeCollectionProject(
            session_storage,
            MetricChangeCollectionProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricCreate(
            session_storage,
            MetricCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricArchive(
            session_storage,
            MetricArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricUpdate(
            session_storage,
            MetricUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricShow(
            session_storage,
            MetricFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        MetricRemove(
            session_storage,
            MetricRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricEntryCreate(
            session_storage,
            MetricEntryCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricEntryArchive(
            session_storage,
            MetricEntryArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricEntryUpdate(
            session_storage,
            MetricEntryUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        MetricEntryRemove(
            session_storage,
            MetricEntryRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        PersonChangeCatchUpProject(
            session_storage,
            PersonChangeCatchUpProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        PersonCreate(
            session_storage,
            PersonCreateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        PersonArchive(
            session_storage,
            PersonArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        PersonUpdate(
            session_storage,
            PersonUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        PersonRemove(
            session_storage,
            PersonRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        PersonShow(
            session_storage,
            PersonFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        SlackTaskArchive(
            session_storage,
            SlackTaskArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SlackTaskRemove(
            session_storage,
            SlackTaskRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SlackTaskUpdate(
            global_properties,
            session_storage,
            SlackTaskUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SlackTaskChangeGenerationProject(
            session_storage,
            SlackTaskChangeGenerationProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        SlackTaskShow(
            session_storage,
            SlackTaskFindUseCase(auth_token_stamper, domain_storage_engine),
        ),
        EmailTaskArchive(
            session_storage,
            EmailTaskArchiveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        EmailTaskRemove(
            session_storage,
            EmailTaskRemoveUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        EmailTaskUpdate(
            global_properties,
            session_storage,
            EmailTaskUpdateUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        EmailTaskChangeGenerationProject(
            session_storage,
            EmailTaskChangeGenerationProjectUseCase(
                time_provider,
                invocation_recorder,
                progress_reporter_factory,
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
        EmailTaskShow(
            session_storage,
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

    subparsers = parser.add_subparsers(
        dest="subparser_name",
        help="Sub-command help",
        metavar="{command}",
    )

    for command in commands:
        if command.should_appear_in_global_help:
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

        logging.basicConfig(
            level=_map_log_level_to_log_class(args.min_log_level),
            format="%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                RichHandler(
                    rich_tracebacks=True,
                    markup=True,
                    log_time_format="%Y-%m-%d %H:%M:%S",
                ),
            ],
        )

        if not args.verbose_logging:
            for handler in logging.root.handlers:
                handler.addFilter(CommandsAndControllersLoggerFilter())

        await sqlite_connection.prepare()

        for command in commands:
            if args.subparser_name != command.name():
                continue

            with progress_reporter_factory.envelope(
                command.should_have_streaming_progress_report, command.name(), args
            ):
                await command.run(args)

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


class CommandsAndControllersLoggerFilter(logging.Filter):
    """A filter for commands and controllers."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        """Filtering the log records for commands."""
        if record.name.startswith("command."):
            return True
        return False


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


# coverage.process_startup()  # type: ignore

if __name__ == "__main__":
    asyncio.run(main())
