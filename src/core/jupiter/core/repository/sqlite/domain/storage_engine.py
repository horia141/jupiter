"""The real implementation of an engine."""
from contextlib import asynccontextmanager
from types import TracebackType
from typing import AsyncIterator, Final, Optional, Type

from jupiter.core.domain.auth.infra.auth_repository import AuthRepository
from jupiter.core.domain.big_plans.infra.big_plan_collection_repository import (
    BigPlanCollectionRepository,
)
from jupiter.core.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.core.domain.chores.infra.chore_collection_repository import (
    ChoreCollectionRepository,
)
from jupiter.core.domain.chores.infra.chore_repository import ChoreRepository
from jupiter.core.domain.fast_info_repository import FastInfoRepository
from jupiter.core.domain.habits.infra.habit_collection_repository import (
    HabitCollectionRepository,
)
from jupiter.core.domain.habits.infra.habit_repository import HabitRepository
from jupiter.core.domain.inbox_tasks.infra.inbox_task_collection_repository import (
    InboxTaskCollectionRepository,
)
from jupiter.core.domain.inbox_tasks.infra.inbox_task_repository import (
    InboxTaskRepository,
)
from jupiter.core.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import (
    MetricEntryRepository,
)
from jupiter.core.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.core.domain.persons.infra.person_collection_repository import (
    PersonCollectionRepository,
)
from jupiter.core.domain.persons.infra.person_repository import PersonRepository
from jupiter.core.domain.projects.infra.project_collection_repository import (
    ProjectCollectionRepository,
)
from jupiter.core.domain.projects.infra.project_repository import ProjectRepository
from jupiter.core.domain.push_integrations.email.infra.email_task_collection_repository import (
    EmailTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_repository import (
    EmailTaskRepository,
)
from jupiter.core.domain.push_integrations.group.infra.push_integration_group_repository import (
    PushIntegrationGroupRepository,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_collection_repository import (
    SlackTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_repository import (
    SlackTaskRepository,
)
from jupiter.core.domain.search_repository import SearchRepository
from jupiter.core.domain.smart_lists.infra.smart_list_collection_repository import (
    SmartListCollectionRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_item_repository import (
    SmartListItemRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_repository import (
    SmartListRepository,
)
from jupiter.core.domain.smart_lists.infra.smart_list_tag_repository import (
    SmartListTagRepository,
)
from jupiter.core.domain.storage_engine import (
    DomainStorageEngine,
    DomainUnitOfWork,
    SearchStorageEngine,
    SearchUnitOfWork,
)
from jupiter.core.domain.user.infra.user_repository import UserRepository
from jupiter.core.domain.user_workspace_link.infra.user_workspace_link_repository import (
    UserWorkspaceLinkRepository,
)
from jupiter.core.domain.vacations.infra.vacation_collection_repository import (
    VacationCollectionRepository,
)
from jupiter.core.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceRepository,
)
from jupiter.core.repository.sqlite.connection import SqliteConnection
from jupiter.core.repository.sqlite.domain.auths import SqliteAuthRepository
from jupiter.core.repository.sqlite.domain.big_plans import (
    SqliteBigPlanCollectionRepository,
    SqliteBigPlanRepository,
)
from jupiter.core.repository.sqlite.domain.chores import (
    SqliteChoreCollectionRepository,
    SqliteChoreRepository,
)
from jupiter.core.repository.sqlite.domain.fast_info import SqliteFastInfoRepository
from jupiter.core.repository.sqlite.domain.habits import (
    SqliteHabitCollectionRepository,
    SqliteHabitRepository,
)
from jupiter.core.repository.sqlite.domain.inbox_tasks import (
    SqliteInboxTaskCollectionRepository,
    SqliteInboxTaskRepository,
)
from jupiter.core.repository.sqlite.domain.metrics import (
    SqliteMetricCollectionRepository,
    SqliteMetricEntryRepository,
    SqliteMetricRepository,
)
from jupiter.core.repository.sqlite.domain.persons import (
    SqlitePersonCollectionRepository,
    SqlitePersonRepository,
)
from jupiter.core.repository.sqlite.domain.projects import (
    SqliteProjectCollectionRepository,
    SqliteProjectRepository,
)
from jupiter.core.repository.sqlite.domain.push_integration.email_tasks import (
    SqliteEmailTaskCollectionRepository,
    SqliteEmailTaskRepository,
)
from jupiter.core.repository.sqlite.domain.push_integration.push_integration_groups import (
    SqlitePushIntegrationGroupRepository,
)
from jupiter.core.repository.sqlite.domain.push_integration.slack_tasks import (
    SqliteSlackTaskCollectionRepository,
    SqliteSlackTaskRepository,
)
from jupiter.core.repository.sqlite.domain.search import SqliteSearchRepository
from jupiter.core.repository.sqlite.domain.smart_lists import (
    SqliteSmartListCollectionRepository,
    SqliteSmartListItemRepository,
    SqliteSmartListRepository,
    SqliteSmartListTagRepository,
)
from jupiter.core.repository.sqlite.domain.user_workspace_links import (
    SqliteUserWorkspaceLinkRepository,
)
from jupiter.core.repository.sqlite.domain.users import SqliteUserRepository
from jupiter.core.repository.sqlite.domain.vacations import (
    SqliteVacationCollectionRepository,
    SqliteVacationRepository,
)
from jupiter.core.repository.sqlite.domain.workspace import (
    SqliteWorkspaceRepository,
)
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine


class SqliteDomainUnitOfWork(DomainUnitOfWork):
    """A Sqlite specific unit of work."""

    _user_repository: Final[SqliteUserRepository]
    _auth_repository: Final[SqliteAuthRepository]
    _workspace_repository: Final[SqliteWorkspaceRepository]
    _user_workspace_link_repository: Final[SqliteUserWorkspaceLinkRepository]
    _vacation_collection_repository: Final[SqliteVacationCollectionRepository]
    _vacation_repository: Final[SqliteVacationRepository]
    _project_collection_repository: Final[SqliteProjectCollectionRepository]
    _project_repository: Final[SqliteProjectRepository]
    _inbox_task_collection_repository: Final[SqliteInboxTaskCollectionRepository]
    _inbox_task_repository: Final[SqliteInboxTaskRepository]
    _habit_collection_repository: Final[SqliteHabitCollectionRepository]
    _habit_repository: Final[SqliteHabitRepository]
    _chore_collection_repository: Final[SqliteChoreCollectionRepository]
    _chore_repository: Final[SqliteChoreRepository]
    _big_plan_collection_repository: Final[SqliteBigPlanCollectionRepository]
    _big_plan_repository: Final[SqliteBigPlanRepository]
    _smart_list_collection_repository: Final[SmartListCollectionRepository]
    _smart_list_repository: Final[SqliteSmartListRepository]
    _smart_list_tag_reposiotry: Final[SqliteSmartListTagRepository]
    _smart_list_item_repository: Final[SqliteSmartListItemRepository]
    _metric_collection_repository: Final[SqliteMetricCollectionRepository]
    _metric_repository: Final[SqliteMetricRepository]
    _metric_entry_repository: Final[SqliteMetricEntryRepository]
    _person_collection_repository: Final[SqlitePersonCollectionRepository]
    _person_repository: Final[SqlitePersonRepository]
    _push_integration_group_repository: Final[SqlitePushIntegrationGroupRepository]
    _slack_task_collection_repository: Final[SqliteSlackTaskCollectionRepository]
    _slack_task_repository: Final[SqliteSlackTaskRepository]
    _email_task_collection_repository: Final[SqliteEmailTaskCollectionRepository]
    _email_task_repository: Final[SqliteEmailTaskRepository]
    _fast_info_repository: Final[SqliteFastInfoRepository]

    def __init__(
        self,
        user_repository: SqliteUserRepository,
        auth_repository: SqliteAuthRepository,
        workspace_repository: SqliteWorkspaceRepository,
        user_workspace_link_repository: SqliteUserWorkspaceLinkRepository,
        vacation_repository: SqliteVacationRepository,
        vacation_collection_repository: SqliteVacationCollectionRepository,
        project_collection_repository: SqliteProjectCollectionRepository,
        project_repository: SqliteProjectRepository,
        inbox_task_collection_repository: SqliteInboxTaskCollectionRepository,
        inbox_task_repository: SqliteInboxTaskRepository,
        habit_collection_repository: SqliteHabitCollectionRepository,
        habit_repository: SqliteHabitRepository,
        chore_collection_repository: SqliteChoreCollectionRepository,
        chore_repository: SqliteChoreRepository,
        big_plan_collection_repository: SqliteBigPlanCollectionRepository,
        big_plan_repository: SqliteBigPlanRepository,
        smart_list_collection_repository: SqliteSmartListCollectionRepository,
        smart_list_repository: SqliteSmartListRepository,
        smart_list_tag_repository: SqliteSmartListTagRepository,
        smart_list_item_repository: SqliteSmartListItemRepository,
        metric_collection_repository: SqliteMetricCollectionRepository,
        metric_repository: SqliteMetricRepository,
        metric_entry_repository: SqliteMetricEntryRepository,
        person_collection_repository: SqlitePersonCollectionRepository,
        person_repository: SqlitePersonRepository,
        push_integration_group_repository: SqlitePushIntegrationGroupRepository,
        slack_task_collection_repository: SqliteSlackTaskCollectionRepository,
        slack_task_repository: SqliteSlackTaskRepository,
        email_task_collection_repository: SqliteEmailTaskCollectionRepository,
        email_task_repository: SqliteEmailTaskRepository,
        fast_into_repository: SqliteFastInfoRepository,
    ) -> None:
        """Constructor."""
        self._user_repository = user_repository
        self._auth_repository = auth_repository
        self._workspace_repository = workspace_repository
        self._user_workspace_link_repository = user_workspace_link_repository
        self._vacation_collection_repository = vacation_collection_repository
        self._vacation_repository = vacation_repository
        self._project_collection_repository = project_collection_repository
        self._project_repository = project_repository
        self._inbox_task_collection_repository = inbox_task_collection_repository
        self._inbox_task_repository = inbox_task_repository
        self._habit_collection_repository = habit_collection_repository
        self._habit_repository = habit_repository
        self._chore_collection_repository = chore_collection_repository
        self._chore_repository = chore_repository
        self._big_plan_collection_repository = big_plan_collection_repository
        self._big_plan_repository = big_plan_repository
        self._smart_list_collection_repository = smart_list_collection_repository
        self._smart_list_repository = smart_list_repository
        self._smart_list_tag_reposiotry = smart_list_tag_repository
        self._smart_list_item_repository = smart_list_item_repository
        self._metric_collection_repository = metric_collection_repository
        self._metric_repository = metric_repository
        self._metric_entry_repository = metric_entry_repository
        self._person_collection_repository = person_collection_repository
        self._person_repository = person_repository
        self._push_integration_group_repository = push_integration_group_repository
        self._slack_task_collection_repository = slack_task_collection_repository
        self._slack_task_repository = slack_task_repository
        self._email_task_collection_repository = email_task_collection_repository
        self._email_task_repository = email_task_repository
        self._fast_info_repository = fast_into_repository

    def __enter__(self) -> "SqliteDomainUnitOfWork":
        """Enter the context."""
        return self

    def __exit__(
        self,
        _exc_type: Optional[Type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context."""

    @property
    def user_repository(self) -> UserRepository:
        """The user repository."""
        return self._user_repository

    @property
    def auth_repository(self) -> AuthRepository:
        """The auth repository."""
        return self._auth_repository

    @property
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace repository."""
        return self._workspace_repository

    @property
    def user_workspace_link_repository(self) -> UserWorkspaceLinkRepository:
        """The user workspace link repository."""
        return self._user_workspace_link_repository

    @property
    def vacation_collection_repository(self) -> VacationCollectionRepository:
        """The vacation collection repository."""
        return self._vacation_collection_repository

    @property
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""
        return self._vacation_repository

    @property
    def project_collection_repository(self) -> ProjectCollectionRepository:
        """The projects repository."""
        return self._project_collection_repository

    @property
    def project_repository(self) -> ProjectRepository:
        """The projects repository."""
        return self._project_repository

    @property
    def inbox_task_collection_repository(self) -> InboxTaskCollectionRepository:
        """The inbox task collection repository."""
        return self._inbox_task_collection_repository

    @property
    def inbox_task_repository(self) -> InboxTaskRepository:
        """The inbox task repository."""
        return self._inbox_task_repository

    @property
    def habit_collection_repository(self) -> HabitCollectionRepository:
        """The habit collection repository."""
        return self._habit_collection_repository

    @property
    def habit_repository(self) -> HabitRepository:
        """The habit repository."""
        return self._habit_repository

    @property
    def chore_collection_repository(self) -> ChoreCollectionRepository:
        """The chore collection repository."""
        return self._chore_collection_repository

    @property
    def chore_repository(self) -> ChoreRepository:
        """The chore repository."""
        return self._chore_repository

    @property
    def big_plan_collection_repository(self) -> BigPlanCollectionRepository:
        """The big plan collection repository."""
        return self._big_plan_collection_repository

    @property
    def big_plan_repository(self) -> BigPlanRepository:
        """The big plan repository."""
        return self._big_plan_repository

    @property
    def smart_list_collection_repository(self) -> SmartListCollectionRepository:
        """The smart list collection repository."""
        return self._smart_list_collection_repository

    @property
    def smart_list_repository(self) -> SmartListRepository:
        """The smart list repository."""
        return self._smart_list_repository

    @property
    def smart_list_tag_repository(self) -> SmartListTagRepository:
        """The smart list tag repository."""
        return self._smart_list_tag_reposiotry

    @property
    def smart_list_item_repository(self) -> SmartListItemRepository:
        """The smart list item repository."""
        return self._smart_list_item_repository

    @property
    def metric_collection_repository(self) -> MetricCollectionRepository:
        """The metric collection repository."""
        return self._metric_collection_repository

    @property
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""
        return self._metric_repository

    @property
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""
        return self._metric_entry_repository

    @property
    def person_collection_repository(self) -> PersonCollectionRepository:
        """The person collection repository."""
        return self._person_collection_repository

    @property
    def person_repository(self) -> PersonRepository:
        """The person repository."""
        return self._person_repository

    @property
    def push_integration_group_repository(self) -> PushIntegrationGroupRepository:
        """The push integration group repository."""
        return self._push_integration_group_repository

    @property
    def slack_task_collection_repository(self) -> SlackTaskCollectionRepository:
        """The Slack task collection repository."""
        return self._slack_task_collection_repository

    @property
    def slack_task_repository(self) -> SlackTaskRepository:
        """The Slack task repository."""
        return self._slack_task_repository

    @property
    def email_task_collection_repository(self) -> EmailTaskCollectionRepository:
        """The email task collection repository."""
        return self._email_task_collection_repository

    @property
    def email_task_repository(self) -> EmailTaskRepository:
        """The email task repository."""
        return self._email_task_repository

    @property
    def fast_into_repository(self) -> FastInfoRepository:
        """The fast info repository."""
        return self._fast_info_repository


class SqliteDomainStorageEngine(DomainStorageEngine):
    """An Sqlite specific engine."""

    _sql_engine: Final[AsyncEngine]
    _metadata: Final[MetaData]

    def __init__(self, connection: SqliteConnection) -> None:
        """Constructor."""
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncIterator[DomainUnitOfWork]:
        """Get the unit of work."""
        async with self._sql_engine.begin() as connection:
            user_repository = SqliteUserRepository(connection, self._metadata)
            auth_repository = SqliteAuthRepository(connection, self._metadata)
            workspace_repository = SqliteWorkspaceRepository(connection, self._metadata)
            user_workspace_link_repository = SqliteUserWorkspaceLinkRepository(
                connection, self._metadata
            )
            vacation_collection_repository = SqliteVacationCollectionRepository(
                connection,
                self._metadata,
            )
            vacation_repository = SqliteVacationRepository(connection, self._metadata)
            project_collection_repository = SqliteProjectCollectionRepository(
                connection,
                self._metadata,
            )
            project_repository = SqliteProjectRepository(connection, self._metadata)
            inbox_task_collection_repository = SqliteInboxTaskCollectionRepository(
                connection,
                self._metadata,
            )
            inbox_task_repository = SqliteInboxTaskRepository(
                connection,
                self._metadata,
            )
            habit_collection_repository = SqliteHabitCollectionRepository(
                connection,
                self._metadata,
            )
            habit_repository = SqliteHabitRepository(connection, self._metadata)
            chore_collection_repository = SqliteChoreCollectionRepository(
                connection,
                self._metadata,
            )
            chore_repository = SqliteChoreRepository(connection, self._metadata)
            big_plan_collection_repository = SqliteBigPlanCollectionRepository(
                connection,
                self._metadata,
            )
            big_plan_repository = SqliteBigPlanRepository(connection, self._metadata)
            smart_list_collection_repository = SqliteSmartListCollectionRepository(
                connection,
                self._metadata,
            )
            smart_list_repository = SqliteSmartListRepository(
                connection,
                self._metadata,
            )
            smart_list_tag_repository = SqliteSmartListTagRepository(
                connection,
                self._metadata,
            )
            smart_list_item_repository = SqliteSmartListItemRepository(
                connection,
                self._metadata,
            )
            metric_collection_repository = SqliteMetricCollectionRepository(
                connection,
                self._metadata,
            )
            metric_repository = SqliteMetricRepository(connection, self._metadata)
            metric_entry_repository = SqliteMetricEntryRepository(
                connection,
                self._metadata,
            )
            person_collection_repository = SqlitePersonCollectionRepository(
                connection,
                self._metadata,
            )
            person_repository = SqlitePersonRepository(connection, self._metadata)
            push_integration_group_repository = SqlitePushIntegrationGroupRepository(
                connection,
                self._metadata,
            )
            slack_task_collection_repository = SqliteSlackTaskCollectionRepository(
                connection,
                self._metadata,
            )
            slack_task_repository = SqliteSlackTaskRepository(
                connection,
                self._metadata,
            )
            email_task_collection_repository = SqliteEmailTaskCollectionRepository(
                connection,
                self._metadata,
            )
            email_task_repository = SqliteEmailTaskRepository(
                connection,
                self._metadata,
            )
            fast_info_repository = SqliteFastInfoRepository(connection)

            yield SqliteDomainUnitOfWork(
                user_repository=user_repository,
                auth_repository=auth_repository,
                workspace_repository=workspace_repository,
                user_workspace_link_repository=user_workspace_link_repository,
                vacation_collection_repository=vacation_collection_repository,
                vacation_repository=vacation_repository,
                project_collection_repository=project_collection_repository,
                project_repository=project_repository,
                inbox_task_collection_repository=inbox_task_collection_repository,
                inbox_task_repository=inbox_task_repository,
                habit_collection_repository=habit_collection_repository,
                habit_repository=habit_repository,
                chore_collection_repository=chore_collection_repository,
                chore_repository=chore_repository,
                big_plan_collection_repository=big_plan_collection_repository,
                big_plan_repository=big_plan_repository,
                smart_list_collection_repository=smart_list_collection_repository,
                smart_list_repository=smart_list_repository,
                smart_list_tag_repository=smart_list_tag_repository,
                smart_list_item_repository=smart_list_item_repository,
                metric_collection_repository=metric_collection_repository,
                metric_repository=metric_repository,
                metric_entry_repository=metric_entry_repository,
                person_collection_repository=person_collection_repository,
                person_repository=person_repository,
                push_integration_group_repository=push_integration_group_repository,
                slack_task_collection_repository=slack_task_collection_repository,
                slack_task_repository=slack_task_repository,
                email_task_collection_repository=email_task_collection_repository,
                email_task_repository=email_task_repository,
                fast_into_repository=fast_info_repository,
            )


class SqliteSearchUnitOfWork(SearchUnitOfWork):
    """A Sqlite specific search unit of work."""

    _search_repository: Final[SqliteSearchRepository]

    def __init__(self, search_repository: SqliteSearchRepository) -> None:
        """Constructor."""
        self._search_repository = search_repository

    def __enter__(self) -> "SqliteSearchUnitOfWork":
        """Enter the context."""
        return self

    def __exit__(
        self,
        _exc_type: Optional[Type[BaseException]],
        _exc_val: Optional[BaseException],
        _exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context."""

    @property
    def search_repository(self) -> SearchRepository:
        """The search repository."""
        return self._search_repository


class SqliteSearchStorageEngine(SearchStorageEngine):
    """An Sqlite specific engine."""

    _sql_engine: Final[AsyncEngine]
    _metadata: Final[MetaData]

    def __init__(self, connection: SqliteConnection) -> None:
        """Constructor."""
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncIterator[SearchUnitOfWork]:
        """Get the unit of work."""
        async with self._sql_engine.begin() as connection:
            search_repository = SqliteSearchRepository(connection, self._metadata)
            yield SqliteSearchUnitOfWork(search_repository=search_repository)
