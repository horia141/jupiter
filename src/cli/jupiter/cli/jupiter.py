"""The CLI entry-point for Jupiter."""
import asyncio
import logging
import sys
from typing import cast

import aiohttp
import jupiter.core.domain
from jupiter.core.framework.base.timestamp import Timestamp
import jupiter.core.use_cases
from jupiter.core.use_cases.auth.reset_password import ResetPasswordResult, ResetPasswordUseCase
from jupiter.core.use_cases.gen.do import GenDoUseCase
from jupiter.core.use_cases.gen.load_runs import GenLoadRunsResult, GenLoadRunsUseCase
from jupiter.core.use_cases.search import SearchResult, SearchUseCase
from jupiter.cli.command.gen_show import GenShow
from jupiter.cli.command.reset_password import ResetPassword
from jupiter.cli.command.search import Search
from jupiter.cli.command.command import CliApp
from jupiter.cli.command.initialize import Initialize
from jupiter.cli.command.login import Login
from jupiter.cli.command.rendering import RichConsoleProgressReporterFactory, boolean_to_rich_text, date_with_label_to_rich_text, entity_id_to_rich_text, entity_summary_snippet_to_rich_text, entity_tag_to_rich_text, event_source_to_rich_text, period_to_rich_text, sync_target_to_rich_text
from jupiter.cli.session_storage import SessionInfoNotFoundError, SessionStorage
from jupiter.cli.top_level_context import TopLevelContext
from jupiter.core.domain.auth.auth_token import (
    ExpiredAuthTokenError,
    InvalidAuthTokenError,
)
from rich.text import Text
from rich.tree import Tree
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
from jupiter.core.framework.repository import EntityNotFoundError
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
from jupiter.core.use_cases.infra.persistent_mutation_use_case_recoder import (
    PersistentMutationUseCaseInvocationRecorder,
)
from jupiter.core.use_cases.infra.realms import ModuleExplorerRealmCodecRegistry
from jupiter.core.use_cases.infra.use_cases import AppGuestUseCaseSession
from jupiter.core.use_cases.init import InitUseCase
from jupiter.core.use_cases.load_top_level_info import (
    LoadTopLevelInfoArgs,
    LoadTopLevelInfoUseCase,
)
from jupiter.core.use_cases.login import InvalidLoginCredentialsError, LoginUseCase
from jupiter.core.utils.global_properties import build_global_properties
from jupiter.core.utils.progress_reporter import (
    NoOpProgressReporterFactory,
)
from jupiter.core.utils.time_provider import TimeProvider
from rich.console import Console

# import coverage


