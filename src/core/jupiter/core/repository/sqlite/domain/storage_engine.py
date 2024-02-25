"""The real implementation of an engine."""
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Any, AsyncIterator, Final, Optional, Type, TypeVar, cast, overload

from jupiter.core.domain.auth.auth import Auth
from jupiter.core.domain.auth.infra.auth_repository import AuthRepository
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.big_plan_collection import BigPlanCollection
from jupiter.core.domain.big_plans.infra.big_plan_collection_repository import (
    BigPlanCollectionRepository,
)
from jupiter.core.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.chore_collection import ChoreCollection
from jupiter.core.domain.chores.infra.chore_collection_repository import (
    ChoreCollectionRepository,
)
from jupiter.core.domain.chores.infra.chore_repository import ChoreRepository
from jupiter.core.domain.core.notes.infra.note_collection_repository import (
    NoteCollectionRepository,
)
from jupiter.core.domain.core.notes.infra.note_repository import NoteRepository
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.core.notes.note_collection import NoteCollection
from jupiter.core.domain.docs.doc import Doc
from jupiter.core.domain.docs.doc_collection import DocCollection
from jupiter.core.domain.docs.infra.doc_collection_repository import (
    DocCollectionRepository,
)
from jupiter.core.domain.docs.infra.doc_repository import DocRepository
from jupiter.core.domain.fast_info_repository import FastInfoRepository
from jupiter.core.domain.gamification.infra.score_log_entry_repository import (
    ScoreLogEntryRepository,
)
from jupiter.core.domain.gamification.infra.score_log_repository import (
    ScoreLogRepository,
)
from jupiter.core.domain.gamification.infra.score_period_best_repository import (
    ScorePeriodBestRepository,
)
from jupiter.core.domain.gamification.infra.score_stats_repository import (
    ScoreStatsRepository,
)
from jupiter.core.domain.gamification.score_log import ScoreLog
from jupiter.core.domain.gamification.score_log_entry import ScoreLogEntry
from jupiter.core.domain.gc.gc_log import GCLog
from jupiter.core.domain.gc.gc_log_entry import GCLogEntry
from jupiter.core.domain.gc.infra.gc_log_entry_repository import GCLogEntryRepository
from jupiter.core.domain.gc.infra.gc_log_repository import GCLogRepository
from jupiter.core.domain.gen.gen_log import GenLog
from jupiter.core.domain.gen.gen_log_entry import GenLogEntry
from jupiter.core.domain.gen.infra.gen_log_entry_repository import GenLogEntryRepository
from jupiter.core.domain.gen.infra.gen_log_repository import GenLogRepository
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.habit_collection import HabitCollection
from jupiter.core.domain.habits.infra.habit_collection_repository import (
    HabitCollectionRepository,
)
from jupiter.core.domain.habits.infra.habit_repository import HabitRepository
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
from jupiter.core.domain.inbox_tasks.inbox_task_collection import InboxTaskCollection
from jupiter.core.domain.inbox_tasks.infra.inbox_task_collection_repository import (
    InboxTaskCollectionRepository,
)
from jupiter.core.domain.inbox_tasks.infra.inbox_task_repository import (
    InboxTaskRepository,
)
from jupiter.core.domain.journals.infra.journal_collection_repository import (
    JournalCollectionRepository,
)
from jupiter.core.domain.journals.infra.journal_repository import JournalRepository
from jupiter.core.domain.journals.journal import Journal
from jupiter.core.domain.journals.journal_collection import JournalCollection
from jupiter.core.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import (
    MetricEntryRepository,
)
from jupiter.core.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_collection import MetricCollection
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.persons.infra.person_collection_repository import (
    PersonCollectionRepository,
)
from jupiter.core.domain.persons.infra.person_repository import PersonRepository
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.persons.person_collection import PersonCollection
from jupiter.core.domain.projects.infra.project_collection_repository import (
    ProjectCollectionRepository,
)
from jupiter.core.domain.projects.infra.project_repository import ProjectRepository
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.projects.project_collection import ProjectCollection
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
from jupiter.core.domain.push_integrations.email.email_task_collection import (
    EmailTaskCollection,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_collection_repository import (
    EmailTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.email.infra.email_task_repository import (
    EmailTaskRepository,
)
from jupiter.core.domain.push_integrations.group.infra.push_integration_group_repository import (
    PushIntegrationGroupRepository,
)
from jupiter.core.domain.push_integrations.group.push_integration_group import (
    PushIntegrationGroup,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_collection_repository import (
    SlackTaskCollectionRepository,
)
from jupiter.core.domain.push_integrations.slack.infra.slack_task_repository import (
    SlackTaskRepository,
)
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
from jupiter.core.domain.push_integrations.slack.slack_task_collection import (
    SlackTaskCollection,
)
from jupiter.core.domain.search.infra.search_repository import SearchRepository
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
from jupiter.core.domain.smart_lists.smart_list import SmartList
from jupiter.core.domain.smart_lists.smart_list_collection import SmartListCollection
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
from jupiter.core.domain.storage_engine import (
    DomainStorageEngine,
    DomainUnitOfWork,
    SearchStorageEngine,
    SearchUnitOfWork,
)
from jupiter.core.domain.user.infra.user_repository import UserRepository
from jupiter.core.domain.user.user import User
from jupiter.core.domain.user_workspace_link.infra.user_workspace_link_repository import (
    UserWorkspaceLinkRepository,
)
from jupiter.core.domain.user_workspace_link.user_workspace_link import (
    UserWorkspaceLink,
)
from jupiter.core.domain.vacations.infra.vacation_collection_repository import (
    VacationCollectionRepository,
)
from jupiter.core.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.vacations.vacation_collection import VacationCollection
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceRepository,
)
from jupiter.core.domain.workspaces.workspace import Workspace
from jupiter.core.framework.entity import (
    CrownEntity,
    Entity,
    RootEntity,
    StubEntity,
    TrunkEntity,
)
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.framework.record import Record
from jupiter.core.framework.repository import (
    CrownEntityRepository,
    EntityRepository,
    RecordRepository,
    Repository,
    RootEntityRepository,
    StubEntityRepository,
    TrunkEntityRepository,
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
from jupiter.core.repository.sqlite.domain.core.notes import (
    SqliteNoteCollectionRepository,
    SqliteNoteRepository,
)
from jupiter.core.repository.sqlite.domain.docs import (
    SqliteDocCollectionRepository,
    SqliteDocRepository,
)
from jupiter.core.repository.sqlite.domain.fast_info import SqliteFastInfoRepository
from jupiter.core.repository.sqlite.domain.gamification.scores import (
    SqliteScoreLogEntryRepository,
    SqliteScoreLogRepository,
    SqliteScorePeriodBestRepository,
    SqliteScoreStatsRepository,
)
from jupiter.core.repository.sqlite.domain.gc import (
    SqliteGCLogEntryRepository,
    SqliteGCLogRepository,
)
from jupiter.core.repository.sqlite.domain.gen import (
    SqliteGenLogEntryRepository,
    SqliteGenLogRepository,
)
from jupiter.core.repository.sqlite.domain.habits import (
    SqliteHabitCollectionRepository,
    SqliteHabitRepository,
)
from jupiter.core.repository.sqlite.domain.inbox_tasks import (
    SqliteInboxTaskCollectionRepository,
    SqliteInboxTaskRepository,
)
from jupiter.core.repository.sqlite.domain.journals import (
    SqliteJournalCollectionRepository,
    SqliteJournalRepository,
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

_RepositoryT = TypeVar("_RepositoryT", bound=Repository)
_RootEntityT = TypeVar("_RootEntityT", bound=RootEntity)
_StubEntityT = TypeVar("_StubEntityT", bound=StubEntity)
_TrunkEntityT = TypeVar("_TrunkEntityT", bound=TrunkEntity)
_CrownEntityT = TypeVar("_CrownEntityT", bound=CrownEntity)


class SqliteDomainUnitOfWork(DomainUnitOfWork):
    """A Sqlite specific unit of work."""

    _entity_repositories: Final[dict[type[Entity], EntityRepository[Entity]]]
    _repositories: Final[dict[type[Repository], Repository]]

    def __init__(
        self,
        user_repository: SqliteUserRepository,
        auth_repository: SqliteAuthRepository,
        score_log_repository: SqliteScoreLogRepository,
        score_log_entry_repository: SqliteScoreLogEntryRepository,
        score_stats_repository: SqliteScoreStatsRepository,
        score_period_best_repository: SqliteScorePeriodBestRepository,
        workspace_repository: SqliteWorkspaceRepository,
        user_workspace_link_repository: SqliteUserWorkspaceLinkRepository,
        inbox_task_collection_repository: SqliteInboxTaskCollectionRepository,
        inbox_task_repository: SqliteInboxTaskRepository,
        habit_collection_repository: SqliteHabitCollectionRepository,
        habit_repository: SqliteHabitRepository,
        chore_collection_repository: SqliteChoreCollectionRepository,
        chore_repository: SqliteChoreRepository,
        big_plan_collection_repository: SqliteBigPlanCollectionRepository,
        big_plan_repository: SqliteBigPlanRepository,
        journal_collection_repository: SqliteJournalCollectionRepository,
        journal_repository: SqliteJournalRepository,
        doc_collection_repository: SqliteDocCollectionRepository,
        doc_repository: SqliteDocRepository,
        vacation_repository: SqliteVacationRepository,
        vacation_collection_repository: SqliteVacationCollectionRepository,
        project_collection_repository: SqliteProjectCollectionRepository,
        project_repository: SqliteProjectRepository,
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
        note_collection_repository: SqliteNoteCollectionRepository,
        note_repository: SqliteNoteRepository,
        fast_into_repository: SqliteFastInfoRepository,
        gen_log_repository: SqliteGenLogRepository,
        gen_log_entry_repository: SqliteGenLogEntryRepository,
        gc_log_repository: SqliteGCLogRepository,
        gc_log_entry_repository: SqliteGCLogEntryRepository,
    ) -> None:
        """Constructor."""
        self._entity_repositories = {
            User: user_repository,
            Auth: auth_repository,
            ScoreLog: score_log_repository,
            ScoreLogEntry: score_log_entry_repository,
            Workspace: workspace_repository,
            UserWorkspaceLink: user_workspace_link_repository,
            InboxTaskCollection: inbox_task_collection_repository,
            InboxTask: inbox_task_repository,
            HabitCollection: habit_collection_repository,
            Habit: habit_repository,
            ChoreCollection: chore_collection_repository,
            Chore: chore_repository,
            BigPlanCollection: big_plan_collection_repository,
            BigPlan: big_plan_repository,
            JournalCollection: journal_collection_repository,
            Journal: journal_repository,
            DocCollection: doc_collection_repository,
            Doc: doc_repository,
            VacationCollection: vacation_collection_repository,
            Vacation: vacation_repository,
            ProjectCollection: project_collection_repository,
            Project: project_repository,
            SmartListCollection: smart_list_collection_repository,
            SmartList: smart_list_repository,
            SmartListTag: smart_list_tag_repository,
            SmartListItem: smart_list_item_repository,
            MetricCollection: metric_collection_repository,
            Metric: metric_repository,
            MetricEntry: metric_entry_repository,
            PersonCollection: person_collection_repository,
            Person: person_repository,
            PushIntegrationGroup: push_integration_group_repository,
            SlackTaskCollection: slack_task_collection_repository,
            SlackTask: slack_task_repository,
            EmailTaskCollection: email_task_collection_repository,
            EmailTask: email_task_repository,
            NoteCollection: note_collection_repository,
            Note: note_repository,
            GenLog: gen_log_repository,
            GenLogEntry: gen_log_entry_repository,
            GCLog: gc_log_repository,
            GCLogEntry: gc_log_entry_repository,
        }
        self._repositories = {
            UserRepository: user_repository,
            AuthRepository: auth_repository,
            ScoreLogRepository: score_log_repository,
            ScoreLogEntryRepository: score_log_entry_repository,
            WorkspaceRepository: workspace_repository,
            UserWorkspaceLinkRepository: user_workspace_link_repository,
            InboxTaskCollectionRepository: inbox_task_collection_repository,
            InboxTaskRepository: inbox_task_repository,
            HabitCollectionRepository: habit_collection_repository,
            HabitRepository: habit_repository,
            ChoreCollectionRepository: chore_collection_repository,
            ChoreRepository: chore_repository,
            BigPlanCollectionRepository: big_plan_collection_repository,
            BigPlanRepository: big_plan_repository,
            JournalCollectionRepository: journal_collection_repository,
            JournalRepository: journal_repository,
            DocCollectionRepository: doc_collection_repository,
            DocRepository: doc_repository,
            VacationCollectionRepository: vacation_collection_repository,
            VacationRepository: vacation_repository,
            ProjectCollectionRepository: project_collection_repository,
            ProjectRepository: project_repository,
            SmartListCollectionRepository: smart_list_collection_repository,
            SmartListRepository: smart_list_repository,
            SmartListTagRepository: smart_list_tag_repository,
            SmartListItemRepository: smart_list_item_repository,
            MetricCollectionRepository: metric_collection_repository,
            MetricRepository: metric_repository,
            MetricEntryRepository: metric_entry_repository,
            PersonCollectionRepository: person_collection_repository,
            PersonRepository: person_repository,
            PushIntegrationGroupRepository: push_integration_group_repository,
            SlackTaskCollectionRepository: slack_task_collection_repository,
            SlackTaskRepository: slack_task_repository,
            EmailTaskCollectionRepository: email_task_collection_repository,
            EmailTaskRepository: email_task_repository,
            NoteCollectionRepository: note_collection_repository,
            NoteRepository: note_repository,
            FastInfoRepository: fast_into_repository,
            GenLogRepository: gen_log_repository,
            GenLogEntryRepository: gen_log_entry_repository,
            GCLogRepository: gc_log_repository,
            GCLogEntryRepository: gc_log_entry_repository,
            ScoreStatsRepository: score_stats_repository,
            ScorePeriodBestRepository: score_period_best_repository,
        }

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

    def get(self, repository_type: Type[_RepositoryT]) -> _RepositoryT:
        """Retrieve a repository."""
        if repository_type not in self._repositories:
            raise ValueError(f"No repository for type: {repository_type}")
        return cast(_RepositoryT, self._repositories[repository_type])

    @overload
    def get_for(
        self, entity_type: Type[_RootEntityT]
    ) -> RootEntityRepository[_RootEntityT]:
        """Retrieve a repository."""

    @overload
    def get_for(
        self, entity_type: Type[_StubEntityT]
    ) -> StubEntityRepository[_StubEntityT]:
        """Retrieve a repository."""

    @overload
    def get_for(
        self, entity_type: Type[_TrunkEntityT]
    ) -> TrunkEntityRepository[_TrunkEntityT]:
        """Retrieve a repository."""

    @overload
    def get_for(
        self, entity_type: Type[_CrownEntityT]
    ) -> CrownEntityRepository[_CrownEntityT]:
        """Retrieve a repository."""

    def get_for(
        self,
        entity_type: Type[_RootEntityT]
        | Type[_StubEntityT]
        | Type[_TrunkEntityT]
        | Type[_CrownEntityT],
    ) -> RootEntityRepository[_RootEntityT] | StubEntityRepository[
        _StubEntityT
    ] | TrunkEntityRepository[_TrunkEntityT] | CrownEntityRepository[_CrownEntityT]:
        """Return a repository for a particular entity."""
        if entity_type not in self._entity_repositories:
            raise ValueError(f"No repository for entity type: {entity_type}")
        if issubclass(entity_type, RootEntity):
            return cast(
                RootEntityRepository[_RootEntityT],
                self._entity_repositories[entity_type],
            )
        if issubclass(entity_type, StubEntity):
            return cast(
                StubEntityRepository[_StubEntityT],
                self._entity_repositories[entity_type],
            )
        if issubclass(entity_type, TrunkEntity):
            return cast(
                TrunkEntityRepository[_TrunkEntityT],
                self._entity_repositories[entity_type],
            )
        if issubclass(entity_type, CrownEntity):
            return cast(
                CrownEntityRepository[_CrownEntityT],
                self._entity_repositories[entity_type],
            )


class SqliteDomainStorageEngine(DomainStorageEngine):
    """An Sqlite specific engine."""

    _realm_codec_registry: Final[RealmCodecRegistry]
    _sql_engine: Final[AsyncEngine]
    _metadata: Final[MetaData]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, connection: SqliteConnection
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncIterator[DomainUnitOfWork]:
        """Get the unit of work."""
        async with self._sql_engine.begin() as connection:
            user_repository = SqliteUserRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            auth_repository = SqliteAuthRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            score_log_repository = SqliteScoreLogRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            score_log_entry_repository = SqliteScoreLogEntryRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            score_stats_repository = SqliteScoreStatsRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            score_period_best_repository = SqliteScorePeriodBestRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            workspace_repository = SqliteWorkspaceRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            user_workspace_link_repository = SqliteUserWorkspaceLinkRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            inbox_task_collection_repository = SqliteInboxTaskCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            inbox_task_repository = SqliteInboxTaskRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            habit_collection_repository = SqliteHabitCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            habit_repository = SqliteHabitRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            chore_collection_repository = SqliteChoreCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            chore_repository = SqliteChoreRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            big_plan_collection_repository = SqliteBigPlanCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            big_plan_repository = SqliteBigPlanRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            journal_collection_repository = SqliteJournalCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            journal_repository = SqliteJournalRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            doc_collection_repository = SqliteDocCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            doc_repository = SqliteDocRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            vacation_collection_repository = SqliteVacationCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            vacation_repository = SqliteVacationRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            project_collection_repository = SqliteProjectCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            project_repository = SqliteProjectRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            smart_list_collection_repository = SqliteSmartListCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            smart_list_repository = SqliteSmartListRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            smart_list_tag_repository = SqliteSmartListTagRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            smart_list_item_repository = SqliteSmartListItemRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            metric_collection_repository = SqliteMetricCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            metric_repository = SqliteMetricRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            metric_entry_repository = SqliteMetricEntryRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            person_collection_repository = SqlitePersonCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            person_repository = SqlitePersonRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            push_integration_group_repository = SqlitePushIntegrationGroupRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            slack_task_collection_repository = SqliteSlackTaskCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            slack_task_repository = SqliteSlackTaskRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            email_task_collection_repository = SqliteEmailTaskCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            email_task_repository = SqliteEmailTaskRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            note_collection_repository = SqliteNoteCollectionRepository(
                self._realm_codec_registry,
                connection,
                self._metadata,
            )
            note_repository = SqliteNoteRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            fast_info_repository = SqliteFastInfoRepository(connection)
            gen_log_repository = SqliteGenLogRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            gen_log_entry_repository = SqliteGenLogEntryRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            gc_log_repository = SqliteGCLogRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            gc_log_entry_repository = SqliteGCLogEntryRepository(
                self._realm_codec_registry, connection, self._metadata
            )

            yield SqliteDomainUnitOfWork(
                user_repository=user_repository,
                auth_repository=auth_repository,
                score_log_repository=score_log_repository,
                score_log_entry_repository=score_log_entry_repository,
                score_stats_repository=score_stats_repository,
                score_period_best_repository=score_period_best_repository,
                workspace_repository=workspace_repository,
                user_workspace_link_repository=user_workspace_link_repository,
                inbox_task_collection_repository=inbox_task_collection_repository,
                inbox_task_repository=inbox_task_repository,
                habit_collection_repository=habit_collection_repository,
                habit_repository=habit_repository,
                chore_collection_repository=chore_collection_repository,
                chore_repository=chore_repository,
                big_plan_collection_repository=big_plan_collection_repository,
                big_plan_repository=big_plan_repository,
                journal_collection_repository=journal_collection_repository,
                journal_repository=journal_repository,
                doc_collection_repository=doc_collection_repository,
                doc_repository=doc_repository,
                vacation_collection_repository=vacation_collection_repository,
                vacation_repository=vacation_repository,
                project_collection_repository=project_collection_repository,
                project_repository=project_repository,
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
                note_collection_repository=note_collection_repository,
                note_repository=note_repository,
                fast_into_repository=fast_info_repository,
                gen_log_repository=gen_log_repository,
                gen_log_entry_repository=gen_log_entry_repository,
                gc_log_repository=gc_log_repository,
                gc_log_entry_repository=gc_log_entry_repository,
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

    _realm_codec_registry: Final[RealmCodecRegistry]
    _sql_engine: Final[AsyncEngine]
    _metadata: Final[MetaData]

    def __init__(
        self, realm_codec_registry: RealmCodecRegistry, connection: SqliteConnection
    ) -> None:
        """Constructor."""
        self._realm_codec_registry = realm_codec_registry
        self._sql_engine = connection.sql_engine
        self._metadata = MetaData(bind=self._sql_engine)

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncIterator[SearchUnitOfWork]:
        """Get the unit of work."""
        async with self._sql_engine.begin() as connection:
            search_repository = SqliteSearchRepository(
                self._realm_codec_registry, connection, self._metadata
            )
            yield SqliteSearchUnitOfWork(search_repository=search_repository)
