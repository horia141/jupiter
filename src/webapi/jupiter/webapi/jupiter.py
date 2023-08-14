"""The Jupiter Web RPC API."""
import asyncio
import signal
from types import FrameType
from typing import Annotated, Any, Callable, Dict, Union

import aiohttp
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.types import DecoratedCallable
from jupiter.core.domain.auth.auth_token import (
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from jupiter.core.domain.auth.auth_token_ext import AuthTokenExt
from jupiter.core.domain.auth.infra.auth_token_stamper import AuthTokenStamper
from jupiter.core.domain.auth.password_plain import PasswordPlain
from jupiter.core.domain.email_address import EmailAddress
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
from jupiter.core.framework.secure import secure_fn
from jupiter.core.repository.sqlite.connection import SqliteConnection
from jupiter.core.repository.sqlite.domain.storage_engine import (
    SqliteDomainStorageEngine,
    SqliteSearchStorageEngine,
)
from jupiter.core.repository.sqlite.use_case.storage_engine import (
    SqliteUseCaseStorageEngine,
)
from jupiter.core.use_cases.auth.change_password import (
    ChangePasswordArgs,
    ChangePasswordUseCase,
)
from jupiter.core.use_cases.auth.reset_password import (
    ResetPasswordArgs,
    ResetPasswordResult,
    ResetPasswordUseCase,
)
from jupiter.core.use_cases.big_plans.archive import (
    BigPlanArchiveArgs,
    BigPlanArchiveUseCase,
)
from jupiter.core.use_cases.big_plans.change_project import (
    BigPlanChangeProjectArgs,
    BigPlanChangeProjectUseCase,
)
from jupiter.core.use_cases.big_plans.create import (
    BigPlanCreateArgs,
    BigPlanCreateResult,
    BigPlanCreateUseCase,
)
from jupiter.core.use_cases.big_plans.find import (
    BigPlanFindArgs,
    BigPlanFindResult,
    BigPlanFindUseCase,
)
from jupiter.core.use_cases.big_plans.load import (
    BigPlanLoadArgs,
    BigPlanLoadResult,
    BigPlanLoadUseCase,
)
from jupiter.core.use_cases.big_plans.update import (
    BigPlanUpdateArgs,
    BigPlanUpdateUseCase,
)
from jupiter.core.use_cases.chores.archive import ChoreArchiveArgs, ChoreArchiveUseCase
from jupiter.core.use_cases.chores.change_project import (
    ChoreChangeProjectArgs,
    ChoreChangeProjectUseCase,
)
from jupiter.core.use_cases.chores.create import (
    ChoreCreateArgs,
    ChoreCreateResult,
    ChoreCreateUseCase,
)
from jupiter.core.use_cases.chores.find import (
    ChoreFindArgs,
    ChoreFindResult,
    ChoreFindUseCase,
)
from jupiter.core.use_cases.chores.load import (
    ChoreLoadArgs,
    ChoreLoadResult,
    ChoreLoadUseCase,
)
from jupiter.core.use_cases.chores.suspend import ChoreSuspendArgs, ChoreSuspendUseCase
from jupiter.core.use_cases.chores.unsuspend import (
    ChoreUnsuspendArgs,
    ChoreUnsuspendUseCase,
)
from jupiter.core.use_cases.chores.update import ChoreUpdateArgs, ChoreUpdateUseCase
from jupiter.core.use_cases.gc import GCArgs, GCUseCase
from jupiter.core.use_cases.gen import GenArgs, GenUseCase
from jupiter.core.use_cases.get_summaries import (
    GetSummariesArgs,
    GetSummariesResult,
    GetSummariesUseCase,
)
from jupiter.core.use_cases.habits.archive import HabitArchiveArgs, HabitArchiveUseCase
from jupiter.core.use_cases.habits.change_project import (
    HabitChangeProjectArgs,
    HabitChangeProjectUseCase,
)
from jupiter.core.use_cases.habits.create import (
    HabitCreateArgs,
    HabitCreateResult,
    HabitCreateUseCase,
)
from jupiter.core.use_cases.habits.find import (
    HabitFindArgs,
    HabitFindResult,
    HabitFindUseCase,
)
from jupiter.core.use_cases.habits.load import (
    HabitLoadArgs,
    HabitLoadResult,
    HabitLoadUseCase,
)
from jupiter.core.use_cases.habits.suspend import HabitSuspendArgs, HabitSuspendUseCase
from jupiter.core.use_cases.habits.unsuspend import (
    HabitUnsuspendArgs,
    HabitUnsuspendUseCase,
)
from jupiter.core.use_cases.habits.update import HabitUpdateArgs, HabitUpdateUseCase
from jupiter.core.use_cases.inbox_tasks.archive import (
    InboxTaskArchiveArgs,
    InboxTaskArchiveUseCase,
)
from jupiter.core.use_cases.inbox_tasks.associate_with_big_plan import (
    InboxTaskAssociateWithBigPlanArgs,
    InboxTaskAssociateWithBigPlanUseCase,
)
from jupiter.core.use_cases.inbox_tasks.change_project import (
    InboxTaskChangeProjectArgs,
    InboxTaskChangeProjectUseCase,
)
from jupiter.core.use_cases.inbox_tasks.create import (
    InboxTaskCreateArgs,
    InboxTaskCreateResult,
    InboxTaskCreateUseCase,
)
from jupiter.core.use_cases.inbox_tasks.find import (
    InboxTaskFindArgs,
    InboxTaskFindResult,
    InboxTaskFindUseCase,
)
from jupiter.core.use_cases.inbox_tasks.load import (
    InboxTaskLoadArgs,
    InboxTaskLoadResult,
    InboxTaskLoadUseCase,
)
from jupiter.core.use_cases.inbox_tasks.update import (
    InboxTaskUpdateArgs,
    InboxTaskUpdateUseCase,
)
from jupiter.core.use_cases.infra.persistent_mutation_use_case_recoder import (
    PersistentMutationUseCaseInvocationRecorder,
)
from jupiter.core.use_cases.infra.use_cases import (
    AppGuestUseCaseSession,
    AppLoggedInUseCaseSession,
)
from jupiter.core.use_cases.init import InitArgs, InitResult, InitUseCase
from jupiter.core.use_cases.load_progress_reporter_token import (
    LoadProgressReporterTokenArgs,
    LoadProgressReporterTokenResult,
    LoadProgressReporterTokenUseCase,
)
from jupiter.core.use_cases.load_top_level_info import (
    LoadTopLevelInfoArgs,
    LoadTopLevelInfoResult,
    LoadTopLevelInfoUseCase,
)
from jupiter.core.use_cases.login import (
    InvalidLoginCredentialsError,
    LoginArgs,
    LoginResult,
    LoginUseCase,
)
from jupiter.core.use_cases.metrics.archive import (
    MetricArchiveArgs,
    MetricArchiveUseCase,
)
from jupiter.core.use_cases.metrics.change_collection_project import (
    MetricChangeCollectionProjectArgs,
    MetricChangeCollectionProjectUseCase,
)
from jupiter.core.use_cases.metrics.create import (
    MetricCreateArgs,
    MetricCreateResult,
    MetricCreateUseCase,
)
from jupiter.core.use_cases.metrics.entry.archive import (
    MetricEntryArchiveArgs,
    MetricEntryArchiveUseCase,
)
from jupiter.core.use_cases.metrics.entry.create import (
    MetricEntryCreateArgs,
    MetricEntryCreateResult,
    MetricEntryCreateUseCase,
)
from jupiter.core.use_cases.metrics.entry.load import (
    MetricEntryLoadArgs,
    MetricEntryLoadResult,
    MetricEntryLoadUseCase,
)
from jupiter.core.use_cases.metrics.entry.update import (
    MetricEntryUpdateArgs,
    MetricEntryUpdateUseCase,
)
from jupiter.core.use_cases.metrics.find import (
    MetricFindArgs,
    MetricFindResult,
    MetricFindUseCase,
)
from jupiter.core.use_cases.metrics.load import (
    MetricLoadArgs,
    MetricLoadResult,
    MetricLoadUseCase,
)
from jupiter.core.use_cases.metrics.load_settings import (
    MetricLoadSettingsArgs,
    MetricLoadSettingsResult,
    MetricLoadSettingsUseCase,
)
from jupiter.core.use_cases.metrics.update import MetricUpdateArgs, MetricUpdateUseCase
from jupiter.core.use_cases.persons.archive import (
    PersonArchiveArgs,
    PersonArchiveUseCase,
)
from jupiter.core.use_cases.persons.change_catch_up_project import (
    PersonChangeCatchUpProjectArgs,
    PersonChangeCatchUpProjectUseCase,
)
from jupiter.core.use_cases.persons.create import (
    PersonCreateArgs,
    PersonCreateResult,
    PersonCreateUseCase,
)
from jupiter.core.use_cases.persons.find import (
    PersonFindArgs,
    PersonFindResult,
    PersonFindUseCase,
)
from jupiter.core.use_cases.persons.load import (
    PersonLoadArgs,
    PersonLoadResult,
    PersonLoadUseCase,
)
from jupiter.core.use_cases.persons.load_settings import (
    PersonLoadSettingsArgs,
    PersonLoadSettingsResult,
    PersonLoadSettingsUseCase,
)
from jupiter.core.use_cases.persons.update import PersonUpdateArgs, PersonUpdateUseCase
from jupiter.core.use_cases.projects.archive import (
    ProjectArchiveArgs,
    ProjectArchiveUseCase,
)
from jupiter.core.use_cases.projects.create import (
    ProjectCreateArgs,
    ProjectCreateResult,
    ProjectCreateUseCase,
)
from jupiter.core.use_cases.projects.find import (
    ProjectFindArgs,
    ProjectFindResult,
    ProjectFindUseCase,
)
from jupiter.core.use_cases.projects.load import (
    ProjectLoadArgs,
    ProjectLoadResult,
    ProjectLoadUseCase,
)
from jupiter.core.use_cases.projects.update import (
    ProjectUpdateArgs,
    ProjectUpdateUseCase,
)
from jupiter.core.use_cases.push_integrations.email.archive import (
    EmailTaskArchiveArgs,
    EmailTaskArchiveUseCase,
)
from jupiter.core.use_cases.push_integrations.email.change_generation_project import (
    EmailTaskChangeGenerationProjectArgs,
    EmailTaskChangeGenerationProjectUseCase,
)
from jupiter.core.use_cases.push_integrations.email.find import (
    EmailTaskFindArgs,
    EmailTaskFindResult,
    EmailTaskFindUseCase,
)
from jupiter.core.use_cases.push_integrations.email.load import (
    EmailTaskLoadArgs,
    EmailTaskLoadResult,
    EmailTaskLoadUseCase,
)
from jupiter.core.use_cases.push_integrations.email.load_settings import (
    EmailTaskLoadSettingsArgs,
    EmailTaskLoadSettingsResult,
    EmailTaskLoadSettingsUseCase,
)
from jupiter.core.use_cases.push_integrations.email.update import (
    EmailTaskUpdateArgs,
    EmailTaskUpdateUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.archive import (
    SlackTaskArchiveArgs,
    SlackTaskArchiveUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.change_generation_project import (
    SlackTaskChangeGenerationProjectArgs,
    SlackTaskChangeGenerationProjectUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.find import (
    SlackTaskFindArgs,
    SlackTaskFindResult,
    SlackTaskFindUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.load import (
    SlackTaskLoadArgs,
    SlackTaskLoadResult,
    SlackTaskLoadUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.load_settings import (
    SlackTaskLoadSettingsArgs,
    SlackTaskLoadSettingsResult,
    SlackTaskLoadSettingsUseCase,
)
from jupiter.core.use_cases.push_integrations.slack.update import (
    SlackTaskUpdateArgs,
    SlackTaskUpdateUseCase,
)
from jupiter.core.use_cases.report import ReportArgs, ReportResult, ReportUseCase
from jupiter.core.use_cases.search import SearchArgs, SearchResult, SearchUseCase
from jupiter.core.use_cases.smart_lists.archive import (
    SmartListArchiveArgs,
    SmartListArchiveUseCase,
)
from jupiter.core.use_cases.smart_lists.create import (
    SmartListCreateArgs,
    SmartListCreateResult,
    SmartListCreateUseCase,
)
from jupiter.core.use_cases.smart_lists.find import (
    SmartListFindArgs,
    SmartListFindResult,
    SmartListFindUseCase,
)
from jupiter.core.use_cases.smart_lists.item.archive import (
    SmartListItemArchiveArgs,
    SmartListItemArchiveUseCase,
)
from jupiter.core.use_cases.smart_lists.item.create import (
    SmartListItemCreateArgs,
    SmartListItemCreateResult,
    SmartListItemCreateUseCase,
)
from jupiter.core.use_cases.smart_lists.item.load import (
    SmartListItemLoadArgs,
    SmartListItemLoadResult,
    SmartListItemLoadUseCase,
)
from jupiter.core.use_cases.smart_lists.item.update import (
    SmartListItemUpdateArgs,
    SmartListItemUpdateUseCase,
)
from jupiter.core.use_cases.smart_lists.load import (
    SmartListLoadArgs,
    SmartListLoadResult,
    SmartListLoadUseCase,
)
from jupiter.core.use_cases.smart_lists.tag.archive import (
    SmartListTagArchiveArgs,
    SmartListTagArchiveUseCase,
)
from jupiter.core.use_cases.smart_lists.tag.create import (
    SmartListTagCreateArgs,
    SmartListTagCreateResult,
    SmartListTagCreateUseCase,
)
from jupiter.core.use_cases.smart_lists.tag.load import (
    SmartListTagLoadArgs,
    SmartListTagLoadResult,
    SmartListTagLoadUseCase,
)
from jupiter.core.use_cases.smart_lists.tag.update import (
    SmartListTagUpdateArgs,
    SmartListTagUpdateUseCase,
)
from jupiter.core.use_cases.smart_lists.update import (
    SmartListUpdateArgs,
    SmartListUpdateUseCase,
)
from jupiter.core.use_cases.user.load import (
    UserLoadArgs,
    UserLoadResult,
    UserLoadUseCase,
)
from jupiter.core.use_cases.user.update import UserUpdateArgs, UserUpdateUseCase
from jupiter.core.use_cases.vacations.archive import (
    VacationArchiveArgs,
    VacationArchiveUseCase,
)
from jupiter.core.use_cases.vacations.create import (
    VacationCreateArgs,
    VacationCreateResult,
    VacationCreateUseCase,
)
from jupiter.core.use_cases.vacations.find import (
    VacationFindArgs,
    VacationFindResult,
    VacationFindUseCase,
)
from jupiter.core.use_cases.vacations.load import (
    VacationLoadArgs,
    VacationLoadResult,
    VacationLoadUseCase,
)
from jupiter.core.use_cases.vacations.update import (
    VacationUpdateArgs,
    VacationUpdateUseCase,
)
from jupiter.core.use_cases.workspaces.change_default_project import (
    WorkspaceChangeDefaultProjectArgs,
    WorkspaceChangeDefaultProjectUseCase,
)
from jupiter.core.use_cases.workspaces.change_feature_flags import (
    WorkspaceChangeFeatureFlagsArgs,
    WorkspaceChangeFeatureFlagsUseCase,
)
from jupiter.core.use_cases.workspaces.load import (
    WorkspaceLoadArgs,
    WorkspaceLoadResult,
    WorkspaceLoadUseCase,
)
from jupiter.core.use_cases.workspaces.update import (
    WorkspaceUpdateArgs,
    WorkspaceUpdateUseCase,
)
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.core.utils.progress_reporter import NoOpProgressReporterFactory
from jupiter.webapi.time_provider import PerRequestTimeProvider
from jupiter.webapi.websocket_progress_reporter import WebsocketProgressReporterFactory
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

time_provider = PerRequestTimeProvider()

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
search_storage_engine = SqliteSearchStorageEngine(sqlite_connection)
usecase_storage_engine = SqliteUseCaseStorageEngine(sqlite_connection)

auth_token_stamper = AuthTokenStamper(
    auth_token_secret=global_properties.auth_token_secret,
    time_provider=time_provider,
)

aio_session = aiohttp.ClientSession()

progress_reporter_factory = WebsocketProgressReporterFactory()

invocation_recorder = PersistentMutationUseCaseInvocationRecorder(
    storage_engine=usecase_storage_engine,
)

init_use_case = InitUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=NoOpProgressReporterFactory(),
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
    global_properties=global_properties,
)

login_use_case = LoginUseCase(
    storage_engine=domain_storage_engine,
    auth_token_stamper=auth_token_stamper,
)

auth_change_password_use_case = ChangePasswordUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)

auth_reset_password_use_case = ResetPasswordUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=NoOpProgressReporterFactory(),
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
)

load_top_level_info_use_case = LoadTopLevelInfoUseCase(
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
    global_properties=global_properties,
)

load_progress_reporter_token_use_case = LoadProgressReporterTokenUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

get_summaries_use_case = GetSummariesUseCase(
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
)

search_use_case = SearchUseCase(
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)

gen_use_case = GenUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)

gc_use_case = GCUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)

user_update_use_case = UserUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)