async def main() -> None:
    """Application main function."""
    logging.disable()

    time_provider = TimeProvider()

    global_properties = build_global_properties()

    realm_codec_registry = ModuleExplorerRealmCodecRegistry.build_from_module_root(
        jupiter.core.domain, jupiter.core.use_cases
    )

    sqlite_connection = SqliteConnection(
        SqliteConnection.Config(
            global_properties.sqlite_db_url,
            global_properties.alembic_ini_path,
            global_properties.alembic_migrations_path,
        ),
    )

    domain_storage_engine = SqliteDomainStorageEngine(
        realm_codec_registry, sqlite_connection
    )
    search_storage_engine = SqliteSearchStorageEngine(
        realm_codec_registry, sqlite_connection
    )
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

    cli_app = CliApp(
        global_properties=global_properties,
        top_level_context=top_level_context,
        console=console,
        progress_reporter_factory=progress_reporter_factory,
        realm_codec_registry=realm_codec_registry,
        session_storage=session_storage,
    )

    cli_app.add_command(
        Initialize(
            realm_codec_registry=realm_codec_registry,
            session_storage=session_storage,
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
    )
    cli_app.add_command(
        Login(
            realm_codec_registry=realm_codec_registry,
            session_storage=session_storage,
            use_case=LoginUseCase(
                auth_token_stamper,
                domain_storage_engine,
            ),
        ),
    )

    if top_level_info.user is not None and top_level_info.workspace is not None:
        cli_app.add_use_case(
            ChangePasswordUseCase(
                time_provider=time_provider,
                invocation_recorder=invocation_recorder,
                progress_reporter_factory=progress_reporter_factory,
                auth_token_stamper=auth_token_stamper,
                domain_storage_engine=domain_storage_engine,
                search_storage_engine=search_storage_engine,
            )
        )
        cli_app.add_command(
            ResetPassword(
                realm_codec_registry=realm_codec_registry,
                session_storage=session_storage,
                use_case=ResetPasswordUseCase(
                    time_provider=time_provider,
                    invocation_recorder=invocation_recorder,
                    progress_reporter_factory=NoOpProgressReporterFactory(),
                    auth_token_stamper=auth_token_stamper,
                    storage_engine=domain_storage_engine,
                ),
                renderer=None
            )
        )
        cli_app.add_command(
            Search(
                realm_codec_registry=realm_codec_registry,
                session_storage=session_storage,
                top_level_context=top_level_context.to_logged_in(),
                use_case=SearchUseCase(
                    time_provider=time_provider,
                    auth_token_stamper=auth_token_stamper,
                    domain_storage_engine=domain_storage_engine,
                    search_storage_engine=search_storage_engine,
                ),
                renderer=None
            ))
        cli_app.add_use_case(
            GenDoUseCase(
                        time_provider,
                        invocation_recorder,
                        progress_reporter_factory,
                        auth_token_stamper,
                        domain_storage_engine,
                        search_storage_engine=search_storage_engine,
                    ),
        )
        cli_app.add_command(
            GenShow(
                realm_codec_registry=realm_codec_registry,
                session_storage=session_storage,
                top_level_context=top_level_context.to_logged_in(),
                use_case=GenLoadRunsUseCase(
                    auth_token_stamper,
                    domain_storage_engine,
                ),
                renderer=None
            )
        )

    # commands: List[Command] = no_session_command

    # if top_level_info.user is not None and top_level_info.workspace is not None:
    #     commands.extend(
    #         [
    # Complex commands.
    #             Report(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ReportUseCase(
    #                     time_provider, auth_token_stamper, domain_storage_engine
    #                 ),
    #             ),
    #             GCDo(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 GCDoUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             GCShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 GCLoadRunsUseCase(
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                 ),
    #             ),
    #             Pomodoro(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 NoOpUseCase(
    #                     auth_token_stamper=auth_token_stamper,
    #                     storage_engine=domain_storage_engine,
    #                 ),
    #             ),
    #             Logout(session_storage=session_storage),
    #             # CRUD Commands.
    #             UserUpdate(
    #                 realm_codec_registry=realm_codec_registry,
    #                 session_storage=session_storage,
    #                 top_level_context=top_level_context.to_logged_in(),
    #                 use_case=UserUpdateUseCase(
    #                     time_provider=time_provider,
    #                     invocation_recorder=invocation_recorder,
    #                     progress_reporter_factory=progress_reporter_factory,
    #                     auth_token_stamper=auth_token_stamper,
    #                     domain_storage_engine=domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             UserChangeFeatureFlags(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 UserChangeFeatureFlagsUseCase(
    #                     time_provider=time_provider,
    #                     invocation_recorder=invocation_recorder,
    #                     progress_reporter_factory=progress_reporter_factory,
    #                     auth_token_stamper=auth_token_stamper,
    #                     domain_storage_engine=domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                     global_properties=global_properties,
    #                 ),
    #             ),
    #             UserShow(
    #                 realm_codec_registry=realm_codec_registry,
    #                 session_storage=session_storage,
    #                 top_level_context=top_level_context.to_logged_in(),
    #                 use_case=UserLoadUseCase(
    #                     auth_token_stamper=auth_token_stamper,
    #                     storage_engine=domain_storage_engine,
    #                     time_provider=time_provider,
    #                 ),
    #             ),
    #             WorkspaceUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 WorkspaceUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             WorkspaceChangeDefaultProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 WorkspaceChangeDefaultProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             WorkspaceChangeFeatureFlags(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 WorkspaceChangeFeatureFlagsUseCase(
    #                     time_provider=time_provider,
    #                     invocation_recorder=invocation_recorder,
    #                     progress_reporter_factory=progress_reporter_factory,
    #                     auth_token_stamper=auth_token_stamper,
    #                     domain_storage_engine=domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                     global_properties=global_properties,
    #                 ),
    #             ),
    #             WorkspaceShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 WorkspaceLoadUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             InboxTaskCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 InboxTaskCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             InboxTaskArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 InboxTaskArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             InboxTaskChangeProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 InboxTaskChangeProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             InboxTaskAssociateWithBigPlan(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 InboxTaskAssociateWithBigPlanUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             InboxTaskRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 InboxTaskRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             InboxTaskUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 InboxTaskUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             InboxTaskShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 InboxTaskFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             HabitCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             HabitArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             HabitChangeProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitChangeProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             HabitSuspend(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitSuspendUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             HabitUnsuspend(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitUnsuspendUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             HabitUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             HabitRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             HabitShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 HabitFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             ChoreCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ChoreArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ChoreChangeProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreChangeProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ChoreSuspend(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreSuspendUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ChoreUnsuspend(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreUnsuspendUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ChoreUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ChoreRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ChoreShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ChoreFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             BigPlanCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 BigPlanCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             BigPlanArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 BigPlanArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             BigPlanRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 BigPlanRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             BigPlanChangeProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 BigPlanChangeProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             BigPlanUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 BigPlanUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             BigPlanShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 BigPlanFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             VacationCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 VacationCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             VacationArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 VacationArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             VacationUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 VacationUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             VacationRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 VacationRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             VacationsShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 VacationFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             ProjectCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ProjectCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ProjectArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ProjectArchiveUseCase(
    #                     time_provider=time_provider,
    #                     invocation_recorder=invocation_recorder,
    #                     progress_reporter_factory=progress_reporter_factory,
    #                     auth_token_stamper=auth_token_stamper,
    #                     domain_storage_engine=domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ProjectUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ProjectUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             ProjectShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ProjectFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             ProjectRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 ProjectRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             SmartListsRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListTagCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListTagCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListTagArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListTagArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListTagUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListTagUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListTagRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListTagRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListItemCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListItemCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListItemArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListItemArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListItemUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListItemUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SmartListItemRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SmartListItemRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricChangeCollectionProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricChangeCollectionProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             MetricRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricEntryCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricEntryCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricEntryArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricEntryArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricEntryUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricEntryUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             MetricEntryRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 MetricEntryRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             PersonChangeCatchUpProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 PersonChangeCatchUpProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             PersonCreate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 PersonCreateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             PersonArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 PersonArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             PersonUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 PersonUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             PersonRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 PersonRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             PersonShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 PersonFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             SlackTaskArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SlackTaskArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SlackTaskRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SlackTaskRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SlackTaskUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SlackTaskUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SlackTaskChangeGenerationProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SlackTaskChangeGenerationProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             SlackTaskShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 SlackTaskFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             EmailTaskArchive(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 EmailTaskArchiveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             EmailTaskRemove(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 EmailTaskRemoveUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             EmailTaskUpdate(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 EmailTaskUpdateUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             EmailTaskChangeGenerationProject(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 EmailTaskChangeGenerationProjectUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine=search_storage_engine,
    #                 ),
    #             ),
    #             EmailTaskShow(
    #                 realm_codec_registry,
    #                 session_storage,
    #                 top_level_context.to_logged_in(),
    #                 EmailTaskFindUseCase(auth_token_stamper, domain_storage_engine),
    #             ),
    #             # Test Helper Commands
    #             TestHelperClearAll(
    #                 session_storage,
    #                 ClearAllUseCase(
    #                     time_provider,
    #                     invocation_recorder,
    #                     progress_reporter_factory,
    #                     auth_token_stamper,
    #                     domain_storage_engine,
    #                     search_storage_engine,
    #                     usecase_storage_engine,
    #                     global_properties,
    #                 ),
    #             ),
    #             TestHelperNuke(
    #                 NukeUseCase(
    #                     EmptyProgressReporterFactory(),
    #                     sqlite_connection,
    #                     domain_storage_engine,
    #                 ),
    #             ),
    #         ]
    #     )

    # parser = argparse.ArgumentParser(description=global_properties.description)
    # parser.add_argument(
    #     "--version",
    #     dest="just_show_version",
    #     action="store_const",
    #     default=False,
    #     const=True,
    #     help="Show the version of the application",
    # )

    # subparsers = parser.add_subparsers(
    #     dest="subparser_name",
    #     help="Sub-command help",
    #     metavar="{command}",
    # )

    # for command in commands:
    #     if (
    #         command.should_appear_in_global_help
    #         and (
    #             top_level_info.user is None
    #             or command.is_allowed_for_user(top_level_info.user)
    #         )
    #         and (
    #             top_level_info.workspace is None
    #             or command.is_allowed_for_workspace(top_level_info.workspace)
    #         )
    #     ):
    #         command_parser = subparsers.add_parser(
    #             command.name(),
    #             help=command.description(),
    #             description=command.description(),
    #         )
    #     else:
    #         command_parser = subparsers.add_parser(
    #             command.name(),
    #             description=command.description(),
    #         )
    #     command.build_parser(command_parser)

    try:
        await cli_app.run(sys.argv)
    except SessionInfoNotFoundError:
        print(
            "There doesn't seem to be a workspace. Please run 'init' or 'login' to create a workspace!",
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
        print("Your session seems to be expired! Please run 'login' to login.")
        sys.exit(1)
    except InvalidLoginCredentialsError:
        print("The user and/or password are invalid!")
        print("You can:")
        print(" * Run `login` to login.")
        print(" * Run 'init' to create a user and workspace!")
        print(" * Run 'reset-password' to reset your password!")
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(1)
    except ProjectInSignificantUseError as err:
        print(f"The selected project is still being used. Reason: {err}")
        print("Please select a backup project via --backup-project-id")
        sys.exit(1)
    except InvalidAuthTokenError:
        print(
            "Your session seems to be invalid! Please run 'init' or 'login' to fix this!"
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
            "The user you're trying to operate as does't seem to exist! Please run `init` to create a user and workspace."
        )
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)
    except WorkspaceNotFoundError:
        print(
            "The workspace you're trying to operate in does't seem to exist! Please run `init` to create a user and workspace."
        )
        print(
            f"For more information checkout: {global_properties.docs_init_workspace_url}",
        )
        sys.exit(2)
    except EntityNotFoundError as err:
        print(str(err))
        sys.exit(1)
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

