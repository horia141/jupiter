"""Domain-level storage interaction."""
import abc
from contextlib import contextmanager
from typing import Iterator, Type, TypeVar

from jupiter.domain.big_plans.infra.big_plan_collection_repository import BigPlanCollectionRepository
from jupiter.domain.big_plans.infra.big_plan_repository import BigPlanRepository
from jupiter.domain.chores.infra.chore_collection_repository import ChoreCollectionRepository
from jupiter.domain.chores.infra.chore_repository import ChoreRepository
from jupiter.domain.entity_key import EntityKey
from jupiter.domain.habits.infra.habit_collection_repository import HabitCollectionRepository
from jupiter.domain.habits.infra.habit_repository import HabitRepository
from jupiter.domain.inbox_tasks.infra.inbox_task_collection_repository import InboxTaskCollectionRepository
from jupiter.domain.inbox_tasks.infra.inbox_task_repository import InboxTaskRepository
from jupiter.domain.metrics.infra.metric_collection_repository import MetricCollectionRepository
from jupiter.domain.metrics.infra.metric_entry_repository import MetricEntryRepository
from jupiter.domain.metrics.infra.metric_repository import MetricRepository
from jupiter.domain.persons.infra.person_collection_repository import PersonCollectionRepository
from jupiter.domain.persons.infra.person_repository import PersonRepository
from jupiter.domain.projects.infra.project_collection_repository import ProjectCollectionRepository
from jupiter.domain.projects.infra.project_repository import ProjectRepository
from jupiter.domain.remote.notion.connection_repository import NotionConnectionRepository
from jupiter.domain.smart_lists.infra.smart_list_collection_repository import SmartListCollectionRepository
from jupiter.domain.smart_lists.infra.smart_list_item_repository import SmartListItemRepository
from jupiter.domain.smart_lists.infra.smart_list_repository import SmartListRepository
from jupiter.domain.smart_lists.infra.smart_list_tag_repository import SmartListTagRepository
from jupiter.domain.vacations.infra.vacation_collection_repository import VacationCollectionRepository
from jupiter.domain.vacations.infra.vacation_repository import VacationRepository
from jupiter.domain.workspaces.infra.workspace_repository import WorkspaceRepository
from jupiter.framework.entity import LeafEntity, TrunkEntity, BranchEntity
from jupiter.framework.repository import TrunkEntityRepository, LeafEntityRepository, BranchEntityRepository

TrunkType = TypeVar("TrunkType", bound=TrunkEntity)
BranchEntityKeyType = TypeVar("BranchEntityKeyType", bound=EntityKey)
BranchType = TypeVar("BranchType", bound=BranchEntity)
LeafType = TypeVar("LeafType", bound=LeafEntity)


class DomainUnitOfWork(abc.ABC):
    """A transactional unit of work from an engine."""

    @property
    @abc.abstractmethod
    def workspace_repository(self) -> WorkspaceRepository:
        """The workspace database repository."""

    @property
    @abc.abstractmethod
    def vacation_collection_repository(self) -> VacationCollectionRepository:
        """The vacation collection repository."""

    @property
    @abc.abstractmethod
    def vacation_repository(self) -> VacationRepository:
        """The vacation repository."""

    @property
    @abc.abstractmethod
    def project_collection_repository(self) -> ProjectCollectionRepository:
        """The project collection repository."""

    @property
    @abc.abstractmethod
    def project_repository(self) -> ProjectRepository:
        """The project database repository."""

    @property
    @abc.abstractmethod
    def inbox_task_collection_repository(self) -> InboxTaskCollectionRepository:
        """The inbox task collection repository."""

    @property
    @abc.abstractmethod
    def inbox_task_repository(self) -> InboxTaskRepository:
        """The inbox task repository."""

    @property
    @abc.abstractmethod
    def habit_collection_repository(self) -> HabitCollectionRepository:
        """The habit collection repository."""

    @property
    @abc.abstractmethod
    def habit_repository(self) -> HabitRepository:
        """The habit repository."""

    @property
    @abc.abstractmethod
    def chore_collection_repository(self) -> ChoreCollectionRepository:
        """The chore collection repository."""

    @property
    @abc.abstractmethod
    def chore_repository(self) -> ChoreRepository:
        """The chore repository."""

    @property
    @abc.abstractmethod
    def big_plan_collection_repository(self) -> BigPlanCollectionRepository:
        """The big plan collection repository."""

    @property
    @abc.abstractmethod
    def big_plan_repository(self) -> BigPlanRepository:
        """The big plan repository."""

    @property
    @abc.abstractmethod
    def smart_list_collection_repository(self) -> SmartListCollectionRepository:
        """The smart list collection repository."""

    @property
    @abc.abstractmethod
    def smart_list_repository(self) -> SmartListRepository:
        """The smart list repository."""

    @property
    @abc.abstractmethod
    def smart_list_tag_repository(self) -> SmartListTagRepository:
        """The smart list tag repository."""

    @property
    @abc.abstractmethod
    def smart_list_item_repository(self) -> SmartListItemRepository:
        """The smart list item repository."""

    @property
    @abc.abstractmethod
    def metric_collection_repository(self) -> MetricCollectionRepository:
        """The metric collection repository."""

    @property
    @abc.abstractmethod
    def metric_repository(self) -> MetricRepository:
        """The metric repository."""

    @property
    @abc.abstractmethod
    def metric_entry_repository(self) -> MetricEntryRepository:
        """The metric entry repository."""

    @property
    @abc.abstractmethod
    def person_collection_repository(self) -> PersonCollectionRepository:
        """The person collection repository."""

    @property
    @abc.abstractmethod
    def person_repository(self) -> PersonRepository:
        """The person repository."""

    @property
    @abc.abstractmethod
    def notion_connection_repository(self) -> NotionConnectionRepository:
        """The Notion connection repository."""

    @abc.abstractmethod
    def get_trunk_repository_for(self, trunk_type: Type[TrunkType]) -> TrunkEntityRepository[TrunkType]:
        """Lookup a trunk repository by a given type."""

    @abc.abstractmethod
    def get_branch_repository_for(
            self, branch_type: Type[BranchType]) -> BranchEntityRepository[BranchEntityKeyType, BranchType]:
        """Lookup a branch repository by a given type."""

    @abc.abstractmethod
    def get_leaf_repository_for(self, leaf_type: Type[LeafType]) -> LeafEntityRepository[LeafType]:
        """Lookup a leaf repository by a given type."""


class DomainStorageEngine(abc.ABC):
    """A storage engine of some form."""

    @abc.abstractmethod
    @contextmanager
    def get_unit_of_work(self) -> Iterator[DomainUnitOfWork]:
        """Build a unit of work."""
