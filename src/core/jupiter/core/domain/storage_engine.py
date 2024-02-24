"""Domain-level storage interaction."""
import abc
from typing import Any, AsyncContextManager, Type, TypeVar, overload

from jupiter.core.domain.auth.infra.auth_repository import AuthRepository
from jupiter.core.domain.big_plans.infra.big_plan_collection_repository import (
    BigPlanCollectionRepository,
)
from jupiter.core.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.core.domain.chores.infra.chore_collection_repository import (
    ChoreCollectionRepository,
)
from jupiter.core.domain.chores.infra.chore_repository import ChoreRepository
from jupiter.core.domain.core.notes.infra.note_collection_repository import (
    NoteCollectionRepository,
)
from jupiter.core.domain.core.notes.infra.note_repository import NoteRepository
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
from jupiter.core.domain.journals.infra.journal_collection_repository import (
    JournalCollectionRepository,
)
from jupiter.core.domain.journals.infra.journal_repository import JournalRepository
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
from jupiter.core.framework.entity import CrownEntity, Entity, RootEntity, StubEntity, TrunkEntity
from jupiter.core.framework.record import Record
from jupiter.core.framework.repository import CrownEntityRepository, EntityRepository, RecordRepository, Repository, RootEntityRepository, StubEntityRepository, TrunkEntityRepository

_RepositoryT = TypeVar("_RepositoryT", bound=Repository)
_EntityRepositoryT = TypeVar("_EntityRepositoryT", bound=EntityRepository[Any], covariant=True)  # type: ignore
_RecordRepositoryT = TypeVar("_RecordRepositoryT", bound=RecordRepository[Any, Any, Any], covariant=True) # type: ignore
_RootEntityT = TypeVar("_RootEntityT", bound=RootEntity)
_StubEntityT = TypeVar("_StubEntityT", bound=StubEntity)
_TrunkEntityT = TypeVar("_TrunkEntityT", bound=TrunkEntity)
_CrownEntityT = TypeVar("_CrownEntityT", bound=CrownEntity)


class DomainUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""
    
    @abc.abstractmethod
    def get(  # type: ignore
        self, repository_type: Type[_EntityRepositoryT]
    ) -> _EntityRepositoryT:
        """Retrieve a repository."""

    @abc.abstractmethod
    def get_r(  # type: ignore
        self, repository_type: Type[_RecordRepositoryT]
    ) -> _RecordRepositoryT:
        """Retrieve a repository."""

    @abc.abstractmethod
    def get_x(
        self, repository: type[_RepositoryT]
    ) -> _RepositoryT:
        """Retrieve a repository"""

    @overload
    @abc.abstractmethod
    def repository_for(
        self, entity_type: Type[_RootEntityT]
    ) -> RootEntityRepository[_RootEntityT]:
        """Retrieve a repository."""

    @overload
    @abc.abstractmethod
    def repository_for(
        self, entity_type: Type[_StubEntityT]
    ) -> StubEntityRepository[_StubEntityT]:
        """Retrieve a repository."""

    @overload
    @abc.abstractmethod
    def repository_for(
        self, entity_type: Type[_TrunkEntityT]
    ) -> TrunkEntityRepository[_TrunkEntityT]:
        """Retrieve a repository."""

    @overload
    @abc.abstractmethod
    def repository_for(
        self, entity_type: Type[_CrownEntityT]
    ) -> CrownEntityRepository[_CrownEntityT]:
        """Retrieve a repository."""

    @abc.abstractmethod
    def repository_for(
        self, entity_type: Type[_RootEntityT] | Type[_StubEntityT] | Type[_TrunkEntityT] | Type[_CrownEntityT]
    ) -> RootEntityRepository[_RootEntityT] | StubEntityRepository[_StubEntityT] | TrunkEntityRepository[_TrunkEntityT] | CrownEntityRepository[_CrownEntityT]:
        """Retrieve a repository."""


class DomainStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AsyncContextManager[DomainUnitOfWork]:
        """Build a unit of work."""


class SearchUnitOfWork(abc.ABC):
    """A unit of work from a search engine."""

    @property
    @abc.abstractmethod
    def search_repository(self) -> SearchRepository:
        """The search repostory."""


class SearchStorageEngine(abc.ABC):
    """A storage engine of some form for the search engine."""

    @abc.abstractmethod
    def get_unit_of_work(self) -> AsyncContextManager[SearchUnitOfWork]:
        """Build a unit of work."""