user_load_use_case = UserLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

workspace_update_use_case = WorkspaceUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
workspace_change_default_project_use_case = WorkspaceChangeDefaultProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
workspace_change_feature_flags_use_case = WorkspaceChangeFeatureFlagsUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
    global_properties=global_properties,
)
workspace_load_use_case = WorkspaceLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

report_use_case = ReportUseCase(
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
)

big_plan_create_use_case = BigPlanCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
big_plan_archive_use_case = BigPlanArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
big_plan_update_use_case = BigPlanUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
big_plan_change_project_use_case = BigPlanChangeProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
big_plan_load_use_case = BigPlanLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
big_plan_find_use_case = BigPlanFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

chore_create_use_case = ChoreCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
chore_archive_use_case = ChoreArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
chore_update_use_case = ChoreUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
chore_change_project_use_case = ChoreChangeProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
chore_suspend_use_case = ChoreSuspendUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
chore_unsuspend_use_case = ChoreUnsuspendUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
chore_load_use_case = ChoreLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
chore_find_use_case = ChoreFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

habit_create_use_case = HabitCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
habit_archive_use_case = HabitArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
habit_update_use_case = HabitUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
habit_change_project_use_case = HabitChangeProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
habit_suspend_use_case = HabitSuspendUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
habit_unsuspend_use_case = HabitUnsuspendUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
habit_load_use_case = HabitLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
habit_find_use_case = HabitFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

