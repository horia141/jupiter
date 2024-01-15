"""The real implementation of an engine."""
from contextlib import asynccontextmanager
from types import TracebackType
from typing import AsyncIterator, Final, Optional, Type, TypeVar, cast

from jupiter.core.domain.auth.infra.auth_repository import AuthRepository
from jupiter.core.domain.big_plans.big_plan import BigPlan
from jupiter.core.domain.big_plans.infra.big_plan_collection_repository import (
    BigPlanCollectionRepository,
)
from jupiter.core.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.core.domain.chores.chore import Chore
from jupiter.core.domain.chores.infra.chore_collection_repository import (
    ChoreCollectionRepository,
)
from jupiter.core.domain.chores.infra.chore_repository import ChoreRepository
from jupiter.core.domain.core.notes.infra.note_collection_repository import (
    NoteCollectionRepository,
)
from jupiter.core.domain.core.notes.infra.note_repository import NoteRepository
from jupiter.core.domain.core.notes.note import Note
from jupiter.core.domain.docs.doc import Doc
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
from jupiter.core.domain.gc.infra.gc_log_entry_repository import GCLogEntryRepository
from jupiter.core.domain.gc.infra.gc_log_repository import GCLogRepository
from jupiter.core.domain.gen.infra.gen_log_entry_repository import GenLogEntryRepository
from jupiter.core.domain.gen.infra.gen_log_repository import GenLogRepository
from jupiter.core.domain.habits.habit import Habit
from jupiter.core.domain.habits.infra.habit_collection_repository import (
    HabitCollectionRepository,
)
from jupiter.core.domain.habits.infra.habit_repository import HabitRepository
from jupiter.core.domain.inbox_tasks.inbox_task import InboxTask
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
from jupiter.core.domain.metrics.infra.metric_collection_repository import (
    MetricCollectionRepository,
)
from jupiter.core.domain.metrics.infra.metric_entry_repository import (
    MetricEntryRepository,
)
from jupiter.core.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.core.domain.metrics.metric import Metric
from jupiter.core.domain.metrics.metric_entry import MetricEntry
from jupiter.core.domain.persons.infra.person_collection_repository import (
    PersonCollectionRepository,
)
from jupiter.core.domain.persons.infra.person_repository import PersonRepository
from jupiter.core.domain.persons.person import Person
from jupiter.core.domain.projects.infra.project_collection_repository import (
    ProjectCollectionRepository,
)
from jupiter.core.domain.projects.infra.project_repository import ProjectRepository
from jupiter.core.domain.projects.project import Project
from jupiter.core.domain.push_integrations.email.email_task import EmailTask
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
from jupiter.core.domain.push_integrations.slack.slack_task import SlackTask
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
from jupiter.core.domain.smart_lists.smart_list_item import SmartListItem
from jupiter.core.domain.smart_lists.smart_list_tag import SmartListTag
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
from jupiter.core.domain.vacations.vacation import Vacation
from jupiter.core.domain.workspaces.infra.workspace_repository import (
    WorkspaceRepository,
)
from jupiter.core.framework.entity import CrownEntity
from jupiter.core.framework.realm import RealmCodecRegistry
from jupiter.core.framework.repository import CrownEntityRepository
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

_CrownEntityT = TypeVar("_CrownEntityT", bound=CrownEntity)