inbox_task_create_use_case = InboxTaskCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
inbox_task_archive_use_case = InboxTaskArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
inbox_task_update_use_case = InboxTaskUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
inbox_task_change_project_use_case = InboxTaskChangeProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
inbox_task_associate_with_big_plan = InboxTaskAssociateWithBigPlanUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
inbox_task_load_use_case = InboxTaskLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
inbox_task_find_use_case = InboxTaskFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

metric_entry_create_use_case = MetricEntryCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
metric_entry_update_use_case = MetricEntryUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
metric_entry_archive_use_case = MetricEntryArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
metric_entry_load_use_case = MetricEntryLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

metric_create_use_case = MetricCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
metric_archive_use_case = MetricArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
metric_update_use_case = MetricUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
metric_load_settings_use_case = MetricLoadSettingsUseCase(
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
)
metric_change_collection_project_use_case = MetricChangeCollectionProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
metric_load_use_case = MetricLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
metric_find_use_case = MetricFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

person_create_use_case = PersonCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
person_archive_use_case = PersonArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
person_update_use_case = PersonUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
person_load_settings_use_case = PersonLoadSettingsUseCase(
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
)
person_change_catch_up_project_use_case = PersonChangeCatchUpProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
person_load_use_case = PersonLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
person_find_use_case = PersonFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

project_create_use_case = ProjectCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
project_archive_use_case = ProjectArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
project_update_use_case = ProjectUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
project_load_use_case = ProjectLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
project_find_use_case = ProjectFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

email_task_archive_use_case = EmailTaskArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
email_task_update_use_case = EmailTaskUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
email_task_load_settings_use_case = EmailTaskLoadSettingsUseCase(
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
)
email_task_change_generation_project_use_case = EmailTaskChangeGenerationProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
email_task_load_use_case = EmailTaskLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
email_task_find_use_case = EmailTaskFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

slack_task_archive_use_case = SlackTaskArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
slack_task_update_use_case = SlackTaskUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
slack_task_load_settings_use_case = SlackTaskLoadSettingsUseCase(
    auth_token_stamper=auth_token_stamper,
    storage_engine=domain_storage_engine,
)
slack_task_change_generation_project_use_case = SlackTaskChangeGenerationProjectUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
slack_task_load_use_case = SlackTaskLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
slack_task_find_use_case = SlackTaskFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

smart_list_item_create_use_case = SmartListItemCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_item_archive_use_case = SmartListItemArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_item_update_use_case = SmartListItemUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_item_load_use_case = SmartListItemLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
smart_list_tag_create_use_case = SmartListTagCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_tag_archive_use_case = SmartListTagArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_tag_load_use_case = SmartListTagLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
smart_list_tag_update_use_case = SmartListTagUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_create_use_case = SmartListCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_archive_use_case = SmartListArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_update_use_case = SmartListUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
smart_list_load_use_case = SmartListLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
smart_list_find_use_case = SmartListFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

vacation_create_use_case = VacationCreateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
vacation_archive_use_case = VacationArchiveUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
vacation_update_use_case = VacationUpdateUseCase(
    time_provider=time_provider,
    invocation_recorder=invocation_recorder,
    progress_reporter_factory=progress_reporter_factory,
    auth_token_stamper=auth_token_stamper,
    domain_storage_engine=domain_storage_engine,
    search_storage_engine=search_storage_engine,
)
vacation_load_use_case = VacationLoadUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)
vacation_find_use_case = VacationFindUseCase(
    auth_token_stamper=auth_token_stamper, storage_engine=domain_storage_engine
)

standard_responses: Dict[Union[int, str], Dict[str, Any]] = {  # type: ignore
    410: {"description": "Workspace Or User Not Found", "content": {"plain/text": {}}},
    406: {"description": "Feature Not Available", "content": {"plain/text": {}}},
}


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate a OpenAPI unique id from just the route name."""
    return f"{route.name}"


app = FastAPI(
    generate_unique_id_function=custom_generate_unique_id,
    openapi_url="/openapi.json" if global_properties.env.is_development else None,
    docs_url="/docs" if global_properties.env.is_development else None,
    redoc_url="/redoc" if global_properties.env.is_development else None,
)


@app.middleware("http")
async def time_provider_middleware(request: Request, call_next: DecoratedCallable) -> Callable[[DecoratedCallable], DecoratedCallable]:  # type: ignore
    """Middleware which provides the time for a particular request on a thread."""
    time_provider.set_request_time()
    return await call_next(request)  # type: ignore


@app.exception_handler(InputValidationError)
async def input_validation_error_handler(
    _request: Request, exc: InputValidationError
) -> JSONResponse:
    """Transform InputValidationErrors from the core to the same thing FastAPI would do."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": [
                {
                    "loc": [
                        "body",
                    ],
                    "msg": f"{exc}",
                    "type": "value_error.inputvalidationerror",
                },
            ],
        },
    )


@app.exception_handler(FeatureUnavailableError)
async def feature_unavailable_error_handler(
    _request: Request, exc: FeatureUnavailableError
) -> JSONResponse:
    """Transform FeatureUnavailableError from the core to the same thing FastAPI would do."""
    return JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=f"{exc}",
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_error_handler(
    _request: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    """Transform UserAlreadyExistsError from the core to the same thing FastAPI would do."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": [
                {
                    "loc": [
                        "body",
                    ],
                    "msg": f"{exc}",
                    "type": "value_error.useralreadyexistserror",
                },
            ],
        },
    )


@app.exception_handler(ExpiredAuthTokenError)
async def expired_auth_token_error_handler(
    _request: Request, exc: ExpiredAuthTokenError
) -> JSONResponse:
    """Transform ExpiredAuthTokenError from the core to the same thing FastAPI would do."""
    return JSONResponse(
        status_code=status.HTTP_426_UPGRADE_REQUIRED,
        content="Your session seems to be expired",
    )


@app.exception_handler(InvalidLoginCredentialsError)
async def invalid_login_credentials_error_handler(
    _request: Request, exc: InvalidLoginCredentialsError
) -> JSONResponse:
    """Transform InvalidLoginCredentialsError from the core to the same thing FastAPI would do."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": [
                {
                    "loc": [
                        "body",
                    ],
                    "msg": "User email or password invalid",
                    "type": "value_error.invalidlogincredentialserror",
                },
            ],
        },
    )