class SqliteDomainUnitOfWork(DomainUnitOfWork):
    """A Sqlite specific unit of work."""

    _user_repository: Final[SqliteUserRepository]
    _auth_repository: Final[SqliteAuthRepository]
    _score_log_repository: Final[SqliteScoreLogRepository]
    _score_log_entry_repository: Final[SqliteScoreLogEntryRepository]
    _score_stats_repository: Final[SqliteScoreStatsRepository]
    _score_period_best_repository: Final[SqliteScorePeriodBestRepository]
    _workspace_repository: Final[SqliteWorkspaceRepository]
    _user_workspace_link_repository: Final[SqliteUserWorkspaceLinkRepository]
    _inbox_task_collection_repository: Final[SqliteInboxTaskCollectionRepository]
    _inbox_task_repository: Final[SqliteInboxTaskRepository]
    _habit_collection_repository: Final[SqliteHabitCollectionRepository]
    _habit_repository: Final[SqliteHabitRepository]
    _chore_collection_repository: Final[SqliteChoreCollectionRepository]
    _chore_repository: Final[SqliteChoreRepository]
    _big_plan_collection_repository: Final[SqliteBigPlanCollectionRepository]
    _big_plan_repository: Final[SqliteBigPlanRepository]
    _journal_collection_repository: Final[SqliteJournalCollectionRepository]
    _journal_repository: Final[SqliteJournalRepository]
    _doc_collection_repository: Final[SqliteDocCollectionRepository]
    _doc_repository: Final[SqliteDocRepository]
    _vacation_collection_repository: Final[SqliteVacationCollectionRepository]
    _vacation_repository: Final[SqliteVacationRepository]
    _project_collection_repository: Final[SqliteProjectCollectionRepository]
    _project_repository: Final[SqliteProjectRepository]
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
    _note_collection_repository: Final[SqliteNoteCollectionRepository]
    _note_repository: Final[SqliteNoteRepository]
    _fast_info_repository: Final[SqliteFastInfoRepository]
    _gen_log_repository: Final[SqliteGenLogRepository]
    _gen_log_entry_repository: Final[SqliteGenLogEntryRepository]
    _gc_log_repository: Final[SqliteGCLogRepository]
    _gc_log_entry_repository: Final[SqliteGCLogEntryRepository]

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
        self._user_repository = user_repository
        self._auth_repository = auth_repository
        self._score_log_repository = score_log_repository
        self._score_log_entry_repository = score_log_entry_repository
        self._score_stats_repository = score_stats_repository
        self._score_period_best_repository = score_period_best_repository
        self._workspace_repository = workspace_repository
        self._user_workspace_link_repository = user_workspace_link_repository
        self._inbox_task_collection_repository = inbox_task_collection_repository
        self._inbox_task_repository = inbox_task_repository
        self._habit_collection_repository = habit_collection_repository
        self._habit_repository = habit_repository
        self._chore_collection_repository = chore_collection_repository
        self._chore_repository = chore_repository
        self._big_plan_collection_repository = big_plan_collection_repository
        self._big_plan_repository = big_plan_repository
        self._journal_collection_repository = journal_collection_repository
        self._journal_repository = journal_repository
        self._doc_collection_repository = doc_collection_repository
        self._doc_repository = doc_repository
        self._vacation_collection_repository = vacation_collection_repository
        self._vacation_repository = vacation_repository
        self._project_collection_repository = project_collection_repository
        self._project_repository = project_repository
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
        self._note_collection_repository = note_collection_repository
        self._note_repository = note_repository
        self._fast_info_repository = fast_into_repository
        self._gen_log_repository = gen_log_repository
        self._gen_log_entry_repository = gen_log_entry_repository
        self._gc_log_repository = gc_log_repository
        self._gc_log_entry_repository = gc_log_entry_repository

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
    def score_log_repository(self) -> ScoreLogRepository:
        """The score log repository."""
        return self._score_log_repository

    @property
    def score_log_entry_repository(self) -> ScoreLogEntryRepository:
        """The score log entry repository."""
        return self._score_log_entry_repository

    @property
    def score_stats_repository(self) -> ScoreStatsRepository:
        """The score stats repository."""
        return self._score_stats_repository

    @property
    def score_period_best_repository(self) -> ScorePeriodBestRepository:
        """The score period best repository."""
        return self._score_period_best_repository

    @property
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace repository."""
        return self._workspace_repository

    @property
    def user_workspace_link_repository(self) -> UserWorkspaceLinkRepository:
        """The user workspace link repository."""
        return self._user_workspace_link_repository

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
    def journal_collection_repository(self) -> JournalCollectionRepository:
        """The journal collection repository."""
        return self._journal_collection_repository

    @property
    def journal_repository(self) -> JournalRepository:
        """The journal repository."""
        return self._journal_repository

    @property
    def doc_collection_repository(self) -> DocCollectionRepository:
        """The doc collection repository."""
        return self._doc_collection_repository

    @property
    def doc_repository(self) -> DocRepository:
        """The doc repository."""
        return self._doc_repository

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
    def note_collection_repository(self) -> NoteCollectionRepository:
        """The note collection repository."""
        return self._note_collection_repository

    @property
    def note_repository(self) -> NoteRepository:
        """The note repository."""
        return self._note_repository

    @property
    def fast_into_repository(self) -> FastInfoRepository:
        """The fast info repository."""
        return self._fast_info_repository

    @property
    def gen_log_repository(self) -> GenLogRepository:
        """The gen log repository."""
        return self._gen_log_repository

    @property
    def gen_log_entry_repository(self) -> GenLogEntryRepository:
        """The gen log entry repository."""
        return self._gen_log_entry_repository

    @property
    def gc_log_repository(self) -> GCLogRepository:
        """The gc log repository."""
        return self._gc_log_repository

    @property
    def gc_log_entry_repository(self) -> GCLogEntryRepository:
        """The gc log entry repository."""
        return self._gc_log_entry_repository

    def get_repository(
        self, entity_type: Type[_CrownEntityT]
    ) -> CrownEntityRepository[_CrownEntityT]:
        """Return a repository for a particular entity."""
        if entity_type is InboxTask:
            return cast(
                CrownEntityRepository[_CrownEntityT], self._inbox_task_repository
            )
        elif entity_type is Habit:
            return cast(CrownEntityRepository[_CrownEntityT], self._habit_repository)
        elif entity_type is Chore:
            return cast(CrownEntityRepository[_CrownEntityT], self._chore_repository)
        elif entity_type is BigPlan:
            return cast(CrownEntityRepository[_CrownEntityT], self._big_plan_repository)
        elif entity_type is Journal:
            return cast(CrownEntityRepository[_CrownEntityT], self._journal_repository)
        elif entity_type is Doc:
            return cast(CrownEntityRepository[_CrownEntityT], self._doc_repository)
        elif entity_type is Vacation:
            return cast(CrownEntityRepository[_CrownEntityT], self._vacation_repository)
        elif entity_type is Project:
            return cast(CrownEntityRepository[_CrownEntityT], self._project_repository)
        elif entity_type is SmartList:
            return cast(
                CrownEntityRepository[_CrownEntityT], self._smart_list_repository
            )
        elif entity_type is SmartListTag:
            return cast(
                CrownEntityRepository[_CrownEntityT], self._smart_list_tag_reposiotry
            )
        elif entity_type is SmartListItem:
            return cast(
                CrownEntityRepository[_CrownEntityT], self._smart_list_item_repository
            )
        elif entity_type is Metric:
            return cast(CrownEntityRepository[_CrownEntityT], self._metric_repository)
        elif entity_type is MetricEntry:
            return cast(
                CrownEntityRepository[_CrownEntityT], self._metric_entry_repository
            )
        elif entity_type is Person:
            return cast(CrownEntityRepository[_CrownEntityT], self._person_repository)
        elif entity_type is SlackTask:
            return cast(
                CrownEntityRepository[_CrownEntityT], self._slack_task_repository
            )
        elif entity_type is EmailTask:
            return cast(
                CrownEntityRepository[_CrownEntityT], self._email_task_repository
            )
        elif entity_type is Note:
            return cast(CrownEntityRepository[_CrownEntityT], self._note_repository)
        else:
            raise Exception("Repository not implemented yet")


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