@app.exception_handler(ProjectInSignificantUseError)
async def project_in_significant_use_error_handler(
    _request: Request, exc: ProjectInSignificantUseError
) -> JSONResponse:
    """Transform ProjectInSignificantUseError from the core to the same thing FastAPI would do."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": [
                {
                    "loc": [
                        "body",
                    ],
                    "msg": f"Cannot remove because: {exc}",
                    "type": "value_error.projectinsignificantuserror",
                },
            ],
        },
    )


@app.exception_handler(LeafEntityNotFoundError)
async def leaf_entity_not_found_error_handler(
    _request: Request,
    _exc: LeafEntityNotFoundError,
) -> PlainTextResponse:
    """Transform LeafEntityNotFoundError to something that signals clients the entity does not exist."""
    return PlainTextResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content="Entity does not exist",
    )


@app.exception_handler(InvalidAuthTokenError)
async def invalid_auth_token_error(
    _request: Request, exc: InvalidAuthTokenError
) -> JSONResponse:
    """Transform InvalidAuthTokenError from the core to the same thing FastAPI would do."""
    return JSONResponse(
        status_code=status.HTTP_426_UPGRADE_REQUIRED,
        content="Your session token seems to be busted",
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_error(
    _request: Request,
    _exc: UserNotFoundError,
) -> PlainTextResponse:
    """Transform UserNotFoundError to something that signals clients the app is in a not-ready state."""
    return PlainTextResponse(
        status_code=status.HTTP_410_GONE,
        content="User does not exist",
    )


@app.exception_handler(WorkspaceNotFoundError)
async def workspace_not_found_error_handler(
    _request: Request,
    _exc: WorkspaceNotFoundError,
) -> PlainTextResponse:
    """Transform WorkspaceNotFoundErrors to something that signals clients the app is in a not-ready state."""
    return PlainTextResponse(
        status_code=status.HTTP_410_GONE,
        content="Workspace does not exist",
    )


@app.on_event("startup")
async def startup_event() -> None:
    """The startup event for the whole service."""
    await sqlite_connection.prepare()
    # aio_session = aiohttp.ClientSession()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """The shutdown event for the whole service."""
    try:
        await sqlite_connection.dispose()
    finally:
        pass
    try:
        await aio_session.close()
    finally:
        pass
    try:
        await progress_reporter_factory.unregister_all_websockets()
    finally:
        pass


websocket_should_close = False


def signal_websocket_to_close(_signum: int, _frame: FrameType | None) -> None:
    """Called when the server receives a SIGTERM to signal to the progress reporter to close its websockets."""
    # This is needed in order to allow FastAPI to proceed with its shutdown procedure.
    global websocket_should_close
    websocket_should_close = True


signal.signal(signal.SIGTERM, signal_websocket_to_close)

oauth2_guest_scheme = OAuth2PasswordBearer(tokenUrl="guest-login", auto_error=False)
oauth2_logged_in_schemea = OAuth2PasswordBearer(tokenUrl="old-skool-login")


def construct_guest_auth_token_ext(
    token_raw: Annotated[str | None, Depends(oauth2_guest_scheme)]
) -> AuthTokenExt | None:
    """Construct a Token from the raw token string."""
    return AuthTokenExt.from_raw(token_raw) if token_raw else None


def construct_logged_in_auth_token_ext(
    token_raw: Annotated[str, Depends(oauth2_logged_in_schemea)]
) -> AuthTokenExt:
    """Construct a Token from the raw token string."""
    return AuthTokenExt.from_raw(token_raw)


def construct_guest_session(
    auth_token_ext: Annotated[
        AuthTokenExt | None, Depends(construct_guest_auth_token_ext)
    ]
) -> AppGuestUseCaseSession:
    """Construct a GuestSession from the AuthTokenExt."""
    return AppGuestUseCaseSession(auth_token_ext)


def construct_logged_in_session(
    auth_token_ext: Annotated[AuthTokenExt, Depends(construct_logged_in_auth_token_ext)]
) -> AppLoggedInUseCaseSession:
    """Construct a LoggedInSession from the AuthTokenExt."""
    return AppLoggedInUseCaseSession(auth_token_ext)


GuestSession = Annotated[AppGuestUseCaseSession, Depends(construct_guest_session)]
LoggedInSession = Annotated[
    AppLoggedInUseCaseSession, Depends(construct_logged_in_session)
]


@app.websocket("/progress-reporter")
async def progress_reporter_websocket(websocket: WebSocket, token: str | None) -> None:
    """Handle the whole lifecycle of the progress reporter websocket."""
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    try:
        progress_reporter_token_ext = AuthTokenExt.from_raw(token)
        progress_reporter_token = (
            auth_token_stamper.verify_auth_token_progress_reporter(
                progress_reporter_token_ext
            )
        )
    except (InputValidationError, ExpiredAuthTokenError, InvalidAuthTokenError) as err:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from err

    await websocket.accept()
    await progress_reporter_factory.register_socket(
        websocket, progress_reporter_token.user_ref_id
    )
    # Seems like this just needs to stay alive for the socket to not expire ...
    try:
        while True:
            await asyncio.sleep(1)  # Sleep one second
            global websocket_should_close
            if websocket_should_close:
                await progress_reporter_factory.unregister_websocket(
                    progress_reporter_token.user_ref_id
                )
                return
    except WebSocketDisconnect:
        await progress_reporter_factory.unregister_websocket(
            progress_reporter_token.user_ref_id
        )


@app.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz() -> None:
    """Health check endpoint."""
    return None


@secure_fn
@app.post("/old-skool-login")
async def old_skool_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Dict[str, str]:
    """Login via OAuth2 password flow and return an auth token."""
    email_address = EmailAddress.from_raw(form_data.username)
    password = PasswordPlain.from_raw(form_data.password)

    result = await login_use_case.execute(
        AppGuestUseCaseSession(),
        LoginArgs(email_address=email_address, password=password),
    )

    return {
        "access_token": result.auth_token_ext.auth_token_str,
        "token_type": "bearer",
    }


@secure_fn
@app.post(
    "/init",
    response_model=InitResult,
    tags=["init"],
    responses=standard_responses,
)
async def init(args: InitArgs, session: GuestSession) -> InitResult:
    """Initialise a new workspace."""
    return await init_use_case.execute(session, args)


@secure_fn
@app.post(
    "/login", response_model=LoginResult, tags=["login"], responses=standard_responses
)
async def login(args: LoginArgs, session: GuestSession) -> LoginResult:
    """Login to a workspace."""
    return await login_use_case.execute(session, args)


@secure_fn
@app.post(
    "/auth/change-password",
    response_model=None,
    tags=["auth"],
    responses=standard_responses,
)
async def change_password(args: ChangePasswordArgs, session: LoggedInSession) -> None:
    """Change password."""
    await auth_change_password_use_case.execute(session, args)


@secure_fn
@app.post(
    "/auth/reset-password",
    response_model=ResetPasswordResult,
    tags=["auth"],
    responses=standard_responses,
)
async def reset_password(
    args: ResetPasswordArgs, session: GuestSession
) -> ResetPasswordResult:
    """Reset password."""
    return await auth_reset_password_use_case.execute(session, args)


@app.post(
    "/load-top-level-info",
    response_model=LoadTopLevelInfoResult,
    tags=["load-top-level-info"],
    responses=standard_responses,
)
async def load_top_level_info(
    args: LoadTopLevelInfoArgs, session: GuestSession
) -> LoadTopLevelInfoResult:
    """Load a user and workspace if they exist and other assorted data."""
    return await load_top_level_info_use_case.execute(session, args)


@app.post(
    "/load-progress-reporter-token",
    response_model=LoadProgressReporterTokenResult,
    tags=["load-progress-reporter-token"],
    responses=standard_responses,
)
async def load_progress_reporter_token(
    args: LoadProgressReporterTokenArgs, session: LoggedInSession
) -> LoadProgressReporterTokenResult:
    """Load a temporary access token useful for reading progress reporter updates."""
    return await load_progress_reporter_token_use_case.execute(session, args)


@app.post(
    "/get-summaries",
    response_model=GetSummariesResult,
    tags=["get-summaries"],
    responses=standard_responses,
)
async def get_summaries(
    args: GetSummariesArgs, session: LoggedInSession
) -> GetSummariesResult:
    """Get summaries about entities."""
    return await get_summaries_use_case.execute(session, args)


@app.post(
    "/search",
    response_model=SearchResult,
    tags=["search"],
    responses=standard_responses,
)
async def search(args: SearchArgs, session: LoggedInSession) -> SearchResult:
    """Search entities."""
    return await search_use_case.execute(session, args)


@app.post("/gen", response_model=None, tags=["gen"], responses=standard_responses)
async def gen(args: GenArgs, session: LoggedInSession) -> None:
    """Generate inbox tasks."""
    await gen_use_case.execute(session, args)


@app.post("/gc", response_model=None, tags=["gc"], responses=standard_responses)
async def garbage_collect(args: GCArgs, session: LoggedInSession) -> None:
    """Garbage collect."""
    await gc_use_case.execute(session, args)


@app.post(
    "/report",
    response_model=ReportResult,
    tags=["report"],
    responses=standard_responses,
)
async def report(args: ReportArgs, session: LoggedInSession) -> ReportResult:
    """Report."""
    return await report_use_case.execute(session, args)


@app.post(
    "/user/update",
    response_model=None,
    tags=["user"],
    responses=standard_responses,
)
async def update_user(args: UserUpdateArgs, session: LoggedInSession) -> None:
    """Update a user."""
    await user_update_use_case.execute(session, args)


@app.post(
    "/user/load",
    response_model=UserLoadResult,
    tags=["user"],
    responses=standard_responses,
)
async def load_user(args: UserLoadArgs, session: LoggedInSession) -> UserLoadResult:
    """Load a user."""
    return await user_load_use_case.execute(session, args)


@app.post(
    "/workspace/update",
    response_model=None,
    tags=["workspace"],
    responses=standard_responses,
)
async def update_workspace(args: WorkspaceUpdateArgs, session: LoggedInSession) -> None:
    """Update a workspace."""
    await workspace_update_use_case.execute(session, args)


@app.post(
    "/workspace/change-default-project",
    response_model=None,
    tags=["workspace"],
    responses=standard_responses,
)
async def change_workspace_default_project(
    args: WorkspaceChangeDefaultProjectArgs, session: LoggedInSession
) -> None:
    """Change the default project for a workspace."""
    await workspace_change_default_project_use_case.execute(session, args)


@app.post(
    "/workspace/change-feature-flags",
    response_model=None,
    tags=["workspace"],
    responses=standard_responses,
)
async def change_workspace_feature_flags(
    args: WorkspaceChangeFeatureFlagsArgs, session: LoggedInSession
) -> None:
    """Change the feature flags for a workspace."""
    await workspace_change_feature_flags_use_case.execute(session, args)


@app.post(
    "/workspace/load",
    response_model=WorkspaceLoadResult,
    tags=["workspace"],
    responses=standard_responses,
)
async def load_workspace(
    args: WorkspaceLoadArgs, session: LoggedInSession
) -> WorkspaceLoadResult:
    """Load a workspace."""
    return await workspace_load_use_case.execute(session, args)


@app.post(
    "/big-plan/create",
    response_model=BigPlanCreateResult,
    tags=["big-plan"],
    responses=standard_responses,
)
async def create_big_plan(
    args: BigPlanCreateArgs, session: LoggedInSession
) -> BigPlanCreateResult:
    """Create a big plan."""
    return await big_plan_create_use_case.execute(session, args)


@app.post(
    "/big-plan/archive",
    response_model=None,
    tags=["big-plan"],
    responses=standard_responses,
)
async def archive_big_plan(args: BigPlanArchiveArgs, session: LoggedInSession) -> None:
    """Archive a big plan."""
    await big_plan_archive_use_case.execute(session, args)


@app.post(
    "/big-plan/update",
    response_model=None,
    tags=["big-plan"],
    responses=standard_responses,
)
async def update_big_plan(args: BigPlanUpdateArgs, session: LoggedInSession) -> None:
    """Update a big plan."""
    await big_plan_update_use_case.execute(session, args)


@app.post(
    "/big-plan/change-project",
    response_model=None,
    tags=["big-plan"],
    responses=standard_responses,
)
async def change_big_plan_project(
    args: BigPlanChangeProjectArgs, session: LoggedInSession
) -> None:
    """Change the project for a big plan."""
    await big_plan_change_project_use_case.execute(session, args)


@app.post(
    "/big-plan/load",
    response_model=BigPlanLoadResult,
    tags=["big-plan"],
    responses=standard_responses,
)
async def load_big_plan(
    args: BigPlanLoadArgs, session: LoggedInSession
) -> BigPlanLoadResult:
    """Load a big plan."""
    return await big_plan_load_use_case.execute(session, args)


@app.post(
    "/big-plan/find",
    response_model=BigPlanFindResult,
    tags=["big-plan"],
    responses=standard_responses,
)
async def find_big_plan(
    args: BigPlanFindArgs, session: LoggedInSession
) -> BigPlanFindResult:
    """Find all big plans, filtering by id."""
    return await big_plan_find_use_case.execute(session, args)


@app.post(
    "/chore/create",
    response_model=ChoreCreateResult,
    tags=["chore"],
    responses=standard_responses,
)
async def create_chore(
    args: ChoreCreateArgs, session: LoggedInSession
) -> ChoreCreateResult:
    """Create a chore."""
    return await chore_create_use_case.execute(session, args)


@app.post(
    "/chore/archive",
    response_model=None,
    tags=["chore"],
    responses=standard_responses,
)
async def archive_chore(args: ChoreArchiveArgs, session: LoggedInSession) -> None:
    """Archive a chore."""
    await chore_archive_use_case.execute(session, args)


@app.post(
    "/chore/update",
    response_model=None,
    tags=["chore"],
    responses=standard_responses,
)
async def update_chore(args: ChoreUpdateArgs, session: LoggedInSession) -> None:
    """Update a chore."""
    await chore_update_use_case.execute(session, args)


@app.post(
    "/chore/change-project",
    response_model=None,
    tags=["chore"],
    responses=standard_responses,
)
async def change_chore_project(
    args: ChoreChangeProjectArgs, session: LoggedInSession
) -> None:
    """Change the project for a chore."""
    await chore_change_project_use_case.execute(session, args)


@app.post(
    "/chore/suspend",
    response_model=None,
    tags=["chore"],
    responses=standard_responses,
)
async def suspend_chore(args: ChoreSuspendArgs, session: LoggedInSession) -> None:
    """Suspend a chore."""
    await chore_suspend_use_case.execute(session, args)


@app.post(
    "/chore/unsuspend",
    response_model=None,
    tags=["chore"],
    responses=standard_responses,
)
async def unsuspend_chore(args: ChoreUnsuspendArgs, session: LoggedInSession) -> None:
    """Unsuspend a chore."""
    await chore_unsuspend_use_case.execute(session, args)


@app.post(
    "/chore/load",
    response_model=ChoreLoadResult,
    tags=["chore"],
    responses=standard_responses,
)
async def load_chore(args: ChoreLoadArgs, session: LoggedInSession) -> ChoreLoadResult:
    """Load a chore."""
    return await chore_load_use_case.execute(session, args)


@app.post(
    "/chore/find",
    response_model=ChoreFindResult,
    tags=["chore"],
    responses=standard_responses,
)
async def find_chore(args: ChoreFindArgs, session: LoggedInSession) -> ChoreFindResult:
    """Find all chores, filtering by id.."""
    return await chore_find_use_case.execute(session, args)


@app.post(
    "/habit/create",
    response_model=HabitCreateResult,
    tags=["habit"],
    responses=standard_responses,
)
async def create_habit(
    args: HabitCreateArgs, session: LoggedInSession
) -> HabitCreateResult:
    """Create a habit."""
    return await habit_create_use_case.execute(session, args)


@app.post(
    "/habit/archive",
    response_model=None,
    tags=["habit"],
    responses=standard_responses,
)
async def archive_habit(args: HabitArchiveArgs, session: LoggedInSession) -> None:
    """Archive a habit."""
    await habit_archive_use_case.execute(session, args)


@app.post(
    "/habit/update",
    response_model=None,
    tags=["habit"],
    responses=standard_responses,
)
async def update_habit(args: HabitUpdateArgs, session: LoggedInSession) -> None:
    """Update a habit."""
    await habit_update_use_case.execute(session, args)


@app.post(
    "/habit/change-project",
    response_model=None,
    tags=["habit"],
    responses=standard_responses,
)
async def change_habit_project(
    args: HabitChangeProjectArgs, session: LoggedInSession
) -> None:
    """Change the project for a habit."""
    await habit_change_project_use_case.execute(session, args)


@app.post(
    "/habit/suspend",
    response_model=None,
    tags=["habit"],
    responses=standard_responses,
)
async def suspend_habit(args: HabitSuspendArgs, session: LoggedInSession) -> None:
    """Suspend a habit."""
    await habit_suspend_use_case.execute(session, args)


@app.post(
    "/habit/unsuspend",
    response_model=None,
    tags=["habit"],
    responses=standard_responses,
)
async def unsuspend_habit(args: HabitUnsuspendArgs, session: LoggedInSession) -> None:
    """Unsuspend a habit."""
    await habit_unsuspend_use_case.execute(session, args)


@app.post(
    "/habit/load",
    response_model=HabitLoadResult,
    tags=["habit"],
    responses=standard_responses,
)
async def load_habit(args: HabitLoadArgs, session: LoggedInSession) -> HabitLoadResult:
    """Load a habit."""
    return await habit_load_use_case.execute(session, args)


@app.post(
    "/habit/find",
    response_model=HabitFindResult,
    tags=["habit"],
    responses=standard_responses,
)
async def find_habit(args: HabitFindArgs, session: LoggedInSession) -> HabitFindResult:
    """Find all habits, filtering by id.."""
    return await habit_find_use_case.execute(session, args)


@app.post(
    "/inbox-task/create",
    response_model=InboxTaskCreateResult,
    tags=["inbox-task"],
    responses=standard_responses,
)
async def create_inbox_task(
    args: InboxTaskCreateArgs, session: LoggedInSession
) -> InboxTaskCreateResult:
    """Create a inbox task."""
    return await inbox_task_create_use_case.execute(session, args)


@app.post(
    "/inbox-task/archive",
    response_model=None,
    tags=["inbox-task"],
    responses=standard_responses,
)
async def archive_inbox_task(
    args: InboxTaskArchiveArgs, session: LoggedInSession
) -> None:
    """Archive a inbox task."""
    await inbox_task_archive_use_case.execute(session, args)


@app.post(
    "/inbox-task/update",
    response_model=None,
    tags=["inbox-task"],
    responses=standard_responses,
)
async def update_inbox_task(
    args: InboxTaskUpdateArgs, session: LoggedInSession
) -> None:
    """Update a inbox task."""
    await inbox_task_update_use_case.execute(session, args)


@app.post(
    "/inbox-task/change-project",
    response_model=None,
    tags=["inbox-task"],
    responses=standard_responses,
)
async def change_inbox_task_project(
    args: InboxTaskChangeProjectArgs, session: LoggedInSession
) -> None:
    """Change the project for a inbox task."""
    await inbox_task_change_project_use_case.execute(session, args)


@app.post(
    "/inbox-task/associate-with-big-plan",
    response_model=None,
    tags=["inbox-task"],
    responses=standard_responses,
)
async def associate_inbox_task_with_big_plan(
    args: InboxTaskAssociateWithBigPlanArgs, session: LoggedInSession
) -> None:
    """Change the inbox task for a project."""
    await inbox_task_associate_with_big_plan.execute(session, args)


@app.post(
    "/inbox-task/load",
    response_model=InboxTaskLoadResult,
    tags=["inbox-task"],
    responses=standard_responses,
)
async def load_inbox_task(
    args: InboxTaskLoadArgs, session: LoggedInSession
) -> InboxTaskLoadResult:
    """Load a inbox task."""
    return await inbox_task_load_use_case.execute(session, args)


@app.post(
    "/inbox-task/find",
    response_model=InboxTaskFindResult,
    tags=["inbox-task"],
    responses=standard_responses,
)
async def find_inbox_task(
    args: InboxTaskFindArgs, session: LoggedInSession
) -> InboxTaskFindResult:
    """Find all inbox tasks, filtering by id."""
    return await inbox_task_find_use_case.execute(session, args)


@app.post(
    "/metric/entry/create",
    response_model=MetricEntryCreateResult,
    tags=["metric"],
    responses=standard_responses,
)
async def create_metric_entry(
    args: MetricEntryCreateArgs, session: LoggedInSession
) -> MetricEntryCreateResult:
    """Create a metric entry."""
    return await metric_entry_create_use_case.execute(session, args)


@app.post(
    "/metric/entry/archive",
    response_model=None,
    tags=["metric"],
    responses=standard_responses,
)
async def archive_metric_entry(
    args: MetricEntryArchiveArgs, session: LoggedInSession
) -> None:
    """Archive a metric entry."""
    await metric_entry_archive_use_case.execute(session, args)


@app.post(
    "/metric/entry/update",
    response_model=None,
    tags=["metric"],
    responses=standard_responses,
)
async def update_metric_entry(
    args: MetricEntryUpdateArgs, session: LoggedInSession
) -> None:
    """Update a metric entry."""
    await metric_entry_update_use_case.execute(session, args)


@app.post(
    "/metric/entry/load",
    response_model=MetricEntryLoadResult,
    tags=["metric"],
    responses=standard_responses,
)
async def load_metric_entry(
    args: MetricEntryLoadArgs, session: LoggedInSession
) -> MetricEntryLoadResult:
    """Load a metric entry."""
    return await metric_entry_load_use_case.execute(session, args)


@app.post(
    "/metric/create",
    response_model=MetricCreateResult,
    tags=["metric"],
    responses=standard_responses,
)
async def create_metric(
    args: MetricCreateArgs, session: LoggedInSession
) -> MetricCreateResult:
    """Create a metric."""
    return await metric_create_use_case.execute(session, args)


@app.post(
    "/metric/archive",
    response_model=None,
    tags=["metric"],
    responses=standard_responses,
)
async def archive_metric(args: MetricArchiveArgs, session: LoggedInSession) -> None:
    """Archive a metric."""
    await metric_archive_use_case.execute(session, args)


@app.post(
    "/metric/update",
    response_model=None,
    tags=["metric"],
    responses=standard_responses,
)
async def update_metric(args: MetricUpdateArgs, session: LoggedInSession) -> None:
    """Update a metric."""
    await metric_update_use_case.execute(session, args)


@app.post(
    "/metric/load-settings",
    response_model=MetricLoadSettingsResult,
    tags=["metric"],
    responses=standard_responses,
)
async def load_metric_settings(
    args: MetricLoadSettingsArgs, session: LoggedInSession
) -> MetricLoadSettingsResult:
    """Load settings for metrics."""
    return await metric_load_settings_use_case.execute(session, args)


@app.post(
    "/metric/change-collection-project",
    response_model=None,
    tags=["metric"],
    responses=standard_responses,
)
async def change_metric_collection_project(
    args: MetricChangeCollectionProjectArgs, session: LoggedInSession
) -> None:
    """Change the collection project for metric."""
    await metric_change_collection_project_use_case.execute(session, args)


@app.post(
    "/metric/load",
    response_model=MetricLoadResult,
    tags=["metric"],
    responses=standard_responses,
)
async def load_metric(
    args: MetricLoadArgs, session: LoggedInSession
) -> MetricLoadResult:
    """Load a metric."""
    return await metric_load_use_case.execute(session, args)


@app.post(
    "/metric/find",
    response_model=MetricFindResult,
    tags=["metric"],
    responses=standard_responses,
)
async def find_metric(
    args: MetricFindArgs, session: LoggedInSession
) -> MetricFindResult:
    """Find all metrics, filtering by id."""
    return await metric_find_use_case.execute(session, args)


@app.post(
    "/person/create",
    response_model=PersonCreateResult,
    tags=["person"],
    responses=standard_responses,
)
async def create_person(
    args: PersonCreateArgs, session: LoggedInSession
) -> PersonCreateResult:
    """Create a person."""
    return await person_create_use_case.execute(session, args)


@app.post(
    "/person/archive",
    response_model=None,
    tags=["person"],
    responses=standard_responses,
)
async def archive_person(args: PersonArchiveArgs, session: LoggedInSession) -> None:
    """Archive a person."""
    await person_archive_use_case.execute(session, args)


@app.post(
    "/person/update",
    response_model=None,
    tags=["person"],
    responses=standard_responses,
)
async def update_person(args: PersonUpdateArgs, session: LoggedInSession) -> None:
    """Update a person."""
    await person_update_use_case.execute(session, args)


@app.post(
    "/person/load-settings",
    response_model=PersonLoadSettingsResult,
    tags=["person"],
    responses=standard_responses,
)
async def load_person_settings(
    args: PersonLoadSettingsArgs, session: LoggedInSession
) -> PersonLoadSettingsResult:
    """Change the catch up project for persons."""
    return await person_load_settings_use_case.execute(session, args)


@app.post(
    "/person/change-catch-up-project",
    response_model=None,
    tags=["person"],
    responses=standard_responses,
)
async def update_change_catch_up_project(
    args: PersonChangeCatchUpProjectArgs, session: LoggedInSession
) -> None:
    """Change the catch up project for persons."""
    await person_change_catch_up_project_use_case.execute(session, args)


@app.post(
    "/person/load",
    response_model=PersonLoadResult,
    tags=["person"],
    responses=standard_responses,
)
async def load_person(
    args: PersonLoadArgs, session: LoggedInSession
) -> PersonLoadResult:
    """Load a person, filtering by id."""
    return await person_load_use_case.execute(session, args)


@app.post(
    "/person/find",
    response_model=PersonFindResult,
    tags=["person"],
    responses=standard_responses,
)
async def find_person(
    args: PersonFindArgs, session: LoggedInSession
) -> PersonFindResult:
    """Find a person, filtering by id."""
    return await person_find_use_case.execute(session, args)


@app.post(
    "/project/create",
    response_model=ProjectCreateResult,
    tags=["project"],
    responses=standard_responses,
)
async def create_project(
    args: ProjectCreateArgs, session: LoggedInSession
) -> ProjectCreateResult:
    """Create a project."""
    return await project_create_use_case.execute(session, args)


@app.post(
    "/project/archive",
    response_model=None,
    tags=["project"],
    responses=standard_responses,
)
async def archive_project(args: ProjectArchiveArgs, session: LoggedInSession) -> None:
    """Create a project."""
    await project_archive_use_case.execute(session, args)


@app.post(
    "/project/update",
    response_model=None,
    tags=["project"],
    responses=standard_responses,
)
async def update_project(args: ProjectUpdateArgs, session: LoggedInSession) -> None:
    """Update a project."""
    await project_update_use_case.execute(session, args)


@app.post(
    "/project/load",
    response_model=ProjectLoadResult,
    tags=["project"],
    responses=standard_responses,
)
async def load_project(
    args: ProjectLoadArgs, session: LoggedInSession
) -> ProjectLoadResult:
    """Load a project, filtering by id."""
    return await project_load_use_case.execute(session, args)


@app.post(
    "/project/find",
    response_model=ProjectFindResult,
    tags=["project"],
    responses=standard_responses,
)
async def find_project(
    args: ProjectFindArgs, session: LoggedInSession
) -> ProjectFindResult:
    """Find a project, filtering by id."""
    return await project_find_use_case.execute(session, args)


@app.post(
    "/email-task/archive",
    response_model=None,
    tags=["email-task"],
    responses=standard_responses,
)
async def archive_email_task(
    args: EmailTaskArchiveArgs, session: LoggedInSession
) -> None:
    """Archive a email task."""
    await email_task_archive_use_case.execute(session, args)


@app.post(
    "/email-task/update",
    response_model=None,
    tags=["email-task"],
    responses=standard_responses,
)
async def update_email_task(
    args: EmailTaskUpdateArgs, session: LoggedInSession
) -> None:
    """Update a email task."""
    await email_task_update_use_case.execute(session, args)


@app.post(
    "/email-task/load-settings",
    response_model=EmailTaskLoadSettingsResult,
    tags=["email-task"],
    responses=standard_responses,
)
async def load_email_task_settings(
    args: EmailTaskLoadSettingsArgs, session: LoggedInSession
) -> EmailTaskLoadSettingsResult:
    """Change the project for a email task."""
    return await email_task_load_settings_use_case.execute(session, args)


@app.post(
    "/email-task/change-project",
    response_model=None,
    tags=["email-task"],
    responses=standard_responses,
)
async def change_email_task_generation_project(
    args: EmailTaskChangeGenerationProjectArgs, session: LoggedInSession
) -> None:
    """Change the project for a email task."""
    await email_task_change_generation_project_use_case.execute(session, args)


@app.post(
    "/email-task/load",
    response_model=EmailTaskLoadResult,
    tags=["email-task"],
    responses=standard_responses,
)
async def load_email_task(
    args: EmailTaskLoadArgs, session: LoggedInSession
) -> EmailTaskLoadResult:
    """Load an email task."""
    return await email_task_load_use_case.execute(session, args)


@app.post(
    "/email-task/find",
    response_model=EmailTaskFindResult,
    tags=["email-task"],
    responses=standard_responses,
)
async def find_email_task(
    args: EmailTaskFindArgs, session: LoggedInSession
) -> EmailTaskFindResult:
    """Find all email tasks, filtering by id."""
    return await email_task_find_use_case.execute(session, args)


@app.post(
    "/slack-task/archive",
    response_model=None,
    tags=["slack-task"],
    responses=standard_responses,
)
async def archive_slack_task(
    args: SlackTaskArchiveArgs, session: LoggedInSession
) -> None:
    """Archive a slack task."""
    await slack_task_archive_use_case.execute(session, args)


@app.post(
    "/slack-task/update",
    response_model=None,
    tags=["slack-task"],
    responses=standard_responses,
)
async def update_slack_task(
    args: SlackTaskUpdateArgs, session: LoggedInSession
) -> None:
    """Update a slack task."""
    await slack_task_update_use_case.execute(session, args)


@app.post(
    "/slack-task/load-settings",
    response_model=SlackTaskLoadSettingsResult,
    tags=["slack-task"],
    responses=standard_responses,
)
async def load_slack_task_settings(
    args: SlackTaskLoadSettingsArgs, session: LoggedInSession
) -> SlackTaskLoadSettingsResult:
    """Change the project for a slack task."""
    return await slack_task_load_settings_use_case.execute(session, args)


@app.post(
    "/slack-task/change-project",
    response_model=None,
    tags=["slack-task"],
    responses=standard_responses,
)
async def change_slack_task_generation_project(
    args: SlackTaskChangeGenerationProjectArgs, session: LoggedInSession
) -> None:
    """Change the project for a slack task."""
    await slack_task_change_generation_project_use_case.execute(session, args)


@app.post(
    "/slack-task/load",
    response_model=SlackTaskLoadResult,
    tags=["slack-task"],
    responses=standard_responses,
)
async def load_slack_task(
    args: SlackTaskLoadArgs, session: LoggedInSession
) -> SlackTaskLoadResult:
    """Load a slack task."""
    return await slack_task_load_use_case.execute(session, args)


@app.post(
    "/slack-task/find",
    response_model=SlackTaskFindResult,
    tags=["slack-task"],
    responses=standard_responses,
)
async def find_slack_task(
    args: SlackTaskFindArgs, session: LoggedInSession
) -> SlackTaskFindResult:
    """Find all slack tasks, filtering by id."""
    return await slack_task_find_use_case.execute(session, args)


@app.post(
    "/smart-list/item/create",
    response_model=SmartListItemCreateResult,
    tags=["smart-list"],
    responses=standard_responses,
)
async def create_smart_list_item(
    args: SmartListItemCreateArgs, session: LoggedInSession
) -> SmartListItemCreateResult:
    """Create a smart list item."""
    return await smart_list_item_create_use_case.execute(session, args)


@app.post(
    "/smart-list/item/archive",
    response_model=None,
    tags=["smart-list"],
    responses=standard_responses,
)
async def archive_smart_list_item(
    args: SmartListItemArchiveArgs, session: LoggedInSession
) -> None:
    """Archive a smart list item."""
    await smart_list_item_archive_use_case.execute(session, args)


@app.post(
    "/smart-list/item/update",
    response_model=None,
    tags=["smart-list"],
    responses=standard_responses,
)
async def update_smart_list_item(
    args: SmartListItemUpdateArgs, session: LoggedInSession
) -> None:
    """Update a smart list item."""
    await smart_list_item_update_use_case.execute(session, args)


@app.post(
    "/smart-list/item/load",
    response_model=SmartListItemLoadResult,
    tags=["smart-list"],
    responses=standard_responses,
)
async def load_smart_list_item(
    args: SmartListItemLoadArgs, session: LoggedInSession
) -> SmartListItemLoadResult:
    """Load a smart list item."""
    return await smart_list_item_load_use_case.execute(session, args)


@app.post(
    "/smart-list/tag/create",
    response_model=SmartListTagCreateResult,
    tags=["smart-list"],
    responses=standard_responses,
)
async def create_smart_list_tag(
    args: SmartListTagCreateArgs, session: LoggedInSession
) -> SmartListTagCreateResult:
    """Create a smart list tag."""
    return await smart_list_tag_create_use_case.execute(session, args)


@app.post(
    "/smart-list/tag/archive",
    response_model=None,
    tags=["smart-list"],
    responses=standard_responses,
)
async def archive_smart_list_tag(
    args: SmartListTagArchiveArgs, session: LoggedInSession
) -> None:
    """Archive a smart list tag."""
    await smart_list_tag_archive_use_case.execute(session, args)


@app.post(
    "/smart-list/tag/update",
    response_model=None,
    tags=["smart-list"],
    responses=standard_responses,
)
async def update_smart_list_tag(
    args: SmartListTagUpdateArgs, session: LoggedInSession
) -> None:
    """Update a smart list tag."""
    await smart_list_tag_update_use_case.execute(session, args)


@app.post(
    "/smart-list/tag/load",
    response_model=SmartListTagLoadResult,
    tags=["smart-list"],
    responses=standard_responses,
)
async def load_smart_list_tag(
    args: SmartListTagLoadArgs, session: LoggedInSession
) -> SmartListTagLoadResult:
    """Load a smart list tag."""
    return await smart_list_tag_load_use_case.execute(session, args)


@app.post(
    "/smart-list/create",
    response_model=SmartListCreateResult,
    tags=["smart-list"],
    responses=standard_responses,
)
async def create_smart_list(
    args: SmartListCreateArgs, session: LoggedInSession
) -> SmartListCreateResult:
    """Create a smart list."""
    return await smart_list_create_use_case.execute(session, args)


@app.post(
    "/smart-list/archive",
    response_model=None,
    tags=["smart-list"],
    responses=standard_responses,
)
async def archive_smart_list(
    args: SmartListArchiveArgs, session: LoggedInSession
) -> None:
    """Archive a smart list."""
    await smart_list_archive_use_case.execute(session, args)


@app.post(
    "/smart-list/update",
    response_model=None,
    tags=["smart-list"],
    responses=standard_responses,
)
async def update_smart_list(
    args: SmartListUpdateArgs, session: LoggedInSession
) -> None:
    """Update a smart list."""
    await smart_list_update_use_case.execute(session, args)


@app.post(
    "/smart-list/load",
    response_model=SmartListLoadResult,
    tags=["smart-list"],
    responses=standard_responses,
)
async def load_smart_list(
    args: SmartListLoadArgs, session: LoggedInSession
) -> SmartListLoadResult:
    """Load a smart list."""
    return await smart_list_load_use_case.execute(session, args)


@app.post(
    "/smart-list/find",
    response_model=SmartListFindResult,
    tags=["smart-list"],
    responses=standard_responses,
)
async def find_smart_list(
    args: SmartListFindArgs, session: LoggedInSession
) -> SmartListFindResult:
    """Find all smart lists, filtering by id."""
    return await smart_list_find_use_case.execute(session, args)


@app.post(
    "/vacation/create",
    response_model=VacationCreateResult,
    tags=["vacation"],
    responses=standard_responses,
)
async def create_vacation(
    args: VacationCreateArgs, session: LoggedInSession
) -> VacationCreateResult:
    """Create a vacation."""
    return await vacation_create_use_case.execute(session, args)


@app.post(
    "/vacation/archive",
    response_model=None,
    tags=["vacation"],
    responses=standard_responses,
)
async def archive_vacation(args: VacationArchiveArgs, session: LoggedInSession) -> None:
    """Archive a vacation."""
    await vacation_archive_use_case.execute(session, args)


@app.post(
    "/vacation/update",
    response_model=None,
    tags=["vacation"],
    responses=standard_responses,
)
async def update_vacation(args: VacationUpdateArgs, session: LoggedInSession) -> None:
    """Update a vacation."""
    await vacation_update_use_case.execute(session, args)


@app.post(
    "/vacation/load",
    response_model=VacationLoadResult,
    tags=["vacation"],
    responses=standard_responses,
)
async def load_vacation(
    args: VacationLoadArgs, session: LoggedInSession
) -> VacationLoadResult:
    """Load all vacations, filtering by id."""
    return await vacation_load_use_case.execute(session, args)


@app.post(
    "/vacation/find",
    response_model=VacationFindResult,
    tags=["vacation"],
    responses=standard_responses,
)
async def find_vacation(
    args: VacationFindArgs, session: LoggedInSession
) -> VacationFindResult:
    """Find all vacations, filtering by id."""
    return await vacation_find_use_case.execute(session, args)
